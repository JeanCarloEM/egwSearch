# RCF especifico - publicacoes EGW

Este RCF subordina-se ao `RCF.md` da raiz e especifica exclusivamente a estrutura, a migracao e a aquisicao do acervo sob `src/publications/egw/`. Divergencia DEVE aplicar o RCF da raiz. [e59c122]

## 1. Identidade e configuracao

`config/publications.json` e a configuracao causal versionada da cadeia. Ela declara raiz-fonte, raiz publica, autores, colecoes, idiomas, tipos e limites de rede; scripts DEVEM resolver seus paths pela raiz do repositorio, nunca pelo diretório corrente. [e59c122]

O autor `egw` representa Ellen G. White. Cada identidade editorial DEVE usar `author`, `language`, `type` e titulo editorial normalizado, sem converter formato em tipo. [e59c122]

Titulo normalizado DEVE preservar Unicode, caixa, diacriticos, pontuacao e trecho parentetico duvidoso; slug de rota e projecao separada e NÃO DEVE substituir nem servir para reconstruir o titulo. Tag ou edicao somente DEVE sair do titulo com evidencia editorial registrada. [PENDENTE-CODIGO]

O acronimo do titulo DEVE derivar apenas de suas palavras normalizadas: titulo de uma palavra usa seu token ASCII normalizado; titulo de varias palavras usa as iniciais alfanumericas, em minusculas. Ausencia de representacao ASCII DEVE usar identificador causal derivado do titulo Unicode. [e59c122]

## 2. Paths e colisoes

A raiz local e `src/publications/`; cada grupo DEVE ocupar `egw/<language>/<type>/<slug-titulo>/`. PDF, EPUB e metadado local do grupo DEVEM usar o mesmo acronimo, respectivamente `<acronimo>.pdf`, `<acronimo>.epub` e `<acronimo>.source.json`. [PENDENTE-CODIGO]

Slug DEVE seguir `[a-z0-9]+(?:-[a-z0-9]+)*`: aplicar minusculas, decomposicao Unicode, transliteracao ASCII deterministica, remocao de acentos, diacriticos e caracteres especiais, substituicao de espacos por hifens, colapso e aparo de hifens; resultado vazio e limite de portabilidade DEVEM usar hash causal. Path e segmento DEVEM permanecer relativos a raiz declarada, sem traversal, path absoluto, controle, nome reservado do Windows ou equivalencia insegura por caixa/normalizacao. [PENDENTE-CODIGO]

Destino ausente DEVE receber o original. Destino existente com SHA-256 identico DEVE eliminar somente a copia redundante depois da validacao transacional. Destino existente com hash diferente DEVE preservar a variante em `<acronimo>.<prefixo-sha256>.<extensao>`; o prefixo DEVE iniciar com oito caracteres e expandir em pares ate desambiguar. [e59c122]

## 3. Metadado local

O downloader DEVE emitir `egw-source/v2`, UTF-8 sem BOM e JSON deterministico. A raiz DEVE conter exatamente `schema_version`, `identity` e `sources`. [e59c122]

`identity` DEVE conter exatamente `author`, `language`, `type`, `title`, `acronym` e `tags`. `tags` DEVE permanecer vazio sem evidencia confirmada. [e59c122]

Cada item de `sources` DEVE conter exatamente `format`, `url`, `accessed_at`, `size` e `hashes`; `hashes` DEVE conter exatamente `sha1`, `sha256` e `sha512`. Registros DEVEM ordenar por formato `pdf`, `epub` e depois URL. [e59c122]

Metadado legado URL-chaveado DEVE permanecer entrada valida da migracao. Sua associacao DEVE exigir compatibilidade de formato, URL e SHA-256 com o arquivo quando esses dados existirem; filename isolado NÃO DEVE bastar para declarar conformidade. [e59c122]

## 4. Contrato comum

`publication_contract.py` e a unidade comum para normalizacao editorial, slug URI, identidade, paths, formatos, hashes, metadados e colisoes. Downloader, migrador, indexador e validador DEVEM reutiliza-la. [PENDENTE-CODIGO]

O modulo comum DEVE usar somente a biblioteca padrao do Python. A escolha preserva o runtime preexistente, evita dependencia para regras deterministicas e deixa bibliotecas de navegador/rede restritas ao downloader. [e59c122]

Toda leitura de arquivo para hash DEVE ser binaria, sequencial e calcular SHA-1, SHA-256 e SHA-512 na mesma passagem. PDF DEVE exigir assinatura `%PDF-`; EPUB DEVE exigir ZIP OCF com entrada `mimetype` igual a `application/epub+zip`. [e59c122]

