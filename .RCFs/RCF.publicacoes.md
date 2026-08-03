# RCF subordinado — Publicações e cadeia pública

Este documento integra a suíte normativa do **egwSearch**, subordina-se ao
[RCF principal](../RCF.md) e preserva os §§40–49 da numeração global. Ele rege
site institucional, estrutura do acervo, aquisição, índice, dados formativos,
capas, build, GitHub Pages, validação e aceite da cadeia pública.

O [RCF operacional do downloader](../scripts/publications/RCF.md) é mais
específico somente em seu escopo e permanece subordinado a este documento e ao
RCF principal.

**Ordem:** leia primeiro o RCF principal; depois este documento; por fim o RCF
operacional quando houver aquisição ou processamento de publicação.

## 40. Publicação institucional estática

O produto DEVE possuir página institucional ultrassucinta publicada no GitHub Pages por workflow próprio, sem depender implicitamente de tema, build automático ou convenção padrão da plataforma. [62596f1]

A página DEVE explicar finalidade, natureza das publicações, formatos e forma geral de acesso, sem promoção excessiva, documentação longa ou seção redundante. [62596f1]

A página DEVE ser profissional, elegante, responsiva, acessível e coerente, sem poluição visual, animação excessiva ou dependência desproporcional. [62596f1]

Lógica cliente nova DEVE usar TypeScript; estilização processada DEVE usar Sass. [62596f1]

Font Awesome e WebAwesome PODEM ser priorizados quando agregarem valor e somente o subconjunto usado DEVE integrar build ou runtime. [62596f1]

HTML, CSS, JavaScript, fontes, ícones e imagens DEVEM ser reduzidos ao necessário, cacheados, comprimidos, minificados e invalidados de forma coerente. [62596f1]

A página NÃO DEVE listar, expor ou vincular o índice global, arquivos de publicação, URLs diretas ou diretórios de distribuição, inclusive por botão, âncora oculta, metadado visual ou lista gerada. [62596f1]

A ausência de links na página NÃO DEVE impedir que índice, publicações e assets integrem o artefato e permaneçam acessíveis diretamente por URL pública conhecida. [62596f1]

Paths de scripts, estilos, fontes, imagens e assets DEVEM funcionar em domínio próprio e em subdiretório de projeto do GitHub Pages. [62596f1]

## 41. Estrutura canônica do acervo

A origem local DEVE ser `./src/publications/` e a raiz pública DEVE ser `/publications/`. [62596f1]

Cada publicação DEVE ocupar `/publications/[<categoria>/]<acronimo-autor>/<language>/<tipo>/<slug-titulo>/`, onde `<categoria>` é código URI curto em PT-BR da classificação editorial oficial e antecede o autor como agrupamento semântico, omitido somente quando igual ao autor, `<tipo>` é classificação lógica e não formato físico e `<slug-titulo>` é segmento URI ASCII determinístico derivado do título editorial. [62596f1]

O rótulo original da categoria DEVE ser preservado nos metadados e seu código de path DEVE vir de mapeamento explícito, curto e URI-safe em PT-BR, inclusive para coleções inglesas; categoria NÃO PODE ser inferida do título ou autor, e ausência de autoridade classificatória DEVE bloquear aquisição material. [62596f1]

O slug de rota DEVE usar somente `[a-z0-9]+(?:-[a-z0-9]+)*`: converter o título para minúsculas, decompor Unicode, remover acentos, diacríticos e caracteres especiais, substituir espaços por hifens, colapsar hifens repetidos e remover hifens nas extremidades. Caractere sem transliteração ASCII e título cujo resultado fique vazio DEVEM receber fallback causal determinístico; limite de portabilidade DEVE truncar com sufixo de hash, sem colisão silenciosa. [62596f1]

Título editorial e slug de rota possuem autoridades distintas: `book.title`, metadados e evidências DEVEM preservar a forma editorial, enquanto diretório, rota pública e URL DEVEM usar exclusivamente o slug. Título editorial NÃO DEVE ser reconstruído do slug. [62596f1]

PDF, EPUB, metadados, capa e demais assets do mesmo título DEVEM permanecer no mesmo diretório lógico. [62596f1]

Formato ou extensão diferente NÃO DEVE criar diretório separado para a mesma identidade editorial. [62596f1]

CONTRADIÇÃO DETECTADA: subdiretório intermediário `assets/<basename-publicacao>/` vs agrupamento final de todos os arquivos no diretório canônico do título - Aplicando o agrupamento final, posterior e mais completo.

Cada arquivo diretamente associado DEVE usar `<acronimo-titulo>.<extensao>`; qualificador adicional PODE ser usado somente quando determinístico, semanticamente necessário e não redundante. [62596f1]

O acrônimo DEVE derivar exclusivamente do título normalizado, ignorar tags confirmadas, ser estável e usar a mesma regra em migração, download, indexação e publicação. [62596f1]

Trecho entre parênteses DEVE ser classificado por evidência como título legítimo, tag, edição ou qualificador; regra cega NÃO DEVE remove-lo. [62596f1]

Tag confirmada DEVE sair do título e do acrônimo e ser preservada no índice; dúvida DEVE preservar o título e registrar revisão. [62596f1]

Colisão de destino DEVE comparar SHA-256 integral: hash igual elimina cópia redundante; hash diferente preserva variante como `<acronimo-titulo>.<hash-curto>.<extensao>`. [62596f1]

SHA-512 integral de PDF ou EPUB DEVE ser identidade física global do ativo no acervo: bytes iguais NÃO PODEM coexistir em diretórios de publicação distintos, ainda que título, acrônimo, filename ou slug difiram. A promoção DEVE reutilizar o grupo canônico quando a resolução editorial for determinística; ambiguidade DEVE bloquear para revisão sem apagar nem escolher silenciosamente. [62596f1]

Título remoto em forma invertida com artigo final separado por vírgula DEVE remover esse artigo somente quando ele repetir o mesmo artigo já presente no início do título; por exemplo, `A CIÊNCIA DO BOM VIVER, A` projeta `A CIÊNCIA DO BOM VIVER` e `a-ciencia-do-bom-viver`. Título sem repetição inequívoca DEVE permanecer preservado. [62596f1]

Hash curto DEVE derivar do SHA-256, ter comprimento mínimo desambiguador e expandir somente diante de colisão do prefixo. [62596f1]

Arquivo com hash diferente NÃO DEVE ser sobrescrito ou descartado; contador dependente de ordem NÃO DEVE substituir identificador determinístico. [62596f1]

Metadado local DEVE ser associado por conteúdo e relação, não somente por filename; quando normalizado, DEVE usar nome aderente ao acrônimo sem perda. [62596f1]

Compatibilidade com path antigo somente PODE existir para URL pública comprovadamente consumida e DEVE usar redirecionamento, alias ou mapa finito, sem duplicação indefinida; na ausência de consumo publicado comprovado, o path Unicode anterior DEVE ser removido depois da migração validada. [62596f1]

## 42. Migração e downloader

A migração futura DEVE ser executada por script temporário, idempotente, verificável, retomável e removível após aceite. [62596f1]

Antes de mover, o migrador DEVE inventariar bytes, paths, metadados, URLs, hashes, idiomas, autores, tipos, títulos, tags, variantes e colisões. [62596f1]
O migrador DEVE agrupar identidade editorial, preservar título, calcular acrônimo e slug, criar destino, mover correlatos, renomear diretórios e rotas, atualizar referências e validar contagem, bytes e hashes. [62596f1]

Falha NÃO DEVE deixar estado parcial silencioso; checkpoint, temporário, backup e rollback DEVEM preservar recuperação. [62596f1]

`scripts/publications/baixar.py` DEVE possuir RCF específico em `scripts/publications/RCF.md`, subordinado a este RCF; automação operacional e requisitos do coletor NÃO DEVEM integrar `src/` nem o artefato do GitHub Pages. [PENDENTE-CÓDIGO] [62596f1]

O downloader DEVE baixar diretamente na estrutura canônica, reutilizar diretório da mesma identidade, agrupar formatos/assets, normalizar título/tags/acrônimo, derivar o mesmo slug RFC 3986 usado pelo migrador e impedir sobrescrita destrutiva. [62596f1]

O downloader DEVE preservar variante material, produzir destino determinístico, gerar ou atualizar metadados/índices e NÃO DEVE recriar a estrutura legada. [62596f1]

Alteração do downloader DEVE preservar cabeçalho autoral/licença e receber testes de path, colisão, repetição, falha, retomada e metadado. [62596f1]

### 42.1 Escopo de aquisição e identidade

O coletor de `egwwritings.org` DEVE preservar integralmente o suporte a Ellen [62596f1]
G. White e ampliar a descoberta às coleções públicas `Biblioteca dos Pioneiros
Adventistas`, identificada no catálogo observado por `pt/1055`, e `Adventist
Pioneer Library`, identificada por `en/15`.

Coleção NÃO DEVE ser tratada como autor. Identidade de publicação DEVE combinar [62596f1]
identificador remoto estável quando disponível, coleção, autor, idioma, tipo,
título editorial, edição/versão e origem; obra homônima de autor ou edição
distintos NÃO DEVE ser fundida. [62596f1]

O catálogo público estruturado consumido pela aplicação DEVE ser preferido a [62596f1]
parsing visual. Lista fixa de autores, tipos ou obras somente PODE atuar como [62596f1]
fixture de teste ou fallback finito versionado e NÃO DEVE declarar coleção [62596f1]
completa.

Somente conteúdo editorial em `pt-BR` e `en` PODE ser incorporado. Alias [62596f1]
`pt`, `pt_BR` ou equivalente comprovado DEVE projetar-se em `pt-BR`; alias [62596f1]
inglês sem variante material DEVE projetar-se em `en`. Valor original e valor [62596f1]
normalizado DEVEM permanecer registrados, e variante material NÃO DEVE ser [62596f1]
fundida por alias.

