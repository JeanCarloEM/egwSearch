# RCF específico - aquisição pública de publicações

Este RCF subordina-se ao `RCF.md` da raiz e especifica a estrutura, a migração e
a aquisição pública pela automação em `scripts/publications/`. O namespace é
neutro quanto a autor: o portal de origem inclui Ellen G. White e autores
pioneiros distintos; cada publicação DEVE ser persistida sob a chave autoral canônica. [3301a97]
Divergência DEVE aplicar o RCF da raiz. [3301a97]

O downloader, o cliente de aquisição, o contrato Python comum e seus requisitos DEVEM residir em `scripts/publications/`, fora de `src/` e do artefato público. [3301a97]

## 1. Identidade e configuracao

`config/publications.json` e a configuracao causal versionada da cadeia. Ela declara raiz-fonte, raiz publica, autores, colecoes, idiomas, tipos e limites de rede; scripts DEVEM resolver seus paths pela raiz do repositorio, nunca pelo diretório corrente. [3301a97]

O autor `egw` representa Ellen G. White. Autores pioneiros DEVEM receber chave [3301a97]
autoral própria, determinística e persistente; coleção, provedor ou editora NÃO
DEVEM substituir autor. Cada identidade editorial DEVE combinar `remote_id` [3301a97]
quando disponível, `collection`, `author`, `language`, `type`, título,
edição/versão e origem, sem converter formato em tipo. [e59c122]

As coleções obrigatórias são as coleções públicas observadas `Biblioteca dos [3301a97]
Pioneiros Adventistas` (`pt/1055`) e `Adventist Pioneer Library` (`en/15`),
além das coleções de Ellen G. White já suportadas. O catálogo real DEVE [3301a97]
descobrir autores, tipos e obras; enumeração fixa somente PODE ser fixture ou [3301a97]
fallback incompleto explicitamente marcado.

Somente `pt-BR` e `en` são idiomas elegíveis. `pt`, `pt_BR` e equivalentes
comprovados DEVEM normalizar para `pt-BR`; inglês sem diferença material, [3301a97]
inclusive `en_US` e `en-GB`, DEVE normalizar para `en`. Valor remoto original [3301a97]
DEVE ser preservado; diferença material de variante DEVE bloquear fusão. [3301a97]

Titulo normalizado DEVE preservar Unicode, caixa, diacriticos, pontuacao e trecho parentetico duvidoso; slug de rota e projecao separada e NÃO DEVE substituir nem servir para reconstruir o titulo. Tag ou edicao somente DEVE sair do titulo com evidencia editorial registrada. [3301a97]

O acronimo do titulo DEVE derivar apenas de suas palavras normalizadas: titulo de uma palavra usa seu token ASCII normalizado; titulo de varias palavras usa as iniciais alfanumericas, em minusculas. Ausencia de representacao ASCII DEVE usar identificador causal derivado do titulo Unicode. [3301a97]

## 2. Paths e colisoes

A raiz local é `src/publications/`; cada grupo DEVE ocupar [3301a97]
`<author-key>/<language-path>/<type>/<slug-titulo>/`. Para Ellen G. White,
`author-key` permanece `egw`; autores pioneiros NÃO DEVEM ser gravados sob [3301a97]
`egw`. `pt-BR` projeta `pt-br` e `en` projeta `en` no path. O legado `en-us`
DEVE ser reconhecido durante transição e NÃO DEVE provocar nova aquisição; [3301a97]
migração para `en` exige plano atômico e prova de ausência de variante
material. PDF, EPUB, Markdown, derivados e metadado do grupo DEVEM permanecer [3301a97]
no mesmo diretório. [c5c4da6]

Slug DEVE seguir `[a-z0-9]+(?:-[a-z0-9]+)*`: aplicar minusculas, decomposicao Unicode, transliteracao ASCII deterministica, remocao de acentos, diacriticos e caracteres especiais, substituicao de espacos por hifens, colapso e aparo de hifens; resultado vazio e limite de portabilidade DEVEM usar hash causal. Path e segmento DEVEM permanecer relativos a raiz declarada, sem traversal, path absoluto, controle, nome reservado do Windows ou equivalencia insegura por caixa/normalizacao. [3301a97]

