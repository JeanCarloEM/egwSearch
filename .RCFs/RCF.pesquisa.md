# RCF subordinado — Pesquisa documental

Este documento integra a suíte normativa do **egwSearch**, subordina-se ao
[RCF principal](../RCF.md) e preserva os §§5–39 e §50 da numeração global. Ele
rege extração, reconstrução, segmentação, indexação, recuperação, avaliação,
interfaces e Modo Pesquisa. Para interpretação hermenêutica, aplica-se também o
[RCF epistemológico](RCF.epistemologia.md).

**Ordem:** leia primeiro o RCF principal; depois este documento; em seguida,
somente o RCF especializado exigido pelo fluxo. Divergência aplica a
precedência declarada no RCF principal.

## 5. Escopo de corpus e descoberta

A ferramenta DEVE receber `target` configurável, percorrer recursivamente toda a árvore, suportar profundidade arbitrária, processar qualquer quantidade de arquivos dentro dos limites configurados, funcionar fora da raiz do repositório, tolerar nomes não padronizados e detectar arquivos novos, alterados, removidos ou duplicados.

A ferramenta NÃO DEVE depender de estrutura fixa, profundidade conhecida, nome específico de diretório, quantidade predeterminada, execução no diretório dos livros ou importação prévia em software externo.

OCR NÃO DEVE ser executado por padrão em arquivos textuais. Falha de extração DEVE acionar rotas alternativas limitadas, registrar o problema, continuar os demais arquivos e NÃO inventar conteúdo.

## 6. Publicação lógica

PDF e EPUB equivalentes DEVEM representar uma única publicação lógica e NÃO DEVEM gerar citações duplicadas.

A associação DEVE considerar, quando disponíveis, título, autor, idioma, editora, edição, ISBN, ISSN, volume, número, data, metadados, nome normalizado, hash, fingerprint, similaridade textual, estrutura e ordem dos capítulos.

Arquivos de mesmo título NÃO DEVEM ser fundidos quando houver diferença material de edição, tradução, data, conteúdo, paginação ou revisão.

Quando PDF e EPUB forem equivalentes, RECOMENDA-SE usar EPUB para estrutura, capítulos, seções e parágrafos; PDF para paginação e representação editorial; alinhamento textual entre ambos; e fallback recíproco.

Associações incertas DEVEM permanecer separadas ou marcadas para revisão.

## 7. Extração de PDF

A extração de PDF DEVE preservar, quando disponíveis, páginas físicas, números impressos, palavras, linhas, blocos, coordenadas, fontes, estilos, colunas, títulos, subtítulos, notas, cabeçalhos, rodapés, datas, volume, número e edição.

A reconstrução NÃO DEVE concatenar indiscriminadamente o texto da página.

Cabeçalhos, rodapés e números de página DEVEM ser identificados por combinação de repetição, posição, frequência, tipografia, baixa variação, padrões e distância do corpo. Um elemento somente DEVE ser removido quando a confiança for suficiente.

## 8. Extração de EPUB

A extração de EPUB DEVE respeitar container, manifesto, spine, XHTML, `nav`, NCX, landmarks, page list, headings, capítulos, seções, parágrafos, notas, metadados, datas, edição, volume e número.

A ordem DEVE seguir o spine e a estrutura semântica DEVE ser preservada.

Sem paginação estável, a ferramenta NÃO DEVE inventar páginas; DEVE usar página do PDF equivalente quando houver alinhamento confiável; caso contrário, DEVE usar localização EPUB determinística e indicar ausência de página.

## 9. Reconstrução editorial

A unidade de citação DEVE ser o parágrafo semântico integral.

A ferramenta DEVE reconstruir parágrafos quebrados por linhas, atravessando páginas, com hifenização editorial, divididos por blocos, interrompidos por cabeçalho ou rodapé e distribuídos em colunas.

A ferramenta DEVE distinguir quebra visual de linha, quebra real de parágrafo, mudança de página, mudança de coluna, título, subtítulo, lista, nota, bloco de citação, unidade editorial e mudança de data.

A decisão DEVERIA combinar geometria, pontuação, capitalização, recuo, espaçamento, tipografia, continuidade sintática, segmentação linguística, estrutura EPUB e contexto anterior/posterior.

Parágrafos distintos NÃO DEVEM ser unidos por heurística isolada. Parágrafo entre páginas DEVE referenciar todas elas, preferencialmente como intervalo.

## 10. Referências e publicações datadas

Cada citação DEVE preservar, quando aplicável, título, autor, capítulo, seção, página ou intervalo, edição, volume, número, data, idioma, localização EPUB e fonte PDF/EPUB.

