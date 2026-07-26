# RCF especifico - publicacoes EGW

Este RCF subordina-se ao `RCF.md` da raiz e especifica exclusivamente a estrutura, a migracao e a aquisicao do acervo sob `src/publications/egw/`. Divergencia DEVE aplicar o RCF da raiz. [e59c122]

## 1. Identidade e configuracao

`config/publications.json` e a configuracao causal versionada da cadeia. Ela declara raiz-fonte, raiz publica, autores, colecoes, idiomas, tipos e limites de rede; scripts DEVEM resolver seus paths pela raiz do repositorio, nunca pelo diretório corrente. [e59c122]

O autor `egw` representa Ellen G. White. Cada identidade editorial DEVE usar `author`, `language`, `type` e titulo editorial normalizado, sem converter formato em tipo. [e59c122]

Titulo normalizado DEVE preservar Unicode, caixa, diacriticos, pontuacao e trecho parentetico duvidoso; somente controles, espacos acidentais e caracteres invalidos de path recebem tratamento deterministico. Tag ou edicao somente DEVE sair do titulo com evidencia editorial registrada. [e59c122]

O acronimo do titulo DEVE derivar apenas de suas palavras normalizadas: titulo de uma palavra usa seu token ASCII normalizado; titulo de varias palavras usa as iniciais alfanumericas, em minusculas. Ausencia de representacao ASCII DEVE usar identificador causal derivado do titulo Unicode. [e59c122]

## 2. Paths e colisoes

A raiz local e `src/publications/`; cada grupo DEVE ocupar `egw/<language>/<type>/<titulo>/`. PDF, EPUB e metadado local do grupo DEVEM usar o mesmo acronimo, respectivamente `<acronimo>.pdf`, `<acronimo>.epub` e `<acronimo>.source.json`. [e59c122]

Path e segmento DEVEM permanecer relativos a raiz declarada, sem traversal, path absoluto, controle, nome reservado do Windows ou equivalencia insegura por caixa/normalizacao. [e59c122]

Destino ausente DEVE receber o original. Destino existente com SHA-256 identico DEVE eliminar somente a copia redundante depois da validacao transacional. Destino existente com hash diferente DEVE preservar a variante em `<acronimo>.<prefixo-sha256>.<extensao>`; o prefixo DEVE iniciar com oito caracteres e expandir em pares ate desambiguar. [e59c122]

## 3. Metadado local

O downloader DEVE emitir `egw-source/v2`, UTF-8 sem BOM e JSON deterministico. A raiz DEVE conter exatamente `schema_version`, `identity` e `sources`. [e59c122]

`identity` DEVE conter exatamente `author`, `language`, `type`, `title`, `acronym` e `tags`. `tags` DEVE permanecer vazio sem evidencia confirmada. [e59c122]

Cada item de `sources` DEVE conter exatamente `format`, `url`, `accessed_at`, `size` e `hashes`; `hashes` DEVE conter exatamente `sha1`, `sha256` e `sha512`. Registros DEVEM ordenar por formato `pdf`, `epub` e depois URL. [e59c122]

Metadado legado URL-chaveado DEVE permanecer entrada valida da migracao. Sua associacao DEVE exigir compatibilidade de formato, URL e SHA-256 com o arquivo quando esses dados existirem; filename isolado NÃO DEVE bastar para declarar conformidade. [e59c122]

## 4. Contrato comum

`publication_contract.py` e a unidade comum para normalizacao, identidade, paths, formatos, hashes, metadados e colisoes. Downloader, migrador, indexador e validador DEVEM reutiliza-la. [e59c122]

O modulo comum DEVE usar somente a biblioteca padrao do Python. A escolha preserva o runtime preexistente, evita dependencia para regras deterministicas e deixa bibliotecas de navegador/rede restritas ao downloader. [e59c122]

