# Fonte da FT-020

- origem: prompt humano superveniente no Codex Desktop
- recebido_em: `2026-08-03`
- incorporacao: imediata
- destinos: RCF de publicacoes, RCF especializado, estado canonico,
  transacao Git, downloader, analisador, indexador, wrappers e testes

## Solicitacao integral

> Quando o ciclo de download de uma publicação e de cálculo dos chunks adequados — executados isoladamente ou em conjunto — for concluído, DEVE ser realizado imediatamente, ao término do enrriquecimento e do cálculos dos algorítimos de cada publicação, imediatamente, um commit contendo exclusivo todo o conteúdo criado ou modificado referente à publicação e à respectiva indexação, incluindo metadados e demais artefatos relacionados.

## Adicao superveniente

> O `baixar.py` e o script de cálculo dos chunks adequados, quando executados em modo global, DEVEM manter um arquivo de log que registre com precisão o ponto exato de execução alcançado. Em execuções subsequentes, o processamento DEVE ser retomado automaticamente a partir desse ponto, salvo quando houver parâmetro explícito indicando `reset` ou comportamento análogo.