A identificação DEVE usar evidência em ordem de confiança: estrutura explícita; metadados confiáveis; conteúdo editorial; página de rosto, sumário ou expediente; filename; diretório; fallback marcado.

Metadados NÃO DEVEM ser inventados.

Devocionais, revistas, jornais e periódicos DEVEM incluir data editorial ou de destinação na referência. A data DEVE ser associada a unidade textual vigente, não apenas ao arquivo.

A ferramenta NÃO DEVE confundir data editorial com criação do arquivo, modificação, extração, execução ou indexação. Datas de filesystem somente PODEM ser usadas com configuração explícita ou confirmação adicional.

## 11. Consulta, expansão e variantes

A consulta PODE ser palavra, expressão, frase, conceito em linguagem natural, termos obrigatórios ou exclusões.

A expansão DEVE considerar de forma controlada tradução, flexão, lematização, singular/plural, gênero, conjugação, variantes ortográficas, sinônimos, locuções, paráfrases, expressões equivalentes, formas correlatas e termos configurados manualmente.

A expansão NÃO DEVE tornar a consulta excessivamente ampla.
Cada variante DEVE registrar texto, idioma, origem, método, peso, confiança e relação com a consulta original.

O usuário DEVE poder revisar, incluir, excluir, fixar expressões, limitar idiomas, definir thresholds, usar busca literal e usar busca híbrida.

## 12. Registro da pesquisa

No início do Markdown de resultado do Modo Pesquisa DEVEM constar termo original, idioma original, idiomas pesquisados, modo de busca, thresholds, inclusões, exclusões, traduções, flexões, sinônimos, expressões equivalentes, paráfrases e todas as variantes efetivamente pesquisadas.

Variantes efetivamente usadas NÃO DEVEM ser omitidas. Variantes geradas e rejeitadas PODEM permanecer apenas no relatório técnico.

## 13. Busca híbrida

A recuperação DEVE combinar, quando proporcional, correspondência literal, normalização, busca por frase, análise morfológica, sinônimos, fuzzy matching, busca semântica multilíngue, reranking contextual, filtros linguísticos e classificação por confiança.

A busca lexical NÃO DEVE ser substituída pela semântica. A busca semântica NÃO DEVE decidir isoladamente.

RECOMENDA-SE pipeline com expansão da consulta, geração lexical de candidatos, geração vetorial de candidatos, união, fusão de rankings, reranking, análise de negação/modalidade/números/datas/termos críticos, threshold, classificação e evidência.

Reciprocal Rank Fusion ou técnica equivalente PODE combinar rankings heterogêneos.

## 14. Tokenização e representações

A ferramenta DEVE preservar separadamente texto original, texto estrutural, texto normalizado, tokens, lemas, offsets, fingerprints e embeddings quando usados.

A normalização DEVE permitir localizar a correspondência e recuperar exatamente o texto original.

Tokenização, normalização e segmentação NÃO DEVEM destruir acentuação original, pontuação relevante, grafia editorial, localização, referência ou offsets.

## 15. Persistência e indexação

A ferramenta DEVERIA manter índice persistente e incremental.

O índice DEVE permitir processamento incremental, consultas repetidas, retomada, atualização, remoção de dados obsoletos, associação PDF-EPUB, busca lexical, busca semântica, deduplicação e rastreabilidade.

O modelo persistente DEVE armazenar publicações, formatos, edições, capítulos, seções, parágrafos, páginas, datas, referências, texto original, texto normalizado, tokens, fingerprints, embeddings, hashes, confiança, versão do extrator, checkpoints e pesquisas.

O Markdown NÃO DEVE ser a fonte primária de persistência.

## 16. Deduplicação

Textos equivalentes após normalização segura DEVEM compartilhar uma única citação lógica. A normalização PODE tratar espaços, quebras visuais, hifenização, Unicode, aspas, travessões, capitalização, pontuação não material e artefatos editoriais.

Variações mínimas PODEM ser consolidadas mediante n-gramas, Jaccard, MinHash, SimHash, Levenshtein, Damerau-Levenshtein, Jaro-Winkler, LCS, RapidFuzz ou equivalente, embeddings e alinhamento de tokens.

A ferramenta DEVE verificar diferenças críticas, incluindo negação, modalidade, condição, agente, objeto, datas, números, nomes, intensidade, conclusão e significado.

Diferença pequena em caracteres NÃO DEVE implicar equivalência semântica.

Resultados DEVEM poder ser classificados como consolidar automaticamente, manter separados ou revisão recomendada.

Antes de adicionar uma citação, a ferramenta DEVE verificar se ela já existe no resultado ou no Markdown da mesma pesquisa. Se já existir, NÃO DEVE criar novo bloco, DEVE adicionar somente referência ausente e NÃO DEVE repetir referência.

