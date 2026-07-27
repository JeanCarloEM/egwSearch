# RCF especifico - aquisição pública do EGW Writings

Este RCF subordina-se ao `RCF.md` da raiz e especifica a estrutura, a migração e
a aquisição pública pelo adaptador `src/publications/egw/`. A localização do
adaptador identifica a origem técnica e NÃO restringe o acervo à autora Ellen
G. White; cada publicação DEVE ser persistida sob a chave autoral canônica. [90f05cd]
Divergência DEVE aplicar o RCF da raiz. [90f05cd]

## 1. Identidade e configuracao

`config/publications.json` e a configuracao causal versionada da cadeia. Ela declara raiz-fonte, raiz publica, autores, colecoes, idiomas, tipos e limites de rede; scripts DEVEM resolver seus paths pela raiz do repositorio, nunca pelo diretório corrente. [e59c122]

O autor `egw` representa Ellen G. White. Autores pioneiros DEVEM receber chave [90f05cd]
autoral própria, determinística e persistente; coleção, provedor ou editora NÃO
DEVEM substituir autor. Cada identidade editorial DEVE combinar `remote_id` [90f05cd]
quando disponível, `collection`, `author`, `language`, `type`, título,
edição/versão e origem, sem converter formato em tipo. [e59c122]

As coleções obrigatórias são as coleções públicas observadas `Biblioteca dos [90f05cd]
Pioneiros Adventistas` (`pt/1055`) e `Adventist Pioneer Library` (`en/15`),
além das coleções de Ellen G. White já suportadas. O catálogo real DEVE [90f05cd]
descobrir autores, tipos e obras; enumeração fixa somente PODE ser fixture ou [90f05cd]
fallback incompleto explicitamente marcado.

Somente `pt-BR` e `en` são idiomas elegíveis. `pt`, `pt_BR` e equivalentes
comprovados DEVEM normalizar para `pt-BR`; inglês sem diferença material, [90f05cd]
inclusive `en_US` e `en-GB`, DEVE normalizar para `en`. Valor remoto original [90f05cd]
DEVE ser preservado; diferença material de variante DEVE bloquear fusão. [90f05cd]

Titulo normalizado DEVE preservar Unicode, caixa, diacriticos, pontuacao e trecho parentetico duvidoso; slug de rota e projecao separada e NÃO DEVE substituir nem servir para reconstruir o titulo. Tag ou edicao somente DEVE sair do titulo com evidencia editorial registrada. [c5c4da6]

O acronimo do titulo DEVE derivar apenas de suas palavras normalizadas: titulo de uma palavra usa seu token ASCII normalizado; titulo de varias palavras usa as iniciais alfanumericas, em minusculas. Ausencia de representacao ASCII DEVE usar identificador causal derivado do titulo Unicode. [e59c122]

## 2. Paths e colisoes

A raiz local é `src/publications/`; cada grupo DEVE ocupar [90f05cd]
`<author-key>/<language-path>/<type>/<slug-titulo>/`. Para Ellen G. White,
`author-key` permanece `egw`; autores pioneiros NÃO DEVEM ser gravados sob [90f05cd]
`egw`. `pt-BR` projeta `pt-br` e `en` projeta `en` no path. O legado `en-us`
DEVE ser reconhecido durante transição e NÃO DEVE provocar nova aquisição; [90f05cd]
migração para `en` exige plano atômico e prova de ausência de variante
material. PDF, EPUB, Markdown, derivados e metadado do grupo DEVEM permanecer [90f05cd]
no mesmo diretório. [c5c4da6]

Slug DEVE seguir `[a-z0-9]+(?:-[a-z0-9]+)*`: aplicar minusculas, decomposicao Unicode, transliteracao ASCII deterministica, remocao de acentos, diacriticos e caracteres especiais, substituicao de espacos por hifens, colapso e aparo de hifens; resultado vazio e limite de portabilidade DEVEM usar hash causal. Path e segmento DEVEM permanecer relativos a raiz declarada, sem traversal, path absoluto, controle, nome reservado do Windows ou equivalencia insegura por caixa/normalizacao. [c5c4da6]

Destino ausente DEVE receber o original. Destino existente com SHA-256 identico DEVE eliminar somente a copia redundante depois da validacao transacional. Destino existente com hash diferente DEVE preservar a variante em `<acronimo>.<prefixo-sha256>.<extensao>`; o prefixo DEVE iniciar com oito caracteres e expandir em pares ate desambiguar. [e59c122]

## 3. Metadado local e estado incremental

