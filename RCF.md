# RCF - egwSearch

Este RCF e a especificacao normativa do egwSearch. `AGENTS.md` governa processo, precedencia e operacao de IA; este arquivo governa produto, requisitos, contratos, criterios de aceite e restricoes de negocio/arquitetura.

Aplicam-se `./AGENTS.md`, `./.ia.rules/core/concepts/microconceitos.md` (`MN-2119`, `MN-DENS`, `MN-PRES`, `MN-REF`, `MN-STATE`, `MN-VAL`, `MN-CLI`, `MN-CMD`) e `./.ia.rules/core/contracts.md`.

## 1. Identidade e objetivo

egwSearch DEVE ser uma ferramenta local para pesquisar conceitos, palavras, expressoes e formulacoes semanticamente equivalentes em colecoes arbitrarias de publicacoes textuais PDF e EPUB distribuidas em diretorios recursivos de profundidade ilimitada.

A ferramenta DEVE suportar livros, compilacoes, devocionais, revistas, jornais, periodicos, edicoes, traducoes e titulos disponiveis simultaneamente em PDF e EPUB.

Cada pesquisa individual DEVE gerar ou atualizar exatamente um arquivo Markdown principal consolidado, com todas as ocorrencias encontradas na colecao, agrupadas, deduplicadas, referenciadas, auditaveis e traduzidas quando aplicavel.

A busca DEVE localizar correspondencia literal, variantes ortograficas e morfologicas, flexoes, traducoes, sinonimos, locucoes, parafrases, expressoes semanticamente equivalentes e formulacoes em `pt-BR` e `en-US`.

Precisao, rastreabilidade, reutilizacao de tecnologia existente, resiliencia, processamento incremental e revisao controlada de ambiguidades DEVEM prevalecer sobre conveniencia de implementacao.

## 2. Estado de inicializacao

Este repositorio esta inicializado somente no quesito normativo. A existencia deste RCF, do README e das FTs NAO DEVE ser interpretada como implementacao funcional, selecao definitiva de tecnologia, instalacao de dependencia, teste executavel, build, pacote, workflow ou publicacao.

A implementacao tecnica somente PODE iniciar apos solicitacao nova, explicita e inequivoca do desenvolvedor, registrada em FT propria conforme `MN-STATE`.

## 3. Direcao tecnologica

Nenhuma linguagem, biblioteca, motor, indice, modelo, banco, runtime ou arquitetura DEVE ser escolhido por preferencia, reputacao ou conveniencia isolada.

A selecao tecnologica DEVE resultar de comparacao objetiva de qualidade, manutencao, licenca, compatibilidade, portabilidade, precisao, desempenho, memoria, instalacao, seguranca, funcionamento local, integracao, maturidade, testes, custo operacional e substituibilidade.

Node.js, Python, Ruby, Rust, Java, C#, shell ou arquitetura hibrida PODEM ser utilizados quando a avaliacao tecnica justificar. Implementacao propria em Node.js DEVE usar TypeScript; essa obrigacao NAO se aplica a dependencias de terceiros.

TypeScript, Python, Rust, SQLite, indice invertido, indice vetorial, embeddings, modelos multilingues, reranking e ferramentas nativas PODEM ser avaliados, mas NAO DEVEM ser tratados como decisao antes da FT tecnica.

Arquitetura hibrida somente DEVE ser adotada quando o ganho verificavel superar complexidade, distribuicao, instalacao, manutencao e risco operacional adicionais.

## 4. Reutilizacao obrigatoria

A implementacao NAO DEVE recriar algoritmos, extratores, parsers, tokenizadores, modelos, indices, tradutores ou funcoes ja oferecidas por solucao adequada.

Antes de implementar qualquer capacidade, a FT tecnica DEVE avaliar solucoes existentes quanto a funcionalidade, manutencao, testes, licenca, seguranca, precisao, desempenho, tamanho, compatibilidade, adequacao ao corpus e substituibilidade.

