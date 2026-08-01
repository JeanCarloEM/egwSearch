# FT-004/02 - Migracao do acervo

- fase: migracao material.
- objetivo: agrupar cada identidade editorial em diretorio canônico e renomear correlatos pelo mesmo acronimo.
- dependencias: subcontexto 01 validado.
- entradas: inventario pre-migracao, plano deterministico e hashes.
- entregaveis: arvore canônica, relatorio de migracao e inventario pos-migracao.
- restricoes: sem perda, sobrescrita, contador de ordem ou tag inferida; variantes diferentes usam hash curto.
- validacoes: contagem, soma de bytes, SHA-256, metadados, repeticao sem mudanca e ausencia de arquivos planos.
- estado: concluido.
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

## Resolucao probatoria dos bloqueios

- as paginas oficiais `text.egwwritings.org` confirmaram titulo, idioma, autoria, codigo bibliografico e link EPUB dos nove panfletos/livro e dos dois periodicos;
- codigos confirmados: `PH026`, `PH168`, `3Red`, `4Red`, `6Red`, `7Red`, `8Red`, `PH124`, `RH`, `ST` e `SMO`;
- URLs oficiais confirmadas: `https://media2.egwwritings.org/epub/en_PH026.epub`, `en_PH168.epub`, `en_3Red.epub`, `en_4Red.epub`, `en_6Red.epub`, `en_7Red.epub`, `en_8Red.epub`, `en_PH124.epub`, `en_RH.epub`, `en_ST.epub` e `pt_SMO.epub` sob o mesmo host/path;
- cada download temporario foi comparado ao asset local por tamanho e SHA-256; os 11 pares foram integralmente identicos;
- os nove metadados legados receberam a fonte EPUB comprovada; os dois periodicos receberam metadado de procedencia nominal;
- nenhum byte de PDF ou EPUB foi alterado.

## Plano liberado

- arquivos: 1578, compostos pelos 1576 originais e pelos dois metadados de procedencia adicionados;
- bytes: `638102876`;
- grupos: 527;
- problemas: zero;
- inventario SHA-256: `fe9d9b2f4336ee89796140fd3d7aeeafe6a234e55080acd433088e706cb16cbf`;
- plan ID: `5660215656f00e721abc0d67344508380fbc8bc62e063d77816a3e32aded50cb`;
- repeticao: plano, inventario, contagens e problema zero identicos.

## Execucao e recuperacao

- o primeiro `apply` encontrou bloqueio transitorio do Windows ao substituir atomicamente o journal;
- o rollback automatico restaurou os 592 movimentos persistidos; o metadado movido na janela anterior ao registro foi identificado por status Git, hash validado e devolvido ao path original;
- o inventario restaurado reproduziu exatamente o plan ID liberado;
- a causa estrutural foi corrigida com protocolo `intencao persistida -> movimento -> confirmacao`, rollback de registro pendente e retry limitado de `PermissionError` no replace atomico;
- teste injetado passou a comprovar falha de persistencia depois do movimento e restauracao integral;
- 12 testes sem rede passaram antes da nova aplicacao.

## Resultado

- journal causal: `5660215656f00e721abc0d67344508380fbc8bc62e063d77816a3e32aded50cb`;
- estado final do journal: `finalized`;
- grupos canônicos: 527;
- arquivos: 1578;
- bytes: `638102876`;
- PDF: 525; EPUB: 526; metadados: 527;
- arquivos planos residuais em diretorio de tipo: zero;
- acoes residuais: zero;
- problemas residuais: zero;
- inventario pos-migracao SHA-256: `9f1d10744d05125287c49666657f0cccce2bade4644f0dc340e98f22e20623a9`;
- post plan ID: `35b8a85ca167dd65410d502e6629e58ea05bdf0426fbfac6242efd9c574c1de0`;
- repeticao pos-migracao: identica;
- comparacao de conteudo pre/post por `kind`, tamanho e SHA-256: 1578/1578, zero ausente e zero adicionado.