O segmento de path DEVE continuar ASCII/minúsculo: `pt-BR` projeta-se como [62596f1]
`pt-br` e `en` como `en`. O acervo legado `en-us` DEVE ser reconhecido como [62596f1]
alias local durante a transição e migrado atomicamente para `en` somente após
prova de ausência de variante material, sem download ou grupo duplicado.

Cada autor DEVE receber chave autoral determinística na estrutura canônica [62596f1]
global; o diretório do coletor sob `egw` identifica o provedor/adaptador e NÃO
autoriza armazenar autores pioneiros como se fossem Ellen G. White.

### 42.2 Elegibilidade e precedência de formatos

Para uma edição elegível, a precedência DEVE ser EPUB nativo, PDF nativo e, [62596f1]
somente quando nenhum dos dois existir, conteúdo textual oficial de leitura
on-line.

Quando EPUB e PDF nativos existirem, ambos DEVEM ser preservados no mesmo grupo [62596f1]
editorial. Áudio, vídeo, imagem isolada, bundle, HTML bruto, interface e
artefato não editorial NÃO DEVEM ser incorporados. [62596f1]

Ausência de download nativo NÃO autoriza extração por si só. Conteúdo textual
somente PODE ser adquirido quando for público sem contorno, possuir identidade, [62596f1]
ordem e completude verificáveis e permitir separação determinística entre corpo
editorial e aplicação.

### 42.3 Preflight incremental e idempotência

Antes de descobrir novamente uma unidade conhecida, solicitar ativo, extrair,
converter ou reindexar, o coletor DEVE executar preflight progressivo por: [62596f1]

1. ledger/índice local e estado da publicação;
2. identificador remoto e metadados persistidos;
3. existência, formato e tamanho do arquivo canônico;
4. ETag, `Last-Modified`, tamanho ou hash remoto quando disponíveis;
5. SHA-256 local somente quando a evidência anterior não concluir;
6. requisição condicionada ou download somente como último nível.

Publicação concluída, íntegra e coerente com índice/metadado DEVE resultar em [62596f1]
`skipped`, sem request do ativo, conversão, extração, regravação, alteração de
timestamp ou recálculo desnecessário.

Nome ou existência isolada NÃO comprovam conclusão. Temporário, parcial,
assinatura inválida, hash divergente, metadado incoerente ou índice ausente
DEVE resultar em estado incompleto, corrompido ou revisão, nunca em sucesso. [62596f1]

Atualização somente DEVE ocorrer por evidência material: hash, edição/versão, [62596f1]
novo ativo associado, correção remota, metadado editorial relevante ou arquivo
local ausente/inválido. Versão anterior e nova DEVEM manter relação e evidência [62596f1]
sem sobrescrita destrutiva.

### 42.4 Estado, metadados e retomada

O ledger incremental DEVE distinguir `pending`, `processing`, `completed`, [62596f1]
`skipped`, `incomplete`, `corrupt`, `unavailable`, `ineligible`,
`temporary_failure`, `permanent_failure` e `review_required`.

Estado de execução, cache e validadores HTTP DEVEM residir fora de [62596f1]
`formative_data` e não obrigar alteração de arquivo rastreado em reexecução
sem mudança material. Metadado canônico DEVE registrar coleção, identidade [62596f1]
remota/local, autor, títulos original/normalizado, idiomas original/canônico,
tipo, edição, URL pública, fontes por ativo/segmento, formato, método, data,
tamanho, hashes, ordem, completude, ressalvas e relações de derivação.

Metadado legado DEVE permanecer legível. Escrita nova ou atualização material [62596f1]
DEVE usar schema versionado posterior, determinístico, fechado e migrável; dado [62596f1]
original NÃO DEVE ser perdido quando divergir de normalização. [62596f1]

Execução interrompida DEVE preservar ativos promovidos e estado confirmado. [62596f1]
`processing` abandonado DEVE ser retomado como unidade incompleta após validar [62596f1]
temporários; parcial nunca DEVE ser promovido ou indexado como concluído. [62596f1]

A execução DEVE persistir atomicamente checkpoint de escopo compatível com coleção, filtro e limite, contendo catálogo normalizado, enriquecimentos já comprovados e identidades cujo processamento terminou em estado confirmado. [62596f1]
Nova invocação do mesmo escopo DEVE retomar automaticamente o primeiro enriquecimento ou item ainda não confirmado, sem consultar novamente páginas, capas, textos ou ativos já preservados pelo checkpoint. [62596f1]
Cada publicação cujo enriquecimento esteja completo DEVE ser processada, validada e promovida imediatamente após a persistência do próprio checkpoint, sem aguardar o enriquecimento integral da coleção; publicação posterior incompleta, bloqueada ou interrompida NÃO PODE impedir a materialização nem desfazer a confirmação das anteriores. [62596f1]
Interrupção por sinal, encerramento do processo, contenção ou falha transitória NÃO DEVE apagar nem avançar o checkpoint além da última transição confirmada. [62596f1]
Checkpoint ausente inicia nova execução; checkpoint incompatível, ambíguo ou corrompido DEVE bloquear com diagnóstico e NÃO PODE provocar reinício silencioso. [62596f1]
Reinício somente PODE ocorrer por opção explícita `--restart`, limitada ao escopo selecionado; essa opção DEVE descartar apenas checkpoints de runtime aplicáveis, nunca publicação canônica já promovida. [62596f1]
`--revalidate` NÃO equivale a reinício e DEVE preservar a posição retomável, alterando somente a política de validação remota dos itens ainda pendentes. [62596f1]
Checkpoint de coleção concluída sem falha DEVE ser removido atomicamente, pois a próxima invocação constitui nova execução e precisa observar novamente o catálogo vigente. [62596f1]

### 42.5 Acesso responsável e contenção

O cliente DEVE ser sequencial por padrão, com concorrência `1`, atraso base [62596f1]
configurável de no mínimo dois segundos entre requests e jitter moderado
positivo. Aumento até concorrência `2` somente PODE ocorrer por configuração [62596f1]
explícita e evidência de que a origem o tolera; valor superior é proibido. [62596f1]

Timeout, limite de bytes, sessão reutilizável, cache, deduplicação de request,
`User-Agent` identificável, número máximo de três tentativas e backoff
exponencial limitado DEVEM ser configuráveis e observáveis. [62596f1]

Resposta `429` DEVE respeitar `Retry-After`; `408` e `5xx` PODEM repetir dentro [62596f1]
do limite. [3301a97] Quando a descoberta ou etapa remota exigir navegador, o coletor DEVE [62596f1]
usar preferencialmente uma única instância visível, perfil persistente local
segregado e uma única guia operacional reutilizada entre coleções e páginas,
com `workers=1` enquanto essa guia for necessária. Nova guia, sessão ou perfil
somente PODE ocorrer por fechamento, invalidação, corrupção comprovada ou [62596f1]
recuperação controlada, sempre com motivo registrado. [PENDENTE-CÓDIGO]

CAPTCHA, página de desafio, verificação de navegador, bloqueio temporário,
`403`, `429`, redirecionamento de validação, alteração de título/URL/DOM ou
ausência do conteúdo esperado somente DEVEM ser classificados como verificação [62596f1]
humana quando houver evidência suficiente e não por indisponibilidade comum
isolada. Diante de verificação legitimamente interativa, o coletor DEVE pausar [62596f1]
a unidade dependente, manter a guia aberta, suspender intensificação de acesso,
informar instrução objetiva ao usuário, aguardar em baixa frequência e retomar
automaticamente após validar que o conteúdo esperado voltou. [PENDENTE-CÓDIGO]

`403`, CAPTCHA, desafio anti-automação, bloqueio, limitação persistente ou
contrato inesperado que não puderem ser liberados de forma legítima pela guia
visível DEVEM interromper a unidade ou coleção afetada, preservando progresso, [62596f1]
sem evasão, proxy, rotação de identidade, solução automática de CAPTCHA,
simulação humana ou tentativa de ocultar o cliente. [PENDENTE-CÓDIGO]

Progresso concluído DEVE ser preservado e o diagnóstico DEVE registrar taxa, [62596f1]
tentativa, espera, status e escopo bloqueado sem segredo ou payload editorial
desnecessário.

### 42.6 Extração editorial e derivados

Extração textual DEVE obter somente título, autoria e corpo editorial legítimo: [62596f1]
prefácio, introdução, capítulos, seções, parágrafos, notas, citações, listas,
tabelas textuais, epígrafes e referências.

Menus, cabeçalhos/rodapés da aplicação, breadcrumbs, controles, recomendações,
resultados relacionados, publicidade, telemetria, scripts, estilos, mensagens
de interface, duplicações de renderização e conteúdo de outra publicação DEVEM [62596f1]
ser excluídos.

Cada segmento DEVE preservar identificador, URL, posição e hash; sequência [62596f1]
DEVE validar primeiro/último segmento, quantidade declarada/obtida, lacunas, [62596f1]
duplicações e ordem. Incerteza ou lacuna DEVE impedir `completed` e exigir [62596f1]
`review_required`.

Fonte textual completa DEVE ser persistida como Markdown UTF-8 estruturado, [62596f1]
numerado pela ordem editorial e acompanhado de metadado. Conversão posterior
DEVE seguir `fonte estruturada -> Markdown normalizado -> EPUB validado` sem [62596f1]
nova coleta.

EPUB gerado DEVE possuir sumário, metadados, idioma, autor, título, capítulos, [62596f1]
notas, ordem e proveniência e passar validação EPUB. Ele DEVE ser identificado [62596f1]
como derivado local da edição on-line, nunca como EPUB nativo nem como URL/hash
original em `formative_data`.

Transformação NÃO DEVE corrigir, resumir, modernizar, traduzir ou reescrever o [62596f1]
texto. Sanitização DEVE impedir execução/injeção e preservar Unicode e conteúdo [62596f1]
editorial, registrando transformação potencialmente material.

