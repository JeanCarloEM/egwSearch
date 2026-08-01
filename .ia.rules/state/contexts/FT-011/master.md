# Contexto mestre - FT-011

## Identidade

- FT: `FT-011`.
- tipo: `implementacao_codigo`.
- estado: em andamento; FT-010 concluída.
- autorização: prompt humano de `2026-08-01` para concluir todas as fases de
  `baixar.py` com funcionalidade efetiva.
- autorização superveniente: após pergunta explícita sobre a colisão de
  edições, o prompt humano determinou continuar e fazer o necessário para a
  conclusão; aplica-se a evolução recomendada de `book.title`, preservando
  `book.edition: {}`.

## Arquitetura de execução

1. consolidar bootstrap e invocador multi-runtime;
2. centralizar estado local e migração compatível;
3. implementar máquina de estados de desafio e handoff desacoplado;
4. implementar validação e transação Git opt-in por publicação;
5. executar testes, validação local, amostra pública legítima e rastreabilidade.

## Subcontextos

| Ordem | Contexto | Entrega | Estado |
| ---: | --- | --- | --- |
| 1 | `01-bootstrap-runtime.md` | ambiente Python e invocador npm | pendente |
| 2 | `02-runtime-e-handoff.md` | raiz local e sessão humana | pendente |
| 3 | `03-transacao-git.md` | completude, allowlist e commit | pendente |
| 4 | `04-validacao.md` | testes, amostra, trace e encerramento | pendente |

## Invariantes

- runtime local nunca integra Git, build, release ou publicação;
- nenhuma proteção de terceiro é burlada;
- importação de módulos não produz efeito;
- publicação canônica só é concluída com integridade e metadado coerentes;
- efeito Git é explícito, isolado e comprovado;
- falha preserva estado retomável sem fabricar sucesso.
