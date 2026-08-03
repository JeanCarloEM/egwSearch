# RCF específico - aquisição pública de publicações

Este RCF subordina-se ao `RCF.md` da raiz e especifica a estrutura, a migração e
a aquisição pública pela automação em `scripts/publications/`. O namespace é
neutro quanto a autor: o portal de origem inclui Ellen G. White e autores
pioneiros distintos; cada publicação DEVE ser persistida sob a chave autoral canônica. [ef2f0c4]
Divergência DEVE aplicar o RCF da raiz. [ef2f0c4]

O downloader, o cliente de aquisição, o contrato Python comum e seus requisitos DEVEM residir em `scripts/publications/`, fora de `src/` e do artefato público. [ef2f0c4]

## 1. Identidade e configuração

`config/publications.json` é a configuração causal versionada da cadeia. Ela declara raiz-fonte, raiz pública, autores, coleções, idiomas, tipos e limites de rede; scripts DEVEM resolver seus paths pela raiz do repositório, nunca pelo diretório corrente. [62596f1]

O autor `egw` representa Ellen G. White. Autores pioneiros DEVEM receber chave [ef2f0c4]
autoral própria, determinística e persistente; coleção, provedor ou editora NÃO
DEVEM substituir autor. Cada identidade editorial DEVE combinar `remote_id` [ef2f0c4]
quando disponível, `collection`, `author`, `language`, `type`, título,
edição/versão e origem, sem converter formato em tipo. [e59c122]

As coleções obrigatórias são as coleções públicas observadas `Biblioteca dos [ef2f0c4]
Pioneiros Adventistas` (`pt/1055`) e `Pioneer Authors` (`en/16`),
além das coleções de Ellen G. White já suportadas. O catálogo real DEVE [ef2f0c4]
descobrir autores, tipos e obras; enumeração fixa somente PODE ser fixture ou [ef2f0c4]
fallback incompleto explicitamente marcado.

O agrupador inglês `/allCollection/en/15`, que encaminha para autores, periódicos e títulos diversos, NÃO constitui grade de obras e NÃO DEVE ser aguardado como catálogo de `en-pioneers`. [1fd53ef]

Somente `pt-BR` e `en` são idiomas elegíveis. `pt`, `pt_BR` e equivalentes
comprovados DEVEM normalizar para `pt-BR`; inglês sem diferença material, [ef2f0c4]
inclusive `en_US` e `en-GB`, DEVE normalizar para `en`. Valor remoto original [ef2f0c4]
DEVE ser preservado; diferença material de variante DEVE bloquear fusão. [ef2f0c4]

Título normalizado DEVE preservar Unicode, caixa, diacríticos, pontuação e trecho parentético duvidoso; slug de rota é projeção separada e NÃO DEVE substituir nem servir para reconstruir o título. Tag ou edição somente DEVE sair do título com evidência editorial registrada. [62596f1]

Artigo final separado por vírgula DEVE ser removido somente quando repetir, por equivalência Unicode sem diacríticos e caixa, o artigo já presente no início; essa canonicalização editorial antecede acrônimo, slug, preflight e destino. Demais sufixos ou inversões ambíguas DEVEM ser preservados. [be19ffb]

O acrônimo do título DEVE derivar apenas de suas palavras normalizadas: título de uma palavra usa seu token ASCII normalizado; título de várias palavras usa as iniciais alfanuméricas, em minúsculas. Ausência de representação ASCII DEVE usar identificador causal derivado do título Unicode. [62596f1]

## 2. Paths e colisoes

A raiz local é `src/publications/`; cada grupo DEVE ocupar `[<category>/]<author-key>/<language-path>/<type>/<slug-titulo>/`; `category` DEVE anteceder o autor como agrupamento semântico, usar código curto explícito em PT-BR e URI-safe também na coleção inglesa, e ser omitida somente quando igual a `author-key`. [68772fb]
O rótulo remoto original e o código da categoria DEVEM integrar metadado e identidade estável; ausência, categoria arbitrária ou inferência por título/autor DEVEM bloquear aquisição. [84df7a6]
Para Ellen G. White,
`author-key` permanece `egw`; autores pioneiros NÃO DEVEM ser gravados sob [ef2f0c4]
`egw`. `pt-BR` projeta `pt-br` e `en` projeta `en` no path. O legado `en-us`
DEVE ser reconhecido durante transição e NÃO DEVE provocar nova aquisição; [ef2f0c4]
migração para `en` exige plano atômico e prova de ausência de variante
material. PDF, EPUB, Markdown, derivados e metadado do grupo DEVEM permanecer [ef2f0c4]
no mesmo diretório. [c5c4da6]

Slug DEVE seguir `[a-z0-9]+(?:-[a-z0-9]+)*`: aplicar minúsculas, decomposição Unicode, transliteração ASCII determinística, remoção de acentos, diacríticos e caracteres especiais, substituição de espaços por hifens, colapso e aparo de hifens; resultado vazio e limite de portabilidade DEVEM usar hash causal. Path e segmento DEVEM permanecer relativos à raiz declarada, sem traversal, path absoluto, controle, nome reservado do Windows ou equivalência insegura por caixa/normalização. [62596f1]

Destino ausente DEVE receber o original. Destino existente com SHA-256 idêntico DEVE eliminar somente a cópia redundante depois da validação transacional. Destino existente com hash diferente DEVE preservar a variante em `<acronimo>.<prefixo-sha256>.<extensao>`; o prefixo DEVE iniciar com oito caracteres e expandir em pares até desambiguar. [62596f1]