Codigo proprio somente DEVE existir para integracao, adaptacao, composicao, regras editoriais especificas, lacuna funcional comprovada, incompatibilidade tecnica, dependencia desproporcional ou ausencia de solucao mantida.

Tecnologias como PyMuPDF, parsers EPUB estruturais, Hugging Face Tokenizers, spaCy, Stanza, SQLite FTS5, Lucene, Xapian, Tantivy, Sentence Transformers, Cross-Encoders, FAISS, HNSW, Qdrant, LanceDB, RapidFuzz, MinHash, SimHash, LSH, Argos Translate, MarianMT, NLLB ou equivalentes PODEM integrar a matriz de avaliacao sem obrigacao de adocao.

## 5. Escopo de corpus e descoberta

A ferramenta DEVE receber `target` configuravel, percorrer recursivamente toda a arvore, suportar profundidade arbitraria, processar qualquer quantidade de arquivos dentro dos limites configurados, funcionar fora da raiz do repositorio, tolerar nomes nao padronizados e detectar arquivos novos, alterados, removidos ou duplicados.

A ferramenta NAO DEVE depender de estrutura fixa, profundidade conhecida, nome especifico de diretorio, quantidade predeterminada, execucao no diretorio dos livros ou importacao previa em software externo.

OCR NAO DEVE ser executado por padrao em arquivos textuais. Falha de extracao DEVE acionar rotas alternativas limitadas, registrar o problema, continuar os demais arquivos e NAO inventar conteudo.

## 6. Publicacao logica

PDF e EPUB equivalentes DEVEM representar uma unica publicacao logica e NAO DEVEM gerar citacoes duplicadas.

A associacao DEVE considerar, quando disponiveis, titulo, autor, idioma, editora, edicao, ISBN, ISSN, volume, numero, data, metadados, nome normalizado, hash, fingerprint, similaridade textual, estrutura e ordem dos capitulos.

Arquivos de mesmo titulo NAO DEVEM ser fundidos quando houver diferenca material de edicao, traducao, data, conteudo, paginacao ou revisao.

Quando PDF e EPUB forem equivalentes, RECOMENDA-SE usar EPUB para estrutura, capitulos, secoes e paragrafos; PDF para paginacao e representacao editorial; alinhamento textual entre ambos; e fallback reciproco.

Associacoes incertas DEVEM permanecer separadas ou marcadas para revisao.

## 7. Extracao de PDF

A extracao de PDF DEVE preservar, quando disponiveis, paginas fisicas, numeros impressos, palavras, linhas, blocos, coordenadas, fontes, estilos, colunas, titulos, subtitulos, notas, cabecalhos, rodapes, datas, volume, numero e edicao.

A reconstrucao NAO DEVE concatenar indiscriminadamente o texto da pagina.

Cabecalhos, rodapes e numeros de pagina DEVEM ser identificados por combinacao de repeticao, posicao, frequencia, tipografia, baixa variacao, padroes e distancia do corpo. Um elemento somente DEVE ser removido quando a confianca for suficiente.

## 8. Extracao de EPUB

A extracao de EPUB DEVE respeitar container, manifesto, spine, XHTML, `nav`, NCX, landmarks, page list, headings, capitulos, secoes, paragrafos, notas, metadados, datas, edicao, volume e numero.

A ordem DEVE seguir o spine e a estrutura semantica DEVE ser preservada.

Sem paginacao estavel, a ferramenta NAO DEVE inventar paginas; DEVE usar pagina do PDF equivalente quando houver alinhamento confiavel; caso contrario, DEVE usar localizacao EPUB deterministica e indicar ausencia de pagina.

## 9. Reconstrucao editorial

A unidade de citacao DEVE ser o paragrafo semantico integral.

A ferramenta DEVE reconstruir paragrafos quebrados por linhas, atravessando paginas, com hifenizacao editorial, divididos por blocos, interrompidos por cabecalho ou rodape e distribuidos em colunas.

A ferramenta DEVE distinguir quebra visual de linha, quebra real de paragrafo, mudanca de pagina, mudanca de coluna, titulo, subtitulo, lista, nota, bloco de citacao, unidade editorial e mudanca de data.

