# RCF subordinado — Conversa probatória

Este documento integra a suíte normativa do **egwSearch**, subordina-se ao
[RCF principal](../RCF.md) e preserva os §§51–58 da numeração global. Ele rege
o Modo Conversa, prova documental, referências, sessão, arquitetura,
degradação e validação. Os contratos comuns de recuperação permanecem no
[RCF de pesquisa](RCF.pesquisa.md); interpretação hermenêutica aplica
obrigatoriamente o [RCF epistemológico](RCF.epistemologia.md).

**Ordem:** leia primeiro o RCF principal; depois o RCF de pesquisa quando houver
recuperação; então este documento e o RCF epistemológico.

## 51. Modo Conversa e contrato comum

O Modo Conversa DEVE permitir diálogo fluido, contextual e iterativo com o acervo, inclusive aprofundar, comparar, interpretar, relacionar, contestar, mudar recorte e solicitar novas provas. [62596f1]

Modo Pesquisa e Modo Conversa PODEM compartilhar descoberta, extração, texto canônico, segmentação, índices, recuperação, expansão, filtros, reranking, confiança, referências, tradução, cache e limites. Cada modo DEVE possuir orquestração, estado, apresentação, saída e aceite próprios sobre contratos comuns versionados. [62596f1]

O contexto conversacional DEVE ser controlado por sessão. Pergunta subsequente PODE reutilizar consulta, filtros, entidades, fontes e evidências ainda válidas; mudança de finalidade, recorte, versão, fonte ou afirmação material DEVE provocar recuperação proporcional nova. [62596f1]

A IA DEVE interpretar e explicar o conteúdo, sem apenas falar em nome das fontes nem apresentar paráfrase desacompanhada de prova. Toda afirmação material atribuida ao acervo DEVE possuir evidência documental suficiente, exata, contextualizada e associada. [62596f1]

Resposta DEVE distinguir de modo inequívoco: `afirmacao`, `evidencia`, `referencia`, `traducao`, `interpretacao`, `comparacao`, `inferencia`, `conclusao` e `limitacao`. Campo ou camada não aplicável PODE ser omitido da apresentação, mas sua natureza NÃO DEVE ser confundida. [62596f1]

A apresentação PODE ser natural, concisa e adaptativa; NÃO DEVE impor estrutura repetitiva ou excessivamente acadêmica quando desnecessária. Fluidez e simplificação visual NÃO DEVEM ocultar origem, substituir prova por autoridade aparente ou reduzir verificabilidade. [62596f1]

## 52. Prova documental, citação e suficiência

Evidência probatória DEVE ser trecho literal conferido contra o texto canônico efetivamente indexado ou acessível, preservando bytes ou caracteres lógicos, idioma, documento, edição/versão, offsets e localização disponível. [62596f1]

Citação direta DEVE reproduzir fielmente o original, sem reconstrução, complementação, fusão, correção silenciosa ou alteração semântica. Paráfrase, tradução, resumo e inferência NÃO DEVEM ser rotulados como citação. [62596f1]

Cada citação DEVE: [62596f1]

1. ter extensão suficiente para inteligibilidade e para preservar condição, exceção, negação, modalidade, agente, objeto e conclusão;
2. permanecer associada somente a afirmação que efetivamente sustenta;
3. identificar publicação, edição ou versão, autor ou entidade, título, idioma e formato;
4. apontar página, intervalo, seção, capítulo, artigo, item, parágrafo, posição, âncora, offset ou identificador interno equivalente conforme disponibilidade;
5. permitir localização e conferência pelo usuário;
6. preservar o original quando acompanhada de tradução.

Quando o trecho isolado for insuficiente, a recuperação DEVE expandir seletivamente definição, premissa, exceção, nota, referência interna, parágrafo adjacente, seção, página ou outra passagem correlata. Citação formalmente correta, mas materialmente enganosa por descontextualização, DEVE ser rejeitada. [62596f1]

Quantidade e extensão de prova DEVEM ser proporcionais ao risco, complexidade e finalidade. Pergunta simples PODE usar prova concisa; comparação, controvérsia, interpretação normativa ou argumento complexo DEVE ampliar fundamentação. Despejo de citações sem função e fragmento incapaz de comprovar a afirmação são proibidos. [62596f1]

Antes da resposta, o sistema DEVE verificar pertinência e suficiência das fontes, cobertura dos argumentos, passagens contraditórias ou qualificadoras, dependências não localizadas, conclusões que excedam o corpus e integridade contextual. [62596f1]

Prova insuficiente DEVE produzir limitação ou abstenção explícita. O sistema NÃO DEVE preencher lacuna com segurança aparente, referência fabricada ou conclusão não suportada. [62596f1]

Validação DEVE impedir ou detectar citação inexistente, página/seção incorreta, trechos de fontes diferentes fundidos, texto alterado, atribuição equivocada, paráfrase como citação, tradução como original, conclusão sem suporte, exceção material omitida e fragmento sem contexto suficiente. [62596f1]