Destino ausente DEVE receber o original. Destino existente com SHA-256 identico DEVE eliminar somente a copia redundante depois da validacao transacional. Destino existente com hash diferente DEVE preservar a variante em `<acronimo>.<prefixo-sha256>.<extensao>`; o prefixo DEVE iniciar com oito caracteres e expandir em pares ate desambiguar. [3301a97]

## 3. Metadado local e estado incremental

O downloader DEVE emitir `egw-source/v2`, UTF-8 sem BOM e JSON deterministico. A raiz DEVE conter exatamente `schema_version`, `identity` e `sources`. [3301a97]

`identity` DEVE conter exatamente `author`, `language`, `type`, `title`, `acronym` e `tags`. `tags` DEVE permanecer vazio sem evidencia confirmada. [3301a97]

Cada item de `sources` DEVE conter exatamente `format`, `url`, `accessed_at`, `size` e `hashes`; `hashes` DEVE conter exatamente `sha1`, `sha256` e `sha512`. Registros DEVEM ordenar por formato `pdf`, `epub` e depois URL. [3301a97]

Metadado legado URL-chaveado DEVE permanecer entrada valida da migracao. Sua associacao DEVE exigir compatibilidade de formato, URL e SHA-256 com o arquivo quando esses dados existirem; filename isolado NÃO DEVE bastar para declarar conformidade. [3301a97]

`egw-source/v2` permanece legível para os 527 grupos existentes e NÃO DEVE ser [3301a97]
reescrito em execução sem mudança material. Aquisição nova ou atualização
material DEVE evoluir para `publication-source/v3`, com raiz fechada [3301a97]
`schema_version`, `identity`, `collection`, `state`, `sources`, `segments`,
`derivations` e `history`.

`identity` v3 DEVE preservar identificador remoto, autor original e chave [3301a97]
autoral, título original e normalizado, idiomas original e canônico, tipo
original e canônico, edição/versão, acrônimo, slug, tags e URL pública.
`collection` DEVE preservar identificador, nome, idioma e URL do catálogo. [3301a97]

`sources` DEVE registrar por ativo ou segmento URL, método [3301a97]
`native-download`/`text-extraction`, formato, validadores HTTP, coleta
material, tamanho, MIME/assinatura e hashes. `segments` DEVE registrar [3301a97]
identificador, URL, índice editorial, título, hash e estado de completude.
`derivations` DEVE relacionar fonte, Markdown e EPUB local com gerador, [3301a97]
versão, transformação e hashes, sem apresentar derivado como original.
`history` DEVE registrar somente mudanças materiais e relação entre versões. [3301a97]

Ledger operacional, cache, tentativas e resultado `skipped` da execução DEVEM [3301a97]
residir em estado local segregado e atômico, fora de `formative_data`; eles
NÃO DEVEM alterar metadado versionado ou timestamps do grupo quando nada [3301a97]
mudou.

Estados permitidos são `pending`, `processing`, `completed`, `skipped`,
`incomplete`, `corrupt`, `unavailable`, `ineligible`, `temporary_failure`,
`permanent_failure` e `review_required`. Somente `completed` com artefatos,
metadado e índice coerentes comprova incorporação.

## 4. Contrato comum

`publication_contract.py` e a unidade comum para normalizacao editorial, slug URI, identidade, paths, formatos, hashes, metadados e colisoes. Downloader, migrador, indexador e validador DEVEM reutiliza-la. [3301a97]

O modulo comum DEVE usar somente a biblioteca padrao do Python. A escolha preserva o runtime preexistente, evita dependencia para regras deterministicas e deixa bibliotecas de navegador/rede restritas ao downloader. [3301a97]

Toda leitura de arquivo para hash DEVE ser binaria, sequencial e calcular SHA-1, SHA-256 e SHA-512 na mesma passagem. PDF DEVE exigir assinatura `%PDF-`; EPUB DEVE exigir ZIP OCF com entrada `mimetype` igual a `application/epub+zip`. [3301a97]

## 5. Migrador temporario

`constructor/publications/migrate.py` e ferramenta interna temporaria, fora da fonte publicada. Sua interface canonica e:

- `plan` DEVE inventariar e gerar plano sem mover; [3301a97]
- `apply --plan <arquivo>` DEVE aplicar somente plano integro e ainda correspondente ao estado; [3301a97]
- `rollback --journal <arquivo>` DEVE reverter operacao incompleta ou aplicada ainda nao finalizada; [3301a97]
- `finalize --journal <arquivo>` DEVE remover quarentena somente depois da validacao completa. [3301a97]

`plan` DEVE ser o default e não possuir efeito no acervo. O plano DEVE declarar schema, identidade causal, configuracao, inventario, grupos, acoes e renomeacoes Unicode-para-slug, problemas e resumo; ordem e identidade DEVEM independer de horario, cwd e enumeracao do filesystem. [3301a97]

`apply` DEVE verificar path, tamanho e SHA-256 antes de cada acao de renomeacao, persistir sua intencao antes do movimento, confirmar o journal atomico depois e usar quarentena para redundancia. Falha DEVE acionar rollback reverso, inclusive de registro pendente cuja origem ou destino comprove se o movimento ocorreu; journal e quarentena DEVEM preservar retomada. Replace atomico temporariamente bloqueado DEVE admitir somente retry limitado. `finalize` DEVE recusar estado nao concluido. [3301a97]

O migrador NÃO DEVE acessar rede nem modificar bytes de PDF/EPUB; diretorio Unicode vazio somente PODE ser removido depois da validacao integral dos arquivos movidos e o rollback DEVE recria-lo quando necessario. Codigo `0` DEVE indicar sucesso; `1`, falha operacional; `2`, uso ou entrada invalida; `3`, conflito ou precondicao; `4`, integridade insegura. [3301a97]

## 6. Downloader e descoberta

`baixar.py` NÃO DEVE produzir efeito por importação. A CLI DEVE carregar [3301a97]
configuração, selecionar coleção, autor ou publicação, descobrir candidatos e
persistir diretamente no diretório canônico. Descoberta, elegibilidade,
preflight, cliente HTTP, download, extração, Markdown, EPUB, metadados, estado
e relatório DEVEM possuir unidades testáveis separadas, sem fragmentação [3301a97]
artificial. [e59c122]

Catálogo ou API pública estruturada consumida pela própria aplicação DEVE ser [3301a97]
preferida ao DOM. Parsing renderizado somente PODE ser fallback quando não [3301a97]
houver contrato direto adequado, e DEVE usar fixture versionada, seletores [3301a97]
semânticos e falha fechada diante de alteração.

Quando o portal oferecer uma interface pública leve com o mesmo conteúdo
editorial, ela DEVE ser preferida à aplicação completa se reduzir desafio, [be82602]
virtualização e dependência de JavaScript sem reduzir cobertura. [PENDENTE-CODIGO]
A enumeração DEVE coletar incrementalmente todos os `href` únicos de obra; [be82602]
rolar e analisar somente o DOM final é insuficiente para grade virtualizada. [PENDENTE-CODIGO]

O cartão do catálogo fornece somente identidade preliminar. A página individual
da obra DEVE ser consultada antes da aquisição e é a autoridade para autor, [be82602]
título, código, URL inicial de leitura e todos os links PDF/EPUB habilitados. [PENDENTE-CODIGO]
Cada ativo habilitado é obrigatório; `disabled`, URL vazia ou `#` significa [be82602]
indisponível e não falha de download.

Antes de solicitar catálogo novamente para unidade conhecida ou qualquer
ativo, o preflight DEVE consultar ledger/índice, identidade remota, metadado, [3301a97]
path, integridade, tamanho, ETag, `Last-Modified` e hash disponível em níveis.
SHA-256 local e request somente DEVEM ocorrer quando o nível anterior não for [3301a97]
conclusivo.

Item `completed`, íntegro e indexado DEVE resultar em `skipped` sem request do [3301a97]
ativo, conversão, extração, reprocessamento ou regravação. Nome existente
isolado, temporário ou parcial NÃO DEVE ser aceito. [3301a97]

Titulo obtido da interface DEVE permanecer candidato editorial integral e NÃO DEVE constituir prova autossuficiente; somente sua projecao de path DEVE aplicar o slug comum, sem remover artigo, parentese, tag, pontuacao ou qualificador do titulo preservado. [3301a97]

