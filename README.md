# egwSearch

![Estado](https://img.shields.io/badge/estado-norma%20consolidada-blue)
![Implementacao](https://img.shields.io/badge/coletor-FT--012%20validado-blue)
![Licenca](https://img.shields.io/badge/licenca-MPL--2.0-green)

egwSearch e uma ferramenta planejada para pesquisar conceitos, palavras e expressoes e conversar de forma probatoria com colecoes arbitrarias de publicacoes textuais PDF e EPUB, preservando resultados e evidencias documentais verificaveis.

## Referencias

- [RCF.md](RCF.md): normas, contratos e requisitos do projeto.
- [AGENTS.md](AGENTS.md): processo, precedencia e modus operandi da IA no repositorio.
- [.ia.rules/state/TODO.ia.md](.ia.rules/state/TODO.ia.md): demandas tecnicas remanescentes.
- [.ia.rules/continue.ia](.ia.rules/continue.ia): FTs e ponto de retomada.

## Estado

O RCF consolidado cobre Modo Pesquisa, Modo Conversa probatorio e cadeia
publica. O coletor de publicacoes possui contratos incrementais para Ellen G.
White, `Biblioteca dos Pioneiros Adventistas` e `Adventist Pioneer Library`,
restritos a `pt-BR`, `en`, PDF, EPUB e texto editorial verificavel. Busca,
interface e etapas publicas remanescentes seguem as FTs registradas.

## Site público

A página institucional e o acervo estático são construídos localmente pela
mesma cadeia usada no GitHub Pages:

```powershell
npm run site:refresh
npm run site:build
npm run site:validate
```

O artefato fica em `dist/`. A página apresenta somente a finalidade do produto;
ela não lista nem vincula o índice ou os arquivos. Metadados, capas, EPUBs e
PDFs permanecem no artefato público sob rotas estáveis conhecidas pelos
consumidores. O workflow dedicado publica a branch primária e também admite
acionamento manual, sem Jekyll ou tema implícito.

## Coletor de publicacoes

O comando abaixo valida descoberta, persistencia temporaria, repeticao e
conversao contra fixtures locais, sem rede nem alteracao do acervo:

```powershell
python -m unittest discover -s tests/publications -v
```

O coletor operacional reside fora do conteúdo público:

```powershell
npm install
npm run publications:baixar -- --help
```

`npm install` prepara o ambiente Python local em
`constructor/.state/egwsearch/environments/python` usando os requisitos fixados do
coletor, sem instalar pacotes globalmente nem executar a coleta. Para verificar
ou reparar o ambiente manualmente, use `npm run publications:bootstrap`; para
validá-lo sem instalar, use `npm run publications:check`. Para atualizar as
dependências npm e então reconciliar obrigatoriamente o ambiente Python, use
`npm run update`.

Uma amostra pública da CLI deve usar `--limit 1` e uma única coleção. Para
selecionar uma publicação exata por identificador remoto, título ou URL, use
`--publication <valor>`. A descoberta percorre o catálogo público leve, inclusive
os catálogos individuais de autores, abre a ficha de cada obra e adquire todos os
PDFs e EPUBs habilitados. Quando não há formato nativo, percorre a sequência real
do leitor por `rel=next`, preserva o conteúdo editorial e gera EPUB verificável.
A capa oficial declarada pela ficha da obra origina `cover.png` e integra o EPUB
como `cover-image`. O EPUB mantém XHTML semântico para indexação, inclui uma
contracapa de proveniência não editorial em estilo ABNT e carrega um manifesto
Markdown interno que permite restauração byte a byte; por isso, os `.md`
externos são removidos depois do round trip validado. PDF derivado permanece
opcional e não é gerado nesta FT.

O progresso e o ponto de retomada de textos extensos ficam exclusivamente em
`constructor/.state/egwsearch`. Fixtures também escrevem nesse estado temporário
por padrão; `--output-root` permite escolher outro destino isolado, mas rejeita o
acervo canônico. Esses artefatos operacionais não integram o produto nem o Git.

O padrão usa um worker, atraso e jitter. Quando a descoberta exige navegador, a
CLI abre Firefox visível com perfil persistente local e reutiliza a mesma guia;
CAPTCHA ou verificação humana pausam a descoberta até intervenção do usuário,
sem tentativa de resolução automática.
`--revalidate` envia `If-None-Match`/`If-Modified-Since` somente quando o
metadado local contém validadores. Coleta ampla não é implícita nem autorizada
por esses comandos.

## Autor e Licença

**Autor:** [JeanCarloEM](https://jeancarloem.com)

**Licença:** [MPL-2.0](https://www.mozilla.org/MPL/2.0/) — uso, modificação e distribuição permitidos; alterações em arquivos MPL devem permanecer sob MPL-2.0.
