# FT-006/03 - Ativos nativos

- tipo: código.
- objetivo: pular ativo íntegro sem requisição, adquirir PDF/EPUB nativo,
  detectar atualização real, validar MIME/assinatura/hash e promover
  atomicamente.
- testes: concluído, parcial, corrompido, idêntico, distinto e atualizado.
- implementação: preflight local antes de rede, compatibilidade v2/v3,
  validação de assinatura/tamanho/hash, promoção atômica e variantes.
- evidência: repetição idempotente sem abrir stream, parcial rejeitado,
  conteúdo distinto preservado, atualização por hash remoto e `304` sem
  alterar timestamp.
- estado: concluído.
