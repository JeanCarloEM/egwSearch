# Fonte humana - FT-027/FT-028

Em `2026-08-09`, solicitou-se inspecionar integralmente o estado real do cálculo
de chunks, seus artefatos, parâmetros diretos/propagados, RCF e contratos, sem
presumir ausência de funcionalidade, e tornar o recálculo incremental,
determinístico e orientado por hash.

A regra requerida para cada fonte é:

```text
recalcular = force || !resultado_existe || hash_atual != hash_registrado ||
             mtime_fonte > mtime_resultado
```

O hash deve permanecer a evidência de identidade do conteúdo e o `mtime`, uma
invalidação adicional. Resultado existente, válido, igual ou posterior à fonte
e com hash idêntico deve ser reutilizado sem parsing, cálculo ou processamento
equivalente; `force` direto ou propagado deve prevalecer. Hash e metadados só
podem representar conclusão bem-sucedida, nunca falha ou interrupção.

Devem ser preservadas execução individual, global/batch, retomada, chamadas
indiretas e toda infraestrutura equivalente existente. RCF, implementação e
testes devem ser alterados somente no delta necessário e cobrir ausência de
resultado, reuso, mudança de hash, fonte posterior, resultado posterior,
`force` direto/propagado e falha/interrupção.
