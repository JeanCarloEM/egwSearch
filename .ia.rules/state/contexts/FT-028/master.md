# Contexto mestre - FT-028

## Identidade

- FT: `FT-028`.
- tipo: `implementação de código`.
- criado_em: `2026-08-09T23:26:17-03:00`.
- fonte: `.ia.rules/state/requests/FT-027/source.md`.
- estado: concluída e sincronizada.
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

## Resultado

- `_current_manifest()` valida conclusão, hashes e `mtime` do fonte antes de
  `inspect_asset()` e dos experimentos;
- resultado íntegro não expira pelo relógio e é reutilizado sem reescrita;
- ausência, hash divergente, fonte posterior ou force acionam recálculo;
- conclusão usa escrita atômica incondicional, renovando o resultado mesmo se
  a serialização coincidir; falha/interrupção não cria nem substitui manifesto;
- parâmetros e propagação existentes foram preservados e seus textos de ajuda
  alinhados ao contrato;
- 127 testes Python, 12 testes Node, compilação TypeScript/Python,
  `git diff --check` e rastreabilidade com 924 cláusulas foram aprovados;
- commits: estado `eaa8f3d`, norma `c1a6351`, implementação `2973124` e
  sincronização pendente do presente fechamento.
