- [ ] **[1A] Orquestrar integralmente:** este item constitui o comando central das solicitações correlatas. Assim como múltiplas frentes integram uma única guerra, TODOs deste arquivo, issues, requisitos, FTs, etapas, tarefas, anexos e normas materialmente relacionados DEVEM ser lidos, analisados, correlacionados e planejados como partes de um único objetivo, ainda que permaneçam separados por rastreabilidade, escopo, fase ou execução. Sua função é coordenar, consolidar, ordenar e preparar todas as frentes, NÃO executá-las indiscriminadamente nesta atuação. O planejamento DEVE prevenir retrabalho, incompatibilidades e futuras reedições ou revisões decorrentes de análise fragmentada ou incompleta.
  - [ ] **Preservar as fontes:** obter integralmente o texto, os comentários relevantes e os anexos aplicáveis de cada issue ou fonte externa; armazená-los temporariamente em estrutura local versionada, rastreável e devidamente aninhada; e lê-los integralmente antes de qualquer normatização ou implementação. Esses registros DEVEM permanecer até a incorporação normativa integral de seu conteúdo e ser removidos exclusivamente no marco de encerramento definido neste item.

  - [ ] **Analisar o conjunto:** ler os demais TODOs, issues, normas, FTs e trabalhos relacionados; identificar objetivos comuns, sobreposições, dependências, conflitos, precedências, lacunas, duplicações e impactos cruzados; e consolidar uma interpretação única, coerente e rastreável. A IA DEVE planejar a “guerra”, não tratar cada “frente” isoladamente.

  - [ ] **Preservar integralmente o conteúdo:** TODOs, issues e demais fontes PODEM ser reorganizados, fundidos, consolidados, desmembrados ou eliminados como unidades autônomas quando deixarem de possuir função própria. Contudo, nenhuma solicitação, regra, restrição, proibição, exceção, nuance, motivação, anexo, detalhe, dependência, precedência ou critério PODE ser perdido, enfraquecido, ignorado ou simplificado. A consolidação DEVE aumentar coerência, convergência e executabilidade, jamais reduzir substância ou rastreabilidade.

  - [ ] **Consolidação documental:** a IA PODE criar artefato temporário único de consolidação quando isso melhorar compreensão, coordenação, rastreabilidade ou eliminação de redundâncias. Esse artefato NÃO é obrigatório nem substitui as fontes antes da preservação integral de seu conteúdo. Cada requisito consolidado DEVE permanecer vinculável à respectiva origem.

  - [ ] **Planejamento global por FTs:** criar uma ou mais FTs vinculadas diretamente às issues ou demais fontes rastreáveis — JAMAIS a este item de `TODO.ia.md` —, planejadas de forma integrada e segregadas apenas quando houver unidade material, dependência, responsabilidade, risco, entregável ou fase distinta. DEVEM ser evitadas, tanto quanto técnica e operacionalmente possível, FTs, etapas ou tarefas duplicadas, sobrepostas, vazias, prematuras, artificiais, órfãs ou sem função no fluxo global.

  - [ ] **Fases obrigatórias e sequenciais:** estruturar as FTs aplicáveis nas fases abaixo, preservando dependências e impedindo execução antecipada:
    1. **Normatização:** incorporar integralmente ao RCF canônico todas as regras, contratos, exceções, relações e critérios consolidados.

    2. **Implementação da publicação pública e de sua cadeia operacional:** implementar integralmente, não necessariamente nesta ordem:
       - **A.** publicação do site do produto no GitHub Pages;
       - **B.** adaptação e correção do script `baixar.py`, incluindo RCF específico em subdiretório adequado da raiz do repositório, com nome inequívoco e referência normativa no RCF global;
       - **C.** script temporário, idempotente e verificável para migrar e corrigir as localizações das publicações, assets e metadados existentes;
       - **D.** script automatizado e workflow associado para gerar e manter o indexador global, incluindo criação, correção ou atualização de capas e demais assets ausentes, inválidos ou desatualizados.

    3. **Conformidade integral do repositório:** implementar, adaptar ou corrigir os demais códigos, scripts, automações, workflows, testes, documentação e artefatos necessários ao cumprimento integral do RCF, excluindo apenas o que já tiver sido concluído e validado na fase 2.

    As fases DEVEM ser planejadas globalmente antes de qualquer execução. A fase 2 NÃO DEVE ser interpretada como autorização para alterar componentes externos à cadeia de publicação pública, salvo dependência estritamente necessária e previamente registrada. A fase 3 NÃO DEVE duplicar trabalho concluído na fase 2.

  - [ ] **Motivação e retomada:** decisões cuja razão não seja evidente, convergências entre solicitações, adiamentos, dependências, exclusões aparentes, conflitos resolvidos ou divisões de escopo DEVEM possuir motivação clara e suficiente. Quando o registro na própria FT for inadequado ou excessivo, a motivação DEVE ser preservada em arquivo temporário rastreável, vinculado às FTs, etapas ou tarefas correspondentes, mantido somente enquanto necessário à retomada e removido integralmente após a conclusão da unidade pertinente.

  - [ ] **Commit das FTs:** após criar, consolidar, revisar e vincular todas as FTs necessárias, realizar commit exclusivo contendo somente as FTs, seus vínculos rastreáveis e, quando indispensáveis à compreensão delas, os artefatos temporários de planejamento. Esse commit DEVE anteceder qualquer alteração normativa ou técnica.

  - [ ] **Executar somente a fase 1:** iniciar imediatamente e concluir integralmente apenas as FTs, etapas e tarefas da fase **1 — Normatização**, incorporando ao RCF canônico a issue e todas as frentes convergentes aplicáveis. Nesta atuação, É PROIBIDO:
    - alterar diretamente `src/`;
    - executar migração de arquivos;
    - modificar a cadeia de build ou publicação;
    - implementar a norma operacional;
    - criar, adaptar ou alterar códigos, scripts ou workflows;
    - iniciar qualquer atividade pertencente às fases 2 ou 3.

  - [ ] **Validar a normatização:** confirmar, mediante revisão rastreável, que:
    - todo requisito, detalhe, restrição, exceção, motivação, dependência, precedência, relação entre frentes e critério aplicável foi incorporado;
    - nenhuma fonte material permaneceu sem tratamento;
    - não existem duplicações normativas desnecessárias;
    - referências internas e vínculos documentais estão corretos;
    - o RCF resultante é determinístico, suficiente e verificável;
    - as fases 2 e 3 permanecem coerentes, não sobrepostas e prontas para execução futura.

  - [ ] **Encerrar a fase:** após validar a normatização:
    1. remover os registros temporários das issues, anexos e arquivos auxiliares cuja função tenha se esgotado;
    2. preservar apenas os artefatos ainda necessários à rastreabilidade ou retomada das fases remanescentes;
    3. realizar commit exclusivo contendo a normatização no RCF, as referências atualizadas e as remoções pertinentes;
    4. marcar este TODO como concluído;
    5. interromper obrigatoriamente a execução, sem iniciar as fases 2 ou 3.

  - [ ] **Comunicação final:** informar ao desenvolvedor que as issues e frentes relacionadas foram integralmente correlacionadas, convergidas e normatizadas no RCF; identificar os commits realizados; e listar nominalmente as fases remanescentes prontas para execução:
    - **Implementação da publicação pública e de sua cadeia operacional**;
    - **Conformidade integral do repositório com o RCF**.

- [ ] **Ampliar a busca semântica, lexical e por sinônimos em coleções bibliográficas, inclusive multilíngues, para reconhecer equivalência bidirecional entre representações numéricas:** uma consulta expressa em algarismos DEVE localizar ocorrências semanticamente equivalentes escritas por extenso, e vice-versa; por exemplo, `144` DEVE corresponder a `cento e quarenta e quatro`.
  - [ ] **Bidirecionalidade:** a equivalência DEVE funcionar independentemente da representação usada na consulta ou no conteúdo indexado, sem exigir duplicação manual dos termos.
  - [ ] **Multilinguismo:** números por extenso DEVEM ser interpretados conforme o idioma e a variante linguística do documento, campo ou consulta, preservando diferenças normativas entre idiomas e evitando correspondências produzidas por tradução ou análise linguística incorreta.
  - [ ] **Normalização canônica:** algarismos e expressões numéricas por extenso DEVEM convergir internamente para uma representação numérica canônica, mantendo o texto original disponível para exibição, relevância, auditoria e destaque do resultado.
  - [ ] **Escopo de equivalência:** abranger, tanto quanto técnica e linguisticamente aplicável, numerais cardinais, sinais, separadores de milhar e decimais, grafias com ou sem conectivos, hifenização, flexões e demais variações ortográficas legítimas que representem o mesmo valor.
  - [ ] **Contexto bibliográfico:** a expansão numérica DEVE integrar os mecanismos existentes de busca semântica, lexical, por sinônimos, indexação e ranqueamento, sem substituir nem degradar correspondências literais, títulos, autores, edições, capítulos, páginas, anos, identificadores ou referências bibliográficas.
  - [ ] **Precisão contextual:** sequências numéricas que possam representar código, ISBN, DOI, edição, volume, capítulo, página, ano, identificador ou fragmento textual NÃO DEVEM ser convertidas indiscriminadamente quando a expansão puder gerar falsos positivos; o mecanismo DEVE considerar campo, idioma, formato e contexto indexado.
  - [ ] **Ranqueamento:** correspondências numéricas equivalentes DEVEM ser tratadas como semanticamente compatíveis, mas a ocorrência literal exata PODE receber prioridade superior quando isso preservar a precisão e o comportamento vigente do ranqueamento.
  - [ ] **Desempenho:** a equivalência DEVE ser implementada preferencialmente por normalização e expansão controlada durante indexação e consulta, com cache ou estrutura equivalente quando útil, evitando crescimento combinatório, geração irrestrita de variantes ou degradação desproporcional de memória, latência e tamanho do índice.
  - [ ] **Resiliência:** valores não reconhecidos, expressões ambíguas, idiomas não suportados ou construções inválidas NÃO DEVEM interromper a busca; nesses casos, o termo original DEVE continuar sendo processado pelos mecanismos já existentes.
  - [ ] **Validação:** testar equivalência nos dois sentidos, em todos os idiomas suportados, incluindo números simples e compostos, variações ortográficas válidas, separadores locais, contextos bibliográficos sensíveis, ambiguidades e casos que NÃO DEVEM ser expandidos.
  - [ ] **Critério de aceite:** considerar concluído somente quando consultas por algarismos e por extenso recuperarem reciprocamente conteúdos numericamente equivalentes, com suporte multilíngue, normalização determinística, integração aos mecanismos de busca existentes, ranqueamento coerente, controle de falsos positivos e ausência de regressão relevante de precisão ou desempenho.

- [ ] **Preservar a operação local por linha de comando e implementar GUI web leve, profissional e preparada arquiteturalmente para futura execução pública:** o projeto DEVE permanecer permanentemente funcional, completo e prioritário em modo local/CLI, acrescentando interface web sem substituir, degradar, duplicar ou acoplar a lógica nuclear à apresentação.
  - [ ] **Local/CLI como contrato primário:** todas as capacidades essenciais DEVEM continuar disponíveis localmente por linha de comando, sem navegador, servidor público, serviço remoto ou dependência obrigatória de rede. A GUI DEVE consumir os mesmos contratos, serviços e mecanismos do núcleo, atuando como adaptador de apresentação.
  - [ ] **GUI secundária, não secundarizada:** fornecer GUI web elegante, profissional, direta, limpa, intuitiva, simples sem ser simplista, responsiva, acessível e coerente, priorizando baixo custo de desenvolvimento, manutenção, carregamento e execução.
  - [ ] **Composição pragmática:** templates, frameworks leves e componentes consolidados, incluindo WebAwesome e Font Awesome, PODEM ser empregados seletivamente quando reduzirem custo líquido sem comprometer desempenho, portabilidade, coesão, acessibilidade, segurança ou controle do produto.
  - [ ] **Inclusão estritamente sob demanda:** estilos, componentes, scripts, fontes, ícones e dependências DEVEM ser incorporados somente quando efetivamente usados. Font Awesome ou equivalente DEVE incluir apenas os ícones necessários e respectivos estilos; importações globais, pacotes integrais ou recursos ociosos DEVEM ser evitados.
  - [ ] **CDN prudente:** CDN PODE ser utilizada quando tecnicamente conveniente e mais leve, mas NÃO DEVE tornar a operação local dependente de conectividade externa. Recursos remotos DEVEM possuir fallback local, vendorização, cache ou estratégia equivalente que preserve o funcionamento integral offline.
  - [ ] **Desempenho e tamanho:** a GUI DEVE minimizar JavaScript, CSS, requisições, dependências, parsing, hidratação, memória e processamento, utilizando carregamento condicional, lazy loading, tree shaking, code splitting ou técnica proporcional quando houver ganho líquido verificável.
  - [ ] **Dois horizontes operacionais:** a arquitetura DEVE considerar desde a concepção: **(a)** execução local, objetivo principal e ativo; e **(b)** futura execução em servidor web público, objetivo secundário e potencial, sem implementar prematuramente infraestrutura de produção não solicitada.
  - [ ] **Local otimizado para capacidade:** a execução local PODE utilizar limites mais amplos de CPU, memória, duração, paralelismo, profundidade analítica e abrangência de busca para maximizar qualidade e desempenho, considerando normalmente um ou poucos usuários.
  - [ ] **Controle local obrigatório:** maior liberdade local NÃO autoriza consumo irrestrito. Limites de CPU, memória, concorrência, filas, tamanho de consulta, duração, cache, workers e demais recursos DEVEM ser centralmente configuráveis, possuir padrões seguros e impedir travamentos, exaustão do sistema ou inutilização do computador.
  - [ ] **Servidor futuro:** preocupações específicas de produção — autenticação pública, multiusuário massivo, quotas, rate limiting, escalabilidade horizontal, filas distribuídas, isolamento entre tenants, balanceamento, observabilidade operacional, endurecimento de infraestrutura e controle agressivo de timeouts — NÃO DEVEM ser implementadas agora sem solicitação explícita.
  - [ ] **Preparação sem antecipação:** embora especializações de servidor permaneçam fora do escopo atual, contratos, pontos de controle, configurações, manifestos, hooks, gatilhos, conectores, adaptadores, limites, desvios de fluxo e interfaces de integração DEVEM ser normatizados e estruturados desde já para permitir implementação futura aditiva, coesa e de baixo impacto.
  - [ ] **Arquitetura híbrida configurável:** diferenças entre operação local e futura operação em servidor DEVEM ser representadas por configuração centralizada, perfis operacionais, injeção de dependências, adaptadores ou contratos equivalentes, evitando condicionais dispersas e reescrita estrutural futura.
  - [ ] **Fonte única de configuração:** runtime, recursos, caminhos, rede, persistência, concorrência, cache, segurança, capacidades da GUI e limites operacionais DEVEM derivar de configuração central, tipada, validada e documentada, com padrões locais seguros e possibilidade de especialização futura por ambiente.
  - [ ] **Separação de responsabilidades:** núcleo de busca, indexação, normalização, persistência e domínio NÃO DEVE depender de DOM, framework visual, protocolo HTTP ou pressupostos de servidor. CLI, GUI local e eventual adaptador web público DEVEM compor o mesmo núcleo por interfaces estáveis.
  - [ ] **Integração futura aditiva:** a futura disponibilização pública DEVE poder acrescentar controles de carga, autenticação, autorização, isolamento, quotas, filas, timeouts, cancelamento e observabilidade sem alterar contratos independentes nem degradar o fluxo local.
  - [ ] **Manifestações de capacidade:** cada serviço ou operação relevante DEVE declarar capacidades, requisitos, limites configuráveis, cancelabilidade, concorrência, consumo esperado e compatibilidade operacional, permitindo que perfis locais e futuros perfis de servidor decidam como executá-lo.
  - [ ] **Cross-platform obrigatório:** CLI, GUI local, scripts, caminhos, processos, filesystem, encoding, sinais, shells e integração entre runtimes DEVEM funcionar de forma consistente nos sistemas operacionais suportados, evitando dependências injustificadas de plataforma e fornecendo adaptadores quando diferenças forem inevitáveis.
  - [ ] **Node.js/TypeScript como eixo principal:** TypeScript sobre Node.js DEVE permanecer o ponto principal de integração e orquestração quando adequado, sem impor monocultura tecnológica que reduza eficiência, compatibilidade ou qualidade.
  - [ ] **Poliglotismo especializado:** Python, Ruby, Rust ou outras linguagens PODEM ser utilizadas em segmentos nos quais ofereçam ganho técnico demonstrável por desempenho, integração nativa, maturidade de bibliotecas, segurança ou adequação ao framework, incluindo Jekyll e ferramentas especializadas.
  - [ ] **Integração entre runtimes:** componentes multilíngues DEVEM possuir contratos explícitos de entrada, saída, erros, serialização, versionamento, cancelamento, timeout e códigos de retorno. Descoberta de runtime, validação de versão, instalação orientada, acionamento e diagnóstico DEVEM ser centralizados e reproduzíveis.
  - [ ] **Fallback e degradação controlada:** ausência ou incompatibilidade de runtime auxiliar NÃO DEVE comprometer funções independentes. Sempre que possível, o sistema DEVE oferecer implementação alternativa, desabilitação localizada ou diagnóstico acionável, sem sucesso falso ou falha global desnecessária.
  - [ ] **Ausência de duplicação:** CLI e GUI NÃO DEVEM manter implementações paralelas da mesma regra de negócio. Lógica reutilizável DEVE residir no núcleo compartilhado; cada interface DEVE limitar-se à coleta, validação, apresentação e tradução de interações.
  - [ ] **Validação:** testar separadamente núcleo, CLI, GUI local, execução offline, carregamento seletivo, limites de recursos, configurações, contratos entre runtimes e sistemas operacionais; verificar também que pontos de extensão futuros existem sem exigir infraestrutura real de servidor.
  - [ ] **Critério de aceite:** considerar concluído somente quando o projeto permanecer integralmente funcional por CLI e localmente; disponibilizar GUI web leve, profissional e offline; compartilhar núcleo sem duplicação; incluir apenas recursos efetivamente usados; controlar centralmente consumo local; operar cross-platform; integrar runtimes auxiliares de forma explícita e resiliente; e possuir contratos, configurações, hooks e adaptadores suficientes para futura evolução pública aditiva, sem implementação prematura de infraestrutura de produção.

