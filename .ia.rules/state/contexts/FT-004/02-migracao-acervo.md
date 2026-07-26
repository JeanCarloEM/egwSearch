# FT-004/02 - Migracao do acervo

- fase: migracao material.
- objetivo: agrupar cada identidade editorial em diretorio canônico e renomear correlatos pelo mesmo acronimo.
- dependencias: subcontexto 01 validado.
- entradas: inventario pre-migracao, plano deterministico e hashes.
- entregaveis: arvore canônica, relatorio de migracao e inventario pos-migracao.
- restricoes: sem perda, sobrescrita, contador de ordem ou tag inferida; variantes diferentes usam hash curto.
- validacoes: contagem, soma de bytes, SHA-256, metadados, repeticao sem mudanca e ausencia de arquivos planos.
- estado: pendente.
- aceite: todos os 1576 arquivos correlatos preservados em grupos canônicos ou diagnostico bloqueante nominal.
