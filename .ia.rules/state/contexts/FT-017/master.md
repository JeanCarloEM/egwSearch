# Contexto mestre — FT-017

## Identidade

- FT: `FT-017`.
- tipo: `documentação, arquitetura normativa e comunicação pública`.
- fonte: `TODO.ia.md`.
- prioridade: alta.
- estado: concluída e validada publicamente.

## Objetivo

Reposicionar a comunicação pública do **egwSearch** como ferramenta planejada
de investigação documental, probatória e hermenêutica; distinguir o que já
existe do que ainda é planejado; e reorganizar o RCF em uma raiz central e
especializações subordinadas sem perda de força, regra, exceção ou nuance.

## Baseline comprovado

- disponíveis: aquisição e preparação de publicações, estrutura canônica,
  capas, índice global, manifestos experimentais de chunking, build estático e
  GitHub Pages;
- parciais: corpus documental ainda não cobre integralmente a prioridade
  declarada, especialmente a Bíblia, e o laboratório de chunking prepara a
  futura recuperação sem constituir busca;
- planejados: núcleo de pesquisa, recuperação híbrida, Modo Pesquisa, Modo
  Conversa probatório, GUI local e aplicação efetiva de RAG;
- desvio: página e configuração apresentam o produto como acervo; README mistura
  estado presente e futuro e contém português sem acentuação adequada;
- dívida estrutural: o RCF principal concentra especializações de pesquisa,
  publicações e conversa em um único arquivo; `RCF.epistemologia.md` é vazio.

## Arquitetura documental

1. `RCF.md`: autoridade principal, propósito, corpus, escopo, precedência,
   conceitos centrais, estado material e mapa de leitura;
2. `.RCFs/RCF.pesquisa.md`: extração, normalização, busca, segmentação, RAG,
   avaliação, CLI/GUI e Modo Pesquisa;
3. `.RCFs/RCF.publicacoes.md`: cadeia pública, acervo, downloader, índice,
   dados formativos, capas, build, Pages e aceite da publicação;
4. `.RCFs/RCF.conversa.md`: Modo Conversa, prova, referência, sessão,
   arquitetura, degradação e validação;
5. `.RCFs/RCF.epistemologia.md`: modus operandi hermenêutico e exegético;
6. `scripts/publications/RCF.md`: especialização operacional já existente,
   subordinada à raiz e a `RCF.publicacoes.md`.

## Invariantes

- nenhuma intenção, implementação parcial ou protótipo será anunciado como
  recurso disponível;
- a finalidade não será confundida com aquisição, catálogo, acervo, downloader,
  indexador ou laboratório de RAG;
- a movimentação normativa preservará integralmente o texto material, com
  referências explícitas para toda regra deslocada;
- os documentos normativos e o README usarão UTF-8 e português brasileiro
  corretamente acentuado;
- a página continuará sem links diretos ao índice ou aos assets, embora estes
  permaneçam no artefato público;
- publicações e saídas concorrentes não integrarão os commits desta FT.

## Ordem e aceite

1. inventariar normas, implementação, site, build, testes e destino público;
2. registrar esta FT em commit exclusivo;
3. reorganizar e validar o RCF sem perda normativa;
4. refatorar README, página, configuração, 404, testes e build;
5. validar UTF-8, referências, links, classificação de estado e artefato local;
6. integrar, publicar o Pages e validar o resultado implantado;
7. concluir TODO, contexto, rastreabilidade e commits isolados.

A FT somente conclui quando o conteúdo público implantado expressar a finalidade
correta, o README e os RCFs forem coerentes com o estado real, a reorganização
for auditável e os assets públicos continuarem íntegros sem links na página.

## Fechamento

- material: `cbf1773`;
- rastreabilidade: `31383dc`, com 829 sentenças materiais validadas;
- testes: documentação 5/5 e site 4/4;
- artefato local: `SITE_PUBLICATION_OK`, 604 publicações e 3.562 arquivos;
- implantação: workflow Pages `30776089574` concluído com sucesso;
- validação pública: `https://egwsearch.jcem.pro/`, sem erro de console ou
  overflow horizontal, com finalidade, corpus e estado planejado corretos.
