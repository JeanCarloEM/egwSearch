# Contexto mestre - FT-012

## Identidade

- FT: `FT-012`.
- tipo: `implementacao_codigo` com correção normativa causal.
- fonte: `.ia.rules/state/requests/FT-012/source.md`.
- estado: reaberta para aprimoramento de capa editorial.
- autorização: solicitação humana explícita para corrigir e concluir a
  funcionalidade real de `baixar.py`.

## Objetivo

Corrigir a conclusão indevida da FT-011 e tornar o coletor verificavelmente
completo: enumerar todas as obras do catálogo, inspecionar cada página de obra,
adquirir todos os PDF/EPUB nativos disponíveis e, somente na ausência de ambos,
extrair a sequência editorial integral e gerar derivados fiéis, incorporando a
capa oficialmente declarada para a obra.

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
7. adquirir e validar a capa declarada pela ficha/coleção, gerar `cover.png`
   canônico e incorporá-la ao EPUB e ao PDF local quando esses derivados forem
   produzidos.
8. empacotar no EPUB uma fonte Markdown reversível com manifesto/hash, remover
   os `.md` externos somente após validação e acrescentar contracapa de
   proveniência inequivocamente não editorial em estilo ABNT.
9. projetar a categoria editorial declarada pela coleção oficial como segmento
   URI adicional do diretório canônico, preservando também seu rótulo original.

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
- capa remota só é aceita quando declarada pela origem oficial da mesma obra;
  imagem arbitrária ou de outra edição não é fallback válido.
- remoção dos `.md` externos depende de restauração byte a byte comprovada a
  partir do EPUB; a nota de proveniência não integra o texto editorial.
- conversão Markdown materializa somente EPUB nesta FT; geração PDF permanece
  opcional, futura e fora do escopo implementado.
- a capa é o único conteúdo da primeira página do EPUB e ocupa a viewport
  inteira, borda a borda, sem margens ou faixas; diferença de proporção usa
  preenchimento com recorte central, sem deformar a imagem.
- categoria de path deriva exclusivamente do rótulo oficial configurado para a
  coleção e usa o normalizador URI comum; ausência ou categoria inválida bloqueia
  a aquisição, sem inferência por título ou autor.

## Aceite global

- contagem de obras coletadas igual à contagem de links únicos do catálogo;
- conjunto de ativos igual ao conjunto habilitado nas páginas individuais;
- texto derivado percorre uma cadeia `rel=next` acíclica até término declarado,
  com cada bloco editorial identificado e preservado;
- EPUB derivado contém o conteúdo real e sumário, e não texto de fixture;
- testes não escrevem em `src/publications`;
- amostra pública comprova ao menos uma obra nativa e uma obra somente textual.
- obra textual com capa declarada produz `cover.png` e derivados que incorporam
  exatamente essa capa validada.
- EPUB expõe estrutura adequada à indexação, contém contracapa não editorial e
  restaura os Markdown originais com nomes, ordem e hashes idênticos, sem exigir
  sua persistência externa.
- primeira página do EPUB contém exclusivamente a capa e preenche toda a área
  visível, comprovada no XHTML interno por layout sem margens e escala `slice`.
- destino canônico segue
  `<autor>/<idioma>/<categoria>/<tipo>/<slug-titulo>/`, e metadados/índice
  preservam rótulo e slug de categoria.

## Resultado

- catálogo público leve adotado e enumeração direta comprovada com 84 obras
  únicas em `pt-br-livros`;
- página individual tornada autoridade para título, autor, leitura e todos os
  ativos PDF/EPUB habilitados;
- obra nativa `1806` comprovada com dois ativos obrigatórios, ambos íntegros e
  idempotentemente reconhecidos;
- obra textual `14389` percorrida até término em 31 unidades reais, com
  checkpoint retomável, 316297 caracteres Markdown e EPUB de 136844 bytes;
- headings e ênfases preservados no EPUB, sem `Primeiro capítulo.` nem
  `Texto editorial inicial`;
- fixtures impedidas de escrever no acervo canônico; saída sintética anterior
  preservada em quarentena de runtime fora do Git;
- 49 testes Python, três testes Node, compilação Python, bootstrap/check,
  `agent:rcf` e `git diff --check` aprovados;
- `agent:verify` permanece não aplicável ao produto Python neste repositório e
  reporta o diagnóstico preexistente `TSCONFIG_AUSENTE`;
- commits materiais e normativos: `2ed0d43` e `279e2ef`.
