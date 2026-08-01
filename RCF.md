# RCF - egwSearch

Este RCF e a especificacao normativa do egwSearch. `AGENTS.md` governa processo, precedencia e operacao de IA; este arquivo governa produto, requisitos, contratos, criterios de aceite e restricoes de negocio/arquitetura.

Aplicam-se `./AGENTS.md`, `./.ia.rules/core/concepts/microconceitos.md` (`MN-2119`, `MN-DENS`, `MN-PRES`, `MN-REF`, `MN-STATE`, `MN-VAL`, `MN-CLI`, `MN-CMD`) e `./.ia.rules/core/contracts.md`.

## 1. Identidade e objetivo

egwSearch DEVE ser uma ferramenta local para pesquisar conceitos, palavras, expressoes e formulacoes semanticamente equivalentes e para conversar de forma probatoria com colecoes arbitrarias de publicacoes textuais PDF e EPUB distribuidas em diretorios recursivos de profundidade ilimitada.

A ferramenta DEVE suportar livros, compilacoes, devocionais, revistas, jornais, periodicos, edicoes, traducoes e titulos disponiveis simultaneamente em PDF e EPUB.

Cada pesquisa individual no Modo Pesquisa DEVE gerar ou atualizar exatamente um arquivo Markdown principal consolidado, com todas as ocorrencias encontradas na colecao, agrupadas, deduplicadas, referenciadas, auditaveis e traduzidas quando aplicavel.

Cada interacao no Modo Conversa DEVE explicar, comparar e argumentar com base no acervo, vinculando afirmacoes materiais a citacoes literais, referencias completas e localizacoes verificadas, sem fabricar prova nem apresentar inferencia como conteudo da fonte.

A busca DEVE localizar correspondencia literal, variantes ortograficas e morfologicas, flexoes, traducoes, sinonimos, locucoes, parafrases, expressoes semanticamente equivalentes e formulacoes em `pt-BR` e `en-US`.

Precisao, rastreabilidade, reutilizacao de tecnologia existente, resiliencia, processamento incremental e revisao controlada de ambiguidades DEVEM prevalecer sobre conveniencia de implementacao.

## 2. Estado material e limites de aceite

O repositorio contem acervo PDF/EPUB e metadados locais sob `src/publications/`, além da automação em `scripts/publications/`; essa existencia NÃO DEVE ser interpretada como conformidade do acervo, do downloader, do buscador, da GUI, do indice global, das capas, do build ou da publicacao com este RCF. [PENDENTE-CODIGO]

Nenhuma capacidade DEVE ser declarada implementada ou aceita sem validacao material proporcional e registrada.

A fase normativa atual NÃO DEVE alterar `src/`, migrar publicacoes, modificar build/publicacao nem criar ou adaptar codigo, script ou workflow.

Cada fase tecnica somente PODE iniciar apos conclusao normativa, FT propria e autorizacao humana nova, explicita e inequivoca conforme `MN-STATE`.

## 3. Direcao tecnologica

Nenhuma linguagem, biblioteca, motor, indice, modelo, banco, runtime ou arquitetura DEVE ser escolhido por preferencia, reputacao ou conveniencia isolada.

A selecao tecnologica DEVE resultar de comparacao objetiva de qualidade, manutencao, licenca, compatibilidade, portabilidade, precisao, desempenho, memoria, instalacao, seguranca, funcionamento local, integracao, maturidade, testes, custo operacional e substituibilidade.

Node.js com TypeScript DEVE ser o eixo principal de integracao, orquestracao, configuracao e interfaces quando adequado; script proprio executado em Node.js DEVE possuir TypeScript como fonte canônica.

Python, Ruby, Rust, Java, C#, shell ou outro runtime PODEM ser utilizados em segmentos especializados quando apresentarem ganho tecnico demonstravel de desempenho, integracao, maturidade, seguranca ou adequacao ao ecossistema.

### 3.1 Bootstrap multi-runtime

Quando um comando suportado depender de runtime ou biblioteca de outra linguagem,
o repositório DEVE declarar a dependência em arquivo versionado próprio do
ecossistema e oferecer bootstrap local idempotente acionável pelos ciclos npm.
`npm install` DEVE preparar as dependências externas necessárias aos comandos
suportados; o fluxo npm que atualiza ou altera a árvore local DEVE aplicar a
mesma verificação, sem depender de execução manual implícita. [PENDENTE-CODIGO]

O bootstrap DEVE usar subscript versionado, com diagnóstico estruturado, e
instalar somente dependências declaradas e necessárias. Para o coletor de
publicações, os requisitos fixados em
`scripts/publications/requirements.txt` DEVEM ser instalados em ambiente Python
local segregado do repositório; o bootstrap NÃO DEVE instalar runtime global,
alterar `PATH`, executar coleta, abrir navegador, acessar origem remota ou
expor credenciais. [PENDENTE-CODIGO]

Ausência, versão incompatível ou falha de `python`/`pip` DEVE interromper o
bootstrap com diagnóstico acionável e sem estado parcialmente aceito. A
reexecução com manifestos inalterados DEVE reutilizar o ambiente válido ou
reconciliá-lo de forma segura; mudança de requisito DEVE ser detectada antes da
execução do comando dependente. Scripts de instalação desabilitados
explicitamente pelo usuário DEVEM permanecer desabilitados, e o comando manual
canônico de bootstrap DEVE continuar disponível. [PENDENTE-CODIGO]

TypeScript, Python, Rust, SQLite, indice invertido, indice vetorial, embeddings, modelos multilingues, reranking e ferramentas nativas PODEM integrar a avaliacao; nenhuma biblioteca, framework, banco, modelo ou servico especifico fica preselecionado sem comparacao material.

Arquitetura hibrida somente DEVE ser adotada quando o ganho verificavel superar complexidade, distribuicao, instalacao, manutencao e risco operacional adicionais.

## 4. Reutilizacao obrigatoria

A implementacao NÃO DEVE recriar algoritmos, extratores, parsers, tokenizadores, modelos, indices, tradutores ou funcoes ja oferecidas por solucao adequada.

Antes de implementar qualquer capacidade, a FT tecnica DEVE avaliar solucoes existentes quanto a funcionalidade, manutencao, testes, licenca, seguranca, precisao, desempenho, tamanho, compatibilidade, adequacao ao corpus e substituibilidade.

Codigo proprio somente DEVE existir para integracao, adaptacao, composicao, regras editoriais especificas, lacuna funcional comprovada, incompatibilidade tecnica, dependencia desproporcional ou ausencia de solucao mantida.

Tecnologias como PyMuPDF, parsers EPUB estruturais, Hugging Face Tokenizers, spaCy, Stanza, SQLite FTS5, Lucene, Xapian, Tantivy, Sentence Transformers, Cross-Encoders, FAISS, HNSW, Qdrant, LanceDB, RapidFuzz, MinHash, SimHash, LSH, Argos Translate, MarianMT, NLLB ou equivalentes PODEM integrar a matriz de avaliacao sem obrigacao de adocao.

## 5. Escopo de corpus e descoberta

A ferramenta DEVE receber `target` configuravel, percorrer recursivamente toda a arvore, suportar profundidade arbitraria, processar qualquer quantidade de arquivos dentro dos limites configurados, funcionar fora da raiz do repositorio, tolerar nomes nao padronizados e detectar arquivos novos, alterados, removidos ou duplicados.

A ferramenta NÃO DEVE depender de estrutura fixa, profundidade conhecida, nome especifico de diretorio, quantidade predeterminada, execucao no diretorio dos livros ou importacao previa em software externo.

OCR NÃO DEVE ser executado por padrao em arquivos textuais. Falha de extracao DEVE acionar rotas alternativas limitadas, registrar o problema, continuar os demais arquivos e NÃO inventar conteudo.

## 6. Publicacao logica

PDF e EPUB equivalentes DEVEM representar uma unica publicacao logica e NÃO DEVEM gerar citacoes duplicadas.

A associacao DEVE considerar, quando disponiveis, titulo, autor, idioma, editora, edicao, ISBN, ISSN, volume, numero, data, metadados, nome normalizado, hash, fingerprint, similaridade textual, estrutura e ordem dos capitulos.

Arquivos de mesmo titulo NÃO DEVEM ser fundidos quando houver diferenca material de edicao, traducao, data, conteudo, paginacao ou revisao.

Quando PDF e EPUB forem equivalentes, RECOMENDA-SE usar EPUB para estrutura, capitulos, secoes e paragrafos; PDF para paginacao e representacao editorial; alinhamento textual entre ambos; e fallback reciproco.

Associacoes incertas DEVEM permanecer separadas ou marcadas para revisao.

## 7. Extracao de PDF

A extracao de PDF DEVE preservar, quando disponiveis, paginas fisicas, numeros impressos, palavras, linhas, blocos, coordenadas, fontes, estilos, colunas, titulos, subtitulos, notas, cabecalhos, rodapes, datas, volume, numero e edicao.

A reconstrucao NÃO DEVE concatenar indiscriminadamente o texto da pagina.

Cabecalhos, rodapes e numeros de pagina DEVEM ser identificados por combinacao de repeticao, posicao, frequencia, tipografia, baixa variacao, padroes e distancia do corpo. Um elemento somente DEVE ser removido quando a confianca for suficiente.

## 8. Extracao de EPUB

A extracao de EPUB DEVE respeitar container, manifesto, spine, XHTML, `nav`, NCX, landmarks, page list, headings, capitulos, secoes, paragrafos, notas, metadados, datas, edicao, volume e numero.

A ordem DEVE seguir o spine e a estrutura semantica DEVE ser preservada.

Sem paginacao estavel, a ferramenta NÃO DEVE inventar paginas; DEVE usar pagina do PDF equivalente quando houver alinhamento confiavel; caso contrario, DEVE usar localizacao EPUB deterministica e indicar ausencia de pagina.

## 9. Reconstrucao editorial

A unidade de citacao DEVE ser o paragrafo semantico integral.

A ferramenta DEVE reconstruir paragrafos quebrados por linhas, atravessando paginas, com hifenizacao editorial, divididos por blocos, interrompidos por cabecalho ou rodape e distribuidos em colunas.

A ferramenta DEVE distinguir quebra visual de linha, quebra real de paragrafo, mudanca de pagina, mudanca de coluna, titulo, subtitulo, lista, nota, bloco de citacao, unidade editorial e mudanca de data.

A decisao DEVERIA combinar geometria, pontuacao, capitalizacao, recuo, espacamento, tipografia, continuidade sintatica, segmentacao linguistica, estrutura EPUB e contexto anterior/posterior.

Paragrafos distintos NÃO DEVEM ser unidos por heuristica isolada. Paragrafo entre paginas DEVE referenciar todas elas, preferencialmente como intervalo.

## 10. Referencias e publicacoes datadas

Cada citacao DEVE preservar, quando aplicavel, titulo, autor, capitulo, secao, pagina ou intervalo, edicao, volume, numero, data, idioma, localizacao EPUB e fonte PDF/EPUB.

A identificacao DEVE usar evidencia em ordem de confianca: estrutura explicita; metadados confiaveis; conteudo editorial; pagina de rosto, sumario ou expediente; filename; diretorio; fallback marcado.

Metadados NÃO DEVEM ser inventados.

Devocionais, revistas, jornais e periodicos DEVEM incluir data editorial ou de destinacao na referencia. A data DEVE ser associada a unidade textual vigente, nao apenas ao arquivo.

A ferramenta NÃO DEVE confundir data editorial com criacao do arquivo, modificacao, extracao, execucao ou indexacao. Datas de filesystem somente PODEM ser usadas com configuracao explicita ou confirmacao adicional.

## 11. Consulta, expansao e variantes

A consulta PODE ser palavra, expressao, frase, conceito em linguagem natural, termos obrigatorios ou exclusoes.

A expansao DEVE considerar de forma controlada traducao, flexao, lematizacao, singular/plural, genero, conjugacao, variantes ortograficas, sinonimos, locucoes, parafrases, expressoes equivalentes, formas correlatas e termos configurados manualmente.

A expansao NÃO DEVE tornar a consulta excessivamente ampla.

Cada variante DEVE registrar texto, idioma, origem, metodo, peso, confianca e relacao com a consulta original.

O usuario DEVE poder revisar, incluir, excluir, fixar expressoes, limitar idiomas, definir thresholds, usar busca literal e usar busca hibrida.

## 12. Registro da pesquisa

No inicio do Markdown de resultado do Modo Pesquisa DEVEM constar termo original, idioma original, idiomas pesquisados, modo de busca, thresholds, inclusoes, exclusoes, traducoes, flexoes, sinonimos, expressoes equivalentes, parafrases e todas as variantes efetivamente pesquisadas.

Variantes efetivamente usadas NÃO DEVEM ser omitidas. Variantes geradas e rejeitadas PODEM permanecer apenas no relatorio tecnico.

## 13. Busca hibrida

A recuperacao DEVE combinar, quando proporcional, correspondencia literal, normalizacao, busca por frase, analise morfologica, sinonimos, fuzzy matching, busca semantica multilingue, reranking contextual, filtros linguisticos e classificacao por confianca.

A busca lexical NÃO DEVE ser substituida pela semantica. A busca semantica NÃO DEVE decidir isoladamente.

RECOMENDA-SE pipeline com expansao da consulta, geracao lexical de candidatos, geracao vetorial de candidatos, uniao, fusao de rankings, reranking, analise de negacao/modalidade/numeros/datas/termos criticos, threshold, classificacao e evidencia.

Reciprocal Rank Fusion ou tecnica equivalente PODE combinar rankings heterogeneos.

## 14. Tokenizacao e representacoes

A ferramenta DEVE preservar separadamente texto original, texto estrutural, texto normalizado, tokens, lemas, offsets, fingerprints e embeddings quando usados.

A normalizacao DEVE permitir localizar a correspondencia e recuperar exatamente o texto original.

Tokenizacao, normalizacao e segmentacao NÃO DEVEM destruir acentuacao original, pontuacao relevante, grafia editorial, localizacao, referencia ou offsets.