A decisao DEVERIA combinar geometria, pontuacao, capitalizacao, recuo, espacamento, tipografia, continuidade sintatica, segmentacao linguistica, estrutura EPUB e contexto anterior/posterior.

Paragrafos distintos NAO DEVEM ser unidos por heuristica isolada. Paragrafo entre paginas DEVE referenciar todas elas, preferencialmente como intervalo.

## 10. Referencias e publicacoes datadas

Cada citacao DEVE preservar, quando aplicavel, titulo, autor, capitulo, secao, pagina ou intervalo, edicao, volume, numero, data, idioma, localizacao EPUB e fonte PDF/EPUB.

A identificacao DEVE usar evidencia em ordem de confianca: estrutura explicita; metadados confiaveis; conteudo editorial; pagina de rosto, sumario ou expediente; filename; diretorio; fallback marcado.

Metadados NAO DEVEM ser inventados.

Devocionais, revistas, jornais e periodicos DEVEM incluir data editorial ou de destinacao na referencia. A data DEVE ser associada a unidade textual vigente, nao apenas ao arquivo.

A ferramenta NAO DEVE confundir data editorial com criacao do arquivo, modificacao, extracao, execucao ou indexacao. Datas de filesystem somente PODEM ser usadas com configuracao explicita ou confirmacao adicional.

## 11. Consulta, expansao e variantes

A consulta PODE ser palavra, expressao, frase, conceito em linguagem natural, termos obrigatorios ou exclusoes.

A expansao DEVE considerar de forma controlada traducao, flexao, lematizacao, singular/plural, genero, conjugacao, variantes ortograficas, sinonimos, locucoes, parafrases, expressoes equivalentes, formas correlatas e termos configurados manualmente.

A expansao NAO DEVE tornar a consulta excessivamente ampla.

Cada variante DEVE registrar texto, idioma, origem, metodo, peso, confianca e relacao com a consulta original.

O usuario DEVE poder revisar, incluir, excluir, fixar expressoes, limitar idiomas, definir thresholds, usar busca literal e usar busca hibrida.

## 12. Registro da pesquisa

No inicio do Markdown de resultado DEVEM constar termo original, idioma original, idiomas pesquisados, modo de busca, thresholds, inclusoes, exclusoes, traducoes, flexoes, sinonimos, expressoes equivalentes, parafrases e todas as variantes efetivamente pesquisadas.

Variantes efetivamente usadas NAO DEVEM ser omitidas. Variantes geradas e rejeitadas PODEM permanecer apenas no relatorio tecnico.

## 13. Busca hibrida

A recuperacao DEVE combinar, quando proporcional, correspondencia literal, normalizacao, busca por frase, analise morfologica, sinonimos, fuzzy matching, busca semantica multilingue, reranking contextual, filtros linguisticos e classificacao por confianca.

A busca lexical NAO DEVE ser substituida pela semantica. A busca semantica NAO DEVE decidir isoladamente.

RECOMENDA-SE pipeline com expansao da consulta, geracao lexical de candidatos, geracao vetorial de candidatos, uniao, fusao de rankings, reranking, analise de negacao/modalidade/numeros/datas/termos criticos, threshold, classificacao e evidencia.

Reciprocal Rank Fusion ou tecnica equivalente PODE combinar rankings heterogeneos.

## 14. Tokenizacao e representacoes

A ferramenta DEVE preservar separadamente texto original, texto estrutural, texto normalizado, tokens, lemas, offsets, fingerprints e embeddings quando usados.

A normalizacao DEVE permitir localizar a correspondencia e recuperar exatamente o texto original.

Tokenizacao, normalizacao e segmentacao NAO DEVEM destruir acentuacao original, pontuacao relevante, grafia editorial, localizacao, referencia ou offsets.

## 15. Persistencia e indexacao

A ferramenta DEVERIA manter indice persistente e incremental.

