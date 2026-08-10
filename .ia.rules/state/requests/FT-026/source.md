# Fonte humana - FT-026

Em `2026-08-09`, após a conclusão da FT-025, a execução de
`node scripts/publications/run-baixar.ts` falhou antes da descoberta com:

```text
ERRO_CONTRATO: diário global incompatível; use reset explícito:
D:\trampo\egwSearch\constructor\.state\egwsearch\logs\baixar.global.json
```

O diário operacional preservado já usa `publication-global-progress/v2`,
fingerprint `94952aeea831ae6aabad3befe9f4c951ae0d8b6ab2f222c073084a13623f6b31`,
as 27 coleções correntes e a unidade `en-devotionals/publication:89` em
processamento. A FT-025 elevou o analisador causal de v2 para v3 sem alterar a
ordem ou a identidade dessas coleções e passou a produzir o fingerprint
`cbd9b909b194b9df1c9b2d3d54928cf48f4aadaf14e192954daabb40998fccb6`.

A correção deve preservar o progresso válido, admitir somente essa evolução
enumerada e manter reset explícito para qualquer ferramenta, escopo, ordem ou
fingerprint não comprovadamente compatível.
