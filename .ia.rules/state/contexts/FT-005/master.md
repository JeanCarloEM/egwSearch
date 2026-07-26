# Contexto mestre - FT-005

## Identidade

- FT: `FT-005`.
- tipo: `implementacao_normativa`.
- fase global: 2 de 3.
- fonte: `.ia.rules/state/requests/FT-005/source.txt`.
- RCF: global e `src/publications/egw/RCF.md`.
- autorização: solicitação explícita recebida em `2026-07-26`.
- estado: em andamento.

## Objetivo e fronteira

Normatizar a evolução do coletor de publicações para aquisição incremental,
idempotente, multiautor e responsável das coleções públicas `Biblioteca dos
Pioneiros Adventistas` e `Adventist Pioneer Library`, preservando o suporte a
Ellen G. White e restringindo incorporação a `pt-BR`, `en`, PDF, EPUB e texto
editorial público controladamente derivado.

Esta FT define contratos e critérios verificáveis. Não altera código,
configuração executável, acervo, dependências, testes ou workflow. A
implementação pertence exclusivamente à `FT-006` e exige nova autorização
humana explícita depois da conclusão desta fase normativa.

## Baseline confirmado

- `baixar.py` descobre coleções por DOM/Selenium e baixa o ativo antes de
  comparar o SHA-256 com o acervo;
- não existe preflight por estado local, identificador remoto, ETag ou
  `Last-Modified`;
- o padrão atual usa quatro coleções concorrentes, sem contrato explícito de
  atraso, jitter, `Retry-After`, cache ou interrupção por contenção;
- identidade e destino são fixados no autor `egw`;
- há 527 grupos, 525 PDF, 526 EPUB e 527 metadados legados de origem;
- todos os 1051 registros de origem apontam para `media2.egwwritings.org`;
- o acervo usa `pt-br` e `en-us`; a evolução deve convergir aquisição para
  `pt-BR` e `en` sem duplicar nem fundir variante material;
- as coleções públicas observadas são `pt/1055` e `en/15`;
- a origem expôs catálogo navegável e leitura textual pública, mas a inspeção
  HTTP direta recebeu desafio anti-automação e foi interrompida sem evasão.

## Subcontextos

| Ordem | Contexto | Entrega | Estado |
| ---: | --- | --- | --- |
| 1 | `01-identidade-e-elegibilidade.md` | coleções, autores, idiomas, tipos e variantes | em andamento |
| 2 | `02-incremental-e-rede.md` | estado, idempotência, atualização e acesso responsável | pendente |
| 3 | `03-texto-e-derivados.md` | extração editorial, Markdown, EPUB e proveniência | pendente |

## Invariantes

- nenhuma coleta em massa ocorre nesta FT;
- `403`, CAPTCHA ou contenção persistente encerram a unidade afetada;
- proteção, autenticação e autorização nunca são contornadas;
- arquivo concluído e íntegro não é solicitado, convertido ou regravado;
- arquivo distinto não é sobrescrito nem variante legítima é fundida;
- conteúdo remoto não é corrigido, resumido, traduzido ou reescrito;
- derivado local nunca se apresenta como original da origem;
- `formative_data` preserva seu contrato fechado; proveniência incremental e
  derivação residem em envelope/estado próprio;
- a decisão editorial pendente da `FT-004/03` permanece intocada.

## Aceite

- todos os requisitos materiais da fonte estão incorporados sem redução nos
  RCFs aplicáveis;
- contratos distinguem descoberta, elegibilidade, estado, aquisição nativa,
  extração textual, persistência e indexação;
- a transição `en-us` para `en` é determinística e não destrutiva;
- a futura implementação possui testes obrigatórios e gate de fixture/amostra
  mínima antes de qualquer coleta ampliada;
- a `FT-006` permanece bloqueada até nova autorização humana explícita.

