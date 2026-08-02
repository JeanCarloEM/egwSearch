# Contexto mestre - FT-013

## Identidade

- FT: `FT-013`.
- tipo: `implementacao_codigo` com evolução normativa causal.
- fonte: `.ia.rules/state/requests/FT-013/source.md`.
- estado: concluída; implementação integral autorizada no mesmo pedido humano.
- escopo: índice global multilocalizado e análise estrutural de EPUB/PDF.

## Objetivo

Materializar uma única capacidade reutilizável que gere ou atualize o índice
global a partir do acervo local e uma capacidade de análise estrutural que
identifique, para cada ativo editorial, estratégias comparáveis de chunking.
Ambas devem possuir CLI própria e integração síncrona no fechamento de cada
publicação adquirida ou gerada por `baixar.py`.

## Arquitetura e ordem

1. evoluir o RCF global e especializado, sem ampliar a autoridade parcial de
   `NORMA-IF-SIL-001`;
2. implementar o analisador de estrutura e seus manifestos derivados;
3. implementar o gerador incremental/global do índice;
4. expor os dois por invocadores isolados e comandos npm;
5. integrar um único gatilho pós-materialização no downloader;
6. validar arquivo, publicação, subárvore, corpus e retomada após falha.

## Invariantes

- metadado local é entrada prioritária; conteúdo editorial serve como evidência
  estrutural, nunca como autorização para inventar dado bibliográfico;
- `formative_data` mantém raiz fechada `book`, `urls`, `global_hashes`;
- derivado local não se apresenta como original em `formative_data`;
- manifesto de chunking recomenda estratégias e registra evidências, versões e
  limitações; não duplica o corpus nem obriga criação de chunks;
- correlação global usa somente sinais/fingerprints derivados e não modifica
  outra publicação durante análise de uma unidade;
- o gatilho síncrono ocorre depois da validação dos ativos e antes da confirmação
  do checkpoint;
- reexecução idempotente não altera bytes quando as entradas forem iguais;
- artefatos de runtime, cache e temporários permanecem fora do Git.

## Entregáveis

- RCF global e `scripts/publications/RCF.md` evoluídos;
- módulo/CLI de análise de estratégias de chunking;
- módulo/CLI do índice global multilocalizado;
- integração compartilhada em `baixar.py`;
- configuração e comandos npm explícitos;
- testes offline e rastreabilidade causal.

## Aceite global

- uma publicação válida produz manifesto para todos os seus EPUB/PDF e item do
  índice antes de ser confirmada;
- uma publicação já íntegra pode reparar somente manifesto/índice local sem
  requisitar a origem;
- execução específica ainda correlaciona fingerprints do corpus completo;
- execução de subdiretório e global gera resultados deterministicamente
  equivalentes para os mesmos itens;
- falha é conclusiva, deixa diagnóstico e não produz sucesso parcial silencioso.

## Evidências de conclusão

- correção precedente do catálogo inglês: `e00ca57`;
- criação da FT e captura da fonte: `0563749`;
- evolução normativa: `718f737`;
- implementação material: `b7a1421`;
- sincronização causal do RCF: `b6b9f8e`;
- suíte Python: 75 testes aprovados;
- suíte Node do invocador: 3 testes aprovados;
- índice real: 564 publicações reconstruídas localmente sem acesso à origem;
- análise específica: EPUB e PDF de `b42` produziram manifestos válidos;
- `publications:check`, compilação Python e verificação de whitespace aprovados;
- `agent:rcf` mantém somente o débito preexistente
  `RCF_SENTENCA_NAO_MAPEADA:RCF.md:9`.
