# Contexto mestre - FT-003

## Identidade

- ordem: 1 de 1 contexto mestre
- fase: normatizacao integrada
- fonte: `TODO.id.md`
- fonte_sha256: `8A21E6FEF4840E32B6381975231094D46C2CD814A8226752E6F8D3380F1AE31B`
- commit_de_origem_mais_recente: `57ae9e99f60e53045582681a382ecb2ac1dc2e5a`
- estado: em andamento

## Objetivo global

Consolidar no RCF, sem executar codigo, todas as regras materialmente relacionadas a busca bibliografica, RAG, operacao local/GUI, publicacao estatica, acervo, download, metadados formativos, hashes, capas, indexacao e validacao.

## Fontes canonicas

| ID | Origem | Escopo |
| --- | --- | --- |
| SRC-NUM | `TODO.id.md:56` | equivalencia numerica bidirecional e multilingue |
| SRC-GUI | `TODO.id.md:69` | CLI primaria, GUI local e perfis operacionais |
| SRC-RAG | `TODO.id.md:95` | avaliacao RAG, chunking, busca, evidencias e metricas |
| SRC-PUB | `TODO.id.md:214` | pagina, indice, dados formativos, capas e workflow |
| SRC-ACERVO | `TODO.id.md:886` | estrutura canonica, migracao, `baixar.py` e disponibilidade direta |

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

## Subcontextos

1. `01-busca-rag.md`
2. `02-cli-gui.md`
3. `03-publicacao-acervo.md`

## Aceite global

- toda regra da fonte possui destino no RCF;
- conflitos possuem precedencia e motivacao;
- fases futuras possuem fronteiras sem sobreposicao;
- nenhum arquivo sob `src/`, script, workflow, build ou publicacao e alterado;
- o estado permanece retomavel e a execucao interrompe apos a fase normativa.