O indice DEVE permitir processamento incremental, consultas repetidas, retomada, atualizacao, remocao de dados obsoletos, associacao PDF-EPUB, busca lexical, busca semantica, deduplicacao e rastreabilidade.

O modelo persistente DEVE armazenar publicacoes, formatos, edicoes, capitulos, secoes, paragrafos, paginas, datas, referencias, texto original, texto normalizado, tokens, fingerprints, embeddings, hashes, confianca, versao do extrator, checkpoints e pesquisas.

O Markdown NAO DEVE ser a fonte primaria de persistencia.

## 16. Deduplicacao

Textos equivalentes apos normalizacao segura DEVEM compartilhar uma unica citacao logica. A normalizacao PODE tratar espacos, quebras visuais, hifenizacao, Unicode, aspas, travessoes, capitalizacao, pontuacao nao material e artefatos editoriais.

Variacoes minimas PODEM ser consolidadas mediante n-gramas, Jaccard, MinHash, SimHash, Levenshtein, Damerau-Levenshtein, Jaro-Winkler, LCS, RapidFuzz ou equivalente, embeddings e alinhamento de tokens.

A ferramenta DEVE verificar diferencas criticas, incluindo negacao, modalidade, condicao, agente, objeto, datas, numeros, nomes, intensidade, conclusao e significado.

Diferenca pequena em caracteres NAO DEVE implicar equivalencia semantica.

Resultados DEVEM poder ser classificados como consolidar automaticamente, manter separados ou revisao recomendada.

Antes de adicionar uma citacao, a ferramenta DEVE verificar se ela ja existe no resultado ou no Markdown da mesma pesquisa. Se ja existir, NAO DEVE criar novo bloco, DEVE adicionar somente referencia ausente e NAO DEVE repetir referencia.

Compilacoes, antologias e republicacoes DEVEM gerar multiplas referencias sob uma unica citacao quando o texto for equivalente.

## 17. Alinhamento PDF-EPUB

Quando ambos existirem, a ferramenta DEVERIA alinhar estrutura EPUB e paginacao PDF.

O alinhamento PODE combinar hashes, ancoras exatas, n-gramas, fingerprints, similaridade lexical, embeddings, LCS, programacao dinamica, Needleman-Wunsch, Smith-Waterman, Dynamic Time Warping e alinhamento monotonico.

A ordem textual DEVERIA ser explorada para reduzir ambiguidades. Cada associacao DEVE possuir confianca.

## 18. Identificacao de idioma

O idioma DEVE ser inferido por combinacao de metadados, deteccao documental, deteccao por paragrafo, vocabulario, modelo de identificacao e contexto.

A ferramenta DEVE suportar conteudo misto e NAO DEVE depender exclusivamente de filename para identificar idioma.

## 19. Traducao

Toda citacao original em `en-US` DEVE ser imediatamente seguida por traducao `pt-BR`.

A traducao DEVE abranger somente o texto, NAO DEVE traduzir referencia, DEVE usar bloco de citacao, DEVE ser identificada como **Traducao livre**, DEVE preservar sentido e tom e DEVE permanecer separada do original.

Traducao local open source DEVERIA ser preferida quando possuir qualidade suficiente.

API publica ou gratuita PODE ser usada somente quando autorizada, estavel, adequada ao volume, compativel com privacidade, configuravel e resiliente.

Conteudo NAO DEVE ser enviado a terceiros sem autorizacao explicita.

Traducoes DEVEM usar cache por hash, idiomas e versao do tradutor. Falha de traducao NAO DEVE remover a citacao original.

## 20. Markdown unico por pesquisa

Cada pesquisa individual DEVE possuir exatamente um Markdown principal.

O Markdown DEVE consolidar consulta, variantes, metadados, resultados em `pt-BR`, resultados em `en-US`, traducoes, referencias, contagens e resumo.

A identidade da pesquisa DEVE considerar consulta original, idiomas, inclusoes, exclusoes, modo, modelos, configuracoes e thresholds.

O arquivo NAO DEVE misturar pesquisas materialmente distintas.

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

