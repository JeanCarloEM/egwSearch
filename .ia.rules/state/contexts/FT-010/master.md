# Contexto mestre - FT-010

## Identidade

- FT: `FT-010`.
- tipo: `implementacao_normativa`.
- fonte: `.ia.rules/state/TODO.ia.md:1416`, `:1577` e `:1763`.
- estado: concluído.

## Objetivo e integração

Normatizar como uma única evolução do coletor: suspensão e handoff humano sem
evasão; estado de runtime central, protegido e fora do Git; publicação
transacional completa com staging e commit por allowlist. A FT absorve o
bootstrap normatizado pela FT-009 e preserva os contratos já concluídos das
FT-006 a FT-008.

## Subcontextos

| Ordem | Contexto | Entrega | Estado |
| ---: | --- | --- | --- |
| 1 | `01-handoff-humano.md` | detecção, suspensão, sessão humana e retomada | concluído |
| 2 | `02-estado-runtime.md` | classificação, raiz, retenção, limpeza e Git | concluído |
| 3 | `03-transacao-publicacao.md` | completude, índice, staging e commit | concluído |

## Decisões estruturantes

- Em domínio de terceiro, falso positivo não autoriza bypass; a automação é
  encerrada ou desacoplada e o humano usa sessão normal, com retomada somente
  após validação objetiva.
- `constructor/.state/` é a raiz operacional já existente e ignorada; a
  configuração deverá centralizar seus subdiretórios sem criar raiz paralela.
- PDF, EPUB, metadado e derivados canônicos são produto/publicação; perfil,
  cache, ledger, temporário, log, lock e credencial são runtime e ficam fora do
  índice Git.
- Commit por publicação será opt-in explícito, serializado e limitado à
  allowlist calculada; worktree alheia permanece intocada.

## Aceite

Todos os requisitos e conflitos da fonte devem estar refletidos no RCF global
e especializado, com fases técnicas ordenadas, testes verificáveis e nenhum
código alterado nesta FT.

## Validação

- RCF global incorporou §§42.9-42.11.
- RCF especializado incorporou §§7.1-7.3 e ampliou testes.
- mapa causal registrou 23 linhas materiais pendentes da FT-011.
- `npm run agent:rcf`: 117 entradas e 116 linhas materiais, aprovado.
