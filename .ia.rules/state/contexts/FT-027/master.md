# Contexto mestre - FT-027

## Identidade

- FT: `FT-027`.
- tipo: `implementação normativa`.
- criado_em: `2026-08-09T23:26:16-03:00`.
- fonte: `.ia.rules/state/requests/FT-027/source.md`.
- estado: em execução.
- dependência posterior: FT-028.

## Auditoria real

- `publication_analysis.py` já calcula hashes antes do parsing custoso e os
  persiste em `asset.hashes`;
- `_current_manifest()` já valida schema, gerador, catálogo, tamanho, hashes e
  atualização do metadado editorial;
- a conclusão é escrita atomicamente e `force_recalculate` já atravessa CLI,
  wrapper TypeScript, downloader e indexador;
- o reuso, porém, está limitado a 24 horas e não compara o `mtime` da fonte ao
  manifesto;
- `_write_json_if_changed()` pode não renovar o `mtime` após recálculo de bytes
  idênticos, perpetuando a invalidação temporal;
- o RCF vigente normatiza a janela de 24 horas e diverge da regra solicitada.

## Objetivo e aceite

Substituir cirurgicamente a janela temporal pela fórmula hash+`mtime`, manter
as demais provas de validade e declarar escrita atômica somente após conclusão.
A FT conclui com RCF centralizado, rastreável e sem duplicação.