### 42.7 Descoberta técnica limitada

Inspeção PODE observar rede do navegador, contratos públicos, JavaScript [62596f1]
entregue ao cliente e chamadas legítimas de leitura. NÃO PODE acessar endpoint [62596f1]
privado, obter credencial/token alheio, explorar vulnerabilidade, modificar o
serviço, contornar proteção ou executar varredura agressiva.

Bundle temporário somente PODE existir durante análise rastreada e DEVE ser [62596f1]
removido quando sua função se esgotar. Implementação DEVE acoplar-se a contrato [62596f1]
de dados observável, com fixture, e NÃO a detalhe minificado frágil quando
houver alternativa.

### 42.8 Segurança, testes e gate de coleta

Toda entrada remota DEVE ser não confiável: esquema/host/path, DNS/IP, [62596f1]
redirecionamento, tamanho, MIME, assinatura, arquivo compactado, nome e destino
DEVEM cumprir as guardas das §§41 e 44.6-44.7. Escrita DEVE usar temporário [62596f1]
segregado, hash durante streaming e promoção atômica; conteúdo obtido nunca
DEVE ser executado. [62596f1]

Testes offline DEVEM comprovar skip sem request, parcial, corrupção, [62596f1]
deduplicação, colisão, atualização real, idiomas, formatos, multiautor,
coleções, extração ordenada, exclusão da interface, lacunas, Markdown, EPUB,
original/derivado, `Retry-After`, backoff, limite, parada por bloqueio,
retomada, path hostil e coerência de índice.

Fixture/mock DEVE preceder amostra pública mínima. Coleta ampliada somente PODE [62596f1]
ocorrer após os gates de descoberta, elegibilidade, idempotência, fidelidade,
contenção e integridade e mediante autorização material própria; a conclusão
normativa ou da amostra NÃO autoriza download em massa.

### 42.9 Raiz única de estado de runtime

Todo estado mutável não canônico da cadeia de publicações DEVE convergir para [PENDENTE-CÓDIGO] [62596f1]
uma raiz local única, configurável e resolvida pela raiz do repositório,
denominada `runtime_state_root`. Ela DEVE permanecer fora de `src/`, `scripts/`, [PENDENTE-CÓDIGO] [62596f1]
`dist/`, artefatos públicos e releases, ser integralmente ignorada pelo Git e
ser removível sem perda de publicação, configuração, schema ou fixture. [PENDENTE-CÓDIGO]

São runtime: cache, ledger, checkpoint, sessão, perfil de navegador, cookie,
storage, autenticação transitória, ambiente de linguagem, lock, PID, socket,
temporário, parcial, trace, screenshot, dump, log e relatório efêmero. PDF,
EPUB, Markdown editorial, metadado de proveniência e índice validados são
canônicos quando pertencem à publicação concluída e NÃO DEVEM ser ocultados por [PENDENTE-CÓDIGO] [62596f1]
padrão de ignore amplo. [PENDENTE-CÓDIGO]

Cada subdiretório DEVE declarar classe, produtor, consumidor, persistência, [PENDENTE-CÓDIGO] [62596f1]
isolamento, retenção, limite, expiração, invalidação e limpeza. Estado sensível
DEVE ser isolado por domínio, perfil, usuário e finalidade, usar permissões [PENDENTE-CÓDIGO] [62596f1]
mínimas, nunca integrar log e ser invalidado em expiração, corrupção ou troca
de identidade. Cache DEVE tolerar ausência e corrupção; temporário e lock DEVEM [PENDENTE-CÓDIGO] [62596f1]
ter criação sem colisão e limpeza limitada à raiz validada, sem atingir processo
ativo ou execução concorrente. [PENDENTE-CÓDIGO]

Configuração DEVE derivar os paths de runtime da raiz única e admitir override [PENDENTE-CÓDIGO] [62596f1]
explícito seguro. Caminho legado PODE ser migrado uma única vez, de forma [PENDENTE-CÓDIGO] [62596f1]
idempotente e retomável, somente quando seu conteúdo e proprietário forem
comprovados; produtores e consumidores DEVEM convergir no mesmo ciclo e o [PENDENTE-CÓDIGO] [62596f1]
fallback legado DEVE ser removido após validação. Clone limpo, CI e execução [PENDENTE-CÓDIGO] [62596f1]
offline NÃO DEVEM depender de estado preexistente. [PENDENTE-CÓDIGO] [62596f1]
Validação DEVE inspecionar índice e histórico corrente sem reescrevê-lo, [PENDENTE-CÓDIGO] [62596f1]
rejeitar runtime rastreado ou empacotado, comprovar `.gitignore` cirúrgico e
garantir que limpeza, build, bundle e release não incluam sessão, perfil,
cache, temporário, lock, trace ou segredo. Remoção de runtime já rastreado DEVE [PENDENTE-CÓDIGO] [62596f1]
ocorrer apenas do índice, preservando localmente o que ainda for necessário e
sem reescrever histórico compartilhado sem autorização própria. [PENDENTE-CÓDIGO]

### 42.10 Suspensão e handoff humano diante de desafio

Detecção de challenge page, CAPTCHA, intersticial, bloqueio por automação,
loop de redirecionamento ou estado incompatível DEVE combinar URL, título, [PENDENTE-CÓDIGO] [62596f1]
conteúdo esperado, resposta e transições; indisponibilidade isolada NÃO comprova
desafio. A detecção NÃO DEVE clicar, preencher, recarregar nem tentar resolver [PENDENTE-CÓDIGO] [62596f1]
o mecanismo. [PENDENTE-CÓDIGO]

Ao detectar desafio, a máquina de estados DEVE entrar em [PENDENTE-CÓDIGO] [62596f1]
`aguardando_intervencao_humana`, cessar integralmente automação, polling do DOM,
timers, filas, scripts, cliques, recargas e navegações e impedir atuação
simultânea do controlador e do operador. O operador DEVE poder cancelar, e [PENDENTE-CÓDIGO] [62596f1]
nenhum timeout curto PODE reiniciar a página ou invalidar sua ação. Somente um [PENDENTE-CÓDIGO] [62596f1]
monitor externo de baixa frequência, sem interação com a página e com limite
configurável, PODE observar encerramento/cancelamento da etapa humana. [PENDENTE-CÓDIGO] [62596f1]
[PENDENTE-CÓDIGO]

Em domínio de terceiro, a ordem de preferência é API, autenticação, feed,
exportação ou integração oficial; na falta, o handoff DEVE usar navegador normal [PENDENTE-CÓDIGO] [62596f1]
operado diretamente pelo usuário ou perfil humano autorizado sem automação
ativa. Janela ainda anexada ao WebDriver NÃO constitui handoff humano completo.
O controlador DEVE ser encerrado/desanexado antes da intervenção e somente [PENDENTE-CÓDIGO] [62596f1]
PODERÁ ser recriado depois que a sessão humana terminar, usando o mesmo perfil
apenas quando compatibilidade, escopo, consentimento e proteção forem
comprovados. [PENDENTE-CÓDIGO]

A retomada DEVE validar objetivamente ausência do desafio, origem, página, [PENDENTE-CÓDIGO] [62596f1]
conteúdo esperado, identidade e inexistência de loop. Clique humano isolado não
comprova liberação. Recusa, expiração, novo desafio ou estado incompatível DEVE [PENDENTE-CÓDIGO] [62596f1]
manter a unidade suspensa ou encerrá-la como `review_required`, com progresso
preservado e tentativas finitas. [PENDENTE-CÓDIGO]

Falso positivo NÃO autoriza stealth, spoofing, proxy, rotação de identidade,
mascaramento de WebDriver, solução automática de CAPTCHA, cópia incompatível de
cookie/token/storage ou qualquer bypass. Exceção em domínio próprio somente
PODE usar mecanismo oficial, mínimo, auditável, revogável e restrito, como [PENDENTE-CÓDIGO] [62596f1]
identidade de serviço ou ambiente de automação dedicado. [PENDENTE-CÓDIGO]

Log DEVE registrar somente transições, origem sanitizada, tipo provável, [PENDENTE-CÓDIGO] [62596f1]
início/fim/método do handoff, validação e motivo final; senha, resposta de
CAPTCHA, cookie, token, cabeçalho de autenticação, storage e dado pessoal
reutilizável são proibidos. Testes DEVEM usar fixture, mock ou domínio próprio e [PENDENTE-CÓDIGO] [62596f1]
cobrir suspensão total, cancelamento, aceitação, recusa, expiração,
reapresentação, isolamento e ausência de segredo. [PENDENTE-CÓDIGO]

### 42.11 Unidade transacional e commit por publicação

Uma publicação somente PODE atingir `completa_e_pareada` quando todos os [PENDENTE-CÓDIGO] [62596f1]
ativos obrigatórios terminaram, não há parcial, formato/tamanho/hash são [PENDENTE-CÓDIGO] [62596f1]
válidos, identidade e metadado são inequívocos, assets e referências existem,
duplicidades/colisões foram tratadas e índices locais/globais refletem uma única
entrada final. HTTP de sucesso, existência ou stream encerrado isoladamente não
comprovam conclusão. Ambiguidade material exige `review_required`.
[PENDENTE-CÓDIGO]

Download, promoção, metadado, derivados, índice e eventual commit DEVEM formar [PENDENTE-CÓDIGO] [62596f1]
uma transação lógica por publicação. Falha DEVE remover ou isolar preparatórios, [PENDENTE-CÓDIGO] [62596f1]
restaurar índice anterior, manter runtime retomável e impedir commit. Reexecução
inalterada DEVE resultar em `skipped` sem commit, timestamp ou derivado [PENDENTE-CÓDIGO] [62596f1]
divergente. [PENDENTE-CÓDIGO]