Antes da promoção, o coletor DEVE comparar o SHA-512 integral do PDF/EPUB com todo o acervo: igualdade em diretórios de publicação distintos caracteriza duplicação física global e proíbe a segunda cópia, quaisquer que sejam nomes ou slugs. Resolução editorial determinística DEVE reutilizar o diretório canônico; sem ela, a operação DEVE bloquear para revisão e preservar ambos os estados anteriores sem promover o temporário. [be19ffb]

## 3. Metadado local e estado incremental

O downloader DEVE emitir `egw-source/v2`, UTF-8 sem BOM e JSON deterministico. A raiz DEVE conter exatamente `schema_version`, `identity` e `sources`. [ef2f0c4]

`identity` DEVE conter exatamente `author`, `language`, `type`, `title`, `acronym` e `tags`. `tags` DEVE permanecer vazio sem evidência confirmada. [62596f1]

Cada item de `sources` DEVE conter exatamente `format`, `url`, `accessed_at`, `size` e `hashes`; `hashes` DEVE conter exatamente `sha1`, `sha256` e `sha512`. Registros DEVEM ordenar por formato `pdf`, `epub` e depois URL. [ef2f0c4]

Metadado legado URL-chaveado DEVE permanecer entrada válida da migração. Sua associação DEVE exigir compatibilidade de formato, URL e SHA-256 com o arquivo quando esses dados existirem; filename isolado NÃO DEVE bastar para declarar conformidade. [62596f1]

`egw-source/v2` permanece legível para os 527 grupos existentes e NÃO DEVE ser [ef2f0c4]
reescrito em execução sem mudança material. Aquisição nova ou atualização
material DEVE evoluir para `publication-source/v3`, com raiz fechada [ef2f0c4]
`schema_version`, `identity`, `collection`, `state`, `sources`, `segments`,
`derivations` e `history`.

`identity` v3 DEVE preservar identificador remoto, autor original e chave [ef2f0c4]
autoral, título original e normalizado, idiomas original e canônico, tipo
original e canônico, edição/versão, acrônimo, slug, tags e URL pública.
`collection` DEVE preservar identificador, nome, idioma e URL do catálogo. [ef2f0c4]

`sources` DEVE registrar por ativo ou segmento URL, método [ef2f0c4]
`native-download`/`text-extraction`, formato, validadores HTTP, coleta
material, tamanho, MIME/assinatura e hashes. `segments` DEVE registrar [ef2f0c4]
identificador, URL, índice editorial, título, hash e estado de completude.
`derivations` DEVE relacionar fonte, Markdown e EPUB local com gerador, [ef2f0c4]
versão, transformação e hashes, sem apresentar derivado como original.
`history` DEVE registrar somente mudanças materiais e relação entre versões. [ef2f0c4]

Ledger operacional, cache, tentativas e resultado `skipped` da execução DEVEM [ef2f0c4]
residir em estado local segregado e atômico, fora de `formative_data`; eles
NÃO DEVEM alterar metadado versionado ou timestamps do grupo quando nada [ef2f0c4]
mudou.

Estados permitidos são `pending`, `processing`, `completed`, `skipped`,
`incomplete`, `corrupt`, `unavailable`, `ineligible`, `temporary_failure`,
`permanent_failure` e `review_required`. Somente `completed` com artefatos,
metadado e índice coerentes comprova incorporação.

## 4. Contrato comum

`publication_contract.py` é a unidade comum para normalização editorial, slug URI, identidade, paths, formatos, hashes, metadados e colisões. Downloader, migrador, indexador e validador DEVEM reutilizá-la. [62596f1]

O modulo comum DEVE usar somente a biblioteca padrao do Python. A escolha preserva o runtime preexistente, evita dependencia para regras deterministicas e deixa bibliotecas de navegador/rede restritas ao downloader. [ef2f0c4]

Toda leitura de arquivo para hash DEVE ser binaria, sequencial e calcular SHA-1, SHA-256 e SHA-512 na mesma passagem. PDF DEVE exigir assinatura `%PDF-`; EPUB DEVE exigir ZIP OCF com entrada `mimetype` igual a `application/epub+zip`. [ef2f0c4]

## 5. Migrador temporario

`constructor/publications/migrate.py` e ferramenta interna temporaria, fora da fonte publicada. Sua interface canonica e:

- `plan` DEVE inventariar e gerar plano sem mover; [ef2f0c4]
- `apply --plan <arquivo>` DEVE aplicar somente plano integro e ainda correspondente ao estado; [ef2f0c4]
- `rollback --journal <arquivo>` DEVE reverter operação incompleta ou aplicada ainda não finalizada; [62596f1]
- `finalize --journal <arquivo>` DEVE remover quarentena somente depois da validação completa. [62596f1]

`plan` DEVE ser o default e não possuir efeito no acervo. O plano DEVE declarar schema, identidade causal, configuração, inventário, grupos, ações e renomeações Unicode-para-slug, problemas e resumo; ordem e identidade DEVEM independer de horário, cwd e enumeração do filesystem. [62596f1]

