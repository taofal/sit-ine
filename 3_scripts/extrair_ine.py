#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extrair_ine.py — pede ao INE os indicadores de ine_indicadores.json e grava as respostas,
exatamente como o INE as devolve, em 1_bruto/ine/<AAAA-MM-DD>/ (+ _entrega.md).

  py extrair_ine.py                 últimos N períodos de cada indicador (N em ine_indicadores.json)
  py extrair_ine.py --completo      séries completas (todos os períodos) — para correr de vez em quando
  py extrair_ine.py --carregar      no fim corre carregar_ine.py (1_bruto -> indicador_territorio.csv)
  py extrair_ine.py --so 0013863    só um ou mais indicadores (códigos separados por vírgula)

Regras:
  - Todas as categorias de todas as dimensões (CAE, segmento, nível de educação, país…): a dimensão
    é omitida no pedido e o INE devolve tudo. Período e local são os únicos filtros.
  - 1_bruto só se acrescenta: um ficheiro que já exista com o mesmo nome nunca é reescrito.
  - Pedidos em fila (2 em simultâneo, 0,6 s de intervalo) e nova tentativa quando o INE responde 429.
  - Ligação: Python direto; se falhar no Windows, usa o proxy do Windows (PowerShell).

Só biblioteca padrão (Python 3.8+). Com inspeção SSL na rede: py -m pip install truststore
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import unicodedata
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime
from pathlib import Path

try:
    import truststore  # type: ignore
    truststore.inject_into_ssl()
except Exception:
    pass

AQUI = Path(__file__).resolve().parent
SIT = AQUI.parent
BRUTO = SIT / "1_bruto" / "ine"
CONFIG = AQUI / "ine_indicadores.json"
BASE_DADOS = "https://www.ine.pt/ine/json_indicador/pindica.jsp"
BASE_META = "https://www.ine.pt/ine/json_indicador/pindicaMeta.jsp"
UA = "CMG-DIIET-SIT/1.0 (+https://www.cm-guimaraes.pt)"
MAX_VALORES = 30000          # valores estimados por pedido; acima disso parte-se em blocos de períodos


def log(msg):
    print(f"{datetime.now():%H:%M:%S}  {msg}", flush=True)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


# ------------------------------------------------------------------ rede
VIA = {"modo": None}
_fila = threading.Semaphore(1)            # um pedido de cada vez
_ritmo = threading.Lock()
_ultimo = [0.0]
INTERVALO = 3.0                           # segundos entre pedidos (o INE limita com pouca margem)
ESPERAS = [30, 60, 120, 240, 300, 300]    # pausas quando o INE recusa (429 ou ligação recusada)