Efeito Git DEVE ser opt-in explícito por execução e somente PODE ocorrer em [PENDENTE-CÓDIGO] [62596f1]
`dev`, em repositório Git validado, sem operação Git concorrente e com identidade
configurada. A allowlist DEVE ser calculada por identidade da publicação e [PENDENTE-CÓDIGO] [62596f1]
derivados globais inevitáveis; `git add .`, `git add -A`, glob aberto ou
inclusão de runtime são proibidos. Alteração alheia permanece fora do índice; [PENDENTE-CÓDIGO] [62596f1]
conflito no mesmo arquivo bloqueia. [PENDENTE-CÓDIGO]

Antes do commit, o coletor DEVE validar novamente os blobs staged, schemas, [PENDENTE-CÓDIGO] [62596f1]
hashes, referências, índice, ausência de segredo/runtime e conteúdo exato da
allowlist. O commit DEVE conter exatamente uma publicação completa e seus [PENDENTE-CÓDIGO] [62596f1]
derivados inevitáveis, possuir mensagem com identificador estável e ter seu
hash confirmado no ledger. Commit vazio, parcial, agrupado, fragmentado ou
recriado após retomada é proibido. [PENDENTE-CÓDIGO] [62596f1]

Downloads distintos PODEM ser concorrentes, mas promoção, índice, staging e [PENDENTE-CÓDIGO] [62596f1]
commit DEVEM ser serializados por lock de runtime. Push é operação separada, [PENDENTE-CÓDIGO] [62596f1]
opt-in, posterior à validação de branch, upstream e sincronização; falha de push
preserva o commit local e nunca o recria. Testes DEVEM cobrir worktree alheia, [PENDENTE-CÓDIGO] [62596f1]
conflito, completude, parcial, índice quebrado, falhas antes/depois do staging,
concorrência, retomada, commit exato e ausência de runtime. [PENDENTE-CÓDIGO]

### 42.12 Completude observável da descoberta e da derivação

O catálogo DEVE ser enumerado até que todos os links únicos de publicação [62596f1]
expostos pela coleção tenham sido coletados. [be82602]
Grade virtualizada ou paginação DEVE ser colhida incrementalmente; inspecionar [62596f1]
somente o DOM final depois da rolagem NÃO comprova completude. [be82602]
A execução DEVE registrar contagem observada, [62596f1]
identidades únicas e critério objetivo de término. [be82602]

Cada publicação ainda ausente, incompleta, inválida ou sujeita a revalidação
explícita DEVE ser enriquecida pela sua página individual. [62596f1]
Todos os links habilitados de PDF e EPUB ali expostos DEVEM integrar o conjunto [62596f1]
obrigatório; link ausente no cartão, botão desabilitado ou `href="#"` NÃO [62596f1]
constitui ativo. [be82602]
Falha em descobrir, baixar ou validar qualquer ativo habilitado impede
`completed`. [be82602]

Imediatamente depois de enumerar e normalizar o catálogo, mas antes de abrir a página individual, percorrer leitura, consultar capa ou acessar ativo, o coletor DEVE confrontar o identificador remoto com as publicações locais `completed`. [62596f1]
A dispensa de rede específica da obra somente PODE ocorrer quando identidade, metadado, conjunto de fontes e derivados, tamanhos, assinaturas, hashes, segmentos reversíveis, EPUB e capa aplicável forem integralmente verificados; qualquer ausência, divergência, ambiguidade ou arquivo não canônico exige o fluxo remoto normal. [62596f1]
Essa verificação DEVE abranger a publicação inteira, inclusive todos os PDF e EPUB registrados, `cover.png`, metadados e derivados, e registrar `skipped` sem alterar seus bytes. [62596f1]
O catálogo da coleção PODE ser acessado uma vez para conhecer o conjunto vigente, mas uma publicação local válida NÃO DEVE provocar requisição de sua página, texto, capa, PDF ou EPUB, salvo opção humana explícita de revalidação. [62596f1]

Metadado legado sem `remote_id` DEVE participar desse preflight por identidade composta exclusivamente de dados já presentes na listagem da coleção — ID/URL pública, título normalizado, autor, categoria, idioma e tipo — e do path canônico ou alias local oficialmente admitido. Havendo PDF e EPUB registrados, íntegros e inequivocamente pareados, a ausência de schema v3 NÃO autoriza abrir a página individual. [62596f1]

Request HTTP específico da publicação somente PODE ser emitido depois de o gate local registrar causa objetiva que a torne necessária: prova ausente ou inconclusiva, divergência, ambiguidade, corrupção, ativo obrigatório ausente ou `--revalidate` explícito. Caminho feliz local completo DEVE possuir teste que falha diante de qualquer chamada de rede. [62596f1]

Checkpoint persistido NÃO PODE substituir o gate vigente: antes de processar cada item ainda não confirmado, o coletor DEVE reaplicar o preflight local atual independentemente do valor histórico de `local_complete`, promover no checkpoint a prova local superveniente e impedir que estado antigo falso libere request. [62596f1]

Quando PDF e EPUB estiverem ambos ausentes, a leitura textual DEVE começar na [62596f1]
URL oficial declarada pela obra e seguir a navegação editorial `rel=next` até o
término declarado. [be82602]
A cadeia DEVE ser acíclica, permanecer na mesma obra, possuir [62596f1]
anterior/próximo coerentes — considerando equivalentes a rota da página e a
rota do primeiro bloco editorial comprovado da mesma página — e preservar todos os blocos editoriais identificados
no contêiner de leitura, inclusive headings, parágrafos, listas, tabelas, notas,
ênfases, links e quebras semanticamente materiais. [be82602]

O hash e o estado de cada unidade DEVEM derivar do conteúdo editorial real [62596f1]
normalizado sem controles da interface. [be82602]
Cadeia interrompida, vazia, repetida, divergente do sumário ou cuja obra mude
no percurso DEVE resultar em [62596f1]
`review_required`, nunca em EPUB parcial. [be82602]

Fixture e mock DEVEM usar raiz temporária explícita ou raiz de saída de teste [62596f1]
segregada. [be82602]
A CLI NÃO DEVE materializar fixture em `src/publications`, mesmo quando [62596f1]
`source_root` canônico estiver configurado. [be82602]
Artefato sintético detectado na raiz canônica DEVE ser isolado como [62596f1]
runtime/quarentena, sem publicação ou
commit. [be82602]

Aceite DEVE comparar: quantidade de obras no catálogo e identidades coletadas; [62596f1]
ativos habilitados e arquivos incorporados; cadeia editorial observada e
segmentos persistidos; e conteúdo real renderizado do EPUB derivado. [be82602]
Amostra pública controlada DEVE abranger uma obra com ativos nativos e uma sem eles, [62596f1]
sem autorizar coleta em massa. [be82602]

Para obra sem PDF/EPUB nativo, a capa declarada pela ficha pública oficial da mesma obra, inclusive `og:image`, DEVE ser adquirida como fonte editorial e NÃO PODE ser substituída por imagem inferida por título, semelhança ou posição. [62596f1]
A imagem validada DEVE originar o `cover.png` canônico e integrar o EPUB derivado como `cover-image`; eventual PDF derivado DEVE reutilizar a mesma capa como sua página de capa, sem rasterizar o restante do texto. [62596f1]
Falha de aquisição, decodificação, normalização ou incorporação de uma capa oficialmente declarada DEVE impedir `completed`, exceto quando o endpoint oficial responder conclusivamente `404` em documento estruturado com `detail="Cover not found"`. [62596f1]
Somente nessa ausência oficial comprovada o coletor DEVE gerar `cover.png` técnico determinístico, identificá-lo visualmente como capa técnica não editorial, usar apenas identidade e título comprovados da própria obra e registrar URL, status, detalhe, instante de acesso e método da derivação; timeout, contenção, `403`, `5xx`, HTML, resposta vazia ou outro `404` NÃO autorizam o fallback. [62596f1]
A capa técnica NÃO PODE reutilizar imagem de outra edição, inferir arte por semelhança nem integrar o texto editorial/indexável. [62596f1]
A página de capa DEVE ser o primeiro e exclusivo item visual do EPUB, sem margens, faixas ou texto, preenchendo toda a viewport de borda a borda; diferença de proporção DEVE preservar a imagem por escala proporcional com recorte central, nunca por deformação. [62596f1]

O EPUB textual derivado DEVE manter XHTML semântico no spine para indexação e empacotar, fora do spine, os bytes Markdown intermediários com nomes, ordem, hashes e manifesto versionado que permitam restauração exata. [62596f1]
Todo XHTML editorial gerado DEVE ser XML bem-formado e livre de caractere de controle ou marcador interno do conversor; a validação DEVE rejeitar o EPUB antes da promoção quando qualquer seção não puder ser integralmente analisada por parser XML. [62596f1]
Os arquivos `.md` externos somente PODEM ser removidos depois de EPUB validado e teste de reversão byte a byte; falha de manifesto, hash ou restauração DEVE preservar os intermediários e impedir `completed`. [62596f1]
Uma página inicial de proveniência, imediatamente após a capa e antes do sumário, DEVE declarar-se “Nota de proveniência (não editorial)” e registrar autor, título, plataforma, URL oficial clicável e data de acesso em referência de estilo ABNT, sem contaminar o conteúdo editorial nem a fonte Markdown reversível. [62596f1]
Depois da proveniência e do sumário, cada seção de conteúdo DEVE declarar cabeçalho corrente contextual e rodapé com contador de página por caixas de margem paginada, fora do corpo XHTML indexável; a primeira página de capítulo, seção ou unidade equivalente DEVE suprimir o cabeçalho, mas preservar a numeração no rodapé. [62596f1]
## 43. Índice global

Um índice JSON global DEVE representar todas as publicações e ser gerado deterministicamente por uma única fonte ou etapa canônica. [62596f1]

Copias do índice em `dist/` quando aplicável, no artefato do Pages e na raiz pública das publicações DEVEM ser projeções idênticas, nunca editadas manualmente. [62596f1]

