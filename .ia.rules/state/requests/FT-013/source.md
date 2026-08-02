# Fonte canônica - FT-013

- origem: solicitação humana desta conversa.
- recebido em: `2026-08-02`.
- incorporação: em andamento pela FT-013.
- precedente imediato: correção do catálogo `en-pioneers` no commit `e00ca57`.

## Solicitação integral

> Embora um script isolado (invocador) para gerar/refatorar o indexador global
> (e multilocalizado) deva existir, o `baixar.py` deve, a cada publicação
> baixada/atualizada, atualizar imediatamente o indexador global (que deve
> possuir gatilho/parâmetro próprio, evitando redundância de implementação), já
> com os metadados, links, hashes e demais informações, conforme definido na
> norma RCF.
>
> Conforme se efetua o download do EPUB/PDF ou a própria geração manual do
> EPUB, deve ser criado um manifesto meramente identificador, extremamente
> inteligente, das melhores estratégias de chunking para aquele arquivo
> específico. A análise deve considerar múltiplos cenários e alternativas,
> como parágrafo, frase, página, tópicos e microtópicos, dias de meditações,
> seções de periódicos e artigo inteiro, permitindo comparar futuramente
> estratégias de chunks em RAG.
>
> Um script especializado deve ser invocado para cada arquivo, usando
> preferencialmente algoritmos e bibliotecas open source reconhecidos,
> mantidos e consolidados, complementados quando insuficientes. Em arquivos
> gerados, deve aproveitar o conhecimento prévio da estrutura e potenciais
> fontes `.md` embutidas. O script deve analisar parsers e estratégias, além de
> correlacionar padrões compartilhados de formatação ou codificação entre as
> publicações.
>
> O analisador deve poder ser invocado sobre uma publicação, um diretório
> aninhado ou globalmente, sempre podendo enxergar e correlacionar a estrutura
> completa do acervo. Sua execução pelo `baixar.py` deve ser síncrona para a
> publicação e abranger todos os EPUB/PDF baixados ou gerados. Não é obrigatório
> materializar chunks antecipadamente, salvo quando comprovadamente conveniente.

## Aceite derivado da solicitação

1. gerador único e determinístico do índice global, invocável isoladamente e
   reutilizado pelo downloader por gatilho explícito;
2. atualização imediata do item afetado depois de publicação válida, sem
   reimplementar o contrato no `baixar.py`;
3. índice multilocalizado com metadados, rotas públicas, proveniência e hashes,
   mantendo `formative_data` estritamente conforme `NORMA-IF-SIL-001`;
4. manifesto de análise por ativo, identificador e sem chunks obrigatórios;
5. análise EPUB/PDF segura, explicável e determinística, com correlação global;
6. CLI apta a arquivo, publicação, subárvore e acervo integral;
7. integração síncrona: falha de análise ou índice impede confirmação final da
   publicação e preserva estado retomável;
8. código, testes e contratos versionados sem incluir caches, temporários,
   perfis ou publicações geradas pela execução do downloader.
