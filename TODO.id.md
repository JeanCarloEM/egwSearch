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

  - [ ] **Envelope do índice global:** o índice global DEVE manter a estrutura externa abaixo. `formative_data` DEVE conter, sem ampliação, o documento integral definido pela `NORMA-IF-SIL-001`:

  - [ ] **Localização de assets:** todo asset de uma publicação deve localizar-se aninhada imediatamente sob mesmo diretório de localização da publicação (pdf/epub) em `./assets/<basename-publicacao>/`, incluindo cover.png ou qualquer outro metadado, como os já previamente existentes .json com o mesmo nome .json que devem ser movidos para a nova localização e ter sua nova localização adequadalizada em `baixar.py`.

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

  - [ ] **Exemplo não produtivo:** os marcadores de hash existem somente para demonstrar o aninhamento. Payload produtivo DEVE conter hashes reais, integralmente recalculados sobre os bytes originais.

  - [ ] **Separação entre envelope e documento formativo:**
    - `publications`, `title`, `urls` e `formative_data` pertencem exclusivamente ao índice global;
    - `formative_data` DEVE conter exatamente `book` e `global_hashes`;
    - nenhuma chave do envelope global DEVE ser inserida em `formative_data`;
    - nenhuma propriedade adicional DEVE ser criada em `formative_data` para satisfazer necessidades do índice;
    - o documento formativo NÃO DEVE ser denominado nem tratado como metadado canônico integral;
    - eventual substituição de `formative_data` por referência externa somente PODE ocorrer mediante alteração normativa explícita do contrato do índice.

  - [ ] **Contrato do índice global:**
    - `publications` DEVE ser um array;
    - cada item DEVE representar uma publicação lógica;
    - `title` DEVE conter o título público e legível;
    - `urls` DEVE conter uma ou mais URLs absolutas;
    - cada URL DEVE apontar para representação válida da mesma publicação;
    - `formative_data` DEVE ser documento completo e válido conforme a `NORMA-IF-SIL-001`;
    - formatos diferentes da mesma edição DEVEM permanecer agrupados no mesmo item;
    - publicações distintas NÃO DEVEM ser fundidas apenas por semelhança de título.

  - [ ] **Correspondência de título:** `publications[].title` DEVE corresponder a `publications[].formative_data.book.title`, admitindo diferença somente quando regra editorial externa e explícita distinguir título de apresentação e título editorial.

  - [ ] **Correspondência de formatos:** cada URL pública DEVE apontar para formato efetivamente publicado e validado. Para cada `pdf` ou `epub` listado nas URLs, DEVE existir exatamente um item correspondente em `formative_data.global_hashes`; formato ausente, excedente ou duplicado DEVE falhar.

  - [ ] **Dados formativos obrigatórios:** cada item do índice DEVE incluir `formative_data`, obtido e validado conforme a `NORMA-IF-SIL-001`.
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
    - `tags`.

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
    - `SIL-001` Esta norma DEVE ser subordinada ao `RCF-IF-001` e reger exclusivamente as propriedades `book` e `global_hashes`, com suas propriedades descendentes expressamente definidas neste documento.
    - `SIL-002` A estrutura DEVE ser semanticamente idêntica em JSON e YAML.
    - `SIL-003` O objeto raiz DEVE conter exatamente `book` e `global_hashes`.
    - `SIL-004` `book` DEVE conter exatamente `title`, `contributors`, `edition`, `language`, `primary_category` e `tags`.
    - `SIL-005` Cada item de `book.contributors` DEVE conter exatamente `name` e `role`.
    - `SIL-006` `book.edition` DEVE ser exatamente o objeto vazio `{}` neste perfil restrito.
    - `SIL-007` Cada item de `global_hashes` DEVE conter exatamente `format`, `sha1`, `sha256` e `sha512`.
    - `SIL-008` Propriedade não enumerada em `SIL-003..007` NÃO DEVE constar desta norma nem de documento conforme a ela.
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

    ## 6. Extração específica por formato

    ### 6.1 EPUB
    - `SIL-EPUB-001` EPUB DEVE ser tratado como contêiner ZIP OCF não confiável.
    - `SIL-EPUB-002` Antes de ler conteúdo, o processo DEVE limitar quantidade de entradas, tamanho comprimido, tamanho expandido, razão de expansão, profundidade e comprimento de caminho.
    - `SIL-EPUB-003` Path absoluto, traversal, symlink, colisão após normalização e entidade XML externa DEVEM ser rejeitados.
    - `SIL-EPUB-004` O Package Document DEVE ser localizado pelo arquivo de contêiner e analisado com namespaces.
    - `SIL-EPUB-005` Título, idioma e colaboradores estruturados DEVEM ser confrontados com página de rosto e colofão na ordem de leitura definida pelo spine.
    - `SIL-EPUB-006` A ordem física das entradas compactadas NÃO DEVE ser tratada como ordem editorial.
    - `SIL-EPUB-007` Impressão textual usada apenas para comparar PDF e EPUB DEVE seguir o spine, excluir script, estilo e navegação repetitiva e normalizar Unicode e espaços em cópia derivada.

    ### 6.2 PDF
    - `SIL-PDF-001` PDF DEVE ser analisado por biblioteca que interprete objetos, xref, streams, fontes, páginas e metadados.
    - `SIL-PDF-002` Regex sobre bytes crus NÃO DEVE ser usada para extrair `book`.
    - `SIL-PDF-003` Página de rosto e colofão visíveis DEVEM prevalecer sobre metadado técnico conflitante.
    - `SIL-PDF-004` Extração de texto DEVE preservar número e ordem das páginas e registrar falha, página vazia e baixa densidade textual.
    - `SIL-PDF-005` OCR somente DEVE ser usado quando a camada textual for ausente ou insuficiente. Resultado de OCR é evidência derivada e NÃO DEVE substituir o original.
    - `SIL-PDF-006` PDF cifrado sem autorização de leitura, corrompido ou acima dos limites operacionais DEVE falhar com diagnóstico.

    ### 6.3 Associação entre PDF e EPUB
    - `SIL-MATCH-001` PDF e EPUB somente DEVEM integrar o mesmo documento quando título, autoria, idioma e identidade editorial forem compatíveis.
    - `SIL-MATCH-002` Comparação DEVERIA usar impressão textual derivada de amostras distribuídas na ordem editorial, nunca igualdade de hashes entre formatos.
    - `SIL-MATCH-003` Diferença de paginação, layout ou codificação NÃO implica obra distinta.
    - `SIL-MATCH-004` Diferença material de conteúdo, idioma, autoria ou edição DEVE impedir associação automática.
    - `SIL-MATCH-005` Confiança insuficiente DEVE encaminhar para revisão humana.

    ## 7. Validação integral
    1. Analisar JSON ou YAML em modo seguro.
    2. Confirmar que a raiz contém somente `book` e `global_hashes`.
    3. Confirmar as seis chaves exatas de `book`.
    4. Confirmar `edition: {}` e a presença de `tags`, ainda que `[]`.
    5. Confirmar ao menos um contribuidor e ao menos um `author`.
    6. Confirmar duas chaves exatas em cada contribuidor.
    7. Validar título, nomes, papéis, idioma, categoria e tags.
    8. Confirmar um ou dois itens em `global_hashes`, sem formato duplicado.
    9. Confirmar quatro chaves exatas em cada item.
    10. Recalcular os três hashes dos bytes originais e comparar todos os valores.
    11. Confirmar a associação editorial quando PDF e EPUB coexistirem.
    12. Serializar no outro formato, analisar novamente e exigir igualdade profunda.
    - `SIL-VAL-001` Falha DEVE indicar a propriedade, a regra violada e a evidência necessária, sem inventar valor substituto.
    - `SIL-VAL-002` Item inválido NÃO DEVE ser silenciosamente removido para fazer o documento parecer conforme.
    - `SIL-VAL-003` Documento somente é conforme quando todas as propriedades obrigatórias existem e nenhuma propriedade adicional existe.

    ## 8. Exemplos semanticamente equivalentes

    ### 8.1 JSON

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

    ### 8.2 YAML

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

    ## 9. Referências técnicas
    - RCF local: [`../RCF.md`](../RCF.md), especialmente `RCF-IF-DATA-009..015`, `RCF-IF-HASH-001..006` e `RCF-IF-DATA-022..025`.
    - JSON: [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259).
    - YAML: [YAML 1.2.2](https://yaml.org/spec/1.2.2/).
    - Idiomas: [BCP 47 / RFC 5646](https://www.rfc-editor.org/rfc/rfc5646).
    - EPUB: [EPUB 3.3](https://www.w3.org/TR/epub-33/).
    - Hash em Node.js: [`node:crypto`](https://nodejs.org/api/crypto.html).
    - PDF em Node.js: [PDF.js API](https://mozilla.github.io/pdf.js/api/).
    - Hash em Python: [`hashlib`](https://docs.python.org/3/library/hashlib.html).
    - EPUB em Python: [`zipfile`](https://docs.python.org/3/library/zipfile.html).
    - PDF em Python: [pypdf](https://pypdf.readthedocs.io/en/latest/user/extract-text.html) e [PyMuPDF](https://pymupdf.readthedocs.io/en/latest/).

    Não existe vínculo com editoras; o projeto não responde pelo conteúdo de terceiros; atribuição, restrições e integridade permanecem obrigatórias.