`apply` DEVE verificar path, tamanho e SHA-256 antes de cada ação de renomeação, persistir sua intenção antes do movimento, confirmar o journal atômico depois e usar quarentena para redundância. Falha DEVE acionar rollback reverso, inclusive de registro pendente cuja origem ou destino comprove se o movimento ocorreu; journal e quarentena DEVEM preservar retomada. Replace atômico temporariamente bloqueado DEVE admitir somente retry limitado. `finalize` DEVE recusar estado não concluído. [62596f1]

O migrador NÃO DEVE acessar rede nem modificar bytes de PDF/EPUB; diretório Unicode vazio somente PODE ser removido depois da validação integral dos arquivos movidos e o rollback DEVE recriá-lo quando necessário. Código `0` DEVE indicar sucesso; `1`, falha operacional; `2`, uso ou entrada inválida; `3`, conflito ou precondição; `4`, integridade insegura. [62596f1]

## 6. Downloader e descoberta

`baixar.py` NÃO DEVE produzir efeito por importação. A CLI DEVE carregar [ef2f0c4]
configuração, selecionar coleção, autor ou publicação, descobrir candidatos e
persistir diretamente no diretório canônico. Descoberta, elegibilidade,
preflight, cliente HTTP, download, extração, Markdown, EPUB, metadados, estado
e relatório DEVEM possuir unidades testáveis separadas, sem fragmentação [ef2f0c4]
artificial. [e59c122]

Catálogo ou API pública estruturada consumida pela própria aplicação DEVE ser [ef2f0c4]
preferida ao DOM. Parsing renderizado somente PODE ser fallback quando não [ef2f0c4]
houver contrato direto adequado, e DEVE usar fixture versionada, seletores [ef2f0c4]
semânticos e falha fechada diante de alteração.

Quando o portal oferecer uma interface pública leve com o mesmo conteúdo
editorial, ela DEVE ser preferida à aplicação completa se reduzir desafio, [57560e8]
virtualização e dependência de JavaScript sem reduzir cobertura. [PENDENTE-CODIGO]
A enumeração DEVE coletar incrementalmente todos os `href` únicos de obra; [57560e8]
rolar e analisar somente o DOM final é insuficiente para grade virtualizada. [PENDENTE-CODIGO]

O cartão do catálogo fornece somente identidade preliminar. A página individual
da obra DEVE ser consultada antes da aquisição e é a autoridade para autor, [57560e8]
título, código, URL inicial de leitura e todos os links PDF/EPUB habilitados. [PENDENTE-CODIGO]
Cada ativo habilitado é obrigatório; `disabled`, URL vazia ou `#` significa [57560e8]
indisponível e não falha de download.

Antes de solicitar catálogo novamente para unidade conhecida ou qualquer
ativo, o preflight DEVE consultar ledger/índice, identidade remota, metadado, [ef2f0c4]
path, integridade, tamanho, ETag, `Last-Modified` e hash disponível em níveis.
SHA-256 local e request somente DEVEM ocorrer quando o nível anterior não for [ef2f0c4]
conclusivo.

Item `completed`, íntegro e indexado DEVE resultar em `skipped` sem request do [ef2f0c4]
ativo, conversão, extração, reprocessamento ou regravação. Nome existente
isolado, temporário ou parcial NÃO DEVE ser aceito. [ef2f0c4]

Depois da listagem única, o preflight DEVE receber também título, URL e autor do cartão e compor com coleção, idioma, categoria e tipo a identidade local. Metadado legado URL-chaveado com PDF e EPUB válidos DEVE ser reconhecido pelo mesmo path/acrônimo, inclusive alias `en-us`, sem exigir página individual nem migração prévia para v3; colisão ou divergência continua exigindo enriquecimento. [42aa8aa]

O adaptador NÃO DEVE chamar `_enrich_book`, capa, leitura ou ativo enquanto o gate local puder comprovar a unidade. A liberação da rede DEVE decorrer somente de motivo objetivo de insuficiência local ou `--revalidate`, e o teste do caminho completo legado DEVE usar sentinela que reprova qualquer chamada HTTP. [42aa8aa]

Na retomada, todo item não confirmado DEVE passar novamente pelo preflight vigente antes do processamento, inclusive quando o checkpoint registrar `local_complete=false`. Prova local válida DEVE substituir atomicamente o item armazenado e produzir `network=skipped`; somente a insuficiência atual, não o booleano histórico, mantém o fluxo remoto. [756d109]

O coletor DEVE gravar checkpoint atômico por coleção, filtro e limite depois da normalização do catálogo, depois de cada enriquecimento e depois de cada item confirmado. [8b60a50]
Retomada DEVE reutilizar catálogo e itens persistidos e continuar somente os enriquecimentos ou itens pendentes; checkpoint textual DEVE continuar da próxima página editorial ainda não confirmada. [8b60a50]
Na descoberta parcial retomada, `len(items)` DEVE ser a fronteira do catálogo já enriquecida: o adaptador NÃO DEVE chamar `on_item_ready` para esse prefixo, DEVE enriquecer e processar primeiro `ordered[len(items):]` e somente depois PODE tentar novamente IDs anteriores ainda não confirmados. Item confirmado NÃO PODE acionar navegador, HTTP, fechamento inteligente ou indexação. [f9423a0]
Item enriquecido e completo DEVE ser entregue ao processamento logo após seu checkpoint atômico, antes de iniciar o enriquecimento seguinte. Item posterior incompleto, bloqueado ou interrompido NÃO DEVE criar bloqueio em cadeia sobre geração, promoção ou confirmação dos itens anteriores. [fe5d354]
Checkpoint inválido NÃO DEVE ser renomeado, apagado ou ignorado automaticamente; a CLI DEVE bloquear e orientar `--restart`. [8b60a50]
`--restart` DEVE ser explícito, apagar somente checkpoints de runtime do escopo solicitado e preservar publicações, ledger e ativos canônicos. [8b60a50]

