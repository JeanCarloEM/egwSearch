# FT-006/05 - Testes e amostra controlada

- tipo: código e validação.
- objetivo: executar suíte offline, depois uma amostra pública mínima e somente
  então habilitar proposta de coleta ampliada separadamente autorizada.
- métricas: descobertos, pulados, baixados, atualizados, extraídos,
  convertidos, rejeitados, falhos, taxa e bloqueios.
- restrição: desafio anti-automação ou `403` encerra a amostra sem evasão.
- suíte offline: 37 testes aprovados, incluindo duas execuções da amostra por
  fixture com hashes e timestamps inalterados na repetição.
- amostra pública: uma execução em `pt-br-pioneiros`, limitada a um item e um
  trabalhador; desafio anti-automação detectado antes da descoberta.
- resultado público: `blocked=true`, `discovered=0`, `downloaded=0`,
  `extracted=0`, `converted=0`; nenhuma evasão ou repetição.
- estado: concluído com limitação externa registrada.