A analise NAO DEVE depender apenas de busca textual bruta.

Identificadores PODEM ser preservados por front matter, comentarios HTML, sidecar, indice ou mecanismo equivalente. Metadados tecnicos NAO DEVEM prejudicar a leitura.

## 23. Confianca e auditabilidade

Cada inferencia relevante DEVE possuir evidencia e confianca separadas, incluindo extracao, estrutura, titulo, capitulo, pagina, data, idioma, associacao PDF-EPUB, correspondencia lexical, correspondencia semantica, deduplicacao e traducao.

Classificacoes PODEM incluir confirmado, alta confianca, provavel, revisao recomendada, indeterminado e rejeitado.

A ferramenta NAO DEVE apresentar inferencia como certeza sem evidencia.

## 24. Failsafe

Failsafe significa concluir todo o trabalho processavel, isolar falhas, preservar resultados validos e informar precisamente o que nao foi concluido.

A ferramenta DEVE possuir isolamento por arquivo, checkpoints, retomada, cache, timeouts, tentativas limitadas, backoff limitado, fallbacks, fila de problemas, logs estruturados, escrita atomica, recuperacao e resumo final.

A ferramenta NAO DEVE entrar em loop infinito, tentar indefinidamente, interromper toda a colecao por falha isolada, ocultar falhas, inventar dados, descartar arquivo silenciosamente, duplicar resultados apos retomada ou corromper saida existente.

Cada fallback DEVE declarar condicao, limite, resultado, motivo e proximo estado.

## 25. Desempenho e configuracao operacional

A ferramenta DEVE evitar carregar toda a colecao simultaneamente.

RECOMENDA-SE streaming, lotes, filas, concorrencia limitada, workers, cache, indexacao incremental, persistencia e processamento por fases.

A concorrencia DEVE respeitar CPU, memoria, disco, APIs e estabilidade dos extratores.

Configuracoes DEVEM incluir workers, lotes, cache, memoria, timeout, tentativas, thresholds, idiomas, tradutor, logs e rede.

## 26. Seguranca e privacidade

A operacao DEVE ser local por padrao.

A ferramenta NAO DEVE enviar publicacoes completas externamente, executar JavaScript de EPUB, confiar em filenames, permitir path traversal, extrair fora de area controlada, sobrescrever sem validacao, registrar conteudo integral desnecessariamente ou expor paths/dados sensiveis.

EPUBs DEVEM ser tratados como arquivos nao confiaveis.

A extracao DEVE proteger contra Zip Slip, expansao excessiva, bomba de compressao, entidades externas, conteudo malformado, loops e arquivos abusivos.

## 27. CLI e saida

A interface de pesquisa DEVERIA ser equivalente a:

```text
search-publications --target <diretorio> --query "<termo ou conceito>" --languages pt-BR,en-US --output <pesquisa.md>
```

A CLI DEVERIA permitir indexar, pesquisar, reconstruir indice, listar publicacoes, inspecionar associacoes, exibir variantes, definir thresholds, selecionar tradutor, operar offline, retomar, atualizar resultado, filtrar autor, filtrar idioma, filtrar data, filtrar tipo e gerar diagnostico.

A configuracao DEVE aplicar precedencia explicita: CLI, arquivo, ambiente e padroes seguros.

A saida DEVE ser sucinta, colorida quando suportado, desativavel, legivel por humanos, processavel por IA, disponivel em formato estruturado e sem inundacao de logs.

Saida destinada a IA ou automacao do repositorio DEVE seguir `MN-CMD` e `MN-OUT` quando integrada ao contrato `agent:*`.

## 28. Testes obrigatorios futuros

