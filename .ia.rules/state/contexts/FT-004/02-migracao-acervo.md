# FT-004/02 - Migracao do acervo

- fase: migracao material.
- objetivo: agrupar cada identidade editorial em diretorio canônico e renomear correlatos pelo mesmo acronimo.
- dependencias: subcontexto 01 validado.
- entradas: inventario pre-migracao, plano deterministico e hashes.
- entregaveis: arvore canônica, relatorio de migracao e inventario pos-migracao.
- restricoes: sem perda, sobrescrita, contador de ordem ou tag inferida; variantes diferentes usam hash curto.
- validacoes: contagem, soma de bytes, SHA-256, metadados, repeticao sem mudanca e ausencia de arquivos planos.
- estado: em andamento.
- aceite: todos os 1576 arquivos correlatos preservados em grupos canônicos ou diagnostico bloqueante nominal.

## Plano

1. diagnosticar os 11 bloqueios nominais do dry-run sem derivar URL por padrao;
2. resolver cada fonte por evidencia local suficiente ou aquisicao de rede validada;
3. repetir o plano ate obter inventario estavel e zero problema bloqueante;
4. aplicar a transacao com journal e validar contagem, bytes e hashes pre/post;
5. repetir o dry-run sobre a arvore canônica, finalizar quarentena e registrar relatorio.

## Entrada causal

- commit material do contrato: `fc95baeba5e399c6825cb7e06146163e0e59c122`;
- commit de rastreabilidade: `fb792a4`;
- plan ID bloqueado: `5ebf1ffcf3a378f52085e5cdb49a241dab0a2de12bac35a3edc4a08108794ee2`;
- inventario SHA-256: `9900a18f91bac8480c38e1aee91ee28d01f485cad9fe19e2b3995d83599f0e28`;
- bloqueios: os 11 paths listados no handoff do subcontexto 01.
