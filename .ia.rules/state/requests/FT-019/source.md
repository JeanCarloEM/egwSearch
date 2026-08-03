# Fonte da FT-019

- origem: prompt humano superveniente no Codex Desktop
- recebido_em: `2026-08-03`
- incorporacao: imediata
- destinos: RCF de publicacoes, RCF especializado do downloader, estado
  canonico, `baixar.py` e testes direcionados

## Solicitacao integral

> A última publicação processada pelo `baixar.py` era a **1105**, quando ocorreu uma interrupção. Ao reexecutar, o script reinicia desde a primeira publicação, em vez de detectar e pular imediatamente as já concluídas, salvas e commitadas. Isso é evidenciado pela reabertura de janelas e repetição de processamento e cálculos desnecessários. O script DEVE retomar do ponto pendente, ignorando eficientemente tudo o que já estiver concluído.

