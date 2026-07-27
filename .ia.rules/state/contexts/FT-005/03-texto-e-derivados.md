# FT-005/03 - Texto editorial e derivados

- tipo: norma.
- objetivo: permitir incorporação fiel quando PDF e EPUB nativos não existirem.
- entrada: segmentos textuais públicos, ordenáveis e distinguíveis da
  interface.
- saída intermediária: Markdown estruturado, numerado e rastreável.
- saída opcional: EPUB mecanicamente gerado e tecnicamente validado.
- proveniência: URLs e identificadores por segmento, ordem, quantidade,
  primeira/última unidade, lacunas, transformações e relação
  fonte -> Markdown -> EPUB.
- exclusões: navegação, controles, recomendações, telemetria, scripts, estilos,
  publicidade e qualquer conteúdo alheio ao corpo editorial.
- bloqueio: lacuna ou ordem incerta impede estado concluído.
- estado: concluído.

## Aceite

O derivado preserva texto, hierarquia, notas, tabelas textuais, Unicode e ordem;
é marcado como local e nunca recebe URL/hash que o apresente como original.

## Resultado

O RCF exige ausência de PDF/EPUB nativo, completude verificável, separação
editorial determinística, segmentos rastreáveis, Markdown ordenado e EPUB
validado como `local-conversion`, fora dos hashes/URLs formativos originais.