Somente URL HTTPS de host allowlisted DEVE ser aceita. Cada request DEVE validar URL, DNS/IP publico e redirecionamento; conexao DEVE usar timeout, limite de bytes, streaming, cancelamento por interrupcao e arquivo parcial no destino. [3301a97]

Arquivo parcial somente DEVE ser incorporado depois de resposta completa, formato confirmado e hashes calculados. Incorporacao DEVE usar replace atomico; colisao DEVE aplicar o contrato comum e nunca sobrescrever bytes diferentes. [3301a97]

Metadado DEVE ser atualizado atomicamente depois da incorporação do asset. [3301a97]
Repetição de identidade/URL/formato/hash DEVE ser idempotente; fonte [3301a97]
alternativa dos mesmos bytes DEVE permanecer registrável; falha NÃO DEVE [3301a97]
emitir registro de sucesso. Atualização exige evidência material por hash,
versão/edição, novo ativo, correção remota, metadado relevante ou arquivo
local inválido/ausente. [e59c122]

Dependencias de Selenium, Requests e tqdm DEVEM ser carregadas apenas pela execucao da CLI. Ausencia de dependencia DEVE produzir diagnostico e codigo `3`, sem impedir importacao, teste do contrato ou migracao. [3301a97]

Os requisitos fixados em `requirements.txt` DEVEM ser preparados pelo bootstrap multi-runtime do repositório em ambiente Python local segregado, antes da execução suportada da CLI. [d9e37be]

O bootstrap DEVE ser idempotente, não executar a CLI, não iniciar navegador e não realizar coleta; ausência ou incompatibilidade do interpretador/instalador DEVE produzir diagnóstico acionável. [d9e37be]

## 7. Cliente HTTP responsável

O cliente DEVE operar sequencialmente por padrão, com concorrência `1`, atraso [3301a97]
base mínimo de dois segundos e jitter positivo configurável. Concorrência `2`
é o máximo e exige opt-in e evidência; qualquer valor superior DEVE ser [3301a97]
rejeitado.

Sessão reutilizável, `User-Agent` identificável, timeout, limite de bytes,
streaming, cache, deduplicação, cancelamento, no máximo três tentativas e
backoff exponencial limitado DEVEM ser aplicados. Requisições condicionais [3301a97]
`If-None-Match` e `If-Modified-Since` DEVEM ser usadas quando houver [3301a97]
validadores.

`429` DEVE respeitar `Retry-After`; `408` e `5xx` PODEM repetir dentro do [3301a97]
limite. [3301a97] Descoberta que dependa de navegador DEVE usar uma única instância [77eac45]
visível, perfil persistente local segregado e uma única guia operacional [PENDENTE-CODIGO]
reutilizada em todas as coleções processadas pela execução; concorrência com [PENDENTE-CODIGO]
navegador DEVE ser `1`, e nova guia/sessão somente PODE ocorrer por fechamento, [77eac45]
invalidação, corrupção ou recuperação controlada, com log do motivo. [PENDENTE-CODIGO]

CAPTCHA, challenge page, verificação de navegador, bloqueio temporário, [PENDENTE-CODIGO]
redirecionamento de validação, `403`, `429`, título/URL/DOM inesperado ou [PENDENTE-CODIGO]
ausência de grade do catálogo DEVEM ser avaliados por múltiplos sinais. Quando [77eac45]
houver verificação humana legitimamente interativa, a automação DEVE manter a [77eac45]
guia aberta, pausar somente o fluxo dependente, reduzir requisições ao mínimo, [PENDENTE-CODIGO]
emitir mensagem objetiva ao usuário, aguardar com intervalo configurável de [PENDENTE-CODIGO]
baixa frequência e retomar automaticamente após a grade ou conteúdo esperado [PENDENTE-CODIGO]
voltar. [PENDENTE-CODIGO]

`403`, CAPTCHA, desafio anti-automação, bloqueio ou contenção persistente que [PENDENTE-CODIGO]
não puderem ser liberados pela guia visível DEVEM parar a unidade/coleção, [77eac45]
preservar progresso e marcar revisão, sem resolver desafio, intensificar, usar [PENDENTE-CODIGO]
proxy, rotacionar identidade, simular comportamento humano ou ocultar o cliente. [PENDENTE-CODIGO]

