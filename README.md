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
2. **Calendário e atualizações** — o calendário de difusão do INE é lido uma vez por dia (`1_bruto/ine-calendario/<data>/`) e diz *quando* há publicações; o catálogo diz *o quê* foi atualizado. O catálogo é relido uma vez por dia e, nos dias com publicação, outra vez depois das 11:15 de Lisboa (o INE publica às 11:00; a releitura fica guardada à parte, p. ex. `catalogo_1130.xml`). Em cada leitura, o catálogo é comparado com o registo: um indicador `feito` cuja última atualização no INE é posterior à `data_colheita` volta a `pendente`, com a nota «INE atualizou a … (colhido a …)».
3. **Fila** — primeiro as atualizações do INE (de qualquer prioridade); depois os por colher, por prioridade (1 = lista de `ine_indicadores.json`, 2–4 = temas); os erros no fim, até 3 tentativas.
4. **Colheita** — série completa de cada indicador, para `1_bruto/ine/<data>/`. Uma atualização vai para a pasta do dia: a versão anterior fica, e o carregamento guarda as duas (a chave inclui a data de extração).
5. **Volta sem trabalho** — fila vazia, calendário lido hoje e catálogo em dia: a volta termina logo, sem pedidos ao INE e sem gravar nada. O agendamento fica de hora a hora; depois de colhido o atraso, na prática só há trabalho uma vez por dia e nos dias de publicação.
6. **Passagem para a base local** — copiam-se só os ficheiros novos; o carregamento junta todas as versões; depois verifica-se a base contra o registo (indicadores `feito` sem valores na base, valores na base fora do registo, colheitas mais recentes ainda não carregadas).

## Banco de Portugal (BPstat)

- **Agendamento:** `.github/workflows/colheita_bportugal.yml` corre `3_scripts/extrair_bportugal.py` no dia 2 de cada mês (06:23 UTC). Para correr à mão: **Actions → Colheita Banco de Portugal → Run workflow**.
- **O que colhe:** API pública do BPstat (JSON-stat), todas as geografias publicadas (Portugal, NUTS II, NUTS III): domínio 178 (indicadores das empresas por região, Central de Balanços, anual), 188 (empréstimos por região do devedor, mensal) e 206 (depósitos por região do balcão, mensal).
- **Só o que mudou:** cada domínio só é descarregado se o BP o atualizou (`obs_updated_at`) depois da última extração guardada; se nenhum mudou, a corrida não grava nada.
- **Onde fica:** `1_bruto/bportugal/<AAAA-MM-DD>/d<domínio>/` — metadados, dimensões e páginas de dados exatamente como devolvidas + `_entrega.md`. Só se acrescenta.
- **Passagem para a base local:** `sincronizar_github.py` traz as pastas novas; depois `carregar_bportugal.py` e `construir_duckdb.py` (scripts da base local).
