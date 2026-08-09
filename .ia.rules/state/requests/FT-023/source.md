# Fonte humana - FT-023

Em `2026-08-09`, após a implementação das FTs 021/022, a execução de
`npm run publications:baixar` falhou antes da descoberta com:

```text
ERRO_CONTRATO: diário global incompatível; use reset explícito:
D:\trampo\egwSearch\constructor\.state\egwsearch\logs\baixar.global.json
```

O diário real preservado usa `publication-global-progress/v1`, fingerprint
`e8f2c8cd0d85a8eceb2a1714a099dbf7dd8dbbeb8ce0eb9d92e07ade9e8dc2bc` e as dez
coleções anteriores. A configuração v5 acrescenta folhas sem renomear nem
reordenar essas identidades e produz novo fingerprint causal.

Autoriza-se corrigir a regressão sem descartar progresso válido, mantendo
reset explícito para qualquer fingerprint, ordem, ferramenta ou escopo que não
corresponda à migração finita comprovada.
