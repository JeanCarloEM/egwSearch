# Fonte da FT-018

- origem: prompt humano superveniente no Codex Desktop
- recebido_em: `2026-08-02`
- incorporação: enfileirada após a FT-017
- destinos: RCF aplicável, analisador de chunking, indexador, downloader,
  wrappers npm, testes e estado canônico

## Solicitação integral

> não interrompa a execução atual, mas adicione a sua fila, criar uma FT e em seguida implementá-la: Ao executar direta ou indiretamente — inclusive por `baixar.py` ou npm equivalente — o avaliador de métodos de chunking DEVE verificar se a última execução foi concluída com sucesso há menos de 24 horas. Nesse caso, NÃO DEVE executar novamente, salvo parâmetro explícito de recálculo forçado, que DEVE ser corretamente propagado por todos os comandos intermediários.
