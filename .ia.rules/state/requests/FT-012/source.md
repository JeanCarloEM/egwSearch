# Fonte canônica - FT-012

- origem: prompts humanos desta conversa e anexo visual.
- recebido em: `2026-08-01`.
- anexo: `codex-clipboard-7727984a-9c3a-4cb0-a921-d3355bc30002.png`.
- incorporação: concluída pela FT-012.

## Solicitação integral

> não está baixando todos os e-pub e pdf disponíveis, e quanto aos conteúdos
> não epub/pdf, ele não está de fato criando o equivalente real, como pode ser
> observado pelo anexo.

## Evidência inicial

O anexo mostra um EPUB derivado contendo somente “Capítulo 1” e “Primeiro
capítulo.”. A inspeção local comprovou que esse conteúdo veio do fixture
sintético `tests/fixtures/publications/pioneers.json`, executado contra a raiz
canônica. A inspeção pública comprovou também que o catálogo leve em
`text.egwwritings.org` expõe todas as obras, que ativos PDF/EPUB aparecem na
página individual da obra e que obras sem ativos nativos expõem conteúdo real
e navegação editorial encadeada por capítulos.

## Complementação de 2026-08-01 — capa editorial

> Faça um aprimoramento relacionado à FT-12. Embora textos online não PDF/EPUB
> não tenham uma capa implícita, a coleção indica uma capa/cover para eles.
> Use-a para o EPUB/PDF eventualmente gerado e para o `cover.png` final gerado
> (`https://egwwritings.org/allCollection/pt/1286`).

A ficha pública leve da obra `14389`, pertencente à coleção indicada, declara
`og:image=https://a.egwwritings.org/covers/14389?type=large`, com alternativa
editorial “Cover of the book ESF”. A projeção móvel oficial confirma a imagem
equivalente em `https://media4.egwwritings.org/covers/14389_r.jpg`.

## Complementação de 2026-08-01 — reversibilidade e nota não editorial

> Uma vez o EPUB gerado a partir dos `.md` e bem formatado para indexação
> conforme o RCF, permitindo fácil reversão posterior, os `.md` originais não
> precisam persistir. O EPUB deve conter contracapa ou nota em página inicial
> adequada, identificada como não editorial, informando origem, data e link em
> estilo ABNT.

A implementação preservará os bytes Markdown e seus hashes dentro do contêiner
EPUB, fora do spine editorial, com manifesto reversível. Somente depois de
validar contêiner, conteúdo renderizado, manifesto e restauração byte a byte os
arquivos `.md` externos serão removidos.

## Esclarecimento de 2026-08-01 — formato derivado

> Para geração a partir de `.md`, pode-se gerar apenas o EPUB. PDF fica como
> opcional e futuramente implementável, caso desejado.

Logo, a FT-012 não implementará gerador PDF; apenas preservará no contrato que
um gerador futuro reutilize a mesma capa canônica e não produza falso
equivalente rasterizado.

## Ajuste de 2026-08-01 — capa em página inteira

> A capa deve ocupar a primeira página inteira, borda a borda.

A página de capa do EPUB será exclusiva, sem margens, faixas ou texto visível.
A imagem preencherá toda a viewport e preservará sua proporção por recorte
central mínimo quando a proporção do dispositivo diferir da capa.

## Ajuste de 2026-08-01 — categoria no path

> Ajustar a slug para incorporar um diretório adicional que informe a
> categoria, como pioneiro ou comentário, seguindo a categorização do site de
> origem e normalizando-a para URI.

A coleção oficial será a autoridade da categoria. Seu rótulo editorial será
preservado em metadados e uma projeção ASCII RFC 3986 formará o segmento
adicional entre idioma e tipo; título ou autoria não serão usados para inferir
categoria ausente.

## Esclarecimento de 2026-08-01 — códigos curtos em PT-BR

> Simplifique os nomes: Ellen White deve ir diretamente para o autor `egw` e
> “Biblioteca dos Pioneiros” deve usar `pioneiros`; aplique às categorias
> inglesas o equivalente em PT-BR.

O rótulo remoto continuará preservado como evidência, mas o path usará código
curto explícito em português. Quando categoria e autor forem ambos `egw`, o
segmento não será duplicado; para autores pioneiros haverá `pioneiros/` antes
do tipo. A mesma tabela semântica valerá para coleções em inglês.

## Ajuste de 2026-08-01 — categoria antes do autor

> Os diretórios `pioneiros` e equivalentes devem anteceder o nome do autor na
> estrutura e no slug, como subcategoria organizacional.

A projeção canônica passa a ser
`[<categoria>/]<autor>/<idioma>/<tipo>/<slug-titulo>/`. A omissão quando
categoria e autor forem idênticos continua evitando a duplicação `egw/egw`.

## Ajuste de 2026-08-01 — procedência e paginação editorial

> A referência ABNT com link oficial deve aparecer no início, para permitir
> validação imediata. Depois do sumário, páginas de conteúdo devem usar
> cabeçalho contextual e rodapé numerado; a página de abertura de capítulo ou
> equivalente não deve exibir cabeçalho.