- [ ] **Avaliar e, mediante ganho líquido comprovado, incorporar princípios, técnicas e componentes de RAG ao projeto de pesquisa, indexação bibliográfica e recuperação avançada de citações, com suporte multilíngue e saída aglutinada:** inspecionar o estado real do repositório antes de definir arquitetura, tecnologias ou dependências, identificando quais estratégias podem ampliar velocidade, precisão, cobertura, capacidade interpretativa, contextualização, rastreabilidade e eficiência de tokens sem degradar resultados existentes.
  - [ ] **Avaliação anterior à adoção:** nenhuma técnica de RAG DEVE ser implementada por tendência, analogia superficial ou benefício presumido. Cada componente DEVE ser comparado às capacidades atuais e adotado somente quando apresentar ganho líquido mensurável em recuperação, interpretação, custo, latência, cobertura, precisão, manutenção ou escalabilidade.
  - [ ] **Escopo mínimo da análise:** avaliar ingestão documental, extração e normalização textual, segmentação, enriquecimento, representação, indexação, recuperação lexical e semântica, expansão de consultas, busca híbrida, filtros, reranking, composição contextual, geração ou aglutinação de resultados, validação de citações, cache, atualização incremental e observabilidade.
  - [ ] **RAG modular e não monolítico:** técnicas PODEM ser aplicadas total ou parcialmente. O projeto NÃO DEVE depender obrigatoriamente de embeddings, banco vetorial, LLM, serviço remoto ou modelo específico quando regex, índices lexicais, estruturas determinísticas ou bibliotecas locais produzirem resultado equivalente ou superior com menor custo e maior previsibilidade.
  - [ ] **Arquitetura inspecionada, não presumida:** linguagem, runtime, banco, mecanismo de índice, modelo, formato documental, infraestrutura e fluxo de processamento DEVEM ser determinados a partir do repositório. Este item NÃO autoriza substituição tecnológica ampla sem necessidade demonstrável.

  - [ ] **Pipeline de chunks configurável:** implementar uma camada explícita de segmentação capaz de registrar, selecionar, combinar e executar múltiplas estratégias de chunks conforme tipo de documento, estrutura, idioma, tarefa, consulta, campo bibliográfico e objetivo de recuperação.
    - [ ] **Estratégias independentes:** cada estratégia DEVE possuir identidade estável, configuração própria, condições de aplicabilidade, entradas, saídas, metadados, limitações e métricas, permitindo uso isolado, combinado ou experimental.
    - [ ] **Granularidade configurável:** tamanho mínimo, ideal e máximo; unidade de medição; sobreposição; limites estruturais; tolerância; expansão contextual e demais parâmetros DEVEM ser configuráveis por estratégia ou perfil, sem valores rígidos dispersos no código.
    - [ ] **Perfis por situação:** o projeto DEVE permitir estratégias e parâmetros diferentes conforme coleção, documento, gênero textual, idioma, tipo de pesquisa, busca de citação, recuperação temática, comparação de fontes ou outra situação efetivamente identificada pelo repositório.
    - [ ] **Seleção explícita ou automática:** a estratégia PODE ser escolhida por configuração, regra determinística, perfil operacional, características detectadas ou roteador especializado, desde que a decisão permaneça rastreável, reproduzível e passível de substituição manual.
    - [ ] **Fallback seguro:** falha, indisponibilidade ou baixa confiança de uma estratégia NÃO DEVE interromper desnecessariamente a indexação. O pipeline DEVE poder aplicar estratégia alternativa compatível e registrar a substituição.

  - [ ] **Estratégias clássicas e determinísticas:** preservar e incorporar, conforme aplicabilidade real, métodos previsíveis e eficientes, incluindo:
    - divisão por tamanho fixo em caracteres, palavras ou tokens;
    - sentenças, parágrafos, páginas, blocos e seções;
    - títulos, subtítulos, capítulos, artigos, incisos, notas ou demais estruturas documentais detectáveis;
    - delimitadores, padrões tipográficos, markup, metadados e regras baseadas em regex;
    - janelas deslizantes;
    - divisão recursiva por hierarquia de separadores;
    - regras específicas para formatos estruturados ou semiestruturados.
  - [ ] **Regex como estratégia de primeira classe:** segmentações por expressões regulares NÃO DEVEM ser tratadas como mecanismo legado inferior. Quando adequadas, DEVEM permanecer configuráveis, testáveis, compostas, reutilizáveis e preferidas sobre métodos probabilísticos mais caros ou menos determinísticos.
  - [ ] **Estratégias linguísticas:** avaliar segmentação por sentença, oração, parágrafo semântico, tópico, entidade, mudança discursiva ou estrutura gramatical, respeitando idioma, variante linguística, abreviações, citações, notas, referências e particularidades editoriais.
  - [ ] **Estratégias semânticas:** avaliar divisão por similaridade, mudança de tópico, embeddings, agrupamento, coerência discursiva ou representações equivalentes, sem aceitar fragmentação semântica opaca ou não reproduzível como requisito inevitável.
  - [ ] **Chunking orientado por LLM:** métodos baseados em LLM PODEM analisar estrutura, tópicos, unidades argumentativas, citações ou transições quando produzirem ganho real sobre métodos determinísticos.
    - O modelo NÃO DEVE alterar, resumir ou reescrever silenciosamente o conteúdo-fonte durante a segmentação.
    - Limites produzidos por LLM DEVEM ser rastreáveis ao texto original.
    - Resultados DEVEM ser validáveis, armazenáveis, reutilizáveis e protegidos contra variação não controlada.
    - Custo, latência, privacidade, disponibilidade, reprodutibilidade e dependência externa DEVEM integrar a decisão de uso.
  - [ ] **Chunking estrutural e bibliográfico:** avaliar estratégias capazes de respeitar unidades relevantes como título, autoria, resumo, capítulo, seção, página, nota, citação direta, citação indireta, referência, bibliografia, edição, volume e demais estruturas efetivamente existentes, sem presumir que todos os documentos possuam o mesmo modelo.
  - [ ] **Chunking orientado a citações:** citações e respectivos contextos NÃO DEVEM ser divididos de modo que se percam autoria atribuída, fonte, início, término, página, nota, referência, qualificadores ou relação com o argumento circundante.
    - Citações extensas PODEM formar chunks próprios vinculados aos chunks antecedentes e subsequentes.
    - Citações curtas incorporadas ao parágrafo DEVEM preservar o contexto necessário à interpretação.
    - Referências bibliográficas associadas DEVEM permanecer vinculáveis sem serem necessariamente duplicadas integralmente em cada chunk.

  - [ ] **Sobreposição configurável:** permitir overlap em caracteres, palavras, tokens, sentenças, parágrafos ou unidades estruturais, conforme a estratégia.
    - A sobreposição DEVE preservar continuidade contextual e impedir perda de conceitos nas fronteiras.
    - Sobreposição excessiva, duplicação massiva ou crescimento desproporcional do índice DEVEM ser evitados.
    - O valor adequado DEVE poder variar por idioma, estrutura, tamanho, gênero documental e tarefa.
  - [ ] **Encadeamento de chunks:** chunks DEVEM poder manter relações explícitas com predecessores, sucessores, pais, filhos, vizinhos, seções, documentos, citações e referências, quando essas relações contribuírem para recuperação ou interpretação.
    - O encadeamento NÃO DEVE depender apenas de proximidade vetorial.
    - Relações DEVEM possuir tipos inequívocos e origem rastreável.
    - A recuperação DEVE poder expandir seletivamente para chunks adjacentes ou relacionados sem carregar indiscriminadamente o documento inteiro.
  - [ ] **Chunks hierárquicos:** avaliar representação em múltiplos níveis, como coleção → obra → edição → capítulo → seção → parágrafo → sentença ou estrutura equivalente detectada no corpus.
    - A recuperação PODE localizar unidade pequena e expandir para o contexto pai necessário.
    - Níveis hierárquicos NÃO DEVEM duplicar conteúdo sem justificativa nem perder correspondência com a fonte.
  - [ ] **Múltiplas segmentações simultâneas:** o mesmo documento PODE manter representações paralelas produzidas por estratégias distintas quando tarefas diferentes exigirem granularidades incompatíveis.
    - Cada representação DEVE identificar estratégia, versão e configuração.
    - Resultados provenientes de representações paralelas DEVEM ser deduplicados ou aglutinados de modo consciente.
    - O custo adicional de armazenamento e indexação DEVE ser comparado ao ganho obtido.
  - [ ] **Chunks virtuais sob consulta:** avaliar composição dinâmica de contexto a partir de unidades menores, relações estruturais e vizinhança, evitando materializar previamente todas as combinações possíveis.
  - [ ] **Chunking adaptativo:** o pipeline PODE ajustar granularidade e contexto conforme densidade semântica, idioma, estrutura, consulta, relevância ou confiança, desde que os critérios sejam verificáveis e não produzam comportamento arbitrário ou impossível de reproduzir.

  - [ ] **Preservação integral da fonte:** chunks DEVEM manter referência exata ao documento, edição ou versão de origem e, quando tecnicamente possível, aos offsets, páginas, blocos, linhas ou coordenadas que permitam reconstruir e conferir o trecho.
  - [ ] **Imutabilidade do conteúdo citado:** normalização, limpeza, tokenização, embeddings ou enriquecimento NÃO DEVEM substituir o texto canônico utilizado para comprovação de citações. Representações derivadas DEVEM permanecer separadas do conteúdo-fonte.
  - [ ] **Metadados por chunk:** registrar somente dados úteis e proporcionais, incluindo, conforme disponibilidade real, documento, coleção, idioma, variante, posição, hierarquia, estratégia, versão, páginas, relações, autoria, edição, referência, entidades, tópicos e demais campos necessários à busca ou validação.
  - [ ] **Versionamento da segmentação:** mudança de estratégia, tokenizer, modelo, regex, configuração ou extração que altere chunks DEVE invalidar ou regenerar deterministicamente os índices afetados, sem misturar representações incompatíveis.
  - [ ] **Deduplicação consciente:** duplicatas exatas, quase duplicatas, traduções, edições e citações repetidas DEVEM ser distinguidas. O sistema NÃO DEVE eliminar automaticamente ocorrências bibliograficamente independentes apenas porque possuem texto igual ou semelhante.

  - [ ] **Representação multilíngue:** avaliar representações lexicais, semânticas e híbridas capazes de recuperar conteúdo entre idiomas sem apagar o idioma-fonte, variantes, diferenças conceituais ou terminologia especializada.
  - [ ] **Consulta cruzada entre idiomas:** uma consulta PODE recuperar equivalentes em outros idiomas por tradução, embeddings multilíngues, léxicos, ontologias, sinônimos ou métodos combinados, mas a origem de cada expansão DEVE ser rastreável.
  - [ ] **Preservação terminológica:** equivalência multilíngue NÃO DEVE tratar traduções aproximadas como identidade conceitual plena. Grau de confiança, ambiguidade, contexto e domínio DEVEM influenciar recuperação e ranqueamento.
  - [ ] **Idioma detectado ou declarado:** seleção de tokenização, segmentação, stemming, lematização, sinônimos e demais operações linguísticas DEVE considerar o idioma efetivo do trecho, sem depender exclusivamente do idioma global do documento.
  - [ ] **Conteúdo multilíngue interno:** documentos que alternem idiomas DEVEM poder ser segmentados e indexados sem forçar classificação única que prejudique trechos em idioma distinto.
  - [ ] **Traduções e originais:** quando identificáveis, traduções DEVEM permanecer relacionadas às respectivas fontes ou versões, sem serem fundidas como um único documento.

  - [ ] **Indexação múltipla e complementar:** avaliar índices lexicais, invertidos, semânticos, por campos, entidades, referências, relações e demais estruturas aplicáveis, permitindo que cada tipo de consulta utilize os mecanismos mais adequados.
  - [ ] **Busca híbrida:** combinar, quando houver ganho, correspondência literal, lexical, morfológica, por sinônimos, semântica, bibliográfica, estrutural e relacional.
    - Correspondências exatas relevantes NÃO DEVEM ser ocultadas por similaridade semântica.
    - Pesos e critérios DEVEM ser configuráveis e verificáveis.
    - Estratégias independentes DEVEM poder ser comparadas antes da fusão.
  - [ ] **Expansão de consulta:** avaliar sinônimos, variantes ortográficas, flexões, entidades, traduções, termos relacionados, equivalências numéricas e vocabulários especializados, mantendo registro entre termo original e expansão aplicada.
  - [ ] **Roteamento de busca:** consultas PODEM ser classificadas e encaminhadas para estratégias específicas de chunk, índice, filtro, expansão ou reranking, conforme intenção detectável e contexto disponível.
    - O roteamento DEVE possuir fallback geral.
    - Baixa confiança NÃO DEVE excluir silenciosamente estratégias potencialmente relevantes.
    - A classificação NÃO DEVE restringir o usuário a um único tipo de busca quando múltiplos forem pertinentes.
  - [ ] **Recuperação progressiva:** iniciar pela quantidade mínima de contexto suficiente e expandir por vizinhança, hierarquia, relações, referências ou documento completo quando a consulta exigir.
  - [ ] **Reranking:** avaliar métodos determinísticos, estatísticos, cross-encoder, LLM ou equivalentes apenas quando elevarem precisão ou cobertura de forma mensurável.
  - [ ] **Diversificação:** resultados DEVEM evitar concentração indevida em chunks redundantes da mesma passagem quando outras fontes relevantes puderem ampliar cobertura, sem ocultar múltiplas ocorrências bibliograficamente significativas.

  - [ ] **Pesquisa avançada de citações:** o pipeline DEVE preservar a distinção entre trecho citado, contexto, obra citante, possível obra citada, referência bibliográfica, tradução, edição e localização documental quando essas informações estiverem disponíveis.
  - [ ] **Validação da citação:** resultados apresentados como citação direta DEVEM permanecer conferíveis contra o texto-fonte; conteúdo reconstruído, traduzido, resumido ou inferido NÃO DEVE ser rotulado como transcrição literal.
  - [ ] **Contexto suficiente:** a recuperação DEVE poder incluir sentenças, parágrafos ou seções adjacentes necessários para impedir interpretação descontextualizada, sem inflar indiscriminadamente a saída.
  - [ ] **Aglutinação de resultados:** resultados multilíngues, duplicados, complementares ou provenientes de diferentes estratégias DEVEM poder ser agrupados por relação verificável, preservando cada ocorrência, fonte, idioma, edição, localização e nível de confiança.
  - [ ] **Ausência de fusão enganosa:** a saída aglutinada NÃO DEVE combinar trechos distintos como se constituíssem uma única citação, nem ocultar divergências entre traduções, versões ou fontes.
  - [ ] **Critérios de agrupamento:** aglutinação PODE considerar obra, autor, referência, trecho equivalente, tradução, citação comum, tópico, entidade ou relação bibliográfica, mas o critério utilizado DEVE permanecer identificável.
  - [ ] **Apresentação orientada à evidência:** sínteses, agrupamentos ou respostas geradas DEVEM manter ligações claras com os chunks e documentos que lhes oferecem suporte.

  - [ ] **Composição de contexto para IA:** quando modelos forem utilizados, o sistema DEVE selecionar chunks relevantes, eliminar duplicação inútil, preservar contexto indispensável e manter referências suficientes para validar a resposta.
  - [ ] **Orçamento de tokens:** composição contextual DEVE considerar limites do modelo, relevância, diversidade, hierarquia, sobreposição e custo acumulado, evitando truncamento arbitrário e inclusão de conteúdo apenas marginal.
  - [ ] **Compressão sem perda probatória:** resumos ou compressões PODEM auxiliar seleção, mas citações, evidências e informações necessárias à conferência DEVEM permanecer acessíveis em sua forma original.
  - [ ] **Recuperação antes de geração:** o modelo NÃO DEVE completar lacunas bibliográficas, citações ou referências por plausibilidade quando a evidência não tiver sido recuperada.
  - [ ] **Resposta abstencionista:** ausência, insuficiência ou conflito de evidências DEVE ser explicitado, sem fabricação de citações, páginas, autores, obras ou relações.
  - [ ] **Modelos substituíveis:** prompts, tokenizadores, embeddings, rerankers e LLMs DEVEM ser abstraídos por contratos suficientes para atualização ou substituição sem reescrever o núcleo do projeto, quando tecnicamente proporcional.

  - [ ] **Execução local e privacidade:** priorizar métodos locais, reproduzíveis e cross-platform. Conteúdo bibliográfico privado ou protegido NÃO DEVE ser enviado a serviços externos sem configuração e autorização explícitas.
  - [ ] **Processamento incremental:** alterações em documentos, configurações, modelos ou estratégias DEVEM reprocessar somente unidades afetadas quando isso for seguro, evitando reconstrução integral desnecessária.
  - [ ] **Cache rastreável:** caches de extração, chunks, embeddings, consultas, reranking ou respostas DEVEM incluir identidade da fonte, estratégia e versões necessárias à invalidação correta.
  - [ ] **Resiliência:** falhas em modelo, serviço, tokenizer, parser, estratégia ou idioma NÃO DEVEM inutilizar mecanismos independentes. O pipeline DEVE aplicar fallback, degradação localizada ou diagnóstico acionável conforme aplicabilidade.
  - [ ] **Desempenho proporcional:** múltiplas estratégias, embeddings, LLMs e representações paralelas somente DEVEM permanecer ativas quando seu ganho superar custos de processamento, armazenamento, memória, latência e manutenção.

  - [ ] **Framework de estratégias:** quando tecnicamente adequado, implementar contrato comum para estratégias de chunking contendo identificação, compatibilidade, configuração, segmentação, validação, serialização, versionamento, métricas e diagnóstico, sem forçar linguagens ou arquiteturas não aderentes ao repositório.
  - [ ] **Registro de estratégias:** disponibilizar catálogo determinístico das estratégias existentes, características, custos, requisitos, idiomas, formatos e cenários aplicáveis, permitindo seleção por humanos, configuração ou roteamento automático.
  - [ ] **Composição de estratégias:** permitir pipelines em que estratégias sejam aplicadas sequencialmente, condicionalmente ou em paralelo, como segmentação estrutural seguida de divisão semântica, regex seguida de ajuste por tokens ou identificação de citações seguida de expansão contextual.
  - [ ] **Prevenção de combinações inválidas:** composição DEVE validar ordem, compatibilidade, duplicação e efeitos, impedindo pipelines que corrompam offsets, relações ou rastreabilidade.
  - [ ] **Configuração centralizada:** perfis, parâmetros, modelos, idiomas, limites, fallbacks e combinações DEVEM ser centralmente configuráveis e validados, evitando constantes e condicionais dispersas.
  - [ ] **Extensibilidade:** novas estratégias DEVEM poder ser adicionadas sem alteração invasiva das existentes, preservando contratos, metadados e índices independentes.

  - [ ] **Baseline e métricas:** medir o comportamento vigente antes de modificar o pipeline e comparar candidatos por conjunto representativo de documentos e consultas.
  - [ ] **Métricas mínimas:** avaliar, conforme aplicabilidade, precisão, recall, `MRR`, `nDCG`, cobertura de citações, completude contextual, acerto multilíngue, qualidade da aglutinação, falsos positivos, falsos negativos, latência, tokens, memória, armazenamento, tempo de indexação e custo operacional.
  - [ ] **Métricas de chunking:** comparar estratégias por preservação semântica, ruptura de citações, redundância por overlap, distribuição de tamanhos, capacidade de localização, quantidade de chunks recuperados e contexto necessário para resposta correta.
  - [ ] **Casos de teste:** incluir documentos curtos e extensos, estruturados e irregulares, monolíngues e multilíngues, citações curtas e extensas, notas, referências, mudanças de idioma, OCR imperfeito, múltiplas edições, traduções e consultas ambíguas.
  - [ ] **Comparação isolada e combinada:** medir cada estratégia individualmente e nas combinações propostas, impedindo atribuição incorreta de ganho a um componente que apenas aumentou custo.
  - [ ] **Avaliação humana:** quando métricas automáticas não forem suficientes para interpretar relevância, contexto ou qualidade de citações, utilizar amostra verificável com critérios explícitos, sem substituir toda validação por avaliação subjetiva.
  - [ ] **Critério de ganho líquido:** técnica somente DEVE tornar-se padrão quando demonstrar benefício recorrente superior aos custos e riscos introduzidos, sem regressão relevante de precisão, rastreabilidade, completude, portabilidade ou manutenção.
  - [ ] **Adoção incremental e reversível:** mudanças aprovadas DEVEM ser introduzidas por etapas, com compatibilidade, observação, comparação e possibilidade de reversão ou troca de estratégia.
  - [ ] **Documentação:** registrar estratégias aprovadas, rejeitadas ou experimentais; parâmetros; limitações; compatibilidades; métricas; critérios de seleção; fallbacks; versionamento; reindexação; e procedimento para criação de novas estratégias.
  - [ ] **Critério de aceite:** considerar concluído somente quando o repositório tiver sido inspecionado; os componentes de RAG tiverem sido avaliados contra baseline; houver arquitetura configurável para múltiplas estratégias de chunks, incluindo métodos determinísticos, regex, linguísticos, semânticos e baseados em LLM quando aprovados; forem suportados overlap, encadeamento, hierarquia, estratégias paralelas, composição e personalização por situação; a fonte e as citações permanecerem rastreáveis; busca híbrida, multilíngue e aglutinação forem preservadas ou aprimoradas; os custos e ganhos estiverem mensurados; e apenas técnicas com benefício líquido comprovado forem incorporadas sem inferir ou impor arquitetura incompatível com o projeto.

