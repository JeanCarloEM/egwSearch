# Contexto mestre - FT-004

## Identidade

- FT: `FT-004`.
- fase global: 2 de 3.
- fonte: `.ia.rules/state/TODO.ia.md:214` e `.ia.rules/state/TODO.ia.md:886`.
- RCF: §§2-4, 32-33 e 40-49.
- autorizacao: explicita em `2026-07-26`.
- estado: em andamento.

## Objetivo e fronteira

Materializar somente a publicacao publica e sua cadeia operacional: estrutura canônica do acervo, downloader, migracao, dados formativos, indice, hashes, capas, site, build, validacao e GitHub Pages.

A FT NÃO implementa busca, RAG, Modo Pesquisa, Modo Conversa, CLI ou GUI da fase 3. Dependencia estritamente necessaria deve ser registrada aqui antes da alteracao.

## Baseline

- acervo: 525 PDF, 526 EPUB e 525 `*.source.json`;
- total: 1576 arquivos sob `src/publications/`, alem de `baixar.py`;
- estrutura: arquivos planos em `<autor>/<idioma>/<tipo>/`;
- downloader: Python legado, destinos planos, efeito material no import e sobrescrita insuficientemente protegida;
- cadeia publica: ausente;
- indice global e capas: ausentes;
- workflow de Pages: ausente;
- runtime local observado: Python 3.14 e Node.js 22; CI deve materializar Node.js 24 quando houver invocacao Node.

## Arquitetura de execucao

1. contrato comum e inventario;
2. migracao idempotente e validada;
3. downloader canônico;
4. geracao de dados, capas, indice, site e artefato;
5. integracao ao hook oficial `publish` e workflow;
6. validacao local, visual e de destino real.

Processamento bibliografico permanece em Python por adequacao ao ecossistema PDF/EPUB/imagem. O site sera estatico, sem runtime cliente desnecessario. O mecanismo oficial `publish` sera especializado por hook local, sem substituir a governanca gerenciada.

## Subcontextos

| Ordem | Contexto | Entrega | Estado |
| ---: | --- | --- | --- |
| 1 | `01-contratos-e-downloader.md` | contrato comum, RCF especifico, migrador e downloader | concluido |
| 2 | `02-migracao-acervo.md` | acervo canônico e inventario pre/post | concluido |
| 3 | `03-indice-capas-site.md` | dados formativos, capas, indice, pagina e artefato | em andamento; decisao editorial pendente |
| 4 | `04-build-workflow.md` | hook, comandos e GitHub Pages | pendente |
| 5 | `05-validacao-encerramento.md` | testes, visual, destino, TODO e estado final | pendente |

## Invariantes

- nenhum original PDF/EPUB pode ter bytes alterados;
- nenhum arquivo pode ser perdido, sobrescrito ou fundido sem igualdade de SHA-256;
- titulo duvidoso preserva valor; tag nao comprovada nao e inventada;
- PDF e EPUB somente compartilham grupo sob identidade editorial comprovada;
- `formative_data` segue exatamente `book`, `urls` e `global_hashes`;
- URL de origem e URL publica permanecem semanticamente distintas;
- pagina nao vincula nem lista indice ou publicacoes;
- artefato publico nao inclui fonte, cache, teste, log ou estado interno;
- fase 3 permanece bloqueada.

## Aceite global

Todos os criterios materiais de RCF §§40-49 e da fonte devem possuir evidencia executada. Validacao de Pages no destino real e obrigatoria; indisponibilidade externa deve permanecer pendencia explicita e nao pode ser convertida em sucesso inferido.

## Estado de integracao

- subcontexto 01 concluiu contrato e ferramentas sem rede nem movimento do acervo.
- commits do subcontexto 01: material `fc95bae`; rastreabilidade `fb792a4`.
- dry-run causal: `5ebf1ffcf3a378f52085e5cdb49a241dab0a2de12bac35a3edc4a08108794ee2`.
- inventario: 1576 arquivos, 638098352 bytes, SHA-256 `9900a18f91bac8480c38e1aee91ee28d01f485cad9fe19e2b3995d83599f0e28`.
- 11 problemas bloqueiam `apply` e foram transferidos nominalmente ao subcontexto 02.
- os 11 problemas eram lacunas de procedencia: downloads oficiais reproduziram tamanho e SHA-256 dos 11 EPUBs locais;
- os metadados foram completados sem alterar PDF/EPUB e o plano repetido ficou estavel com zero bloqueio;
- plano liberado: `5660215656f00e721abc0d67344508380fbc8bc62e063d77816a3e32aded50cb`, 1578 arquivos e 638102876 bytes.
- subcontexto 02 concluiu a migracao em 527 grupos canônicos, com journal finalizado e conteudo pre/post integralmente igual;
- post plan `35b8a85ca167dd65410d502e6629e58ea05bdf0426fbfac6242efd9c574c1de0`: 1578 arquivos, 638102876 bytes, zero acao e zero problema;
- a falha transitoria inicial revelou e corrigiu a janela de persistencia do journal; teste de falha injetada comprova rollback do registro pendente.
- a evolucao autorizada de URI separou titulo editorial e slug de rota:
  RCF `2024dbd`, material
  `0507203f6b0c575ab1f0dfb3e9bc33650c5c4da6`;
- o plano de slugs
  `25ef198629963f60f175e1745eceb567fbe9f2069c4254853709cfc4b616b7fd`
  renomeou 527 diretorios e 1578 arquivos sem alterar o multiconjunto de
  tipo, tamanho e SHA-256; o journal foi finalizado;
- o post plan
  `dd726ed14e2ea1f98f120348db8a4e133882f6c6fe68e038af1a0dbe5dda1a27`
  encontrou zero acao e zero problema, com inventario SHA-256
  `e1fe12163b972cad8f339c7d59bf953be4f4e00b52b6d137a1c2915cbda2ee50`;
- o subcontexto 03 auditou 527 grupos: 525 capas EPUB utilizaveis, dois
  fallbacks PDF e nenhuma alteracao dos originais;
- seis colisoes de titulo-base abrangem 12 grupos cuja distincao depende de
  edicao; RCF §44 exige decisao humana especifica antes da emissao;
- proximo ponto: decidir o tratamento finito dos qualificadores de edicao e
  retomar o gerador do subcontexto 03.
- fase 3 permanece bloqueada.