Compilações, antologias e republicações DEVEM gerar múltiplas referências sob uma única citação quando o texto for equivalente.

## 17. Alinhamento PDF-EPUB

Quando ambos existirem, a ferramenta DEVERIA alinhar estrutura EPUB e paginação PDF.

O alinhamento PODE combinar hashes, âncoras exatas, n-gramas, fingerprints, similaridade lexical, embeddings, LCS, programação dinâmica, Needleman-Wunsch, Smith-Waterman, Dynamic Time Warping e alinhamento monotônico.

A ordem textual DEVERIA ser explorada para reduzir ambiguidades. Cada associação DEVE possuir confiança.

## 18. Identificação de idioma

O idioma DEVE ser inferido por combinação de metadados, detecção documental, detecção por parágrafo, vocabulário, modelo de identificação e contexto.

A ferramenta DEVE suportar conteúdo misto e NÃO DEVE depender exclusivamente de filename para identificar idioma.

## 19. Tradução

Toda citação original em `en-US` DEVE ser imediatamente seguida por tradução `pt-BR`.

A tradução DEVE abranger somente o texto, NÃO DEVE traduzir referência, DEVE usar bloco de citação, DEVE ser identificada como **Tradução livre**, DEVE preservar sentido e tom e DEVE permanecer separada do original.

Tradução local open source DEVERIA ser preferida quando possuir qualidade suficiente.

API pública ou gratuita PODE ser usada somente quando autorizada, estável, adequada ao volume, compatível com privacidade, configurável e resiliente.

Conteúdo NÃO DEVE ser enviado a terceiros sem autorização explícita.
Traduções DEVEM usar cache por hash, idiomas e versão do tradutor. Falha de tradução NÃO DEVE remover a citação original.
No Modo Conversa, fonte em idioma diferente do diálogo DEVE preservar sempre o trecho original; tradução adicional DEVE permanecer imediatamente vinculada, identificada e separada, sem substituir a prova nem atribuir a fonte formulação exclusiva da tradução.

Ambiguidade ou termo técnico, jurídico, normativo ou semanticamente sensível DEVE preservar o termo original, e divergência relevante entre traduções existentes DEVE ser explicitada.

## 20. Markdown único por pesquisa

Esta seção rege exclusivamente o Modo Pesquisa; registro conversacional segue o contrato de sessão dos §§51-57 e NÃO DEVE ser confundido com o Markdown consolidado de ocorrências.

Cada pesquisa individual DEVE possuir exatamente um Markdown principal.

O Markdown DEVE consolidar consulta, variantes, metadados, resultados em `pt-BR`, resultados em `en-US`, traduções, referências, contagens e resumo.

A identidade da pesquisa DEVE considerar consulta original, idiomas, inclusões, exclusões, modo, modelos, configurações e thresholds.

O arquivo NÃO DEVE misturar pesquisas materialmente distintas.

Atualizações DEVEM ser idempotentes, atômicas, recuperáveis e determinísticas. RECOMENDA-SE escrever em arquivo temporário validado antes da substituição.

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

A referência DEVE aparecer somente junto ao original. Citações DEVEM possuir separação visual consistente.

## 22. Atualização de Markdown existente

Quando o arquivo da mesma pesquisa existir, a ferramenta DEVE validar identidade, analisar estruturalmente o Markdown, recuperar citações e referências, reconstruir fingerprints, comparar novos resultados, adicionar apenas conteúdo ausente, preservar conteúdo válido, atualizar contagens e ordenar deterministicamente.

A análise NÃO DEVE depender apenas de busca textual bruta.
Identificadores PODEM ser preservados por front matter, comentários HTML, sidecar, índice ou mecanismo equivalente. Metadados técnicos NÃO DEVEM prejudicar a leitura.

## 23. Confiança e auditabilidade
Cada inferência relevante DEVE possuir evidência e confiança separadas, incluindo extração, estrutura, título, capítulo, página, data, idioma, associação PDF-EPUB, correspondência lexical, correspondência semântica, deduplicação e tradução.

Classificações PODEM incluir confirmado, alta confiança, provável, revisão recomendada, indeterminado e rejeitado.

A ferramenta NÃO DEVE apresentar inferência como certeza sem evidência.

No Modo Conversa, confiança da recuperação, fidelidade da citação, validade da localização, suficiência da prova, completude da referência, tradução e conclusão DEVEM permanecer separadamente auditáveis.

## 24. Failsafe

Failsafe significa concluir todo o trabalho processável, isolar falhas, preservar resultados válidos e informar precisamente o que não foi concluído.

A ferramenta DEVE possuir isolamento por arquivo, checkpoints, retomada, cache, timeouts, tentativas limitadas, backoff limitado, fallbacks, fila de problemas, logs estruturados, escrita atômica, recuperação e resumo final.

