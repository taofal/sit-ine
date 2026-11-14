# Entrega — E-Redes, portal de dados abertos (API) — 2026-11-14

- **Enviado por:** colheita própria (`3_scripts/extrair_eredes_aberto.py`)
- **Recebido em:** 2026-11-14
- **Data de extração (da fonte):** 2026-11-14
- **Âmbito:** todo o país (o que a E-Redes publica); consumo mensal de energia ativa faturada
- **Contrato / base legal:** dados abertos da E-Redes (licença CC BY 4.0)
- **Ficheiros:** um subdiretório por conjunto atualizado (`conjunto.json`, `dados.csv.gz`)
- **Notas da ficha técnica:** ano e mês referem-se ao período de consumo, não à data de faturação; valores aproximados e sujeitos a revisão; por proteção de dados, parte do consumo pode vir agregada em categorias «OUTROS»
- **Restrições de reutilização:** citar a fonte (E-REDES – Distribuição de Eletricidade, «Portal Open Data E-REDES»)

| Conjunto | Processado na E-Redes | Registos | Anunciados | Campos |
|---|---|---:|---:|---|
| 3-consumos-faturados-por-municipio-ultimos-10-anos | 2026-11-10T15:49:26+00:00 | 310745 | 310745 | ano, mes, data, distrito, concelho, freguesia, nivel_de_tensao, energia_ativa_kwh, coddistrito, coddistritoconcelho, coddistritoconcelhofreguesia, mes_int |
| consumo-total-nacional | 2026-11-14T14:35:25+00:00 | 135473 | 451060 | datahora, dia, mes, ano, date, time, bt, mt, at, mat, total |

Pedidos:
- https://e-redes.opendatasoft.com/api/explore/v2.1/catalog/datasets/3-consumos-faturados-por-municipio-ultimos-10-anos
- https://e-redes.opendatasoft.com/api/explore/v2.1/catalog/datasets/3-consumos-faturados-por-municipio-ultimos-10-anos/exports/csv?delimiter=%3B
- https://e-redes.opendatasoft.com/api/explore/v2.1/catalog/datasets/consumo-total-nacional
- https://e-redes.opendatasoft.com/api/explore/v2.1/catalog/datasets/consumo-total-nacional/exports/csv?delimiter=%3B
