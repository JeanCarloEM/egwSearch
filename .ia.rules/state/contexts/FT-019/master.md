# Contexto mestre - FT-019

## Identidade

- FT: `FT-019`.
- tipo: `correcao normativa e implementacao de codigo`.
- fonte: `.ia.rules/state/requests/FT-019/source.md`.
- estado: concluida.
- prioridade: alta.

## Problema comprovado

O checkpoint real de `en-pioneers` conserva 581 entradas de catalogo, 54 itens
enriquecidos, 52 confirmados e a fronteira no remote ID `1104`. Antes de
avancar para o item inedito seguinte (`1105`), `discover_catalog_items` chama
novamente `on_item_ready` para os 54 itens persistidos; os confirmados retornam
sem efeito, mas duas falhas historicas (`1038` e `1439`) sao reprocessadas e
reabrem o navegador. O cursor correto ja existe como comprimento da lista
persistida, mas a retomada o desrespeita ao priorizar o backlog anterior em vez
da fronteira ainda nao visitada.

## Objetivo

Retomar diretamente da fronteira ainda nao visitada do catalogo persistido,
sem chamar novamente itens enriquecidos anteriores e sem reprocessar,
reanalisar ou reindexar o prefixo confirmado. Pendencias historicas anteriores
permanecem registradas e somente voltam a ser tentadas depois de esgotar a
fronteira inedita, sem bloquear a continuidade da colecao.

## Escopo e invariantes

- evoluir o RCF antes do codigo, explicitando a precedencia da fronteira
  inedita sobre o backlog ja tentado;
- derivar o cursor seguro da quantidade ordenada de itens enriquecidos e
  atomicamente persistidos;
- nao invocar callback de processamento para itens ja presentes durante a fase
  parcial de descoberta;
- depois de concluir a descoberta, tentar somente IDs ainda nao confirmados;
- `--restart` continua sendo a unica forma de descartar o cursor do escopo;
- `--revalidate` preserva o cursor e aplica sua politica aos itens pendentes;
- checkpoint ambiguo, corrompido ou divergente bloqueia, sem reinicio silencioso;
- preservar ativos, publicacoes, manifestos gerados e alteracoes alheias.

## Aceite

1. o checkpoint real cuja fronteira termina em `1104` avanca diretamente para
   `1105`, sem tentar antes `1038`, `1439` ou qualquer confirmado;
2. itens confirmados nao provocam navegador, HTTP, analise ou indexacao;
3. pendencias historicas continuam registradas e sao retomadas somente depois
   de esgotada a fronteira inedita;
4. checkpoint parcial preserva ordem e nao salta entrada ainda nao enriquecida;
5. `--restart` e `--revalidate` preservam suas semanticas explicitas;
6. testes pequenos e direcionados comprovam ausencia das chamadas proibidas.

## Ordem

1. registrar FT e contexto em commit exclusivo;
2. evoluir e validar o RCF aplicavel em commit normativo;
3. interromper e aguardar autorizacao humana exigida pela Norma;
4. implementar retomada direta da fronteira e fila posterior de pendencias;
5. validar regressao, rastreabilidade e integracao.

## Fechamento normativo

- causa confirmada diretamente no checkpoint local, sem alterar o runtime;
- RCF global e especializado agora priorizam a fronteira inedita antes do
  backlog historico;
- duas sentencas materiais foram preparadas no mapa causal para
  `baixar.py` e seu teste direcionado;
- `agent:rcf` aprovado com 948 entradas e 835 sentencas materiais;
- a fase de codigo foi autorizada explicitamente em `2026-08-03`.

## Fechamento material

- `discover_catalog_items` nao reinvoca mais o callback para o prefixo ja
  persistido de um checkpoint parcial;
- a fatia inedita `ordered[len(items):]` e promovida primeiro, enquanto o laco
  final existente reconsidera somente depois as falhas historicas ainda nao
  confirmadas;
- o teste reproduz `1038` pendente, `1104` confirmado e `1105` como fronteira,
  comprovando a ordem `1105`, `1038` e nenhuma chamada de enriquecimento remoto;
- quatro testes direcionados passaram em 0,155 s; `py_compile` e
  `git diff --check` foram aprovados;
- commit material causal: `90d53ff33874d0911564f56051ddfeaeaf9423a0`;
- publicacoes, manifestos gerados, caches, temporarios, localstores e runtime
  permaneceram fora da alteracao.
