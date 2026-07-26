# FT-004/03 - Indice, capas, site e artefato

- fase: geracao.
- objetivo: gerar deterministicamente dados formativos, hashes, capas, indice global, pagina institucional e arvore publica.
- dependencias: subcontexto 02 validado.
- entradas: acervo canônico e configuracao versionada.
- entregaveis: gerador, validadores, `cover.png`, indice, pagina e artefato publico.
- restricoes: originais imutaveis; capa EPUB precede PDF; `formative_data` fechado; pagina sem links ao acervo/indice; nenhum intermediario publicado.
- validacoes: formato, metadado, identidade editorial, hashes, URLs, PNG, dimensoes, regeneracao, determinismo, HTML, assets e base path.
- estado: em andamento, bloqueado somente na decisao editorial descrita abaixo.
- aceite: build local completo, reproduzivel e validado.

## Evolucao das rotas do acervo

- autorizacao humana explicita recebida em `2026-07-26` para evoluir o RCF,
  o contrato e o migrador e aplicar imediatamente a normalizacao fisica;
- rota canônica normalizada para
  `<autor>/<idioma>/<tipo>/<slug-titulo>/`, com slug ASCII em minusculas,
  sem acentos, diacriticos ou caracteres especiais e separado por hifens;
- RCF normativo: commit `2024dbd`; implementacao e renomeacoes:
  `0507203f6b0c575ab1f0dfb3e9bc33650c5c4da6`;
- plano aplicado:
  `25ef198629963f60f175e1745eceb567fbe9f2069c4254853709cfc4b616b7fd`,
  com 527 diretorios e 1578 arquivos, totalizando 638102876 bytes;
- journal finalizado, incluindo dez renomeacoes apenas de caixa por salto
  temporario seguro no Windows;
- o multiconjunto pre/post de tipo, tamanho e SHA-256 permaneceu identico:
  zero arquivo perdido, acrescentado, fundido ou alterado;
- plano posterior:
  `dd726ed14e2ea1f98f120348db8a4e133882f6c6fe68e038af1a0dbe5dda1a27`,
  inventario SHA-256
  `e1fe12163b972cad8f339c7d59bf953be4f4e00b52b6d137a1c2915cbda2ee50`,
  zero acao, zero problema e repeticao identica;
- a normalizacao de rota nao resolve nem altera a decisao editorial abaixo.

## Auditoria inicial

- runtime observado: Python 3.14.0;
- dependencias proporcionais ensaiadas: `Pillow==12.3.0` e
  `pypdfium2==5.12.1`, ambas fixadas em
  `requirements-publications.txt`;
- grupos descobertos: 527;
- formatos: 526 EPUB e 525 PDF;
- capas editoriais EPUB utilizaveis: 525, todas JPEG;
- dimensoes das capas EPUB: 405 em 546 x 801 e 120 em 546 x 800;
- fallback PDF necessario: `Christ Our Saviour`, sem EPUB, e
  `The Impending Conflict`, cujo EPUB OCF nao contem o Package Document
  declarado;
- a primeira pagina dos dois PDFs de fallback e tecnica e inadequada; a
  terceira pagina possui titulo e autoria visiveis e e a primeira pagina
  editorial adequada;
- autoria estruturada dos 525 EPUBs legiveis: `Ellen G. White`;
- idiomas estruturados: 428 `en` e 97 `pt`, compativeis com as colecoes
  configuradas `en-us` e `pt-br`;
- divergencias candidatas que o gerador devera classificar, sem escolha
  silenciosa: 19 entre titulo canônico e Package Document EPUB e 65 entre
  titulos visiveis/estruturados de pares PDF/EPUB.

## Bloqueio normativo

O RCF §44 determina `book.edition: {}` e proibe emitir documento quando
detalhe de edicao for necessario para distinguir a publicacao ate decisao
especifica. A auditoria encontrou seis colisoes de titulo-base, abrangendo
12 grupos:

1. `Gospel Workers (1892_1893 ed.)` e `Gospel Workers (1915 ed.)`;
2. `Life Sketches of James White and Ellen G. White (1880 ed.)` e
   `Life Sketches of James White and Ellen G. White (1888 ed.)`;
3. `The Great Controversy` e `The Great Controversy (1888 ed.)`;
4. `A Ciência Do Bom Viver` e `A Ciência do Bom Viver (condensado)`;
5. `Caminho a Cristo` e `Caminho a Cristo (nova edição)`;
6. `O Grande Conflito` e `O Grande Conflito (condensado)`.

Nenhum indice ou documento formativo foi emitido. A continuacao exige
decisao humana evolutiva sobre como preservar a distincao dessas edicoes sem
violar o escopo fechado de `formative_data`. A alternativa recomendada e
tratar os qualificadores oficiais ja preservados nos titulos canônicos como
parte indivisivel de `book.title`, manter `book.edition` exatamente `{}` e
registrar no RCF a decisao finita para estes grupos, sem criar propriedade
formativa adicional.