Toda leitura de arquivo para hash DEVE ser binaria, sequencial e calcular SHA-1, SHA-256 e SHA-512 na mesma passagem. PDF DEVE exigir assinatura `%PDF-`; EPUB DEVE exigir ZIP OCF com entrada `mimetype` igual a `application/epub+zip`. [e59c122]

## 5. Migrador temporario

`constructor/publications/migrate.py` e ferramenta interna temporaria, fora da fonte publicada. Sua interface canonica e:

- `plan` DEVE inventariar e gerar plano sem mover; [e59c122]
- `apply --plan <arquivo>` DEVE aplicar somente plano integro e ainda correspondente ao estado; [e59c122]
- `rollback --journal <arquivo>` DEVE reverter operacao incompleta ou aplicada ainda nao finalizada; [e59c122]
- `finalize --journal <arquivo>` DEVE remover quarentena somente depois da validacao completa. [e59c122]

`plan` DEVE ser o default e não possuir efeito no acervo. O plano DEVE declarar schema, identidade causal, configuracao, inventario, grupos, acoes, problemas e resumo; ordem e identidade DEVEM independer de horario, cwd e enumeracao do filesystem. [e59c122]

`apply` DEVE verificar path, tamanho e SHA-256 antes de cada acao, registrar journal atomico apos cada movimento e usar quarentena para redundancia. Falha DEVE acionar rollback reverso; journal e quarentena DEVEM preservar retomada. `finalize` DEVE recusar estado nao concluido. [e59c122]

O migrador NÃO DEVE acessar rede, modificar bytes de PDF/EPUB ou remover diretorio de origem antes do aceite integral. Codigo `0` DEVE indicar sucesso; `1`, falha operacional; `2`, uso ou entrada invalida; `3`, conflito ou precondicao; `4`, integridade insegura. [e59c122]

## 6. Downloader

`baixar.py` NÃO DEVE produzir efeito por importacao. A CLI DEVE carregar configuracao, selecionar colecoes, descobrir candidatos no catalogo e baixar diretamente no diretorio canônico. [e59c122]

Titulo obtido da interface DEVE ser candidato de path e NÃO DEVE constituir prova editorial autossuficiente. O downloader NÃO DEVE remover artigo, parentese, tag, pontuacao ou qualificador sem evidencia. [e59c122]

Somente URL HTTPS de host allowlisted DEVE ser aceita. Cada request DEVE validar URL, DNS/IP publico e redirecionamento; conexao DEVE usar timeout, limite de bytes, streaming, cancelamento por interrupcao e arquivo parcial no destino. [e59c122]

Arquivo parcial somente DEVE ser incorporado depois de resposta completa, formato confirmado e hashes calculados. Incorporacao DEVE usar replace atomico; colisao DEVE aplicar o contrato comum e nunca sobrescrever bytes diferentes. [e59c122]

Metadado DEVE ser atualizado atomicamente depois da incorporacao do asset. Repeticao de URL/formato/hash DEVE ser idempotente; fonte alternativa dos mesmos bytes DEVE permanecer registravel; falha NÃO DEVE emitir registro de sucesso. [e59c122]

Dependencias de Selenium, Requests e tqdm DEVEM ser carregadas apenas pela execucao da CLI. Ausencia de dependencia DEVE produzir diagnostico e codigo `3`, sem impedir importacao, teste do contrato ou migracao. [e59c122]

## 7. Validacao e fronteira

Testes sem rede DEVEM cobrir normalizacao, acronimo, path, assinatura, hashes, colisao, metadado legado/v2, plano, repeticao, apply e rollback. [e59c122]

O dry-run integral DEVE contabilizar todo arquivo legado esperado, rejeitar orfao ou conflito, comparar bytes/hashes e produzir plano reproduzivel antes de qualquer movimento. [e59c122]

Este subcontexto nao executa download, nao move o acervo, nao gera indice/capa/site e nao publica. Essas operacoes permanecem nos subcontextos posteriores da FT-004.
