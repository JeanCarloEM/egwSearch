# Contexto mestre - FT-006

## Identidade

- FT: `FT-006`.
- tipo: `implementacao_codigo`.
- fase global: 2 de 3.
- fonte: `.ia.rules/state/requests/FT-005/source.txt`.
- dependência: conclusão da `FT-005`.
- autorização: explícita, recebida em `2026-07-26`.
- estado: concluído.

## Objetivo e fronteira

Implementar e validar os contratos normatizados pela `FT-005` sem iniciar
coleta ampla. A FT cobre código, configuração, estado incremental, fixtures,
testes, amostra mínima controlada, documentação e integração futura ao índice.

## Subcontextos

| Ordem | Contexto | Entrega | Estado |
| ---: | --- | --- | --- |
| 1 | `01-catalogo-e-identidade.md` | descoberta estruturada, normalização e multiautor | concluído |
| 2 | `02-estado-e-cliente.md` | ledger incremental e cliente HTTP responsável | concluído |
| 3 | `03-ativos-nativos.md` | preflight, download, integridade e atualização | concluído |
| 4 | `04-texto-e-epub.md` | extração, Markdown e EPUB derivado | concluído |
| 5 | `05-testes-e-amostra.md` | fixtures, gates, amostra mínima e relatório | concluído |

## Gate de autorização

Gate satisfeito pelo prompt humano `autorizo implementar e testar a FT-006`.
Coleta ampla permanece fora do escopo e exige autorização própria.

## Encerramento

- commit causal: `d1579e891031e3bbabaf23603352bbc0f90f05cd`;
- suíte: 37 testes offline aprovados;
- rastreabilidade: 60 pendências materializadas;
- amostra pública: interrompida corretamente por desafio anti-automação antes
  da descoberta, sem transferência ou mutação do acervo;
- limitação externa: descoberta pública real não pôde ser validada sem evasão;
- pendência separada: coleta ampla continua não autorizada.
