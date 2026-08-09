# Contexto mestre - FT-023

## Identidade

- FT: `FT-023`.
- tipo: `correção de regressão e migração compatível`.
- fonte: `.ia.rules/state/requests/FT-023/source.md`.
- estado: concluída e sincronizada.

## Causa comprovada

`GlobalProgressJournal._load()` converte a forma v1 para v2, mas continua
exigindo igualdade com o fingerprint v5 no mesmo gate. Como o fingerprint
inclui schema e lista de coleções, a ampliação append-only torna impossível
concluir a migração e bloqueia toda execução antes do inventário.

## Solução

- o consumidor deve declarar explicitamente fingerprints legados aceitos;
- o downloader deve calcular o fingerprint v4 conhecido a partir das dez
  coleções preservadas, sem constante opaca;
- somente diário v1, com fingerprint declarado, ferramenta/escopo iguais e
  ordem compatível pode adotar o fingerprint atual durante a conversão v2;
- qualquer outra divergência continua exigindo reset explícito;
- a migração preserva confirmações, unidade corrente e amplia somente a ordem.

## Aceite

1. fixture idêntica ao diário real migra sem `--restart`;
2. confirmações v1 são preservadas e novas coleções ficam pendentes;
3. fingerprint legado não declarado, ordem divergente ou diário v2 divergente
   continuam bloqueados;
4. o diário operacional real é migrável sem abrir catálogo ou obra;
5. testes e rastreabilidade são sincronizados sem versionar runtime.

## Fechamento

- implementação: `d4d6ec069fb6180d196189902d7f2dbdc5a61f80`;
- o fingerprint v4 conhecido é calculado a partir das dez coleções preservadas,
  não aceito por constante opaca ou wildcard;
- 111 testes Python foram aprovados;
- as duas sentenças materiais foram sincronizadas;
- o diário operacional foi migrado atomicamente, sem rede, para v2/27 coleções,
  preservando `publication:1740:processing` e zero confirmações.
