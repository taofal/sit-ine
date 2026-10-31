# Entrega — INE — 2026-10-31

- **Enviado por:** API JSON do INE (extração própria do DIIET, script 3_scripts/extrair_ine.py)
- **Recebido em:** 2026-10-31
- **Data de extração (da fonte):** campo `DataExtracao` de cada ficheiro
- **Âmbito:** ver extrações abaixo
- **Contrato / base legal:** 
- **Ficheiros:** `<varcd>_dados_<hash>.json` (resposta de dados, exatamente como devolvida) e `<varcd>_meta.json` (metadados)
- **Notas da ficha técnica:** ver `MetaInfUrl` em cada ficheiro de dados
- **Restrições de reutilização:** 

## Extração — 2026-10-31 07:34 — séries completas
Geografias pedidas: Guimarães, Ave, Cávado, Barcelos, Santo Tirso, Matosinhos, Porto, Área Metropolitana do Porto, Norte, Portugal. Todas as categorias das restantes dimensões.

- **0008080** Despesa em investigação e desenvolvimento (I&D - €) das instituições e empresas com investigação e desenvolvimento — 0 valores, 0 ficheiros novos; FALHAS: metadados: INE recusou: HTTP Error 403: Forbidden

## Extração — 2026-10-31 13:57 — séries completas
Geografias pedidas: Guimarães, Ave, Cávado, Barcelos, Santo Tirso, Matosinhos, Porto, Área Metropolitana do Porto, Norte, Portugal. Todas as categorias das restantes dimensões.

- **0008080** Despesa em investigação e desenvolvimento (I&D - €) das instituições e empresas com investigação e desenvolvimento — 0 valores, 0 ficheiros novos; FALHAS: metadados: INE recusou: <urlopen error timed out>

## Extração — 2026-10-31 14:51 — séries completas
Geografias pedidas: Guimarães, Ave, Cávado, Barcelos, Santo Tirso, Matosinhos, Porto, Área Metropolitana do Porto, Norte, Portugal. Todas as categorias das restantes dimensões.

- **0008080** Despesa em investigação e desenvolvimento (I&D - €) das instituições e empresas com investigação e desenvolvimento — 700 valores, 1 ficheiros novos
    - `0008080_dados_30d3a77ec6.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0008080&lang=PT&Dim1=S7A2010,S7A2011,S7A2012,S7A2013,S7A2014,S7A2015,S7A2016,S7A2017,S7A2018,S7A2019,S7A2020,S7A2021,S7A2022,S7A2023&Dim2=1190308,119,112,1120302,11A1314,11A1308,11A1312,11A,11,PT
- **0008081** Investigadoras/es equivalente a tempo integral (ETI) (N.º) nas instituições e empresas com investigação e desenvolvimento — 140 valores, 1 ficheiros novos
    - `0008081_dados_14ee00addc.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0008081&lang=PT&Dim1=S7A2010,S7A2011,S7A2012,S7A2013,S7A2014,S7A2015,S7A2016,S7A2017,S7A2018,S7A2019,S7A2020,S7A2021,S7A2022,S7A2023&Dim2=1190308,119,112,1120302,11A1314,11A1308,11A1312,11A,11,PT
- **0008082** Pessoal ao serviço equivalente a tempo integral (ETI) em atividades de investigação e desenvolvimento (I&D) (N.º) das instituições e empresas com investigação e desenvolvimento — 650 valores, 1 ficheiros novos
    - `0008082_dados_becc794469.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0008082&lang=PT&Dim1=S7A2011,S7A2012,S7A2013,S7A2014,S7A2015,S7A2016,S7A2017,S7A2018,S7A2019,S7A2020,S7A2021,S7A2022,S7A2023&Dim2=1190308,119,112,1120302,11A1314,11A1308,11A1312,11A,11,PT
- **0010251** Unidades de investigação e desenvolvimento (I&D) - (N.º) nas instituições e empresas com investigação e desenvolvimento — 110 valores, 1 ficheiros novos
    - `0010251_dados_ea1649ca9b.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0010251&lang=PT&Dim1=S7A2013,S7A2014,S7A2015,S7A2016,S7A2017,S7A2018,S7A2019,S7A2020,S7A2021,S7A2022,S7A2023&Dim2=1190308,119,112,1120302,11A1314,11A1308,11A1312,11A,11,PT
