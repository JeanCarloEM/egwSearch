# Contexto mestre - FT-003

## Identidade

- ordem: 1 de 1 contexto mestre
- fase: normatizacao integrada
- fonte_atual: `.ia.rules/state/TODO.ia.md`
- fonte_original: `TODO.id.md`
- fonte_sha256: `4655483CF985A5C0A9C7E99495B404ED793006CA349BF11138A62925B50953A4`
- commit_de_origem_mais_recente: `11c4199c150e149c70c4e4d7abb9550b79c929d7`
- estado: em andamento; revisao 2 por alteracao material da fonte

## Objetivo global

Consolidar no RCF, sem executar codigo, todas as regras materialmente relacionadas a busca bibliografica, RAG, conversa probatoria, operacao local/GUI, publicacao estatica, acervo, download, metadados formativos, hashes, capas, indexacao e validacao.

## Fontes canonicas

| ID | Origem | Escopo |
| --- | --- | --- |
| SRC-NUM | `.ia.rules/state/TODO.ia.md:56` | equivalencia numerica bidirecional e multilingue |
| SRC-GUI | `.ia.rules/state/TODO.ia.md:69` | CLI primaria, GUI local e perfis operacionais |
| SRC-RAG | `.ia.rules/state/TODO.ia.md:95` | avaliacao RAG, chunking, busca, evidencias e metricas |
| SRC-PUB | `.ia.rules/state/TODO.ia.md:214` | pagina, indice, dados formativos, capas e workflow |
| SRC-ACERVO | `.ia.rules/state/TODO.ia.md:886` | estrutura canonica, migracao, `baixar.py` e disponibilidade direta |
| SRC-CONV | `.ia.rules/state/TODO.ia.md:1182` | modos Pesquisa/Conversa, prova documental, referencias, traducao, sessao e avaliacao |

Nenhuma URL, numero de issue ou repositorio externo foi identificado como fonte autônoma. Referencias tecnicas externas dentro do anexo servem a fundamentacao, nao constituem issues a preservar.

## Arquitetura das frentes

| Fase | FT | Resultado | Autorizacao |
| --- | --- | --- | --- |
| 1 | FT-003 | RCF consolidado e TODO orquestrador concluido | presente nesta solicitacao |
| 2 | FT-004 | publicacao publica e cadeia operacional | nova autorizacao obrigatoria |
| 3 | FT-002 | conformidade tecnica restante do repositorio | nova autorizacao obrigatoria |

## Relacoes e precedencias

- `NORMA-IF-SIL-001` rege exclusivamente o documento formativo `book`, `urls` e `global_hashes`; envelope global, metadado canônico, assets, capas, rotas e publicacao permanecem contratos externos.
- O subitem anterior que restringe `formative_data` a `book` e `global_hashes` conflita com o anexo final, que exige tambem `urls`; prevalece o anexo expresso e mais especifico, preservando `urls` no documento formativo.
- A pagina institucional nao divulga nem vincula o indice ou as publicacoes, mas o artefato publicado DEVE manter URLs diretas estaveis e acessiveis para consumidores que as conhecam.
- A estrutura canonica final agrupa formatos e assets no diretorio do titulo; a formulacao intermediaria `assets/<basename-publicacao>/` fica superada pela regra posterior, mais completa, de agrupamento integral por titulo.
- CLI/local permanece contrato primario; GUI local e pagina institucional sao entregas distintas, ambas compartilhando contratos sem duplicar o nucleo.
- A fase 2 materializa somente a cadeia publica; a fase 3 implementa busca e conformidade restante sem refazer artefatos validados.
- O Modo Pesquisa preserva integralmente os contratos ja consolidados; o Modo Conversa os compoe sem substituir a recuperacao deterministica, lexical, semantica ou hibrida.
- A resposta conversacional distingue afirmacao, evidencia literal, referencia, traducao, interpretacao e inferencia; ausencia de prova suficiente exige abstencao.
- LLM, tradutor e reranker permanecem opcionais e condicionados a ganho liquido; indisponibilidade degrada capacidades dependentes sem fabricar resultado.

## Subcontextos

1. `01-busca-rag.md`
2. `02-cli-gui.md`
3. `03-publicacao-acervo.md`
4. `04-conversa-probatoria.md`

## Matriz origem para RCF

| Fonte | Destino normativo |
| --- | --- |
| SRC-NUM | RCF §§38, 39, 47 e 49 |
| SRC-GUI | RCF §§34, 35, 40, 48 e 49 |
| SRC-RAG | RCF §§36, 37, 39, 47, 48 e 49 |
| SRC-PUB | RCF §§40, 43, 44, 45, 46, 47, 48 e 49 |
| SRC-ACERVO | RCF §§41, 42, 43, 46, 47, 48 e 49 |
| SRC-CONV | RCF §§11-13, 19, 23-25, 34, 36-39, 48-57 |

## Aceite global

- toda regra da fonte possui destino no RCF;
- conflitos possuem precedencia e motivacao;
- fases futuras possuem fronteiras sem sobreposicao;
- nenhum arquivo sob `src/`, script, workflow, build ou publicacao e alterado;
- o estado permanece retomavel e a execucao interrompe apos a fase normativa.

## Resultado anterior

- estado: concluido
- RCF: consolidado
- TODO `[1A]`: concluido
- codigo, acervo, scripts, workflows, build e publicacao: inalterados nesta FT
- retomada: FT-004, somente mediante autorizacao humana explicita

## Reabertura

- motivo: adicao material de 234 linhas ao TODO pelo commit `11c4199`.
- estado: revisao normativa em andamento.
- preservado: RCF anterior, fases tecnicas e fronteiras entre FT-004 e FT-002.
- pendente: incorporar integralmente SRC-CONV, validar a revisao e interromper novamente antes do codigo.