Título obtido da interface DEVE permanecer candidato editorial integral e NÃO DEVE constituir prova autossuficiente; somente sua projeção de path DEVE aplicar o slug comum, sem remover artigo, parêntese, tag, pontuação ou qualificador do título preservado. [62596f1]

Somente URL HTTPS de host allowlisted DEVE ser aceita. Cada request DEVE validar URL, DNS/IP público e redirecionamento; conexão DEVE usar timeout, limite de bytes, streaming, cancelamento por interrupção e arquivo parcial no destino. [62596f1]

Arquivo parcial somente DEVE ser incorporado depois de resposta completa, formato confirmado e hashes calculados. Incorporacao DEVE usar replace atomico; colisao DEVE aplicar o contrato comum e nunca sobrescrever bytes diferentes. [ef2f0c4]

Metadado DEVE ser atualizado atomicamente depois da incorporação do asset. [ef2f0c4]
Repetição de identidade/URL/formato/hash DEVE ser idempotente; fonte [ef2f0c4]
alternativa dos mesmos bytes DEVE permanecer registrável; falha NÃO DEVE [ef2f0c4]
emitir registro de sucesso. Atualização exige evidência material por hash,
versão/edição, novo ativo, correção remota, metadado relevante ou arquivo
local inválido/ausente. [e59c122]

Dependências de Selenium, Requests e tqdm DEVEM ser carregadas apenas pela execução da CLI. Ausência de dependência DEVE produzir diagnóstico e código `3`, sem impedir importação, teste do contrato ou migração. [62596f1]

Os requisitos fixados em `requirements.txt` DEVEM ser preparados pelo bootstrap multi-runtime do repositório em ambiente Python local segregado, antes da execução suportada da CLI. [8c1d9ef]

O bootstrap DEVE ser idempotente, não executar a CLI, não iniciar navegador e não realizar coleta; ausência ou incompatibilidade do interpretador/instalador DEVE produzir diagnóstico acionável. [8c1d9ef]

## 7. Cliente HTTP responsável

O cliente DEVE operar sequencialmente por padrão, com concorrência `1`, atraso [ef2f0c4]
base mínimo de dois segundos e jitter positivo configurável. Concorrência `2`
é o máximo e exige opt-in e evidência; qualquer valor superior DEVE ser [ef2f0c4]
rejeitado.

Sessão reutilizável, `User-Agent` identificável, timeout, limite de bytes,
streaming, cache, deduplicação, cancelamento, no máximo três tentativas e
backoff exponencial limitado DEVEM ser aplicados. Requisições condicionais [ef2f0c4]
`If-None-Match` e `If-Modified-Since` DEVEM ser usadas quando houver [ef2f0c4]
validadores.

`429` DEVE respeitar `Retry-After`; `408` e `5xx` PODEM repetir dentro do [ef2f0c4]
limite. [3301a97] Descoberta que dependa de navegador DEVE usar uma única instância [e284bcc]
visível, perfil persistente local segregado e uma única guia operacional [PENDENTE-CODIGO]
reutilizada em todas as coleções processadas pela execução; concorrência com [PENDENTE-CODIGO]
navegador DEVE ser `1`, e nova guia/sessão somente PODE ocorrer por fechamento, [e284bcc]
invalidação, corrupção ou recuperação controlada, com log do motivo. [PENDENTE-CODIGO]

CAPTCHA, challenge page, verificação de navegador, bloqueio temporário, [PENDENTE-CODIGO]
redirecionamento de validação, `403`, `429`, título/URL/DOM inesperado ou [PENDENTE-CODIGO]
ausência de grade do catálogo DEVEM ser avaliados por múltiplos sinais. Quando [e284bcc]
houver verificação humana legitimamente interativa, a automação DEVE manter a [e284bcc]
guia aberta, pausar somente o fluxo dependente, reduzir requisições ao mínimo, [PENDENTE-CODIGO]
emitir mensagem objetiva ao usuário, aguardar com intervalo configurável de [PENDENTE-CODIGO]
baixa frequência e retomar automaticamente após a grade ou conteúdo esperado [PENDENTE-CODIGO]
voltar. [PENDENTE-CODIGO]

`403`, CAPTCHA, desafio anti-automação, bloqueio ou contenção persistente que [PENDENTE-CODIGO]
não puderem ser liberados pela guia visível DEVEM parar a unidade/coleção, [e284bcc]
preservar progresso e marcar revisão, sem resolver desafio, intensificar, usar [PENDENTE-CODIGO]
proxy, rotacionar identidade, simular comportamento humano ou ocultar o cliente. [PENDENTE-CODIGO]

Log DEVE registrar coleção/unidade, taxa, tentativa, espera, status, [ef2f0c4]
cache/condicional e motivo de parada, sem credencial, token, corpo editorial
desnecessário ou dados privados.