A ferramenta NÃO DEVE entrar em loop infinito, tentar indefinidamente, interromper toda a coleção por falha isolada, ocultar falhas, inventar dados, descartar arquivo silenciosamente, duplicar resultados após retomada ou corromper saída existente.

Cada fallback DEVE declarar condição, limite, resultado, motivo e próximo estado.

Componente conversacional, LLM, tradutor ou reranker indisponível NÃO DEVE fabricar resposta, citação, referência ou localização; a capacidade independente DEVE continuar quando segura e a limitação aplicável DEVE ser informada objetivamente.

## 25. Desempenho e configuração operacional

A ferramenta DEVE evitar carregar toda a coleção simultaneamente.

RECOMENDA-SE streaming, lotes, filas, concorrência limitada, workers, cache, indexação incremental, persistência e processamento por fases.

A concorrência DEVE respeitar CPU, memória, disco, APIs e estabilidade dos extratores.

Configurações DEVEM incluir workers, lotes, cache, memória, timeout, tentativas, thresholds, idiomas, tradutor, logs e rede.

## 26. Segurança e privacidade

A operação DEVE ser local por padrão.

A ferramenta NÃO DEVE enviar publicações completas externamente, executar JavaScript de EPUB, confiar em filenames, permitir path traversal, extrair fora de área controlada, sobrescrever sem validação, registrar conteúdo integral desnecessariamente ou expor paths/dados sensíveis.

EPUBs DEVEM ser tratados como arquivos não confiáveis.

A extração DEVE proteger contra Zip Slip, expansão excessiva, bomba de compressão, entidades externas, conteúdo malformado, loops e arquivos abusivos.

Memória de conversa, consulta, decomposição, trecho recuperado, referência, tradução e diagnóstico DEVEM seguir configuração explícita de privacidade e retenção, com minimização, isolamento por sessão e exclusão controlada.

Rastreabilidade NÃO DEVE armazenar raciocínio interno privado da IA, segredo, credencial ou conteúdo integral desnecessário do acervo.

## 27. CLI e saída

A interface de pesquisa DEVERIA ser equivalente a:

```text
search-publications --target <diretorio> --query "<termo ou conceito>" --languages pt-BR,en-US --output <pesquisa.md>
```

A CLI DEVERIA permitir indexar, pesquisar, reconstruir índice, listar publicações, inspecionar associações, exibir variantes, definir thresholds, selecionar tradutor, operar offline, retomar, atualizar resultado, filtrar autor, filtrar idioma, filtrar data, filtrar tipo e gerar diagnóstico.

A configuração DEVE aplicar precedência explícita: CLI, arquivo, ambiente e padrões seguros.

Interface que exponha ambos os modos DEVE exigir seleção inequívoca entre `search` e `conversation`; default, alias ou comando abreviado NÃO DEVE alterar silenciosamente a semântica escolhida.

A saída DEVE ser sucinta, colorida quando suportado, desativável, legível por humanos, processável por IA, disponível em formato estruturado e sem inundação de logs.

Saída destinada a IA ou automação do repositório DEVE seguir `MN-CMD` e `MN-OUT` quando integrada ao contrato `agent:*`.

## 28. Testes obrigatórios futuros

A implementação DEVE possuir testes para PDF simples, cabeçalho/rodapé, múltiplas colunas, página atravessada, hifenização, paginação romana, EPUB com `nav`, EPUB com NCX, EPUB sem página, associação PDF-EPUB, edições distintas, diretórios profundos, busca literal, morfologia, sinônimos, paráfrases, busca bilíngue, polissemia, negação, ranking híbrido, deduplicação exata, variação mínima, diferença material, múltiplas referências, compilações, devocionais, revistas, jornais, tradução, cache, retomada, escrita atômica, Markdown existente, falhas de extrator, falhas de tradução, timeout, arquivo corrompido, Zip Slip, bomba de compressão, segurança e desempenho.

Fixtures DEVEM incluir arquivos reais autorizados, arquivos emulados e arquivos gerados automaticamente. Testes externos DEVEM permanecer separados e opcionais.

O Modo Conversa DEVE adicionar conjuntos determinísticos e avaliações verificáveis de fidelidade literal, localização, completude de referência, contexto, relação multifuente, tradução vinculada, abstenção, alucinação, metadado incompleto, degradação e desempenho proporcional.

## 29. Ordem de implementação futura

A FT técnica DEVE executar em etapas validadas sequencialmente: análise do corpus; avaliação de linguagens, bibliotecas e modelos; contratos; descoberta; modelo de publicação; extração EPUB; extração PDF; limpeza; reconstrução; referências e datas; alinhamento; persistência; tokenização; indexação lexical; indexação semântica; expansão bilíngue; recuperação híbrida; reranking; deduplicação; consolidação; localização e validação de citações; tradução; Markdown; composição probatória; sessão conversacional; interface de modos; failsafe; testes; otimização; documentação; validação.

