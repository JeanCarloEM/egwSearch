# Contexto mestre — FT-016

- tipo: `implementacao_codigo`.
- estado: implementação local concluída; commit/rastreabilidade pendentes.
- objetivo: derivar de `src/publications/index.json` um manifesto mínimo,
  determinístico e verificável, sem duplicar registros do índice.
- saída: `src/publications/index.manifest.json`.
- conteúdo: raiz, notação de cardinalidade/nulabilidade e tipos estruturais;
  nenhum hash, fingerprint, total, contagem ou valor observado.
- integração: o mesmo gerador atualiza índice e manifesto; `--manifest-only`
  permite recompor apenas o manifesto.
- preservação: alterações concorrentes do downloader permanecem intocadas.
- evidência: a mesma saída é produzida sem consultar estado ou quantidade de
  publicações; teste direcionado e compilação aprovados.
- pendência: criar commit material somente mediante solicitação humana.