O downloader DEVE emitir `egw-source/v2`, UTF-8 sem BOM e JSON deterministico. A raiz DEVE conter exatamente `schema_version`, `identity` e `sources`. [e59c122]

`identity` DEVE conter exatamente `author`, `language`, `type`, `title`, `acronym` e `tags`. `tags` DEVE permanecer vazio sem evidencia confirmada. [e59c122]

Cada item de `sources` DEVE conter exatamente `format`, `url`, `accessed_at`, `size` e `hashes`; `hashes` DEVE conter exatamente `sha1`, `sha256` e `sha512`. Registros DEVEM ordenar por formato `pdf`, `epub` e depois URL. [e59c122]

Metadado legado URL-chaveado DEVE permanecer entrada valida da migracao. Sua associacao DEVE exigir compatibilidade de formato, URL e SHA-256 com o arquivo quando esses dados existirem; filename isolado NÃO DEVE bastar para declarar conformidade. [e59c122]

`egw-source/v2` permanece legível para os 527 grupos existentes e NÃO DEVE ser [90f05cd]
reescrito em execução sem mudança material. Aquisição nova ou atualização
material DEVE evoluir para `publication-source/v3`, com raiz fechada [90f05cd]
`schema_version`, `identity`, `collection`, `state`, `sources`, `segments`,
`derivations` e `history`.

`identity` v3 DEVE preservar identificador remoto, autor original e chave [90f05cd]
autoral, título original e normalizado, idiomas original e canônico, tipo
original e canônico, edição/versão, acrônimo, slug, tags e URL pública.
`collection` DEVE preservar identificador, nome, idioma e URL do catálogo. [90f05cd]

`sources` DEVE registrar por ativo ou segmento URL, método [90f05cd]
`native-download`/`text-extraction`, formato, validadores HTTP, coleta
material, tamanho, MIME/assinatura e hashes. `segments` DEVE registrar [90f05cd]
identificador, URL, índice editorial, título, hash e estado de completude.
`derivations` DEVE relacionar fonte, Markdown e EPUB local com gerador, [90f05cd]
versão, transformação e hashes, sem apresentar derivado como original.
`history` DEVE registrar somente mudanças materiais e relação entre versões. [90f05cd]

Ledger operacional, cache, tentativas e resultado `skipped` da execução DEVEM [90f05cd]
residir em estado local segregado e atômico, fora de `formative_data`; eles
NÃO DEVEM alterar metadado versionado ou timestamps do grupo quando nada [90f05cd]
mudou.

Estados permitidos são `pending`, `processing`, `completed`, `skipped`,
`incomplete`, `corrupt`, `unavailable`, `ineligible`, `temporary_failure`,
`permanent_failure` e `review_required`. Somente `completed` com artefatos,
metadado e índice coerentes comprova incorporação.

## 4. Contrato comum

`publication_contract.py` e a unidade comum para normalizacao editorial, slug URI, identidade, paths, formatos, hashes, metadados e colisoes. Downloader, migrador, indexador e validador DEVEM reutiliza-la. [c5c4da6]

O modulo comum DEVE usar somente a biblioteca padrao do Python. A escolha preserva o runtime preexistente, evita dependencia para regras deterministicas e deixa bibliotecas de navegador/rede restritas ao downloader. [e59c122]

Toda leitura de arquivo para hash DEVE ser binaria, sequencial e calcular SHA-1, SHA-256 e SHA-512 na mesma passagem. PDF DEVE exigir assinatura `%PDF-`; EPUB DEVE exigir ZIP OCF com entrada `mimetype` igual a `application/epub+zip`. [e59c122]

## 5. Migrador temporario

`constructor/publications/migrate.py` e ferramenta interna temporaria, fora da fonte publicada. Sua interface canonica e:

- `plan` DEVE inventariar e gerar plano sem mover; [e59c122]
- `apply --plan <arquivo>` DEVE aplicar somente plano integro e ainda correspondente ao estado; [e59c122]
- `rollback --journal <arquivo>` DEVE reverter operacao incompleta ou aplicada ainda nao finalizada; [e59c122]
- `finalize --journal <arquivo>` DEVE remover quarentena somente depois da validacao completa. [e59c122]

`plan` DEVE ser o default e não possuir efeito no acervo. O plano DEVE declarar schema, identidade causal, configuracao, inventario, grupos, acoes e renomeacoes Unicode-para-slug, problemas e resumo; ordem e identidade DEVEM independer de horario, cwd e enumeracao do filesystem. [c5c4da6]

