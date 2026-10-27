# SIT — colheita INE

Colheita lenta e contínua dos indicadores do INE com dados por município, para o **Sistema de Inteligência Territorial e Económica (DIIET, Câmara Municipal de Guimarães)**. Os dados são públicos (API JSON do INE).

- **Agendamento:** `.github/workflows/colheita.yml` corre `3_scripts/colheita_ine.py` de hora a hora (até 100 pedidos por volta, 5 s entre pedidos; à 1.ª recusa persistente do INE a volta pára e retoma na seguinte). Para correr à mão: separador **Actions → Colheita INE → Run workflow**.
- **O que colhe:** primeiro os indicadores de `3_scripts/ine_indicadores.json`; depois todo o catálogo do INE cujo nível geográfico mais fino é o município ou a freguesia. Séries completas, todas as categorias de todas as dimensões (CAE incluída), para as geografias de `ine_indicadores.json`.
- **Onde fica:**
  - `1_bruto/ine/<AAAA-MM-DD>/` — respostas do INE exatamente como devolvidas (`<varcd>_dados_<hash>.json`, `<varcd>_meta.json`) + `_entrega.md` com o URL de cada pedido. Só se acrescenta; nada é reescrito.
  - `1_bruto/ine-catalogo/<AAAA-MM-DD>/catalogo.xml` — catálogo do INE (relido de 7 em 7 dias).
  - `3_scripts/_estado/colheita_ine.csv` — estado por indicador (pendente · feito · sem_geografia · erro); `colheita_ine.log` — registo das voltas.
- **Passagem para a SIT:** os ficheiros novos de `1_bruto` são copiados para a SIT (só os que ainda lá não estão; nunca reescreve). Depois, `carregar_ine.py` passa-os para `2_normalizado/indicador_territorio.csv`.
