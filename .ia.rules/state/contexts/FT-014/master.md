# Contexto mestre - FT-014

## Identidade

- FT: `FT-014`.
- tipo: `implementacao_codigo` com correção normativa causal.
- fonte: `.ia.rules/state/requests/FT-014/source.md`.
- estado: em andamento; implementação integral autorizada no pedido humano.
- escopo: laboratório experimental de chunking por EPUB/PDF e conhecimento
  global deduplicado.

## Baseline reprovado

- schema `publication-chunking-analysis/v1` replica benefícios, riscos,
  parâmetros e textos genéricos em todos os ativos;
- a seleção usa pontuação heurística derivada de contagens estruturais;
- não há execução real das estratégias, comparação com referência nem métricas
  de perda, duplicação, contaminação ou fidelidade de fronteira;
- correlação limita-se a contagens por fingerprint/tipo/idioma/categoria e não
  acumula resultados experimentais.

## Objetivo e arquitetura

1. pesquisar literatura acadêmica primária recente e consolidar no RCF um
   catálogo global de hipóteses, referências e critérios experimentais;
2. criar referências estruturais normalizadas por recurso a partir dos parsers
   locais e testar candidatos efetivamente executáveis;
3. medir fidelidade, cobertura, ordem, unicidade, contaminação e fronteiras;
4. gravar no manifesto somente evidência específica, IDs normativos e decisão;
5. agregar resultados anonimizados/deduplicados em base global de aprendizado;
6. introduzir uma camada Rich compartilhada para analisador, downloader e
   indexador, capaz de compor execução isolada ou encadeada sem redundância;
7. preservar CLI, integração síncrona, idempotência e ausência de rede.

## Invariantes

- hipótese documentada não é verdade presumida nem recomendação;
- recomendação exige experimento `passed`; resultado insuficiente permanece
  `inconclusive` ou `rejected`;
- métricas e amostras de prova devem ser reprodutíveis sem expor o conteúdo;
- cabeçalhos, rodapés e números de página são ruído somente quando detectados
  por evidência repetitiva verificável, nunca por lista editorial presumida;
- parâmetros recomendados são os efetivamente testados no ativo;
- conhecimento global agrega assinaturas, métricas e padrões, não texto;
- IA externa é opcional e não integra o caminho determinístico obrigatório;
- saída de máquina/redirect permanece estável e sem ANSI; Rich é apresentação
  humana, com detecção de terminal e fallback seguro;
- a largura é limitada e calculada antes da renderização; path longo é truncado
  de modo determinístico preservando início e basename;
- artefatos gerados de publicações permanecem fora dos commits.

## Aceite global

- PDF multipágina de teste reconstrói parágrafo/frase atravessando páginas sem
  perda ou duplicação e exclui ruído repetido comprovado;
- EPUB de teste preserva ordem do spine e fronteiras sem inventar paginação;
- regex e demais candidatos só aparecem no resultado específico quando foram
  executados, medidos e classificados;
- manifestos não repetem benefícios, riscos, descrições ou parâmetros globais;
- aprendizagem global é estável, deduplicada e atualizada no mesmo gatilho;
- tabelas por recurso mostram estado, eficiência, acerto/erro e códigos causais
  sem despejar métricas brutas; duas linhas ou separador equivalente distinguem
  publicações;
- execução isolada mostra identidade e resumo próprios; composição pelo
  downloader suprime cabeçalhos/resumos equivalentes do analisador/indexador;
- suítes offline, compilação, contrato, rastreabilidade e amostra real passam.