Configuração do downloader DEVE declarar visibilidade do navegador, diretório [e284bcc]
do perfil persistente, intervalo de verificação, limite opcional de espera [PENDENTE-CODIGO]
humana, tempo de espera da grade, limite de recuperação e tamanho da janela. [PENDENTE-CODIGO]
Padrões DEVEM privilegiar navegador visível, perfil fora de commits, espera sem [e284bcc]
timeout curto, baixo consumo e recuperação finita. [PENDENTE-CODIGO]

### 7.1 Estado local central

`config/publications.json` DEVE declarar uma única `runtime_state_root`; ambiente [8c1d9ef]
Python, ledger, cache, perfil, sessão, temporários, locks, traces e logs DEVEM [8c1d9ef]
derivar dela por funções centrais, nunca por paths hardcoded dispersos. [PENDENTE-CODIGO]
A raiz
DEVE ser criada sob demanda, ignorada integralmente e excluída de build, Pages, [8c1d9ef]
pacote e release. [PENDENTE-CODIGO]

O estado local DEVE ser classificado em persistente, temporário ou sensível e [8c1d9ef]
possuir isolamento, retenção, limite, invalidação e limpeza próprios. [PENDENTE-CODIGO]
Perfil e
sessão DEVEM ser isolados por provedor/domínio e finalidade; parcial DEVE ficar [8c1d9ef]
em subdiretório de runtime até promoção atômica. [PENDENTE-CODIGO]
PDF, EPUB, Markdown, metadado e
índice validados permanecem canônicos e não podem ser ignorados como runtime. [8c1d9ef]
[PENDENTE-CODIGO]

Migração do perfil legado PODE mover somente árvore local comprovada, com [8c1d9ef]
origem/destino validados, ausência de processo ativo, operação idempotente e
fallback removido após sucesso. [PENDENTE-CODIGO]
Clone sem a raiz DEVE recriá-la sem perda [8c1d9ef]
funcional; corrupção de cache/perfil DEVE causar reset controlado ou diagnóstico, [8c1d9ef]
nunca sucesso falso. [PENDENTE-CODIGO]

### 7.2 Handoff humano desacoplado

O estado do navegador DEVE seguir `automatizado`, [8c1d9ef]
`aguardando_intervencao_humana`, `validando_retomada`, `retomado`, `cancelado`
ou `bloqueado`. [PENDENTE-CODIGO]
Transição para intervenção DEVE encerrar o WebDriver e todos os [8c1d9ef]
efeitos automáticos antes de abrir ou orientar o uso de navegador normal no
perfil autorizado. [PENDENTE-CODIGO]
Automação e humano não podem atuar simultaneamente. [8c1d9ef]
[PENDENTE-CODIGO]

O handoff DEVE usar processo normal sem flags de WebDriver e aguardar seu [8c1d9ef]
encerramento ou cancelamento sem inspecionar/interagir com o DOM. [PENDENTE-CODIGO]
Reinício do
controlador no mesmo perfil somente PODE ocorrer depois do encerramento humano; [8c1d9ef]
a retomada exige catálogo esperado, origem correta e ausência de desafio. [PENDENTE-CODIGO]
Perfil
incompatível, bloqueio persistente, expiração ou reapresentação encerra a
coleção como revisão, sem bypass ou retry ilimitado. [PENDENTE-CODIGO]

CLI DEVE permitir cancelar a espera, limitar seu tempo quando configurado, [8c1d9ef]
selecionar binário normal explicitamente e desabilitar handoff. [PENDENTE-CODIGO]
Log DEVE usar [8c1d9ef]
eventos sanitizados e nunca registrar cookie, token, storage ou resposta do
desafio. [PENDENTE-CODIGO]

### 7.3 Publicação completa e efeito Git

O coletor DEVE centralizar uma função que calcule e valide a unidade [f313f39]
`completa_e_pareada`: ativos, metadado, segmentos, derivados, referências e
entradas de índice impactadas. [PENDENTE-CODIGO]
O resultado DEVE expor allowlist relativa à raiz, [f313f39]
hashes e evidência de completude; item ambíguo ou incompleto não é elegível a
Git. [PENDENTE-CODIGO]

Finalização canônica que altere a unidade DEVE adquirir lock global no runtime, validar `dev`, executar análise e indexação compartilhadas e criar imediatamente um commit por publicação antes de confirmar seu checkpoint; ativação por flag é proibida. [PENDENTE-CODIGO]

Downloader, `publication_analysis.py` isolado e `publication_index.py --analyze` DEVEM reutilizar a mesma finalização transacional, sem commits duplicados na composição; fixture/teste com raiz explicitamente segregada NÃO DEVE tocar Git. [PENDENTE-CODIGO]

A finalização DEVE excluir estado não canônico, adicionar somente a allowlist positiva com `git add -- <paths>`, incluir a árvore da publicação e somente índice, manifesto estrutural ou aprendizado global efetivamente alterados por ela, validar o diff staged e criar exatamente um commit. [PENDENTE-CODIGO]

Alteração staged preexistente, alteração alheia ou conflito em path global DEVE bloquear sem incorporá-los nem modificar o índice Git correspondente. [PENDENTE-CODIGO]

Falha entre promoção e commit DEVE restaurar índice/metadado da transação ou preservar preparação no runtime como `commit_pending`; commit confirmado DEVE ser registrado no ledger e não pode ser repetido. [PENDENTE-CODIGO]

Push DEVE permanecer fase separada e NÃO DEVE ser requisito implícito do download, da análise ou da indexação. [PENDENTE-CODIGO]