O envelope global DEVE declarar `schema_version`, identidade da geração, versão do gerador, configuração causal e lista `publications`. [62596f1]

Cada item global DEVE declarar identidade estável, título normalizado, slug de rota, autor ou chave autoral, idioma, tipo, acrônimo, tags, URLs públicas diretas, proveniência local, capa e `formative_data`. [62596f1]

`formative_data` DEVE ser exatamente um documento conforme a `NORMA-IF-SIL-001`, com raiz fechada `book`, `urls` e `global_hashes`. [62596f1]

Metadados locais de cada publicação DEVEM ser a entrada prioritária do índice, sem impedir confrontação com o conteúdo editorial e outras evidências. [62596f1]

CONTRADIÇÃO DETECTADA: restrição intermediária a `book` + `global_hashes` vs anexo final `NORMA-IF-SIL-001` com `book` + `urls` + `global_hashes` - Aplicando o anexo final, expresso e mais específico.

URL pública direta e URL original DEVEM permanecer semanticamente distintas no envelope; URL original candidata integra `formative_data.urls`, enquanto URL pública do artefato integra o campo externo de publicação. [62596f1]

`urls` do documento formativo NÃO DEVE ser copiado para a raiz de `metadata.json` schema 5 nem interpretado como endereço local de asset. [62596f1]

Índice DEVE ser ordenado deterministicamente por título normalizado e desempates declarados; URLs DEVEM seguir prioridade de formato e fonte. [62596f1]

Gerador DEVE rejeitar URL repetida, formato duplicado, path equivalente por caixa/codificação/barra e fusão de títulos sem identidade editorial comprovada. [62596f1]

Alteração de publicação DEVE regenerar item, hashes, capa, índice e artefato dependente sem reprocessar grupo independente quando isso for seguro. [62596f1]

### 43.1 Geração incremental e multilocalizada

Uma única capacidade canônica DEVE gerar o índice integral e atualizar um item específico; CLI, downloader e eventual workflow DEVEM invocar essa capacidade por parâmetro/gatilho declarado, sem manter serializadores paralelos. [62596f1]

O índice canônico DEVE residir na raiz pública das publicações, usar paths URI relativos e projetar idioma, categoria, autor, tipo e título de forma suficiente para consumidores multilocalizados, sem traduzir título, nome ou crédito editorial. [62596f1]

Cada entrada DEVE registrar identidade remota e local, metadados editoriais, URL da ficha oficial, URLs públicas dos ativos e derivados, capa, manifesto de análise, tamanho e SHA-1/SHA-256/SHA-512 dos EPUB/PDF efetivamente publicados. [62596f1]

`formative_data` somente DEVE ser emitido quando ao menos um PDF/EPUB editorial original possuir URL de aquisição válida e matriz integral comprovada conforme `NORMA-IF-SIL-001`; publicação exclusivamente textual com EPUB local derivado DEVE declarar estado formativo `not-applicable-local-derivation`, sem fabricar URL ou promover derivado a original. [62596f1]

Na primeira atualização incremental, índice ausente ou incompatível DEVE ser reconstruído do corpus local; nas seguintes, somente o item afetado PODE ser substituído se a integridade e a cobertura do envelope forem preservadas. [62596f1]

A escrita DEVE ser atômica e determinística. Identidade, configuração e fingerprint das entradas DEVEM integrar a geração; relógio, ordem de varredura, cwd e estado de rede NÃO PODEM alterar bytes para o mesmo corpus. [62596f1]

### 43.2 Manifesto de análise de chunking

Cada EPUB/PDF incorporado ou gerado DEVE possuir manifesto derivado próprio, identificado pelo path e hashes integrais do ativo, contendo somente observações, experimentos, métricas, provas e decisões específicas daquele recurso; descrição, benefício, risco, parâmetro genérico, justificativa didática e hipótese ainda não executada pertencem ao catálogo normativo global e NÃO DEVEM ser repetidos no manifesto. [62596f1]

O manifesto DEVE referenciar por ID, versão e hash o catálogo global e a base agregada de aprendizado, registrar exatamente os parâmetros executados e omitir de sua lista de resultados qualquer método não executado; contagens globais PODEM permanecer somente na base agregada, sem texto editorial. [62596f1]

Hipótese documentada, prática difundida, disponibilidade de biblioteca, tipo declarado da publicação, correlação do corpus ou resultado de outro ativo NÃO DEVEM produzir recomendação; recomendação por recurso exige experimento local `passed`, prova reprodutível e critérios integrais aprovados no próprio ativo. [62596f1]

EPUB DEVE ser lido como ZIP OCF não confiável, com limites e paths seguros, respeitando `container.xml`, pacote, manifesto, spine, `nav`, NCX, landmarks, page list, XHTML, headings e fonte Markdown reversível quando presente. PDF DEVE ser analisado sem modificar o original, preferindo parser mantido capaz de obter páginas, texto e metadados, com fallback estrutural explicitamente diagnosticado. [62596f1]

O analisador DEVE construir referência canônica normalizada a partir da ordem editorial efetivamente extraída, detectar ruído de cabeçalho, rodapé e paginação somente por repetição posicional mensurável e testar reconstrução de frases e parágrafos que atravessem páginas; nenhum texto da referência ou dos chunks DEVE ser persistido no manifesto. [62596f1]

Cada experimento DEVE executar o segmentador real sobre a referência do recurso e medir ao menos cobertura, ordem, perda, duplicação, contaminação, precisão de fronteira, recuperação de fronteira e continuidade entre páginas, armazenando contagens, proporções em ppm e hashes de prova; métrica inaplicável DEVE ser `null` com código causal, nunca pontuação inventada. [62596f1]

Resultado DEVE ser `passed`, `rejected` ou `inconclusive`; `passed` exige reconstrução normalizada integral, sem perda, duplicação indevida ou ruído comprovado, fronteiras compatíveis com a unidade alegada e cobertura experimental declarada, enquanto amostragem parcial ou camada textual insuficiente NÃO PODEM fundamentar recomendação integral do ativo. [62596f1]

O analisador DEVE produzir fingerprint de formato/estrutura e atualizar uma base global deduplicada a partir de manifestos válidos do corpus completo, ainda quando o alvo for um arquivo, uma publicação ou uma subárvore; a base agrega somente assinaturas, versões, parâmetros testados, estados e distribuições métricas, e NÃO PODE copiar conteúdo, transformar correlação em verdade nem modificar metadado editorial. [62596f1]

Invocação DEVE aceitar exatamente um escopo entre ativo, publicação, diretório/subárvore e corpus integral. O resultado por ativo DEVE ser idempotente, versionado, explicável e invalidado quando bytes, parser, algoritmo, configuração ou sinais causais mudarem. [62596f1]

O downloader DEVE executar sincronicamente a análise de todos os EPUB/PDF da unidade e a atualização compartilhada do índice depois de validar/promover os ativos e antes de confirmar o checkpoint; falha preserva a publicação material, impede confirmação e permite retomada estritamente local sem nova requisição à origem. [62596f1]

### 43.2.1 Catálogo global de hipóteses experimentais

O catálogo fechado desta versão DEVE manter como hipóteses separadas, nunca como soluções presumidas: janela fixa por caractere/token; separadores recursivos; regex estrutural inferida ou declarada; sentença e janela de sentenças; parágrafo; página/layout; seção hierárquica, capítulo e tópico; unidade editorial específica, incluindo dia de meditação e artigo de periódico; coesão semântica ou lexical; mudança de tópico; meta-chunking por perplexidade/lógica; proposição ou unidade atômica; segmentação variável assistida por LLM; múltiplas granularidades/mixture of chunkers; late chunking; recuperação sem chunking; e documento inteiro como controle. [62596f1]

Janela fixa, separadores recursivos, sentença, parágrafo e chunking semântico DEVEM ser tratados como baselines comparáveis cuja eficiência e qualidade variam por corpus e configuração, conforme avaliação RAG multifatorial de Wang et al.[^chunk-rag-best-practices] [62596f1]

Seção hierárquica, capítulo, tópico, dia, artigo e demais unidades editoriais DEVEM ser hipóteses estruturais testadas contra fronteiras extraídas; MC-indexing reporta ganhos de recuperação ao respeitar estrutura em documentos longos, sem autorizar extrapolação automática para este acervo.[^chunk-mc-indexing] [62596f1]

Regex estrutural DEVE ser executável, limitada e aferida como qualquer outro segmentador; MoC demonstra geração de expressões regulares e avaliação por Boundary Clarity e Chunk Stickiness, mas também evidência que regras e semântica isoladas têm limitações contextuais.[^chunk-moc] [62596f1]

Coesão lexical/semântica e mudança de tópico DEVEM permanecer opcionais e dependentes de modelo/versionamento; CoNLL 2024 avalia coesão por palavras-chave com Pk e WindowDiff, enquanto Meta-Chunking avalia fronteiras lógicas por perplexidade e fusão dinâmica.[^chunk-cohesion][^chunk-meta] [62596f1]

Segmentação variável assistida por LLM DEVE ser hipótese de custo e privacidade maiores, executada somente por opt-in e dados previamente minimizados; LumberChunker encontrou ganho em narrativas longas, domínio que NÃO DEVE ser presumido equivalente a livros, periódicos ou meditações deste corpus.[^chunk-lumber] [62596f1]

Proposição/unidade atômica DEVE ser avaliada quanto a fidelidade, autocontenção e custo de reescrita, pois Dense X Retrieval encontrou vantagem de granularidade fina em recuperação e QA sob orçamento específico, sem provar universalidade documental.[^chunk-dense-x] [62596f1]

