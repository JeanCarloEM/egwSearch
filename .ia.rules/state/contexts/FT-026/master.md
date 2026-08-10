# Contexto mestre - FT-026

## Identidade

- FT: `FT-026`.
- tipo: `correção de regressão e migração compatível`.
- criado_em: `2026-08-09T22:46:01-03:00`.
- fonte: `.ia.rules/state/requests/FT-026/source.md`.
- estado: concluída e sincronizada.

## Causa comprovada

O fingerprint do downloader inclui a versão do analisador. A FT-025 elevou-a
de `2` para `3`, mas `_known_legacy_downloader_fingerprints()` enumera somente
o fingerprint v4/analisador v2 e `GlobalProgressJournal._load()` permite adoção
de fingerprint atual somente durante a conversão estrutural v1 para v2. Assim,
o diário v2 íntegro e com a ordem corrente é recusado antes do inventário.

## Solução

- permitir migração de fingerprint no mesmo schema somente quando o consumidor
  declarar o valor anterior em allowlist finita;
- calcular o fingerprint v5/analisador v2 pela configuração e pelas 27
  coleções correntes, sem aceitar constante opaca ou wildcard;
- preservar `confirmed`, `current`, `last_confirmed`, ordem e `next_index`;
- atualizar atomicamente apenas o fingerprint do diário após todas as provas;
- continuar rejeitando divergência desconhecida, ferramenta, escopo, schema,
  ordem ou estrutura incompatível;
- provar a correção sem rede e sem versionar ou apagar o diário operacional.

## Plano

1. Registrar causa, contrato e fronteira de preservação.
2. Normatizar evolução enumerada de fingerprint dentro do mesmo schema.
3. Implementar migração geral fail-safe e allowlist específica do downloader.
4. Validar testes direcionados, suíte de publicações e migração operacional
   sem rede.
5. Sincronizar rastreabilidade e fechar a FT.

## Aceite

1. fixture equivalente ao diário real v2 migra sem `--restart`;
2. estado corrente e limites confirmados permanecem idênticos;
3. fingerprint não allowlisted e ordem divergente continuam bloqueados;
4. o diário real pode ser migrado sem abrir catálogo, publicação ou rede;
5. nenhuma alteração concorrente do acervo integra os commits.

## Resultado

- `GlobalProgressJournal` aceita evolução de fingerprint no schema v2 somente
  quando o valor anterior pertence à allowlist finita do consumidor e todas as
  demais provas estruturais permanecem válidas;
- o downloader calcula os fingerprints históricos v4 e v5/analisador v2 a
  partir das identidades de coleção enumeradas;
- 125 testes Python, 12 testes Node e compilação Python foram aprovados;
- o diário operacional foi migrado sob lock e sem rede, alterando somente
  `fingerprint`; `current`, `confirmed`, `last_confirmed`, `next_index` e
  `order` permaneceram iguais;
- commits faseados: estado `cc5fdfb`, norma `a646ef1`, implementação
  `05a8970` e sincronização pendente do presente fechamento.