Log DEVE registrar coleção/unidade, taxa, tentativa, espera, status, [3301a97]
cache/condicional e motivo de parada, sem credencial, token, corpo editorial
desnecessário ou dados privados.

Configuração do downloader DEVE declarar visibilidade do navegador, diretório [77eac45]
do perfil persistente, intervalo de verificação, limite opcional de espera [PENDENTE-CODIGO]
humana, tempo de espera da grade, limite de recuperação e tamanho da janela. [PENDENTE-CODIGO]
Padrões DEVEM privilegiar navegador visível, perfil fora de commits, espera sem [77eac45]
timeout curto, baixo consumo e recuperação finita. [PENDENTE-CODIGO]

### 7.1 Estado local central

`config/publications.json` DEVE declarar uma única `runtime_state_root`; ambiente [d9e37be]
Python, ledger, cache, perfil, sessão, temporários, locks, traces e logs DEVEM [d9e37be]
derivar dela por funções centrais, nunca por paths hardcoded dispersos. [PENDENTE-CODIGO]
A raiz
DEVE ser criada sob demanda, ignorada integralmente e excluída de build, Pages, [d9e37be]
pacote e release. [PENDENTE-CODIGO]

O estado local DEVE ser classificado em persistente, temporário ou sensível e [d9e37be]
possuir isolamento, retenção, limite, invalidação e limpeza próprios. [PENDENTE-CODIGO]
Perfil e
sessão DEVEM ser isolados por provedor/domínio e finalidade; parcial DEVE ficar [d9e37be]
em subdiretório de runtime até promoção atômica. [PENDENTE-CODIGO]
PDF, EPUB, Markdown, metadado e
índice validados permanecem canônicos e não podem ser ignorados como runtime. [d9e37be]
[PENDENTE-CODIGO]

Migração do perfil legado PODE mover somente árvore local comprovada, com [d9e37be]
origem/destino validados, ausência de processo ativo, operação idempotente e
fallback removido após sucesso. [PENDENTE-CODIGO]
Clone sem a raiz DEVE recriá-la sem perda [d9e37be]
funcional; corrupção de cache/perfil DEVE causar reset controlado ou diagnóstico, [d9e37be]
nunca sucesso falso. [PENDENTE-CODIGO]

### 7.2 Handoff humano desacoplado

O estado do navegador DEVE seguir `automatizado`, [d9e37be]
`aguardando_intervencao_humana`, `validando_retomada`, `retomado`, `cancelado`
ou `bloqueado`. [PENDENTE-CODIGO]
Transição para intervenção DEVE encerrar o WebDriver e todos os [d9e37be]
efeitos automáticos antes de abrir ou orientar o uso de navegador normal no
perfil autorizado. [PENDENTE-CODIGO]
Automação e humano não podem atuar simultaneamente. [d9e37be]
[PENDENTE-CODIGO]

O handoff DEVE usar processo normal sem flags de WebDriver e aguardar seu [d9e37be]
encerramento ou cancelamento sem inspecionar/interagir com o DOM. [PENDENTE-CODIGO]
Reinício do
controlador no mesmo perfil somente PODE ocorrer depois do encerramento humano; [d9e37be]
a retomada exige catálogo esperado, origem correta e ausência de desafio. [PENDENTE-CODIGO]
Perfil
incompatível, bloqueio persistente, expiração ou reapresentação encerra a
coleção como revisão, sem bypass ou retry ilimitado. [PENDENTE-CODIGO]

CLI DEVE permitir cancelar a espera, limitar seu tempo quando configurado, [d9e37be]
selecionar binário normal explicitamente e desabilitar handoff. [PENDENTE-CODIGO]
Log DEVE usar [d9e37be]
eventos sanitizados e nunca registrar cookie, token, storage ou resposta do
desafio. [PENDENTE-CODIGO]

### 7.3 Publicação completa e efeito Git

