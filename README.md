# egwSearch

[![GitHub Pages](https://github.com/JeanCarloEM/egwSearch/actions/workflows/pages.yml/badge.svg)](https://github.com/JeanCarloEM/egwSearch/actions/workflows/pages.yml)
![Licença](https://img.shields.io/badge/licença-MPL--2.0-green)

Ferramenta em desenvolvimento para pesquisa documental e hermenêutica
probatória em coleções textuais PDF e EPUB.

O objetivo é pesquisar conceitos, palavras e expressões e conversar com as
fontes por meio de citações, referências e localizações verificáveis. O corpus
prioritário compreende a Bíblia, os escritos de Ellen G. White, os pioneiros
adventistas e literatura pertinente à investigação hermenêutica.

## Estado

- **Disponível:** aquisição e preparação de publicações; validação de PDF/EPUB;
  capas, metadados, índice global, manifestos experimentais de chunking; build e
  publicação estática no GitHub Pages.
- **Parcial:** cobertura do corpus prioritário e avaliação preparatória de
  estratégias para futura recuperação.
- **Planejado:** pesquisa lexical, semântica e híbrida; Modo Pesquisa; conversa
  probatória; CLI de pesquisa e GUI local. Esses recursos ainda não estão
  disponíveis.

## Uso atual

```powershell
npm install
npm run publications:baixar -- --help
npm run site:build
npm run site:validate
```

O downloader pode exigir intervenção humana legítima no navegador e preserva
seu estado local fora do Git. O site gerado fica em `dist/`.

## Documentação

- [RCF principal](RCF.md)
- [Epistemologia hermenêutica](.RCFs/RCF.epistemologia.md)
- [Pesquisa documental](.RCFs/RCF.pesquisa.md)
- [Publicações e cadeia pública](.RCFs/RCF.publicacoes.md)
- [Conversa probatória](.RCFs/RCF.conversa.md)
- [Norma operacional da IA](AGENTS.md)

**Autor:** [JeanCarloEM](https://jeancarloem.com)

**Licença:** [MPL-2.0](https://www.mozilla.org/MPL/2.0/)
