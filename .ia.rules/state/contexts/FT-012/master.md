# Contexto mestre - FT-012

## Identidade

- FT: `FT-012`.
- tipo: `implementacao_codigo` com correção normativa causal.
- fonte: `.ia.rules/state/requests/FT-012/source.md`.
- estado: em andamento.
- autorização: solicitação humana explícita para corrigir e concluir a
  funcionalidade real de `baixar.py`.

## Objetivo

Corrigir a conclusão indevida da FT-011 e tornar o coletor verificavelmente
completo: enumerar todas as obras do catálogo, inspecionar cada página de obra,
adquirir todos os PDF/EPUB nativos disponíveis e, somente na ausência de ambos,
extrair a sequência editorial integral e gerar EPUB derivado fiel.

## Decomposição

1. registrar a lacuna e evoluir o RCF com critérios de completude observáveis;
2. preferir o catálogo público leve e coletar todas as identidades sem perda;
3. enriquecer cada obra pela página individual e obter todos os ativos nativos;
4. percorrer a cadeia editorial completa de texto, preservando semântica e
   referências, e validar primeira/última unidade, unicidade e encadeamento;
5. isolar fixtures fora de `src/publications`, retirar a saída sintética da
   árvore canônica e impedir regressão;
6. validar por fixtures realistas e amostra pública controlada, atualizar
   rastreabilidade, estado e commits.

## Invariantes

- nenhum fixture ou resultado sintético integra o acervo canônico;
- toda URL de PDF/EPUB habilitada na página da obra é adquirida ou causa falha
  explícita; um formato encontrado no cartão não encerra a descoberta;
- derivação textual só ocorre quando PDF e EPUB nativos estiverem ambos
  ausentes;
- conteúdo derivado corresponde às unidades editoriais reais, sem placeholder,
  resumo, reescrita ou salto silencioso;
- desafio de segurança continua sem bypass e estado de runtime continua fora do
  Git.

## Aceite global

- contagem de obras coletadas igual à contagem de links únicos do catálogo;
- conjunto de ativos igual ao conjunto habilitado nas páginas individuais;
- texto derivado percorre uma cadeia `rel=next` acíclica até término declarado,
  com cada bloco editorial identificado e preservado;
- EPUB derivado contém o conteúdo real e sumário, e não texto de fixture;
- testes não escrevem em `src/publications`;
- amostra pública comprova ao menos uma obra nativa e uma obra somente textual.