O coletor DEVE centralizar uma função que calcule e valide a unidade [5cacaf1]
`completa_e_pareada`: ativos, metadado, segmentos, derivados, referências e
entradas de índice impactadas. [PENDENTE-CODIGO]
O resultado DEVE expor allowlist relativa à raiz, [5cacaf1]
hashes e evidência de completude; item ambíguo ou incompleto não é elegível a
Git. [PENDENTE-CODIGO]

Commit automático DEVE ser desabilitado por padrão e exigir opção explícita da [5cacaf1]
CLI. [PENDENTE-CODIGO]
Quando habilitado, a finalização DEVE adquirir lock global no runtime, [5cacaf1]
validar `dev`, worktree/índice, excluir estado não canônico, adicionar somente a
allowlist com `git add -- <paths>`, validar o diff staged e criar exatamente um
commit por publicação. [PENDENTE-CODIGO]
Alteração staged preexistente ou conflito em path da
unidade bloqueia sem modificar o índice. [PENDENTE-CODIGO]

Falha entre promoção e commit DEVE restaurar índice/metadata da transação ou [5cacaf1]
preservar preparação no runtime para retomada. [PENDENTE-CODIGO]
Commit confirmado DEVE ser [5cacaf1]
registrado no ledger e não pode ser repetido. [5cacaf1]
Push, se futuramente habilitado,
é fase separada e nunca requisito implícito do download. [PENDENTE-CODIGO]

## 8. Conteúdo textual e derivados

Texto on-line somente PODE ser adquirido se PDF e EPUB nativos estiverem [3301a97]
ausentes e se identidade, ordem, primeira/última unidade e completude forem
determináveis sem contorno.

A extração DEVE iniciar na URL `Read Online` da página individual e seguir [be82602]
somente links editoriais `rel=next` da mesma obra até ausência ou marca de
término. [PENDENTE-CODIGO]
Cada transição DEVE validar URL, identificador da obra, ausência de [be82602]
ciclo, coerência do `rel=prev` quando aplicável e presença do contêiner
editorial `#r-pl` ou contrato público equivalente. [PENDENTE-CODIGO]

Extrator DEVE preservar título, subtítulo, autoria, prefácio, introdução, [3301a97]
capítulos, seções, parágrafos, notas, citações, listas, tabelas textuais,
epígrafes e referências. DEVE excluir navegação, menus, cabeçalhos/rodapés da [3301a97]
aplicação, breadcrumbs, controles, recomendações, relacionados, anúncios,
telemetria, scripts, estilos, mensagens e duplicações de renderização.

Cada segmento DEVE possuir identificador, URL, ordem e hash. Lacuna, [3301a97]
duplicação, contagem divergente ou ordem incerta DEVE impedir `completed` e [3301a97]
produzir `review_required`.

Markdown DEVE usar UTF-8, arquivos numerados pela ordem editorial, nomes com [3301a97]
slug canônico e metadado próprio. EPUB derivado DEVE ser gerado mecanicamente a [3301a97]
partir do Markdown já preservado, conter sumário/metadados/idioma/autor/notas,
passar validação técnica e ser marcado `local-conversion`.

O pipeline `fonte estruturada -> Markdown -> EPUB` NÃO DEVE recolher texto já [3301a97]
completo. Sanitização NÃO DEVE corrigir, resumir, modernizar, traduzir ou [3301a97]
reescrever conteúdo; Unicode e estrutura semântica DEVEM ser preservados. [3301a97]

No contêiner editorial, elementos `h1` a `h6`, parágrafos, listas, tabelas,
blockquote, imagens editoriais, notas, ênfase, links e quebras materiais DEVEM [be82602]
ser preservados em ordem. [PENDENTE-CODIGO]
Marcadores de referência e controles da aplicação DEVEM ser separados do texto, [be82602]
mas seu identificador editorial DEVE permanecer no metadado do bloco. [be82602]
Texto vazio, placeholder, fixture ou corpo sem blocos
editoriais válidos DEVE impedir derivação. [be82602]

Fixture executada pela CLI DEVE exigir `--output-root` explícito fora da raiz [be82602]
canônica ou usar automaticamente subdiretório temporário da raiz de runtime; [PENDENTE-CODIGO]
ela nunca PODE gravar em `src/publications`. [be82602]

