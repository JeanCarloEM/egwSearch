# Contexto mestre - FT-028

## Identidade

- FT: `FT-028`.
- tipo: `implementação de código`.
- criado_em: `2026-08-09T23:26:17-03:00`.
- fonte: `.ia.rules/state/requests/FT-027/source.md`.
- estado: em execução.
- dependência: FT-027 concluída.

## Escopo

- centralizar o gate antes de `inspect_asset()` e dos experimentos;
- reutilizar `hash_file`, manifesto e escrita atômica existentes;
- invalidar por ausência, hash divergente ou `mtime` da fonte posterior;
- fazer `force_recalculate` prevalecer em todas as rotas existentes;
- garantir que recálculo bem-sucedido atualize atomicamente o resultado mesmo
  quando seu conteúdo serializado coincidir;
- não alterar schema nem criar cache/implementação paralela.

## Validação mínima

Cobrir os oito cenários humanos, EPUB/PDF/JSON estruturado, chamadas direta e
propagada, falha/interrupção, suíte integral e rastreabilidade. Nenhuma saída
operacional ou alteração concorrente do downloader integra os commits.