def _python(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def _powershell(url, timeout):
    fd, tmp = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    ps = ("$ErrorActionPreference='Stop';"
          "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12;"
          "$w=New-Object System.Net.WebClient;"
          f"$w.Headers.Add('User-Agent','{UA}');"
          "$p=[System.Net.WebRequest]::GetSystemWebProxy();"
          "$p.Credentials=[System.Net.CredentialCache]::DefaultNetworkCredentials;"
          "$w.Proxy=$p;"
          f"$w.DownloadFile('{url}','{tmp}')")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                           capture_output=True, timeout=timeout + 15,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        if r.returncode != 0:
            raise RuntimeError("PowerShell: " + (r.stderr or r.stdout).decode("utf-8", "replace").strip()[:300])
        return Path(tmp).read_bytes()
    finally:
        try:
            os.remove(tmp)
        except OSError:
            pass


def _uma(url, timeout):
    """O modo (Python direto ou proxy do Windows) decide-se no 1.º pedido e fica fixo:
    falhas posteriores são o INE a limitar, não a rede — trocar de modo não ajuda."""
    if VIA["modo"] == "powershell":
        return _powershell(url, timeout)
    if VIA["modo"] == "python":
        return _python(url, timeout)
    try:
        b = _python(url, 20)
        VIA["modo"] = "python"
        return b
    except Exception as e:
        if os.name != "nt":
            raise
        log(f"ligação direta falhou ({type(e).__name__}) — a tentar pelo proxy do Windows")
        b = _powershell(url, timeout)
        VIA["modo"] = "powershell"
        return b


def http_get(url, timeout=120):
    for tentativa in range(len(ESPERAS) + 1):
        with _fila:
            with _ritmo:
                falta = _ultimo[0] + INTERVALO - time.time()
                if falta > 0:
                    time.sleep(falta)
                _ultimo[0] = time.time()
            try:
                return _uma(url, timeout).decode("utf-8")
            except Exception as e:
                if tentativa == len(ESPERAS):
                    raise
                motivo = "429 — demasiados pedidos" if "429" in str(e) else f"{type(e).__name__}: {str(e)[:80]}"
                espera = ESPERAS[tentativa]
                log(f"INE recusou ({motivo}) — pausa de {espera}s e nova tentativa ({tentativa + 1}/{len(ESPERAS)})")
                _ultimo[0] = time.time() + espera
        time.sleep(espera)


# ------------------------------------------------------------------ INE
def categorias(no):
    if isinstance(no, dict):
        if "categ_cod" in no and "dim_num" in no:
            yield no
        else:
            for v in no.values():
                yield from categorias(v)
    elif isinstance(no, list):
        for v in no:
            yield from categorias(v)


def ler_meta(varcd, texto=None):
    texto = texto or http_get(f"{BASE_META}?varcd={varcd}&lang=PT")
    m = json.loads(texto)
    m = m[0] if isinstance(m, list) else m
    if not m or "IndicadorCod" not in m:
        raise ValueError("indicador não encontrado")
    dims = {}
    for c in categorias(m.get("Dimensoes", {}).get("Categoria_Dim")):
        dims.setdefault(str(c["dim_num"]), []).append(c)
    if "1" in dims:
        dims["1"].sort(key=lambda c: c.get("categ_ord") or "")
    return texto, m, dims


def resolver_geos(dims, geos):
    cats = dims.get("2", [])
    por_cod = {c["categ_cod"] for c in cats}
    por_nome = {norm(c["categ_dsg"]): c["categ_cod"] for c in cats}
    achados, falta = [], []
    for g in geos:
        cod = next((c for c in [g.get("cod")] + g.get("alt", []) if c and c in por_cod), None)
        cod = cod or por_nome.get(norm(g["nome"]))
        (achados if cod else falta).append(cod or g["nome"])
    return achados, falta


def url_dados(varcd, dim1, dim2):
    params = {"op": "2", "varcd": varcd, "lang": "PT", "Dim1": ",".join(dim1), "Dim2": ",".join(dim2)}
    return BASE_DADOS + "?" + urllib.parse.urlencode(params, safe=",")


def pedir(varcd, dim1, dim2):
    url = url_dados(varcd, dim1, dim2)
    texto = http_get(url)
    r = json.loads(texto)
    r = r[0] if isinstance(r, list) else r
    suc = r.get("Sucesso") or {}
    if "Falso" in suc:
        raise ValueError("; ".join(x.get("Msg", "") for x in suc["Falso"]) or "recusado")
    return url, texto, sum(len(v) for v in (r.get("Dados") or {}).values())


# ------------------------------------------------------------------ gravação
def gravar(pasta, nome, texto):
    f = pasta / nome
    if f.exists():
        return False
    f.write_text(texto, encoding="utf-8")
    return True


def extrair_indicador(varcd, nome, geos, n_periodos, completo, pasta):
    res = {"varcd": varcd, "nome": nome, "ficheiros": [], "valores": 0, "falhas": [], "geos_em_falta": []}
    try:
        f_meta = pasta / f"{varcd}_meta.json"
        if f_meta.exists():                                   # retoma: metadados já gravados hoje
            meta_txt = f_meta.read_text(encoding="utf-8")
            _, meta, dims = ler_meta(varcd, meta_txt)
        else:
            meta_txt, meta, dims = ler_meta(varcd)
            gravar(pasta, f_meta.name, meta_txt)
    except Exception as e:
        res["falhas"].append(f"metadados: {str(e)[:150]}")
        return res
    dim2, res["geos_em_falta"] = resolver_geos(dims, geos)
    if not dim2:
        res["falhas"].append("nenhuma das geografias existe neste indicador")
        return res
    periodos = [c["categ_cod"] for c in dims.get("1", [])]
    if not completo:
        periodos = periodos[-n_periodos:]
    por_periodo = len(dim2)
    for n, cats in dims.items():
        if n not in ("1", "2"):
            por_periodo *= max(1, len(cats))
    bloco = max(1, min(len(periodos), MAX_VALORES // max(1, por_periodo)))
    def um_pedido(p):
        url = url_dados(varcd, p, dim2)
        nome_f = f"{varcd}_dados_{hashlib.sha256(url.encode()).hexdigest()[:10]}.json"
        if (pasta / nome_f).exists():                          # retoma: já gravado hoje, não volta a pedir
            res["ja_existiam"] = res.get("ja_existiam", 0) + 1
            return
        url, texto, n = pedir(varcd, p, dim2)
        if gravar(pasta, nome_f, texto):
            res["ficheiros"].append((nome_f, url))
        res["valores"] += n

    for k in range(0, len(periodos), bloco):
        parte = periodos[k:k + bloco]
        try:
            um_pedido(parte)
        except Exception as e:
            if len(parte) == 1:
                res["falhas"].append(f"{parte[0]}: {str(e)[:150]}")
                continue
            for p in parte:                            # bloco recusado -> período a período
                try:
                    um_pedido([p])
                except Exception as e2:
                    res["falhas"].append(f"{p}: {str(e2)[:150]}")
    return res


def escrever_entrega(pasta, resultados, completo, geos):
    f = pasta / "_entrega.md"
    if not f.exists():
        f.write_text(
            f"# Entrega — INE — {pasta.name}\n\n"
            "- **Enviado por:** API JSON do INE (extração própria do DIIET, script 3_scripts/extrair_ine.py)\n"
            f"- **Recebido em:** {pasta.name}\n"
            "- **Data de extração (da fonte):** campo `DataExtracao` de cada ficheiro\n"
            "- **Âmbito:** ver extrações abaixo\n"
            "- **Contrato / base legal:** \n"
            "- **Ficheiros:** `<varcd>_dados_<hash>.json` (resposta de dados, exatamente como devolvida) e `<varcd>_meta.json` (metadados)\n"
            "- **Notas da ficha técnica:** ver `MetaInfUrl` em cada ficheiro de dados\n"
            "- **Restrições de reutilização:** \n", encoding="utf-8")
    linhas = [f"\n## Extração — {datetime.now():%Y-%m-%d %H:%M} — {'séries completas' if completo else 'períodos recentes'}",
              f"Geografias pedidas: {', '.join(g['nome'] for g in geos)}. Todas as categorias das restantes dimensões.", ""]
    for r in resultados:
        linhas.append(f"- **{r['varcd']}** {r['nome']} — {r['valores']} valores, {len(r['ficheiros'])} ficheiros novos"
                      + (f"; geografias inexistentes neste indicador: {', '.join(r['geos_em_falta'])}" if r["geos_em_falta"] else "")
                      + (f"; FALHAS: {' | '.join(r['falhas'])}" if r["falhas"] else ""))
        for nome_f, url in r["ficheiros"]:
            linhas.append(f"    - `{nome_f}` ← {url}")
    with f.open("a", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--completo", action="store_true", help="séries completas (todos os períodos)")
    ap.add_argument("--carregar", action="store_true", help="no fim, correr carregar_ine.py")
    ap.add_argument("--so", default="", help="só estes códigos (separados por vírgula)")
    a = ap.parse_args()

    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    vistos, inds = set(), []
    for i in cfg["indicadores"]:
        v = str(i["varcd"]).zfill(7)
        if v not in vistos and (not a.so or v in a.so.split(",")):
            vistos.add(v)
            inds.append((v, i.get("nome", "")))
    pasta = BRUTO / date.today().isoformat()
    pasta.mkdir(parents=True, exist_ok=True)
    log(f"{len(inds)} indicadores · {'séries completas' if a.completo else 'últimos ' + str(cfg.get('periodos', 6)) + ' períodos'} · destino {pasta}")


    resultados = []
    with ThreadPoolExecutor(max_workers=1) as ex:
        for r in ex.map(lambda t: extrair_indicador(t[0], t[1], cfg["geografias"], int(cfg.get("periodos", 6)),
                                                    a.completo, pasta), inds):
            estado = "OK " if not r["falhas"] else "ERRO"
            log(f"{estado} {r['varcd']} {r['nome'][:50]:50} {r['valores']:>7} valores  {len(r['ficheiros'])} novos"
                + (f"  ({r['ja_existiam']} já gravados hoje)" if r.get("ja_existiam") else "")
                + (f"  ! {' | '.join(r['falhas'])[:160]}" if r["falhas"] else ""))
            resultados.append(r)
    escrever_entrega(pasta, resultados, a.completo, cfg["geografias"])
    novos = sum(len(r["ficheiros"]) for r in resultados)
    com_falhas = [r["varcd"] for r in resultados if r["falhas"]]
    log(f"FIM: {novos} ficheiros novos em {pasta.relative_to(SIT)}"
        + (f" · indicadores com falhas: {', '.join(com_falhas)} — volte a correr mais tarde: retoma onde parou"
           if com_falhas else ""))

    if a.carregar:
        sys.path.insert(0, str(AQUI))
        import carregar_ine
        r = carregar_ine.carregar(SIT)
        log(f"carregar_ine: {r['linhas_ine']} linhas INE em indicador_territorio.csv "
            f"({r['ficheiros_novos_registados']} ficheiros novos em carregamento.csv)")
        if r["geos_sem_dicionario"]:
            log(f"geografias sem linha em 0_referencia/geo.csv: {', '.join(r['geos_sem_dicionario'])}")


if __name__ == "__main__":
    main()