Cada etapa DEVE ser validada antes da seguinte.
## 30. Critérios de aceite técnico

A implementação somente DEVE ser considerada concluída quando percorre diretórios arbitrários, processa PDF e EPUB textuais, associa formatos equivalentes, distingue edições, reconstrói parágrafos, identifica título/capítulo/página/data, registra variantes pesquisadas, combina busca lexical e semântica, traduz citações inglesas, gera um único Markdown por pesquisa, consolida citações repetidas, acumula referências, preserva diferenças materiais, oferece seleção inequívoca entre Pesquisa e Conversa, fundamenta afirmações conversacionais com prova verificável, atualiza idempotentemente, retoma após falhas, não entra em loop, não fabrica metadados, citações ou localizações, registra confiança, registra arquivos não processados e executa testes verificáveis.
Nenhuma capacidade DEVE ser declarada como aceita sem evidência de validação executada.
## 31. Entregáveis futuros
A entrega funcional DEVE conter projeto funcional, fontes, configuração, CLI, GUI aplicável, persistência/índices, testes, conjuntos de avaliação, fixtures, documentação, exemplo de Markdown consolidado, exemplo de sessão probatória e relatório sucinto com tecnologia escolhida, alternativas avaliadas, bibliotecas reutilizadas, código próprio e justificativa, arquitetura, modelos, índices, modos, critérios de uso de LLM, contrato de citação/referência/tradução, comandos, testes, métricas, resultados, limitações, níveis de confiança, fallbacks e arquivos não processados.

## 32. README, badges e metadados

`README.md` DEVE existir, ser ultrassucinto, informativo e não normativo.

O README DEVE identificar o projeto sem anunciar como implementado o que estiver apenas planejado, e DEVE apontar para `RCF.md` e `AGENTS.md`.

Badges e indicadores DEVEM acompanhar a evolução real do escopo, licença, validações, linguagens, runtimes, builds, cobertura, pacote, release, manutenção e compatibilidade. Indicador dinâmico somente DEVE existir quando a fonte verificável correspondente existir. Indicador estático PODE informar estado documental, planejamento ou licença quando verdadeiro.

Badges NÃO DEVEM apresentar aprovação, cobertura, compatibilidade, build, release ou disponibilidade não verificada; DEVEM ser atualizados ou removidos quando obsoletos.

Autoria, repositório e licença DEVEM vir de artefatos reais do repositório. Dado ausente NÃO DEVE ser inventado e DEVE permanecer como pendência.

## 33. FTs e continuidade

FT normativa e FT técnica DEVEM permanecer segregadas em `.ia.rules/continue.ia`.

FT normativa DEVE cobrir RCF, README, validação documental, remoção de artefato transitório aplicável, commit e push.

FT técnica DEVE permanecer pendente até autorização humana explícita e DEVE cobrir avaliação tecnológica, arquitetura, código, bibliotecas, dependências, testes, builds, integrações, automações, CI/CD e publicação quando aplicáveis.

A conclusão normativa NÃO autoriza implementação de código.

## 34. Arquitetura compartilhada e perfis operacionais

O núcleo de domínio, descoberta, extração, normalização, segmentação, indexação, busca, persistência, deduplicação, tradução e geração de resultados NÃO DEVE depender de DOM, framework visual, protocolo HTTP ou pressuposto de servidor.

CLI, GUI local e eventual adaptador web público DEVEM compor o mesmo núcleo por interfaces estáveis e NÃO DEVEM duplicar regra de negócio. Modo Pesquisa e Modo Conversa DEVEM compor recuperação, evidência e persistência comuns por contratos estáveis, mantendo orquestração e apresentação específicas.

O perfil `local` DEVE permanecer primário, completo, funcional sem navegador, servidor público, serviço remoto ou rede obrigatória.

A GUI local DEVE ser leve, profissional, direta, responsiva, acessível, offline e funcionalmente completa para as capacidades que expuser.

O perfil `public-future` DEVE existir apenas como contrato de extensão; autenticação pública, multiusuário massivo, quotas, rate limiting, escalabilidade horizontal, filas distribuídas, isolamento entre tenants, balanceamento e infraestrutura de produção NÃO DEVEM ser implementados sem autorização específica.

Perfis operacionais DEVEM especializar configuração, limites e adaptadores centralizados, sem condicionais dispersas ou reescrita do núcleo.

Cada serviço relevante DEVE declarar capacidades, requisitos, limites, cancelabilidade, concorrência, consumo esperado, plataformas, runtimes e compatibilidade de perfil.

