# RCF especifico - publicacoes EGW

Este RCF subordina-se ao `RCF.md` da raiz e especifica exclusivamente a estrutura, a migracao e a aquisicao do acervo sob `src/publications/egw/`. Divergencia aplica o RCF da raiz.

## 1. Identidade e configuracao

`config/publications.json` e a configuracao causal versionada da cadeia. Ela declara raiz-fonte, raiz publica, autores, colecoes, idiomas, tipos e limites de rede; scripts resolvem seus paths pela raiz do repositorio, nunca pelo diretório corrente.

O autor `egw` representa Ellen G. White. Cada identidade editorial usa `author`, `language`, `type` e titulo editorial normalizado, sem converter formato em tipo.

Titulo normalizado preserva Unicode, caixa, diacriticos, pontuacao e trecho parentetico duvidoso; somente controles, espacos acidentais e caracteres invalidos de path recebem tratamento deterministico. Tag ou edicao somente sai do titulo com evidencia editorial registrada.

O acronimo do titulo deriva apenas de suas palavras normalizadas: titulo de uma palavra usa seu token ASCII normalizado; titulo de varias palavras usa as iniciais alfanumericas, em minusculas. Ausencia de representacao ASCII usa identificador causal derivado do titulo Unicode.

## 2. Paths e colisoes

A raiz local e `src/publications/`; cada grupo ocupa `egw/<language>/<type>/<titulo>/`. PDF, EPUB e metadado local do grupo usam o mesmo acronimo, respectivamente `<acronimo>.pdf`, `<acronimo>.epub` e `<acronimo>.source.json`.

Path e segmento devem permanecer relativos a raiz declarada, sem traversal, path absoluto, controle, nome reservado do Windows ou equivalencia insegura por caixa/normalizacao.

Destino ausente recebe o original. Destino existente com SHA-256 identico elimina somente a copia redundante depois da validacao transacional. Destino existente com hash diferente preserva a variante em `<acronimo>.<prefixo-sha256>.<extensao>`; o prefixo inicia com oito caracteres e expande em pares ate desambiguar.

## 3. Metadado local

O downloader emite `egw-source/v2`, UTF-8 sem BOM e JSON deterministico. A raiz contem exatamente `schema_version`, `identity` e `sources`.

`identity` contem exatamente `author`, `language`, `type`, `title`, `acronym` e `tags`. `tags` permanece vazio sem evidencia confirmada.

Cada item de `sources` contem exatamente `format`, `url`, `accessed_at`, `size` e `hashes`; `hashes` contem exatamente `sha1`, `sha256` e `sha512`. Registros ordenam por formato `pdf`, `epub` e depois URL.

Metadado legado URL-chaveado permanece entrada valida da migracao. Sua associacao exige compatibilidade de formato, URL e SHA-256 com o arquivo quando esses dados existirem; filename isolado nao basta para declarar conformidade.

## 4. Contrato comum

`publication_contract.py` e a unidade comum para normalizacao, identidade, paths, formatos, hashes, metadados e colisoes. Downloader, migrador, indexador e validador devem reutiliza-la.

O modulo comum usa somente a biblioteca padrao do Python. A escolha preserva o runtime preexistente, evita dependencia para regras deterministicas e deixa bibliotecas de navegador/rede restritas ao downloader.

Toda leitura de arquivo para hash e binaria, sequencial e calcula SHA-1, SHA-256 e SHA-512 na mesma passagem. PDF exige assinatura `%PDF-`; EPUB exige ZIP OCF com entrada `mimetype` igual a `application/epub+zip`.

## 5. Migrador temporario

`constructor/publications/migrate.py` e ferramenta interna temporaria, fora da fonte publicada. Sua interface canonica e:

- `plan`: inventaria e gera plano sem mover;
- `apply --plan <arquivo>`: aplica somente plano integro e ainda correspondente ao estado;
- `rollback --journal <arquivo>`: reverte operacao incompleta ou aplicada ainda nao finalizada;
- `finalize --journal <arquivo>`: remove quarentena somente depois da validacao completa.

`plan` e o default e nao possui efeito no acervo. O plano declara schema, identidade causal, configuracao, inventario, grupos, acoes, problemas e resumo; ordem e identidade independem de horario, cwd e enumeracao do filesystem.

`apply` verifica path, tamanho e SHA-256 antes de cada acao, registra journal atomico apos cada movimento e usa quarentena para redundancia. Falha aciona rollback reverso; journal e quarentena preservam retomada. `finalize` recusa estado nao concluido.

O migrador nao acessa rede, nao modifica bytes de PDF/EPUB e nao remove diretorio de origem antes do aceite integral. Codigo `0` indica sucesso; `1`, falha operacional; `2`, uso ou entrada invalida; `3`, conflito ou precondicao; `4`, integridade insegura.

## 6. Downloader

`baixar.py` nao produz efeito por importacao. A CLI carrega configuracao, seleciona colecoes, descobre candidatos no catalogo e baixa diretamente no diretorio canônico.

Titulo obtido da interface e candidato de path e nao prova editorial autossuficiente. O downloader nao remove artigo, parentese, tag, pontuacao ou qualificador sem evidencia.

Somente URL HTTPS de host allowlisted e aceita. Cada request valida URL, DNS/IP publico e redirecionamento; conexao usa timeout, limite de bytes, streaming, cancelamento por interrupcao e arquivo parcial no destino.

Arquivo parcial somente e incorporado depois de resposta completa, formato confirmado e hashes calculados. Incorporacao usa replace atomico; colisao aplica o contrato comum e nunca sobrescreve bytes diferentes.

Metadado e atualizado atomicamente depois da incorporacao do asset. Repeticao de URL/formato/hash e idempotente; fonte alternativa dos mesmos bytes permanece registravel; falha nao emite registro de sucesso.

Dependencias de Selenium, Requests e tqdm sao carregadas apenas pela execucao da CLI. Ausencia de dependencia produz diagnostico e codigo `3`, sem impedir importacao, teste do contrato ou migracao.

## 7. Validacao e fronteira

Testes sem rede cobrem normalizacao, acronimo, path, assinatura, hashes, colisao, metadado legado/v2, plano, repeticao, apply e rollback.

O dry-run integral deve contabilizar todo arquivo legado esperado, rejeitar orfao ou conflito, comparar bytes/hashes e produzir plano reproduzivel antes de qualquer movimento.

Este subcontexto nao executa download, nao move o acervo, nao gera indice/capa/site e nao publica. Essas operacoes permanecem nos subcontextos posteriores da FT-004.