## 15. Persistencia e indexacao

A ferramenta DEVERIA manter indice persistente e incremental.

O indice DEVE permitir processamento incremental, consultas repetidas, retomada, atualizacao, remocao de dados obsoletos, associacao PDF-EPUB, busca lexical, busca semantica, deduplicacao e rastreabilidade.

O modelo persistente DEVE armazenar publicacoes, formatos, edicoes, capitulos, secoes, paragrafos, paginas, datas, referencias, texto original, texto normalizado, tokens, fingerprints, embeddings, hashes, confianca, versao do extrator, checkpoints e pesquisas.

O Markdown NÃO DEVE ser a fonte primaria de persistencia.

## 16. Deduplicacao

Textos equivalentes apos normalizacao segura DEVEM compartilhar uma unica citacao logica. A normalizacao PODE tratar espacos, quebras visuais, hifenizacao, Unicode, aspas, travessoes, capitalizacao, pontuacao nao material e artefatos editoriais.

Variacoes minimas PODEM ser consolidadas mediante n-gramas, Jaccard, MinHash, SimHash, Levenshtein, Damerau-Levenshtein, Jaro-Winkler, LCS, RapidFuzz ou equivalente, embeddings e alinhamento de tokens.

A ferramenta DEVE verificar diferencas criticas, incluindo negacao, modalidade, condicao, agente, objeto, datas, numeros, nomes, intensidade, conclusao e significado.

Diferenca pequena em caracteres NÃO DEVE implicar equivalencia semantica.

Resultados DEVEM poder ser classificados como consolidar automaticamente, manter separados ou revisao recomendada.

Antes de adicionar uma citacao, a ferramenta DEVE verificar se ela ja existe no resultado ou no Markdown da mesma pesquisa. Se ja existir, NÃO DEVE criar novo bloco, DEVE adicionar somente referencia ausente e NÃO DEVE repetir referencia.

Compilacoes, antologias e republicacoes DEVEM gerar multiplas referencias sob uma unica citacao quando o texto for equivalente.

## 17. Alinhamento PDF-EPUB

Quando ambos existirem, a ferramenta DEVERIA alinhar estrutura EPUB e paginacao PDF.

O alinhamento PODE combinar hashes, ancoras exatas, n-gramas, fingerprints, similaridade lexical, embeddings, LCS, programacao dinamica, Needleman-Wunsch, Smith-Waterman, Dynamic Time Warping e alinhamento monotonico.

A ordem textual DEVERIA ser explorada para reduzir ambiguidades. Cada associacao DEVE possuir confianca.

## 18. Identificacao de idioma

O idioma DEVE ser inferido por combinacao de metadados, deteccao documental, deteccao por paragrafo, vocabulario, modelo de identificacao e contexto.

A ferramenta DEVE suportar conteudo misto e NÃO DEVE depender exclusivamente de filename para identificar idioma.

## 19. Traducao

Toda citacao original em `en-US` DEVE ser imediatamente seguida por traducao `pt-BR`.

A traducao DEVE abranger somente o texto, NÃO DEVE traduzir referencia, DEVE usar bloco de citacao, DEVE ser identificada como **Traducao livre**, DEVE preservar sentido e tom e DEVE permanecer separada do original.

Traducao local open source DEVERIA ser preferida quando possuir qualidade suficiente.

API publica ou gratuita PODE ser usada somente quando autorizada, estavel, adequada ao volume, compativel com privacidade, configuravel e resiliente.

Conteudo NÃO DEVE ser enviado a terceiros sem autorizacao explicita.

Traducoes DEVEM usar cache por hash, idiomas e versao do tradutor. Falha de traducao NÃO DEVE remover a citacao original.

No Modo Conversa, fonte em idioma diferente do dialogo DEVE preservar sempre o trecho original; traducao adicional DEVE permanecer imediatamente vinculada, identificada e separada, sem substituir a prova nem atribuir a fonte formulacao exclusiva da traducao.

Ambiguidade ou termo tecnico, juridico, normativo ou semanticamente sensivel DEVE preservar o termo original, e divergencia relevante entre traducoes existentes DEVE ser explicitada.

## 20. Markdown unico por pesquisa

Esta secao rege exclusivamente o Modo Pesquisa; registro conversacional segue o contrato de sessao dos §§51-57 e NÃO DEVE ser confundido com o Markdown consolidado de ocorrencias.

Cada pesquisa individual DEVE possuir exatamente um Markdown principal.

O Markdown DEVE consolidar consulta, variantes, metadados, resultados em `pt-BR`, resultados em `en-US`, traducoes, referencias, contagens e resumo.

A identidade da pesquisa DEVE considerar consulta original, idiomas, inclusoes, exclusoes, modo, modelos, configuracoes e thresholds.

O arquivo NÃO DEVE misturar pesquisas materialmente distintas.

Atualizacoes DEVEM ser idempotentes, atomicas, recuperaveis e deterministicas. RECOMENDA-SE escrever em arquivo temporario validado antes da substituicao.

## 21. Estrutura Markdown de resultado

A estrutura do Markdown DEVE ser equivalente a:

```markdown
# Resultados da pesquisa: <consulta>

## Consulta e variantes

- Termo original: <termo>
- Idioma: <idioma>
- Modo: <modo>
- Thresholds: <valores>
- Variantes: <por idioma e categoria>
- Exclusoes: <termos>

## Portugues - Brasil

### <Publicacao>

#### Citacao <n>

> <paragrafo>

**Referencias:**

- *<Livro>*, cap. "<Capitulo>", p. <pagina>.
- *<Devocional>*, meditacao de <data>, p. <pagina>.
- *<Revista>*, v. <volume>, n. <numero>, <periodo>, p. <pagina>.
- *<Jornal>*, <data>, p. <pagina>.

---

## Ingles - Estados Unidos

### <Publicacao>

#### Citacao <n> - Original

> <texto>

**Referencias:**

- ...

##### Traducao livre

> <traducao>

---
```

A referencia DEVE aparecer somente junto ao original. Citacoes DEVEM possuir separacao visual consistente.

## 22. Atualizacao de Markdown existente

Quando o arquivo da mesma pesquisa existir, a ferramenta DEVE validar identidade, analisar estruturalmente o Markdown, recuperar citacoes e referencias, reconstruir fingerprints, comparar novos resultados, adicionar apenas conteudo ausente, preservar conteudo valido, atualizar contagens e ordenar deterministicamente.

A analise NÃO DEVE depender apenas de busca textual bruta.

Identificadores PODEM ser preservados por front matter, comentarios HTML, sidecar, indice ou mecanismo equivalente. Metadados tecnicos NÃO DEVEM prejudicar a leitura.

## 23. Confianca e auditabilidade

Cada inferencia relevante DEVE possuir evidencia e confianca separadas, incluindo extracao, estrutura, titulo, capitulo, pagina, data, idioma, associacao PDF-EPUB, correspondencia lexical, correspondencia semantica, deduplicacao e traducao.

Classificacoes PODEM incluir confirmado, alta confianca, provavel, revisao recomendada, indeterminado e rejeitado.

A ferramenta NÃO DEVE apresentar inferencia como certeza sem evidencia.

No Modo Conversa, confianca da recuperacao, fidelidade da citacao, validade da localizacao, suficiência da prova, completude da referencia, traducao e conclusao DEVEM permanecer separadamente auditaveis.

## 24. Failsafe

Failsafe significa concluir todo o trabalho processavel, isolar falhas, preservar resultados validos e informar precisamente o que nao foi concluido.

A ferramenta DEVE possuir isolamento por arquivo, checkpoints, retomada, cache, timeouts, tentativas limitadas, backoff limitado, fallbacks, fila de problemas, logs estruturados, escrita atomica, recuperacao e resumo final.

A ferramenta NÃO DEVE entrar em loop infinito, tentar indefinidamente, interromper toda a colecao por falha isolada, ocultar falhas, inventar dados, descartar arquivo silenciosamente, duplicar resultados apos retomada ou corromper saida existente.

Cada fallback DEVE declarar condicao, limite, resultado, motivo e proximo estado.

Componente conversacional, LLM, tradutor ou reranker indisponivel NÃO DEVE fabricar resposta, citacao, referencia ou localizacao; a capacidade independente DEVE continuar quando segura e a limitacao aplicavel DEVE ser informada objetivamente.

## 25. Desempenho e configuracao operacional

A ferramenta DEVE evitar carregar toda a colecao simultaneamente.

RECOMENDA-SE streaming, lotes, filas, concorrencia limitada, workers, cache, indexacao incremental, persistencia e processamento por fases.

A concorrencia DEVE respeitar CPU, memoria, disco, APIs e estabilidade dos extratores.

Configuracoes DEVEM incluir workers, lotes, cache, memoria, timeout, tentativas, thresholds, idiomas, tradutor, logs e rede.

## 26. Seguranca e privacidade

A operacao DEVE ser local por padrao.

A ferramenta NÃO DEVE enviar publicacoes completas externamente, executar JavaScript de EPUB, confiar em filenames, permitir path traversal, extrair fora de area controlada, sobrescrever sem validacao, registrar conteudo integral desnecessariamente ou expor paths/dados sensiveis.

EPUBs DEVEM ser tratados como arquivos nao confiaveis.

A extracao DEVE proteger contra Zip Slip, expansao excessiva, bomba de compressao, entidades externas, conteudo malformado, loops e arquivos abusivos.

Memoria de conversa, consulta, decomposicao, trecho recuperado, referencia, traducao e diagnostico DEVEM seguir configuracao explicita de privacidade e retencao, com minimizacao, isolamento por sessao e exclusao controlada.

Rastreabilidade NÃO DEVE armazenar raciocinio interno privado da IA, segredo, credencial ou conteudo integral desnecessario do acervo.

## 27. CLI e saida

A interface de pesquisa DEVERIA ser equivalente a:

```text
search-publications --target <diretorio> --query "<termo ou conceito>" --languages pt-BR,en-US --output <pesquisa.md>
```

A CLI DEVERIA permitir indexar, pesquisar, reconstruir indice, listar publicacoes, inspecionar associacoes, exibir variantes, definir thresholds, selecionar tradutor, operar offline, retomar, atualizar resultado, filtrar autor, filtrar idioma, filtrar data, filtrar tipo e gerar diagnostico.

A configuracao DEVE aplicar precedencia explicita: CLI, arquivo, ambiente e padroes seguros.

Interface que exponha ambos os modos DEVE exigir selecao inequívoca entre `search` e `conversation`; default, alias ou comando abreviado NÃO DEVE alterar silenciosamente a semantica escolhida.

A saida DEVE ser sucinta, colorida quando suportado, desativavel, legivel por humanos, processavel por IA, disponivel em formato estruturado e sem inundacao de logs.

Saida destinada a IA ou automacao do repositorio DEVE seguir `MN-CMD` e `MN-OUT` quando integrada ao contrato `agent:*`.

## 28. Testes obrigatorios futuros

A implementacao DEVE possuir testes para PDF simples, cabecalho/rodape, multiplas colunas, pagina atravessada, hifenizacao, paginacao romana, EPUB com `nav`, EPUB com NCX, EPUB sem pagina, associacao PDF-EPUB, edicoes distintas, diretorios profundos, busca literal, morfologia, sinonimos, parafrases, busca bilingue, polissemia, negacao, ranking hibrido, deduplicacao exata, variacao minima, diferenca material, multiplas referencias, compilacoes, devocionais, revistas, jornais, traducao, cache, retomada, escrita atomica, Markdown existente, falhas de extrator, falhas de traducao, timeout, arquivo corrompido, Zip Slip, bomba de compressao, seguranca e desempenho.

Fixtures DEVEM incluir arquivos reais autorizados, arquivos emulados e arquivos gerados automaticamente. Testes externos DEVEM permanecer separados e opcionais.

O Modo Conversa DEVE adicionar conjuntos determinísticos e avaliações verificaveis de fidelidade literal, localizacao, completude de referencia, contexto, relacao multifuente, traducao vinculada, abstencao, alucinacao, metadado incompleto, degradacao e desempenho proporcional.

## 29. Ordem de implementacao futura

A FT tecnica DEVE executar em etapas validadas sequencialmente: analise do corpus; avaliacao de linguagens, bibliotecas e modelos; contratos; descoberta; modelo de publicacao; extracao EPUB; extracao PDF; limpeza; reconstrucao; referencias e datas; alinhamento; persistencia; tokenizacao; indexacao lexical; indexacao semantica; expansao bilingue; recuperacao hibrida; reranking; deduplicacao; consolidacao; localizacao e validacao de citacoes; traducao; Markdown; composicao probatoria; sessao conversacional; interface de modos; failsafe; testes; otimizacao; documentacao; validacao.

Cada etapa DEVE ser validada antes da seguinte.

## 30. Criterios de aceite tecnico

A implementacao somente DEVE ser considerada concluida quando percorre diretorios arbitrarios, processa PDF e EPUB textuais, associa formatos equivalentes, distingue edicoes, reconstroi paragrafos, identifica titulo/capitulo/pagina/data, registra variantes pesquisadas, combina busca lexical e semantica, traduz citacoes inglesas, gera um unico Markdown por pesquisa, consolida citacoes repetidas, acumula referencias, preserva diferencas materiais, oferece selecao inequívoca entre Pesquisa e Conversa, fundamenta afirmacoes conversacionais com prova verificavel, atualiza idempotentemente, retoma apos falhas, nao entra em loop, nao fabrica metadados, citacoes ou localizacoes, registra confianca, registra arquivos nao processados e executa testes verificaveis.

Nenhuma capacidade DEVE ser declarada como aceita sem evidencia de validacao executada.

## 31. Entregaveis futuros