CPU, memória, workers, filas, tamanho de consulta, duração, cache, rede e demais recursos DEVEM possuir limites centrais, tipados, validados, documentados e com defaults seguros.

CLI, GUI, scripts, paths, processos, filesystem, encoding, sinais, shells e integração entre runtimes DEVEM operar de forma consistente nas plataformas suportadas; diferença inevitável DEVE usar adaptador explícito.

Componente auxiliar em outro runtime DEVE declarar entrada, saída, erro, serialização, versão, timeout, cancelamento, código de retorno, descoberta e diagnóstico.

Ausência ou incompatibilidade de runtime auxiliar NÃO DEVE inutilizar capacidade independente; fallback, desabilitação localizada ou falha acionável DEVE preservar o restante do sistema.

## 35. GUI local, dependências visuais e offline

HTML DEVE prover estrutura e conteúdo essencial; CSS ou Sass DEVE prover apresentação; TypeScript somente DEVE aprimorar estado ou interação não atendidos adequadamente por recursos nativos.

Quando houver estilização processada, Sass DEVE ser compilado e fonte `.scss` desnecessária NÃO DEVE integrar o artefato final.

WebAwesome, Font Awesome, templates, frameworks leves e componentes consolidados PODEM ser adotados somente quando reduzirem custo líquido sem degradar desempenho, portabilidade, acessibilidade, segurança ou controle.

Biblioteca visual NÃO DEVE ser incorporada integralmente quando apenas subconjunto for utilizado; ícones, estilos, fontes, componentes e scripts DEVEM ser selecionados sob demanda.

CDN PODE ser usada quando o ganho de cache, latência, peso, disponibilidade e manutenção superar os riscos de privacidade, integridade e dependência externa.

Recurso remoto crítico DEVE possuir fallback local, vendorização, cache ou degradação funcional que preserve a operação offline.

GUI DEVE minimizar JavaScript, CSS, requests, parsing, hidratação, memória e processamento por carregamento condicional, lazy loading, tree shaking ou code splitting somente quando houver ganho verificável.

Validação da GUI DEVE cobrir núcleo isolado, CLI, GUI, offline, teclado, foco, contraste, toque, overflow, responsividade, carregamento seletivo, limites de recursos e ausência de duplicação de negócio.

## 36. Estratégias de segmentação e RAG proporcional

RAG DEVE ser tratado como conjunto modular de técnicas opcionais e NÃO DEVE impor embeddings, banco vetorial, LLM, serviço remoto ou modelo específico quando mecanismo determinístico produzir resultado equivalente ou superior.

Antes de adotar técnica de RAG, a FT técnica DEVE inspecionar o repositório e medir baseline de ingestão, extração, normalização, segmentação, enriquecimento, representação, indexação, recuperação, expansão, busca híbrida, filtros, reranking, composição, validação, cache, incremento e observabilidade.
Cada estratégia DEVE declarar identidade, versão, configuração, aplicabilidade, entradas, saídas, metadados, limites, custo, métricas, validação, serialização e diagnóstico.

O pipeline DEVE suportar seleção explícita ou determinística por coleção, documento, gênero, idioma, campo, consulta, citação, tarefa ou perfil, sempre com decisão rastreável e override manual.

Parâmetros de tamanho mínimo, ideal e máximo, unidade, overlap, limite estrutural, tolerância e expansão contextual DEVEM ser configuráveis por estratégia ou perfil.

Estratégias clássicas DEVEM permanecer de primeira classe quando aplicáveis: tamanho fixo, sentença, parágrafo, página, bloco, seção, título, capítulo, artigo, inciso, nota, delimitador, tipografia, markup, metadado, regex, janela deslizante e divisão recursiva.

Regex NÃO DEVE ser tratada como mecanismo inferior; quando adequada, DEVE permanecer configurável, testável, composível e preferível a método probabilístico mais caro ou menos determinístico.

Estratégias linguísticas PODEM usar sentença, oração, parágrafo semântico, tópico, entidade, mudança discursiva e estrutura gramatical, respeitando idioma, abreviação, citação, nota e referência.

Estratégias semânticas PODEM usar similaridade, mudança de tópico, embedding, agrupamento e coerência discursiva quando seus limites forem rastreáveis e reproduzíveis.

LLM PODE delimitar estrutura, tópico, unidade argumentativa ou citação somente quando demonstrar ganho líquido; NÃO DEVE alterar, resumir ou reescrever silenciosamente a fonte.

Limite produzido por LLM DEVE apontar ao texto original, ser validável, armazenável, reutilizável e versionado; custo, latência, privacidade, disponibilidade e variação DEVEM integrar a decisão.