- **0010254** Despesa em investigação e desenvolvimento (I&D - €) das instituições e empresas com investigação e desenvolvimento — 660 valores, 1 ficheiros novos
    - `0010254_dados_ed6b797704.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0010254&lang=PT&Dim1=S7A2013,S7A2014,S7A2015,S7A2016,S7A2017,S7A2018,S7A2019,S7A2020,S7A2021,S7A2022,S7A2023&Dim2=1190308,119,112,1120302,11A1314,11A1308,11A1312,11A,11,PT
- **0010255** Despesa em investigação e desenvolvimento (I&D) - (€) das instituições dos setores de execução do Estado, ensino superior e instituições privadas sem fins lucrativos com investigação e desenvolvimento — 770 valores, 1 ficheiros novos
    - `0010255_dados_486ca93c99.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0010255&lang=PT&Dim1=S7A2013,S7A2014,S7A2015,S7A2016,S7A2017,S7A2018,S7A2019,S7A2020,S7A2021,S7A2022,S7A2023&Dim2=1190308,119,112,1120302,11A1314,11A1308,11A1312,11A,11,PT
- **0003970** Valores médios de avaliação bancária (€/ m²) dos alojamentos — 900 valores, 1 ficheiros novos; geografias inexistentes neste indicador: Ave, Cávado, Matosinhos, Área Metropolitana do Porto, Norte, Portugal
    - `0003970_dados_c009f5bb4b.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0003970&lang=PT&Dim1=S3A200809,S3A200810,S3A200811,S3A200812,S3A200901,S3A200902,S3A200903,S3A200904,S3A200905,S3A200906,S3A200907,S3A200908,S3A200909,S3A200910,S3A200911,S3A200912,S3A201001,S3A201002,S3A201003,S3A201004,S3A201005,S3A201006,S3A201007,S3A201008,S3A201009,S3A201010,S3A201011,S3A201012,S3A201101,S3A201102,S3A201103,S3A201104,S3A201105,S3A201106,S3A201107,S3A201108,S3A201109,S3A201110,S3A201111,S3A201112,S3A201201,S3A201202,S3A201203,S3A201204,S3A201205,S3A201206,S3A201207,S3A201208,S3A201209,S3A201210,S3A201211,S3A201212,S3A201301,S3A201302,S3A201303,S3A201304,S3A201305,S3A201306,S3A201307,S3A201308,S3A201309,S3A201310,S3A201311,S3A201312,S3A201401,S3A201402,S3A201403,S3A201404,S3A201405,S3A201406,S3A201407,S3A201408,S3A201409,S3A201410,S3A201411&Dim2=0308,0302,1314,1312
- **0007606** Valores médios de avaliação bancária (€/ m²) dos alojamentos — 900 valores, 1 ficheiros novos; geografias inexistentes neste indicador: Guimarães, Ave, Cávado, Barcelos, Norte, Portugal
    - `0007606_dados_4a28032131.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0007606&lang=PT&Dim1=S3A200809,S3A200810,S3A200811,S3A200812,S3A200901,S3A200902,S3A200903,S3A200904,S3A200905,S3A200906,S3A200907,S3A200908,S3A200909,S3A200910,S3A200911,S3A200912,S3A201001,S3A201002,S3A201003,S3A201004,S3A201005,S3A201006,S3A201007,S3A201008,S3A201009,S3A201010,S3A201011,S3A201012,S3A201101,S3A201102,S3A201103,S3A201104,S3A201105,S3A201106,S3A201107,S3A201108,S3A201109,S3A201110,S3A201111,S3A201112,S3A201201,S3A201202,S3A201203,S3A201204,S3A201205,S3A201206,S3A201207,S3A201208,S3A201209,S3A201210,S3A201211,S3A201212,S3A201301,S3A201302,S3A201303,S3A201304,S3A201305,S3A201306,S3A201307,S3A201308,S3A201309,S3A201310,S3A201311,S3A201312,S3A201401,S3A201402,S3A201403,S3A201404,S3A201405,S3A201406,S3A201407,S3A201408,S3A201409,S3A201410,S3A201411&Dim2=1314,1308,1312,AMP
