# Colheita INE

Colheita lenta e contínua dos indicadores do INE com dados por município, para uma base de dados local de indicadores territoriais. Os dados são públicos (API JSON do INE).

- **Agendamento:** `.github/workflows/colheita.yml` corre `3_scripts/colheita_ine.py` de hora a hora (até 100 pedidos por volta, 5 s entre pedidos; à 1.ª recusa persistente do INE a volta pára e retoma na seguinte). Para correr à mão: separador **Actions → Colheita INE → Run workflow**.
- **O que colhe:** primeiro os indicadores de `3_scripts/ine_indicadores.json` — incluindo, desde 2026-11-01, indicadores sem detalhe municipal: preços (IPC, IHPC, preços da habitação, custo de construção, preços na produção), índices de atividade (indústria, construção, comércio, serviços, conjuntura, PIB) e contas regionais por NUTS; depois todo o catálogo do INE cujo nível geográfico mais fino é o município ou a freguesia. Séries completas, todas as categorias de todas as dimensões (CAE incluída), para as geografias de `ine_indicadores.json`.
- **Onde fica:**
  - `1_bruto/ine/<AAAA-MM-DD>/` — respostas do INE exatamente como devolvidas (`<varcd>_dados_<hash>.json`, `<varcd>_meta.json`) + `_entrega.md` com o URL de cada pedido. Só se acrescenta; nada é reescrito.
  - `1_bruto/ine-catalogo/<AAAA-MM-DD>/catalogo.xml` — catálogo do INE (relido todos os dias: é por ele que se sabe que séries o INE atualizou).
  - `3_scripts/_estado/colheita_ine.csv` — estado por indicador (pendente · feito · sem_geografia · erro); `colheita_ine.log` — registo das voltas.
- **Passagem para a base local:** os ficheiros novos de `1_bruto` são copiados para a base local (só os que ainda lá não estão; nunca reescreve). Depois, `carregar_ine.py` passa-os para `2_normalizado/indicador_territorio.csv`.

## Ciclo (cada passo parte do anterior; nada é apagado nem reescrito)

1. **Registo** — `3_scripts/_estado/colheita_ine.csv` diz, por indicador, o que já foi colhido (`feito`, com `data_colheita`) e o que falta. Cada volta parte dele.
2. **Atualizações** — no início de cada volta, o catálogo do INE (relido uma vez por dia) é comparado com o registo: um indicador `feito` cuja última atualização no INE é posterior à `data_colheita` volta a `pendente`, com a nota «INE atualizou a … (colhido a …)».
3. **Fila** — primeiro as atualizações do INE (de qualquer prioridade); depois os por colher, por prioridade (1 = lista de `ine_indicadores.json`, 2–4 = temas); os erros no fim, até 3 tentativas.
4. **Colheita** — série completa de cada indicador, para `1_bruto/ine/<data>/`. Uma atualização vai para a pasta do dia: a versão anterior fica, e o carregamento guarda as duas (a chave inclui a data de extração).
5. **Passagem para a base local** — copiam-se só os ficheiros novos; o carregamento junta todas as versões; depois verifica-se a base contra o registo (indicadores `feito` sem valores na base, valores na base fora do registo, colheitas mais recentes ainda não carregadas).
