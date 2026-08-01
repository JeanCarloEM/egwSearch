# Fonte canônica - FT-012

- origem: prompts humanos desta conversa e anexo visual.
- recebido em: `2026-08-01`.
- anexo: `codex-clipboard-7727984a-9c3a-4cb0-a921-d3355bc30002.png`.
- incorporação: em andamento pela FT-012.

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