Segmentação bibliográfica DEVE preservar título, autoria, resumo, capítulo, seção, página, nota, citação, referência, bibliografia, edição e volume quando presentes.

Citação NÃO DEVE ser dividida de modo a perder atribuição, fonte, início, fim, página, nota, referência, qualificador ou contexto necessário.

Citação extensa PODE formar chunk próprio ligado aos vizinhos; citação curta DEVE preservar o parágrafo e a referência associada.

Overlap PODE usar caracteres, palavras, tokens, sentenças, parágrafos ou unidades estruturais; DEVE preservar continuidade sem duplicação massiva ou crescimento desproporcional.

Chunk DEVE poder relacionar predecessor, sucessor, pai, filho, vizinho, seção, documento, citação e referência por tipos explícitos, sem depender apenas de proximidade vetorial.

Representação hierárquica PODE seguir coleção, documento, edição, capítulo, seção, parágrafo e sentença; recuperação PODE localizar unidade pequena e expandir seletivamente ao pai ou vizinho.

O mesmo documento PODE manter segmentações paralelas quando tarefas exigirem granularidades incompatíveis; cada representação DEVE registrar estratégia, versão e configuração.

Resultados de segmentações paralelas DEVEM ser deduplicados ou aglutinados conscientemente, e o custo adicional DEVE ser comparado ao ganho.

Chunks virtuais PODEM ser compostos durante a consulta a partir de unidades, hierarquia e vizinhança, sem materializar combinações irrestritas.

Chunking adaptativo PODE variar por densidade, idioma, estrutura, consulta, relevância ou confiança somente por critérios verificáveis e reproduzíveis.

Cada chunk DEVE preservar documento, edição ou versão, idioma efetivo, estratégia, hierarquia, offsets e, quando disponíveis, página, bloco, linha ou coordenada que permitam conferir o trecho.

Texto canônico citado DEVE permanecer imutável e separado de limpeza, normalização, tokens, embeddings, resumos e outros derivados.

Mudança de extrator, regex, tokenizer, modelo, estratégia ou configuração que altere chunks DEVE invalidar deterministicamente somente índices afetados.

Duplicata, quase duplicata, tradução, edição e citação repetida DEVEM permanecer classes distintas; igualdade textual NÃO DEVE apagar ocorrências bibliograficamente independentes.

## 37. Busca multilíngue, roteamento e aglutinação

Representação lexical, semântica e híbrida DEVE preservar idioma-fonte, variante, terminologia e diferença conceitual.

Consulta cruzada entre idiomas PODE usar tradução, embedding multilíngue, léxico, ontologia, sinônimo ou combinação, mas cada expansão DEVE registrar origem, relação e confiança.

Tradução aproximada NÃO DEVE ser tratada como identidade conceitual plena.

Tokenização, segmentação, stemming, lematização e sinônimos DEVEM considerar o idioma efetivo do trecho; documento misto NÃO DEVE ser forçado a idioma único.

Traduções e originais DEVEM permanecer relacionados sem fusão como documento único.

Índices lexicais, invertidos, semânticos, por campo, entidade, referência e relação PODEM coexistir como capacidades independentes.

Busca híbrida DEVE preservar correspondência exata relevante, permitir pesos configuráveis e comparar estratégias antes da fusão.

Roteamento PODE selecionar chunk, índice, filtro, expansão ou reranker por intenção e contexto, mas DEVE possuir fallback geral e NÃO DEVE excluir silenciosamente estratégia relevante sob baixa confiança.

Recuperação DEVE iniciar pelo contexto mínimo suficiente e PODE expandir por vizinhança, hierarquia, relação, referência ou documento.

Reranking determinístico, estatístico, cross-encoder ou por LLM somente PODE tornar-se padrão quando elevar precisão ou cobertura de forma mensurável.

Diversificação DEVE evitar concentração em chunks redundantes sem ocultar ocorrências bibliograficamente significativas.

Resultado de citação direta DEVE ser conferível contra a fonte; tradução, resumo, reconstrução ou inferência NÃO DEVE ser rotulada como transcrição literal.

Aglutinação PODE agrupar por obra, autor, referência, trecho equivalente, tradução, citação comum, tópico, entidade ou relação, mas DEVE preservar ocorrência, fonte, idioma, edição, localização, divergência e critério de agrupamento.

Trechos distintos NÃO DEVEM ser combinados como uma única citação nem divergências entre versões ou traduções podem ser ocultadas.

Quando IA for usada, a composição DEVE selecionar evidência relevante, controlar duplicação, respeitar orçamento de tokens e manter acesso ao original.

