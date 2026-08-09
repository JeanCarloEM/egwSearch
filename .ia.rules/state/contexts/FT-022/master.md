# Contexto mestre - FT-022

## Identidade

- FT: `FT-022`.
- tipo: `evolucao normativa e implementacao de codigo`.
- fonte: `.ia.rules/state/requests/FT-022/source.md`.
- estado: concluída e sincronizada.
- prioridade: crítica para integridade do corpus.

## Dependências

- preservar integralmente contratos e fluxo das FTs 006-020;
- concluir materialmente a FT-021, pois uma varredura que interrompa após falha
  não cobre as novas coleções;
- reutilizar aquisição, checkpoint, transação por publicação, análise, índice,
  console e validação existentes, ampliando seus contratos sem fluxo paralelo.

## Objetivo

Ampliar o catálogo para REFERENCE e BIBLE, classificar cada obra por conteúdo
observado e materializar corpora bíblicos, léxicos/dicionários, concordâncias e
demais obras em representações universais, determinísticas, rastreáveis e
UTF-8, com JSON obrigatório nos domínios estruturados e EPUB quando adequado.

## Arquitetura

1. configuração declara agrupadores/folhas e `content_model` esperado;
2. catálogo continua produzindo `CatalogItem`, com classe semântica declarada
   pela coleção e confirmada pelo conteúdo antes da promoção;
3. um módulo compartilhado, sem rede, converte segmentos HTML preservados em
   `scripture-corpus/v1`, `lexical-corpus/v1` ou `concordance-corpus/v1`;
4. cada parser valida cardinalidade, ordem, IDs, referências e ausência de
   texto residual antes de escrever JSON UTF-8;
5. o EPUB derivado continua sendo gerado pelo fluxo existente, preservando o
   HTML/Markdown editorial; JSON integra a mesma unidade, metadado e commit;
6. contraprovas externas produzem relatório de validação e nunca substituem a
   fonte primária nem entram sem licença/termos registrados.

## Invariantes

- uma unidade bíblica JSON representa exatamente um versículo; intervalos ou
  múltiplos números no mesmo bloco bloqueiam, nunca concatenam;
- coleção/testamento e ordem de livros são dados, não enumerações fixas;
- nomes e abreviações ficam em `meta.books`; o caminho é
  `text.<collection>.<book>.<chapter>.<verse>`;
- marcação semântica fica em fragmentos tipados dentro do item do versículo,
  sem alterar seu texto integral normalizado;
- léxico preserva `definition.en`; `translation.pt-BR` é distinto e declara
  método/provedor/estado, sem simular original;
- concordância preserva entrada, formas e referências como relações, sem
  convertê-las em definição lexical inexistente;
- UTF-8 sem BOM é obrigatório para JSON, Markdown, XHTML, CSV/TSV e logs
  textuais próprios; exceção exige diagnóstico e registro de encoding original
  e transcoding, sem perda;
- obra sem licença/termo compatível, sem prova de completude ou com estrutura
  ambígua permanece `review_required` e não é promovida.

## Aceite

1. configuração seleciona as folhas observadas de `en/6`, `en/22`, `pt/68`,
   `en/1368`, `en/1369` e `en/1370`, sem tratar agrupador como obra;
2. teste bíblico cobre dois livros/organizações e falha por versículo ausente,
   duplicado, concatenado ou contaminado;
3. teste lexical cobre original, escrita, romanização, IDs, definição inglesa,
   tradução identificada, referências e relações;
4. teste de concordância preserva formas e referências sem confundir semântica;
5. JSON é determinístico, UTF-8 sem BOM e validado após releitura; EPUB é
   produzido quando adequado e PDF permanece opcional/dispensado por política;
6. índice, completude transacional e análise aceitam JSON como artefato
   estruturado sem degradar EPUB/PDF existentes;
7. testes demonstram classificação por estrutura e bloqueio de divergência
   título/conteúdo;
8. nenhuma coleta pública em massa é necessária ao aceite: fixtures reais
   reduzidas precedem amostra pública e toda origem externa respeita bloqueios.

## Fora de escopo imediato

- afirmar incorporação de corpora originais sem fonte/licença comprovada;
- executar tradução externa sem configuração e autorização específicas;
- baixar em massa durante a implementação ou versionar saídas operacionais;
- criar parser por título/obra quando o modelo universal cobre a estrutura.

## Ordem

1. fonte, FT e contexto em commit exclusivo;
2. RCF global e especializado em commit normativo;
3. implementação material da FT-021;
4. configuração, modelo universal, integração e testes da FT-022;
5. validação, commits materiais e sincronização de rastreabilidade/estado.

## Fechamento normativo

- RCF global centraliza agrupadores/folhas, schemas bíblico, lexical e de
  concordância, UTF-8, contraprovas, licenças e critérios de integridade;
- RCF especializado vincula `content_model`, `structured_content.py`, escrita
  atômica, metadado v3, índice/análise, tradução opt-in e testes;
- 36 sentenças materiais foram registradas como pendências causais da FT-022;
- `agent:rcf` validou o mapa com 1.018 entradas e 887 sentenças materiais,
  preservando apenas o estado global `RCF_DEGRADED` já conhecido da raiz.

## Fechamento material

- `912ff996f41605800effa1c74cf055c5d13976cf` implementou as folhas observadas
  de Reference/Bible, os três schemas universais, UTF-8 estrito, JSON/EPUB,
  metadado, índice, completude, inventário e progresso compartilhado;
- 109 testes Python e 8 testes Node foram aprovados, além de
  `publications:check`, `agent:rcf`, compilação e `git diff --check`;
- as 49 sentenças pendentes das FTs 021/022 foram sincronizadas com o commit;
- não houve coleta em massa, tradução externa nem habilitação de corpus cuja
  licença/termos permaneçam sem prova; `tanach.us` ficou declarada e desabilitada
  até essa verificação;
- os dois manifestos de chunking preexistentes e alheios à FT foram preservados
  fora dos commits.