A entrega funcional DEVE conter projeto funcional, fontes, configuracao, CLI, GUI aplicavel, persistencia/indices, testes, conjuntos de avaliacao, fixtures, documentacao, exemplo de Markdown consolidado, exemplo de sessao probatoria e relatorio sucinto com tecnologia escolhida, alternativas avaliadas, bibliotecas reutilizadas, codigo proprio e justificativa, arquitetura, modelos, indices, modos, criterios de uso de LLM, contrato de citacao/referencia/traducao, comandos, testes, metricas, resultados, limitacoes, niveis de confianca, fallbacks e arquivos nao processados.

## 32. README, badges e metadados

`README.md` DEVE existir, ser ultrassucinto, informativo e nao normativo.

O README DEVE identificar o projeto sem anunciar como implementado o que estiver apenas planejado, e DEVE apontar para `RCF.md` e `AGENTS.md`.

Badges e indicadores DEVEM acompanhar a evolucao real do escopo, licenca, validacoes, linguagens, runtimes, builds, cobertura, pacote, release, manutencao e compatibilidade. Indicador dinamico somente DEVE existir quando a fonte verificavel correspondente existir. Indicador estatico PODE informar estado documental, planejamento ou licenca quando verdadeiro.

Badges NÃO DEVEM apresentar aprovacao, cobertura, compatibilidade, build, release ou disponibilidade nao verificada; DEVEM ser atualizados ou removidos quando obsoletos.

Autoria, repositorio e licenca DEVEM vir de artefatos reais do repositorio. Dado ausente NÃO DEVE ser inventado e DEVE permanecer como pendencia.

## 33. FTs e continuidade

FT normativa e FT tecnica DEVEM permanecer segregadas em `.ia.rules/continue.ia`.

FT normativa DEVE cobrir RCF, README, validacao documental, remocao de artefato transitorio aplicavel, commit e push.

FT tecnica DEVE permanecer pendente ate autorizacao humana explicita e DEVE cobrir avaliacao tecnologica, arquitetura, codigo, bibliotecas, dependencias, testes, builds, integracoes, automacoes, CI/CD e publicacao quando aplicaveis.

A conclusao normativa NÃO autoriza implementacao de codigo.

## 34. Arquitetura compartilhada e perfis operacionais

O nucleo de dominio, descoberta, extracao, normalizacao, segmentacao, indexacao, busca, persistencia, deduplicacao, traducao e geracao de resultados NÃO DEVE depender de DOM, framework visual, protocolo HTTP ou pressuposto de servidor.

CLI, GUI local e eventual adaptador web publico DEVEM compor o mesmo nucleo por interfaces estaveis e NÃO DEVEM duplicar regra de negocio. Modo Pesquisa e Modo Conversa DEVEM compor recuperacao, evidencia e persistencia comuns por contratos estáveis, mantendo orquestracao e apresentacao especificas.

O perfil `local` DEVE permanecer primario, completo, funcional sem navegador, servidor publico, servico remoto ou rede obrigatoria.

A GUI local DEVE ser leve, profissional, direta, responsiva, acessivel, offline e funcionalmente completa para as capacidades que expuser.

O perfil `public-future` DEVE existir apenas como contrato de extensao; autenticacao publica, multiusuario massivo, quotas, rate limiting, escalabilidade horizontal, filas distribuidas, isolamento entre tenants, balanceamento e infraestrutura de producao NÃO DEVEM ser implementados sem autorizacao especifica.

Perfis operacionais DEVEM especializar configuracao, limites e adaptadores centralizados, sem condicionais dispersas ou reescrita do nucleo.

Cada servico relevante DEVE declarar capacidades, requisitos, limites, cancelabilidade, concorrencia, consumo esperado, plataformas, runtimes e compatibilidade de perfil.

CPU, memoria, workers, filas, tamanho de consulta, duracao, cache, rede e demais recursos DEVEM possuir limites centrais, tipados, validados, documentados e com defaults seguros.

CLI, GUI, scripts, paths, processos, filesystem, encoding, sinais, shells e integracao entre runtimes DEVEM operar de forma consistente nas plataformas suportadas; diferenca inevitavel DEVE usar adaptador explicito.

Componente auxiliar em outro runtime DEVE declarar entrada, saida, erro, serializacao, versao, timeout, cancelamento, codigo de retorno, descoberta e diagnostico.

Ausencia ou incompatibilidade de runtime auxiliar NÃO DEVE inutilizar capacidade independente; fallback, desabilitacao localizada ou falha acionavel DEVE preservar o restante do sistema.

## 35. GUI local, dependencias visuais e offline

HTML DEVE prover estrutura e conteudo essencial; CSS ou Sass DEVE prover apresentacao; TypeScript somente DEVE aprimorar estado ou interacao nao atendidos adequadamente por recursos nativos.

Quando houver estilização processada, Sass DEVE ser compilado e fonte `.scss` desnecessaria NÃO DEVE integrar o artefato final.

WebAwesome, Font Awesome, templates, frameworks leves e componentes consolidados PODEM ser adotados somente quando reduzirem custo liquido sem degradar desempenho, portabilidade, acessibilidade, seguranca ou controle.

Biblioteca visual NÃO DEVE ser incorporada integralmente quando apenas subconjunto for utilizado; icones, estilos, fontes, componentes e scripts DEVEM ser selecionados sob demanda.

CDN PODE ser usada quando o ganho de cache, latencia, peso, disponibilidade e manutencao superar os riscos de privacidade, integridade e dependencia externa.

Recurso remoto critico DEVE possuir fallback local, vendorizacao, cache ou degradacao funcional que preserve a operacao offline.

GUI DEVE minimizar JavaScript, CSS, requests, parsing, hidratacao, memoria e processamento por carregamento condicional, lazy loading, tree shaking ou code splitting somente quando houver ganho verificavel.

Validacao da GUI DEVE cobrir nucleo isolado, CLI, GUI, offline, teclado, foco, contraste, toque, overflow, responsividade, carregamento seletivo, limites de recursos e ausencia de duplicacao de negocio.

## 36. Estrategias de segmentacao e RAG proporcional

RAG DEVE ser tratado como conjunto modular de tecnicas opcionais e NÃO DEVE impor embeddings, banco vetorial, LLM, servico remoto ou modelo especifico quando mecanismo deterministico produzir resultado equivalente ou superior.

Antes de adotar tecnica de RAG, a FT tecnica DEVE inspecionar o repositorio e medir baseline de ingestao, extracao, normalizacao, segmentacao, enriquecimento, representacao, indexacao, recuperacao, expansao, busca hibrida, filtros, reranking, composicao, validacao, cache, incremento e observabilidade.

Cada estrategia DEVE declarar identidade, versao, configuracao, aplicabilidade, entradas, saidas, metadados, limites, custo, metricas, validacao, serializacao e diagnostico.

O pipeline DEVE suportar selecao explicita ou deterministica por colecao, documento, genero, idioma, campo, consulta, citacao, tarefa ou perfil, sempre com decisao rastreavel e override manual.

Parametros de tamanho minimo, ideal e maximo, unidade, overlap, limite estrutural, tolerancia e expansao contextual DEVEM ser configuraveis por estrategia ou perfil.

Estrategias classicas DEVEM permanecer de primeira classe quando aplicaveis: tamanho fixo, sentenca, paragrafo, pagina, bloco, secao, titulo, capitulo, artigo, inciso, nota, delimitador, tipografia, markup, metadado, regex, janela deslizante e divisao recursiva.

Regex NÃO DEVE ser tratada como mecanismo inferior; quando adequada, DEVE permanecer configuravel, testavel, composivel e preferivel a metodo probabilistico mais caro ou menos deterministico.

Estrategias linguisticas PODEM usar sentenca, oracao, paragrafo semantico, topico, entidade, mudanca discursiva e estrutura gramatical, respeitando idioma, abreviacao, citacao, nota e referencia.

Estrategias semanticas PODEM usar similaridade, mudanca de topico, embedding, agrupamento e coerencia discursiva quando seus limites forem rastreaveis e reproduziveis.

LLM PODE delimitar estrutura, topico, unidade argumentativa ou citacao somente quando demonstrar ganho liquido; NÃO DEVE alterar, resumir ou reescrever silenciosamente a fonte.

Limite produzido por LLM DEVE apontar ao texto original, ser validavel, armazenavel, reutilizavel e versionado; custo, latencia, privacidade, disponibilidade e variacao DEVEM integrar a decisao.

Segmentacao bibliografica DEVE preservar titulo, autoria, resumo, capitulo, secao, pagina, nota, citacao, referencia, bibliografia, edicao e volume quando presentes.

Citacao NÃO DEVE ser dividida de modo a perder atribuicao, fonte, inicio, fim, pagina, nota, referencia, qualificador ou contexto necessario.

Citacao extensa PODE formar chunk proprio ligado aos vizinhos; citacao curta DEVE preservar o paragrafo e a referencia associada.

Overlap PODE usar caracteres, palavras, tokens, sentencas, paragrafos ou unidades estruturais; DEVE preservar continuidade sem duplicacao massiva ou crescimento desproporcional.

Chunk DEVE poder relacionar predecessor, sucessor, pai, filho, vizinho, secao, documento, citacao e referencia por tipos explicitos, sem depender apenas de proximidade vetorial.

Representacao hierarquica PODE seguir colecao, documento, edicao, capitulo, secao, paragrafo e sentenca; recuperacao PODE localizar unidade pequena e expandir seletivamente ao pai ou vizinho.

O mesmo documento PODE manter segmentacoes paralelas quando tarefas exigirem granularidades incompatíveis; cada representacao DEVE registrar estrategia, versao e configuracao.

Resultados de segmentacoes paralelas DEVEM ser deduplicados ou aglutinados conscientemente, e o custo adicional DEVE ser comparado ao ganho.

Chunks virtuais PODEM ser compostos durante a consulta a partir de unidades, hierarquia e vizinhanca, sem materializar combinacoes irrestritas.

Chunking adaptativo PODE variar por densidade, idioma, estrutura, consulta, relevancia ou confianca somente por criterios verificaveis e reproduziveis.

Cada chunk DEVE preservar documento, edicao ou versao, idioma efetivo, estrategia, hierarquia, offsets e, quando disponiveis, pagina, bloco, linha ou coordenada que permitam conferir o trecho.

Texto canonico citado DEVE permanecer imutavel e separado de limpeza, normalizacao, tokens, embeddings, resumos e outros derivados.

Mudanca de extrator, regex, tokenizer, modelo, estrategia ou configuracao que altere chunks DEVE invalidar deterministicamente somente indices afetados.

Duplicata, quase duplicata, traducao, edicao e citacao repetida DEVEM permanecer classes distintas; igualdade textual NÃO DEVE apagar ocorrencias bibliograficamente independentes.

## 37. Busca multilingue, roteamento e aglutinacao

Representacao lexical, semantica e hibrida DEVE preservar idioma-fonte, variante, terminologia e diferenca conceitual.

Consulta cruzada entre idiomas PODE usar traducao, embedding multilingue, lexico, ontologia, sinonimo ou combinacao, mas cada expansao DEVE registrar origem, relacao e confianca.

Traducao aproximada NÃO DEVE ser tratada como identidade conceitual plena.

Tokenizacao, segmentacao, stemming, lematizacao e sinonimos DEVEM considerar o idioma efetivo do trecho; documento misto NÃO DEVE ser forçado a idioma unico.

Traducoes e originais DEVEM permanecer relacionados sem fusao como documento unico.

Indices lexicais, invertidos, semanticos, por campo, entidade, referencia e relacao PODEM coexistir como capacidades independentes.

Busca hibrida DEVE preservar correspondencia exata relevante, permitir pesos configuraveis e comparar estrategias antes da fusao.

Roteamento PODE selecionar chunk, indice, filtro, expansao ou reranker por intencao e contexto, mas DEVE possuir fallback geral e NÃO DEVE excluir silenciosamente estrategia relevante sob baixa confianca.

Recuperacao DEVE iniciar pelo contexto minimo suficiente e PODE expandir por vizinhanca, hierarquia, relacao, referencia ou documento.

Reranking deterministico, estatistico, cross-encoder ou por LLM somente PODE tornar-se padrao quando elevar precisao ou cobertura de forma mensuravel.

Diversificacao DEVE evitar concentracao em chunks redundantes sem ocultar ocorrencias bibliograficamente significativas.

Resultado de citacao direta DEVE ser conferivel contra a fonte; traducao, resumo, reconstrucao ou inferencia NÃO DEVE ser rotulada como transcricao literal.

Aglutinacao PODE agrupar por obra, autor, referencia, trecho equivalente, traducao, citacao comum, topico, entidade ou relacao, mas DEVE preservar ocorrencia, fonte, idioma, edicao, localizacao, divergencia e criterio de agrupamento.

Trechos distintos NÃO DEVEM ser combinados como uma unica citacao nem divergencias entre versoes ou traducoes podem ser ocultadas.

Quando IA for usada, a composicao DEVE selecionar evidencia relevante, controlar duplicacao, respeitar orcamento de tokens e manter acesso ao original.

Modelo NÃO DEVE completar citacao, pagina, autor, obra ou referencia por plausibilidade; evidencia ausente, insuficiente ou conflitante DEVE produzir abstencao explicita.

Prompt, tokenizer, embedding, reranker e LLM DEVEM ser substituiveis por contrato proporcional.

LLM PODE auxiliar expansao, desambiguacao, classificacao, reranking, sintese ou conexao semantica somente quando houver ganho demonstravel; mecanismo deterministico ou especializado mais adequado DEVE prevalecer e a pesquisa independente NÃO DEVE ser inutilizada por ausencia de LLM.

## 38. Equivalencia numerica bidirecional

Consulta por algarismo DEVE localizar numero por extenso semanticamente equivalente e consulta por extenso DEVE localizar algarismo equivalente, sem duplicacao manual.

Numero por extenso DEVE ser interpretado conforme idioma e variante do trecho ou consulta.

Algarismo e expressao por extenso DEVEM convergir para valor canonico derivado, preservando texto original, offsets, idioma, evidencia e forma de destaque.

Normalizacao numerica DEVE considerar, quando linguisticamente aplicavel, cardinais, sinais, separadores de milhar e decimal, conectivos, hifenizacao, flexoes e variantes ortograficas legitimas.

