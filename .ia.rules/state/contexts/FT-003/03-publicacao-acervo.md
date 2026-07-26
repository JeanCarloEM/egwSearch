# Subcontexto 03 - Publicacao, acervo e dados formativos

- ordem: 3 de 3
- fase: normatizacao
- fontes: `.ia.rules/state/TODO.ia.md:214` e `.ia.rules/state/TODO.ia.md:886`
- objetivo: consolidar pagina institucional, estrutura canonica do acervo, download, migracao, indice global, dados formativos, hashes, capas, build e deploy.
- entradas: acervo real sob `src/publications/egw/`, `src/publications/egw/baixar.py`, metadados `*.source.json` e anexo `NORMA-IF-SIL-001`.
- dependencias: identidade editorial, paths publicos, validacao de PDF/EPUB, configuracao e cadeia local/CI.
- restricoes: nesta fase nenhum arquivo do acervo, codigo, script, workflow, build ou deploy e alterado.
- entregaveis: secoes RCF da cadeia publica e incorporacao integral de `NORMA-IF-SIL-001`.
- validacoes: raiz e propriedades fechadas; seguranca de URL/EPUB/PDF; hashes dos originais; capa regeneravel; pagina sem links; assets publicos diretamente acessiveis; migracao futura sem perda.
- efeitos posteriores: FT-004 materializa toda a cadeia publica apos autorizacao.
- estado: concluido no RCF §§40-49.
