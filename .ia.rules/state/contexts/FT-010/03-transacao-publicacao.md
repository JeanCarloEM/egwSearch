# FT-010/03 - Transação por publicação

- ordem: 3 de 3.
- estado: pendente.
- objetivo: normatizar `COMPLETA_E_PAREADA`, arquivos impactados, índices,
  staging seletivo, commit, retomada, concorrência e push separado.
- restrições: sem `git add .`/`-A`, sem commit parcial, vazio, agrupado ou com
  alteração alheia; nenhum efeito Git sem opt-in explícito da execução.
- aceite: allowlist determinística, validação staged, rollback, idempotência e
  testes de conteúdo exato do commit definidos.
