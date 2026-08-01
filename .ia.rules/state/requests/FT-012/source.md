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