O EPUB refluível usará a ordem `capa -> proveniência -> sumário -> conteúdo`.
Cabeçalhos e números serão conteúdo gerado em caixas de margem CSS paginada,
fora do corpo XHTML, para não integrar o texto editorial consumido por parser,
indexador, tokenizador ou LLM. A primeira página de cada unidade suprimirá o
cabeçalho, preservando o contador no rodapé.

## Evidência superveniente de 2026-08-01 — navegação e capa inexistente

> `TEXT_DISCOVERY_PROGRESS book=14623 units=1 complete=false`
> `ERRO_CONTRATO: navegação editorial anterior/próximo divergente`

A execução pública controlada comprovou que uma página pode apontar em
`rel=prev` para o identificador do primeiro bloco editorial da página anterior,
em vez da rota pela qual ela foi acessada. A correção passou a reconhecer essas
duas identidades somente quando ambas pertencem à mesma obra e página; a obra
`14623` então concluiu sua cadeia real com 12 unidades.

Na fase seguinte, o `og:image` oficial da mesma obra declarou
`https://a.egwwritings.org/covers/14623?type=large`, mas o próprio endpoint
respondeu conclusivamente `404`, `application/problem+json` e
`detail="Cover not found"`; as variantes oficiais conhecidas também não
oferecem imagem válida. O RCF vigente bloqueia `completed` nessa condição. A
decisão entre manter o bloqueio ou reconhecer metadado remoto quebrado como
ausência comprovada de capa exige confirmação humana antes de evolução
comportamental.

## Decisão e ajuste de 2026-08-01 — ausência oficial e preflight integral

> sim, está funcional. O script baixar deve evitar disperdiçar requisições http
> com publicações que já existam, ou seja, se ele conseguiu uma lista de
> publicações de determinado autor, fez a normalização, e a publicação já existe
> localmente (íntegra, verificável e válida), não há necessidade de gastar
> recursos e, muito menos acessar o servidor e potencialmente acionar mecanismo
> de prevenção de ataques. Corrija este ponto, faça o merge com main/master e
> push.
>
> isso se aplica, não apenas a logo mas a própria publicação epub/pdf.

O “sim” autoriza a evolução solicitada para a ausência oficial comprovada de
capa da obra `14623`. O preflight passa a ocorrer entre a listagem normalizada e
o enriquecimento individual: somente uma publicação inteira validada pode ser
dispensada, abrangendo PDF, EPUB, capa, metadado, derivados e fontes reversíveis.
Uma unidade incompleta ou inválida continua no fluxo remoto, e `--revalidate`
permanece como opt-in humano para conferência condicional.

## Evidência de conclusão de 2026-08-01

A execução controlada de `14623` terminou `completed`, com 12 segmentos, um
EPUB derivado e `cover.png` técnico originado exclusivamente do `404` oficial
estruturado. A validação do contêiner confirmou a ordem de spine `capa ->
proveniência -> sumário -> 12 seções`, URL oficial na nota não editorial, 12
Markdown internos e zero `.md` externo. A repetição terminou `skipped`, com
`downloaded=0`, `extracted=0`, `converted=0` e sem navegação específica da obra.

## Complementação de 2026-08-01 — retomada sem reinício implícito

> relativo a FT-012, baixar.py precisa ser capaz de continuar do ponto de onde
> parou ou de onde foi interrompido sem reiniciar, a não ser que seja
> explicitamente solicitado a isso.

A retomada passa a abranger descoberta e processamento da coleção, além do
checkpoint textual já existente. Reinício será uma operação separada e
explícita por `--restart`; reexecução normal e `--revalidate` não podem apagar
progresso confirmado.

Implementação concluída no commit `51edffb`: checkpoint versionado por coleção,
filtro e limite persiste catálogo, enriquecimentos e IDs confirmados. Teste de
interrupção confirmou que o item anterior não é reexecutado; corrupção bloqueia
sem renomear/apagar; `--restart` é a única operação que descarta o checkpoint
do escopo. A suíte total passou com 62 testes Python e três Node.

## Complementação de 2026-08-01 — identidade por SHA-512 e artigo repetido

> publicação com mesmo sha512 não podem coexistir = duplicações. Ainda que
> possuam nomes diferentes. A resolução do conflito de nome deve seguir a
> lógica, por exemplo: `a-ciencia-do-bom-viver-a` e
> `a-ciencia-do-bom-viver`; obviamente, o primeiro está errado, pois duplica o
> artigo `a`.

A auditoria local comprovou que os EPUBs e os PDFs desses dois diretórios têm,
respectivamente, SHA-512 idênticos. O título remoto `A CIÊNCIA DO BOM VIVER, A`
repete no final o artigo já presente no início. A identidade canônica deve
eliminar somente essa repetição editorial inequívoca e projetar o slug
`a-ciencia-do-bom-viver`. Igualdade SHA-512 integral de um ativo PDF/EPUB em
diretórios distintos deve impedir a promoção da segunda publicação, mesmo que
nomes, acrônimos ou slugs difiram; colisão nominal sem regra editorial
determinística deve bloquear para revisão, nunca escolher ou apagar conteúdo
silenciosamente.