Derivado local NÃO DEVE integrar `formative_data.urls` ou [3301a97]
`formative_data.global_hashes` como se fosse original. Seu hash, gerador e
proveniência DEVEM residir no envelope global e no metadado v3. [3301a97]

Quando a ficha pública da obra textual declarar capa por `og:image`, relação equivalente ou endpoint oficial do mesmo identificador remoto, essa URL DEVE ser preservada e adquirida de host allowlisted como fonte obrigatória. [PENDENTE-CODIGO]
A imagem DEVE ser limitada, decodificada e normalizada deterministicamente para `cover.png`, com no máximo 800 px por eixo, proporção preservada, sem ampliação e sem metadados dispensáveis; escrita e promoção DEVEM ser atômicas. [PENDENTE-CODIGO]
O EPUB derivado DEVE incluir a imagem no manifesto com propriedade `cover-image`, página de capa no início do spine e bytes iguais ao `cover.png`; um gerador PDF futuro DEVE usar o mesmo arquivo como capa antes do texto, sem autorizar PDF rasterizado como falso equivalente editorial. [PENDENTE-CODIGO]
Metadado v3 DEVE registrar separadamente a fonte remota e o derivado normalizado, com URL, método, path, tamanho e hashes verificáveis. [PENDENTE-CODIGO]
Reexecução sem mudança DEVE validar e reutilizar capa e EPUB; `--revalidate` DEVE readquirir ou revalidar a capa antes de concluir. [PENDENTE-CODIGO]

## 9. Segurança, validação e fronteira

Todo dado remoto DEVE ser não confiável. URL, esquema, host allowlisted, [3301a97]
DNS/IP, redirecionamento, nome, path, MIME, assinatura, tamanho e arquivo
compactado DEVEM ser validados; traversal, path absoluto, dispositivo, symlink, [3301a97]
colisão normalizada, execução, macro, script e conteúdo ativo DEVEM ser [3301a97]
bloqueados.

Testes sem rede DEVEM cobrir normalização editorial, transliteração e slug RFC [3301a97]
3986, acrônimo, path, assinatura, hashes, colisão, metadado legado/v2/v3,
plano, repetição, apply, rollback, falha de persistência, skip sem request,
parcial, corrupção, atualização, `pt-BR`/`en`, rejeição de idioma, multiautor,
coleções, extração ordenada, exclusão da interface, lacunas, Markdown, EPUB,
original/derivado, `Retry-After`, backoff, limite, contenção, retomada, entrada
hostil, índice, raiz de runtime ausente/corrompida, migração de perfil, suspensão
integral, handoff cancelado/aceito/recusado, segredo em log, publicação completa,
allowlist Git, worktree alheia, falha de commit e retomada. [PENDENTE-CODIGO]

O dry-run integral DEVE contabilizar todo arquivo esperado, rejeitar orfao, slug invalido ou colisao, comparar bytes/hashes e produzir plano reproduzivel antes de qualquer movimento. Depois da aplicacao, DEVE auditar a arvore canônica integralmente em slugs, produzir zero acao residual e repetir inventario identico. [3301a97]

Fixture/mock DEVE preceder amostra pública mínima. A amostra DEVE limitar [3301a97]
coleção, autor/publicação e ativos; desafio ou `403` encerra sem evasão. Coleta
ampliada exige todos os gates e autorização material própria.

O gate de completude DEVE incluir catálogo com múltiplas obras, ativos presentes [be82602]
somente na página individual, múltiplos formatos obrigatórios, botão [be82602]
desabilitado, cadeia textual multiunidade, ciclo, quebra de obra, ausência de
contêiner, preservação semântica, isolamento de fixture e comparação do texto
real no EPUB. [PENDENTE-CODIGO]
O gate também DEVE cobrir capa oficial JPEG/PNG, host e redirecionamento permitidos, limite de bytes/dimensões, remoção de metadados, determinismo, `cover.png`, manifesto/spine EPUB, igualdade de bytes e falha de capa. [PENDENTE-CODIGO]

A FT-005 não executa download, altera código ou move acervo. Implementação
pertence à FT-006 e exige nova autorização humana explícita após a conclusão
normativa. A decisão editorial pendente da FT-004/03 permanece independente e
intocada.
