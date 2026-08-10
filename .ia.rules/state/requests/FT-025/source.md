# Fonte humana - FT-025

Em `2026-08-09`, solicitou-se adaptar e normatizar o indexador e o fluxo de
análise/cálculo de chunks para suportarem integralmente os novos formatos e
tipos ingeridos, especialmente JSONs estruturados de Bíblias, léxicos,
dicionários, concordâncias e equivalentes.

A evolução deve reconhecer a semântica de cada schema, preservar hierarquia,
metadados, referências e unidades naturais, impedir tratamento de JSON como
texto plano e aplicar chunking compatível sem perda, concatenação indevida ou
fragmentação semântica. Formatos já suportados devem permanecer compatíveis.

Para Bíblias, livro, capítulo e versículo são fronteiras autoritativas. Para
léxicos, dicionários e concordâncias, cada entrada e suas relações constituem a
unidade semântica indivisível. A solicitação autoriza atualizar norma, código,
índice, análise, catálogo experimental, benchmarks, validações e testes.