`apply` DEVE verificar path, tamanho e SHA-256 antes de cada acao de renomeacao, persistir sua intencao antes do movimento, confirmar o journal atomico depois e usar quarentena para redundancia. Falha DEVE acionar rollback reverso, inclusive de registro pendente cuja origem ou destino comprove se o movimento ocorreu; journal e quarentena DEVEM preservar retomada. Replace atomico temporariamente bloqueado DEVE admitir somente retry limitado. `finalize` DEVE recusar estado nao concluido. [c5c4da6]

O migrador NÃO DEVE acessar rede nem modificar bytes de PDF/EPUB; diretorio Unicode vazio somente PODE ser removido depois da validacao integral dos arquivos movidos e o rollback DEVE recria-lo quando necessario. Codigo `0` DEVE indicar sucesso; `1`, falha operacional; `2`, uso ou entrada invalida; `3`, conflito ou precondicao; `4`, integridade insegura. [c5c4da6]

## 6. Downloader e descoberta

`baixar.py` NÃO DEVE produzir efeito por importação. A CLI DEVE carregar [90f05cd]
configuração, selecionar coleção, autor ou publicação, descobrir candidatos e
persistir diretamente no diretório canônico. Descoberta, elegibilidade,
preflight, cliente HTTP, download, extração, Markdown, EPUB, metadados, estado
e relatório DEVEM possuir unidades testáveis separadas, sem fragmentação [90f05cd]
artificial. [e59c122]

Catálogo ou API pública estruturada consumida pela própria aplicação DEVE ser [90f05cd]
preferida ao DOM. Parsing renderizado somente PODE ser fallback quando não [90f05cd]
houver contrato direto adequado, e DEVE usar fixture versionada, seletores [90f05cd]
semânticos e falha fechada diante de alteração.

Antes de solicitar catálogo novamente para unidade conhecida ou qualquer
ativo, o preflight DEVE consultar ledger/índice, identidade remota, metadado, [90f05cd]
path, integridade, tamanho, ETag, `Last-Modified` e hash disponível em níveis.
SHA-256 local e request somente DEVEM ocorrer quando o nível anterior não for [90f05cd]
conclusivo.

Item `completed`, íntegro e indexado DEVE resultar em `skipped` sem request do [90f05cd]
ativo, conversão, extração, reprocessamento ou regravação. Nome existente
isolado, temporário ou parcial NÃO DEVE ser aceito. [90f05cd]

Titulo obtido da interface DEVE permanecer candidato editorial integral e NÃO DEVE constituir prova autossuficiente; somente sua projecao de path DEVE aplicar o slug comum, sem remover artigo, parentese, tag, pontuacao ou qualificador do titulo preservado. [c5c4da6]

Somente URL HTTPS de host allowlisted DEVE ser aceita. Cada request DEVE validar URL, DNS/IP publico e redirecionamento; conexao DEVE usar timeout, limite de bytes, streaming, cancelamento por interrupcao e arquivo parcial no destino. [e59c122]

Arquivo parcial somente DEVE ser incorporado depois de resposta completa, formato confirmado e hashes calculados. Incorporacao DEVE usar replace atomico; colisao DEVE aplicar o contrato comum e nunca sobrescrever bytes diferentes. [e59c122]

Metadado DEVE ser atualizado atomicamente depois da incorporação do asset. [90f05cd]
Repetição de identidade/URL/formato/hash DEVE ser idempotente; fonte [90f05cd]
alternativa dos mesmos bytes DEVE permanecer registrável; falha NÃO DEVE [90f05cd]
emitir registro de sucesso. Atualização exige evidência material por hash,
versão/edição, novo ativo, correção remota, metadado relevante ou arquivo
local inválido/ausente. [e59c122]

Dependencias de Selenium, Requests e tqdm DEVEM ser carregadas apenas pela execucao da CLI. Ausencia de dependencia DEVE produzir diagnostico e codigo `3`, sem impedir importacao, teste do contrato ou migracao. [e59c122]

## 7. Cliente HTTP responsável

O cliente DEVE operar sequencialmente por padrão, com concorrência `1`, atraso [90f05cd]
base mínimo de dois segundos e jitter positivo configurável. Concorrência `2`
é o máximo e exige opt-in e evidência; qualquer valor superior DEVE ser [90f05cd]
rejeitado.

Sessão reutilizável, `User-Agent` identificável, timeout, limite de bytes,
streaming, cache, deduplicação, cancelamento, no máximo três tentativas e
backoff exponencial limitado DEVEM ser aplicados. Requisições condicionais [90f05cd]
`If-None-Match` e `If-Modified-Since` DEVEM ser usadas quando houver [90f05cd]
validadores.

