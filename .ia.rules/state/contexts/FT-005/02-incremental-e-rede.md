# FT-005/02 - Incrementalidade e acesso responsável

- tipo: norma.
- objetivo: eliminar a causa do reprocessamento e tornar cada operação
  retomável, observável e conservadora.
- preflight: estado/índice, identidade remota, metadado, arquivo, validadores
  HTTP e SHA-256 sob necessidade.
- estados mínimos: não processado, em processamento, concluído, pulado,
  incompleto, corrompido, indisponível, não elegível, falha temporária, falha
  permanente e requer revisão.
- rede: sequencial por padrão, taxa explícita, atraso, jitter, timeout,
  tentativas limitadas, backoff, `Retry-After`, cache, condicionais e conexão
  reutilizável.
- contenção: `403`, CAPTCHA, bloqueio ou limitação persistente interrompem a
  unidade sem repetição intensiva ou evasão.
- persistência: temporário segregado e promoção atômica após integridade.
- estado: pendente.

## Aceite

Reexecução equivalente não solicita ativo concluído, não altera timestamps ou
metadados sem mudança material e preserva progresso diante de falha.