ISBN, DOI, ano, edicao, volume, capitulo, pagina, codigo e identificador NÃO DEVEM ser expandidos indiscriminadamente; campo, formato, idioma e contexto DEVEM controlar a decisao.

Correspondencia literal exata PODE receber peso superior a equivalencia numerica quando isso preservar precisao.

Expansao numerica DEVE integrar indexacao e consulta por mecanismo controlado, cacheavel e sem crescimento combinatorio.

Valor desconhecido, ambiguo, invalido ou em idioma nao suportado NÃO DEVE interromper a busca; o termo original DEVE seguir pelos mecanismos restantes.

Validacao DEVE cobrir ambos os sentidos, idiomas suportados, numeros simples e compostos, sinais, decimais, separadores locais, grafias validas, ambiguidades e contextos bibliograficos que nao admitem expansao.

## 39. Avaliacao, metricas e adocao reversivel

Baseline DEVE ser medido antes de alterar segmentacao, indice, expansao, recuperacao, reranking ou aglutinacao.

Avaliacao DEVE medir, conforme aplicabilidade, precisao, recall, MRR, nDCG, cobertura de citacoes, fidelidade literal, validade de localizacoes, completude de referencias, associacao entre afirmacao e prova, completude contextual, acerto multilingue, qualidade da aglutinacao, contradicoes detectadas, abstencoes corretas, falsos positivos, falsos negativos, latencia, tokens, memoria, armazenamento, tempo de indexacao e custo operacional.

Chunking DEVE ser comparado por preservacao semantica, ruptura de citacao, redundancia de overlap, distribuicao de tamanho, localizacao, quantidade recuperada e contexto necessario.

Casos DEVEM incluir documentos curtos, longos, estruturados, irregulares, monolingues, multilingues, OCR imperfeito, notas, referencias, edicoes, traducoes e consultas ambiguas.

Cada estrategia DEVE ser medida isoladamente e nas combinacoes propostas.

Avaliacao humana PODE complementar metrica automatica mediante amostra verificavel e criterios explicitos.

Tecnica somente DEVE tornar-se padrao quando beneficio recorrente superar processamento, armazenamento, memoria, latencia, manutencao, privacidade e risco, sem regressao relevante.

Adocao DEVE ser incremental, observavel, versionada, comparavel e reversivel.

Catalogo de estrategias DEVE registrar aprovadas, rejeitadas e experimentais, parametros, custos, idiomas, formatos, limitacoes, fallbacks, metricas, versionamento e reindexacao.

## 40. Publicacao institucional estatica

O produto DEVE possuir pagina institucional ultrassucinta publicada no GitHub Pages por workflow proprio, sem depender implicitamente de tema, build automatico ou convencao padrao da plataforma.

A pagina DEVE explicar finalidade, natureza das publicacoes, formatos e forma geral de acesso, sem promocao excessiva, documentacao longa ou secao redundante.

A pagina DEVE ser profissional, elegante, responsiva, acessivel e coerente, sem poluicao visual, animacao excessiva ou dependencia desproporcional.

Logica cliente nova DEVE usar TypeScript; estilização processada DEVE usar Sass.

Font Awesome e WebAwesome PODEM ser priorizados quando agregarem valor e somente o subconjunto usado DEVE integrar build ou runtime.

HTML, CSS, JavaScript, fontes, icones e imagens DEVEM ser reduzidos ao necessario, cacheados, comprimidos, minificados e invalidados de forma coerente.

A pagina NÃO DEVE listar, expor ou vincular o indice global, arquivos de publicacao, URLs diretas ou diretorios de distribuicao, inclusive por botao, ancora oculta, metadado visual ou lista gerada.

A ausencia de links na pagina NÃO DEVE impedir que indice, publicacoes e assets integrem o artefato e permaneçam acessiveis diretamente por URL publica conhecida.

Paths de scripts, estilos, fontes, imagens e assets DEVEM funcionar em dominio proprio e em subdiretorio de projeto do GitHub Pages.

## 41. Estrutura canonica do acervo

A origem local DEVE ser `./src/publications/` e a raiz publica DEVE ser `/publications/`.

Cada publicacao DEVE ocupar `/publications/<acronimo-autor>/<language>/<tipo>/<slug-titulo>/`, onde `<tipo>` e classificacao logica e nao formato fisico e `<slug-titulo>` e segmento URI ASCII deterministico derivado do titulo editorial.

O slug de rota DEVE usar somente `[a-z0-9]+(?:-[a-z0-9]+)*`: converter o titulo para minusculas, decompor Unicode, remover acentos, diacriticos e caracteres especiais, substituir espacos por hifens, colapsar hifens repetidos e remover hifens nas extremidades. Caractere sem transliteracao ASCII e titulo cujo resultado fique vazio DEVEM receber fallback causal deterministico; limite de portabilidade DEVE truncar com sufixo de hash, sem colisao silenciosa.

Titulo editorial e slug de rota possuem autoridades distintas: `book.title`, metadados e evidencias DEVEM preservar a forma editorial, enquanto diretorio, rota publica e URL DEVEM usar exclusivamente o slug. Titulo editorial NÃO DEVE ser reconstruido do slug.

PDF, EPUB, metadados, capa e demais assets do mesmo titulo DEVEM permanecer no mesmo diretorio logico.

Formato ou extensao diferente NÃO DEVE criar diretorio separado para a mesma identidade editorial.

CONTRADICAO DETECTADA: subdiretorio intermediario `assets/<basename-publicacao>/` vs agrupamento final de todos os arquivos no diretorio canônico do titulo - Aplicando o agrupamento final, posterior e mais completo.

Cada arquivo diretamente associado DEVE usar `<acronimo-titulo>.<extensao>`; qualificador adicional PODE ser usado somente quando deterministico, semanticamente necessario e nao redundante.

O acronimo DEVE derivar exclusivamente do titulo normalizado, ignorar tags confirmadas, ser estavel e usar a mesma regra em migracao, download, indexacao e publicacao.

Trecho entre parenteses DEVE ser classificado por evidencia como titulo legitimo, tag, edicao ou qualificador; regra cega NÃO DEVE remove-lo.

Tag confirmada DEVE sair do titulo e do acronimo e ser preservada no indice; duvida DEVE preservar o titulo e registrar revisao.

Colisao de destino DEVE comparar SHA-256 integral: hash igual elimina copia redundante; hash diferente preserva variante como `<acronimo-titulo>.<hash-curto>.<extensao>`.

Hash curto DEVE derivar do SHA-256, ter comprimento minimo desambiguador e expandir somente diante de colisao do prefixo.

Arquivo com hash diferente NÃO DEVE ser sobrescrito ou descartado; contador dependente de ordem NÃO DEVE substituir identificador deterministico.

Metadado local DEVE ser associado por conteudo e relacao, nao somente por filename; quando normalizado, DEVE usar nome aderente ao acronimo sem perda.

Compatibilidade com path antigo somente PODE existir para URL publica comprovadamente consumida e DEVE usar redirecionamento, alias ou mapa finito, sem duplicacao indefinida; na ausencia de consumo publicado comprovado, o path Unicode anterior DEVE ser removido depois da migracao validada.

## 42. Migracao e downloader

A migracao futura DEVE ser executada por script temporario, idempotente, verificavel, retomavel e removivel apos aceite.

Antes de mover, o migrador DEVE inventariar bytes, paths, metadados, URLs, hashes, idiomas, autores, tipos, titulos, tags, variantes e colisoes.

O migrador DEVE agrupar identidade editorial, preservar titulo, calcular acronimo e slug, criar destino, mover correlatos, renomear diretorios e rotas, atualizar referencias e validar contagem, bytes e hashes.

Falha NÃO DEVE deixar estado parcial silencioso; checkpoint, temporario, backup e rollback DEVEM preservar recuperacao.

`scripts/publications/baixar.py` DEVE possuir RCF especifico em `scripts/publications/RCF.md`, subordinado a este RCF; automação operacional e requisitos do coletor NÃO DEVEM integrar `src/` nem o artefato do GitHub Pages. [PENDENTE-CODIGO]

O downloader DEVE baixar diretamente na estrutura canonica, reutilizar diretorio da mesma identidade, agrupar formatos/assets, normalizar titulo/tags/acronimo, derivar o mesmo slug RFC 3986 usado pelo migrador e impedir sobrescrita destrutiva.

O downloader DEVE preservar variante material, produzir destino deterministico, gerar ou atualizar metadados/indices e NÃO DEVE recriar a estrutura legada.

Alteracao do downloader DEVE preservar cabecalho autoral/licenca e receber testes de path, colisao, repeticao, falha, retomada e metadado.

### 42.1 Escopo de aquisição e identidade

O coletor de `egwwritings.org` DEVE preservar integralmente o suporte a Ellen
G. White e ampliar a descoberta às coleções públicas `Biblioteca dos Pioneiros
Adventistas`, identificada no catálogo observado por `pt/1055`, e `Adventist
Pioneer Library`, identificada por `en/15`.

Coleção NÃO DEVE ser tratada como autor. Identidade de publicação DEVE combinar
identificador remoto estável quando disponível, coleção, autor, idioma, tipo,
título editorial, edição/versão e origem; obra homônima de autor ou edição
distintos NÃO DEVE ser fundida.

O catálogo público estruturado consumido pela aplicação DEVE ser preferido a
parsing visual. Lista fixa de autores, tipos ou obras somente PODE atuar como
fixture de teste ou fallback finito versionado e NÃO DEVE declarar coleção
completa.

Somente conteúdo editorial em `pt-BR` e `en` PODE ser incorporado. Alias
`pt`, `pt_BR` ou equivalente comprovado DEVE projetar-se em `pt-BR`; alias
inglês sem variante material DEVE projetar-se em `en`. Valor original e valor
normalizado DEVEM permanecer registrados, e variante material NÃO DEVE ser
fundida por alias.

O segmento de path DEVE continuar ASCII/minúsculo: `pt-BR` projeta-se como
`pt-br` e `en` como `en`. O acervo legado `en-us` DEVE ser reconhecido como
alias local durante a transição e migrado atomicamente para `en` somente após
prova de ausência de variante material, sem download ou grupo duplicado.

Cada autor DEVE receber chave autoral determinística na estrutura canônica
global; o diretório do coletor sob `egw` identifica o provedor/adaptador e NÃO
autoriza armazenar autores pioneiros como se fossem Ellen G. White.

### 42.2 Elegibilidade e precedência de formatos

Para uma edição elegível, a precedência DEVE ser EPUB nativo, PDF nativo e,
somente quando nenhum dos dois existir, conteúdo textual oficial de leitura
on-line.

Quando EPUB e PDF nativos existirem, ambos DEVEM ser preservados no mesmo grupo
editorial. Áudio, vídeo, imagem isolada, bundle, HTML bruto, interface e
artefato não editorial NÃO DEVEM ser incorporados.

Ausência de download nativo NÃO autoriza extração por si só. Conteúdo textual
somente PODE ser adquirido quando for público sem contorno, possuir identidade,
ordem e completude verificáveis e permitir separação determinística entre corpo
editorial e aplicação.

### 42.3 Preflight incremental e idempotência

Antes de descobrir novamente uma unidade conhecida, solicitar ativo, extrair,
converter ou reindexar, o coletor DEVE executar preflight progressivo por:

1. ledger/índice local e estado da publicação;
2. identificador remoto e metadados persistidos;
3. existência, formato e tamanho do arquivo canônico;
4. ETag, `Last-Modified`, tamanho ou hash remoto quando disponíveis;
5. SHA-256 local somente quando a evidência anterior não concluir;
6. requisição condicionada ou download somente como último nível.

Publicação concluída, íntegra e coerente com índice/metadado DEVE resultar em
`skipped`, sem request do ativo, conversão, extração, regravação, alteração de
timestamp ou recálculo desnecessário.

Nome ou existência isolada NÃO comprovam conclusão. Temporário, parcial,
assinatura inválida, hash divergente, metadado incoerente ou índice ausente
DEVE resultar em estado incompleto, corrompido ou revisão, nunca em sucesso.

Atualização somente DEVE ocorrer por evidência material: hash, edição/versão,
novo ativo associado, correção remota, metadado editorial relevante ou arquivo
local ausente/inválido. Versão anterior e nova DEVEM manter relação e evidência
sem sobrescrita destrutiva.

### 42.4 Estado, metadados e retomada

O ledger incremental DEVE distinguir `pending`, `processing`, `completed`,
`skipped`, `incomplete`, `corrupt`, `unavailable`, `ineligible`,
`temporary_failure`, `permanent_failure` e `review_required`.

Estado de execução, cache e validadores HTTP DEVEM residir fora de
`formative_data` e não obrigar alteração de arquivo rastreado em reexecução
sem mudança material. Metadado canônico DEVE registrar coleção, identidade
remota/local, autor, títulos original/normalizado, idiomas original/canônico,
tipo, edição, URL pública, fontes por ativo/segmento, formato, método, data,
tamanho, hashes, ordem, completude, ressalvas e relações de derivação.

Metadado legado DEVE permanecer legível. Escrita nova ou atualização material
DEVE usar schema versionado posterior, determinístico, fechado e migrável; dado
original NÃO DEVE ser perdido quando divergir de normalização.

Execução interrompida DEVE preservar ativos promovidos e estado confirmado.
`processing` abandonado DEVE ser retomado como unidade incompleta após validar
temporários; parcial nunca DEVE ser promovido ou indexado como concluído.

### 42.5 Acesso responsável e contenção

O cliente DEVE ser sequencial por padrão, com concorrência `1`, atraso base
configurável de no mínimo dois segundos entre requests e jitter moderado
positivo. Aumento até concorrência `2` somente PODE ocorrer por configuração
explícita e evidência de que a origem o tolera; valor superior é proibido.

Timeout, limite de bytes, sessão reutilizável, cache, deduplicação de request,
`User-Agent` identificável, número máximo de três tentativas e backoff
exponencial limitado DEVEM ser configuráveis e observáveis.

