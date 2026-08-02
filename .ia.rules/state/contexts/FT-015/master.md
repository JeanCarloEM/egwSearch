# Contexto mestre - FT-015

## Identidade

- FT: `FT-015`.
- tipo: `implementacao_codigo`.
- criado_em: `2026-08-02T18:59:01-03:00`.
- fonte: `.ia.rules/state/requests/FT-015/source.md`.
- RCF: §§40-41 e 43-49.
- prioridade: alta.
- estado: em andamento.

## Objetivo

Concluir a superfície pública estática do produto e sua cadeia reproduzível de
GitHub Pages: página institucional sem links diretos, artefato contendo todo o
acervo canônico em `/publications/`, build e validação locais equivalentes ao
CI, workflow dedicado e validação no destino público real.

## Baseline e conciliação

- `FT-004` foi resumida como concluída, mas seus subcontextos 03, 04 e 05
  preservam site, workflow e validação pública como pendentes;
- índice global, metadados, EPUBs, PDFs e capas já residem no acervo canônico e
  não serão regenerados sem necessidade;
- não há aplicação web nem workflow `.github` no baseline desta FT;
- a correção do downloader pertence ao commit isolado `99e1c7b` e não integra
  os commits da FT-015.

## Arquitetura e ordem

1. inventariar contratos, acervo e configuração remota do Pages;
2. criar build estático determinístico e validador público;
3. criar página institucional mínima, acessível e sem links ao acervo;
4. copiar integralmente `src/publications/` para `dist/publications/` e validar
   igualdade, hashes, URLs e ausência de conteúdo interno;
5. integrar comandos locais e workflow dedicado de GitHub Pages;
6. executar somente testes pequenos, rápidos e limitados a cinco minutos;
7. publicar, acompanhar o deployment e validar HTML/assets no endereço real;
8. sincronizar rastreabilidade e encerrar a FT somente com prova pública.

## Invariantes

- nenhum PDF, EPUB, metadado ou capa canônicos terá bytes alterados;
- a página não lista, vincula nem revela URLs diretas, índice ou diretórios;
- o artefato inclui todo o acervo e mantém URLs diretas conhecidas funcionais;
- paths funcionam no subdiretório de projeto e em domínio próprio;
- workflow usa permissões mínimas, concorrência segura e artifact oficial;
- cache, estado, teste, log, fonte de desenvolvimento e intermediário não
  integram `dist/` nem o artifact;
- nenhuma validação individual excede cinco minutos.

## Entregáveis

- fonte do site e estilos;
- build e validação reproduzíveis;
- comandos NPM próprios;
- workflow de GitHub Pages;
- testes direcionados;
- deployment e evidência pública real;
- estado, TODO e rastreabilidade sincronizados.

## Aceite

- build local determinístico e válido;
- `dist/` contém página mínima e projeção integral do acervo;
- HTML real não contém links ou revelações do acervo;
- workflow publicado conclui com sucesso;
- página e amostras conhecidas de metadados, EPUB, PDF e capa respondem no
  GitHub Pages com conteúdo correspondente ao repositório;
- branch `dev` e branch primária convergem ao final, conforme a Norma.