## 8. Conteúdo textual e derivados

Texto on-line somente PODE ser adquirido se PDF e EPUB nativos estiverem [ef2f0c4]
ausentes e se identidade, ordem, primeira/última unidade e completude forem
determináveis sem contorno.

A extração DEVE iniciar na URL `Read Online` da página individual e seguir [57560e8]
somente links editoriais `rel=next` da mesma obra até ausência ou marca de
término. [PENDENTE-CODIGO]
Cada transição DEVE validar URL, identificador da obra, ausência de [57560e8]
ciclo, coerência do `rel=prev` quando aplicável e presença do contêiner
editorial `#r-pl` ou contrato público equivalente. [PENDENTE-CODIGO]

Extrator DEVE preservar título, subtítulo, autoria, prefácio, introdução, [ef2f0c4]
capítulos, seções, parágrafos, notas, citações, listas, tabelas textuais,
epígrafes e referências. DEVE excluir navegação, menus, cabeçalhos/rodapés da [ef2f0c4]
aplicação, breadcrumbs, controles, recomendações, relacionados, anúncios,
telemetria, scripts, estilos, mensagens e duplicações de renderização.

Cada segmento DEVE possuir identificador, URL, ordem e hash. Lacuna, [ef2f0c4]
duplicação, contagem divergente ou ordem incerta DEVE impedir `completed` e [ef2f0c4]
produzir `review_required`.

Markdown DEVE usar UTF-8, arquivos numerados pela ordem editorial, nomes com [ef2f0c4]
slug canônico e metadado próprio. EPUB derivado DEVE ser gerado mecanicamente a [ef2f0c4]
partir do Markdown já preservado, conter sumário/metadados/idioma/autor/notas,
passar validação técnica e ser marcado `local-conversion`.

O pipeline `fonte estruturada -> Markdown -> EPUB` NÃO DEVE recolher texto já [ef2f0c4]
completo. Sanitização NÃO DEVE corrigir, resumir, modernizar, traduzir ou [ef2f0c4]
reescrever conteúdo; Unicode e estrutura semântica DEVEM ser preservados. [ef2f0c4]

No contêiner editorial, elementos `h1` a `h6`, parágrafos, listas, tabelas,
blockquote, imagens editoriais, notas, ênfase, links e quebras materiais DEVEM [57560e8]
ser preservados em ordem. [PENDENTE-CODIGO]
Marcadores de referência e controles da aplicação DEVEM ser separados do texto, [57560e8]
mas seu identificador editorial DEVE permanecer no metadado do bloco. [57560e8]
Texto vazio, placeholder, fixture ou corpo sem blocos
editoriais válidos DEVE impedir derivação. [57560e8]

Fixture executada pela CLI DEVE exigir `--output-root` explícito fora da raiz [57560e8]
canônica ou usar automaticamente subdiretório temporário da raiz de runtime; [PENDENTE-CODIGO]
ela nunca PODE gravar em `src/publications`. [57560e8]

Derivado local NÃO DEVE integrar `formative_data.urls` ou [ef2f0c4]
`formative_data.global_hashes` como se fosse original. Seu hash, gerador e
proveniência DEVEM residir no envelope global e no metadado v3. [ef2f0c4]

Quando a ficha pública da obra textual declarar capa por `og:image`, relação equivalente ou endpoint oficial do mesmo identificador remoto, essa URL DEVE ser preservada e adquirida de host allowlisted como fonte obrigatória. [84df7a6]
A imagem DEVE ser limitada, decodificada e normalizada deterministicamente para `cover.png`, com no máximo 800 px por eixo, proporção preservada, sem ampliação e sem metadados dispensáveis; escrita e promoção DEVEM ser atômicas. [84df7a6]
O EPUB derivado DEVE incluir a imagem no manifesto com propriedade `cover-image`, página de capa no início do spine e bytes iguais ao `cover.png`; um gerador PDF futuro DEVE usar o mesmo arquivo como capa antes do texto, sem autorizar PDF rasterizado como falso equivalente editorial. [84df7a6]
A página `cover.xhtml` DEVE ser o primeiro item do spine e conter exclusivamente a capa, com viewport e página sem margens e preenchimento integral de borda a borda; proporções divergentes DEVEM usar escala proporcional `slice` e recorte central, sem faixas ou deformação. [84df7a6]
Metadado v3 DEVE registrar separadamente a fonte remota e o derivado normalizado, com URL, método, path, tamanho e hashes verificáveis. [84df7a6]
Reexecução sem mudança DEVE validar e reutilizar capa e EPUB; `--revalidate` DEVE readquirir ou revalidar a capa antes de concluir. [84df7a6]
O EPUB textual DEVE manter documentos XHTML semânticos no spine e armazenar fora dele os bytes Markdown intermediários, acompanhados de manifesto versionado com nome, ordem e SHA-256. [84df7a6]
O conversor NÃO DEVE emitir bytes NUL, caracteres de controle ou sentinelas internas no Markdown/XHTML; cada documento do spine DEVE passar por parser XML antes da promoção, e falha de análise DEVE invalidar o derivado local. [fe5d354]
Uma operação de restauração DEVE validar paths, cardinalidade, ordem e hashes do manifesto e recriar os `.md` byte a byte sem interpretar o XHTML. [84df7a6]
Os `.md` externos somente PODEM ser removidos após validação integral do EPUB e round trip de restauração em runtime temporário; qualquer falha DEVE preservar os arquivos e bloquear conclusão. [84df7a6]
A página `provenance.xhtml` DEVE suceder imediatamente à capa no spine e anteceder o sumário e qualquer conteúdo, usar `epub:type="frontmatter acknowledgments"` e permanecer separada das fontes Markdown e do corpo editorial. [9679008]
A nota DEVE registrar autor, título, plataforma EGW Writings, URL oficial clicável e data de acesso em forma de referência ABNT, usando data da aquisição efetiva e sem inventar local, editora ou data de publicação ausentes. [9679008]
O sumário navegável DEVE integrar o spine depois da proveniência e antes da primeira seção editorial. [9679008]
Cada documento de conteúdo DEVE declarar cabeçalho corrente contextual conforme o título editorial da unidade — inclusive capítulo/seção, edição de periódico ou dia de meditação quando essa for a autoridade disponível — e rodapé com `counter(page)` por caixas de margem CSS `@page`, sem inserir `header` ou `footer` no corpo XHTML indexável. [9679008]
A pseudo-página `:first` de cada capítulo, seção ou unidade equivalente DEVE suprimir o cabeçalho corrente e manter o rodapé numerado. [9679008]
Metadado de segmentos DEVE referenciar paths internos do EPUB e a validação incremental DEVE comprovar os hashes diretamente no contêiner, sem depender de `.md` externo. [84df7a6]