Resposta `429` DEVE respeitar `Retry-After`; `408` e `5xx` PODEM repetir dentro
do limite. [3301a97] Quando a descoberta ou etapa remota exigir navegador, o coletor DEVE
usar preferencialmente uma única instância visível, perfil persistente local
segregado e uma única guia operacional reutilizada entre coleções e páginas,
com `workers=1` enquanto essa guia for necessária. Nova guia, sessão ou perfil
somente PODE ocorrer por fechamento, invalidação, corrupção comprovada ou
recuperação controlada, sempre com motivo registrado. [PENDENTE-CODIGO]

CAPTCHA, página de desafio, verificação de navegador, bloqueio temporário,
`403`, `429`, redirecionamento de validação, alteração de título/URL/DOM ou
ausência do conteúdo esperado somente DEVEM ser classificados como verificação
humana quando houver evidência suficiente e não por indisponibilidade comum
isolada. Diante de verificação legitimamente interativa, o coletor DEVE pausar
a unidade dependente, manter a guia aberta, suspender intensificação de acesso,
informar instrução objetiva ao usuário, aguardar em baixa frequência e retomar
automaticamente após validar que o conteúdo esperado voltou. [PENDENTE-CODIGO]

`403`, CAPTCHA, desafio anti-automação, bloqueio, limitação persistente ou
contrato inesperado que não puderem ser liberados de forma legítima pela guia
visível DEVEM interromper a unidade ou coleção afetada, preservando progresso,
sem evasão, proxy, rotação de identidade, solução automática de CAPTCHA,
simulação humana ou tentativa de ocultar o cliente. [PENDENTE-CODIGO]

Progresso concluído DEVE ser preservado e o diagnóstico DEVE registrar taxa,
tentativa, espera, status e escopo bloqueado sem segredo ou payload editorial
desnecessário.

### 42.6 Extração editorial e derivados

Extração textual DEVE obter somente título, autoria e corpo editorial legítimo:
prefácio, introdução, capítulos, seções, parágrafos, notas, citações, listas,
tabelas textuais, epígrafes e referências.

Menus, cabeçalhos/rodapés da aplicação, breadcrumbs, controles, recomendações,
resultados relacionados, publicidade, telemetria, scripts, estilos, mensagens
de interface, duplicações de renderização e conteúdo de outra publicação DEVEM
ser excluídos.

Cada segmento DEVE preservar identificador, URL, posição e hash; sequência
DEVE validar primeiro/último segmento, quantidade declarada/obtida, lacunas,
duplicações e ordem. Incerteza ou lacuna DEVE impedir `completed` e exigir
`review_required`.

Fonte textual completa DEVE ser persistida como Markdown UTF-8 estruturado,
numerado pela ordem editorial e acompanhado de metadado. Conversão posterior
DEVE seguir `fonte estruturada -> Markdown normalizado -> EPUB validado` sem
nova coleta.

EPUB gerado DEVE possuir sumário, metadados, idioma, autor, título, capítulos,
notas, ordem e proveniência e passar validação EPUB. Ele DEVE ser identificado
como derivado local da edição on-line, nunca como EPUB nativo nem como URL/hash
original em `formative_data`.

Transformação NÃO DEVE corrigir, resumir, modernizar, traduzir ou reescrever o
texto. Sanitização DEVE impedir execução/injeção e preservar Unicode e conteúdo
editorial, registrando transformação potencialmente material.

### 42.7 Descoberta técnica limitada

Inspeção PODE observar rede do navegador, contratos públicos, JavaScript
entregue ao cliente e chamadas legítimas de leitura. NÃO PODE acessar endpoint
privado, obter credencial/token alheio, explorar vulnerabilidade, modificar o
serviço, contornar proteção ou executar varredura agressiva.

Bundle temporário somente PODE existir durante análise rastreada e DEVE ser
removido quando sua função se esgotar. Implementação DEVE acoplar-se a contrato
de dados observável, com fixture, e NÃO a detalhe minificado frágil quando
houver alternativa.

### 42.8 Segurança, testes e gate de coleta

Toda entrada remota DEVE ser não confiável: esquema/host/path, DNS/IP,
redirecionamento, tamanho, MIME, assinatura, arquivo compactado, nome e destino
DEVEM cumprir as guardas das §§41 e 44.6-44.7. Escrita DEVE usar temporário
segregado, hash durante streaming e promoção atômica; conteúdo obtido nunca
DEVE ser executado.

Testes offline DEVEM comprovar skip sem request, parcial, corrupção,
deduplicação, colisão, atualização real, idiomas, formatos, multiautor,
coleções, extração ordenada, exclusão da interface, lacunas, Markdown, EPUB,
original/derivado, `Retry-After`, backoff, limite, parada por bloqueio,
retomada, path hostil e coerência de índice.

Fixture/mock DEVE preceder amostra pública mínima. Coleta ampliada somente PODE
ocorrer após os gates de descoberta, elegibilidade, idempotência, fidelidade,
contenção e integridade e mediante autorização material própria; a conclusão
normativa ou da amostra NÃO autoriza download em massa.

### 42.9 Raiz única de estado de runtime

Todo estado mutável não canônico da cadeia de publicações DEVE convergir para [PENDENTE-CODIGO]
uma raiz local única, configurável e resolvida pela raiz do repositório,
denominada `runtime_state_root`. Ela DEVE permanecer fora de `src/`, `scripts/`, [PENDENTE-CODIGO]
`dist/`, artefatos públicos e releases, ser integralmente ignorada pelo Git e
ser removível sem perda de publicação, configuração, schema ou fixture. [PENDENTE-CODIGO]

São runtime: cache, ledger, checkpoint, sessão, perfil de navegador, cookie,
storage, autenticação transitória, ambiente de linguagem, lock, PID, socket,
temporário, parcial, trace, screenshot, dump, log e relatório efêmero. PDF,
EPUB, Markdown editorial, metadado de proveniência e índice validados são
canônicos quando pertencem à publicação concluída e NÃO DEVEM ser ocultados por [PENDENTE-CODIGO]
padrão de ignore amplo. [PENDENTE-CODIGO]

Cada subdiretório DEVE declarar classe, produtor, consumidor, persistência, [PENDENTE-CODIGO]
isolamento, retenção, limite, expiração, invalidação e limpeza. Estado sensível
DEVE ser isolado por domínio, perfil, usuário e finalidade, usar permissões [PENDENTE-CODIGO]
mínimas, nunca integrar log e ser invalidado em expiração, corrupção ou troca
de identidade. Cache DEVE tolerar ausência e corrupção; temporário e lock DEVEM [PENDENTE-CODIGO]
ter criação sem colisão e limpeza limitada à raiz validada, sem atingir processo
ativo ou execução concorrente. [PENDENTE-CODIGO]

Configuração DEVE derivar os paths de runtime da raiz única e admitir override [PENDENTE-CODIGO]
explícito seguro. Caminho legado PODE ser migrado uma única vez, de forma [PENDENTE-CODIGO]
idempotente e retomável, somente quando seu conteúdo e proprietário forem
comprovados; produtores e consumidores DEVEM convergir no mesmo ciclo e o [PENDENTE-CODIGO]
fallback legado DEVE ser removido após validação. Clone limpo, CI e execução [PENDENTE-CODIGO]
offline NÃO DEVEM depender de estado preexistente. [PENDENTE-CODIGO]

Validação DEVE inspecionar índice e histórico corrente sem reescrevê-lo, [PENDENTE-CODIGO]
rejeitar runtime rastreado ou empacotado, comprovar `.gitignore` cirúrgico e
garantir que limpeza, build, bundle e release não incluam sessão, perfil,
cache, temporário, lock, trace ou segredo. Remoção de runtime já rastreado DEVE [PENDENTE-CODIGO]
ocorrer apenas do índice, preservando localmente o que ainda for necessário e
sem reescrever histórico compartilhado sem autorização própria. [PENDENTE-CODIGO]

### 42.10 Suspensão e handoff humano diante de desafio

Detecção de challenge page, CAPTCHA, intersticial, bloqueio por automação,
loop de redirecionamento ou estado incompatível DEVE combinar URL, título, [PENDENTE-CODIGO]
conteúdo esperado, resposta e transições; indisponibilidade isolada NÃO comprova
desafio. A detecção NÃO DEVE clicar, preencher, recarregar nem tentar resolver [PENDENTE-CODIGO]
o mecanismo. [PENDENTE-CODIGO]

Ao detectar desafio, a máquina de estados DEVE entrar em [PENDENTE-CODIGO]
`aguardando_intervencao_humana`, cessar integralmente automação, polling do DOM,
timers, filas, scripts, cliques, recargas e navegações e impedir atuação
simultânea do controlador e do operador. O operador DEVE poder cancelar, e [PENDENTE-CODIGO]
nenhum timeout curto PODE reiniciar a página ou invalidar sua ação. Somente um [PENDENTE-CODIGO]
monitor externo de baixa frequência, sem interação com a página e com limite
configurável, PODE observar encerramento/cancelamento da etapa humana. [PENDENTE-CODIGO]
[PENDENTE-CODIGO]

Em domínio de terceiro, a ordem de preferência é API, autenticação, feed,
exportação ou integração oficial; na falta, o handoff DEVE usar navegador normal [PENDENTE-CODIGO]
operado diretamente pelo usuário ou perfil humano autorizado sem automação
ativa. Janela ainda anexada ao WebDriver NÃO constitui handoff humano completo.
O controlador DEVE ser encerrado/desanexado antes da intervenção e somente [PENDENTE-CODIGO]
PODERÁ ser recriado depois que a sessão humana terminar, usando o mesmo perfil
apenas quando compatibilidade, escopo, consentimento e proteção forem
comprovados. [PENDENTE-CODIGO]

A retomada DEVE validar objetivamente ausência do desafio, origem, página, [PENDENTE-CODIGO]
conteúdo esperado, identidade e inexistência de loop. Clique humano isolado não
comprova liberação. Recusa, expiração, novo desafio ou estado incompatível DEVE [PENDENTE-CODIGO]
manter a unidade suspensa ou encerrá-la como `review_required`, com progresso
preservado e tentativas finitas. [PENDENTE-CODIGO]

Falso positivo NÃO autoriza stealth, spoofing, proxy, rotação de identidade,
mascaramento de WebDriver, solução automática de CAPTCHA, cópia incompatível de
cookie/token/storage ou qualquer bypass. Exceção em domínio próprio somente
PODE usar mecanismo oficial, mínimo, auditável, revogável e restrito, como [PENDENTE-CODIGO]
identidade de serviço ou ambiente de automação dedicado. [PENDENTE-CODIGO]

Log DEVE registrar somente transições, origem sanitizada, tipo provável, [PENDENTE-CODIGO]
início/fim/método do handoff, validação e motivo final; senha, resposta de
CAPTCHA, cookie, token, cabeçalho de autenticação, storage e dado pessoal
reutilizável são proibidos. Testes DEVEM usar fixture, mock ou domínio próprio e [PENDENTE-CODIGO]
cobrir suspensão total, cancelamento, aceitação, recusa, expiração,
reapresentação, isolamento e ausência de segredo. [PENDENTE-CODIGO]

### 42.11 Unidade transacional e commit por publicação

Uma publicação somente PODE atingir `completa_e_pareada` quando todos os [PENDENTE-CODIGO]
ativos obrigatórios terminaram, não há parcial, formato/tamanho/hash são [PENDENTE-CODIGO]
válidos, identidade e metadado são inequívocos, assets e referências existem,
duplicidades/colisões foram tratadas e índices locais/globais refletem uma única
entrada final. HTTP de sucesso, existência ou stream encerrado isoladamente não
comprovam conclusão. Ambiguidade material exige `review_required`.
[PENDENTE-CODIGO]

Download, promoção, metadado, derivados, índice e eventual commit DEVEM formar [PENDENTE-CODIGO]
uma transação lógica por publicação. Falha DEVE remover ou isolar preparatórios, [PENDENTE-CODIGO]
restaurar índice anterior, manter runtime retomável e impedir commit. Reexecução
inalterada DEVE resultar em `skipped` sem commit, timestamp ou derivado [PENDENTE-CODIGO]
divergente. [PENDENTE-CODIGO]

Efeito Git DEVE ser opt-in explícito por execução e somente PODE ocorrer em [PENDENTE-CODIGO]
`dev`, em repositório Git validado, sem operação Git concorrente e com identidade
configurada. A allowlist DEVE ser calculada por identidade da publicação e [PENDENTE-CODIGO]
derivados globais inevitáveis; `git add .`, `git add -A`, glob aberto ou
inclusão de runtime são proibidos. Alteração alheia permanece fora do índice; [PENDENTE-CODIGO]
conflito no mesmo arquivo bloqueia. [PENDENTE-CODIGO]

Antes do commit, o coletor DEVE validar novamente os blobs staged, schemas, [PENDENTE-CODIGO]
hashes, referências, índice, ausência de segredo/runtime e conteúdo exato da
allowlist. O commit DEVE conter exatamente uma publicação completa e seus [PENDENTE-CODIGO]
derivados inevitáveis, possuir mensagem com identificador estável e ter seu
hash confirmado no ledger. Commit vazio, parcial, agrupado, fragmentado ou
recriado após retomada é proibido. [PENDENTE-CODIGO]

Downloads distintos PODEM ser concorrentes, mas promoção, índice, staging e [PENDENTE-CODIGO]
commit DEVEM ser serializados por lock de runtime. Push é operação separada, [PENDENTE-CODIGO]
opt-in, posterior à validação de branch, upstream e sincronização; falha de push
preserva o commit local e nunca o recria. Testes DEVEM cobrir worktree alheia, [PENDENTE-CODIGO]
conflito, completude, parcial, índice quebrado, falhas antes/depois do staging,
concorrência, retomada, commit exato e ausência de runtime. [PENDENTE-CODIGO]

### 42.12 Completude observável da descoberta e da derivação