`429` DEVE respeitar `Retry-After`; `408` e `5xx` PODEM repetir dentro do [90f05cd]
limite. `403`, CAPTCHA, desafio anti-automação, bloqueio ou contenção
persistente DEVEM parar imediatamente a unidade/coleção, preservar progresso e [90f05cd]
marcar revisão, sem resolver desafio, intensificar, usar proxy, rotacionar
identidade ou ocultar o cliente.

Log DEVE registrar coleção/unidade, taxa, tentativa, espera, status, [90f05cd]
cache/condicional e motivo de parada, sem credencial, token, corpo editorial
desnecessário ou dados privados.

## 8. Conteúdo textual e derivados

Texto on-line somente PODE ser adquirido se PDF e EPUB nativos estiverem [90f05cd]
ausentes e se identidade, ordem, primeira/última unidade e completude forem
determináveis sem contorno.

Extrator DEVE preservar título, subtítulo, autoria, prefácio, introdução, [90f05cd]
capítulos, seções, parágrafos, notas, citações, listas, tabelas textuais,
epígrafes e referências. DEVE excluir navegação, menus, cabeçalhos/rodapés da [90f05cd]
aplicação, breadcrumbs, controles, recomendações, relacionados, anúncios,
telemetria, scripts, estilos, mensagens e duplicações de renderização.

Cada segmento DEVE possuir identificador, URL, ordem e hash. Lacuna, [90f05cd]
duplicação, contagem divergente ou ordem incerta DEVE impedir `completed` e [90f05cd]
produzir `review_required`.

Markdown DEVE usar UTF-8, arquivos numerados pela ordem editorial, nomes com [90f05cd]
slug canônico e metadado próprio. EPUB derivado DEVE ser gerado mecanicamente a [90f05cd]
partir do Markdown já preservado, conter sumário/metadados/idioma/autor/notas,
passar validação técnica e ser marcado `local-conversion`.

O pipeline `fonte estruturada -> Markdown -> EPUB` NÃO DEVE recolher texto já [90f05cd]
completo. Sanitização NÃO DEVE corrigir, resumir, modernizar, traduzir ou [90f05cd]
reescrever conteúdo; Unicode e estrutura semântica DEVEM ser preservados. [90f05cd]

Derivado local NÃO DEVE integrar `formative_data.urls` ou [90f05cd]
`formative_data.global_hashes` como se fosse original. Seu hash, gerador e
proveniência DEVEM residir no envelope global e no metadado v3. [90f05cd]

## 9. Segurança, validação e fronteira

Todo dado remoto DEVE ser não confiável. URL, esquema, host allowlisted, [90f05cd]
DNS/IP, redirecionamento, nome, path, MIME, assinatura, tamanho e arquivo
compactado DEVEM ser validados; traversal, path absoluto, dispositivo, symlink, [90f05cd]
colisão normalizada, execução, macro, script e conteúdo ativo DEVEM ser [90f05cd]
bloqueados.

Testes sem rede DEVEM cobrir normalização editorial, transliteração e slug RFC [90f05cd]
3986, acrônimo, path, assinatura, hashes, colisão, metadado legado/v2/v3,
plano, repetição, apply, rollback, falha de persistência, skip sem request,
parcial, corrupção, atualização, `pt-BR`/`en`, rejeição de idioma, multiautor,
coleções, extração ordenada, exclusão da interface, lacunas, Markdown, EPUB,
original/derivado, `Retry-After`, backoff, limite, contenção, retomada, entrada
hostil e índice. [c5c4da6]

O dry-run integral DEVE contabilizar todo arquivo esperado, rejeitar orfao, slug invalido ou colisao, comparar bytes/hashes e produzir plano reproduzivel antes de qualquer movimento. Depois da aplicacao, DEVE auditar a arvore canônica integralmente em slugs, produzir zero acao residual e repetir inventario identico. [c5c4da6]

Fixture/mock DEVE preceder amostra pública mínima. A amostra DEVE limitar [90f05cd]
coleção, autor/publicação e ativos; desafio ou `403` encerra sem evasão. Coleta
ampliada exige todos os gates e autorização material própria.

A FT-005 não executa download, altera código ou move acervo. Implementação
pertence à FT-006 e exige nova autorização humana explícita após a conclusão
normativa. A decisão editorial pendente da FT-004/03 permanece independente e
intocada.
