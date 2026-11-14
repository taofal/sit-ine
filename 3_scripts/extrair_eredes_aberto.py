"""Descarrega do portal de dados abertos da E-Redes os consumos mensais de eletricidade.

Fonte: https://e-redes.opendatasoft.com  (API pública Opendatasoft «explore v2.1», sem registo; licença CC BY 4.0)
Conjuntos de dados (lista CONJUNTOS, em baixo):
  3-consumos-faturados-por-municipio-ultimos-10-anos   energia ativa faturada por mês, distrito, concelho,
                                                       freguesia e nível de tensão (todo o país)
  consumo-total-nacional                               consumo nacional por nível de tensão (termo de comparação)

Grava em 1_bruto/eredes-aberto/AAAA-MM-DD/<conjunto>/ (data de hoje):
  conjunto.json     metadados tal como a API os devolve (campos, n.º de registos, data de processamento)
  dados.csv.gz      exportação completa em CSV (separador «;»), tal como devolvida, comprimida com gzip
  _entrega.md       (na pasta da data) o que foi descarregado, com o URL de cada pedido

Só descarrega um conjunto se a E-Redes o processou depois da última extração guardada (data de
processamento diferente); se nenhum mudou, não cria pasta. --forcar descarrega tudo.
1_bruto só se acrescenta: um ficheiro que já exista nunca é reescrito.
Corre igual num computador (Windows: curl.exe --ssl-no-revoke) e no agendamento do repositório da colheita.
Só biblioteca padrão (Python 3.8+).
"""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import date
from pathlib import Path

API = "https://e-redes.opendatasoft.com/api/explore/v2.1/catalog/datasets"
CONJUNTOS = [
    "3-consumos-faturados-por-municipio-ultimos-10-anos",
    "consumo-total-nacional",
]
CURL = shutil.which("curl.exe") or shutil.which("curl")
LIMITE_MB = 95          # o GitHub recusa ficheiros de 100 MB ou mais


def raiz() -> Path:
    """Raiz da base local (ou do repositório): a pasta-mãe de 3_scripts."""
    return Path(__file__).resolve().parent.parent


def hoje() -> str:
    return date.today().strftime("%Y-%m-%d")


def descarregar(url: str, destino: Path, tentativas: int = 4) -> None:
    """GET → ficheiro, com repetições. curl se existir; senão urllib."""
    ultimo = None
    for t in range(tentativas):
        try:
            if CURL:
                cmd = [CURL, "-s", "-S", "-f", "-L", "-m", "900", "-o", str(destino), url]
                if sys.platform == "win32":
                    cmd.insert(1, "--ssl-no-revoke")
                subprocess.run(cmd, capture_output=True, check=True)
            else:
                import urllib.request
                with urllib.request.urlopen(url, timeout=900) as r, destino.open("wb") as fh:
                    shutil.copyfileobj(r, fh, 1 << 20)
            if destino.stat().st_size > 0:
                return
            ultimo = "resposta vazia"
        except Exception as e:  # noqa: BLE001 — a rede falha às vezes; repetir
            ultimo = getattr(e, "stderr", b"") or e
        time.sleep(5 * (t + 1))
    raise SystemExit(f"Falhou depois de {tentativas} tentativas: {url}\n{ultimo}")


def processado(meta: dict) -> str:
    """Data em que a E-Redes processou os dados pela última vez (ou, na falta, a de modificação)."""
    m = (meta.get("metas") or {}).get("default") or {}
    return str(m.get("data_processed") or m.get("modified") or "")