Implementação concluída no commit material `c3fbb92`: `CatalogItem` aplica a
canonicalização antes de identidade, slug e checkpoint; o downloader monta um
índice local por SHA-256 de metadado apenas para reduzir candidatos e recalcula
SHA-512 integral antes de qualquer decisão. A promoção bloqueia cópia existente
em outro diretório. A auditoria do acervo removeu nove diretórios rastreados de
aliases históricos e o diretório não rastreado do exemplo, preservando em cada
grupo o título declarado dentro do EPUB e mantendo os removidos em quarentena
local recuperável. O acervo ativo terminou com 1.036 identidades físicas sem
SHA-512 repetido entre publicações.

## Evidência superveniente de 2026-08-01 — request individual no legado

> eu percebo que ele faz pelo menos um HTTP request por publicação, mesmo que a
> publicação já exista com ambos os assets (epub/pdf) possíveis. Por exemplo,
> `https://text.egwwritings.org/book/b42`. Se ambos os assets possíveis são
> válidos e verificados, e é possível obter o título pelo índice da coleção uma
> única vez, qual o motivo de cada publicação ter uma requisição?
>
> o exemplo é apenas um mero exemplo; o caso ocorre com todas as publicações já
> existentes localmente.

A causa comprovada é sistêmica: `build_local_publication_index()` indexa apenas
`publication-source/v3` por `identity.remote_id`, enquanto 518 das 521
publicações locais ainda usam metadado legado URL-chaveado; 515 delas possuem
PDF e EPUB. O callback de descoberta recebe somente o ID remoto, não encontra
essas unidades e chama `_enrich_book()` para cada entrada. O catálogo já
fornece ID/URL, título, autor, coleção, idioma e tipo suficientes para projetar
o path legado determinístico. O preflight deve usar essa identidade composta,
validar metadado, URL, ambos os assets, assinatura, tamanho e hashes localmente
e dispensar toda requisição específica quando a prova for inequívoca.

## Garantia adicional de 2026-08-01 — rede somente por necessidade

> Garanta que a requisição HTTP à origem ocorra apenas quando efetivamente
> necessária.

O preflight local completo é gate anterior à rede específica da publicação.
Somente prova local inconclusiva, divergência, ambiguidade, corrupção, ausência
de ativo obrigatório ou `--revalidate` explícito pode liberar enriquecimento,
capa, texto ou download remoto; a decisão e seu motivo devem ser testáveis.

Implementação concluída no commit material `16b0886`: o callback recebe os
quatro dados do cartão (ID, título, URL e autor), compõe a identidade com a
coleção e valida metadado legado, PDF e EPUB no path canônico ou alias `en-us`.
O teste `b42` transforma `_enrich_book()` em sentinela proibida e comprova
`PUBLICATION_LOCAL_VALID remote_id=42 network=skipped`. Na coleção real
`en-books`, 116 de 121 entradas foram comprovadas localmente sem página
individual; somente cinco unidades sem prova local completa permaneceram
elegíveis ao enriquecimento necessário.

## Regressão observada de 2026-08-01 — checkpoint legado contorna o gate

> persiste, veja exemplo: `https://text.egwwritings.org/book/b11101`.

O preflight isolado comprova `b11101` com PDF e EPUB locais válidos. Porém, o
checkpoint de `pt-br-livros` persistiu 84 itens enriquecidos anteriormente com
`local_complete=false`. Na retomada, a condição `if not item.local_complete:
continue` impede exatamente esses itens antigos de passar pelo gate novo. Todo
item não confirmado deve ser reavaliado localmente com a versão corrente do
contrato, independentemente do booleano armazenado; checkpoint é cache de
progresso, não autoridade para liberar rede nem invalidar prova local.

Implementação concluída no commit material `dbd8096`: a retomada reaplica o
preflight a todo item não confirmado, fornece os dados originais do cartão e
substitui atomicamente o item histórico quando a prova local é válida. Teste
dedicado persiste `b11101` como `local_complete=false`, proíbe
`_enrich_book()` por sentinela e comprova atualização para
`PUBLICATION_LOCAL_VALID ... checkpoint=updated network=skipped`.

## Regressão observada de 2026-08-02 — enriquecimento completo sem asset

> BUG: Mostrou e carregou no navegador sem erro no console como aparentemente
> concluídos, mas não geraram assets (PDF/EPUB) no `src/`; entre outros:
> `https://text.egwwritings.org/read/14386.2`,
> `TEXT_DISCOVERY_PROGRESS book=14386 units=1 complete=false` e
> `https://text.egwwritings.org/read/14382.24`.

O checkpoint real comprova a causa sistêmica: `14386` terminou 45 unidades e
`complete=true`, mas permaneceu como sexto item não confirmado da coleção;
`14382`, iniciado depois, ficou incompleto. A descoberta enriquece toda a
coleção antes de iniciar qualquer processamento, de modo que uma publicação
posterior interrompida impede a geração das anteriores já completas. A
correção deve promover cada publicação imediatamente após seu enriquecimento e
checkpoint, preservando a seguinte como pendente e retomável.
