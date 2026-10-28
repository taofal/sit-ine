#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
colheita_ine.py — colheita lenta e contínua de TODO o INE com dados por município, para a SIT.

Cada execução faz uma volta curta (por omissão até 40 pedidos ou 20 minutos) e termina. Corre a cada hora
pelo Agendador de Tarefas do Windows (ver «Instalar colheita INE.bat»). Ao longo de dias cobre todos os
indicadores do catálogo do INE cujo nível geográfico mais fino é o município ou mais fino (freguesia…),
com séries completas e todas as categorias de todas as dimensões, para as geografias de ine_indicadores.json.

Regras:
  - À 1.ª recusa do INE (429 ou ligação recusada) espera 60 s, tenta uma vez e, se voltar a falhar, PÁRA a volta.
    Não insiste: a volta seguinte (daqui a 1 h) continua onde esta ficou.
  - Estado por indicador em 3_scripts/_estado/colheita_ine.csv (abre no Excel):
      pendente → feito | sem_geografia | erro   (com data, períodos, ficheiros, valores e nota)
  - Prioridade: primeiro os indicadores de ine_indicadores.json, depois o resto do catálogo, os mais
    recentes primeiro.
  - Atualização: quando o catálogo (relido de 7 em 7 dias) mostra uma atualização do INE posterior à colheita,
    o indicador volta a «pendente».
  - Respostas gravadas como em extrair_ine.py: 1_bruto/ine/<AAAA-MM-DD>/ + _entrega.md. O catálogo fica em
    1_bruto/ine-catalogo/<AAAA-MM-DD>/catalogo.xml.
  - Não corre carregar_ine.py (o volume cresce muito); correr à mão quando for preciso.

  py colheita_ine.py                    uma volta (é isto que o Agendador corre)
  py colheita_ine.py --pedidos 100      volta maior
  py colheita_ine.py --estado           só mostra o ponto de situação