## 9. Segurança, validação e fronteira

Todo dado remoto DEVE ser não confiável. URL, esquema, host allowlisted, [ef2f0c4]
DNS/IP, redirecionamento, nome, path, MIME, assinatura, tamanho e arquivo
compactado DEVEM ser validados; traversal, path absoluto, dispositivo, symlink, [ef2f0c4]
colisão normalizada, execução, macro, script e conteúdo ativo DEVEM ser [ef2f0c4]
bloqueados.

Testes sem rede DEVEM cobrir normalização editorial, transliteração e slug RFC [ef2f0c4]
3986, acrônimo, path, assinatura, hashes, colisão, metadado legado/v2/v3,
plano, repetição, apply, rollback, falha de persistência, skip sem request,
parcial, corrupção, atualização, `pt-BR`/`en`, rejeição de idioma, multiautor,
coleções, extração ordenada, exclusão da interface, lacunas, Markdown, EPUB,
original/derivado, `Retry-After`, backoff, limite, contenção, retomada, entrada
hostil, índice, raiz de runtime ausente/corrompida, migração de perfil, suspensão
integral, handoff cancelado/aceito/recusado, segredo em log, publicação completa,
allowlist Git, worktree alheia, falha de commit e retomada. [PENDENTE-CODIGO]

O dry-run integral DEVE contabilizar todo arquivo esperado, rejeitar orfao, slug invalido ou colisao, comparar bytes/hashes e produzir plano reproduzivel antes de qualquer movimento. Depois da aplicacao, DEVE auditar a arvore canônica integralmente em slugs, produzir zero acao residual e repetir inventario identico. [ef2f0c4]

Fixture/mock DEVE preceder amostra pública mínima. A amostra DEVE limitar [ef2f0c4]
coleção, autor/publicação e ativos; desafio ou `403` encerra sem evasão. Coleta
ampliada exige todos os gates e autorização material própria.

O gate de completude DEVE incluir catálogo com múltiplas obras, ativos presentes [57560e8]
somente na página individual, múltiplos formatos obrigatórios, botão [57560e8]
desabilitado, cadeia textual multiunidade, ciclo, quebra de obra, ausência de
contêiner, preservação semântica, isolamento de fixture e comparação do texto
real no EPUB. [PENDENTE-CODIGO]
O gate também DEVE cobrir capa oficial JPEG/PNG, host e redirecionamento permitidos, limite de bytes/dimensões, remoção de metadados, determinismo, `cover.png`, manifesto/spine EPUB, igualdade de bytes e falha de capa. [84df7a6]
O gate DEVE inspecionar `cover.xhtml` e comprovar primeira página exclusiva, ausência de margens/faixas/texto visível, preenchimento integral e recorte central proporcional. [84df7a6]
O gate também DEVE cobrir manifesto Markdown interno, restauração byte a byte, remoção pós-validação, indexabilidade XHTML e separação/texto/data/link da nota ABNT não editorial. [84df7a6]

## 10. Inteligência estrutural e índice global

`publication_analysis.py` DEVE ser a capacidade única de análise de EPUB/PDF e `publication_index.py` a capacidade única do índice global; seus `main()` são invocadores finos das mesmas funções usadas pelo downloader, sem reimplementação de schema ou regra de negócio. [1fd53ef]

O indexador DEVE manter ao lado do índice um manifesto estrutural ultrassucinto, tipado, determinístico e agnóstico de estado, quantidade ou conteúdo real, definindo exclusivamente a forma do índice sem replicar publicações ou valores observados. [eac8a30]

O manifesto de cada ativo DEVE usar schema versionado e registrar somente identidade/hashes, parser realmente executado, estrutura observada, referência normalizada sem texto, experimentos executados, métricas, hashes de prova e recomendação comprovada; benefícios, riscos, descrições, parâmetros genéricos e hipóteses não executadas DEVEM permanecer no catálogo global versionado referenciado por ID/versão/hash. [25d99c4]