- [ ] **Implementar publicação web institucional, indexação global, dados bibliográficos formativos e geração de capas das publicações por GitHub Pages:** configurar mecanismo próprio de publicação, baseado em workflow e scripts do repositório, sem depender da publicação padronizada ou automática do GitHub Pages, gerando página web ultrassucinta, profissional, elegante, visualmente atraente e tecnicamente otimizada para apresentar o produto.
  - [ ] **Leitura e precedência normativa:** antes da implementação, ler integralmente o RCF aplicável, `AGENTS.md`, a estrutura real do repositório e a `NORMA-IF-SIL-001` incorporada ao final deste arquivo.
    - A implementação DEVE adaptar caminhos, nomes, ferramentas e integração ao estado real do projeto, sem inferir arquitetura ausente.
    - Em conflito, o RCF vigente DEVE prevalecer.
    - A `NORMA-IF-SIL-001` DEVE reger exclusivamente a estrutura, obtenção, validação, evidência, associação entre formatos, hashes e serialização das propriedades `book` e `global_hashes`.
    - A `NORMA-IF-SIL-001` constitui perfil parcial e formativo; NÃO DEVE ser interpretada como contrato integral de metadados, índice, publicação, asset, fonte, rota ou schema canônico.
    - Este TODO NÃO DEVE inserir na estrutura conforme à norma nenhuma propriedade além de `book` e `global_hashes`.
    - Requisitos próprios deste TODO — página, índice global, URLs públicas, capas, workflows, build e publicação — permanecem externos ao documento formativo e NÃO DEVEM ser atribuídos à `NORMA-IF-SIL-001`.
    - O envelope do índice global e o documento formativo possuem responsabilidades distintas e NÃO DEVEM ser fundidos estruturalmente.

  - [ ] **Publicação não padronizada:** a implantação DEVE ocorrer por workflow dedicado, responsável por preparar, validar e publicar os artefatos no GitHub Pages a partir da origem, branch ou diretório definidos pelo projeto, sem depender implicitamente de build automático, tema ou convenção padrão da plataforma.

  - [ ] **Página explicativa:** a página DEVE explicar de forma direta e compacta:
    - finalidade do produto;
    - natureza das publicações disponibilizadas;
    - formatos suportados;
    - forma geral de acesso;
    - demais informações indispensáveis à compreensão do projeto.

  - [ ] **Concisão:** a página NÃO DEVE conter conteúdo promocional excessivo, documentação extensa, seções redundantes ou informações sem utilidade imediata.

  - [ ] **Qualidade visual:** o resultado DEVE apresentar composição profissional, elegante, bonita, atraente, responsiva, acessível e coerente, sem poluição visual, excesso de animações ou dependências desproporcionais.

  - [ ] **Tecnologias preferenciais:** quando houver necessidade de lógica cliente, utilizar TypeScript; quando houver estilização processada, utilizar Sass.

  - [ ] **Recursos avançados:** quando ícones, componentes ou recursos de interface agregarem valor real, priorizar Font Awesome e WebAwesome.

  - [ ] **Uso proporcional:** bibliotecas e frameworks NÃO DEVEM ser incorporados integralmente quando apenas pequena parcela for necessária. O build ou carregamento DEVE incluir somente componentes, estilos, ícones e recursos efetivamente utilizados.

  - [ ] **Significado de incorporação:** “incorporar” NÃO DEVE ser interpretado como embutir indiscriminadamente todo o conteúdo no HTML, JavaScript ou CSS principal. Recursos externos DEVEM, quando apropriado, ser referenciados por URLs distintas, estáveis e favoráveis ao cache.

  - [ ] **CDN:** o uso de CDN PODE ser adotado quando apresentar ganho líquido em cache compartilhado, peso transferido, disponibilidade, latência e manutenção. A decisão DEVE considerar também privacidade, integridade, disponibilidade offline, dependência externa e possibilidade de indisponibilidade.

  - [ ] **Fallback:** dependências externas críticas DEVEM possuir estratégia proporcional de fallback ou degradação aceitável quando sua indisponibilidade puder inutilizar a página.

  - [ ] **Otimização:** HTML, CSS, JavaScript, fontes, ícones, imagens e demais ativos DEVEM ser reduzidos ao necessário, com cache, compressão, minificação, carregamento seletivo e invalidação adequados.

  - [ ] **Separação de responsabilidades:** a página pública DEVE apresentar o produto, mas NÃO DEVE expor, listar ou vincular diretamente:
    - o arquivo JSON indexador global;
    - os arquivos de publicação;
    - URLs diretas das publicações;
    - diretórios internos de distribuição.

  - [ ] **Ausência de links indiretos:** o JSON e as publicações também NÃO DEVEM ser divulgados por botões, âncoras ocultas, metadados visuais ou listagens geradas na página, salvo futura determinação normativa expressa.

  - [ ] **Indexador global obrigatório:** manter, de forma gerada e sincronizada, um indexador global de todas as publicações em JSON.

  - [ ] **Localização:** o indexador DEVE existir:
    - em `dist/`, quando esse diretório integrar o fluxo de build ou distribuição;
    - no conteúdo efetivamente publicado pelo GitHub Pages;
    - no subdiretório-raiz destinado às publicações.

  - [ ] **Fonte única:** as diferentes cópias do indexador NÃO DEVEM ser mantidas manualmente de forma independente. DEVEM resultar da mesma fonte canônica ou da mesma etapa determinística de geração.
  - [ ] **Localização de assets:** todo asset de uma publicação deve localizar-se aninhada imediatamente sob mesmo diretório de localização da publicação (pdf/epub) em `./assets/<basename-publicacao>/`, incluindo cover.png ou qualquer outro metadado, como os já previamente existentes .json com o mesmo nome .json que devem ser movidos para a nova localização e ter sua nova localização adequadalizada em `baixar.py`.

  - [ ] **Exemplo não produtivo:** os marcadores de hash existem somente para demonstrar o aninhamento. Payload produtivo DEVE conter hashes reais, integralmente recalculados sobre os bytes originais.

  - [ ] **Dados formativos obrigatórios:** cada item do índice DEVE ser validado conforme a `NORMA-IF-SIL-001`.
    - Título, colaboradores e idioma DEVEM ser confrontados com ao menos duas evidências independentes quando ambas estiverem disponíveis.
    - Metadados estruturados e conteúdo editorial diretamente acessível DEVEM preceder OCR.
    - OCR somente DEVE ser utilizado quando a camada textual for ausente ou insuficiente.
    - OCR NÃO DEVE alterar os bytes usados nos hashes, substituir o original nem ser apresentado como evidência primária autossuficiente.
    - Conflito material, baixa confiança, ausência de autoria, arquivo ilegível ou ausência de evidência obrigatória DEVE produzir diagnóstico e bloquear emissão conforme.
    - O gerador NÃO DEVE inventar, completar por plausibilidade ou escolher silenciosamente entre evidências materiais conflitantes.

  - [ ] **Escopo fechado de `book`:** `book` DEVE conter exatamente:
    - `title`;
    - `contributors`;
    - `edition`;
    - `language`;
    - `primary_category`;
    - `tags`;

  - [ ] **Escopo fechado de `urls`:** `urls` DEVE conter:
    - as urls de cada asset epub/pdf pertencente àquela publicação disponibilizado neste repositório, além daqueles utilizados como origem, existentes em eventuais arquivos de metadados (como `.source.mjson` e outros equivalentes) que aponntem diretamente para arquivos epub/pdf.

  - [ ] **Escopo fechado de contribuidores:** cada item de `book.contributors` DEVE conter exatamente `name` e `role`, preservando forma creditada, função editorial comprovada e ordem de crédito da edição.

  - [ ] **Edição restrita:** `book.edition` DEVE ser exatamente `{}`. Se qualificador de edição for necessário para distinguir a publicação, o documento NÃO DEVE ser emitido como conforme até decisão normativa específica; a informação NÃO DEVE ser descartada nem projetada em outra propriedade.

  - [ ] **Categoria e tags:** categoria e tags DEVEM resultar de vocabulário controlado e evidência editorial. Sem tag adicional comprovada, `book.tags` DEVE ser `[]`.

  - [ ] **Aglutinação entre formatos:** PDF e EPUB somente DEVEM integrar o mesmo item quando título, autoria, idioma e identidade editorial forem compatíveis.
    - equivalência textual aproximada isolada NÃO DEVE bastar;
    - igualdade de hashes entre formatos NÃO DEVE ser esperada nem utilizada;
    - diferença de paginação, layout ou codificação não implica obra distinta;
    - diferença material de conteúdo, idioma, autoria ou edição DEVE impedir associação automática;
    - confiança insuficiente DEVE encaminhar para revisão humana.

  - [ ] **URLs:** as URLs DEVEM ser válidas, estáveis, corretamente codificadas e coerentes com o caminho final publicado.

  - [ ] **Ordenação:** a ordem das publicações e URLs DEVE ser determinística, preferencialmente por título normalizado e prioridade de formato definida pelo projeto. Em `global_hashes`, quando ambos existirem, a ordem DEVE ser `pdf`, depois `epub`.

  - [ ] **Duplicidade:** o gerador DEVE impedir URLs repetidas, formatos duplicados e entradas equivalentes produzidas por diferenças irrelevantes de caminho, caixa, codificação ou barra terminal. Títulos iguais NÃO DEVEM ser fundidos sem comprovação de identidade editorial.

  - [ ] **Descoberta das publicações:** o método de identificação dos arquivos publicáveis DEVE respeitar regras, formatos, exclusões e convenções reais do repositório, sem inferir extensões ou diretórios não confirmados.

  - [ ] **Preservação dos originais:** PDF e EPUB originais DEVEM permanecer inalterados antes do cálculo dos hashes. Conversão, reparo, reempacotamento, normalização, OCR, renderização ou extração NÃO DEVEM modificar o arquivo usado como origem normativa.

  - [ ] **Identificação de formato:** o formato DEVE ser confirmado por assinatura e estrutura interna, não somente por extensão, URL ou tipo declarado.

  - [ ] **Hashes globais:**
    - cada formato original aceito DEVE possuir exatamente um item;
    - a lista DEVE conter um ou dois itens;
    - `format` DEVE ser exclusivamente `pdf` ou `epub`;
    - `sha1`, `sha256` e `sha512` DEVEM coexistir;
    - hashes DEVEM ser calculados na mesma passagem, sobre os mesmos chunks e bytes integrais do original;
    - saídas DEVEM ser hexadecimais minúsculas, sem prefixo ou separador;
    - divergência em qualquer algoritmo DEVE rejeitar igualdade byte a byte;
    - SHA-1 NÃO DEVE, isoladamente, comprovar integridade.

  - [ ] **Processamento seguro de EPUB:** tratar EPUB como ZIP OCF não confiável; limitar entradas, tamanhos, razão de expansão, profundidade e caminhos; rejeitar traversal, path absoluto, symlink, colisão normalizada e entidade XML externa; localizar o Package Document pelo contêiner e respeitar o spine como ordem editorial.

  - [ ] **Processamento seguro de PDF:** usar biblioteca que interprete objetos, xref, streams, fontes, páginas e metadados. Regex sobre bytes crus NÃO DEVE extrair `book`. Página de rosto e colofão visíveis DEVEM prevalecer sobre metadado técnico conflitante.

  - [ ] **Capa pública obrigatória:** imediatamente no mesmo diretório público de cada publicação, EPUB ou PDF, DEVE existir arquivo denominado exatamente `cover.png`.

  - [ ] **Escopo por grupo lógico:** quando EPUB e PDF da mesma obra compartilharem diretório, DEVE existir uma única `cover.png` canônica. Quando estiverem em diretórios distintos, cada diretório DEVE conter cópia gerada da capa correspondente.

  - [ ] **Precedência da capa:** como requisito autônomo deste TODO, a capa DEVE resultar:
    1. da capa EPUB utilizável;
    2. sem capa EPUB utilizável, da primeira página PDF adequada.

  - [ ] **Limite de autoridade:** regras de capa, arquivo `cover.png`, localização, dimensões, compressão e regeneração pertencem a este TODO ou ao RCF geral; NÃO DEVEM ser apresentadas como propriedades ou exigências estruturais da `NORMA-IF-SIL-001`.

  - [ ] **Capa EPUB:** utilizar primeiro o item identificado editorialmente como capa, incluindo `cover-image` quando aplicável; fallback legado somente DEVE ser aceito com referência válida. Imagem arbitrária de maior dimensão NÃO DEVE ser presumida como capa.

  - [ ] **Fallback PDF:** sem capa EPUB utilizável, renderizar a primeira página PDF adequada por analisador próprio, preservando conteúdo editorial e sem modificar o PDF original.

  - [ ] **Primeira página adequada:** página vazia, meramente técnica, corrompida, de erro, sem conteúdo representativo ou ilegível NÃO DEVE ser aceita.

  - [ ] **Falha do grupo:** ausência de capa EPUB utilizável e de primeira página PDF adequada DEVE falhar a geração do grupo. Grupo incompleto NÃO DEVE ser publicado silenciosamente.

  - [ ] **Formato e dimensão:** a capa pública DEVE:
    - chamar-se exatamente `cover.png`;
    - ser PNG válido e decodificável;
    - possuir no máximo 800 px em cada eixo;
    - preservar proporção, nitidez e legibilidade;
    - não ampliar artificialmente imagem menor sem justificativa;
    - remover EXIF, comentários, miniaturas e metadados sem utilidade de renderização;
    - ser otimizada para navegador sem degradação desproporcional.

  - [ ] **Artefatos intermediários:** páginas renderizadas, imagens-fonte convertidas, caches de extração e demais intermediários NÃO DEVEM integrar `dist/` nem o site publicado.

  - [ ] **Regenerabilidade:** `cover.png` DEVE ser integralmente regenerável a partir das fontes canônicas e configuração versionada.
    - removida a capa, a próxima execução local ou em CI DEVE regenerá-la;
    - mudança material no EPUB, PDF, parser, extrator, configuração ou gerador DEVE invalidá-la;
    - imagem externa NÃO DEVE ser escolhida por semelhança de nome, título ou arquivo.

  - [ ] **Validação obrigatória da capa:** comprovar existência, localização, origem, precedência, dimensões, proporção, legibilidade, validade PNG, remoção de metadados desnecessários, ausência de intermediários e regeneração após remoção.

  - [ ] **Teste de regeneração:** remover `cover.png`, executar novamente o gerador e confirmar origem, validade, dimensões e determinismo aplicável.

  - [ ] **Falha bloqueante de capa:** capa ausente, inválida, ilegível, acima do limite, gerada por precedência incorreta ou impossível de regenerar DEVE falhar a geração do grupo.

  - [ ] **Geração por script:** indexador, capas, dados formativos, ativos web e demais artefatos derivados DEVEM ser produzidos por script reexecutável, determinístico e compatível com execução local e CI.

  - [ ] **TypeScript nos scripts Node.js:** qualquer novo script executado em Node.js DEVE ser implementado em TypeScript e transpilado para o alvo normatizado pelo projeto.

  - [ ] **Sass:** quando utilizado, DEVE ser compilado durante o build; fontes `.scss` desnecessárias ao site NÃO DEVEM ser publicadas.

  - [ ] **Dependências proporcionais:** bibliotecas para EPUB, PDF, OCR, imagem, YAML, JSON ou compactação DEVEM ser mantidas, estáveis e proporcionais. Alternativas somente são conformes quando preservarem segurança, bytes, ordem, evidência e resultados normativos.

  - [ ] **Processamento incremental:** alterações em uma publicação DEVEM reprocessar somente seu grupo e índices dependentes, quando seguro e consistente.

  - [ ] **Cache rastreável:** caches PODEM evitar reprocessamento, mas DEVEM incorporar identidade suficiente das fontes, configuração e versões dos analisadores e geradores aplicáveis.

  - [ ] **Workflow:** criar ou atualizar workflow dedicado para:
    1. obter o código-fonte;
    2. instalar somente dependências necessárias;
    3. descobrir e agrupar publicações;
    4. identificar formatos por assinatura e estrutura;
    5. preservar originais e calcular hashes;
    6. extrair e validar `book`;
    7. comprovar identidade editorial entre formatos;
    8. gerar e validar capas;
    9. montar e validar `formative_data`;
    10. gerar o índice global;
    11. gerar e otimizar a página;
    12. preparar o diretório publicável;
    13. validar URLs, JSON, dados formativos, capas e ativos;
    14. publicar no GitHub Pages.

  - [ ] **Gatilhos:** o workflow DEVE executar quando alterações puderem afetar página, publicações, capas, índice, dados formativos, scripts, estilos, ativos, parser, norma ou configuração de publicação.

  - [ ] **Execução manual:** o workflow DEVE permitir disparo manual para validação, recuperação ou republicação controlada.

  - [ ] **Permissões mínimas:** as permissões DEVEM limitar-se às estritamente necessárias para build e publicação.

  - [ ] **Concorrência:** publicações concorrentes DEVEM ser serializadas ou canceladas com segurança, impedindo que execução antiga sobrescreva resultado mais recente.

  - [ ] **Execução local equivalente:** o processo local DEVE reproduzir, tanto quanto tecnicamente possível, as mesmas etapas, validações e resultados do workflow.

  - [ ] **Saída operacional:** scripts demorados DEVEM exibir progresso ultrassucinto, indicando etapa, publicação corrente, sucesso ou falha, sem inundar a saída nem aparentar congelamento.

  - [ ] **Validação do índice global:** o build DEVE falhar quando:
    - o arquivo não for JSON válido;
    - o envelope não respeitar o contrato;
    - houver publicação sem `title`, `urls` ou `formative_data`;
    - `urls` estiver vazio ou contiver URL inválida;
    - `formative_data` não contiver exatamente `book` e `global_hashes`;
    - `book`, contribuidores ou hashes possuírem chave adicional, ausente, duplicada, tipo, padrão ou cardinalidade inválidos;
    - `book.edition` não for exatamente `{}`;
    - não houver ao menos um contribuidor com `role: "author"`;
    - houver formato ausente, excedente ou duplicado;
    - título, URLs, formatos ou hashes forem incoerentes;
    - o índice divergir dos arquivos efetivamente publicados.

  - [ ] **Validação integral da norma:** aplicar:
    1. parse seguro de JSON ou YAML;
    2. raiz exata `book` + `global_hashes`;
    3. seis chaves exatas de `book`;
    4. `edition: {}` e presença de `tags`;
    5. ao menos um contribuidor e um `author`;
    6. duas chaves exatas por contribuidor;
    7. validação de título, nomes, papéis, idioma, categoria e tags;
    8. um ou dois itens em `global_hashes`, sem formato duplicado;
    9. quatro chaves exatas por hash;
    10. recálculo dos três hashes sobre os bytes originais;
    11. confirmação da associação editorial quando PDF e EPUB coexistirem;
    12. conversão para o outro formato e igualdade profunda.

  - [ ] **Diagnóstico:** falha DEVE indicar propriedade, regra violada e evidência necessária, sem inventar valor substituto nem remover item inválido para simular conformidade.

  - [ ] **Validação da página:** verificar, no mínimo:
    - HTML válido;
    - ausência de links públicos para o JSON e para as publicações;
    - carregamento correto dos ativos;
    - responsividade;
    - acessibilidade básica;
    - ausência de dependências não utilizadas;
    - funcionamento sob o caminho real do GitHub Pages.

  - [ ] **Validação de integridade pública:** cada URL do índice DEVE corresponder a arquivo efetivamente publicado; cada diretório de publicação DEVE conter `cover.png`; cada `global_hashes[]` DEVE corresponder aos bytes originais do formato indicado; e cada `book` DEVE corresponder à publicação agrupada.

  - [ ] **Base path:** scripts, estilos, imagens, fontes e demais recursos DEVEM funcionar em domínio próprio e sob subdiretório de projeto, sem caminhos absolutos incompatíveis.

  - [ ] **Sincronização:** toda alteração nas publicações DEVE regenerar índice, dados formativos, hashes, capas afetadas e conteúdo publicável correspondente. Artefato obsoleto ou divergente NÃO DEVE ser publicado.

  - [ ] **Artefatos gerados:** derivados DEVEM ser identificáveis como gerados e NÃO DEVEM ser editados manualmente quando houver fonte canônica correspondente.

  - [ ] **Release limpo:** o conteúdo publicado NÃO DEVE incluir fontes de desenvolvimento, caches, testes, logs, mapas de origem, documentação interna, configurações de desenvolvimento, dependências desnecessárias, imagens intermediárias, temporários, evidências internas ou saídas transitórias de OCR.

  - [ ] **Divergência entre subitens acima e `NORMA-IF-SIL-001`**: em caso de divergência entre as explicações solicitadas nos subitens acima, e a norma eftiva `NORMA-IF-SIL-001`, prrevalece a explicação normativa conitda em `NORMA-IF-SIL-001`.

  - [ ] **Critério de aceite:** considerar concluído somente quando houver:
    - página institucional ultrassucinta e profissional publicada por workflow próprio;
    - scripts em TypeScript e estilos em Sass quando aplicáveis;
    - dependências seletivas, proporcionais e otimizadas;
    - ausência de links públicos para índice e publicações;
    - índice global válido e sincronizado nos destinos definidos;
    - separação inequívoca entre envelope global e documento formativo;
    - `formative_data` contendo somente `book` e `global_hashes`;
    - inexistência de `schema_version`, `book.id`, `short_token`, `artifact_id`, `assets`, `sources`, QR, pacote ou contêiner como propriedade do documento conforme à norma;
    - extração prioritariamente estruturada ou textual, com OCR apenas quando necessário;
    - identidade editorial comprovada antes da aglutinação de PDF e EPUB;
    - hashes recalculados sobre os bytes integrais originais;
    - `cover.png` válida, otimizada, regenerável e localizada junto à publicação;
    - precedência da capa EPUB e fallback pela primeira página PDF adequada comprovados;
    - limite máximo de 800 px por eixo;
    - ausência de intermediários desnecessários em `dist/`;
    - falha bloqueante de grupos incompletos ou inconsistentes;
    - build local reproduzível;
    - validações automatizadas;
    - publicação contendo exclusivamente artefatos necessários.

    ***

    # Anexo normativo obrigatório

    ***

    # NORMA-IF-SIL-001 — Dados Formativos para Sugestão de Livro

    ## 1. Autoridade e escopo fechado
    - `SIL-001` Esta norma DEVE ser subordinada ao `RCF-IF-001` e reger exclusivamente as propriedades `book`, `urls` e `global_hashes`, com suas propriedades descendentes expressamente definidas neste documento.
    - `SIL-002` A estrutura DEVE ser semanticamente idêntica em JSON e YAML.
    - `SIL-003` O objeto raiz DEVE conter exatamente `book`, `urls` e `global_hashes`.
    - `SIL-004` `book` DEVE conter exatamente `title`, `contributors`, `edition`, `language`, `primary_category` e `tags`.
    - `SIL-005` Cada item de `book.contributors` DEVE conter exatamente `name` e `role`.
    - `SIL-006` `book.edition` DEVE ser exatamente o objeto vazio `{}` neste perfil restrito.
    - `SIL-007` Cada item de `global_hashes` DEVE conter exatamente `format`, `sha1`, `sha256` e `sha512`.
    - `SIL-007A` Cada item de `urls` DEVE conter exatamente `format` e `url`.
    - `SIL-008` Propriedade não enumerada em `SIL-003..007A` NÃO DEVE constar desta norma nem de documento conforme a ela.
    - `SIL-009` Todas as propriedades enumeradas são estruturalmente obrigatórias. Somente `book.edition` e `book.tags` admitem os valores vazios definidos nesta norma.
    - `SIL-010` Informação declarada ou extraída DEVE ser tratada como candidata até validação por evidência reprodutível. Dado incerto, conflitante ou inventado NÃO DEVE preencher propriedade.
    - `SIL-011` Documento conforme a esta norma constitui perfil parcial e formativo de sugestão. Ele NÃO DEVE ser interpretado como metadado canônico integral nem substituir o contrato completo regido pelo RCF.

    ## 2. Agnosticismo entre JSON e YAML

    | Semântica      | JSON   | YAML          | Regra                                      |
    | -------------- | ------ | ------------- | ------------------------------------------ |
    | objeto         | object | mapping       | chaves textuais únicas e sensíveis a caixa |
    | lista ordenada | array  | sequence      | ordem preservada                           |
    | texto          | string | string scalar | Unicode válido                             |
    | objeto vazio   | `{}`   | `{}`          | permitido somente em `book.edition`        |
    | lista vazia    | `[]`   | `[]`          | permitida somente em `book.tags`           |
    - `SIL-FMT-001` A representação DEVE possuir um único documento e um único objeto raiz.
    - `SIL-FMT-002` Chaves, hierarquia, tipos, valores, Unicode e ordem das listas DEVEM permanecer iguais após conversão JSON ↔ YAML.
    - `SIL-FMT-003` JSON DEVE ser UTF-8 válido, sem BOM, comentário, vírgula final, chave duplicada ou valor numérico não finito.
    - `SIL-FMT-004` YAML DEVE usar o subconjunto seguro de YAML 1.2 composto por mapping, sequence e string. Âncora, alias, merge key, tag explícita, construtor, diretiva e múltiplos documentos DEVEM ser rejeitados.
    - `SIL-FMT-005` Em YAML, toda string DEVERIA usar aspas para impedir resolução implícita e preservar caixa, pontuação e zeros.
    - `SIL-FMT-006` `null`, chave omitida, string vazia e lista ou objeto vazio fora dos dois casos autorizados DEVEM ser rejeitados.
    - `SIL-FMT-007` A ordem recomendada das chaves DEVE seguir os exemplos; consumidor NÃO DEVE depender da ordem de chaves.

    ## 3. Matriz integral de propriedades

    ### 3.1 Raiz

    | Propriedade     | Obrigatória | Tipo   | Cardinalidade             | Valor vazio |
    | --------------- | ----------- | ------ | ------------------------- | ----------- |
    | `book`          | sim         | objeto | exatamente 6 propriedades | proibido    |
    | `urls`          | sim         | lista  | 1 ou mais itens           | proibido    |
    | `global_hashes` | sim         | lista  | 1 ou 2 itens              | proibido    |

    ### 3.2 `book`

    | Propriedade             | Obrigatória | Tipo   | Domínio                              | Valor vazio      |
    | ----------------------- | ----------- | ------ | ------------------------------------ | ---------------- |
    | `book.title`            | sim         | string | título editorial Unicode não vazio   | proibido         |
    | `book.contributors`     | sim         | lista  | 1 ou mais contribuidores             | proibido         |
    | `book.edition`          | sim         | objeto | exclusivamente `{}`                  | `{}` obrigatório |
    | `book.language`         | sim         | string | etiqueta BCP 47 válida em minúsculas | proibido         |
    | `book.primary_category` | sim         | string | slug `[a-z0-9]+(?:-[a-z0-9]+)*`      | proibido         |
    | `book.tags`             | sim         | lista  | zero ou mais slugs únicos            | `[]` permitido   |

    ### 3.3 `book.contributors[]`

    | Propriedade                | Obrigatória | Tipo   | Domínio                          | Valor vazio |
    | -------------------------- | ----------- | ------ | -------------------------------- | ----------- |
    | `book.contributors[].name` | sim         | string | nome editorial Unicode não vazio | proibido    |
    | `book.contributors[].role` | sim         | string | token `[a-z][a-z0-9-]*`          | proibido    |

    ### 3.4 `global_hashes[]`

    | Propriedade              | Obrigatória | Tipo   | Domínio                        | Valor vazio |
    | ------------------------ | ----------- | ------ | ------------------------------ | ----------- |
    | `global_hashes[].format` | sim         | string | exclusivamente `pdf` ou `epub` | proibido    |
    | `global_hashes[].sha1`   | sim         | string | 40 caracteres `[0-9a-f]`       | proibido    |
    | `global_hashes[].sha256` | sim         | string | 64 caracteres `[0-9a-f]`       | proibido    |
    | `global_hashes[].sha512` | sim         | string | 128 caracteres `[0-9a-f]`      | proibido    |

    ### 3.5 `urls[]`

    | Propriedade     | Obrigatória | Tipo   | Domínio                            | Valor vazio |
    | --------------- | ----------- | ------ | ---------------------------------- | ----------- |
    | `urls[].format` | sim         | string | exclusivamente `pdf` ou `epub`     | proibido    |
    | `urls[].url`    | sim         | string | URI HTTP(S) absoluta e normalizada | proibido    |

    ## 4. Regras de obtenção de `book`

    ### 4.1 Sequência comum de evidência
    1. Preservar o arquivo original sem conversão, reparo, reempacotamento ou normalização.
    2. Identificar o formato pela assinatura e pela estrutura interna, não somente por extensão ou tipo declarado.
    3. Extrair metadado estruturado por analisador próprio do formato.
    4. Extrair página de rosto, verso da página de rosto, colofão e primeiras unidades textuais na ordem editorial.
    5. Normalizar somente uma cópia de comparação: Unicode, espaços e caixa. O valor editorial original permanece preservado.
    6. Comparar ao menos duas evidências independentes para título, autoria e idioma quando ambas estiverem disponíveis.
    7. Interromper diante de conflito material, ausência de autoria, baixa confiança ou arquivo ilegível.
    8. Definir categoria e tags somente por vocabulário controlado e evidência editorial.
    9. Montar `book` somente após validar todas as suas propriedades.

    ### 4.2 `book.title`
    - `SIL-TITLE-001` `book.title` DEVE representar o título editorial principal da obra na edição analisada.
    - `SIL-TITLE-002` A precedência DEVE ser: página de rosto ou colofão visível; título estruturado do EPUB coerente; metadado estruturado do PDF coerente; cabeçalho editorial recorrente.
    - `SIL-TITLE-003` Nome de arquivo, nome de diretório, endereço de aquisição, texto de capa isolado, primeira linha extraída ou resultado de OCR isolado NÃO DEVE constituir prova suficiente.
    - `SIL-TITLE-004` Capitalização, diacríticos, pontuação e grafia editorial DEVEM ser preservados.
    - `SIL-TITLE-005` Espaço inicial ou final, controle Unicode e repetição acidental de espaços DEVEM ser removidos sem alterar o conteúdo lexical.
    - `SIL-TITLE-006` Dois títulos materialmente distintos DEVEM produzir diagnóstico e revisão humana, nunca escolha automática do primeiro.

    ### 4.3 `book.contributors`
    - `SIL-CONTRIB-001` `book.contributors` DEVE conter ao menos um item com `role: "author"`.
    - `SIL-CONTRIB-002` O primeiro item com `role: "author"` DEVE representar o autor principal.
    - `SIL-CONTRIB-003` A ordem dos itens DEVE seguir a ordem de crédito da edição.
    - `SIL-CONTRIB-004` Duplicata exata de `name + role` DEVE ser removida; homônimos NÃO DEVEM ser fundidos sem evidência.
    - `SIL-CONTRIB-005` Papéis recomendados, quando comprovados, são `author`, `editor`, `translator`, `compiler` e `illustrator`.
    - `SIL-CONTRIB-006` Outro valor de `role` somente DEVE ser aceito quando atender ao padrão e possuir significado editorial comprovado; ele NÃO adquire semântica inferida.
    - `SIL-CONTRIB-007` Ausência, abreviação não comprovada, tradução de nome, conflito ou autoria inferida exclusivamente do nome do arquivo DEVE bloquear o documento.

    #### 4.3.1 `book.contributors[].name`
    - `SIL-NAME-001` `name` DEVE preservar a forma creditada na edição.
    - `SIL-NAME-002` Prefixo, sufixo, inicial, diacrítico e ordem nominal NÃO DEVEM ser alterados sem autoridade editorial.
    - `SIL-NAME-003` Comparação para duplicidade PODE normalizar Unicode, espaços e caixa em cópia derivada; o valor emitido DEVE conservar a forma editorial.

    #### 4.3.2 `book.contributors[].role`
    - `SIL-ROLE-001` `role` DEVE descrever a função editorial efetivamente creditada.
    - `SIL-ROLE-002` A função NÃO DEVE ser inferida da posição do nome quando a fonte apresentar papel explícito.
    - `SIL-ROLE-003` Pessoa citada, prefaciador, personagem, organização mantenedora ou proprietário do arquivo NÃO DEVE ser classificado como autor sem crédito editorial.

    ### 4.4 `book.edition`
    - `SIL-EDITION-001` `book.edition` DEVE existir e ser exatamente `{}`.
    - `SIL-EDITION-002` Nenhuma propriedade descendente DEVE ser acrescentada neste perfil.
    - `SIL-EDITION-003` O objeto vazio NÃO DEVE significar que todas as edições são equivalentes; significa somente que este perfil restrito não representa detalhe de edição.
    - `SIL-EDITION-004` Quando ano, número, revisão, volume, adaptação, condensação ou outro qualificador for necessário para distinguir a publicação, o documento NÃO DEVE ser emitido como conforme a este perfil até decisão normativa específica. A informação NÃO DEVE ser descartada nem projetada em outra propriedade.

    ### 4.5 `book.language`
    - `SIL-LANG-001` `book.language` DEVE representar o idioma predominante da edição, não o idioma da interface, do site ou do operador.
    - `SIL-LANG-002` O valor DEVE ser etiqueta BCP 47 válida e serializada em minúsculas, como `pt-br`, `en-us` ou `es`.
    - `SIL-LANG-003` A precedência DEVE ser: idioma estruturado do EPUB coerente; declaração editorial visível; análise do conteúdo textual predominante; revisão humana.
    - `SIL-LANG-004` Detector automático de idioma DEVE ser somente evidência auxiliar e operar sobre amostra distribuída, não sobre título ou primeira página isolados.
    - `SIL-LANG-005` Nome de arquivo, domínio, país do fornecedor ou idioma de metadado técnico isolado NÃO DEVE definir o valor.
    - `SIL-LANG-006` Edição materialmente multilíngue sem idioma predominante inequívoco DEVE ser encaminhada para decisão humana.

    ### 4.6 `book.primary_category`
    - `SIL-CATEGORY-001` `book.primary_category` DEVE conter exatamente uma classificação principal do vocabulário controlado.
    - `SIL-CATEGORY-002` O valor DEVE usar minúsculas ASCII, hífen como separador e nenhum diacrítico.
    - `SIL-CATEGORY-003` Para o exemplo desta norma, o valor comprovado é `livros`.
    - `SIL-CATEGORY-004` Categoria NÃO DEVE ser inferida do nome de arquivo.
    - `SIL-CATEGORY-005` Quando duas categorias forem igualmente plausíveis, decisão editorial DEVE selecionar uma única categoria principal.

    ### 4.7 `book.tags`
    - `SIL-TAGS-001` `book.tags` DEVE existir.
    - `SIL-TAGS-002` Sem classificação adicional comprovada, o valor DEVE ser `[]`.
    - `SIL-TAGS-003` Cada item DEVE seguir `[a-z0-9]+(?:-[a-z0-9]+)*`, ser semanticamente relevante e não repetir `book.primary_category`.
    - `SIL-TAGS-004` Itens DEVEM ser únicos e ordenados por comparação lexical determinística.
    - `SIL-TAGS-005` Termo inferido somente de nome de arquivo, fornecedor, formato, idioma ou detalhe técnico NÃO DEVE integrar a lista.

    ## 5. Regras de obtenção de `global_hashes`

    ### 5.1 Conceito e cardinalidade
    - `SIL-GLOBAL-001` `global_hashes` DEVE conter exatamente um item para cada formato editorial original aceito.
    - `SIL-GLOBAL-002` A lista DEVE possuir um item quando houver somente PDF ou somente EPUB e dois itens quando ambos existirem.
    - `SIL-GLOBAL-003` `format` NÃO DEVE repetir-se na lista.
    - `SIL-GLOBAL-004` Quando ambos existirem, a ordem canônica DEVE ser `pdf`, depois `epub`.
    - `SIL-GLOBAL-005` PDF e EPUB da mesma edição DEVEM possuir matrizes próprias; equivalência textual NÃO implica igualdade de bytes.

    ### 5.2 Bytes normativos
    - `SIL-BYTES-001` Cada matriz DEVE ser calculada exclusivamente sobre os bytes integrais do PDF ou EPUB original.
    - `SIL-BYTES-002` Cálculo DEVE ocorrer antes de extração, conversão, correção, OCR, renderização, compactação ou qualquer alteração.
    - `SIL-BYTES-003` Leitura DEVE ser binária, sequencial e completa, sem conversão de texto ou normalização de fim de linha.
    - `SIL-BYTES-004` Arquivo reparado ou regravado constitui sequência de bytes diferente e NÃO DEVE herdar a matriz do original.
    - `SIL-BYTES-005` Para EPUB, a matriz DEVE incidir sobre o contêiner EPUB integral, não sobre arquivos internos isolados.
    - `SIL-BYTES-006` Para PDF, a matriz DEVE incidir sobre o arquivo PDF integral, incluindo todos os objetos, streams e atualizações incrementais presentes.

    ### 5.3 Algoritmos
    - `SIL-HASH-001` `sha1`, `sha256` e `sha512` DEVEM ser calculados na mesma passagem sobre os mesmos chunks.
    - `SIL-HASH-002` A saída DEVE ser hexadecimal minúscula, sem prefixo, espaço, hífen ou separador.
    - `SIL-HASH-003` `sha1` DEVE possuir 40 caracteres, `sha256` 64 e `sha512` 128.
    - `SIL-HASH-004` SHA-1 existe somente para interoperabilidade e NÃO DEVE, isoladamente, comprovar integridade.
    - `SIL-HASH-005` Divergência em qualquer um dos três valores DEVE rejeitar a alegação de igualdade byte a byte.
    - `SIL-HASH-006` Matriz parcial, algoritmo ausente, valor truncado, maiúsculo ou calculado sobre representação textual DEVE ser rejeitado.

    ### 5.4 Métodos recomendados

    #### 5.4.1 Node.js
    - Usar fluxo binário de `node:fs` e três instâncias de `node:crypto.createHash`, com algoritmos `sha1`, `sha256` e `sha512`.
    - Alimentar as três instâncias com cada chunk recebido, sem converter o chunk para string.
    - Finalizar cada instância com `digest("hex")`.
    - Confirmar que a leitura terminou normalmente e que nenhum erro de stream foi ignorado.
    - Para EPUB, usar leitor ZIP com limites para validar estrutura e extrair evidência de `book`, mas nunca para calcular `global_hashes`.
    - Para PDF, usar PDF.js ou analisador equivalente para metadado e texto; análise NÃO DEVE modificar o arquivo usado nos hashes.

    #### 5.4.2 Python
    - Abrir o arquivo em modo `rb`.
    - Usar simultaneamente `hashlib.sha1()`, `hashlib.sha256()` e `hashlib.sha512()`.
    - Ler blocos de tamanho fixo, alimentar os três objetos com cada bloco e finalizar com `hexdigest()`.
    - Confirmar leitura completa e propagar qualquer erro de entrada/saída.
    - Para EPUB, usar `zipfile` somente após validar limites e caminhos; `extractall()` sem guarda NÃO DEVE ser usado.
    - Para PDF, usar `pypdf`, PyMuPDF ou analisador equivalente para metadado, texto e renderização; OCR deve permanecer separado do original.

    #### 5.4.3 Neutralidade
    - Biblioteca citada é método recomendado, não dependência normativa.
    - Implementação alternativa somente é conforme quando produz os mesmos valores a partir dos mesmos bytes e preserva as regras de segurança e evidência.
    - Comando de shell cuja saída textual seja analisada NÃO DEVERIA substituir APIs criptográficas nativas quando estas estiverem disponíveis.

    ## 6. Regras de obtenção de `urls`

    ### 6.1 Conceito, estrutura e finalidade
    - `SIL-URL-001` `urls` DEVE ser uma lista não vazia de endereços candidatos à aquisição das variantes editoriais que se pretende incorporar.
    - `SIL-URL-002` Cada item DEVE vincular explicitamente uma única `url` ao respectivo `format`; formato NÃO DEVE ser inferido somente da extensão do endereço.
    - `SIL-URL-003` `urls[].format` DEVE ser exatamente `pdf` ou `epub`, em minúsculas, e identificar o formato editorial esperado após obtenção ou extração segura.
    - `SIL-URL-004` `urls[].url` DEVE ser URI HTTP(S) absoluta, sem credenciais, sem fragmento e com host explícito. Caminho e consulta DEVEM ser preservados integralmente.
    - `SIL-URL-005` `urls` é dado formativo de entrada da Issue. A propriedade NÃO DEVE ser copiada para a raiz do `metadata.json` schema 5 nem interpretada como endereço local de asset.
    - `SIL-URL-006` Após aquisição e validação, um processo editorial autorizado PODE usar cada item para formar a proveniência e a fonte canônica exigidas pelo RCF e para gerar o asset vinculativo correspondente. A sugestão ou a URL, isoladamente, NÃO autoriza download, incorporação nem publicação.

    ### 6.2 Cardinalidade e correlação
    - `SIL-URL-LINK-001` Para cada formato presente em `global_hashes`, `urls` DEVE conter ao menos um item com o mesmo `format`.
    - `SIL-URL-LINK-002` Todo formato presente em `urls` DEVE possuir exatamente um item correspondente em `global_hashes`.
    - `SIL-URL-LINK-003` Mais de uma URL do mesmo formato PODE existir quando representar fonte alternativa candidata para os mesmos bytes editoriais.
    - `SIL-URL-LINK-004` URLs duplicadas, após normalização segura para comparação, DEVEM ser rejeitadas; a ordem relativa das URLs distintas do mesmo formato DEVE seguir a preferência editorial declarada ou, sem preferência comprovada, a ordem de submissão.
    - `SIL-URL-LINK-005` A ordem canônica DEVE agrupar primeiro `pdf` e depois `epub`, acompanhando `global_hashes`; dentro de cada formato, a fonte preferencial DEVE anteceder as alternativas.
    - `SIL-URL-LINK-006` URL cujo conteúdo direto ou extraído não corresponda integralmente ao Hash Global do formato declarado NÃO DEVE ser usada para gerar asset, ainda que título, extensão ou tamanho pareçam corretos.

    ### 6.3 Como localizar e obter a URL
    1. Preferir o link oficial de download da publicação fornecido pelo editor, autor, biblioteca, repositório institucional ou provedor confiável.
    2. Quando houver página de publicação, localizar nela o link específico da variante PDF ou EPUB; a URL da página NÃO DEVE substituir o endereço do arquivo neste perfil estrito.
    3. Consultar, em seguida, manifesto oficial, catálogo estruturado, feed ou API pública do mesmo provedor.
    4. Usar URL declarada nos metadados do EPUB ou PDF apenas como pista e confirmá-la no provedor; endereço incorporado no arquivo NÃO DEVE ser aceito sem verificação.
    5. Resolver URL relativa somente contra a página ou manifesto que a declarou e registrar o resultado absoluto.
    6. Preservar a URL de aquisição submetida. Redirecionamento observado PODE ser registrado no relatório de validação, mas NÃO DEVE substituir silenciosamente o valor sugerido.
    7. Não inventar endereço por padrão de nome, trocar extensão, alterar código de idioma nem construir URL a partir do nome do arquivo sem confirmação por resposta válida do provedor.
    - `SIL-URL-SOURCE-001` Resultado de mecanismo de busca, cache, espelho não atribuído ou URL copiada de terceiro DEVE ser tratado somente como candidato até confirmação da origem e do conteúdo.
    - `SIL-URL-SOURCE-002` URL temporária, assinada, com token secreto, credencial, sessão ou validade curta NÃO DEVE constar do documento.
    - `SIL-URL-SOURCE-003` Parâmetro de consulta indispensável à obtenção pública DEVE ser preservado; parâmetro comprovadamente apenas analítico ou de rastreamento DEVERIA ser removido sem alterar o recurso entregue.
    - `SIL-URL-SOURCE-004` Se não existir URL pública direta e estável para uma variante, o documento NÃO DEVE inventá-la nem usar caminho local; a sugestão permanece não conforme a este perfil até que a URL seja fornecida.

    ### 6.4 Verificação segura da aquisição
    1. Analisar a URL com parser de URI, validar esquema e host e aplicar a política de rede antes de qualquer requisição.
    2. Fazer `HEAD` apenas como sondagem opcional; disponibilidade, tipo e integridade DEVEM ser confirmados por `GET`.
    3. Seguir quantidade limitada de redirecionamentos e revalidar esquema, host, DNS e endereço IP em cada salto.
    4. Rejeitar loop, redirecionamento para protocolo não HTTP(S), host local, endereço privado, link-local, multicast, reservado ou destino bloqueado pela política.
    5. Aplicar timeout, limite de bytes, limite de taxa, cancelamento e leitura em fluxo; corpo parcial ou truncado DEVE falhar.
    6. Identificar o conteúdo por assinatura e estrutura. Extensão e `Content-Type` são evidências auxiliares, nunca prova suficiente.
    7. Calcular os três hashes durante a leitura. Para PDF ou EPUB direto, os bytes recebidos DEVEM coincidir com a matriz de `global_hashes` do formato.
    8. Se a URL entregar invólucro admitido pelo processo editorial, extraí-lo em ambiente isolado e limitado; exatamente um artefato do formato declarado DEVE corresponder aos três Hashes Globais.
    9. Registrar diagnóstico, URL submetida, cadeia de redirecionamento, tamanho, tipo detectado e resultado dos hashes fora deste documento formativo.
    - `SIL-URL-NET-001` Êxito de `HEAD`, código HTTP, nome do arquivo ou `Content-Type` compatível NÃO DEVE bastar para aceitar uma URL.
    - `SIL-URL-NET-002` Resolução DNS DEVE ser reavaliada no momento da conexão para reduzir risco de DNS rebinding; validação apenas textual do hostname NÃO É suficiente.
    - `SIL-URL-NET-003` Falha de rede, bloqueio por política, resposta autenticada, conteúdo HTML, desafio interativo ou indisponibilidade DEVE produzir diagnóstico e impedir incorporação automática.
    - `SIL-URL-NET-004` O processo NÃO DEVE executar script, macro, mídia ativa nem conteúdo incorporado obtido pela URL.

    ### 6.5 Métodos recomendados

    #### 6.5.1 Node.js
    - Analisar com `URL` e aceitar somente `http:` ou `https:`.
    - Usar cliente HTTP com redirecionamento manual e limitado, resolução DNS validada, `AbortSignal` para timeout e limite incremental de bytes.
    - Ler `Response.body` como fluxo binário e alimentar simultaneamente `node:crypto.createHash("sha1")`, `createHash("sha256")` e `createHash("sha512")`.
    - Validar assinatura `%PDF-` e estrutura PDF com analisador próprio; para EPUB, validar contêiner ZIP OCF e o arquivo `mimetype`.
    - Não usar `arrayBuffer()` ou equivalente sem limite prévio quando a resposta puder ser grande.

    #### 6.5.2 Python
    - Analisar com `urllib.parse.urlsplit`, exigir esquema `http` ou `https`, `hostname` não vazio e `username`, `password` e `fragment` ausentes.
    - Usar cliente HTTP que permita controlar redirecionamentos, timeout, resolução de destino e leitura incremental; `requests` ou `httpx` PODE ser usado sob essas guardas.
    - Ler blocos binários e alimentar simultaneamente `hashlib.sha1()`, `hashlib.sha256()` e `hashlib.sha512()`.
    - Validar PDF com analisador próprio; validar EPUB com `zipfile` sob limites de entradas, tamanhos, razão de expansão e caminhos.
    - Não usar `response.content` ou equivalente sem limite prévio quando a resposta puder ser grande.

    #### 6.5.3 Neutralidade
    - Biblioteca ou cliente citado é recomendação operacional, não dependência normativa.
    - Implementação alternativa somente é conforme quando aplica as mesmas restrições de URI, rede, limites, detecção de formato e comparação dos três hashes.
    - Navegador PODE auxiliar a localizar a URL, mas inspeção manual, abertura bem-sucedida ou download visual NÃO substitui a validação binária reproduzível.

    ## 7. Extração específica por formato

    ### 7.1 EPUB
    - `SIL-EPUB-001` EPUB DEVE ser tratado como contêiner ZIP OCF não confiável.
    - `SIL-EPUB-002` Antes de ler conteúdo, o processo DEVE limitar quantidade de entradas, tamanho comprimido, tamanho expandido, razão de expansão, profundidade e comprimento de caminho.
    - `SIL-EPUB-003` Path absoluto, traversal, symlink, colisão após normalização e entidade XML externa DEVEM ser rejeitados.
    - `SIL-EPUB-004` O Package Document DEVE ser localizado pelo arquivo de contêiner e analisado com namespaces.
    - `SIL-EPUB-005` Título, idioma e colaboradores estruturados DEVEM ser confrontados com página de rosto e colofão na ordem de leitura definida pelo spine.
    - `SIL-EPUB-006` A ordem física das entradas compactadas NÃO DEVE ser tratada como ordem editorial.
    - `SIL-EPUB-007` Impressão textual usada apenas para comparar PDF e EPUB DEVE seguir o spine, excluir script, estilo e navegação repetitiva e normalizar Unicode e espaços em cópia derivada.

    ### 7.2 PDF
    - `SIL-PDF-001` PDF DEVE ser analisado por biblioteca que interprete objetos, xref, streams, fontes, páginas e metadados.
    - `SIL-PDF-002` Regex sobre bytes crus NÃO DEVE ser usada para extrair `book`.
    - `SIL-PDF-003` Página de rosto e colofão visíveis DEVEM prevalecer sobre metadado técnico conflitante.
    - `SIL-PDF-004` Extração de texto DEVE preservar número e ordem das páginas e registrar falha, página vazia e baixa densidade textual.
    - `SIL-PDF-005` OCR somente DEVE ser usado quando a camada textual for ausente ou insuficiente. Resultado de OCR é evidência derivada e NÃO DEVE substituir o original.
    - `SIL-PDF-006` PDF cifrado sem autorização de leitura, corrompido ou acima dos limites operacionais DEVE falhar com diagnóstico.

    ### 7.3 Associação entre PDF e EPUB
    - `SIL-MATCH-001` PDF e EPUB somente DEVEM integrar o mesmo documento quando título, autoria, idioma e identidade editorial forem compatíveis.
    - `SIL-MATCH-002` Comparação DEVERIA usar impressão textual derivada de amostras distribuídas na ordem editorial, nunca igualdade de hashes entre formatos.
    - `SIL-MATCH-003` Diferença de paginação, layout ou codificação NÃO implica obra distinta.
    - `SIL-MATCH-004` Diferença material de conteúdo, idioma, autoria ou edição DEVE impedir associação automática.
    - `SIL-MATCH-005` Confiança insuficiente DEVE encaminhar para revisão humana.

    ## 8. Validação integral
    1. Analisar JSON ou YAML em modo seguro.
    2. Confirmar que a raiz contém somente `book`, `urls` e `global_hashes`.
    3. Confirmar as seis chaves exatas de `book`.
    4. Confirmar `edition: {}` e a presença de `tags`, ainda que `[]`.
    5. Confirmar ao menos um contribuidor e ao menos um `author`.
    6. Confirmar duas chaves exatas em cada contribuidor.
    7. Validar título, nomes, papéis, idioma, categoria e tags.
    8. Confirmar `urls` não vazio e duas chaves exatas em cada item.
    9. Validar formato, sintaxe, segurança e unicidade de cada URL.
    10. Confirmar correspondência total entre os formatos de `urls` e `global_hashes`.
    11. Confirmar um ou dois itens em `global_hashes`, sem formato duplicado.
    12. Confirmar quatro chaves exatas em cada Hash Global.
    13. Obter cada variante, identificar seu formato e comparar os três hashes.
    14. Confirmar a associação editorial quando PDF e EPUB coexistirem.
    15. Serializar no outro formato, analisar novamente e exigir igualdade profunda.
    - `SIL-VAL-001` Falha DEVE indicar a propriedade, a regra violada e a evidência necessária, sem inventar valor substituto.
    - `SIL-VAL-002` Item inválido NÃO DEVE ser silenciosamente removido para fazer o documento parecer conforme.
    - `SIL-VAL-003` Documento somente é conforme quando todas as propriedades obrigatórias existem e nenhuma propriedade adicional existe.

    ## 9. Exemplos semanticamente equivalentes

    ### 9.1 JSON

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

    ### 9.2 YAML

    ```yaml
    book:
      title: "Atos Dos Apóstolos"
      contributors:
        - name: "Ellen G. White"
          role: "author"
      edition: {}
      language: "pt-br"
      primary_category: "livros"
      tags: []
    urls:
      - format: "pdf"
        url: "https://media2.egwwritings.org/pdf/pt_AA(AA).pdf"
      - format: "epub"
        url: "https://media2.egwwritings.org/epub/pt_AA(AA).epub"
    global_hashes:
      - format: "pdf"
        sha1: "ef605032eb4011e6f058c100dc845f414e36e4f4"
        sha256: "91e2d4ea3e74a3ec55ecd61fb659f57927ef90ae413ea699cd8b4e92c7d9051a"
        sha512: "75b0c5ffda1ae8314cae7612afc947393817581b9ac219db497d526ee90417841e16b0e5f3ab0f2421eb8201358502ba6f9628e62195b4c37437d0967748cb42"
      - format: "epub"
        sha1: "6df74abc8e2d57f82ff54a3b373d855c016f9f15"
        sha256: "46d2ed2d02977d96d625c6c0d2ad65de4f769cece56b2e45f64f65555f5eba29"
        sha512: "cc055518caab4bcf2399dde632359ab808b5dfeea2259e886b9f9af161eca7fea611d7658d11d42f1a68b4d3f54e57a25ff50e2a68d010c83bb8337d1e41ff80"
    ```

    - `SIL-EX-001` Os exemplos JSON e YAML DEVEM produzir estruturas profundamente iguais após parse seguro.
    - `SIL-EX-002` Os exemplos contêm todas e somente as propriedades autorizadas.

    ## 10. Referências técnicas
    - RCF local: [`../RCF.md`](../RCF.md), especialmente `RCF-IF-DATA-009..025` e `RCF-IF-HASH-001..006`.
    - JSON: [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259).
    - YAML: [YAML 1.2.2](https://yaml.org/spec/1.2.2/).
    - URI: [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986).
    - Idiomas: [BCP 47 / RFC 5646](https://www.rfc-editor.org/rfc/rfc5646).
    - EPUB: [EPUB 3.3](https://www.w3.org/TR/epub-33/).
    - Hash em Node.js: [`node:crypto`](https://nodejs.org/api/crypto.html).
    - URL em Node.js: [`URL`](https://nodejs.org/api/url.html#the-whatwg-url-api).
    - PDF em Node.js: [PDF.js API](https://mozilla.github.io/pdf.js/api/).
    - Hash em Python: [`hashlib`](https://docs.python.org/3/library/hashlib.html).
    - URL em Python: [`urllib.parse`](https://docs.python.org/3/library/urllib.parse.html).
    - EPUB em Python: [`zipfile`](https://docs.python.org/3/library/zipfile.html).
    - PDF em Python: [pypdf](https://pypdf.readthedocs.io/en/latest/user/extract-text.html) e [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/).

    Não existe vínculo com editoras; o projeto não responde pelo conteúdo de terceiros; atribuição, restrições e integridade permanecem obrigatórias.

- [ ] Reestruturar publicação, indexação e disponibilidade de assets

  ## Objetivo

  Reestruturar integralmente o armazenamento, download, publicação e indexação das publicações para que todo conteúdo relacionado ao mesmo título seja agrupado, normalizado e disponibilizado no GitHub Pages, independentemente de existir link ou botão para ele na página do produto.

  ## Requisitos

  ### 1. Publicação obrigatória

  Ao gerar a página do produto:
  - todas as publicações e seus assets associados DEVEM ser incluídos no artefato publicado;
  - os arquivos DEVEM permanecer acessíveis diretamente pelo domínio público do GitHub Pages;
  - a ausência de links, botões ou referências visuais na página NÃO DEVE impedir cópia, build, deploy ou acesso direto aos arquivos;
  - rotinas de otimização, tree-shaking, limpeza ou seleção de assets NÃO DEVEM remover arquivos pertencentes à estrutura de publicações.

  ### 2. Estrutura canônica

  Substituir a estrutura atual:

  ```text
  /publications/<acronimo-autor>/<language>/<tipo>/<titulo>.<extensao>
  ```

  pela estrutura:

  ```text
  /publications/<acronimo-autor>/<language>/<tipo>/<titulo>/
  ```

  Considerando:
  - origem local: `./src/publications/`;
  - raiz pública: `/publications/`;
  - `<tipo>` representa a classificação lógica da publicação, NÃO o formato físico do arquivo;
  - todos os arquivos relacionados ao mesmo título DEVEM permanecer no mesmo diretório, incluindo PDF, EPUB, metadados, capas e demais assets;
  - diferenças de extensão ou formato NÃO DEVEM criar diretórios distintos para o mesmo título.

  Exemplo:

  ```text
  ./src/publications/<acronimo-autor>/<language>/<tipo>/<titulo>/
  ├── <acronimo-titulo>.pdf
  ├── <acronimo-titulo>.epub
  ├── <acronimo-titulo>.json
  └── <demais-assets>
  ```

  URL pública correspondente:

  ```text
  /publications/<acronimo-autor>/<language>/<tipo>/<titulo>/<arquivo>
  ```

  ### 3. Migração do acervo existente

  Mover os arquivos atualmente existentes para a estrutura canônica, preservando integralmente:
  - conteúdo;
  - formatos;
  - metadados;
  - assets relacionados;
  - variantes legítimas;
  - URLs de origem;
  - hashes;
  - idiomas;
  - autores;
  - classificações;
  - rastreabilidade.

  A migração DEVE:
  1. identificar arquivos pertencentes ao mesmo título;
  2. normalizar o título;
  3. determinar seu acrônimo;
  4. criar o diretório canônico;
  5. mover todos os arquivos correlatos para esse diretório;
  6. renomear os arquivos conforme este TO-DO;
  7. atualizar referências, índices, metadados, scripts, testes e documentação afetados;
  8. validar que nenhum arquivo foi perdido, sobrescrito ou publicado em caminho incorreto.

  ### 4. Adequação do `baixar.py`

  O script `baixar.py` DEVE ser ajustado para:
  - baixar diretamente na estrutura canônica;
  - reutilizar diretório existente do mesmo título;
  - agrupar no mesmo diretório todos os formatos e assets relacionados;
  - normalizar título, tags e acrônimo antes de definir o destino;
  - impedir sobrescrita destrutiva;
  - preservar variantes com conteúdo distinto;
  - produzir resultado determinístico para entradas equivalentes;
  - gerar ou atualizar metadados e índices aplicáveis;
  - não recriar a estrutura legada.

  ### 5. Normalização dos nomes de arquivo

  Dentro do diretório de cada título, todo arquivo diretamente associado à publicação DEVE utilizar:

  ```text
  <acronimo-titulo>.<extensao>
  ```

  O acrônimo DEVE:
  - derivar exclusivamente do título normalizado;
  - ignorar tags removidas do título;
  - ser estável e determinístico;
  - utilizar a mesma regra em migração, download, indexação e publicação.

  Arquivos auxiliares cuja semântica exija sufixo adicional PODEM utilizar:

  ```text
  <acronimo-titulo>.<qualificador>.<extensao>
  ```

  desde que o qualificador seja determinístico, semanticamente necessário e não recrie o título completo de forma redundante.

  ### 6. Colisões e preservação de variantes

  Quando o nome de destino já existir:
  1. calcular ou obter o SHA-256 de ambos os arquivos;
  2. se os hashes forem iguais, tratar como duplicata idêntica, sem criar nova cópia;
  3. se os hashes forem diferentes, preservar ambos mediante variação mínima, estável e não destrutiva do nome.

  Formato preferencial:

  ```text
  <acronimo-titulo>.<extensao>
  <acronimo-titulo>.<hash-curto>.<extensao>
  ```

  O hash curto DEVE:
  - derivar do SHA-256 do próprio arquivo;
  - possuir comprimento suficiente para desambiguar os arquivos presentes no diretório;
  - ser expandido apenas em caso de colisão do próprio prefixo;
  - permitir rastrear inequivocamente o arquivo ao hash integral registrado.

  É PROIBIDO:
  - sobrescrever arquivo de hash diferente;
  - descartar silenciosamente uma variante;
  - usar contador dependente da ordem de execução quando houver identificador determinístico disponível.

  ### 7. Tags incorporadas ao nome

  Trechos entre parênteses presentes no nome de alguns títulos DEVEM ser avaliados como tags, qualificadores ou atributos, e não automaticamente como parte do título bibliográfico.

  Quando confirmados como tag:
  - DEVEM ser removidos do título canônico;
  - NÃO DEVEM integrar `<titulo>`;
  - NÃO DEVEM integrar `<acronimo-titulo>`;
  - DEVEM ser normalizados e transferidos ao JSON indexador global apropriado;
  - DEVEM permanecer associados à publicação correspondente;
  - sua remoção NÃO DEVE causar perda semântica nem colisão não tratada.

  Parênteses que façam parte legítima do título NÃO DEVEM ser removidos por regra cega. A implementação DEVE utilizar metadados disponíveis e critérios determinísticos; caso não seja possível decidir com segurança, DEVE preservar o valor e registrar a necessidade de revisão, sem convertê-lo silenciosamente em tag.

  ### 8. Metadados locais

  Cada diretório de título DEVE preservar e associar corretamente seus arquivos de metadados.

  Os metadados existentes podem, mas não necessariamente DEVEM, seguir o padrão:

  ```text
  <nome-publicacao>.source.json
  ```

  A implementação NÃO DEVE depender exclusivamente do nome do arquivo para identificar metadados. DEVE inspecionar estrutura, campos e associação com a publicação.

  Quando aplicável, os metadados DEVEM ser normalizados para nome aderente ao acrônimo, sem perda de conteúdo:

  ```text
  <acronimo-titulo>.source.json
  ```

  ### 9. JSON indexador global

  O JSON indexador global DEVE ser gerado ou atualizado prioritariamente a partir dos metadados locais de cada publicação.

  Para cada origem e formato disponível, incorporar:
  - URL pública direta do arquivo publicado;
  - URL original da fonte;
  - SHA-256 já calculado;
  - formato;
  - idioma;
  - autor;
  - tipo;
  - título normalizado;
  - acrônimo do título;
  - tags extraídas;
  - demais metadados existentes e aplicáveis.

  As URLs originais e seus respectivos hashes, normalmente presentes nos arquivos `*.source.json`, DEVEM ser adicionados às URLs diretas já previstas no indexador global, sem substituí-las.

  A composição, estrutura e semântica dessas origens DEVEM obedecer ao normativo anteriormente definido na TO-DO anexada:

  ```text
  NORMA-IF-SIL-001
  ```

  Antes de alterar o indexador, a implementação DEVE localizar e ler integralmente `NORMA-IF-SIL-001`. É PROIBIDO presumir sua estrutura, reproduzi-la por memória ou criar contrato incompatível. Em caso de conflito, aplicar a precedência documental vigente e registrar a decisão.

  ### 10. Build e GitHub Pages

  A cadeia de build/deploy DEVE:
  - copiar integralmente `./src/publications/` para `/publications/` no artefato público;
  - preservar diretórios, arquivos, extensões e nomes;
  - não exigir importação por código para publicar os arquivos;
  - não depender de referências na página do produto;
  - manter URLs estáveis e diretamente acessíveis;
  - detectar arquivos ausentes, caminhos inválidos e colisões;
  - falhar de forma explícita quando houver perda, sobrescrita ou inconsistência estrutural.

  ### 11. Compatibilidade e referências

  Atualizar todas as referências afetadas, incluindo, quando existentes:
  - página do produto;
  - geradores;
  - scripts;
  - indexadores;
  - manifestos;
  - JSONs;
  - testes;
  - documentação;
  - rotinas de download;
  - validações;
  - workflows;
  - caminhos públicos;
  - URLs internas e externas.

  Compatibilidade temporária com caminhos antigos somente PODE ser mantida quando já houver URLs públicas consumidas externamente. Nesse caso, a solução DEVE privilegiar redirecionamento, alias ou mapa de compatibilidade, sem duplicação indefinida do acervo.

  ### 12. Normatização no RCF

  Todo o comportamento definido neste TO-DO DEVE ser incorporado ao RCF aplicável como norma permanente, incluindo:
  - estrutura canônica;
  - agrupamento por título;
  - nomenclatura;
  - acrônimos;
  - tratamento de tags;
  - colisões;
  - hashes;
  - metadados;
  - indexação;
  - publicação;
  - disponibilidade direta;
  - migração;
  - validação;
  - precedência de `NORMA-IF-SIL-001`.

  O RCF NÃO DEVE apenas referenciar este TO-DO como fonte transitória. DEVE absorver integralmente suas regras, reconciliá-las com normas vigentes e remover ambiguidades ou contradições.

  ## Ordem de execução
  1. Ler normas aplicáveis, incluindo `NORMA-IF-SIL-001`.
  2. Inspecionar estrutura, acervo, `baixar.py`, indexadores, build e deploy reais.
  3. Mapear títulos, formatos, metadados, tags, hashes e colisões.
  4. Definir regras determinísticas de normalização e acrônimos aderentes ao projeto.
  5. Implementar migração segura e idempotente.
  6. Migrar os arquivos existentes.
  7. Ajustar `baixar.py`.
  8. Atualizar o JSON indexador global.
  9. Atualizar build, deploy e referências.
  10. Incorporar as regras ao RCF.
  11. Executar validações completas.
  12. Emitir relatório final.

  ## Critérios de aceite
  - [ ] Todas as publicações estão sob a estrutura canônica.
  - [ ] Cada título possui diretório próprio.
  - [ ] PDF, EPUB, metadados e assets do mesmo título estão agrupados.
  - [ ] Arquivos utilizam o acrônimo normalizado do título.
  - [ ] Tags válidas foram removidas do título e registradas no índice.
  - [ ] Parênteses legítimos não foram removidos indevidamente.
  - [ ] Duplicatas idênticas não foram replicadas.
  - [ ] Arquivos homônimos com hashes distintos foram preservados.
  - [ ] Nenhum arquivo foi perdido ou sobrescrito.
  - [ ] `baixar.py` gera apenas a nova estrutura.
  - [ ] Metadados locais são associados por conteúdo, não apenas pelo nome.
  - [ ] URLs originais e SHA-256 foram incorporados ao indexador global.
  - [ ] URLs públicas diretas permanecem no indexador.
  - [ ] O índice está aderente à `NORMA-IF-SIL-001`.
  - [ ] O build publica todo o conteúdo, mesmo sem links na interface.
  - [ ] Cada arquivo é acessível diretamente no GitHub Pages.
  - [ ] Referências internas e documentação foram atualizadas.
  - [ ] As regras foram integralmente normatizadas no RCF.
  - [ ] Testes e validações passam sem regressão.

  ## Relatório final

  Registrar objetivamente:
  - arquivos criados, movidos, renomeados, deduplicados ou preservados como variantes;
  - regra aplicada para título, tag e acrônimo;
  - colisões e respectivos hashes;
  - alterações no `baixar.py`;
  - alterações no indexador global;
  - aderência à `NORMA-IF-SIL-001`;
  - alterações no build/deploy;
  - URLs públicas validadas;
  - testes executados e resultados;
  - pendências ou ambiguidades que não puderam ser resolvidas sem inventar regras.

- [ ] **Estender a pesquisa para pesquisa assistida e conversa probatória com o acervo:** ampliar o recurso de pesquisa já normatizado no RCF para permitir interação conversacional com as publicações, sem substituir, reduzir, enfraquecer ou descaracterizar os mecanismos, especializações, critérios de relevância, pesquisa avançada, força normativa ou demais capacidades já existentes. A extensão DEVE oferecer modos distintos de atuação, preservar o rigor documental e materializar toda argumentação relevante mediante citações exatas, íntegras, verificáveis e contextualizadas das fontes.
  - [ ] **Preservar o recurso vigente:** inspecionar integralmente o RCF atual e identificar os contratos, mecanismos, especializações, fluxos, critérios e restrições já normatizados para pesquisa. A implementação DEVE estendê-los por composição e especialização; NÃO DEVE removê-los, substituí-los por uma interface conversacional genérica, reduzir sua precisão nem reinterpretar requisitos vigentes como opcionais.

  - [ ] **Modos explícitos de atuação:** permitir que o usuário selecione, de forma inequívoca, ao menos:
    1. **Modo Pesquisa:** pesquisa documental avançada, híbrida e não conversacional;
    2. **Modo Conversa:** diálogo interpretativo, argumentativo e obrigatoriamente fundamentado no acervo.

    A seleção DEVE controlar comportamento, apresentação, profundidade, encadeamento e critérios de resposta. Os modos PODEM compartilhar indexação, recuperação, reranqueamento, interpretação e infraestrutura, mas NÃO DEVEM ser semanticamente confundidos.

  - [ ] **Modo Pesquisa:** preservar integralmente a pesquisa avançada já normatizada, incluindo seus mecanismos híbridos, especializações, filtros, estratégias de recuperação, critérios de relevância, rastreabilidade e formatos de resultado. LLMs PODEM auxiliar expansão de consulta, desambiguação, classificação, reranqueamento, síntese, conexão semântica ou outras etapas quando houver ganho demonstrável de qualidade ou desempenho; contudo:
    - a LLMs e análogos SÃO desejáveis como meios de otimizar (se e quando houver ganho líquido) mas NÃO exigidos;
    - a experiência final DEVE permanecer caracterizada como pesquisa, não conversa;
    - o uso de LLM NÃO DEVE substituir mecanismos determinísticos ou especializados quando estes forem mais adequados;
    - resultados, evidências e referências DEVEM permanecer verificáveis;
    - otimização por LLM NÃO DEVE reduzir cobertura, precisão, auditabilidade ou força normativa já estabelecida;
    - a indisponibilidade ou inadequação do LLM NÃO DEVE inutilizar a pesquisa quando houver mecanismo alternativo aplicável.

  - [ ] **Modo Conversa:** permitir conversa fluida, contextual e iterativa com o acervo, mantendo memória controlada do diálogo e capacidade de aprofundar, comparar, interpretar, relacionar e questionar múltiplas publicações. A IA NÃO DEVE apenas falar em nome das fontes ou apresentar paráfrases desacompanhadas de prova; DEVE explicar o conteúdo e sustentar materialmente seus argumentos mediante o próprio conteúdo documental recuperado.

  - [ ] **Argumentação probatória:** toda afirmação material atribuída ao acervo DEVE ser acompanhada, na granularidade adequada, por evidência documental suficiente para comprovar seu mérito. A resposta DEVE combinar:
    - interpretação da IA;
    - rigor lógico e acadêmico;
    - exposição fluida e proporcional ao usuário;
    - citações literais exatas;
    - referências completas;
    - distinção inequívoca entre conteúdo da fonte, interpretação, inferência, comparação e conclusão da IA.

    A fluidez NÃO PODE ocultar a origem das afirmações, substituir prova por autoridade aparente nem transformar interpretação em texto atribuído à publicação.

  - [ ] **Citações íntegras e pontuais:** as citações DEVEM:
    - reproduzir fielmente o trecho original, sem reconstrução, complementação ou alteração semântica;
    - conter extensão suficiente para preservar contexto e inteligibilidade;
    - evitar fragmentos truncados que distorçam condicionantes, exceções, negações ou conclusão;
    - apontar precisamente para publicação, edição ou versão, autor ou entidade, título, idioma, formato e localização interna disponível;
    - incluir, conforme o formato, página, seção, capítulo, artigo, item, parágrafo, posição, âncora, intervalo ou identificador equivalente;
    - permitir que o usuário localize e confira a passagem;
    - permanecer associadas à proposição que efetivamente sustentam;
    - diferenciar citação direta, paráfrase e inferência;
    - preservar o texto original mesmo quando acompanhadas de tradução.

  - [ ] **Referência completa:** cada fonte utilizada DEVE possuir referência bibliográfica ou documental completa conforme os metadados disponíveis, incluindo, quando aplicável:
    - autor, órgão, entidade ou responsável;
    - título;
    - subtítulo;
    - edição, versão ou revisão;
    - data;
    - editora, órgão emissor ou repositório;
    - idioma;
    - tipo e formato;
    - identificador persistente;
    - URL pública direta e URL de origem;
    - data de acesso quando pertinente;
    - SHA-256 ou outro identificador de integridade normatizado;
    - localização exata do trecho citado.

    Ausência de metadado NÃO DEVE ser preenchida por invenção. Campos indisponíveis DEVEM ser omitidos ou explicitamente identificados como não determinados, conforme o contrato de saída aplicável.

  - [ ] **Tradução vinculada ao original:** quando a fonte estiver em idioma diferente do utilizado na conversa:
    - a citação original DEVE ser preservada;
    - tradução PODE ser adicionada imediatamente associada ao trecho original;
    - a tradução DEVE ser identificada como tradução;
    - ambiguidades, termos técnicos, jurídicos, normativos ou semanticamente sensíveis DEVEM preservar também o termo original;
    - a tradução NÃO DEVE substituir o original como prova;
    - divergências relevantes entre traduções existentes DEVEM ser explicitadas;
    - a IA NÃO DEVE atribuir à fonte formulação existente apenas na tradução interpretativa.

  - [ ] **Contexto suficiente da prova:** quando um trecho isolado não for suficiente para sustentar corretamente a afirmação, o sistema DEVE recuperar e apresentar o contexto necessário, incluindo definições, premissas, exceções, notas, parágrafos anteriores ou posteriores, referências internas e demais passagens correlatas. É PROIBIDO utilizar citação formalmente correta, porém materialmente enganosa por descontextualização.

  - [ ] **Pesquisa profunda e multifuente:** o modo Conversa DEVE poder executar pesquisa profunda antes de responder, inclusive:
    - decompor perguntas complexas;
    - localizar conceitos expressos com terminologias distintas;
    - relacionar partes distantes da mesma publicação;
    - cruzar múltiplas publicações;
    - identificar convergências, divergências, evolução, dependência ou conflito;
    - distinguir fontes primárias, secundárias, normativas, interpretativas e históricas;
    - comparar versões, revisões ou edições;
    - recuperar fundamentos e não apenas trechos lexicalmente semelhantes;
    - revisar a suficiência das evidências antes da resposta.

    A pesquisa profunda DEVE ser proporcional à complexidade da pergunta e NÃO DEVE ser simulada mediante resposta baseada apenas nos primeiros fragmentos recuperados.

  - [ ] **Relações entre publicações:** ao conectar fontes, a IA DEVE explicitar o tipo de relação identificado, como confirmação, complementação, especialização, divergência, revogação, dependência, evolução histórica, aplicação, interpretação ou analogia. Relações inferidas DEVEM ser identificadas como inferências e sustentadas por evidências próprias; NÃO DEVEM ser apresentadas como vínculo declarado pelas fontes quando não o forem.

  - [ ] **Publicações técnicas, normativas, governamentais e legais:** o mecanismo DEVE suportar com rigor especial documentos cuja interpretação dependa de hierarquia, vigência, competência, versão, escopo, definições e referências internas, sem limitar o recurso a essas categorias. Nesses casos, DEVE:
    - privilegiar fontes primárias quando disponíveis;
    - distinguir texto normativo de explicação, parecer, jurisprudência, doutrina, manual ou comentário;
    - preservar verbos normativos, condições, exceções e remissões;
    - identificar versão, vigência e jurisdição quando os metadados permitirem;
    - evitar conclusão categórica quando a fonte não a sustentar;
    - sinalizar conflitos, revogações, alterações ou incertezas documentais detectadas.

  - [ ] **Separação entre prova e síntese:** a resposta conversacional DEVE possuir associação clara entre:
    - **afirmação:** o que está sendo explicado ou defendido;
    - **evidência:** o trecho literal que a sustenta;
    - **referência:** a identificação e localização completas da fonte;
    - **interpretação:** a explicação produzida pela IA;
    - **inferência:** conclusão derivada, mas não expressamente declarada pela fonte.

    Essa estrutura PODE ser apresentada de forma visualmente fluida, sem obrigar formato enfadonho, repetitivo ou excessivamente acadêmico quando a complexidade não o exigir. A simplificação visual NÃO DEVE reduzir verificabilidade.

  - [ ] **Cobertura e suficiência:** antes de concluir, a IA DEVE avaliar se:
    - as fontes recuperadas são pertinentes e suficientes;
    - cada argumento relevante possui prova;
    - existem passagens contraditórias ou qualificadoras;
    - a resposta depende de fonte não localizada;
    - a conclusão excede o conteúdo disponível;
    - as citações preservam contexto e integridade.

    Quando a prova for insuficiente, a resposta DEVE declarar a limitação e NÃO DEVE preencher a lacuna com aparente segurança.

  - [ ] **Controle de alucinação e fidelidade:** a implementação DEVE impedir ou detectar:
    - citações inexistentes;
    - referências fabricadas;
    - páginas ou seções incorretas;
    - combinação de trechos de fontes distintas como se fossem um único excerto;
    - alteração silenciosa de texto citado;
    - atribuição equivocada;
    - paráfrase apresentada como citação;
    - tradução apresentada como original;
    - conclusão não suportada;
    - omissão de exceção material;
    - uso de fragmento sem contexto suficiente.

    Nenhuma resposta DEVE apresentar citação ou localização cuja existência não tenha sido verificada no conteúdo efetivamente indexado ou acessível.

  - [ ] **Granularidade adaptativa:** quantidade, extensão e detalhamento das citações DEVEM ser proporcionais ao risco, complexidade e finalidade da resposta. Perguntas simples PODEM receber prova concisa; comparações, controvérsias, interpretações normativas ou argumentos complexos DEVEM receber fundamentação ampliada. O sistema NÃO DEVE despejar citações extensas sem função, nem reduzir evidência a fragmentos incapazes de comprovação.

  - [ ] **Experiência conversacional:** o modo Conversa DEVE permanecer natural e útil, permitindo perguntas subsequentes, pedidos de aprofundamento, contestação, comparação, mudança de recorte e solicitação de novas provas. A IA DEVE reutilizar contexto válido sem perder o vínculo documental de cada afirmação e DEVE refazer a recuperação quando a nova pergunta exigir evidência distinta.

  - [ ] **Rastreabilidade da sessão:** registrar, conforme as normas de privacidade, contexto e retenção aplicáveis:
    - consulta original e decomposições relevantes;
    - modo selecionado;
    - filtros e recortes;
    - publicações consultadas;
    - trechos utilizados;
    - referências emitidas;
    - traduções geradas;
    - relações e inferências relevantes;
    - limitações ou falhas de recuperação.

    O registro DEVE permitir auditoria e reprodução proporcional da resposta, sem exigir exposição de raciocínio interno privado da IA.

  - [ ] **Desempenho e arquitetura:** selecionar mecanismos de recuperação, indexação, busca lexical, semântica, híbrida, reranqueamento, expansão, leitura contextual e geração conforme aplicabilidade e estado real do projeto. A implementação NÃO DEVE impor LLM a todas as etapas nem degradar pesquisas simples. Cache, pré-processamento, índices especializados e execução local ou remota DEVEM seguir o RCF vigente e ser combinados para maximizar precisão, latência, custo e disponibilidade sem sacrificar fidelidade.

  - [ ] **Degradação controlada:** quando LLM, tradutor, reranqueador ou outro componente avançado estiver indisponível:
    - o Modo Pesquisa DEVE preservar as capacidades não dependentes desse componente;
    - o Modo Conversa PODE limitar síntese ou interpretação, mas NÃO DEVE fabricar respostas;
    - citações e referências somente DEVEM ser emitidas quando verificadas;
    - a interface DEVE informar objetivamente a limitação aplicável;
    - mecanismos alternativos DEVEM ser utilizados quando previstos e seguros.

  - [ ] **Interface e apresentação:** projetar a seleção de modo e a apresentação das respostas de forma inequívoca, permitindo ao usuário:
    - alternar entre Pesquisa e Conversa;
    - distinguir resultado recuperado de síntese da IA;
    - abrir a publicação na localização citada, quando tecnicamente suportado;
    - consultar referência completa;
    - visualizar original e tradução;
    - expandir contexto adjacente;
    - identificar quais afirmações cada citação sustenta;
    - solicitar mais evidências ou aprofundamento;
    - copiar referência e citação sem perda de integridade.

  - [ ] **Normatização no RCF:** incorporar integralmente esta extensão ao RCF canônico, reconciliando-a com o recurso de pesquisa vigente e centralizando regras comuns de recuperação, evidência, referência, tradução, rastreabilidade e validação. O RCF DEVE distinguir claramente:
    - contratos comuns aos dois modos;
    - requisitos exclusivos do Modo Pesquisa;
    - requisitos exclusivos do Modo Conversa;
    - uso opcional e condicionado de LLMs;
    - critérios de prova, fidelidade e suficiência;
    - degradação e tratamento de falhas.

    É PROIBIDO criar uma especificação paralela que duplique, contradiga ou enfraqueça a normatização atual.

  - [ ] **Planejamento por FTs:** após inspeção do estado real e normatização, decompor a implementação em FTs rastreáveis conforme unidades materiais, incluindo, quando aplicável:
    - extensão dos índices e metadados;
    - recuperação híbrida e profunda;
    - extração e validação de citações;
    - localização interna por formato;
    - tradução vinculada;
    - composição argumentativa;
    - interface dos modos;
    - rastreabilidade;
    - testes de fidelidade;
    - desempenho e degradação.

    FTs NÃO DEVEM ser criadas artificialmente por camada quando uma unidade coesa produzir melhor execução, nem fundidas quando responsabilidades ou critérios de aceite forem materialmente distintos.

  - [ ] **Validação:** criar testes determinísticos e conjuntos de avaliação que verifiquem, no mínimo:
    - preservação integral do Modo Pesquisa atual;
    - distinção funcional entre os modos;
    - precisão de recuperação;
    - fidelidade literal das citações;
    - validade das localizações;
    - completude das referências;
    - preservação de contexto;
    - associação entre afirmação e prova;
    - distinção entre fonte, tradução, interpretação e inferência;
    - tratamento de múltiplas fontes;
    - detecção de contradições;
    - ausência de citações fabricadas;
    - comportamento com metadados incompletos;
    - degradação sem LLM ou componentes auxiliares;
    - desempenho proporcional à profundidade solicitada.

  - [ ] **Critérios de aceite:**
    - [ ] O recurso de pesquisa vigente permanece integralmente preservado.
    - [ ] O usuário pode selecionar explicitamente Pesquisa ou Conversa.
    - [ ] O Modo Pesquisa continua não conversacional e utiliza os melhores mecanismos aplicáveis já normatizados.
    - [ ] LLMs são usadas apenas quando agregam valor e não como substituição obrigatória da pesquisa.
    - [ ] O Modo Conversa interpreta, conecta e argumenta com base no acervo.
    - [ ] Afirmações materiais são acompanhadas de citações exatas e referências completas.
    - [ ] As citações preservam contexto, condicionantes, exceções e integridade.
    - [ ] Fontes em outro idioma exibem original e, quando necessário, tradução identificada.
    - [ ] O usuário pode verificar a origem e a localização de cada prova.
    - [ ] Conteúdo da fonte, interpretação e inferência permanecem distinguíveis.
    - [ ] Relações entre múltiplas publicações são identificadas e fundamentadas.
    - [ ] Documentos técnicos, normativos, governamentais e legais recebem tratamento compatível com sua natureza.
    - [ ] Citações, referências, localizações e atribuições inexistentes são impedidas ou detectadas.
    - [ ] Limitações de prova são declaradas sem fabricação de resposta.
    - [ ] A apresentação mantém rigor acadêmico e lógico sem prolixidade ou rigidez desnecessária.
    - [ ] A extensão foi integralmente incorporada ao RCF sem duplicar ou enfraquecer normas vigentes.

  - [ ] **Relatório final:** registrar:
    - normas do recurso anterior preservadas ou especializadas;
    - alterações realizadas no RCF;
    - arquitetura e mecanismos efetivamente adotados;
    - diferenças funcionais entre os modos;
    - critérios de seleção e uso de LLMs;
    - modelo de citações, referências e traduções;
    - mecanismos de validação e prevenção de alucinações;
    - FTs criadas e vínculos;
    - testes e conjuntos de avaliação executados;
    - métricas de precisão, fidelidade, cobertura, latência e custo disponíveis;
    - limitações, pendências e riscos remanescentes.

- [ ] Corrigir o tratamento de desafios anti-bot com intervenção humana real

  ## Objetivo e limites

  Corrigir o fluxo que detecta desafios anti-bot, exibe o navegador e transfere a resolução ao operador, mas continua sendo recusado — sobretudo e especialmente por proteções Cloudflare.

  Diante de desafio incompatível com automação legítima, o sistema DEVE suspender integralmente a automação, entregar o controle a uma sessão humana adequada e somente retomar após comprovação objetiva de acesso autorizado.

  Tendo em vista o faldo positivo, e objetivando a continuidade do acesso legítimo da resolução humana:
  - Esta tarefa AUTORIZA EXPRESSAMENTE implementar mecanismo que permitam burlar, enfraquecer, ocultar, enganar ou neutralizar mecanismos de segurança que estão identificando falso positivio, EXCLUSIVAMENTE com o fim de D:
    - respeitar autorização, termos de uso, políticas do serviço e canais oficiais disponíveis, ou seja, GARANTINDO que um HUMANO e, JAMAIS um bot, seja capaz de resolver e e transpor mecanismos anti bot.

  APIs, autenticação, feeds, exportações e integrações oficiais DEVEM ser preferidos quando disponíveis.

  ## Problema e hipótese

  O fluxo atual detecta ou alcança o desafio, abre uma janela visível e permite interação humana, mas a sessão permanece classificada como automatizada ou não confiável.

  A hipótese de que a intervenção ocorra em sessão ainda criada, instrumentada ou controlada por automação DEVE ser investigada, porém NÃO PODE ser tratada como causa confirmada sem evidência reproduzível.

  ## Inspeção obrigatória

  Antes de alterar o código, a IA executora DEVE:
  - ler os normativos aplicáveis;
  - localizar todo código de navegador, automação, sessão, perfil, cookies, storage, CAPTCHA, Cloudflare, retries, timeout e retomada;
  - identificar a tecnologia real usada, como Playwright, Puppeteer, Selenium, WebDriver, CDP ou equivalente;
  - mapear criação, controle, pausa, handoff e retomada da sessão;
  - verificar se o navegador continua anexado ao controlador e se timers, filas, polling, scripts, recargas, navegações ou eventos permanecem ativos durante a intervenção;
  - verificar se a sessão é persistente ou descartável, se o estado validado é realmente reutilizado e se cookies, storage, headers, perfil e origem são preservados legitimamente;
  - identificar timeouts, redirecionamentos, reloads ou retries capazes de invalidar a resolução;
  - registrar evidências reproduzíveis sem expor dados sensíveis.

  ## Contrato central do fluxo

  A lógica comum de detecção, suspensão, handoff, preservação de estado, retomada, retry, timeout, cancelamento, logging e segurança DEVE ser centralizada e reutilizada por todos os submódulos. É PROIBIDA correção isolada por site quando o comportamento for comum.

  Especializações locais somente PODEM declarar padrões próprios de detecção, estado esperado, autenticação legítima, timeout humano, política de retomada e integração oficial do serviço.

  ### 1. Detecção

  O sistema DEVE reconhecer conservadoramente challenge page, CAPTCHA, intersticial, bloqueio por automação, resposta ou navegação incompatível, loop de redirecionamento e espera que exija ação humana.

  A detecção NÃO DEVE interagir automaticamente com o desafio.

  ### 2. Suspensão

  Ao detectar desafio:
  - toda automação DEVE cessar, inclusive filas, timers, polling, cliques, preenchimentos, scripts, reloads e navegações;
  - o estado DEVE mudar para `AGUARDANDO_INTERVENCAO_HUMANA` ou equivalente;
  - automação e operador NÃO PODEM atuar simultaneamente;
  - o operador DEVE receber instrução objetiva;
  - NÃO DEVE existir timeout curto incompatível com intervenção humana;
  - a página e a sessão NÃO DEVEM ser reiniciadas ou recarregadas sem consentimento.

  ### 3. Handoff humano

  A implementação DEVE avaliar, conforme a arquitetura real e nesta ordem preferencial:
  1. navegador normal já instalado e operado diretamente pelo usuário;
  2. perfil humano autorizado e persistente, sem automação ativa;
  3. autenticação ou verificação concluída fora do contexto automatizado;
  4. callback, handoff, importação autorizada de estado ou reabertura legítima da sessão;
  5. em domínio próprio, integração oficial do provedor.

  Janela visível ainda criada, instrumentada ou controlada por automação NÃO DEVE ser presumida como sessão humana válida. A solução DEVE resultar de inspeção e testes e NÃO PODE prometer aceitação por terceiros.

  ### 4. Preservação de estado

  Quando autorizada e tecnicamente compatível, a continuidade PODE preservar o estado obtido pela intervenção humana, desde que:
  - restrito ao domínio, usuário, perfil e finalidade aplicáveis;
  - armazenado com proteção, escopo e expiração adequados;
  - nunca exposto integralmente em logs;
  - invalidado em erro, expiração, corrupção ou mudança de identidade;
  - separado entre perfis, usuários e submódulos;
  - não convertido de token temporário em autorização permanente.

  Cookies, tokens, `localStorage`, `sessionStorage` ou perfis NÃO DEVEM ser copiados entre contextos sem compatibilidade comprovada exceto se, e SOMENTE se HOUVER justificativa técnica plausível e mediante autorização explicita.

  ### 5. Retomada

  A automação somente PODE retomar após verificar objetivamente:
  - ausência do desafio;
  - origem, página, recurso e estado esperados;
  - inexistência de loop ou novo bloqueio;
  - validade da sessão e identidade correta, quando aplicável.

  Clique humano isolado NÃO comprova liberação.

  Persistindo o bloqueio, o sistema DEVE manter a suspensão, informar a recusa, permitir cancelamento seguro, registrar diagnóstico conciso e impedir novas tentativas ilimitadas.

  ## Cloudflare e domínio

  Para domínio de terceiro, o sistema DEVE respeitar a decisão do provedor, preferir API ou acesso autorizado e tratar bloqueio persistente como impedimento legítimo, sem evasão.

  Para domínio controlado pelo projeto, DEVEM ser avaliados mecanismos oficiais, conforme aplicabilidade:
  - regras de segurança adequadas;
  - allowlists mínimas e justificadas;
  - Service Tokens ou equivalente para automação autorizada;
  - Turnstile com verificação server-side;
  - rotas ou ambientes próprios para automação interna;
  - políticas por identidade autenticada, origem ou serviço.

  Toda exceção DEVE ser mínima, auditável, revogável e restrita ao sistema autorizado. É PROIBIDO desabilitar proteção amplamente para facilitar automação ou testes.

  ## Resiliência, segurança e observabilidade

  O fluxo DEVE ser idempotente, cancelável e retomável; impedir concorrência, múltiplas janelas para o mesmo desafio, perda de estado, recarga durante a intervenção e retries ilimitados; distinguir falha de rede, autenticação, desafio e bloqueio definitivo; registrar transições; preservar compatibilidade com os submódulos.

  Registrar, sem dados sensíveis:
  - instante, origem e tipo provável do desafio;
  - estado anterior e suspensão efetiva;
  - início, fim e método do handoff;
  - resultado da validação, motivo de falha, tentativas e estado final.

  É PROIBIDO registrar senhas, respostas de CAPTCHA, cookies ou tokens integrais, conteúdo sensível de formulários, dados pessoais desnecessários ou material reutilizável para acesso.

  ## Testes obrigatórios

  Validar, conforme aplicabilidade:
  - detecção sem interação automática;
  - suspensão integral e ausência de concorrência;
  - cancelamento;
  - sessão aceita, recusada, expirada ou desafiada novamente;
  - retomada legítima na sessão validada e bloqueio de retomada inválida;
  - ausência de loops e isolamento entre usuários e submódulos;
  - ausência de segredos nos logs;
  - execução local e demais ambientes suportados;
  - fallback oficial disponível;
  - tratamento distinto para domínio próprio e de terceiro.

  Testes NÃO DEVEM atacar, sobrecarregar ou tentar evadir serviços externos. DEVEM preferir fixtures, mocks, ambiente controlado ou domínio próprio.

  ## Ordem de execução
  1. Ler os normativos e mapear integralmente o fluxo atual.
  2. Reproduzir a falha de forma controlada e autorizada.
  3. Confirmar o estado real da automação durante a intervenção e a causa raiz.
  4. Classificar o domínio e verificar integrações oficiais.
  5. Definir e implementar o contrato central de detecção, suspensão, handoff, preservação e retomada.
  6. Eliminar concorrência, loops e retries inadequados.
  7. Migrar todos os submódulos aplicáveis.
  8. Adicionar observabilidade e testes regressivos.
  9. Atualizar documentação e rastreabilidade.
  10. Emitir relatório final.

  ## Critérios de aceite

  A tarefa somente estará concluída quando:
  - desafios forem detectados sem tentativa automática de resolução;
  - a automação cessar integralmente antes da intervenção;
  - o operador atuar sem concorrência em sessão humana adequada;
  - a retomada depender de validação objetiva;
  - bloqueios persistentes não gerarem loop, evasão ou mascaramento;
  - integrações oficiais forem preferidas e domínios próprios e terceiros forem tratados distintamente;
  - sessões, tokens e dados sensíveis forem isolados e protegidos;
  - a lógica estiver centralizada e adotada por todos os submódulos aplicáveis;
  - testes cobrirem sucesso, falha, cancelamento, expiração e reapresentação do desafio;
  - nenhuma técnica de stealth, spoofing ou bypass tiver sido introduzida.

  ## Relatório final

  Registrar causa raiz, tecnologias e fluxos inspecionados, estado da automação antes e depois, estratégia de handoff, preservação ou descarte do estado, integrações oficiais, diferenças por domínio, arquivos e submódulos alterados, testes e resultados, limitações externas e comprovação de inexistência de evasão.

- [ ] Centralizar e excluir do Git caches, sessões e arquivos temporários

  ## Objetivo

  Identificar, classificar, centralizar e excluir do versionamento todo estado de runtime não canônico: caches, sessões, perfis de navegador, cookies e storages persistidos, autenticação transitória, locks, sockets, PIDs, temporários, downloads intermediários, traces, screenshots, dumps, logs e relatórios efêmeros, filas, checkpoints e equivalentes.

  Quando tecnicamente possível, esses dados DEVEM convergir para um único `<RUNTIME_STATE_DIR>` claramente identificado. Código, configuração, schema, fixture deliberada e demais fontes canônicas NÃO DEVEM ser movidos ou ignorados indevidamente.

  ## Princípios
  - fonte canônica e estado de execução DEVEM permanecer separados;
  - estado local ou sensível NÃO DEVE integrar Git, build, release, bundle ou publicação;
  - o projeto DEVE funcionar após clone limpo e sem arquivos locais preexistentes;
  - a reorganização NÃO DEVE quebrar autenticação, retomada, intervenção humana, testes, builds ou submódulos;
  - migrações DEVEM ser mínimas, seguras, idempotentes e rastreáveis.

  ## Inspeção e classificação

  Antes de criar, mover, excluir ou ignorar arquivos, a implementação DEVE:
  - ler os normativos e inspecionar a estrutura real;
  - localizar produtores e consumidores de cache, sessão, perfil, cookies, storage, temporários, locks, traces, downloads e equivalentes;
  - localizar paths hardcoded, variáveis, defaults, scripts, workflows, testes, containers, releases e documentação dependentes;
  - verificar `.gitignore`, `.git/info/exclude`, arquivos já rastreados e restrições de navegador, framework, biblioteca ou sistema operacional;
  - identificar dados sensíveis eventualmente versionados;
  - mapear ciclo de vida, proprietário, escopo, retenção, concorrência e limpeza;
  - NÃO classificar item apenas pelo nome ou extensão.

  Cada item DEVE ser classificado como:
  1. **Canônico:** fonte, configuração, schema, template, fixture deliberada ou asset necessário; PODE ser versionado.
  2. **Gerado reproduzível:** reconstruível; NÃO DEVE ser fonte nem ser versionado, salvo norma superior.
  3. **Runtime persistente:** necessário entre execuções; NÃO DEVE ser versionado e DEVE possuir retenção e proteção.
  4. **Runtime temporário:** descartável; NÃO DEVE ser versionado e DEVE ser limpo automaticamente.
  5. **Sensível:** segredo, sessão, token, cookie ou identidade; NÃO DEVE ser versionado, distribuído ou logado integralmente.
  6. **Exceção técnica:** caminho imposto externamente; DEVE ser isolado, ignorado e documentado.

  A classificação DEVE determinar localização, retenção, limpeza e segurança.

  ## `<RUNTIME_STATE_DIR>`

  A implementação DEVE reutilizar diretório central já normatizado. Na ausência de opção adequada, DEVE criar um único diretório semanticamente compatível com a arquitetura, sem presumir previamente seu caminho.

  `<RUNTIME_STATE_DIR>` DEVE:
  - ficar fora de fonte e distribuição;
  - ser integralmente ignorado pelo Git e excluído de build, release, bundle e publicação;
  - ser criado automaticamente e removível sem perda canônica;
  - permitir isolamento por função, usuário, perfil, submódulo ou execução;
  - impedir colisões e não depender ambiguamente do diretório corrente;
  - ser configurável, seguro e compatível com o sistema operacional.

  Sua estrutura interna DEVE ser curta, estável e derivada das funções reais. Categorias como `cache/`, `sessions/`, `profiles/`, `tmp/`, `locks/`, `downloads/`, `traces/`, `logs/`, `screenshots/` e `checkpoints/` são semânticas, não obrigatórias.

  É PROIBIDO:
  - espalhar estado equivalente sem necessidade;
  - criar raízes paralelas por submódulo quando a estrutura comum bastar;
  - misturar estado mutável com configuração canônica;
  - gravar runtime em `src/`, `dist/`, `scripts/`, raiz ou assets;
  - usar nomes ambíguos ou transformar a raiz em depósito não classificado.

  ## Configuração central

  Raiz, subdiretórios, retenção, TTL, limites, limpeza, persistência, permissões, isolamento, ambientes e overrides DEVEM derivar de configuração central.

  É PROIBIDO manter paths de cache, sessão ou temporários hardcoded em múltiplos módulos. Especializações locais DEVEM herdar a configuração comum e declarar apenas diferenças necessárias.

  ## Git e histórico

  A implementação DEVE:
  - atualizar o `.gitignore` canônico para abranger `<RUNTIME_STATE_DIR>`, equivalentes externos e variantes reais como locks, journals e backups;
  - evitar padrões amplos que ocultem fonte legítima;
  - preservar `.gitkeep` somente por necessidade comprovada;
  - remover arquivos indevidos já rastreados apenas do índice, sem excluir dados locais ainda necessários;
  - verificar o resultado com comandos Git e impedir reinclusão futura.

  Se dados sensíveis tiverem sido versionados, DEVE:
  - interromper reutilização e revogar credenciais, tokens, cookies ou sessões afetados;
  - registrar o incidente sem reproduzir segredos;
  - avaliar limpeza do histórico conforme política e autorização;
  - NÃO reescrever histórico compartilhado sem planejamento e análise de impacto.

  Excluir no commit atual NÃO remove conteúdo do histórico.

  ## Políticas por classe

  ### Sessões e autenticação

  DEVEM permanecer fora do Git, ser isoladas por usuário, perfil, domínio e finalidade, usar permissões mínimas, respeitar expiração, admitir reset controlado e nunca ser copiadas para builds, releases, bundles ou logs.

  Sessões NÃO DEVEM ser compartilhadas entre submódulos sem contrato explícito nem constituir dependência oculta de clone limpo. Persistência somente DEVE ocorrer quando necessária e autorizada; sessões temporárias DEVEM ser descartadas ao término.

  ### Cache

  DEVE ser reconstruível, tolerar ausência e corrupção, impedir mistura entre versões, usuários, targets e submódulos, possuir invalidação por mudança de fonte, configuração, versão ou contrato e limite ou descarte quando houver crescimento relevante.

  Remover cache NÃO DEVE alterar o resultado funcional. Corrupção DEVE causar regeneração segura, não erro permanente ou resultado silenciosamente incorreto.

  ### Temporários, locks, sockets e PIDs

  DEVEM possuir ciclo de vida, nomes sem colisão, criação atômica quando necessária, limpeza em sucesso, cancelamento e falha, tolerância a resíduos e validação de pertencimento antes de remoção.

  Uma execução NÃO DEVE usar ou excluir estado pertencente a outra. A limpeza NÃO DEVE atingir processo ativo ou dado canônico.

  ## Migração e exceções

  Para cada item disperso, criar mapa com caminho atual, classe, produtor, consumidor, sensibilidade, destino, retenção, limpeza, referências, compatibilidade, migração, rollback e critério de remoção do legado.

  A migração DEVE:
  - preservar estado legítimo somente quando necessário e seguro;
  - atualizar produtores e consumidores no mesmo fluxo;
  - impedir gravação simultânea em caminhos antigo e novo, salvo transição controlada;
  - manter retrocompatibilidade apenas quando materialmente necessária;
  - remover fallback legado após validação;
  - ser idempotente e retomável.

  Quando localização externa for imposta, a exceção DEVE ser mínima, isolada, ignorada e documentada; apontar para `<RUNTIME_STATE_DIR>` por opção oficial quando suportado; NÃO duplicar o mesmo estado nem aplicar hacks de filesystem sem necessidade.

  ## Limpeza segura

  Cada classe DEVE possuir política aplicável em conclusão, cancelamento, inicialização, TTL, limite de tamanho, versão incompatível, corrupção ou solicitação explícita.

  A limpeza DEVE:
  - limitar-se à raiz autorizada ou exceção explícita;
  - validar o path resolvido e impedir traversal ou remoção da raiz incorreta;
  - preservar sessões e processos ativos;
  - ser idempotente;
  - registrar apenas resumo não sensível;
  - oferecer inspeção ou `dry-run` quando houver risco relevante.

  ## CI, empacotamento e observabilidade

  CI DEVE iniciar sem estado local e usar diretório efêmero próprio.

  Build, release e bundle NÃO DEVEM conter sessões, perfis, cookies, caches locais, temporários, locks, traces, screenshots, logs ou arquivos de máquina/usuário. A validação de empacotamento DEVE falhar ao detectar item proibido.

  Fixtures DEVEM ser sintéticas, sanitizadas, identificadas e mantidas fora do runtime.

  Logs PODEM registrar classe, path relativo sanitizado, criação, expiração, remoção, tamanho agregado, motivo de invalidação e erro. NÃO DEVEM registrar cookies, tokens, sessão integral, cabeçalhos de autenticação, URLs sensíveis, dados pessoais desnecessários ou payload reutilizável.

  Quando proporcional, adicionar verificação automatizada contra runtime rastreado, paths externos ou hardcoded, segredos, artefatos proibidos, diretórios legados, temporários sem limpeza, permissões inseguras, sessões indevidamente compartilhadas e dependência de estado local. Exceções normatizadas NÃO DEVEM gerar falso positivo.

  ## Testes obrigatórios

  Validar no mínimo:
  - clone limpo e primeira execução sem a raiz;
  - criação automática e override de localização;
  - cache e sessão válidos, expirados, removidos ou corrompidos;
  - interrupção abrupta, lock residual e concorrência;
  - isolamento entre usuários, perfis e submódulos;
  - ambiente somente leitura, quando aplicável;
  - CI, build, release e bundle offline;
  - ausência de runtime no Git e nos artefatos;
  - ausência de segredos nos logs;
  - compatibilidade com anti-bot, intervenção humana e retomada;
  - inexistência de dependência ou gravação em caminho legado;
  - limpeza limitada à raiz autorizada.

  ## Ordem de execução
  1. Ler normas, mapear e classificar todo estado de runtime.
  2. Identificar rastreamento Git, dados sensíveis, produtores, consumidores e configuração existente.
  3. Definir `<RUNTIME_STATE_DIR>` e o mapa de migração.
  4. Centralizar configuração e atualizar produtores e consumidores.
  5. Migrar estado necessário com segurança e remover fallbacks validados.
  6. Atualizar `.gitignore` e remover arquivos indevidos do índice.
  7. Implementar retenção, invalidação, limpeza e proteção.
  8. Validar CI, build, release e bundle.
  9. Executar testes, atualizar rastreabilidade e emitir relatório final.

  ## Critérios de aceite

  A tarefa somente estará concluída quando:
  - todo estado estiver classificado;
  - nenhum estado não canônico permanecer rastreado ou empacotado;
  - `<RUNTIME_STATE_DIR>` concentrar os dados sempre que possível e exceções estiverem justificadas;
  - paths e políticas forem centralizados;
  - sessões e perfis estiverem isolados e protegidos;
  - caches forem descartáveis e reconstruíveis;
  - temporários e locks possuírem limpeza segura;
  - arquivos rastreados indevidamente tiverem sido removidos do índice;
  - segredos expostos tiverem sido tratados;
  - clone limpo, CI, build, execução, release e bundle funcionarem sem estado preexistente;
  - intervenção humana e retomada permanecerem funcionais;
  - não existirem referências residuais a caminhos legados;
  - nenhuma fonte ou fixture legítima tiver sido ignorada.

  ## Relatório final

  Registrar itens encontrados e classificação, rastreamento anterior, dados sensíveis e providências, raiz central, exceções, configuração, produtores e consumidores migrados, regras de ignore, remoções do índice, retenção, limpeza, validações, testes, compatibilidades transitórias, riscos e limitações remanescentes.

- [ ] Criar commit atômico por publicação integralmente baixada e pareada

  ## Objetivo

  Cada nova publicação somente DEVE ser registrada após estar integralmente baixada, validada, pareada aos metadados, incorporada aos índices e acompanhada de todos os assets, referências e derivados aplicáveis.

  Cada publicação concluída DEVE gerar exatamente um commit próprio, completo, isolado, atômico e rastreável, sem misturar outras publicações, manutenção paralela ou alterações não relacionadas.

  ## Unidade transacional

  A unidade de publicação compreende, conforme aplicabilidade:
  - arquivo principal, capas, imagens, anexos e assets;
  - metadados, identificadores, hashes e relações de pareamento;
  - índices locais e globais;
  - manifests, catálogos, mapas, registros derivados e referências cruzadas;
  - estado canônico e rastreabilidade diretamente impactados.

  A ausência, inconsistência ou falha de qualquer componente obrigatório DEVE impedir o commit.

  ## Estado `COMPLETA_E_PAREADA`

  A publicação somente PODE atingir esse estado quando:
  1. todos os downloads obrigatórios terminarem;
  2. nenhum arquivo permanecer parcial, temporário ou em transferência;
  3. formato, tamanho e integridade forem válidos;
  4. conteúdo, identidade e metadados estiverem inequivocamente associados;
  5. assets estiverem completos, nomeados e referenciados corretamente;
  6. duplicidades e colisões tiverem sido verificadas;
  7. índices locais e globais estiverem atualizados;
  8. toda referência interna apontar para arquivo existente;
  9. todas as validações aplicáveis forem aprovadas.

  HTTP de sucesso, existência física ou encerramento do stream, isoladamente, NÃO comprovam conclusão.

  Pareamento heurístico somente PODE concluir automaticamente ao atingir critérios normatizados de confiança. Ambiguidade material DEVE interromper o fluxo para resolução controlada.

  ## Contrato central

  A lógica de unidade transacional, completude, pareamento, arquivos impactados, atualização global, staging seletivo, commit, validação, retomada, concorrência e rastreabilidade DEVE ser centralizada e reutilizada por todos os submódulos.

  É PROIBIDO implementar política de commit independente por submódulo.

  Especializações locais somente PODEM declarar metadados e assets obrigatórios, critérios de pareamento, validadores, chaves de identificação e arquivos globais legitimamente impactados.

  ## Staging e commit

  Para cada publicação `COMPLETA_E_PAREADA`, o fluxo DEVE:
  1. calcular deterministicamente sua allowlist de arquivos;
  2. excluir caches, sessões, temporários, logs e demais estados não canônicos;
  3. inspecionar worktree e índice e isolar alterações alheias;
  4. adicionar somente a unidade e derivados inevitáveis;
  5. validar novamente o conteúdo staged;
  6. criar um único commit;
  7. confirmar que o commit contém integralmente a unidade e nada além dela;
  8. registrar hash e resultado.

  É PROIBIDO:
  - agrupar novas publicações;
  - fragmentar uma publicação entre commits;
  - commitar download parcial, asset órfão, metadado sem conteúdo ou índice inconsistente;
  - incluir alteração independente;
  - usar `git add .`, `git add -A` ou equivalente sem allowlist e validação;
  - criar commit vazio;
  - considerar concluída a publicação antes da confirmação do commit;
  - enviar estado parcial ao remoto.

  Alterações preexistentes ou concorrentes DEVEM permanecer fora do staging, não ser sobrescritas nem descartadas. Conflito material nos mesmos arquivos DEVE interromper explicitamente a operação.

  ## Índices e validação

  Índices globais e demais arquivos derivados pela inclusão DEVEM integrar o mesmo commit.

  O índice global DEVE incluir a publicação uma única vez, usar IDs e paths finais, preservar formato e ordenação, manter referências válidas, não perder entradas, não incorporar publicação incompleta e ser atualizado deterministicamente.

  Antes do staging, validar no mínimo:
  - ausência de arquivos parciais e temporários;
  - hashes, legibilidade e formato;
  - schemas e metadados obrigatórios;
  - unicidade de IDs, nomes e paths;
  - existência de assets e referências;
  - ausência de órfãos, duplicatas indevidas, segredos e dados de sessão;
  - coerência dos índices;
  - conformidade com normas e testes do pipeline.

  Qualquer falha DEVE impedir staging e commit.

  ## Mensagem

  A mensagem DEVE seguir a convenção do repositório. Na ausência de convenção específica, DEVE identificar ação, publicação e identificador estável:

  ```text
  <tipo>: adicionar publicação <identificador ou título canônico>
  ```

  A mensagem NÃO DEVE ser genérica, omitir a publicação, declarar sucesso parcial, expor dado sensível ou depender apenas de sequência instável quando houver ID canônico.

  ## Atomicidade, falhas e retomada

  Download, pareamento, indexação, staging e commit DEVEM compor uma única operação lógica.

  Se qualquer fase falhar:
  - nenhum commit DEVE ser criado;
  - parciais DEVEM permanecer fora da fonte canônica;
  - índices NÃO DEVEM conservar entrada inválida;
  - alterações preparatórias DEVEM ser revertidas ou mantidas em área controlada;
  - o estado DEVE permitir retomada idempotente;
  - o diagnóstico DEVE identificar publicação e fase.

  Commit válido já criado NÃO DEVE ser recriado na retomada.

  Reprocessar publicação inalterada DEVE produzir operação sem commit, sem duplicar arquivos, índices ou registros e sem alterar derivados por mudança não material. Inclusão inédita, correção e atualização DEVEM ser distinguidas.

  ## Concorrência e remoto

  Execuções concorrentes NÃO PODEM processar a mesma publicação, alterar índice global sem coordenação, misturar staging, usar estado obsoleto ou sobrescrever alterações válidas.

  Downloads PODEM ocorrer em paralelo, mas finalização, atualização global e commits DEVEM ser serializados ou coordenados transacionalmente.

  Push, quando aplicável, somente PODE ocorrer após validar commit, branch, remoto, sincronização e ausência de conflito. Falha no push DEVE preservar o commit local para nova tentativa, sem recriação ou duplicação.

  ## Rastreabilidade

  Registrar identificador, arquivos da unidade, validações, pareamento, índices alterados, hash do commit, branch, resultado do push e falhas ou retomadas. Arquivos temporários de controle NÃO DEVEM ser versionados.

  ## Testes obrigatórios

  Validar no mínimo:
  - publicação completa e já existente;
  - download parcial, asset ausente, metadado inválido, pareamento ambíguo e duplicidade;
  - índice desatualizado ou referência quebrada;
  - worktree com alterações alheias e conflito no mesmo arquivo;
  - conclusões simultâneas de publicações distintas e disputa pela mesma publicação;
  - falha antes ou depois do staging, falha do commit e retomada;
  - push recusado;
  - reexecução idempotente;
  - ausência de temporários, caches e sessões;
  - exatamente um commit por publicação e conteúdo exato do staging e do commit.

  ## Ordem de execução
  1. Ler normas e mapear download, pareamento, indexação e Git.
  2. Definir a unidade transacional e o estado `COMPLETA_E_PAREADA`.
  3. Centralizar validações e cálculo dos arquivos impactados.
  4. Integrar índices à mesma transação.
  5. Implementar staging por allowlist e isolamento do worktree.
  6. Implementar e validar commit único.
  7. Implementar idempotência, retomada e concorrência.
  8. Integrar push seguro, quando aplicável.
  9. Adicionar testes, documentação e rastreabilidade.
  10. Emitir relatório final.

  ## Critérios de aceite

  A tarefa somente estará concluída quando:
  - cada publicação completa gerar exatamente um commit próprio;
  - nenhuma publicação incompleta puder ser commitada;
  - arquivos, assets, metadados, índices e derivados integrarem a mesma transação;
  - staging e commit forem calculados por allowlist determinística;
  - alterações alheias permanecerem fora do commit;
  - publicações não forem agrupadas nem fragmentadas;
  - reexecução não criar duplicatas;
  - concorrência não produzir mistura, perda ou estado obsoleto;
  - falhas não deixarem fonte ou índice parcialmente aplicados;
  - runtime não canônico permanecer fora do Git;
  - o commit seguir a convenção vigente e seu hash permanecer rastreável;
  - todos os submódulos aplicáveis adotarem o contrato central;
  - testes cobrirem sucesso, falha, duplicidade, retomada, concorrência e conteúdo exato.

  ## Relatório final

  Registrar unidade transacional, critérios de completude e pareamento, arquivos por publicação, índices alterados, staging seletivo, convenção de commit, concorrência, rollback e retomada, testes, commits de validação, resultado de push e limitações remanescentes.