## 5. Migrador temporario

`constructor/publications/migrate.py` e ferramenta interna temporaria, fora da fonte publicada. Sua interface canonica e:

- `plan` DEVE inventariar e gerar plano sem mover; [e59c122]
- `apply --plan <arquivo>` DEVE aplicar somente plano integro e ainda correspondente ao estado; [e59c122]
- `rollback --journal <arquivo>` DEVE reverter operacao incompleta ou aplicada ainda nao finalizada; [e59c122]
- `finalize --journal <arquivo>` DEVE remover quarentena somente depois da validacao completa. [e59c122]

`plan` DEVE ser o default e não possuir efeito no acervo. O plano DEVE declarar schema, identidade causal, configuracao, inventario, grupos, acoes e renomeacoes Unicode-para-slug, problemas e resumo; ordem e identidade DEVEM independer de horario, cwd e enumeracao do filesystem. [PENDENTE-CODIGO]

`apply` DEVE verificar path, tamanho e SHA-256 antes de cada acao de renomeacao, persistir sua intencao antes do movimento, confirmar o journal atomico depois e usar quarentena para redundancia. Falha DEVE acionar rollback reverso, inclusive de registro pendente cuja origem ou destino comprove se o movimento ocorreu; journal e quarentena DEVEM preservar retomada. Replace atomico temporariamente bloqueado DEVE admitir somente retry limitado. `finalize` DEVE recusar estado nao concluido. [PENDENTE-CODIGO]

O migrador NÃO DEVE acessar rede nem modificar bytes de PDF/EPUB; diretorio Unicode vazio somente PODE ser removido depois da validacao integral dos arquivos movidos e o rollback DEVE recria-lo quando necessario. Codigo `0` DEVE indicar sucesso; `1`, falha operacional; `2`, uso ou entrada invalida; `3`, conflito ou precondicao; `4`, integridade insegura. [PENDENTE-CODIGO]

## 6. Downloader

`baixar.py` NÃO DEVE produzir efeito por importacao. A CLI DEVE carregar configuracao, selecionar colecoes, descobrir candidatos no catalogo e baixar diretamente no diretorio canônico. [e59c122]

Titulo obtido da interface DEVE permanecer candidato editorial integral e NÃO DEVE constituir prova autossuficiente; somente sua projecao de path DEVE aplicar o slug comum, sem remover artigo, parentese, tag, pontuacao ou qualificador do titulo preservado. [PENDENTE-CODIGO]

Somente URL HTTPS de host allowlisted DEVE ser aceita. Cada request DEVE validar URL, DNS/IP publico e redirecionamento; conexao DEVE usar timeout, limite de bytes, streaming, cancelamento por interrupcao e arquivo parcial no destino. [e59c122]

Arquivo parcial somente DEVE ser incorporado depois de resposta completa, formato confirmado e hashes calculados. Incorporacao DEVE usar replace atomico; colisao DEVE aplicar o contrato comum e nunca sobrescrever bytes diferentes. [e59c122]

Metadado DEVE ser atualizado atomicamente depois da incorporacao do asset. Repeticao de URL/formato/hash DEVE ser idempotente; fonte alternativa dos mesmos bytes DEVE permanecer registravel; falha NÃO DEVE emitir registro de sucesso. [e59c122]

Dependencias de Selenium, Requests e tqdm DEVEM ser carregadas apenas pela execucao da CLI. Ausencia de dependencia DEVE produzir diagnostico e codigo `3`, sem impedir importacao, teste do contrato ou migracao. [e59c122]

## 7. Validacao e fronteira

Testes sem rede DEVEM cobrir normalizacao editorial, transliteracao e slug RFC 3986, acronimo, path, assinatura, hashes, colisao de slug, metadado legado/v2, plano, repeticao, apply, remocao de diretorio vazio, rollback e falha de persistencia entre intencao e confirmacao. [PENDENTE-CODIGO]

O dry-run integral DEVE contabilizar todo arquivo esperado, rejeitar orfao, slug invalido ou colisao, comparar bytes/hashes e produzir plano reproduzivel antes de qualquer movimento. Depois da aplicacao, DEVE auditar a arvore canônica integralmente em slugs, produzir zero acao residual e repetir inventario identico. [PENDENTE-CODIGO]

O subcontexto de contratos não executa download nem move o acervo. Migração, índice/capa/site e publicação permanecem em seus subcontextos materiais próprios da FT-004.