Modelo NÃO DEVE completar citação, página, autor, obra ou referência por plausibilidade; evidência ausente, insuficiente ou conflitante DEVE produzir abstenção explícita.
Prompt, tokenizer, embedding, reranker e LLM DEVEM ser substituíveis por contrato proporcional.

LLM PODE auxiliar expansão, desambiguação, classificação, reranking, síntese ou conexão semântica somente quando houver ganho demonstrável; mecanismo determinístico ou especializado mais adequado DEVE prevalecer e a pesquisa independente NÃO DEVE ser inutilizada por ausência de LLM.

## 38. Equivalência numérica bidirecional
Consulta por algarismo DEVE localizar número por extenso semanticamente equivalente e consulta por extenso DEVE localizar algarismo equivalente, sem duplicação manual.

Número por extenso DEVE ser interpretado conforme idioma e variante do trecho ou consulta.

Algarismo e expressão por extenso DEVEM convergir para valor canônico derivado, preservando texto original, offsets, idioma, evidência e forma de destaque.

Normalização numérica DEVE considerar, quando linguisticamente aplicável, cardinais, sinais, separadores de milhar e decimal, conectivos, hifenização, flexões e variantes ortográficas legítimas.

ISBN, DOI, ano, edição, volume, capítulo, página, código e identificador NÃO DEVEM ser expandidos indiscriminadamente; campo, formato, idioma e contexto DEVEM controlar a decisão.

Correspondência literal exata PODE receber peso superior a equivalência numérica quando isso preservar precisão.

Expansão numérica DEVE integrar indexação e consulta por mecanismo controlado, cacheável e sem crescimento combinatório.

Valor desconhecido, ambíguo, inválido ou em idioma não suportado NÃO DEVE interromper a busca; o termo original DEVE seguir pelos mecanismos restantes.

Validação DEVE cobrir ambos os sentidos, idiomas suportados, números simples e compostos, sinais, decimais, separadores locais, grafias válidas, ambiguidades e contextos bibliográficos que não admitem expansão.

## 39. Avaliação, métricas e adoção reversível

Baseline DEVE ser medido antes de alterar segmentação, índice, expansão, recuperação, reranking ou aglutinação.

Avaliação DEVE medir, conforme aplicabilidade, precisão, recall, MRR, nDCG, cobertura de citações, fidelidade literal, validade de localizações, completude de referências, associação entre afirmação e prova, completude contextual, acerto multilíngue, qualidade da aglutinação, contradições detectadas, abstenções corretas, falsos positivos, falsos negativos, latência, tokens, memória, armazenamento, tempo de indexação e custo operacional.

Chunking DEVE ser comparado por preservação semântica, ruptura de citação, redundância de overlap, distribuição de tamanho, localização, quantidade recuperada e contexto necessário.

Casos DEVEM incluir documentos curtos, longos, estruturados, irregulares, monolíngues, multilíngues, OCR imperfeito, notas, referências, edições, traduções e consultas ambíguas.

Cada estratégia DEVE ser medida isoladamente e nas combinações propostas.

Avaliação humana PODE complementar métrica automática mediante amostra verificável e critérios explícitos.

Técnica somente DEVE tornar-se padrão quando benefício recorrente superar processamento, armazenamento, memória, latência, manutenção, privacidade e risco, sem regressão relevante.

Adoção DEVE ser incremental, observável, versionada, comparável e reversível.

Catálogo de estratégias DEVE registrar aprovadas, rejeitadas e experimentais, parâmetros, custos, idiomas, formatos, limitações, fallbacks, métricas, versionamento e reindexação.


## 50. Preservação da pesquisa vigente

O Modo Pesquisa DEVE preservar integralmente §§5-39 e suas especializações posteriores como pesquisa documental avançada, híbrida e não conversacional.

O usuário DEVE selecionar explicitamente o Modo Pesquisa ou o Modo Conversa. A seleção DEVE controlar comportamento, apresentação, profundidade, encadeamento, persistência e critérios de resposta; infraestrutura compartilhada NÃO autoriza confundir sua semântica.

No Modo Pesquisa, expansão, recuperação, filtros, ranking, aglutinação, referências, Markdown e rastreabilidade DEVEM permanecer operacionais sem conversa e sem LLM obrigatória.

LLM e análogo SÃO meios opcionais de otimização quando ganho líquido de qualidade ou desempenho for demonstrado. Eles NÃO DEVEM substituir mecanismo determinístico ou especializado mais adequado, reduzir cobertura, precisão, auditabilidade ou força normativa, nem tornar a pesquisa indisponível quando alternativa aplicável existir.

Resultado do Modo Pesquisa DEVE continuar distinguindo ocorrência recuperada, texto original, tradução, referência, confiança e derivado; síntese auxiliar por IA NÃO DEVE converter a experiência em conversa nem ocultar os resultados verificáveis.

