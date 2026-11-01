"""Descarrega da API do BPstat (Banco de Portugal) os domínios territoriais úteis ao SIT.

Fonte: https://bpstat.bportugal.pt/data/v1  (API pública, sem registo; JSON-stat 2.0)
Domínios (todas as geografias que o BP publica: Portugal, NUTS II, NUTS III):
  178  Indicadores económicos e financeiros das empresas por região (Central de Balanços, anual)
  188  Empréstimos (por região do devedor; SNF e famílias; inclui crédito vencido; mensal)
  206  Depósitos (por região do balcão; mensal)

Grava em 1_bruto/bportugal/AAAA-MM-DD/ (data de hoje):
  _entrega.md                         data de extração e data de atualização de cada domínio no BP
  d<dom>/dominio.json                 metadados do domínio (inclui obs_updated_at)
  d<dom>/dimensoes.json               lista de dimensões; d<dom>/dim_<id>.json membros de cada uma
  d<dom>/datasets.json                lista de datasets
  d<dom>/<dataset>_p<NNN>.json        páginas de dados (100 séries por página, o máximo da API)

Só descarrega um domínio se o BP o atualizou depois da última extração guardada (obs_updated_at
diferente); se nenhum mudou, não cria pasta. --forcar descarrega tudo.
Corrido de novo no mesmo dia, salta os ficheiros que já existem (retoma onde parou).
Corre igual no computador (Windows: curl.exe --ssl-no-revoke, por causa do certificado da rede)
e no GitHub (repositório taofal/sit-ine, .github/workflows/colheita_bportugal.yml).
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

API = "https://bpstat.bportugal.pt/data/v1"
DOMINIOS = [178, 188, 206]
CURL = shutil.which("curl.exe") or shutil.which("curl")


def raiz() -> Path:
    """Raiz do SIT (ou do repositório): a pasta-mãe de 3_scripts."""
    return Path(__file__).resolve().parent.parent


def hoje() -> str:
    return date.today().strftime("%Y-%m-%d")


def obter(url: str, tentativas: int = 4) -> dict:
    """GET → JSON, com repetições. curl se existir; senão urllib."""
    ultimo = None
    for t in range(tentativas):
        try:
            if CURL:
                cmd = [CURL, "-s", "-f", "-L", "-m", "120", url]
                if sys.platform == "win32":
                    cmd.insert(1, "--ssl-no-revoke")
                out = subprocess.run(cmd, capture_output=True, check=True).stdout
            else:
                import urllib.request
                with urllib.request.urlopen(url, timeout=120) as r:
                    out = r.read()
            return json.loads(out.decode("utf-8"))
        except Exception as e:  # noqa: BLE001 — a rede falha às vezes; repetir
            ultimo = e
            time.sleep(3 * (t + 1))
    raise SystemExit(f"Falhou depois de {tentativas} tentativas: {url}\n{ultimo}")


def guardar(p: Path, url: str) -> dict:
    """Descarrega para p (se ainda não existir) e devolve o JSON."""
    if p.exists() and p.stat().st_size > 0:
        return json.loads(p.read_text(encoding="utf-8"))
    d = obter(url)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    return d


def todas_paginas(url: str) -> list:
    """Listas paginadas (dimensões): junta os 'item' de todas as páginas."""
    itens = []
    while url:
        d = obter(url)
        itens += d.get("link", {}).get("item", [])
        url = d.get("extension", {}).get("next_page")
    return itens


def ultima_atualizacao(bruto: Path, dom: int, antes_de: str) -> str:
    """obs_updated_at da extração completa mais recente do domínio, anterior a hoje ('' se não houver)."""
    for pasta in sorted((p for p in bruto.glob("????-??-??") if p.name < antes_de), reverse=True):
        f = pasta / f"d{dom}" / "dominio.json"
        if f.exists() and any((pasta / f"d{dom}").glob("*_p*.json")):
            return json.loads(f.read_text(encoding="utf-8")).get("obs_updated_at", "")
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forcar", action="store_true", help="descarregar mesmo os domínios sem atualização")
    a = ap.parse_args()

    r = raiz()
    bruto = r / "1_bruto" / "bportugal"
    pasta = bruto / hoje()
    resumo = []
    for dom in DOMINIOS:
        meta = obter(f"{API}/domains/{dom}/?lang=PT")
        atual, anterior = meta.get("obs_updated_at", ""), ultima_atualizacao(bruto, dom, hoje())
        if atual and atual == anterior and not a.forcar:
            print(f"  d{dom} {meta['label']}: sem atualização no BP desde {anterior[:10]} — salta")
            continue
        pd_ = pasta / f"d{dom}"
        pd_.mkdir(parents=True, exist_ok=True)
        (pd_ / "dominio.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
        # dimensões e respetivos membros (servem de dicionário ao carregador)
        fdim = pd_ / "dimensoes.json"
        if not fdim.exists():
            fdim.write_text(json.dumps(todas_paginas(f"{API}/domains/{dom}/dimensions/?lang=PT"),
                                       ensure_ascii=False), encoding="utf-8")
        for d in json.loads(fdim.read_text(encoding="utf-8")):
            did = d["extension"]["id"]
            guardar(pd_ / f"dim_{did}.json", f"{API}/domains/{dom}/dimensions/{did}/?lang=PT")
        # datasets → páginas de dados
        dsl = guardar(pd_ / "datasets.json", f"{API}/domains/{dom}/datasets/?lang=PT")
        n_series = n_pag = 0
        for it in dsl["link"]["item"]:
            dsid = it["extension"]["id"]
            url, pag = f"{API}/domains/{dom}/datasets/{dsid}/?lang=PT&page_size=100", 1
            while url:
                d = guardar(pd_ / f"{dsid}_p{pag:03d}.json", url)
                n_series += len(d.get("extension", {}).get("series", []))
                url, pag = d.get("extension", {}).get("next_page"), pag + 1
                n_pag += 1
        esperado = meta.get("num_series")
        print(f"  d{dom} {meta['label']}: {n_series} séries em {n_pag} páginas (BP indica {esperado}; "
              f"atualizado no BP a {atual[:10]})")
        if esperado and n_series != esperado:
            print(f"  AVISO: d{dom} — número de séries descarregadas difere do anunciado")
        resumo.append((dom, meta["label"], atual, n_series))

    if not resumo:
        print("Nenhum domínio atualizado pelo BP desde a última extração — nada gravado.")
        return
    linhas = [f"# Entrega — Banco de Portugal, BPstat (API) — {hoje()}", "",
              "- **Enviado por:** colheita própria (`3_scripts/extrair_bportugal.py`)",
              f"- **Recebido em:** {hoje()}",
              f"- **Data de extração (da fonte):** {hoje()}",
              "- **Âmbito:** Portugal, NUTS II e NUTS III (todas as geografias publicadas); sociedades não financeiras e famílias",
              "- **Contrato / base legal:** dados abertos do Banco de Portugal (BPstat)",
              "- **Ficheiros:** um subdiretório por domínio atualizado (domínio, dimensões, datasets, páginas JSON-stat)",
              "- **Notas da ficha técnica:** metainformação de cada dimensão em `dim_<id>.json`",
              "- **Restrições de reutilização:** citar a fonte (Banco de Portugal, BPstat)", "",
              "| Domínio | Designação | Atualizado no BP | Séries |", "|---|---|---|---:|"]
    linhas += [f"| {d} | {l} | {u} | {n} |" for d, l, u, n in resumo]
    (pasta / "_entrega.md").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Gravado em {pasta.relative_to(r)}")


if __name__ == "__main__":
    main()