- **0011601** Indivíduos desempregados (N.º) nos agregados  domésticos privados — 690 valores, 1 ficheiros novos
    - `0011601_dados_3913934de2.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011601&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011606** Taxa de analfabetismo (%) — 60 valores, 1 ficheiros novos
    - `0011606_dados_db3cf02c7d.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011606&lang=PT&Dim1=S7A2011,S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011607** População residente com 10 e mais anos de idade (analfabetos) (N.º) — 30 valores, 1 ficheiros novos
    - `0011607_dados_5559a322a5.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011607&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011608** População empregada (N.º) — 2520 valores, 1 ficheiros novos
    - `0011608_dados_477d607224.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011608&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011637** População desempregada (N.º) — 1260 valores, 1 ficheiros novos
    - `0011637_dados_7e7f8e7674.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011637&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011638** População ativa (N.º) — 11100 valores, 1 ficheiros novos
    - `0011638_dados_78036ad761.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011638&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011639** População empregada (N.º) — 23580 valores, 1 ficheiros novos
    - `0011639_dados_5b5ee5df63.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011639&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011640** População empregada (N.º) — 49140 valores, 10 ficheiros novos
    - `0011640_dados_812116755d.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=0308
    - `0011640_dados_a9011aeb3a.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=119
    - `0011640_dados_be2a08c4ae.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=112
    - `0011640_dados_1c756a7c59.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=0302
    - `0011640_dados_83e64e5949.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=1314
    - `0011640_dados_6b79e96d90.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=1308
    - `0011640_dados_4d9c1e52ba.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=1312
    - `0011640_dados_c59b8a68da.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=11A
    - `0011640_dados_988b73ec01.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=11
    - `0011640_dados_8ec8d1c610.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011640&lang=PT&Dim1=S7A2021&Dim2=PT
- **0011641** População empregada (N.º) — 411180 valores, 10 ficheiros novos
    - `0011641_dados_60c8b22b5a.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=0308
    - `0011641_dados_3df0f0c72d.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=119
    - `0011641_dados_19dc4e594f.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=112
    - `0011641_dados_0331c7a980.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=0302
    - `0011641_dados_82925665d9.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=1314
    - `0011641_dados_761f5e3c82.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=1308
    - `0011641_dados_00dd8b1c5d.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=1312
    - `0011641_dados_c54ffde538.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=11A
    - `0011641_dados_75b44c7fbf.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=11
    - `0011641_dados_026ceb6056.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011641&lang=PT&Dim1=S7A2021&Dim2=PT
- **0011642** População empregada (Residente no estrangeiro a 31 de Dezembro de 2019 - N.º) — 2520 valores, 1 ficheiros novos
    - `0011642_dados_eaed867f7e.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011642&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011643** População desempregada (N.º) — 3240 valores, 1 ficheiros novos
    - `0011643_dados_a42d9e7aa4.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011643&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011648** Proporção da população residente com pelo menos o 3º ciclo do ensino básico completo (%) — 30 valores, 1 ficheiros novos
    - `0011648_dados_38f8cb5b01.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011648&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011650** Taxa de atividade (%) da população residente — 60 valores, 1 ficheiros novos
    - `0011650_dados_eb4d6a271f.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011650&lang=PT&Dim1=S7A2011,S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011656** Proporção da população residente com 15 e mais anos de idade sem nenhum nível de escolaridade completo (%) — 30 valores, 1 ficheiros novos
    - `0011656_dados_34e63d40b1.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011656&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011657** Proporção da população residente com idade entre 18 e 24 anos com o 3º ciclo do ensino básico completo que não está a frequentar o sistema de ensino (%) — 30 valores, 1 ficheiros novos
    - `0011657_dados_bbf9d99ed4.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011657&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011658** Proporção da população residente com idade entre 20 e 24 anos com pelo menos o ensino secundário completo (%) — 30 valores, 1 ficheiros novos
    - `0011658_dados_e79b4de6c1.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011658&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011659** Proporção da população residente com idade entre 30 e 34 anos com pelo menos o ensino superior completo (%) — 30 valores, 1 ficheiros novos
    - `0011659_dados_b275a593e5.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011659&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011660** Proporção da população residente com pelo menos o ensino secundário completo (%) — 60 valores, 1 ficheiros novos
    - `0011660_dados_91156c939a.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011660&lang=PT&Dim1=S7A2011,S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011661** Taxa de desemprego (%) — 60 valores, 1 ficheiros novos
    - `0011661_dados_c3c86686e7.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011661&lang=PT&Dim1=S7A2011,S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011667** Taxa de desemprego (%) da população residente ativa com idade entre 15 e 24 anos — 30 valores, 1 ficheiros novos
    - `0011667_dados_ec05ab53d1.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011667&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011676** Proporção da população empregada por conta de outrem (%) — 30 valores, 1 ficheiros novos
    - `0011676_dados_00d848ab01.json` ← https://www.ine.pt/ine/json_indicador/pindica.jsp?op=2&varcd=0011676&lang=PT&Dim1=S7A2021&Dim2=0308,119,112,0302,1314,1308,1312,11A,11,PT
- **0011687** População empregada (N.º) — 0 valores, 0 ficheiros novos; FALHAS: metadados: orçamento da volta esgotado
