# FT-004/01 - Contratos, migrador e downloader

- fase: codigo e scripts.
- objetivo: definir regra deterministica compartilhada e eliminar destinos legados do downloader.
- entradas: RCF §§41-46, acervo plano, `baixar.py`, metadados locais.
- entregaveis: RCF especifico, modulo comum, migrador temporario, downloader canônico e testes unitarios.
- restricoes: preservar cabecalho/licenca; nao executar download externo durante validacao local; nao mover acervo antes de validar plano.
- validacoes: inventario, dry-run, repeticao, colisao, path, metadado, import sem efeito e falha retomavel.
- estado: concluido.
- aceite: plano deterministico e downloader incapaz de recriar a estrutura plana.

## Decisoes

- Python permanece no processamento bibliografico por ser o runtime preexistente e adequado a PDF, EPUB, imagem e Selenium.
- O contrato comum usa somente biblioteca padrao; Requests, tqdm e Selenium ficam restritos a execucao da CLI e sao carregados tardiamente.
- Configuracao causal reside em `config/publications.json`; nenhum script infere raiz, colecao, host ou limite pelo cwd.
- O migrador e interno e temporario em `constructor/publications/`; plano e journal locais permanecem em `constructor/.state/`, ignorado pelo Git.
- A migracao nao foi executada. Os 11 problemas do acervo sao bloqueios do subcontexto 02, nao permissoes para inventar URL ou metadado.

## Entregaveis

- `src/publications/egw/RCF.md`: contrato especifico subordinado.
- `src/publications/egw/publication_contract.py`: identidade, paths, hashes, formatos, colisoes e metadados.
- `constructor/publications/migrate.py`: `plan`, `apply`, `rollback` e `finalize`.
- `src/publications/egw/baixar.py`: importacao sem efeito, rede limitada, destino canônico, incorporacao e metadado atomicos.
- `tests/publications/`: testes unitarios sem rede.

## Evidencias

- `python -m unittest discover -s tests/publications -v`: 10 testes, sucesso.
- `python src/publications/egw/baixar.py --help`: sucesso sem carregar dependencias opcionais.
- `python constructor/publications/migrate.py --help`: sucesso.
- `npm run agent:rcf`: `RCF_OK`, 83550 bytes.
- `npm run agent:status`: sucesso, branch `dev`.
- `npm run agent:verify`: `TSCONFIG_AUSENTE`; gate global permanece pendente ate a materializacao do eixo TypeScript da pagina/build, sem invalidar os testes Python deste subcontexto.
- `git diff --check`: sem erro; somente avisos de conversao futura LF/CRLF em arquivos preexistentes.
- dry-run integral: 1576 arquivos; 638098352 bytes; 527 grupos; 1576 movimentos planejados; nenhuma deduplicacao; 11 problemas bloqueantes.
- inventario SHA-256: `9900a18f91bac8480c38e1aee91ee28d01f485cad9fe19e2b3995d83599f0e28`.
- plan ID repetido em duas execucoes: `5ebf1ffcf3a378f52085e5cdb49a241dab0a2de12bac35a3edc4a08108794ee2`.
- igualdade entre repeticoes: plan ID, inventario e lista de problemas identicos.
- commit material: `fc95baeba5e399c6825cb7e06146163e0e59c122`.
- rastreabilidade: 30 sentencas sincronizadas e validadas no commit `fb792a4`.

## Bloqueios transferidos ao subcontexto 02

- EPUB sem fonte correspondente no metadado do grupo:
  - `egw/en-us/pamphlets/Do You Eat Flesh.epub`;
  - `egw/en-us/pamphlets/In Memoriam - A Sketch of the Last Sickness and Death of Elder James White.epub`;
  - `egw/en-us/pamphlets/Redemption - or the Ministry of Peter and the Conversion of Saul.epub`;
  - `egw/en-us/pamphlets/Redemption - Or the Miracles of Christ, the Mighty One.epub`;
  - `egw/en-us/pamphlets/Redemption - or the Resurrection of Christ; and His Ascension.epub`;
  - `egw/en-us/pamphlets/Redemption - or the Teachings of Christ, the Anointed One.epub`;
  - `egw/en-us/pamphlets/Redemption - or the Teachings of Paul, and his Mission to the Gentiles.epub`;
  - `egw/en-us/pamphlets/What Shall We Teach.epub`;
  - `egw/pt-br/livros/Ser Mãe — O que é.epub`.
- Grupos sem metadado local:
  - `egw/en-us/periodicals/The Review and Herald`;
  - `egw/en-us/periodicals/The Signs of the Times`.

## Handoff

O subcontexto 02 deve resolver os 11 bloqueios por evidencia existente ou aquisicao validada; derivacao de URL por troca de extensao e proibida. Depois, deve gerar novo plano sem problemas, aplicar a transacao, validar inventario pre/post e somente entao finalizar a quarentena.