O catálogo DEVE ser enumerado até que todos os links únicos de publicação [be82602]
expostos pela coleção tenham sido coletados. [be82602]
Grade virtualizada ou paginação DEVE ser colhida incrementalmente; inspecionar [be82602]
somente o DOM final depois da rolagem NÃO comprova completude. [be82602]
A execução DEVE registrar contagem observada, [be82602]
identidades únicas e critério objetivo de término. [be82602]

Cada publicação DEVE ser enriquecida pela sua página individual. [be82602]
Todos os links habilitados de PDF e EPUB ali expostos DEVEM integrar o conjunto [be82602]
obrigatório; link ausente no cartão, botão desabilitado ou `href="#"` NÃO [be82602]
constitui ativo. [be82602]
Falha em descobrir, baixar ou validar qualquer ativo habilitado impede
`completed`. [be82602]

Quando PDF e EPUB estiverem ambos ausentes, a leitura textual DEVE começar na [be82602]
URL oficial declarada pela obra e seguir a navegação editorial `rel=next` até o
término declarado. [be82602]
A cadeia DEVE ser acíclica, permanecer na mesma obra, possuir [be82602]
anterior/próximo coerentes e preservar todos os blocos editoriais identificados
no contêiner de leitura, inclusive headings, parágrafos, listas, tabelas, notas,
ênfases, links e quebras semanticamente materiais. [be82602]

O hash e o estado de cada unidade DEVEM derivar do conteúdo editorial real [be82602]
normalizado sem controles da interface. [be82602]
Cadeia interrompida, vazia, repetida, divergente do sumário ou cuja obra mude
no percurso DEVE resultar em [be82602]
`review_required`, nunca em EPUB parcial. [be82602]

Fixture e mock DEVEM usar raiz temporária explícita ou raiz de saída de teste [be82602]
segregada. [be82602]
A CLI NÃO DEVE materializar fixture em `src/publications`, mesmo quando [be82602]
`source_root` canônico estiver configurado. [be82602]
Artefato sintético detectado na raiz canônica DEVE ser isolado como [be82602]
runtime/quarentena, sem publicação ou
commit. [be82602]

Aceite DEVE comparar: quantidade de obras no catálogo e identidades coletadas; [be82602]
ativos habilitados e arquivos incorporados; cadeia editorial observada e
segmentos persistidos; e conteúdo real renderizado do EPUB derivado. [be82602]
Amostra pública controlada DEVE abranger uma obra com ativos nativos e uma sem eles, [be82602]
sem autorizar coleta em massa. [be82602]

## 43. Indice global

Um indice JSON global DEVE representar todas as publicacoes e ser gerado deterministicamente por uma unica fonte ou etapa canônica.

Copias do indice em `dist/` quando aplicavel, no artefato do Pages e na raiz publica das publicacoes DEVEM ser projeções identicas, nunca editadas manualmente.

O envelope global DEVE declarar `schema_version`, identidade da geracao, versao do gerador, configuracao causal e lista `publications`.

Cada item global DEVE declarar identidade estavel, titulo normalizado, slug de rota, autor ou chave autoral, idioma, tipo, acronimo, tags, URLs publicas diretas, proveniencia local, capa e `formative_data`.

`formative_data` DEVE ser exatamente um documento conforme a `NORMA-IF-SIL-001`, com raiz fechada `book`, `urls` e `global_hashes`.

Metadados locais de cada publicacao DEVEM ser a entrada prioritaria do indice, sem impedir confrontacao com o conteudo editorial e outras evidencias.

CONTRADICAO DETECTADA: restricao intermediaria a `book` + `global_hashes` vs anexo final `NORMA-IF-SIL-001` com `book` + `urls` + `global_hashes` - Aplicando o anexo final, expresso e mais especifico.

URL publica direta e URL original DEVEM permanecer semanticamente distintas no envelope; URL original candidata integra `formative_data.urls`, enquanto URL publica do artefato integra o campo externo de publicacao.

`urls` do documento formativo NÃO DEVE ser copiado para a raiz de `metadata.json` schema 5 nem interpretado como endereco local de asset.

Indice DEVE ser ordenado deterministicamente por titulo normalizado e desempates declarados; URLs DEVEM seguir prioridade de formato e fonte.

Gerador DEVE rejeitar URL repetida, formato duplicado, path equivalente por caixa/codificacao/barra e fusao de titulos sem identidade editorial comprovada.

Alteracao de publicacao DEVE regenerar item, hashes, capa, indice e artefato dependente sem reprocessar grupo independente quando isso for seguro.

## 44. NORMA-IF-SIL-001 - autoridade e estrutura

`NORMA-IF-SIL-001` DEVE reger exclusivamente o documento formativo de sugestao bibliografica e NÃO DEVE ser interpretada como metadado canônico integral, envelope global, contrato de capa, asset, rota, publicacao ou autorizacao de aquisicao.

O documento DEVE ser semanticamente identico em JSON e YAML e possuir exatamente uma raiz com `book`, `urls` e `global_hashes`.

`book` DEVE conter exatamente `title`, `contributors`, `edition`, `language`, `primary_category` e `tags`.

Cada `book.contributors[]` DEVE conter exatamente `name` e `role`.

`book.edition` DEVE existir e ser exatamente `{}`. Qualificador editorial oficial
necessário para distinguir publicações, quando já integrar inequivocamente o
título canônico ou a evidência editorial, DEVE permanecer como parte indivisível
de `book.title`, sem ser projetado em propriedade adicional. Qualificador
inferido, técnico ou não comprovado DEVE bloquear conformidade.

`book.tags` DEVE existir e PODE ser `[]`; nenhum outro objeto ou lista vazia e admitido.

Cada `urls[]` DEVE conter exatamente `format` e `url`.

Cada `global_hashes[]` DEVE conter exatamente `format`, `sha1`, `sha256` e `sha512`.

Propriedade nao enumerada NÃO DEVE integrar o documento formativo.

`schema_version`, `book.id`, `short_token`, `artifact_id`, `assets`, `sources`, QR, pacote e contêiner NÃO DEVEM ser propriedades do documento formativo; quando necessarios ao envelope global, permanecem externos a `formative_data`.

Toda informacao extraida DEVE permanecer candidata ate validacao por evidencia reproduzivel; incerteza, conflito ou plausibilidade NÃO DEVE preencher propriedade.

### 44.1 Serializacao segura

JSON DEVE ser UTF-8 sem BOM, comentario, virgula final, chave duplicada ou numero nao finito.

YAML DEVE usar subconjunto seguro 1.2 com mapping, sequence e string; ancora, alias, merge key, tag, construtor, diretiva e multiplos documentos DEVEM ser rejeitados.

String YAML DEVERIA usar aspas para evitar resolucao implicita e preservar caixa, pontuacao e zeros.

Conversao JSON para YAML e retorno DEVE preservar chaves, hierarquia, tipos, Unicode, valores e ordem das listas com igualdade profunda.

`null`, chave omitida, string vazia e vazio fora de `book.edition` e `book.tags` DEVEM ser rejeitados.

### 44.2 Dominios fechados

`book.title` DEVE ser string Unicode editorial nao vazia.

`book.contributors` DEVE possuir um ou mais itens e ao menos um `role: "author"`.

`book.language` DEVE ser BCP 47 valida em minusculas.

`book.primary_category` DEVE seguir `[a-z0-9]+(?:-[a-z0-9]+)*`.

Cada tag DEVE seguir o mesmo padrao, ser unica, relevante, ordenada lexicalmente e nao repetir a categoria.

`contributors[].name` DEVE ser Unicode editorial nao vazio; `role` DEVE seguir `[a-z][a-z0-9-]*`.

`urls` DEVE ter um ou mais itens; `format` DEVE ser `pdf` ou `epub` e `url` DEVE ser URI HTTP(S) absoluta normalizada.

`global_hashes` DEVE ter um item por formato aceito, no minimo um e no maximo dois, sem formato repetido e em ordem `pdf`, depois `epub`.

SHA-1, SHA-256 e SHA-512 DEVEM ser hexadecimais minusculos de 40, 64 e 128 caracteres.

### 44.3 Evidencia de `book`

O original DEVE ser preservado, identificado por assinatura/estrutura e analisado antes de conversao, reparo, reempacotamento, OCR ou normalizacao.

Metadado estruturado, pagina de rosto, verso, colofao e primeiras unidades editoriais DEVEM ser extraidos na ordem do formato.

Titulo, autoria e idioma DEVEM ser comparados com ao menos duas evidencias independentes quando disponiveis.

Conflito material, autoria ausente, baixa confianca ou arquivo ilegivel DEVE bloquear o documento e produzir diagnostico.

OCR somente DEVE ser usado quando a camada textual for ausente ou insuficiente e NÃO DEVE substituir o original nem servir como evidencia primaria autossuficiente.

Titulo DEVE preservar capitalizacao, diacritico, pontuacao e grafia editorial; espaco externo, controle Unicode e repeticao acidental PODEM ser normalizados em copia.

Pagina de rosto ou colofao visivel DEVE preceder titulo estruturado EPUB coerente, metadado PDF coerente e cabecalho editorial recorrente.

Filename, diretorio, URL, capa isolada, primeira linha ou OCR isolado NÃO DEVEM comprovar titulo.

Contribuidores DEVEM preservar forma creditada, funcao e ordem editorial; o primeiro autor DEVE representar autoria principal.

Duplicata exata `name + role` DEVE ser removida, mas homonimos NÃO DEVEM ser fundidos sem evidencia.

Papeis recomendados PODEM incluir `author`, `editor`, `translator`, `compiler` e `illustrator`; outro papel exige significado editorial comprovado.

Pessoa citada, prefaciador, personagem, mantenedor ou proprietario NÃO DEVE ser autor sem credito editorial.

Idioma DEVE representar a edicao e seguir precedencia de metadado EPUB coerente, declaracao editorial, amostra textual distribuida e revisao.

Detector de idioma DEVE ser auxiliar e NÃO DEVE usar somente titulo, primeira pagina, filename, dominio ou pais do fornecedor.

Edicao multilingue sem predominancia inequívoca DEVE ir a revisao.

Categoria DEVE vir de vocabulario controlado e evidencia; empate exige decisao editorial unica.

Tag NÃO DEVE ser inferida somente de filename, fornecedor, formato, idioma ou detalhe tecnico.

### 44.4 Hashes globais

Hash DEVE incidir nos bytes integrais e originais do contêiner EPUB ou arquivo PDF, antes de qualquer extracao, conversao, reparo, OCR, renderizacao ou compactacao.

Leitura DEVE ser binaria, sequencial, completa e alimentar SHA-1, SHA-256 e SHA-512 na mesma passagem e nos mesmos chunks.

Arquivo reparado ou regravado NÃO DEVE herdar hash do original.

SHA-1 DEVE existir somente para interoperabilidade e NÃO DEVE provar integridade isoladamente.

Divergencia em qualquer algoritmo DEVE rejeitar igualdade byte a byte.

Hash parcial, ausente, truncado, maiusculo ou calculado sobre texto DEVE ser rejeitado.

Implementacao Node.js DEVERIA usar fluxo binario e `node:crypto`; implementacao Python DEVERIA usar modo `rb` e `hashlib`, sem converter chunks em string.

Biblioteca alternativa PODE ser usada somente se produzir os mesmos valores sobre os mesmos bytes e preservar seguranca/evidencia.

### 44.5 URLs formativas e aquisicao

Cada URL DEVE vincular explicitamente formato esperado, usar HTTP(S), host explicito, sem credencial ou fragmento, preservando path e query necessarios.

Para cada formato em `global_hashes` DEVE existir ao menos uma URL do mesmo formato; todo formato de URL DEVE possuir exatamente um hash correspondente.

Multiplas URLs do mesmo formato PODEM representar fontes alternativas dos mesmos bytes e DEVEM manter preferencia editorial ou ordem de submissao.

URL duplicada apos normalizacao segura DEVE ser rejeitada; grupos DEVEM ordenar `pdf` antes de `epub`.

URL somente DEVE gerar asset quando os bytes diretos ou extraidos corresponderem integralmente aos tres hashes.

Fonte DEVERIA ser link oficial direto de editor, autor, biblioteca, repositorio institucional ou provedor confiavel; pagina, manifesto, catalogo, feed ou API PODEM ajudar a localizar o arquivo.

Endereco incorporado no arquivo, busca, cache, espelho ou terceiro DEVE permanecer candidato ate confirmacao.

URL relativa somente DEVE ser resolvida contra a pagina ou manifesto que a declarou.

Redirecionamento observado NÃO DEVE substituir silenciosamente a URL submetida.

Endereco NÃO DEVE ser inventado por padrao de nome, troca de extensao, codigo de idioma ou filename.

URL temporaria, assinada, secreta, autenticada ou de validade curta NÃO DEVE integrar o documento.

Parametro indispensavel DEVE ser preservado; parametro comprovadamente analitico DEVERIA ser removido sem alterar o recurso.

Ausencia de URL publica direta e estavel DEVE bloquear conformidade, sem usar path local inventado.

### 44.6 Rede e validacao de aquisicao

Antes de request, URL DEVE ser analisada, esquema/host validados e politica de rede aplicada.

`HEAD` PODE sondar, mas somente `GET` limitado DEVE confirmar disponibilidade, tipo e integridade.

Redirecionamentos DEVEM ser limitados e revalidar esquema, host, DNS e IP em cada salto.

Host local, IP privado, link-local, multicast, reservado, protocolo nao HTTP(S), loop e DNS rebinding DEVEM ser bloqueados.

Conexao DEVE usar timeout, limite de bytes, rate limit, cancelamento e streaming; corpo parcial DEVE falhar.

Formato DEVE ser confirmado por assinatura e estrutura; extensao, `Content-Type`, codigo HTTP ou nome NÃO DEVEM bastar.

Hashes DEVEM ser calculados durante a leitura e comparados antes da incorporacao.

Invólucro permitido DEVE ser extraido em ambiente isolado e limitado, produzindo exatamente um artefato correspondente.

