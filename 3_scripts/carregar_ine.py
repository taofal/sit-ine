#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
carregar_ine.py — fonte INE → 2_normalizado/indicador_territorio.csv

Lê todas as respostas guardadas em 1_bruto/ine/<AAAA-MM-DD>/ (ficheiros <varcd>_dados_*.json e
<varcd>_meta.json, gravados pela interface 3_scripts/ine/), reconstrói por inteiro as linhas com
fonte = INE em indicador_territorio.csv e regista cada ficheiro em 0_referencia/carregamento.csv.

Idempotente: correr duas vezes dá o mesmo resultado. As linhas de outras fontes não são tocadas.

  python carregar_ine.py            (a partir de 3_scripts/, ou com o caminho da SIT: --sit <pasta>)

Convenções aplicadas (README da SIT):
  - indicador  = INE_<varcd>|d3=<cód>|d4=<cód>…   (as dimensões além de período e local fazem parte da identidade)
  - geo_id     = geo_id de 0_referencia/geo.csv pelo codigo_ine; se ainda não houver linha, fica o próprio código INE
  - períodos   = periodo_tipo + periodo_inicio + periodo_fim em datas reais, a partir dos códigos do INE
                 (S7A2023 ano · S3A202608 mês · S5A20234 trimestre)
  - valores confidenciais/ausentes do INE não geram linha
  - derivado = 0 (tudo o que vem daqui é valor publicado pelo INE)