def ultimo_processado(bruto: Path, conj: str, antes_de: str) -> str:
    """Data de processamento da extração completa mais recente do conjunto, anterior a hoje."""
    for pasta in sorted((p for p in bruto.glob("????-??-??") if p.name < antes_de), reverse=True):
        f = pasta / conj / "conjunto.json"
        if f.exists() and (pasta / conj / "dados.csv.gz").exists():
            return processado(json.loads(f.read_text(encoding="utf-8")))
    return ""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--forcar", action="store_true", help="descarregar mesmo os conjuntos sem atualização")
    a = ap.parse_args()

    r = raiz()
    bruto = r / "1_bruto" / "eredes-aberto"
    pasta = bruto / hoje()
    resumo = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for conj in CONJUNTOS:
            url_meta = f"{API}/{conj}"
            fmeta = tmp / f"{conj}.json"
            descarregar(url_meta, fmeta)
            meta = json.loads(fmeta.read_text(encoding="utf-8"))
            atual, anterior = processado(meta), ultimo_processado(bruto, conj, hoje())
            if atual and atual == anterior and not a.forcar:
                print(f"  {conj}: sem atualização na E-Redes desde {anterior[:10]} — salta")
                continue
            pc = pasta / conj
            fdados = pc / "dados.csv.gz"
            if fdados.exists():
                print(f"  {conj}: já descarregado hoje — salta")
                continue
            url_dados = f"{url_meta}/exports/csv?delimiter=%3B"
            fcsv = tmp / f"{conj}.csv"
            descarregar(url_dados, fcsv)
            with fcsv.open("rb") as fh:
                linhas = sum(1 for _ in fh) - 1
            pc.mkdir(parents=True, exist_ok=True)
            if not (pc / "conjunto.json").exists():
                shutil.copyfile(fmeta, pc / "conjunto.json")
            with fcsv.open("rb") as fi, gzip.open(fdados, "wb", compresslevel=9) as fo:
                shutil.copyfileobj(fi, fo, 1 << 20)
            mb = fdados.stat().st_size / 1e6
            esperado = ((meta.get("metas") or {}).get("default") or {}).get("records_count")
            campos = [c.get("name") for c in meta.get("fields", [])]
            print(f"  {conj}: {linhas} registos ({mb:.1f} MB comprimido; a E-Redes indica {esperado}; "
                  f"processado a {atual[:10]}); campos: {', '.join(map(str, campos))}")
            if esperado and linhas != esperado:
                print(f"  AVISO: {conj} — n.º de registos descarregados difere do anunciado")
            if mb > LIMITE_MB:
                print(f"  AVISO: {conj} — ficheiro acima de {LIMITE_MB} MB; o GitHub pode recusá-lo")
            resumo.append((conj, atual, linhas, esperado, url_meta, url_dados, campos))

    if not resumo:
        print("Nenhum conjunto atualizado pela E-Redes desde a última extração — nada gravado.")
        return
    fent = pasta / "_entrega.md"
    if not fent.exists():
        ls = [f"# Entrega — E-Redes, portal de dados abertos (API) — {hoje()}", "",
              "- **Enviado por:** colheita própria (`3_scripts/extrair_eredes_aberto.py`)",
              f"- **Recebido em:** {hoje()}",
              f"- **Data de extração (da fonte):** {hoje()}",
              "- **Âmbito:** todo o país (o que a E-Redes publica); consumo mensal de energia ativa faturada",
              "- **Contrato / base legal:** dados abertos da E-Redes (licença CC BY 4.0)",
              "- **Ficheiros:** um subdiretório por conjunto atualizado (`conjunto.json`, `dados.csv.gz`)",
              "- **Notas da ficha técnica:** ano e mês referem-se ao período de consumo, não à data de faturação; "
              "valores aproximados e sujeitos a revisão; por proteção de dados, parte do consumo pode vir agregada "
              "em categorias «OUTROS»",
              "- **Restrições de reutilização:** citar a fonte (E-REDES – Distribuição de Eletricidade, "
              "«Portal Open Data E-REDES»)", "",
              "| Conjunto | Processado na E-Redes | Registos | Anunciados | Campos |", "|---|---|---:|---:|---|"]
        ls += [f"| {c} | {u} | {n} | {e} | {', '.join(map(str, k))} |" for c, u, n, e, _, _, k in resumo]
        ls += ["", "Pedidos:"] + [f"- {x}" for _, _, _, _, um, ud, _ in resumo for x in (um, ud)]
        fent.write_text("\n".join(ls) + "\n", encoding="utf-8")
    print(f"Gravado em {pasta.relative_to(r)}")


if __name__ == "__main__":
    main()
