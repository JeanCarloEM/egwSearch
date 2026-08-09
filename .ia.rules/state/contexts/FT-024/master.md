# Contexto mestre - FT-024

## Identidade

- FT: `FT-024`.
- tipo: `correção fail-safe e materialização offline`.
- fonte: `.ia.rules/state/requests/FT-024/source.md`.
- estado: implementação validada; sincronização de commits em fechamento.

## Causa comprovada

`GitPublicationPublisher.preflight()` consulta o status de toda a raiz de
publicações e rejeita qualquer path que não pertença à unidade corrente ou aos
artefatos globais. O fechamento posterior já calcula, adiciona e commita somente
a allowlist causal da unidade; portanto, o gate anterior transforma preservação
de alteração alheia em bloqueio global sem ampliar a segurança do commit.

O `--no-network` existente é exclusivo de fixture e rejeita o catálogo canônico,
embora checkpoints completos já contenham ordem, identidade, segmentos e URLs
necessários para retomar materialização local.

## Solução

- limitar o preflight à unidade corrente e aos artefatos globais compartilhados;
- manter alteração alheia visível no Git, intocada e fora de staging/commit;
- preservar alteração preexistente da própria unidade em recuperação auditável,
  reconciliá-la com a base íntegra e reconstruir artefato global causal;
- criar modo/comando canônico de materialização offline baseado somente em
  checkpoints/arquivos locais, inclusive escopo inequivocamente contido no
  prefixo enriquecido de uma descoberta parcial;
- não inicializar navegador, cliente HTTP, DNS ou rate limiter de rede nesse modo;
- deixar itens sem insumo como pendentes, continuar os independentes e nunca
  confirmar coleção incompleta;
- retomar itens falhados na execução corrente sem reiniciar checkpoints.
- desambiguar colisões de rota por ID remoto sem alterar título/autoria;
- recuperar transacionalmente unidade rastreada sobrescrita, preservando cópia
  integral em runtime antes da restauração;
- recalcular análise inválida e reconstruir índice duplicado/incompatível sem
  exigir comando manual auxiliar.

## Aceite

1. dois manifestos sujos de publicação A não bloqueiam preflight/commit de B e
   não aparecem no commit de B;
2. path parcial da própria unidade é preservado e reconciliado; global derivado
   é reconstruído e validado sem bloquear itens independentes;
3. o comando offline processa checkpoint completo ou escopo comprovado de
   prefixo parcial sem navegador ou HTTP;
4. checkpoint ausente/incompleto e ativo local ausente são reportados como
   pendentes, sem impedir coleções posteriores nem confirmar falso sucesso;
5. a execução corrente permanece ativa e os dois manifestos não perdem bytes;
6. testes, RCF e rastreabilidade são sincronizados antes do fechamento.
7. IDs remotos colidentes nunca compartilham destino gravável e a unidade
   anterior é restaurada byte a byte a partir de base Git íntegra;
8. índice duplicado, corrompido ou com análise divergente se autorrepara por
   reconstrução/reanálise mínima e escrita atômica.

## Estado operacional

- o preflight foi limitado à unidade e aos globais causais;
- `publications:materialize` reutiliza checkpoint completo ou deriva escopo
  comprovado de prefixo parcial, não carrega runtime HTTP/navegador, desativa
  DNS e preserva pendências;
- lock consultivo de SO serializa coleta/materialização/indexação e não deixa
  stale lock;
- uma tentativa de encadeamento baseada em `Wait-Process` iniciou cedo, foi
  encerrada somente em seus PIDs e substituída por polling read-only;
- a promoção local válida de `1808` foi deduplicada por reconstrução integral
  do índice e commitada exclusivamente em `66dcc77`;
- o job offline terminou em `761.005` segundos com 389 falhas e 18 pendências;
- a falha revelou bloqueio por global parcial e sobrescrita `1034`→`1333`;
- o indexador restaurou transacionalmente a unidade `1034` a partir de `HEAD`,
  preservando a árvore divergente em runtime recuperável, e reconstruiu índice
  integral de 741 entradas;
- a publicação `1333` foi materializada offline em rota própria, revalidada e
  commitada exclusivamente em `f87bafa8f88b707818b06edef0eccf71311ec2`;
- a reexecução offline idempotente terminou em `10.4` segundos, com zero HTTP,
  zero pendência, zero falha e nenhum novo commit;
- 119 testes Python, oito testes Node, compilação, bootstrap, diff-check e
  rastreabilidade de 900 cláusulas passaram; `agent:rcf` encerrou com código 0
  e preservou o diagnóstico raiz conhecido `RCF_DEGRADED`;
- os dois manifestos independentes de `a-ciencia-do-bom-viver` permanecem
  visíveis, byte a byte fora do staging e dos commits da FT.