"""
import argparse
import calendar
import csv
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path

VERSAO = "1.0"
FONTE = "INE"
CAB_IT = ["geo_id", "periodo_tipo", "periodo_inicio", "periodo_fim", "indicador", "valor", "unidade",
          "agregacao", "derivado", "fonte", "data_extracao", "carregamento_id"]
CAB_CARGA = ["id", "fonte", "ficheiro", "hash_sha256", "data_extracao", "data_carga", "n_linhas",
             "script", "versao_script", "notas"]


def ler_csv(f):
    if not f.exists():
        return []
    with f.open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def escrever_csv(f, cab, linhas):
    tmp = f.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cab, extrasaction="ignore")
        w.writeheader()
        w.writerows(linhas)
    tmp.replace(f)


def periodo(cod, rotulo):
    """Código de período do INE -> (tipo, início, fim)."""
    m = re.fullmatch(r"S7A(\d{4})", cod or "")
    if m:
        a = int(m.group(1))
        return "ano", date(a, 1, 1), date(a, 12, 31)
    m = re.fullmatch(r"S3A(\d{4})(\d{2})", cod or "")
    if m:
        a, mes = int(m.group(1)), int(m.group(2))
        return "mes", date(a, mes, 1), date(a, mes, calendar.monthrange(a, mes)[1])
    m = re.fullmatch(r"S5A(\d{4})([1-4])", cod or "")
    if m:
        a, t = int(m.group(1)), int(m.group(2))
        return "trimestre", date(a, 3 * t - 2, 1), date(a, 3 * t, calendar.monthrange(a, 3 * t)[1])
    m = re.search(r"(\d{4})\s*/\s*(\d{4})", rotulo or "")        # ano letivo 2025/2026
    if m:
        return "ano_letivo", date(int(m.group(1)), 9, 1), date(int(m.group(2)), 8, 31)
    m = re.fullmatch(r"\d{4}", (rotulo or "").strip())
    if m:
        a = int(rotulo)
        return "ano", date(a, 1, 1), date(a, 12, 31)
    return None


def categorias(no):
    """Percorre Categoria_Dim seja qual for a forma (dict de listas, lista de dicts, aninhado)."""
    if isinstance(no, dict):
        if "categ_cod" in no and "dim_num" in no:
            yield no
        else:
            for v in no.values():
                yield from categorias(v)
    elif isinstance(no, list):
        for v in no:
            yield from categorias(v)


def numero(v):
    s = str(v if v is not None else "").strip()
    try:
        return float(s.replace(",", "."))
    except ValueError:
        return None


def carregar(sit):
    sit = Path(sit)
    bruto = sit / "1_bruto" / "ine"
    f_it = sit / "2_normalizado" / "indicador_territorio.csv"
    f_carga = sit / "0_referencia" / "carregamento.csv"
    geo = {r["codigo_ine"]: r["geo_id"] for r in ler_csv(sit / "0_referencia" / "geo.csv") if r.get("codigo_ine")}

    cargas = ler_csv(f_carga)
    por_hash = {r["hash_sha256"]: r for r in cargas}
    prox_id = max([int(r["id"]) for r in cargas if str(r.get("id", "")).isdigit()] + [0]) + 1

    # metadados: o mais recente de cada indicador (os períodos novos só aparecem nos metadados novos)
    metas = {}
    for f in sorted(bruto.glob("*/*_meta.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        m = m[0] if isinstance(m, list) else m
        metas[m.get("IndicadorCod") or f.name[:7]] = m

    novas, avisos, geos_sem_dicionario = {}, [], set()
    novas_cargas = []
    for f in sorted(bruto.glob("*/*_dados_*.json")):
        texto = f.read_text(encoding="utf-8")
        h = hashlib.sha256(texto.encode("utf-8")).hexdigest()
        r = json.loads(texto)
        r = r[0] if isinstance(r, list) else r
        varcd = r.get("IndicadorCod") or f.name[:7]
        meta = metas.get(varcd)
        if not meta:
            avisos.append(f"{f.name}: sem {varcd}_meta.json — ignorado")
            continue
        rot2cod = {}
        for c in categorias(meta.get("Dimensoes", {}).get("Categoria_Dim")):
            if str(c.get("dim_num")) == "1":
                rot2cod[c.get("categ_dsg")] = c.get("categ_cod")
        unidade = meta.get("UnidadeMedida") or ""
        p10 = str(meta.get("Potencia10") or "0")
        if p10 not in ("", "0"):
            unidade += f" (x10^{p10})"
        extr = (r.get("DataExtracao") or "")[:10]

        if h in por_hash:
            cid = por_hash[h]["id"]
        else:
            cid = str(prox_id)
            prox_id += 1
        n = 0
        for rotulo, itens in (r.get("Dados") or {}).items():
            per = periodo(rot2cod.get(rotulo), rotulo)
            if not per:
                avisos.append(f"{varcd}: período «{rotulo}» não reconhecido — ignorado")
                continue
            for it in itens:
                v = numero(it.get("valor"))
                if v is None:
                    continue
                dims = sorted((int(k[4:]), it[k]) for k in it if re.fullmatch(r"dim_\d+", k))
                ind = f"INE_{varcd}" + "".join(f"|d{k}={c}" for k, c in dims)
                gcod = it.get("geocod")
                gid = geo.get(gcod)
                if gid is None:
                    gid = gcod
                    geos_sem_dicionario.add(f"{gcod} {it.get('geodsg')}")
                linha = {"geo_id": gid, "periodo_tipo": per[0], "periodo_inicio": per[1].isoformat(),
                         "periodo_fim": per[2].isoformat(), "indicador": ind, "valor": repr(v) if v != int(v) else str(int(v)),
                         "unidade": unidade, "agregacao": "", "derivado": "0", "fonte": FONTE,
                         "data_extracao": extr, "carregamento_id": cid}
                chave = (gid, linha["periodo_inicio"], linha["periodo_fim"], ind, extr)
                novas[chave] = linha
                n += 1
        if h not in por_hash:
            reg = {"id": cid, "fonte": FONTE, "ficheiro": str(f.relative_to(sit)).replace("\\", "/"),
                   "hash_sha256": h, "data_extracao": extr, "data_carga": date.today().isoformat(),
                   "n_linhas": str(n), "script": "3_scripts/carregar_ine.py", "versao_script": VERSAO,
                   "notas": f"{varcd} {meta.get('IndicadorNome', '')[:120]}"}
            novas_cargas.append(reg)
            por_hash[h] = reg

    outras = [x for x in ler_csv(f_it) if x.get("fonte") != FONTE]
    escrever_csv(f_it, CAB_IT, outras + list(novas.values()))
    if novas_cargas:
        escrever_csv(f_carga, CAB_CARGA, cargas + novas_cargas)
    return {"linhas_ine": len(novas), "linhas_outras_fontes": len(outras),
            "ficheiros_novos_registados": len(novas_cargas),
            "geos_sem_dicionario": sorted(geos_sem_dicionario), "avisos": avisos}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sit", default=str(Path(__file__).resolve().parent.parent))
    res = carregar(ap.parse_args().sit)
    print(f"INE → indicador_territorio.csv: {res['linhas_ine']} linhas "
          f"({res['ficheiros_novos_registados']} ficheiros novos em carregamento.csv)")
    if res["geos_sem_dicionario"]:
        print("Geografias sem linha em 0_referencia/geo.csv (geo_id = código INE):")
        for g in res["geos_sem_dicionario"]:
            print("  ", g)
    for a in res["avisos"]:
        print("AVISO:", a)
    sys.exit(0)