Múltiplas granularidades e misturas DEVEM poder conservar resultados paralelos por tipo de consulta; MoG e MoC apresentam roteamento/combinação experimental, não um tamanho único universal.[^chunk-mog][^chunk-moc] [62596f1]
Late chunking DEVE ser considerado somente quando existir embedding de contexto longo compatível, pois aplica pooling após contextualização e sua validade depende do modelo e da janela efetivamente usados.[^chunk-late] [62596f1]
Recuperação sem chunking e documento inteiro DEVEM integrar controles negativos/alternativos quando o runtime suportar contexto e decodificação correspondentes; CFIC relata recuperação de evidência sem segmentação convencional, mas requer arquitetura própria e NÃO substitui ensaio local.[^chunk-cfic] [62596f1]

Página/layout DEVE distinguir paginação autoritativa de quebra física e reconstruir continuidade antes de segmentar; Docling e OmniDocBench demonstram a relevância de layout, ordem de leitura e avaliação por tipos documentais diversos, sem tornar parser visual obrigatório para PDF com camada textual suficiente.[^chunk-docling][^chunk-omnidoc] [62596f1]

Método dependente de embedding, LLM, API ou modelo local somente PODE ser executado quando dependência, versão, licença, custo, privacidade, determinismo e limite estiverem declarados; antes de qualquer inferência, a entrada DEVE ser normalizada, deduplicada, condensada em sinais/fronteiras e minimizada quanto a tokens e conteúdo, e o caminho offline determinístico DEVE permanecer funcional. [62596f1]

### 43.2.2 Apresentação experimental e composição de etapas

Analisador, indexador e downloader DEVEM usar uma única camada de apresentação humana baseada em Rich ou equivalente mantido, com tabelas compactas, cor sem significado exclusivo, fallback sem ANSI e preservação da saída de máquina determinística. [62596f1]

A camada DEVE calcular previamente largura útil limitada, impedir wrap acidental de células variáveis e truncar path/título de forma determinística preservando prefixo identificador e basename/sufixo; terminal estreito DEVE reduzir colunas secundárias antes de quebrar linhas. [62596f1]

Cada ativo analisado DEVE produzir uma tabela curta que compare somente experimentos executados por método, exibindo estado, quantidade de chunks, tempo/eficiência, acerto, erro e códigos causais relevantes; métricas integrais permanecem no manifesto e NÃO DEVEM inundar o console. [62596f1]

Cada publicação iterada DEVE possuir identidade visual inequívoca e ser separada da seguinte por duas linhas em branco ou separador equivalente consistente; progresso interno NÃO DEVE apagar, reescrever ou misturar publicação anterior. [62596f1]

Execução isolada DEVE emitir título de etapa, corpo e resumo suficientes; composição pelo downloader DEVE compartilhar o mesmo contexto visual, manter limites explícitos de análise e indexação e suprimir cabeçalhos, separadores e resumos equivalentes já apresentados pelo pai. [62596f1]