Diagnostico DEVE registrar URL submetida, redirecionamentos, tamanho, tipo e hashes fora do documento formativo.

Falha de rede, bloqueio, resposta autenticada, HTML, desafio ou indisponibilidade DEVE impedir incorporacao automatica.

Conteudo obtido NÃO DEVE executar script, macro, midia ativa ou incorporado.

Cliente Node.js DEVERIA usar `URL`, redirecionamento manual, DNS validado, `AbortSignal` e streaming; cliente Python DEVERIA usar `urllib.parse` e cliente com as mesmas guardas.

Buffer integral sem limite previo NÃO DEVE ser usado em resposta potencialmente grande.

### 44.7 EPUB, PDF e associacao editorial

EPUB DEVE ser tratado como ZIP OCF nao confiavel com limites de entradas, tamanho comprimido/expandido, razao, profundidade e path.

Path absoluto, traversal, symlink, colisao normalizada e entidade XML externa DEVEM ser rejeitados.

Package Document DEVE ser localizado pelo container, namespaces respeitados e spine usado como ordem editorial.

Titulo, idioma e contribuidores estruturados DEVEM ser confrontados com pagina de rosto e colofao.

Impressao textual EPUB DEVE seguir spine, excluir script/estilo/navegacao repetitiva e normalizar somente copia derivada.

PDF DEVE ser analisado por biblioteca que compreenda objetos, xref, streams, fontes, paginas e metadados; regex sobre bytes crus NÃO DEVE extrair `book`.

Pagina de rosto e colofao visiveis DEVEM prevalecer sobre metadado tecnico conflitante.

Extracao PDF DEVE preservar numero/ordem das paginas e diagnosticar pagina vazia ou baixa densidade.

PDF cifrado sem autorizacao, corrompido ou acima de limite DEVE falhar com diagnostico.

PDF e EPUB somente DEVEM compartilhar documento quando titulo, autoria, idioma e identidade editorial forem compativeis.

Equivalencia textual aproximada isolada ou igualdade de hashes entre formatos NÃO DEVEM comprovar identidade.

Diferenca de paginacao, layout ou codificacao NÃO DEVE separar por si so; diferenca material de conteudo, idioma, autoria ou edicao DEVE impedir associacao automatica.

Confianca insuficiente DEVE encaminhar para revisao humana.

### 44.8 Validacao integral do documento formativo

Validador DEVE confirmar parser seguro, raiz exata, seis chaves de `book`, `edition: {}`, `tags`, contribuidor/autor, chaves de contribuidor, dominios, URLs, correspondencia de formatos, cardinalidade dos hashes, recálculo dos tres hashes, associacao editorial e igualdade profunda JSON/YAML.

Falha DEVE indicar propriedade, regra e evidencia necessaria sem inventar substituto.

Item invalido NÃO DEVE ser removido silenciosamente para simular conformidade.

Documento somente DEVE ser aceito quando toda propriedade obrigatoria existir e nenhuma adicional existir.

Referencias tecnicas aplicaveis DEVEM considerar RFC 8259, YAML 1.2.2, RFC 3986, BCP 47/RFC 5646 e EPUB 3.3.

### 44.9 Exemplo delimitador

O exemplo abaixo e formativo e NÃO DEVE fornecer hashes a payload produtivo; toda matriz produtiva DEVE ser recalculada sobre os bytes originais.

```json
{
  "book": {
    "title": "Atos Dos Apóstolos",
    "contributors": [
      {
        "name": "Ellen G. White",
        "role": "author"
      }
    ],
    "edition": {},
    "language": "pt-br",
    "primary_category": "livros",
    "tags": []
  },
  "urls": [
    {
      "format": "pdf",
      "url": "https://media2.egwwritings.org/pdf/pt_AA(AA).pdf"
    },
    {
      "format": "epub",
      "url": "https://media2.egwwritings.org/epub/pt_AA(AA).epub"
    }
  ],
  "global_hashes": [
    {
      "format": "pdf",
      "sha1": "ef605032eb4011e6f058c100dc845f414e36e4f4",
      "sha256": "91e2d4ea3e74a3ec55ecd61fb659f57927ef90ae413ea699cd8b4e92c7d9051a",
      "sha512": "75b0c5ffda1ae8314cae7612afc947393817581b9ac219db497d526ee90417841e16b0e5f3ab0f2421eb8201358502ba6f9628e62195b4c37437d0967748cb42"
    },
    {
      "format": "epub",
      "sha1": "6df74abc8e2d57f82ff54a3b373d855c016f9f15",
      "sha256": "46d2ed2d02977d96d625c6c0d2ad65de4f769cece56b2e45f64f65555f5eba29",
      "sha512": "cc055518caab4bcf2399dde632359ab808b5dfeea2259e886b9f9af161eca7fea611d7658d11d42f1a68b4d3f54e57a25ff50e2a68d010c83bb8337d1e41ff80"
    }
  ]
}
```

Representacao YAML conforme DEVE analisar para estrutura profundamente igual ao exemplo JSON, sem propriedade, valor ou ordem de lista divergente.

O projeto NÃO DEVE declarar vinculo com editoras nem responder pelo conteudo de terceiros; atribuicao, restricao de uso, proveniencia e integridade permanecem obrigatorias.

## 45. Capas

Cada diretorio publico de publicacao DEVE conter arquivo decodificavel chamado exatamente `cover.png`.

Grupo PDF/EPUB no mesmo diretorio DEVE compartilhar uma capa canônica; grupo em diretorios distintos DEVE possuir copia gerada correspondente.

Capa DEVE vir primeiro da capa EPUB editorialmente identificada, incluindo `cover-image`; fallback legado exige referencia valida.

Maior imagem arbitraria NÃO DEVE ser presumida capa.

Sem capa EPUB utilizavel, gerador DEVE renderizar a primeira pagina PDF editorialmente adequada sem modificar o original.

Pagina vazia, tecnica, corrompida, de erro, ilegivel ou nao representativa NÃO DEVE ser aceita.

Ausencia de ambas as fontes DEVE bloquear o grupo.

`cover.png` DEVE possuir no maximo 800 px em cada eixo, preservar proporcao/nitidez/legibilidade, nao ampliar sem justificativa e remover EXIF, comentario, miniatura e metadado inutil.

Capa DEVE ser otimizada para navegador e regeneravel a partir das fontes e configuracao versionada.

Remocao da capa DEVE causar regeneracao na execucao seguinte; mudanca de EPUB, PDF, parser, extrator, configuracao ou gerador DEVE invalidar derivado afetado.

Imagem externa NÃO DEVE ser escolhida por similaridade de nome, titulo ou arquivo.

Intermediarios de renderizacao, conversao ou extracao NÃO DEVEM integrar `dist/` ou site.

Validacao DEVE comprovar existencia, path, origem, precedencia, formato, dimensoes, proporcao, legibilidade, metadados removidos e regeneracao deterministica.

## 46. Scripts, workflow, build e publicacao

Indexador, capas, dados formativos, ativos web e demais derivados DEVEM ser produzidos por script reexecutavel, deterministico, incremental e equivalente em local/CI.

Script Node.js novo DEVE usar TypeScript como fonte e artefato conforme o contrato operacional; Python PODE permanecer quando adequado ao ecossistema real.

Biblioteca de EPUB, PDF, OCR, imagem, YAML, JSON ou compactacao DEVE ser mantida, licenciada, segura e proporcional.

Cache DEVE incluir identidade das fontes, configuracao, parser, extrator e gerador para invalidacao correta.

Workflow dedicado DEVE obter fonte, instalar dependencias necessarias, descobrir/agrupar publicacoes, validar formatos, preservar originais, calcular hashes, extrair `book`, comprovar identidade, gerar capas, montar dados formativos, gerar indice/pagina, preparar artefato, validar e publicar.

Workflow DEVE reagir a mudanca de pagina, publicacao, capa, indice, dado, script, estilo, asset, parser, RCF ou configuracao e DEVE permitir disparo manual.

Permissoes DEVEM ser minimas; concorrencia DEVE serializar ou cancelar com seguranca para impedir execucao antiga sobre resultado novo.

Processo longo DEVE emitir progresso ultrassucinto por etapa e publicacao sem inundar logs ou aparentar congelamento.

Build DEVE copiar integralmente `./src/publications/` para `/publications/`, independentemente de importacao ou link na interface.

Tree shaking, limpeza e otimizacao NÃO DEVEM remover publicacao ou asset pertencente ao acervo canônico.

Build DEVE falhar por arquivo ausente, path invalido, colisao, perda, sobrescrita, indice invalido, URL sem artefato, hash divergente, capa invalida ou grupo incompleto.

Release publico NÃO DEVE conter fonte de desenvolvimento, cache, teste, log, source map, configuracao de desenvolvimento, dependencia inutil, intermediario, temporario, evidencia interna ou OCR transitório.

Derivado DEVE ser identificavel como gerado e NÃO DEVE receber edicao manual quando houver fonte canônica.

## 47. Validacao da cadeia publica

Validador do indice DEVE rejeitar JSON invalido, envelope divergente, publicacao sem campos obrigatorios, URL invalida, `formative_data` divergente, chave extra/ausente, hash incorreto, formato duplicado ou item sem autor.

Validador publico DEVE confirmar que cada URL direta corresponde a arquivo publicado, cada diretorio possui capa, cada hash corresponde ao original e cada `book` corresponde ao grupo.

Pagina DEVE ser validada por HTML real, assets carregados, base path real, responsividade, acessibilidade, ausencia de dependencia ociosa e ausencia de links ao indice/acervo.

Teste de capa DEVE remover `cover.png`, regenerar e comparar origem, validade, dimensoes e determinismo.

Teste de migracao DEVE comparar inventario pre/post, bytes, hashes, contagens, metadados, paths, colisoes e retomada.

Execucao local DEVE reproduzir as mesmas etapas, schemas e resultados do CI tanto quanto tecnicamente possivel.

Nenhuma publicacao DEVE ocorrer com artefato obsoleto, divergente ou parcial.

## 48. Ordem global e fronteiras de implementacao

A fase 1 DEVE concluir somente esta normatizacao, validacao documental, estado, TODO e commits.

A fase 2, FT-004, DEVE implementar: pagina no GitHub Pages; RCF especifico e correcao de `baixar.py`; migrador temporario; estrutura canônica; indice, hashes, metadados, capas, assets, build, validacao e workflow.

A fase 2 NÃO DEVE implementar busca independente da cadeia publica, salvo dependencia estritamente necessaria registrada antes da alteracao.

A fase 3, FT-002, DEVE implementar o nucleo de busca, persistencia, segmentacao, RAG aprovado, equivalencia numerica, recuperacao hibrida, Modo Pesquisa, Modo Conversa probatorio, citacoes e localizacoes verificadas, referencias, traducao vinculada, sessao auditavel, CLI, GUI, Markdown e conformidade restante.

A fase 3 NÃO DEVE duplicar artefato concluido e validado na fase 2.

Antes do codigo, a FT-002 DEVE decompor unidades materiais de indices/metadados, recuperacao profunda, citacoes/localizacao, traducao, composicao argumentativa, interface, sessao/rastreabilidade e avaliacao/degradacao. A decomposicao NÃO DEVE separar camada sem entrega coesa nem fundir responsabilidades com aceite materialmente distinto.

Cada fase tecnica DEVE iniciar por inspecao do estado real, baseline, arquitetura, dependencias e plano atualizado; conclusao local NÃO DEVE antecipar a fase seguinte.

## 49. Aceite integrado

O produto somente DEVE ser considerado integralmente conforme quando a operacao local/CLI estiver completa; GUI local estiver compartilhando o nucleo e operando offline; corpus estiver na estrutura canônica; downloader e migracao forem seguros; pagina e cadeia publica forem reproduziveis; indice, `NORMA-IF-SIL-001`, hashes e capas forem validados; Modo Pesquisa estiver preservado, multilingue, numerico, hibrido, rastreavel, resiliente e medido; e Modo Conversa estiver materializado com prova documental, fidelidade, abstencao e degradacao verificadas.

Aceite DEVE comprovar ausencia de perda ou sobrescrita, URLs estaveis, identidade editorial, correspondencia de hashes, regeneracao, seguranca de EPUB/PDF/rede, incremento, retomada, configuracao, desempenho, cross-platform e ausencia de regressao.

Relatorio final de cada fase DEVE listar arquivos, decisoes, colisoes, hashes, tecnologias, dependencias, comandos, testes, resultados, limitacoes, fallbacks e pendencias sem declarar execucao nao comprovada. A fase conversacional DEVE registrar ainda normas anteriores preservadas, diferencas entre modos, criterios de uso de LLM, modelo de citacao/referencia/traducao, prevencao de alucinacao, FTs, conjuntos de avaliacao e metricas disponiveis.

## 50. Preservacao da pesquisa vigente

O Modo Pesquisa DEVE preservar integralmente §§5-39 e suas especializacoes posteriores como pesquisa documental avancada, hibrida e nao conversacional.

O usuario DEVE selecionar explicitamente o Modo Pesquisa ou o Modo Conversa. A selecao DEVE controlar comportamento, apresentacao, profundidade, encadeamento, persistencia e criterios de resposta; infraestrutura compartilhada NÃO autoriza confundir sua semantica.

No Modo Pesquisa, expansao, recuperacao, filtros, ranking, aglutinacao, referencias, Markdown e rastreabilidade DEVEM permanecer operacionais sem conversa e sem LLM obrigatoria.

LLM e análogo SAO meios opcionais de otimizacao quando ganho liquido de qualidade ou desempenho for demonstrado. Eles NÃO DEVEM substituir mecanismo deterministico ou especializado mais adequado, reduzir cobertura, precisao, auditabilidade ou forca normativa, nem tornar a pesquisa indisponivel quando alternativa aplicavel existir.

Resultado do Modo Pesquisa DEVE continuar distinguindo ocorrencia recuperada, texto original, traducao, referencia, confianca e derivado; sintese auxiliar por IA NÃO DEVE converter a experiencia em conversa nem ocultar os resultados verificaveis.

