# Subcontexto - implementação da FT-030

- ordem: 2;
- estado: bloqueado até autorização humana expressa;
- dependência: FT-029 concluída;
- tarefa futura: reutilizar o writer comum e o gate incremental, comparar o
  candidato antes da persistência, propagar `changed/no-op`, distinguir logs e
  condicionar commit a diff versionado real;
- validação futura: fonte atual, uma mudança real, índice/chunks iguais e
  divergentes, chamadas diretas/compostas, múltiplas publicações, toque temporal,
  serialização repetida, worktree limpa, falha/interrupção e compatibilidade;
- proibições: implementação paralela, mudança da fórmula hash+`mtime`, reset,
  restore ou limpeza para mascarar falso positivo, e absorção de saída alheia.