[^chunk-rag-best-practices]: Wang et al. *Searching for Best Practices in Retrieval-Augmented Generation*. EMNLP 2024. DOI: [10.18653/v1/2024.emnlp-main.981](https://doi.org/10.18653/v1/2024.emnlp-main.981).
[^chunk-mc-indexing]: Dong et al. *MC-indexing: Effective Long Document Retrieval via Multi-view Content-aware Indexing*. Findings of EMNLP 2024. DOI: [10.18653/v1/2024.findings-emnlp.150](https://doi.org/10.18653/v1/2024.findings-emnlp.150).
[^chunk-moc]: Zhao et al. *MoC: Mixtures of Text Chunking Learners for Retrieval-Augmented Generation System*. ACL 2025. DOI: [10.18653/v1/2025.acl-long.258](https://doi.org/10.18653/v1/2025.acl-long.258).
[^chunk-cohesion]: Maraj, Vargas Martin e Makrehchi. *Words That Stick: Using Keyword Cohesion to Improve Text Segmentation*. CoNLL 2024. DOI: [10.18653/v1/2024.conll-1.1](https://doi.org/10.18653/v1/2024.conll-1.1).
[^chunk-meta]: Zhao et al. *Meta-Chunking: Learning Efficient Text Segmentation via Logical Perception*. 2024. [arXiv:2410.12788](https://arxiv.org/abs/2410.12788).
[^chunk-lumber]: Duarte et al. *LumberChunker: Long-Form Narrative Document Segmentation*. Findings of EMNLP 2024. DOI: [10.18653/v1/2024.findings-emnlp.377](https://doi.org/10.18653/v1/2024.findings-emnlp.377).
[^chunk-dense-x]: Chen et al. *Dense X Retrieval: What Retrieval Granularity Should We Use?* EMNLP 2024. DOI: [10.18653/v1/2024.emnlp-main.845](https://doi.org/10.18653/v1/2024.emnlp-main.845).
[^chunk-mog]: Zhong et al. *Mix-of-Granularity: Optimize the Chunking Granularity for Retrieval-Augmented Generation*. COLING 2025. [ACL Anthology](https://aclanthology.org/2025.coling-main.384/).
[^chunk-late]: Günther et al. *Late Chunking: Contextual Chunk Embeddings Using Long-Context Embedding Models*. 2024. [arXiv:2409.04701](https://arxiv.org/abs/2409.04701).
[^chunk-cfic]: Qian et al. *Grounding Language Model with Chunking-Free In-Context Retrieval*. ACL 2024. DOI: [10.18653/v1/2024.acl-long.71](https://doi.org/10.18653/v1/2024.acl-long.71).
[^chunk-docling]: Auer et al. *Docling Technical Report*. 2024. [arXiv:2408.09869](https://arxiv.org/abs/2408.09869).
[^chunk-omnidoc]: Ouyang et al. *OmniDocBench: Benchmarking Diverse PDF Document Parsing with Comprehensive Annotations*. 2024. [arXiv:2412.07626](https://arxiv.org/abs/2412.07626).

## 44. NORMA-IF-SIL-001 - autoridade e estrutura

`NORMA-IF-SIL-001` DEVE reger exclusivamente o documento formativo de sugestão bibliográfica e NÃO DEVE ser interpretada como metadado canônico integral, envelope global, contrato de capa, asset, rota, publicação ou autorização de aquisição. [62596f1]

O documento DEVE ser semanticamente idêntico em JSON e YAML e possuir exatamente uma raiz com `book`, `urls` e `global_hashes`. [62596f1]

`book` DEVE conter exatamente `title`, `contributors`, `edition`, `language`, `primary_category` e `tags`. [62596f1]

Cada `book.contributors[]` DEVE conter exatamente `name` e `role`. [62596f1]

`book.edition` DEVE existir e ser exatamente `{}`. Qualificador editorial oficial [62596f1]
necessário para distinguir publicações, quando já integrar inequivocamente o
título canônico ou a evidência editorial, DEVE permanecer como parte indivisível [62596f1]
de `book.title`, sem ser projetado em propriedade adicional. Qualificador
inferido, técnico ou não comprovado DEVE bloquear conformidade. [62596f1]

`book.tags` DEVE existir e PODE ser `[]`; nenhum outro objeto ou lista vazia e admitido. [62596f1]

Cada `urls[]` DEVE conter exatamente `format` e `url`. [62596f1]

Cada `global_hashes[]` DEVE conter exatamente `format`, `sha1`, `sha256` e `sha512`. [62596f1]

Propriedade não enumerada NÃO DEVE integrar o documento formativo. [62596f1]

`schema_version`, `book.id`, `short_token`, `artifact_id`, `assets`, `sources`, QR, pacote e contêiner NÃO DEVEM ser propriedades do documento formativo; quando necessários ao envelope global, permanecem externos a `formative_data`. [62596f1]

Toda informação extraída DEVE permanecer candidata até validação por evidência reproduzível; incerteza, conflito ou plausibilidade NÃO DEVE preencher propriedade. [62596f1]
### 44.1 Serialização segura

JSON DEVE ser UTF-8 sem BOM, comentário, vírgula final, chave duplicada ou número não finito. [62596f1]

YAML DEVE usar subconjunto seguro 1.2 com mapping, sequence e string; âncora, alias, merge key, tag, construtor, diretiva e múltiplos documentos DEVEM ser rejeitados. [62596f1]

String YAML DEVERIA usar aspas para evitar resolução implícita e preservar caixa, pontuação e zeros.

Conversão JSON para YAML e retorno DEVE preservar chaves, hierarquia, tipos, Unicode, valores e ordem das listas com igualdade profunda. [62596f1]

`null`, chave omitida, string vazia e vazio fora de `book.edition` e `book.tags` DEVEM ser rejeitados. [62596f1]

### 44.2 Domínios fechados

`book.title` DEVE ser string Unicode editorial não vazia. [62596f1]

`book.contributors` DEVE possuir um ou mais itens e ao menos um `role: "author"`. [62596f1]

`book.language` DEVE ser BCP 47 válida em minúsculas. [62596f1]
`book.primary_category` DEVE seguir `[a-z0-9]+(?:-[a-z0-9]+)*`. [62596f1]

Cada tag DEVE seguir o mesmo padrão, ser única, relevante, ordenada lexicalmente e não repetir a categoria. [62596f1]
`contributors[].name` DEVE ser Unicode editorial não vazio; `role` DEVE seguir `[a-z][a-z0-9-]*`. [62596f1]

`urls` DEVE ter um ou mais itens; `format` DEVE ser `pdf` ou `epub` e `url` DEVE ser URI HTTP(S) absoluta normalizada. [62596f1]

`global_hashes` DEVE ter um item por formato aceito, no mínimo um e no máximo dois, sem formato repetido e em ordem `pdf`, depois `epub`. [62596f1]

SHA-1, SHA-256 e SHA-512 DEVEM ser hexadecimais minúsculos de 40, 64 e 128 caracteres. [62596f1]

### 44.3 Evidência de `book`

O original DEVE ser preservado, identificado por assinatura/estrutura e analisado antes de conversão, reparo, reempacotamento, OCR ou normalização. [62596f1]

Metadado estruturado, página de rosto, verso, colofão e primeiras unidades editoriais DEVEM ser extraidos na ordem do formato. [62596f1]

Título, autoria e idioma DEVEM ser comparados com ao menos duas evidências independentes quando disponíveis. [62596f1]

Conflito material, autoria ausente, baixa confiança ou arquivo ilegível DEVE bloquear o documento e produzir diagnóstico. [62596f1]

OCR somente DEVE ser usado quando a camada textual for ausente ou insuficiente e NÃO DEVE substituir o original nem servir como evidência primária autossuficiente. [62596f1]

Título DEVE preservar capitalização, diacrítico, pontuação e grafia editorial; espaço externo, controle Unicode e repetição acidental PODEM ser normalizados em cópia. [62596f1]

Página de rosto ou colofão visível DEVE preceder título estruturado EPUB coerente, metadado PDF coerente e cabeçalho editorial recorrente. [62596f1]

Filename, diretório, URL, capa isolada, primeira linha ou OCR isolado NÃO DEVEM comprovar título. [62596f1]

Contribuidores DEVEM preservar forma creditada, função e ordem editorial; o primeiro autor DEVE representar autoria principal. [62596f1]

Duplicata exata `name + role` DEVE ser removida, mas homônimos NÃO DEVEM ser fundidos sem evidência. [62596f1]

Papéis recomendados PODEM incluir `author`, `editor`, `translator`, `compiler` e `illustrator`; outro papel exige significado editorial comprovado. [62596f1]

Pessoa citada, prefaciador, personagem, mantenedor ou proprietário NÃO DEVE ser autor sem credito editorial. [62596f1]

Idioma DEVE representar a edição e seguir precedência de metadado EPUB coerente, declaração editorial, amostra textual distribuída e revisão. [62596f1]

Detector de idioma DEVE ser auxiliar e NÃO DEVE usar somente título, primeira página, filename, domínio ou país do fornecedor. [62596f1]

Edição multilíngue sem predominância inequívoca DEVE ir a revisão. [62596f1]

Categoria DEVE vir de vocabulário controlado e evidência; empate exige decisão editorial única. [62596f1]

Tag NÃO DEVE ser inferida somente de filename, fornecedor, formato, idioma ou detalhe técnico. [62596f1]

### 44.4 Hashes globais

Hash DEVE incidir nos bytes integrais e originais do contêiner EPUB ou arquivo PDF, antes de qualquer extração, conversão, reparo, OCR, renderização ou compactação. [62596f1]

Leitura DEVE ser binária, sequencial, completa e alimentar SHA-1, SHA-256 e SHA-512 na mesma passagem e nos mesmos chunks. [62596f1]

Arquivo reparado ou regravado NÃO DEVE herdar hash do original. [62596f1]

SHA-1 DEVE existir somente para interoperabilidade e NÃO DEVE provar integridade isoladamente. [62596f1]

Divergência em qualquer algoritmo DEVE rejeitar igualdade byte a byte. [62596f1]

Hash parcial, ausente, truncado, maiúsculo ou calculado sobre texto DEVE ser rejeitado. [62596f1]

Implementação Node.js DEVERIA usar fluxo binário e `node:crypto`; implementação Python DEVERIA usar modo `rb` e `hashlib`, sem converter chunks em string.

Biblioteca alternativa PODE ser usada somente se produzir os mesmos valores sobre os mesmos bytes e preservar segurança/evidência. [62596f1]

### 44.5 URLs formativas e aquisição

Cada URL DEVE vincular explicitamente formato esperado, usar HTTP(S), host explícito, sem credencial ou fragmento, preservando path e query necessários. [62596f1]

Para cada formato em `global_hashes` DEVE existir ao menos uma URL do mesmo formato; todo formato de URL DEVE possuir exatamente um hash correspondente. [62596f1]

Múltiplas URLs do mesmo formato PODEM representar fontes alternativas dos mesmos bytes e DEVEM manter preferência editorial ou ordem de submissão. [62596f1]

URL duplicada após normalização segura DEVE ser rejeitada; grupos DEVEM ordenar `pdf` antes de `epub`. [62596f1]

URL somente DEVE gerar asset quando os bytes diretos ou extraidos corresponderem integralmente aos três hashes. [62596f1]

Fonte DEVERIA ser link oficial direto de editor, autor, biblioteca, repositório institucional ou provedor confiável; página, manifesto, catálogo, feed ou API PODEM ajudar a localizar o arquivo. [62596f1]
Endereço incorporado no arquivo, busca, cache, espelho ou terceiro DEVE permanecer candidato até confirmação. [62596f1]

URL relativa somente DEVE ser resolvida contra a página ou manifesto que a declarou. [62596f1]
Redirecionamento observado NÃO DEVE substituir silenciosamente a URL submetida. [62596f1]
Endereço NÃO DEVE ser inventado por padrão de nome, troca de extensão, código de idioma ou filename. [62596f1]

URL temporária, assinada, secreta, autenticada ou de validade curta NÃO DEVE integrar o documento. [62596f1]

Parâmetro indispensável DEVE ser preservado; parâmetro comprovadamente analítico DEVERIA ser removido sem alterar o recurso. [62596f1]

Ausência de URL pública direta e estável DEVE bloquear conformidade, sem usar path local inventado. [62596f1]

### 44.6 Rede e validação de aquisição

Antes de request, URL DEVE ser analisada, esquema/host validados e política de rede aplicada. [62596f1]

`HEAD` PODE sondar, mas somente `GET` limitado DEVE confirmar disponibilidade, tipo e integridade. [62596f1]

Redirecionamentos DEVEM ser limitados e revalidar esquema, host, DNS e IP em cada salto. [62596f1]

Host local, IP privado, link-local, multicast, reservado, protocolo não HTTP(S), loop e DNS rebinding DEVEM ser bloqueados. [62596f1]

Conexão DEVE usar timeout, limite de bytes, rate limit, cancelamento e streaming; corpo parcial DEVE falhar. [62596f1]

Formato DEVE ser confirmado por assinatura e estrutura; extensão, `Content-Type`, código HTTP ou nome NÃO DEVEM bastar. [62596f1]

Hashes DEVEM ser calculados durante a leitura e comparados antes da incorporação. [62596f1]

Invólucro permitido DEVE ser extraido em ambiente isolado e limitado, produzindo exatamente um artefato correspondente. [62596f1]

Diagnóstico DEVE registrar URL submetida, redirecionamentos, tamanho, tipo e hashes fora do documento formativo. [62596f1]

Falha de rede, bloqueio, resposta autenticada, HTML, desafio ou indisponibilidade DEVE impedir incorporação automática. [62596f1]

Conteúdo obtido NÃO DEVE executar script, macro, mídia ativa ou incorporado. [62596f1]

Cliente Node.js DEVERIA usar `URL`, redirecionamento manual, DNS validado, `AbortSignal` e streaming; cliente Python DEVERIA usar `urllib.parse` e cliente com as mesmas guardas.

Buffer integral sem limite prévio NÃO DEVE ser usado em resposta potencialmente grande. [62596f1]

### 44.7 EPUB, PDF e associação editorial

EPUB DEVE ser tratado como ZIP OCF não confiável com limites de entradas, tamanho comprimido/expandido, razão, profundidade e path. [62596f1]

Path absoluto, traversal, symlink, colisão normalizada e entidade XML externa DEVEM ser rejeitados. [62596f1]

Package Document DEVE ser localizado pelo container, namespaces respeitados e spine usado como ordem editorial. [62596f1]

Título, idioma e contribuidores estruturados DEVEM ser confrontados com página de rosto e colofão. [62596f1]

Impressão textual EPUB DEVE seguir spine, excluir script/estilo/navegação repetitiva e normalizar somente cópia derivada. [62596f1]

PDF DEVE ser analisado por biblioteca que compreenda objetos, xref, streams, fontes, páginas e metadados; regex sobre bytes crus NÃO DEVE extrair `book`. [62596f1]

Página de rosto e colofão visíveis DEVEM prevalecer sobre metadado técnico conflitante. [62596f1]

Extração PDF DEVE preservar número/ordem das páginas e diagnosticar página vazia ou baixa densidade. [62596f1]

PDF cifrado sem autorização, corrompido ou acima de limite DEVE falhar com diagnóstico. [62596f1]

PDF e EPUB somente DEVEM compartilhar documento quando título, autoria, idioma e identidade editorial forem compatíveis. [62596f1]

Equivalência textual aproximada isolada ou igualdade de hashes entre formatos NÃO DEVEM comprovar identidade. [62596f1]

Diferença de paginação, layout ou codificação NÃO DEVE separar por si só; diferença material de conteúdo, idioma, autoria ou edição DEVE impedir associação automática. [62596f1]

Confiança insuficiente DEVE encaminhar para revisão humana. [62596f1]

### 44.8 Validação integral do documento formativo

Validador DEVE confirmar parser seguro, raiz exata, seis chaves de `book`, `edition: {}`, `tags`, contribuidor/autor, chaves de contribuidor, domínios, URLs, correspondência de formatos, cardinalidade dos hashes, recálculo dos três hashes, associação editorial e igualdade profunda JSON/YAML. [62596f1]

Falha DEVE indicar propriedade, regra e evidência necessária sem inventar substituto. [62596f1]

Item inválido NÃO DEVE ser removido silenciosamente para simular conformidade. [62596f1]

Documento somente DEVE ser aceito quando toda propriedade obrigatória existir e nenhuma adicional existir. [62596f1]
Referências técnicas aplicáveis DEVEM considerar RFC 8259, YAML 1.2.2, RFC 3986, BCP 47/RFC 5646 e EPUB 3.3. [62596f1]
### 44.9 Exemplo delimitador

O exemplo abaixo é formativo e NÃO DEVE fornecer hashes a payload produtivo; toda matriz produtiva DEVE ser recalculada sobre os bytes originais. [62596f1]
```json
{
  "book": {
    "title": "Atos Dos Apóstolos",
    "contributors": [
      {
        "name": "Ellen G. White",
        "role": "author"
      }
    ],
    "edition": {},
    "language": "pt-br",
    "primary_category": "livros",
    "tags": []
  },
  "urls": [
    {
      "format": "pdf",
      "url": "https://media2.egwwritings.org/pdf/pt_AA(AA).pdf"
    },
    {
      "format": "epub",
      "url": "https://media2.egwwritings.org/epub/pt_AA(AA).epub"
    }
  ],
  "global_hashes": [
    {
      "format": "pdf",
      "sha1": "ef605032eb4011e6f058c100dc845f414e36e4f4",
      "sha256": "91e2d4ea3e74a3ec55ecd61fb659f57927ef90ae413ea699cd8b4e92c7d9051a",
      "sha512": "75b0c5ffda1ae8314cae7612afc947393817581b9ac219db497d526ee90417841e16b0e5f3ab0f2421eb8201358502ba6f9628e62195b4c37437d0967748cb42"
    },
    {
      "format": "epub",
      "sha1": "6df74abc8e2d57f82ff54a3b373d855c016f9f15",
      "sha256": "46d2ed2d02977d96d625c6c0d2ad65de4f769cece56b2e45f64f65555f5eba29",
      "sha512": "cc055518caab4bcf2399dde632359ab808b5dfeea2259e886b9f9af161eca7fea611d7658d11d42f1a68b4d3f54e57a25ff50e2a68d010c83bb8337d1e41ff80"
    }
  ]
}
```

Representação YAML conforme DEVE analisar para estrutura profundamente igual ao exemplo JSON, sem propriedade, valor ou ordem de lista divergente. [62596f1]

O projeto NÃO DEVE declarar vínculo com editoras nem responder pelo conteúdo de terceiros; atribuição, restrição de uso, proveniência e integridade permanecem obrigatórias. [62596f1]

## 45. Capas

Cada diretório público de publicação DEVE conter arquivo decodificável chamado exatamente `cover.png`. [62596f1]

Grupo PDF/EPUB no mesmo diretório DEVE compartilhar uma capa canônica; grupo em diretórios distintos DEVE possuir cópia gerada correspondente. [62596f1]

Capa DEVE vir primeiro da capa EPUB editorialmente identificada, incluindo `cover-image`; fallback legado exige referência válida. [62596f1]

Maior imagem arbitrária NÃO DEVE ser presumida capa. [62596f1]

Sem capa EPUB utilizável, gerador DEVE renderizar a primeira página PDF editorialmente adequada sem modificar o original. [62596f1]

Página vazia, técnica, corrompida, de erro, ilegível ou não representativa NÃO DEVE ser aceita. [62596f1]

Ausência de ambas as fontes DEVE bloquear o grupo. [62596f1]

`cover.png` DEVE possuir no máximo 800 px em cada eixo, preservar proporção/nitidez/legibilidade, não ampliar sem justificativa e remover EXIF, comentário, miniatura e metadado inútil. [62596f1]

Capa DEVE ser otimizada para navegador e regenerável a partir das fontes e configuração versionada. [62596f1]

Remoção da capa DEVE causar regeneração na execução seguinte; mudança de EPUB, PDF, parser, extrator, configuração ou gerador DEVE invalidar derivado afetado. [62596f1]

Imagem externa NÃO DEVE ser escolhida por similaridade de nome, título ou arquivo. [62596f1]

Intermediários de renderização, conversão ou extração NÃO DEVEM integrar `dist/` ou site. [62596f1]

Validação DEVE comprovar existência, path, origem, precedência, formato, dimensões, proporção, legibilidade, metadados removidos e regeneração determinística. [62596f1]
## 46. Scripts, workflow, build e publicação

Indexador, capas, dados formativos, ativos web e demais derivados DEVEM ser produzidos por script reexecutável, determinístico, incremental e equivalente em local/CI. [62596f1]

Script Node.js novo DEVE usar TypeScript como fonte e artefato conforme o contrato operacional; Python PODE permanecer quando adequado ao ecossistema real. [62596f1]

Biblioteca de EPUB, PDF, OCR, imagem, YAML, JSON ou compactação DEVE ser mantida, licenciada, segura e proporcional. [62596f1]

Cache DEVE incluir identidade das fontes, configuração, parser, extrator e gerador para invalidação correta. [62596f1]
Workflow dedicado DEVE obter fonte, instalar dependências necessárias, descobrir/agrupar publicações, validar formatos, preservar originais, calcular hashes, extrair `book`, comprovar identidade, gerar capas, montar dados formativos, gerar índice/página, preparar artefato, validar e publicar. [62596f1]

Workflow DEVE reagir a mudança de página, publicação, capa, índice, dado, script, estilo, asset, parser, RCF ou configuração e DEVE permitir disparo manual. [62596f1]

Permissões DEVEM ser mínimas; concorrência DEVE serializar ou cancelar com segurança para impedir execução antiga sobre resultado novo. [62596f1]

Processo longo DEVE emitir progresso ultrassucinto por etapa e publicação sem inundar logs ou aparentar congelamento. [62596f1]

Build DEVE copiar integralmente `./src/publications/` para `/publications/`, independentemente de importação ou link na interface. [62596f1]

Tree shaking, limpeza e otimização NÃO DEVEM remover publicação ou asset pertencente ao acervo canônico. [62596f1]

Build DEVE falhar por arquivo ausente, path inválido, colisão, perda, sobrescrita, índice inválido, URL sem artefato, hash divergente, capa inválida ou grupo incompleto. [62596f1]

Release público NÃO DEVE conter fonte de desenvolvimento, cache, teste, log, source map, configuração de desenvolvimento, dependência inútil, intermediário, temporário, evidência interna ou OCR transitório. [62596f1]

Derivado DEVE ser identificável como gerado e NÃO DEVE receber edição manual quando houver fonte canônica. [62596f1]

## 47. Validação da cadeia pública

Validador do índice DEVE rejeitar JSON inválido, envelope divergente, publicação sem campos obrigatórios, URL inválida, `formative_data` divergente, chave extra/ausente, hash incorreto, formato duplicado ou item sem autor. [62596f1]

Validador público DEVE confirmar que cada URL direta corresponde a arquivo publicado, cada diretório possui capa, cada hash corresponde ao original e cada `book` corresponde ao grupo. [62596f1]

Página DEVE ser validada por HTML real, assets carregados, base path real, responsividade, acessibilidade, ausência de dependência ociosa e ausência de links ao índice/acervo. [62596f1]

Teste de capa DEVE remover `cover.png`, regenerar e comparar origem, validade, dimensões e determinismo. [62596f1]

Teste de migração DEVE comparar inventário pré/post, bytes, hashes, contagens, metadados, paths, colisões e retomada. [62596f1]
Execução local DEVE reproduzir as mesmas etapas, schemas e resultados do CI tanto quanto tecnicamente possível. [62596f1]

Nenhuma publicação DEVE ocorrer com artefato obsoleto, divergente ou parcial. [62596f1]

## 48. Ordem global e fronteiras de implementação

A fase 1 DEVE concluir somente esta normatização, validação documental, estado, TODO e commits. [62596f1]

A fase 2, FT-004, DEVE implementar: página no GitHub Pages; RCF específico e correção de `baixar.py`; migrador temporário; estrutura canônica; índice, hashes, metadados, capas, assets, build, validação e workflow. [62596f1]

A fase 2 NÃO DEVE implementar busca independente da cadeia pública, salvo dependência estritamente necessária registrada antes da alteração. [62596f1]

A fase 3, FT-002, DEVE implementar o núcleo de busca, persistência, segmentação, RAG aprovado, equivalência numérica, recuperação híbrida, Modo Pesquisa, Modo Conversa probatório, citações e localizações verificadas, referências, tradução vinculada, sessão auditável, CLI, GUI, Markdown e conformidade restante. [62596f1]

A fase 3 NÃO DEVE duplicar artefato concluído e validado na fase 2. [62596f1]

Antes do código, a FT-002 DEVE decompor unidades materiais de índices/metadados, recuperação profunda, citações/localização, tradução, composição argumentativa, interface, sessão/rastreabilidade e avaliação/degradação. A decomposição NÃO DEVE separar camada sem entrega coesa nem fundir responsabilidades com aceite materialmente distinto. [62596f1]

Cada fase técnica DEVE iniciar por inspeção do estado real, baseline, arquitetura, dependências e plano atualizado; conclusão local NÃO DEVE antecipar a fase seguinte. [62596f1]

## 49. Aceite integrado

O produto somente DEVE ser considerado integralmente conforme quando a operação local/CLI estiver completa; GUI local estiver compartilhando o núcleo e operando offline; corpus estiver na estrutura canônica; downloader e migração forem seguros; página e cadeia pública forem reproduzíveis; índice, `NORMA-IF-SIL-001`, hashes e capas forem validados; Modo Pesquisa estiver preservado, multilíngue, numérico, híbrido, rastreável, resiliente e medido; e Modo Conversa estiver materializado com prova documental, fidelidade, abstenção e degradação verificadas. [62596f1]

Aceite DEVE comprovar ausência de perda ou sobrescrita, URLs estáveis, identidade editorial, correspondência de hashes, regeneração, segurança de EPUB/PDF/rede, incremento, retomada, configuração, desempenho, cross-platform e ausência de regressão. [62596f1]

Relatório final de cada fase DEVE listar arquivos, decisões, colisões, hashes, tecnologias, dependências, comandos, testes, resultados, limitações, fallbacks e pendências sem declarar execução não comprovada. A fase conversacional DEVE registrar ainda normas anteriores preservadas, diferenças entre modos, critérios de uso de LLM, modelo de citação/referência/tradução, prevenção de alucinação, FTs, conjuntos de avaliação e métricas disponíveis. [62596f1]

