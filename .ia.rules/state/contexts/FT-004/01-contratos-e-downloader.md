# FT-004/01 - Contratos, migrador e downloader

- fase: codigo e scripts.
- objetivo: definir regra deterministica compartilhada e eliminar destinos legados do downloader.
- entradas: RCF §§41-46, acervo plano, `baixar.py`, metadados locais.
- entregaveis: RCF especifico, modulo comum, migrador temporario, downloader canônico e testes unitarios.
- restricoes: preservar cabecalho/licenca; nao executar download externo durante validacao local; nao mover acervo antes de validar plano.
- validacoes: inventario, dry-run, repeticao, colisao, path, metadado, import sem efeito e falha retomavel.
- estado: pendente.
- aceite: plano deterministico e downloader incapaz de recriar a estrutura plana.