Para EPUB gerado pelo produto, a análise DEVE reconhecer o manifesto Markdown reversível, separar capa/proveniência/sumário do spine editorial e aproveitar headings, IDs, unidades e source map já conhecidos; Markdown embutido serve de evidência estrutural e NÃO DEVE ser extraído persistentemente. [1fd53ef]

Para PDF, `pypdfium2` DEVE ser o parser preferencial já preparado pelo bootstrap para extrair integralmente, dentro dos limites declarados, páginas e camada textual; amostragem parcial ou fallback binário PODEM diagnosticar estrutura, mas NÃO PODEM recomendar estratégia integral do ativo nem acionar OCR implícito. [25d99c4]

Cada método localmente disponível DEVE ser executado sobre a mesma referência canônica e aferido por cobertura, ordem, perda, duplicação, contaminação, fronteiras e continuidade entre páginas; recomendação exige `passed`, e insuficiência de prova gera `inconclusive`, nunca pontuação heurística. [25d99c4]

Manifestos compatíveis existentes no corpus DEVEM alimentar uma base global deduplicada por perfil estrutural, método, implementação, parâmetros e versão. Essa base DEVE agregar somente estados e distribuições métricas, sem conteúdo textual, explicação repetida, inferência editorial ou conversão automática de frequência em recomendação. [25d99c4]

O catálogo global DEVE enumerar hipóteses fixas, recursivas, regex, sentença, parágrafo, página/layout, hierarquia/tópico, unidades editoriais, coesão semântica, perplexidade, proposição, LLM, múltiplas granularidades, late chunking, chunk-free e documento inteiro, com referências e condições definidas em `RCF.md` §43.2.1. [25d99c4]

Integração opcional com IA DEVE receber somente representação previamente normalizada, condensada, deduplicada e minimizada; conteúdo bruto, cabeçalho/rodapé comprovado e elemento irrelevante NÃO DEVEM ser enviados, e o laboratório offline determinístico permanece obrigatório. [25d99c4]

`publication_console.py` DEVE ser a camada visual compartilhada de `baixar.py`, `publication_analysis.py` e `publication_index.py`; modo isolado possui cabeçalho/resumo próprios e modo embutido reutiliza o contexto pai sem duplicá-los. [25d99c4]

Rich DEVE renderizar tabelas sem wrap acidental, com largura limitada e truncamento previsível de paths/títulos; ambiente não TTY, `NO_COLOR` ou indisponibilidade controlada DEVE usar fallback textual sem ANSI e com os mesmos dados essenciais. [25d99c4]

Tabela experimental por ativo DEVE sintetizar método, estado, chunks, duração/throughput, acerto, erro e códigos de diagnóstico, preservando métricas completas somente no JSON. Publicações consecutivas DEVEM manter duas linhas em branco ou separador visual inequívoco. [25d99c4]

O índice `publication-global-index/v1` DEVE conter envelope de geração e lista ordenada de publicações; cada item DEVE expor identidade, autoria, localização, rotas públicas, ativos, capa, manifestos de análise, hashes e estado/dados formativos elegíveis. [1fd53ef]

Atualização `--publication` DEVE substituir somente a identidade alvo quando o índice existente cobrir integralmente os metadados válidos do corpus; índice ausente, incompatível ou incompleto DEVE acionar reconstrução integral local. `--scope` analisa/regenera somente a subárvore solicitada, e `--all` cobre o corpus, sempre com resolução a partir da raiz configurada. [1fd53ef]

Toda invocação direta ou indireta da análise DEVE reutilizar sem reexecução uma prova `completed` com menos de 24 horas somente quando ativo, hashes, analisador, catálogo/configuração e contexto editorial continuarem válidos; o skip NÃO DEVE reescrever manifesto, aprendizado, índice, checkpoint ou timestamp. [f0c7638]

`--force-recalculate` DEVE ser o único override da janela e ser propagado pelo downloader, pelo modo de análise do indexador, pelo wrapper TypeScript e pelos comandos npm; prova ausente, falha, expirada, futura, inválida ou materialmente divergente DEVE recalcular. [f0c7638]

Depois de `_process_catalog_item` concluir ou reutilizar uma unidade válida, o orquestrador DEVE chamar um único fechamento síncrono que analisa todos os EPUB/PDF, valida os manifestos, atualiza índice/aprendizado e cria o commit exclusivo; somente então PODE marcar o remote ID como confirmado. [PENDENTE-CODIGO]

Fechamento local incompleto DEVE falhar o item sem apagar ativos já promovidos; na retomada, o preflight editorial válido DEVE permitir reparar análise/índice somente com arquivos locais, mantendo `network=skipped`. [1fd53ef]

Nos modos globais, downloader e analisador DEVEM persistir atomicamente em runtime um diário versionado com escopo, ordem, fingerprint, publicação, ativo, fase e último limite confirmado e DEVEM retomá-lo automaticamente sem reiterar unidades concluídas. [PENDENTE-CODIGO]

`--restart` no downloader e `--reset` no analisador DEVEM descartar somente o cursor do escopo explícito e ser propagados sem perda pelo indexador e wrappers; cursor incompatível ou corrompido DEVE bloquear em vez de reiniciar silenciosamente. [PENDENTE-CODIGO]

A FT-005 não executa download, altera código ou move acervo. Implementação
pertence à FT-006 e exige nova autorização humana explícita após a conclusão
normativa. A decisão editorial pendente da FT-004/03 permanece independente e
intocada.