"""
import argparse
import csv
import io
import re
import sys
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
import extrair_ine as X  # noqa: E402  (rede, metadados, extração e gravação já testadas)

SIT = AQUI.parent
ESTADO_DIR = AQUI / "_estado"
ESTADO = ESTADO_DIR / "colheita_ine.csv"
LOG = ESTADO_DIR / "colheita_ine.log"
CAT_DIR = SIT / "1_bruto" / "ine-catalogo"
# O INE tem mais de um catálogo XML: opc=3 é curto (~330 indicadores); opc=2 é mais amplo. Lêem-se ambos e juntam-se.
CATALOGOS = {"catalogo.xml": "https://www.ine.pt/ine/xml_indic.jsp?opc=3&lang=PT",
             "catalogo_opc2.xml": "https://www.ine.pt/ine/xml_indic.jsp?opc=2&lang=PT"}
NIVEIS_MUNICIPAIS = ("munic", "freguesia", "seccao", "subseccao", "lugar", "concelho")
CAMPOS = ["varcd", "titulo", "tema", "nivel_geo", "ultimo_periodo_ine", "atualizacao_ine", "prioridade",
          "estado", "data_colheita", "periodos", "ficheiros", "valores", "tentativas", "nota"]


class Parar(Exception):
    pass


def log(msg):
    linha = f"{datetime.now():%Y-%m-%d %H:%M:%S}  {msg}"
    print(linha, flush=True)
    ESTADO_DIR.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(linha + "\n")


# ------------------------------------------------------------------ rede: parar à 1.ª recusa persistente
_estado_rede = {"parado": False, "pedidos": 0, "limite": 40, "fim": None, "motivo": ""}

# Ordem do catálogo por tema (1 = lista DIIET em ine_indicadores.json, sempre primeiro)
TEMAS_PRIORIDADE = {
    2: ("empresas", "mercado de trabalho", "turismo", "comercio internacional", "industria e energia",
        "inovacao e conhecimento", "educacao, formacao e aprendizagem", "condicoes de vida e cidadania"),
    3: ("populacao", "construcao e habitacao", "territorio", "agricultura, floresta e pescas",
        "transportes e comunicacoes", "cultura, desporto e lazer", "ambiente", "administracoes publicas"),
}


def prioridade_tema(tema):
    t = X.norm(tema)
    for p, temas in TEMAS_PRIORIDADE.items():
        if t in temas:
            return p
    return 4
_http_original = X.http_get


def http_get_cauteloso(url, timeout=120):
    if _estado_rede["parado"]:
        raise Parar("volta parada")
    if _estado_rede["pedidos"] >= _estado_rede["limite"] or time.time() > _estado_rede["fim"]:
        _estado_rede["parado"], _estado_rede["motivo"] = True, "orçamento"
        raise Parar("orçamento da volta esgotado")
    _estado_rede["pedidos"] += 1
    try:
        return _http_original(url, timeout)
    except Exception as e:
        _estado_rede["parado"], _estado_rede["motivo"] = True, f"falha: {str(e)[:150]}"
        raise Parar(f"INE recusou: {str(e)[:150]}")


def ine_responde():
    """Pedido de controlo (metadados de um indicador conhecido): distingue «o INE recusa tudo» de
    «este indicador dá erro»."""
    if _estado_rede["pedidos"] >= _estado_rede["limite"] or time.time() > _estado_rede["fim"]:
        return False
    _estado_rede["pedidos"] += 1
    try:
        _http_original(f"{X.BASE_META}?varcd=0008273&lang=PT", 60)
        return True
    except Exception:
        return False


X.http_get = http_get_cauteloso
X.ESPERAS = [60]          # uma só espera de 60 s; depois pára a volta
X.INTERVALO = 5.0         # 5 s entre pedidos


# ------------------------------------------------------------------ estado
def ler_estado():
    if not ESTADO.exists():
        return {}
    with ESTADO.open(encoding="utf-8-sig", newline="") as fh:
        return {r["varcd"]: r for r in csv.DictReader(fh, delimiter=";")}


def gravar_estado(est):
    ESTADO_DIR.mkdir(exist_ok=True)
    tmp = ESTADO.with_suffix(".tmp")
    linhas = sorted(est.values(), key=lambda r: (int(r.get("prioridade") or 9), r["varcd"]))
    with tmp.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=CAMPOS, delimiter=";", extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)
    try:
        tmp.replace(ESTADO)
    except PermissionError:
        log("AVISO: colheita_ine.csv está aberto no Excel — estado gravado em colheita_ine.tmp; feche o Excel")


# ------------------------------------------------------------------ catálogo
def catalogo_mais_recente(nome):
    xs = sorted(CAT_DIR.glob(f"*/{nome}"))
    return xs[-1] if xs else None


def atualizar_catalogo(est, cfg):
    feito = False
    for nome, url in CATALOGOS.items():
        f = catalogo_mais_recente(nome)
        if f and date.fromisoformat(f.parent.name) > date.today() - timedelta(days=7):
            continue
        log(f"a descarregar o catálogo do INE {nome} (1 pedido, pode demorar)")
        texto = X.http_get(url, timeout=900)
        pasta = CAT_DIR / date.today().isoformat()
        pasta.mkdir(parents=True, exist_ok=True)
        X.gravar(pasta, nome, texto)
        if not (pasta / "_entrega.md").exists():
            (pasta / "_entrega.md").write_text(
                f"# Entrega — INE (catálogos de indicadores) — {pasta.name}\n\n"
                "- **Enviado por:** INE, xml_indic.jsp (colheita_ine.py)\n"
                f"- **Recebido em:** {pasta.name}\n"
                "- **Âmbito:** catálogos de indicadores (código, tema, nível geográfico, último período, última atualização)\n"
                "- **Contrato / base legal:** \n- **Restrições de reutilização:** \n", encoding="utf-8")
        with (pasta / "_entrega.md").open("a", encoding="utf-8") as fh:
            fh.write(f"- `{nome}` ← {url}\n")
        integrar_catalogo(est, cfg, texto, nome)
        feito = True
    return feito


def integrar_catalogo(est, cfg, texto, nome=""):
    prioritarios = {str(i["varcd"]).zfill(7) for i in cfg["indicadores"]}
    novos = reabertos = 0
    total = 0
    try:
        eventos = list(ET.iterparse(io.BytesIO(texto.encode("utf-8")), events=("end",)))
    except ET.ParseError as e:                     # catálogo cortado/malformado: aproveita o que der
        log(f"AVISO: {nome} malformado ({e}) — a aproveitar os indicadores completos")
        eventos = []
        for bloco in re.findall(r"<indicator\b.*?</indicator>", texto, flags=re.S):
            try:
                eventos.append(("end", ET.fromstring(bloco)))
            except ET.ParseError:
                pass
    for _, el in eventos:
        if el.tag != "indicator":
            continue
        total += 1
        t = lambda tag: (el.findtext(tag) or "").strip()  # noqa: E731
        varcd = (t("varcd") or el.get("id") or "").zfill(7)
        nivel = t("geo_lastlevel")
        if not varcd.strip("0") or not any(n in X.norm(nivel) for n in NIVEIS_MUNICIPAIS):
            el.clear()
            continue
        atual = (el.findtext("dates/last_update") or "").strip()
        r = est.get(varcd)
        if r is None:
            est[varcd] = r = {"varcd": varcd, "estado": "pendente", "tentativas": "0"}
            novos += 1
        elif r.get("estado") == "feito" and atual and r.get("data_colheita") and atual[:10] > r["data_colheita"]:
            r["estado"], r["nota"] = "pendente", f"INE atualizou a {atual[:10]}"
            reabertos += 1
        r.update({"titulo": t("title"), "tema": t("theme"), "nivel_geo": nivel,
                  "ultimo_periodo_ine": (el.findtext("dates/last_period_available") or "").strip(),
                  "atualizacao_ine": atual, "prioridade": "1" if varcd in prioritarios else "2"})
        el.clear()
    for v in prioritarios:                      # os da lista entram mesmo que o catálogo os classifique de outra forma
        if v not in est:
            est[v] = {"varcd": v, "estado": "pendente", "tentativas": "0", "prioridade": "1"}
            novos += 1
    log(f"catálogo {nome} integrado: {total} indicadores no catálogo, {novos} novos com nível municipal, "
        f"{reabertos} reabertos por atualização do INE")


def fila(est):
    for r in est.values():
        if r.get("prioridade") != "1":
            r["prioridade"] = str(prioridade_tema(r.get("tema", "")))
    pend = [r for r in est.values() if r.get("estado") == "pendente" or
            (r.get("estado") == "erro" and int(r.get("tentativas") or 0) < MAX_TENTATIVAS)]
    pend.sort(key=lambda r: r.get("atualizacao_ine") or "", reverse=True)          # mais recentes primeiro
    pend.sort(key=lambda r: (int(r.get("prioridade") or 9), r.get("estado") == "erro"))  # lista DIIET e temas DIIET primeiro; erros no fim
    return pend


MAX_TENTATIVAS = 3


def ponto_de_situacao(est):
    from collections import Counter
    c = Counter(r.get("estado") for r in est.values())
    return " · ".join(f"{k}: {v}" for k, v in sorted(c.items())) or "vazio"


# ------------------------------------------------------------------ volta
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pedidos", type=int, default=40)
    ap.add_argument("--minutos", type=int, default=20)
    ap.add_argument("--estado", action="store_true")
    a = ap.parse_args()

    import json
    cfg = json.loads(X.CONFIG.read_text(encoding="utf-8"))
    est = ler_estado()
    if a.estado:
        print(ponto_de_situacao(est))
        return
    _estado_rede.update(limite=a.pedidos, fim=time.time() + a.minutos * 60)
    log(f"--- volta: até {a.pedidos} pedidos / {a.minutos} min · {ponto_de_situacao(est)}")

    try:
        if not est:                                     # 1.ª volta: os da lista entram já, o catálogo a seguir
            for i in cfg["indicadores"]:
                v = str(i["varcd"]).zfill(7)  # noqa
                est.setdefault(v, {"varcd": v, "titulo": i.get("nome", ""), "estado": "pendente",
                                   "tentativas": "0", "prioridade": "1"})
        atualizar_catalogo(est, cfg)
    except Parar as e:
        log(f"catálogo adiado: {e}")
    gravar_estado(est)

    pasta = X.BRUTO / date.today().isoformat()
    pasta.mkdir(parents=True, exist_ok=True)
    resultados = []
    for r in fila(est):
        if _estado_rede["parado"]:
            break
        res = X.extrair_indicador(r["varcd"], r.get("titulo", ""), cfg["geografias"], 0, True, pasta)
        resultados.append(res)
        parou = _estado_rede["parado"]
        if parou and _estado_rede["motivo"].startswith("falha"):
            erro = _estado_rede["motivo"]
            _estado_rede.update(parado=False, motivo="")
            if ine_responde():                         # o INE responde: o erro é deste indicador, não um bloqueio
                n = int(r.get("tentativas") or 0) + 1
                r.update(tentativas=str(n), estado="erro",
                         nota=f"erro neste indicador ({n}/{MAX_TENTATIVAS}): {erro[7:200]}")
                log(f"erro          {r['varcd']} {(r.get('titulo') or '')[:60]:60}  — o INE responde a outros pedidos; "
                    f"segue para o próximo ({n}/{MAX_TENTATIVAS})")
                gravar_estado(est)
                continue
            _estado_rede.update(parado=True, motivo=erro)
        r["tentativas"] = str(int(r.get("tentativas") or 0) + (0 if parou else 1))
        if parou:
            r["nota"] = "interrompido a meio; retoma na próxima volta"
        elif not res["falhas"]:
            r.update(estado="feito", data_colheita=date.today().isoformat(), ficheiros=str(len(res["ficheiros"])),
                     valores=str(res["valores"]), tentativas="0",
                     nota=(f"geografias inexistentes: {', '.join(res['geos_em_falta'])}" if res["geos_em_falta"] else ""))
        elif any("nenhuma das geografias" in f for f in res["falhas"]):
            r.update(estado="sem_geografia", data_colheita=date.today().isoformat(),
                     nota="nenhuma das geografias pedidas existe neste indicador")
        else:
            r.update(estado="erro", nota=" | ".join(res["falhas"])[:300])
        log(f"{r['estado']:13} {r['varcd']} {(r.get('titulo') or '')[:60]:60} {res['valores']:>8} valores"
            + (f"  ({r['nota'][:80]})" if r.get("nota") else ""))
        gravar_estado(est)

    if resultados:
        X.escrever_entrega(pasta, [x for x in resultados if x["ficheiros"] or x["falhas"]], True, cfg["geografias"])
    motivo = ("INE recusou — pára até à próxima volta" if _estado_rede["motivo"].startswith("falha")
              else "fim da volta (limite de pedidos/tempo)" if _estado_rede["motivo"] == "orçamento"
              else "fim da volta (fila vazia)")
    log(f"--- {motivo}: {_estado_rede['pedidos']} pedidos · {ponto_de_situacao(est)}")


if __name__ == "__main__":
    main()