## 51. Modo Conversa e contrato comum

O Modo Conversa DEVE permitir dialogo fluido, contextual e iterativo com o acervo, inclusive aprofundar, comparar, interpretar, relacionar, contestar, mudar recorte e solicitar novas provas.

Modo Pesquisa e Modo Conversa PODEM compartilhar descoberta, extracao, texto canônico, segmentacao, indices, recuperacao, expansao, filtros, reranking, confianca, referencias, traducao, cache e limites. Cada modo DEVE possuir orquestracao, estado, apresentacao, saida e aceite proprios sobre contratos comuns versionados.

O contexto conversacional DEVE ser controlado por sessao. Pergunta subsequente PODE reutilizar consulta, filtros, entidades, fontes e evidencias ainda validas; mudanca de finalidade, recorte, versao, fonte ou afirmacao material DEVE provocar recuperacao proporcional nova.

A IA DEVE interpretar e explicar o conteudo, sem apenas falar em nome das fontes nem apresentar parafrase desacompanhada de prova. Toda afirmacao material atribuida ao acervo DEVE possuir evidencia documental suficiente, exata, contextualizada e associada.

Resposta DEVE distinguir de modo inequívoco: `afirmacao`, `evidencia`, `referencia`, `traducao`, `interpretacao`, `comparacao`, `inferencia`, `conclusao` e `limitacao`. Campo ou camada não aplicavel PODE ser omitido da apresentacao, mas sua natureza NÃO DEVE ser confundida.

A apresentacao PODE ser natural, concisa e adaptativa; NÃO DEVE impor estrutura repetitiva ou excessivamente academica quando desnecessaria. Fluidez e simplificacao visual NÃO DEVEM ocultar origem, substituir prova por autoridade aparente ou reduzir verificabilidade.

## 52. Prova documental, citacao e suficiência

Evidencia probatoria DEVE ser trecho literal conferido contra o texto canônico efetivamente indexado ou acessivel, preservando bytes ou caracteres logicos, idioma, documento, edicao/versao, offsets e localizacao disponivel.

Citacao direta DEVE reproduzir fielmente o original, sem reconstrucao, complementacao, fusao, correcao silenciosa ou alteracao semantica. Parafrase, traducao, resumo e inferencia NÃO DEVEM ser rotulados como citacao.

Cada citacao DEVE:

1. ter extensao suficiente para inteligibilidade e para preservar condicao, excecao, negacao, modalidade, agente, objeto e conclusao;
2. permanecer associada somente a afirmacao que efetivamente sustenta;
3. identificar publicacao, edicao ou versao, autor ou entidade, titulo, idioma e formato;
4. apontar pagina, intervalo, secao, capitulo, artigo, item, paragrafo, posicao, ancora, offset ou identificador interno equivalente conforme disponibilidade;
5. permitir localizacao e conferencia pelo usuario;
6. preservar o original quando acompanhada de traducao.

Quando o trecho isolado for insuficiente, a recuperacao DEVE expandir seletivamente definicao, premissa, excecao, nota, referencia interna, paragrafo adjacente, secao, pagina ou outra passagem correlata. Citacao formalmente correta, mas materialmente enganosa por descontextualizacao, DEVE ser rejeitada.

Quantidade e extensao de prova DEVEM ser proporcionais ao risco, complexidade e finalidade. Pergunta simples PODE usar prova concisa; comparacao, controversia, interpretacao normativa ou argumento complexo DEVE ampliar fundamentacao. Despejo de citacoes sem funcao e fragmento incapaz de comprovar a afirmacao sao proibidos.

Antes da resposta, o sistema DEVE verificar pertinencia e suficiência das fontes, cobertura dos argumentos, passagens contraditorias ou qualificadoras, dependencias nao localizadas, conclusoes que excedam o corpus e integridade contextual.

Prova insuficiente DEVE produzir limitacao ou abstencao explicita. O sistema NÃO DEVE preencher lacuna com seguranca aparente, referencia fabricada ou conclusao não suportada.

Validacao DEVE impedir ou detectar citacao inexistente, pagina/secao incorreta, trechos de fontes diferentes fundidos, texto alterado, atribuicao equivocada, parafrase como citacao, traducao como original, conclusao sem suporte, excecao material omitida e fragmento sem contexto suficiente.

## 53. Referencia, localizacao e traducao vinculada

Cada fonte utilizada DEVE possuir referencia documental ou bibliografica completa segundo os metadados efetivamente disponiveis: autor, orgao, entidade ou responsavel; titulo e subtitulo; edicao, versao ou revisao; data; editora, emissor ou repositorio; idioma; tipo e formato; identificador persistente; URL publica direta e URL de origem; data de acesso quando pertinente; hash de integridade normatizado; e localizacao exata do trecho.

Metadado ausente NÃO DEVE ser inventado. Campo indisponivel DEVE ser omitido ou marcado como nao determinado conforme o contrato de saida, sem preencher por plausibilidade.

Referencia e localizacao DEVEM ser validadas contra a publicacao e a representacao efetivamente consultadas. Alinhamento PDF-EPUB PODE enriquecer pagina e estrutura somente sob confianca suficiente; sem alinhamento, a localizacao real disponivel DEVE prevalecer.

Fonte em idioma diferente da conversa DEVE manter a citacao original como prova. Traducao PODE ser adicionada imediatamente associada, identificada como traducao e separada da transcricao; a obrigacao mais estrita de traducao `en-US` para `pt-BR` do §19 permanece.

Traducao NÃO DEVE substituir o original, esconder ambiguidade nem atribuir a fonte redacao existente apenas na interpretacao traduzida. Termo tecnico, juridico, normativo ou semanticamente sensivel DEVE preservar tambem a forma original. Divergencia material entre traducoes existentes DEVE ser informada.

Interface aplicavel DEVE permitir abrir a publicacao na localizacao citada quando tecnicamente suportado, consultar referencia completa, alternar original/traducao, expandir contexto adjacente e copiar citacao ou referencia sem perda de integridade.

## 54. Pesquisa profunda, relacoes e documentos de autoridade

O Modo Conversa DEVE poder executar pesquisa profunda proporcional antes de responder, decompondo pergunta complexa, localizando terminologias distintas, relacionando partes distantes da mesma publicacao, cruzando publicacoes, comparando edicoes/versoes e recuperando fundamentos além dos primeiros fragmentos semelhantes.

Pesquisa profunda NÃO DEVE ser simulada. A estrategia DEVE revisar suficiência e PODE iterar recuperacao, filtros, expansao, vizinhanca, referencia, hierarquia, reranking e diversidade dentro dos limites configurados.

Cada fonte DEVE poder ser classificada, quando a evidencia permitir, como primaria, secundaria, normativa, interpretativa, historica ou outra categoria declarada. A classificacao DEVE influenciar precedencia e apresentacao sem ocultar fonte relevante.

Relacao entre publicacoes DEVE possuir tipo explicito, incluindo confirmacao, complementacao, especializacao, divergencia, revogacao, dependencia, evolucao historica, aplicacao, interpretacao ou analogia. Relacao inferida DEVE ser marcada como inferencia, sustentada por evidencias proprias e NÃO DEVE ser apresentada como vinculo declarado.

Documento tecnico, normativo, governamental ou legal DEVE receber tratamento compativel com hierarquia, vigencia, competencia, jurisdicao, versao, escopo, definicoes, remissoes, condicoes e excecoes.

Nesses documentos, a recuperacao e composicao DEVEM privilegiar fonte primaria disponivel; distinguir texto normativo de explicacao, parecer, jurisprudencia, doutrina, manual ou comentario; preservar verbos normativos e condicionantes; identificar versao, vigencia e jurisdicao quando comprovadas; e sinalizar conflito, revogacao, alteracao ou incerteza.

Conclusao categórica NÃO DEVE ser emitida quando a fonte, sua autoridade, vigencia ou cobertura não a sustentar.

## 55. Sessao, rastreabilidade e reproducao

Cada sessao conversacional DEVE possuir identidade estável e registrar, conforme privacidade e retencao configuradas: consulta original; decomposicoes relevantes; modo; filtros e recortes; publicacoes consultadas; unidades recuperadas; trechos utilizados; referencias emitidas; traducoes geradas; relacoes e inferencias relevantes; componentes/versoes; limitacoes; e falhas de recuperacao.

Registro DEVE permitir auditoria e reproducao proporcional da resposta sem exigir exposicao de raciocinio interno privado da IA.

Associacao entre afirmacao, evidencia, referencia, traducao, interpretacao e inferencia DEVE ser persistida por identificadores estáveis ou relacoes equivalentes, sem depender somente da apresentacao visual.

Alteracao de documento, edicao, extrator, segmentacao, indice, modelo, prompt, tradutor, reranker, configuracao causal ou politica que invalide evidencia DEVE marcar resposta ou sessao afetada como obsoleta e exigir revalidacao antes de reutilizacao probatoria.

Retomada DEVE restaurar apenas contexto validado, respeitar limites e impedir mistura entre sessoes. Cancelamento, expiracao, exclusao e falha DEVEM preservar estado íntegro e diagnostico proporcional.

Logs e telemetria DEVEM minimizar conteudo, usar referencias/hashes quando suficientes e manter consulta ou trecho sensivel fora de saida publica.

## 56. Arquitetura, interface, desempenho e degradacao

Recuperacao, indexacao, busca lexical, semantica e hibrida, reranking, expansao, leitura contextual e geracao DEVEM ser selecionados conforme aplicabilidade e estado real. LLM NÃO DEVE ser imposta a todas as etapas nem degradar pesquisa simples.

Cache, pre-processamento, indices especializados e execucao local ou remota DEVEM equilibrar precisao, cobertura, latencia, custo, disponibilidade e fidelidade. Profundidade da pesquisa e orcamento de recursos DEVEM ser configuraveis, limitados e visiveis no diagnostico.

LLM, tradutor, reranker e componente avançado DEVEM declarar contrato, modelo/versao, entrada, saida, limite, timeout, cancelamento, custo, privacidade, variacao, fallback e validacao. A adocao como padrao exige ganho medido conforme §39.

Indisponibilidade ou inadequacao de componente avançado DEVE:

1. preservar no Modo Pesquisa todas as capacidades independentes;
2. limitar sintese ou interpretacao do Modo Conversa sem fabricar resposta;
3. emitir citacao e referencia somente quando verificadas;
4. informar objetivamente a limitacao;
5. usar alternativa prevista e segura quando existente.

A interface DEVE oferecer controle inequívoco de modo e distinguir resultado recuperado de sintese da IA. No Modo Conversa, DEVE permitir identificar quais afirmacoes cada citacao sustenta, solicitar evidencia adicional ou aprofundamento, consultar referencia, visualizar original/traducao e expandir contexto.

Controle de modo, filtros, profundidade, evidencia e sessao DEVE permanecer acessivel por teclado e tecnologias assistivas quando houver GUI. Estado visual NÃO DEVE ser a unica fonte semantica.

Operacao local continua padrao. Componente remoto NÃO DEVE receber conteudo sem autorizacao e configuracao explicitas conforme §§19, 26 e 34.

## 57. Validacao e aceite dos modos

A validacao futura DEVE usar testes determinísticos e conjuntos de avaliacao versionados que cubram:

1. preservacao integral do Modo Pesquisa e distincao funcional entre modos;
2. precisao e cobertura de recuperacao;
3. fidelidade literal e contexto das citacoes;
4. validade das localizacoes e completude das referencias;
5. associacao entre afirmacao e prova;
6. distincao entre fonte, traducao, interpretacao e inferencia;
7. relacoes multifuente, versoes e contradicoes;
8. documentos técnicos, normativos, governamentais e legais;
9. ausencia de citacao, referencia, localizacao ou atribuicao fabricada;
10. metadados incompletos, prova insuficiente e abstencao;
11. degradacao sem LLM, tradutor, reranker ou auxiliar;
12. desempenho proporcional a profundidade, latencia, tokens, memoria e custo.

O produto somente DEVE aceitar esta extensao quando:

1. o recurso de pesquisa vigente permanecer integralmente preservado e nao conversacional;
2. o usuario puder selecionar explicitamente Pesquisa ou Conversa;
3. LLM for usada apenas quando agregar valor e nunca como substituicao obrigatoria;
4. o Modo Conversa interpretar, conectar e argumentar com base no acervo;
5. cada afirmacao material possuir citacao exata, referencia completa disponivel e localizacao verificavel;
6. citacoes preservarem contexto, condicionantes, excecoes e integridade;
7. fonte em outro idioma exibir original e traducao identificada quando exigida ou necessaria;
8. conteudo da fonte, interpretacao, comparacao e inferencia permanecerem distinguiveis;
9. relacoes entre publicacoes forem tipadas e fundamentadas;
10. documentos de autoridade receberem tratamento compativel com sua natureza;
11. fabricacao e atribuicao incorreta forem impedidas ou detectadas;
12. limitacao de prova produzir declaracao ou abstencao;
13. apresentacao mantiver rigor logico e academico proporcional sem prolixidade obrigatoria;
14. os contratos forem incorporados ao RCF sem duplicar ou enfraquecer normas vigentes.

Relatorio de aceite DEVE registrar normas preservadas/especializadas, alteracoes do RCF, arquitetura adotada, diferencas entre modos, criterios de uso de LLM, modelo de citacao/referencia/traducao, prevencao de alucinacao, FTs, testes, conjuntos de avaliacao, metricas de precisao/fidelidade/cobertura/latencia/custo, limitacoes, pendencias e riscos.

## 58. Convergencia das fontes

Os requisitos registrados na fonte canônica `.ia.rules/state/TODO.ia.md` linhas 56, 69, 95, 214, 886 e 1182 foram absorvidos por este RCF como contratos permanentes.

O arquivo de TODO permanece somente como fonte versionada e controle de demanda ate o encerramento documental da FT-003; implementacao futura DEVE derivar deste RCF e das FTs, nao do TODO.
