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
| 2 | `02-migracao-acervo.md` | acervo canônico e inventario pre/post | pendente |
| 3 | `03-indice-capas-site.md` | dados formativos, capas, indice, pagina e artefato | pendente |
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
- dry-run causal: `5ebf1ffcf3a378f52085e5cdb49a241dab0a2de12bac35a3edc4a08108794ee2`.
- inventario: 1576 arquivos, 638098352 bytes, SHA-256 `9900a18f91bac8480c38e1aee91ee28d01f485cad9fe19e2b3995d83599f0e28`.
- 11 problemas bloqueiam `apply` e foram transferidos nominalmente ao subcontexto 02.
- fase 3 permanece bloqueada.
