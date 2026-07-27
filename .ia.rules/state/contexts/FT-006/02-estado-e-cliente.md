# FT-006/02 - Estado e cliente responsável

- tipo: código.
- objetivo: ledger incremental, cache, retomada, condicionais, taxa, jitter,
  backoff, `Retry-After`, tentativas e parada por contenção.
- testes: relógio/rede simulados, repetição determinística e falhas injetadas.
- implementação: ledger JSON atômico, retomada, limitador compartilhado,
  atraso/jitter, até três tentativas, backoff limitado, `Retry-After`,
  condicionais e parada por contenção.
- evidência: relógio e respostas simulados; `403` sem repetição e `429`
  respeitando espera.
- estado: concluído.
