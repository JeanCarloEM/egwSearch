# egwSearch

![Estado](https://img.shields.io/badge/estado-norma%20consolidada-blue)
![Implementacao](https://img.shields.io/badge/coletor-FT--006%20validado-blue)
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

## Coletor de publicacoes

O comando abaixo valida descoberta, persistencia temporaria, repeticao e
conversao contra fixtures locais, sem rede nem alteracao do acervo:

```powershell
python -m unittest discover -s tests/publications -v
```

Uma amostra pública da CLI deve usar `--limit 1` e uma única coleção. O padrão usa um
worker, atraso e jitter; `403`, CAPTCHA ou desafio interrompem a coleção.
`--revalidate` envia `If-None-Match`/`If-Modified-Since` somente quando o
metadado local contém validadores. Coleta ampla não é implícita nem autorizada
por esses comandos.

## Autoria, repositorio e licenca

Autoria: nao declarada nos artefatos atuais do repositorio.

Repositorio: remoto Git configurado no proprio checkout.

Licenca: [Mozilla Public License 2.0](LICENSE). Texto de cabecalho equivalente: `This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.`