## 53. Referência, localização e tradução vinculada

Cada fonte utilizada DEVE possuir referência documental ou bibliográfica completa segundo os metadados efetivamente disponíveis: autor, órgão, entidade ou responsável; título e subtítulo; edição, versão ou revisão; data; editora, emissor ou repositório; idioma; tipo e formato; identificador persistente; URL pública direta e URL de origem; data de acesso quando pertinente; hash de integridade normatizado; e localização exata do trecho. [62596f1]

Metadado ausente NÃO DEVE ser inventado. Campo indisponível DEVE ser omitido ou marcado como não determinado conforme o contrato de saída, sem preencher por plausibilidade. [62596f1]

Referência e localização DEVEM ser validadas contra a publicação e a representação efetivamente consultadas. Alinhamento PDF-EPUB PODE enriquecer página e estrutura somente sob confiança suficiente; sem alinhamento, a localização real disponível DEVE prevalecer. [62596f1]

Fonte em idioma diferente da conversa DEVE manter a citação original como prova. Tradução PODE ser adicionada imediatamente associada, identificada como tradução e separada da transcrição; a obrigação mais estrita de tradução `en-US` para `pt-BR` do §19 permanece. [62596f1]

Tradução NÃO DEVE substituir o original, esconder ambiguidade nem atribuir a fonte redação existente apenas na interpretação traduzida. Termo técnico, jurídico, normativo ou semanticamente sensível DEVE preservar também a forma original. Divergência material entre traduções existentes DEVE ser informada. [62596f1]

Interface aplicável DEVE permitir abrir a publicação na localização citada quando tecnicamente suportado, consultar referência completa, alternar original/tradução, expandir contexto adjacente e copiar citação ou referência sem perda de integridade. [62596f1]

## 54. Pesquisa profunda, relações e documentos de autoridade

O Modo Conversa DEVE poder executar pesquisa profunda proporcional antes de responder, decompondo pergunta complexa, localizando terminologias distintas, relacionando partes distantes da mesma publicação, cruzando publicações, comparando edições/versões e recuperando fundamentos além dos primeiros fragmentos semelhantes. [62596f1]

Pesquisa profunda NÃO DEVE ser simulada. A estratégia DEVE revisar suficiência e PODE iterar recuperação, filtros, expansão, vizinhança, referência, hierarquia, reranking e diversidade dentro dos limites configurados. [62596f1]

Cada fonte DEVE poder ser classificada, quando a evidência permitir, como primária, secundária, normativa, interpretativa, histórica ou outra categoria declarada. A classificação DEVE influenciar precedência e apresentação sem ocultar fonte relevante. [62596f1]

Relação entre publicações DEVE possuir tipo explícito, incluindo confirmação, complementação, especialização, divergência, revogação, dependência, evolução histórica, aplicação, interpretação ou analogia. Relação inferida DEVE ser marcada como inferência, sustentada por evidências próprias e NÃO DEVE ser apresentada como vínculo declarado. [62596f1]

Documento técnico, normativo, governamental ou legal DEVE receber tratamento compatível com hierarquia, vigência, competência, jurisdição, versão, escopo, definições, remissões, condições e exceções. [62596f1]

Nesses documentos, a recuperação e composição DEVEM privilegiar fonte primária disponível; distinguir texto normativo de explicação, parecer, jurisprudência, doutrina, manual ou comentário; preservar verbos normativos e condicionantes; identificar versão, vigência e jurisdição quando comprovadas; e sinalizar conflito, revogação, alteração ou incerteza. [62596f1]

Conclusão categórica NÃO DEVE ser emitida quando a fonte, sua autoridade, vigência ou cobertura não a sustentar. [62596f1]

## 55. Sessão, rastreabilidade e reprodução

Cada sessão conversacional DEVE possuir identidade estável e registrar, conforme privacidade e retenção configuradas: consulta original; decomposições relevantes; modo; filtros e recortes; publicações consultadas; unidades recuperadas; trechos utilizados; referências emitidas; traduções geradas; relações e inferências relevantes; componentes/versões; limitações; e falhas de recuperação. [62596f1]

Registro DEVE permitir auditoria e reprodução proporcional da resposta sem exigir exposição de raciocínio interno privado da IA. [62596f1]

Associação entre afirmação, evidência, referência, tradução, interpretação e inferência DEVE ser persistida por identificadores estáveis ou relações equivalentes, sem depender somente da apresentação visual. [62596f1]

Alteração de documento, edição, extrator, segmentação, índice, modelo, prompt, tradutor, reranker, configuração causal ou política que invalide evidência DEVE marcar resposta ou sessão afetada como obsoleta e exigir revalidação antes de reutilização probatória. [62596f1]

Retomada DEVE restaurar apenas contexto validado, respeitar limites e impedir mistura entre sessões. Cancelamento, expiração, exclusão e falha DEVEM preservar estado íntegro e diagnóstico proporcional. [62596f1]

