# Contexto mestre - FT-021

## Identidade

- FT: `FT-021`.
- tipo: `correcao normativa e implementacao de codigo`.
- fonte: `.ia.rules/state/requests/FT-021/source.md`.
- estado: criada; fase RCF pendente.
- prioridade: alta.

## Causas comprovadas

1. o laço global de `baixar.py` executa `break` depois de qualquer coleção com
   falha ou bloqueio, portanto falhas individuais em `pt-br-livros` impedem a
   visita às coleções posteriores;
2. o fechamento transacional exige metadado `publication-source/v3`, mas o
   preflight admite corretamente publicações locais legadas completas; essa
   incompatibilidade transforma reutilizações válidas em falhas em massa;
3. o rate limiter é chamado em fronteiras remotas, mas o contrato ainda não
   comprova nem observa que esperas correspondem exclusivamente a requests
   efetivamente emitidos;
4. a apresentação compartilhada sintetiza publicações e experimentos, porém
   não possui um modelo global/corrente com total, concluídas, restantes,
   percentual, média observada e ETA, nem propriedade explícita na composição.

## Objetivo

Percorrer todas as coleções e publicações elegíveis apesar de falhas unitárias,
reutilizar ou promover deterministicamente metadados locais válidos antes do
fechamento, aplicar rate limit somente na fronteira de uma requisição real e
exibir progresso global/corrente sucinto e não redundante no downloader e no
analisador.

## Escopo e invariantes

- falha de item ou coleção permanece registrada e retomável, mas não encerra a
  varredura de coleções independentes;
- o diário global representa unidades concluídas e pendentes por identidade,
  sem depender de um único prefixo contíguo que force `break`;
- metadado legado local completo deve ser promovido de modo determinístico ao
  contrato transacional vigente, sem rede nem alteração dos ativos válidos;
- espera de rate limit somente pode ocorrer imediatamente antes de HTTP GET ou
  navegação real; skip, preflight, cache, índice, análise e commit não esperam;
- o inventário normalizado de catálogos deve fornecer o total global antes da
  varredura material, reutilizando checkpoint válido e acessando apenas os
  catálogos ainda desconhecidos;
- progresso informa escopo atual e global, percentual, total, processadas,
  restantes, tempo médio observado e ETA; estimativa sem amostra é inequívoca;
- execução composta tem um único proprietário do progresso principal; filhos
  preservam seus resultados materiais sem duplicar barra, cabeçalho ou resumo;
- falha não conta como concluída no diário retomável, mas conta como visitada na
  execução corrente para que percentual e ETA não regridam;
- preservar publicações, caches, temporários, localstores, checkpoints e saídas
  concorrentes fora dos commits desta FT.

## Aceite

1. falhas em `pt-br-livros` não impedem a visita a todas as coleções seguintes;
2. publicação local legada completa fecha ou migra localmente sem request e sem
   `transação exige publication-source/v3`;
3. teste-sentinela comprova zero sleep quando zero request é emitido e uma
   espera compartilhada somente entre requests reais;
4. execução global calcula total antes da varredura material e atualiza, a cada
   item, processadas, restantes, percentual e ETA pela média observada;
5. analisador isolado mostra o mesmo conjunto essencial de indicadores;
6. downloader composto é o único progresso principal, sem duplicação pelo
   analisador/indexador filho;
7. retomada visita diretamente pendências sem repetir unidades concluídas e
   mantém as falhas diagnosticáveis para execução posterior;
8. testes pequenos cobrem continuação entre coleções, legado v3, rate limit,
   cálculo de ETA e composição visual.

## Ordem

1. registrar fonte, FT e contexto em commit exclusivo;
2. evoluir e validar os RCFs em commit normativo;
3. interromper e aguardar autorização humana explícita para código;
4. implementar em capacidades compartilhadas e testes direcionados;
5. validar, criar commit material e sincronizar rastreabilidade.