A implementacao DEVE possuir testes para PDF simples, cabecalho/rodape, multiplas colunas, pagina atravessada, hifenizacao, paginacao romana, EPUB com `nav`, EPUB com NCX, EPUB sem pagina, associacao PDF-EPUB, edicoes distintas, diretorios profundos, busca literal, morfologia, sinonimos, parafrases, busca bilingue, polissemia, negacao, ranking hibrido, deduplicacao exata, variacao minima, diferenca material, multiplas referencias, compilacoes, devocionais, revistas, jornais, traducao, cache, retomada, escrita atomica, Markdown existente, falhas de extrator, falhas de traducao, timeout, arquivo corrompido, Zip Slip, bomba de compressao, seguranca e desempenho.

Fixtures DEVEM incluir arquivos reais autorizados, arquivos emulados e arquivos gerados automaticamente. Testes externos DEVEM permanecer separados e opcionais.

## 29. Ordem de implementacao futura

A FT tecnica DEVE executar em etapas validadas sequencialmente: analise do corpus; avaliacao de linguagens, bibliotecas e modelos; contratos; descoberta; modelo de publicacao; extracao EPUB; extracao PDF; limpeza; reconstrucao; referencias e datas; alinhamento; persistencia; tokenizacao; indexacao lexical; indexacao semantica; expansao bilingue; recuperacao hibrida; reranking; deduplicacao; consolidacao; traducao; Markdown; failsafe; testes; otimizacao; documentacao; validacao.

Cada etapa DEVE ser validada antes da seguinte.

## 30. Criterios de aceite tecnico

A implementacao somente DEVE ser considerada concluida quando percorre diretorios arbitrarios, processa PDF e EPUB textuais, associa formatos equivalentes, distingue edicoes, reconstroi paragrafos, identifica titulo/capitulo/pagina/data, registra variantes pesquisadas, combina busca lexical e semantica, traduz citacoes inglesas, gera um unico Markdown por pesquisa, consolida citacoes repetidas, acumula referencias, preserva diferencas materiais, atualiza idempotentemente, retoma apos falhas, nao entra em loop, nao fabrica metadados, registra confianca, registra arquivos nao processados e executa testes verificaveis.

Nenhuma capacidade DEVE ser declarada como aceita sem evidencia de validacao executada.

## 31. Entregaveis futuros

A entrega funcional DEVE conter projeto funcional, fontes, configuracao, CLI, persistencia/indices, testes, fixtures, documentacao, exemplo de Markdown consolidado e relatorio sucinto com tecnologia escolhida, alternativas avaliadas, bibliotecas reutilizadas, codigo proprio e justificativa, arquitetura, modelos, indices, comandos, testes, resultados, limitacoes, niveis de confianca, fallbacks e arquivos nao processados.

## 32. README, badges e metadados

`README.md` DEVE existir, ser ultrassucinto, informativo e nao normativo.

O README DEVE identificar o projeto sem anunciar como implementado o que estiver apenas planejado, e DEVE apontar para `RCF.md` e `AGENTS.md`.

Badges e indicadores DEVEM acompanhar a evolucao real do escopo, licenca, validacoes, linguagens, runtimes, builds, cobertura, pacote, release, manutencao e compatibilidade. Indicador dinamico somente DEVE existir quando a fonte verificavel correspondente existir. Indicador estatico PODE informar estado documental, planejamento ou licenca quando verdadeiro.

Badges NAO DEVEM apresentar aprovacao, cobertura, compatibilidade, build, release ou disponibilidade nao verificada; DEVEM ser atualizados ou removidos quando obsoletos.

Autoria, repositorio e licenca DEVEM vir de artefatos reais do repositorio. Dado ausente NAO DEVE ser inventado e DEVE permanecer como pendencia.

## 33. FTs e continuidade

FT normativa e FT tecnica DEVEM permanecer segregadas em `.ia.rules/state/continue.ia`.

FT normativa DEVE cobrir RCF, README, validacao documental, remocao de artefato transitorio aplicavel, commit e push.

FT tecnica DEVE permanecer pendente ate autorizacao humana explicita e DEVE cobrir avaliacao tecnologica, arquitetura, codigo, bibliotecas, dependencias, testes, builds, integracoes, automacoes, CI/CD e publicacao quando aplicaveis.

A conclusao normativa NAO autoriza implementacao de codigo.