Logs e telemetria DEVEM minimizar conteúdo, usar referências/hashes quando suficientes e manter consulta ou trecho sensível fora de saída pública. [62596f1]

## 56. Arquitetura, interface, desempenho e degradação

Recuperação, indexação, busca lexical, semântica e híbrida, reranking, expansão, leitura contextual e geração DEVEM ser selecionados conforme aplicabilidade e estado real. LLM NÃO DEVE ser imposta a todas as etapas nem degradar pesquisa simples. [62596f1]

Cache, pré-processamento, índices especializados e execução local ou remota DEVEM equilibrar precisão, cobertura, latência, custo, disponibilidade e fidelidade. Profundidade da pesquisa e orçamento de recursos DEVEM ser configuráveis, limitados e visíveis no diagnóstico. [62596f1]

LLM, tradutor, reranker e componente avançado DEVEM declarar contrato, modelo/versão, entrada, saída, limite, timeout, cancelamento, custo, privacidade, variação, fallback e validação. A adoção como padrão exige ganho medido conforme §39. [62596f1]

Indisponibilidade ou inadequação de componente avançado DEVE: [62596f1]

1. preservar no Modo Pesquisa todas as capacidades independentes;
2. limitar síntese ou interpretação do Modo Conversa sem fabricar resposta;
3. emitir citação e referência somente quando verificadas;
4. informar objetivamente a limitação;
5. usar alternativa prevista e segura quando existente.

A interface DEVE oferecer controle inequívoco de modo e distinguir resultado recuperado de síntese da IA. No Modo Conversa, DEVE permitir identificar quais afirmações cada citação sustenta, solicitar evidência adicional ou aprofundamento, consultar referência, visualizar original/tradução e expandir contexto. [62596f1]

Controle de modo, filtros, profundidade, evidência e sessão DEVE permanecer acessível por teclado e tecnologias assistivas quando houver GUI. Estado visual NÃO DEVE ser a única fonte semântica. [62596f1]

Operação local continua padrão. Componente remoto NÃO DEVE receber conteúdo sem autorização e configuração explicitas conforme §§19, 26 e 34. [62596f1]

## 57. Validação e aceite dos modos

A validação futura DEVE usar testes determinísticos e conjuntos de avaliação versionados que cubram: [62596f1]

1. preservação integral do Modo Pesquisa e distinção funcional entre modos;
2. precisão e cobertura de recuperação;
3. fidelidade literal e contexto das citações;
4. validade das localizações e completude das referências;
5. associação entre afirmação e prova;
6. distinção entre fonte, tradução, interpretação e inferência;
7. relações multifuente, versões e contradições;
8. documentos técnicos, normativos, governamentais e legais;
9. ausência de citação, referência, localização ou atribuição fabricada;
10. metadados incompletos, prova insuficiente e abstenção;
11. degradação sem LLM, tradutor, reranker ou auxiliar;
12. desempenho proporcional a profundidade, latência, tokens, memória e custo.

O produto somente DEVE aceitar esta extensão quando: [62596f1]

1. o recurso de pesquisa vigente permanecer integralmente preservado e não conversacional;
2. o usuário puder selecionar explicitamente Pesquisa ou Conversa;
3. LLM for usada apenas quando agregar valor e nunca como substituição obrigatória; [62596f1]
4. o Modo Conversa interpretar, conectar e argumentar com base no acervo;
5. cada afirmação material possuir citação exata, referência completa disponível e localização verificável;
6. citações preservarem contexto, condicionantes, exceções e integridade;
7. fonte em outro idioma exibir original e tradução identificada quando exigida ou necessária;
8. conteúdo da fonte, interpretação, comparação e inferência permanecerem distinguíveis;
9. relações entre publicações forem tipadas e fundamentadas;
10. documentos de autoridade receberem tratamento compatível com sua natureza;
11. fabricação e atribuição incorreta forem impedidas ou detectadas;
12. limitação de prova produzir declaração ou abstenção;
13. apresentação mantiver rigor lógico e acadêmico proporcional sem prolixidade obrigatória; [62596f1]
14. os contratos forem incorporados ao RCF sem duplicar ou enfraquecer normas vigentes.

Relatório de aceite DEVE registrar normas preservadas/especializadas, alterações do RCF, arquitetura adotada, diferenças entre modos, critérios de uso de LLM, modelo de citação/referência/tradução, prevenção de alucinação, FTs, testes, conjuntos de avaliação, métricas de precisão/fidelidade/cobertura/latência/custo, limitações, pendências e riscos. [62596f1]

## 58. Convergência das fontes

Os requisitos registrados na fonte canônica `.ia.rules/state/TODO.ia.md` linhas 56, 69, 95, 214, 886 e 1182 foram absorvidos por este RCF como contratos permanentes.

O arquivo de TODO permanece somente como fonte versionada e controle de demanda até o encerramento documental da FT-003; implementação futura DEVE derivar deste RCF e das FTs, não do TODO. [62596f1]

