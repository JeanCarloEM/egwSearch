# Pipeline RAG completa — revisão rápida em diálogo técnico

> Síntese compacta da videoaula (`pipeline-rag-aula-sintetizada-dialogo.md`). Preserva arquitetura, decisões, exemplos, limitações e correções técnicas relevantes; remove divulgação, saudações e repetições. Termos incorretamente inferidos pela legenda automática foram normalizados.

- Termos da aula foram inferidos a partir de legenda gerada automaticamente, por conter erros.
- Video aula original: https://www.youtube.com/watch?v=9i6r90i17iA
- Repositório usado na aula:
  - https://github.com/caio-moliveira/rag-project
  - https://github.com/lvgalvao/data-engineering-roadmap

## 1. Objetivo e arquitetura

**Dev 1:** Qual problema a aula resolve?

**Dev 2:** Construir uma pipeline RAG capaz de consultar documentos por linguagem natural. O exemplo usa 126 PDFs públicos de súmulas do TCE, mas a fonte poderia ser Word, TXT, JSON, planilha, banco de dados ou outro repositório.

**Dev 1:** Qual é o fluxo completo?

**Dev 2:**

`documentos -> extração -> chunking -> metadados -> embeddings -> Qdrant -> retrieval híbrido + filtros -> LangGraph -> LLM -> Streamlit`

O Langfuse observa execuções, custo, tokens e latência; guardrails restringem domínio e abuso.

**Dev 1:** Qual stack foi usada?

**Dev 2:** Python, `uv`, OpenAI, MarkItDown, Qdrant, LangChain, LangGraph, Langfuse e Streamlit. LlamaIndex, Chainlit, Context7, FastAPI, PydanticAI, Groq, Pinecone e Agno aparecem como alternativas ou extensões.

## 2. Infraestrutura e dados

**Dev 1:** Como o Qdrant foi executado?

**Dev 2:** Localmente, em container Docker, com dashboard acessível pelo endpoint `/dashboard`. No Qdrant, cada `point` representa um registro vetorial associado a um chunk.

**Dev 1:** Qual foi o volume final?

**Dev 2:** Os 126 PDFs geraram 356 chunks. A maioria das súmulas foi dividida em três partes; algumas, em duas.

**Dev 1:** E o Langfuse?

**Dev 2:** Foi usado no cloud, mas pode ser self-hosted. As credenciais — `public key`, `secret key` e `host` — ficam no `.env`, junto da chave OpenAI e da conexão do Qdrant.

**Dev 1:** O que ele registra?

**Dev 2:** Input, output, nós executados, traces, spans, latência, tokens, custo estimado, modelo, tags, metadados, usuário, sessão e dashboards agregados.

**Dev 1:** A aula menciona limites gratuitos.

**Dev 2:** Sim, cita aproximadamente 50 mil registros no Langfuse Cloud e cerca de 5 mil no LangSmith naquele momento. São valores históricos da live, não garantias atuais. A decisão prática pelo Langfuse ocorreu principalmente pela possibilidade de hospedagem interna.

## 3. Chunking: não existe estratégia universal

**Dev 1:** O que é um chunk?

**Dev 2:** Um fragmento do documento indexado e recuperado de forma independente. Deve ser pequeno o suficiente para busca eficiente, mas grande o bastante para preservar contexto.

**Dev 1:** Um splitter semântico é sempre a melhor escolha?

**Dev 2:** Não. A estratégia depende do layout, do domínio e das consultas. Em processos de 40 a 60 páginas, splitters por sentença e parágrafo falharam porque abreviações como “pág.” e “art.” eram interpretadas como fim de unidade. Uma regex específica apresentou resultado melhor.

**Dev 1:** Então regras determinísticas continuam relevantes.

**Dev 2:** Muito. Em extratos, notas de corretagem e documentos financeiros, regex e parsers podem ser mais confiáveis, baratos e previsíveis que LLMs, sobretudo quando nenhum valor ou separador pode ser alterado.

**Dev 1:** Quais opções LangChain e LlamaIndex oferecem?

**Dev 2:** Divisão por caracteres, sentenças, parágrafos, Markdown, HTML, JSON, código-fonte, semântica, separadores customizados e regex. O `SentenceSplitter` do LlamaIndex foi destacado pela flexibilidade de separadores e expressões regulares.

**Dev 1:** E quando há múltiplos layouts?

**Dev 2:** Use pipelines e collections distintas. No projeto real havia seis collections para seis tipos documentais. Um agente podia classificar a intenção, selecionar a collection correta e aplicar um prompt especializado.

## 4. Chunking usado nas súmulas

**Dev 1:** Como os PDFs curtos foram divididos?

**Dev 2:** O MarkItDown converteu cada PDF em Markdown. Depois, um LLM recebeu instruções para retornar JSON com três blocos:

- `conteudo_principal`;
- `referencias_normativas`;
- `precedentes`.

O JSON foi limpo, validado e convertido em documentos com `page_content` e `metadata`.

**Dev 1:** Qual a desvantagem?

**Dev 2:** Chunking por LLM adiciona custo e latência. Foi aceitável porque os documentos eram curtos e estruturados. Em escala maior, devem ser comparados parser, regex, OCR, regras de layout e splitters nativos.

## 5. Metadados

**Dev 1:** Quais atributos acompanharam cada chunk?

**Dev 2:** Número da súmula, data do status, ano, status atual, nome do PDF, tipo e índice do chunk.

**Dev 1:** Por que repetir isso em cada fragmento?

**Dev 2:** Porque cada chunk precisa ser filtrável isoladamente. Metadados reduzem o espaço de busca, custo, ruído e dependência de similaridade semântica.

**Dev 1:** Qual exemplo real demonstra isso?

**Dev 2:** No TCE, o banco relacional já possuía número do processo, relator, data, natureza e páginas. Para um número de processo único, aplica-se filtro direto, sem varrer semanticamente cerca de 20 mil PDFs.

**Dev 1:** E conhecimento de domínio pode virar filtro?

**Dev 2:** Sim. Como a ementa geralmente estava nas páginas 1 e 2, perguntas sobre ementa priorizavam essas páginas, mesmo quando documentos antigos não continham o rótulo explícito.

## 6. Projeto Python

**Dev 1:** Como o projeto foi inicializado?

**Dev 2:** Com `uv init`, ambiente virtual e dependências no `pyproject.toml`. A aula utilizou Python 3.13.3 e `tiktoken` para contagem de tokens.

**Dev 1:** Como o código foi organizado?

**Dev 2:** Aproximadamente assim:

- `app/ingest/`: extração, transformação, embeddings e carga;
- `app/retrieval/`: recuperação e schema de metadados;
- `app/graph/`: estado, prompts e grafo;
- `app/utils/`: configurações;
- aplicação Streamlit.

Um módulo central de settings carregava o `.env`.

**Dev 1:** Houve problema com imports.

**Dev 2:** Sim. A inclusão de `__init__.py` fez `app` ser reconhecido corretamente naquele ambiente. A correção conceitual é que namespace packages sem esse arquivo existem desde Python 3.3, não 3.9; mesmo assim, ferramentas e modos de execução ainda podem exigir ou se beneficiar dele.

**Dev 1:** Python novo sempre executa código antigo?

**Dev 2:** Não é garantia. Bibliotecas, extensões nativas, APIs removidas e mudanças comportamentais podem quebrar compatibilidade. Deve-se testar.

## 7. Modelos e embeddings

**Dev 1:** Quais modelos foram configurados?

**Dev 2:** GPT-4.1 mini para geração e interpretação; `text-embedding-3-large`, com 3.072 dimensões, para embeddings. O `text-embedding-3-small`, com 1.536 dimensões, foi citado como alternativa.

**Dev 1:** Qual temperatura usar?

**Dev 2:** Em aplicações jurídicas ou factuais, `0` ou próximo disso para maior consistência. Temperatura elevada aumenta variação, não equivale automaticamente a alucinação, mas pode reduzir aderência.

**Dev 1:** Mais dimensões garantem melhor retrieval?

**Dev 2:** Não. Dimensão é apenas um fator. Modelo, idioma, domínio, normalização, chunking, métrica e avaliação também importam. A dimensão da collection deve coincidir exatamente com a saída do embedding; trocar 3.072 por 1.536 exige reconfiguração ou recriação.

## 8. Busca híbrida no Qdrant

**Dev 1:** Qual a diferença entre `dense` e `sparse`?

**Dev 2:**

- `dense`: similaridade semântica; aproxima “carro” e “automóvel”;
- `sparse`: correspondência lexical e relevância de termos exatos.

A combinação forma uma busca híbrida.

**Dev 1:** Os pesos podem variar?

**Dev 2:** Sim. Pode-se priorizar sete resultados semânticos e três lexicais, por exemplo, ou inverter a proporção conforme a consulta.

**Dev 1:** Qual métrica vetorial foi usada?

**Dev 2:** Similaridade por cosseno.

## 9. Ingestão

**Dev 1:** Como a collection é preparada?

**Dev 2:** O código conecta ao Qdrant, verifica se a collection existe e, caso contrário, cria-a com dimensão, métrica e configurações dense/sparse compatíveis.

**Dev 1:** Qual o processamento por PDF?

**Dev 2:**

1. converter;
2. extrair texto;
3. gerar chunks e metadados estruturados;
4. criar documentos;
5. gerar embeddings;
6. gravar points no Qdrant.

O payload armazena `page_content` e `metadata`.

**Dev 1:** Para outro catálogo, basta substituir os PDFs?

**Dev 2:** Não necessariamente. Se layout, extensão ou semântica mudarem, parser, chunking, prompt e metadados também devem mudar.

## 10. Self-query retrieval

**Dev 1:** Como o sistema combina linguagem natural e filtros?

**Dev 2:** Com `SelfQueryRetriever`. Cada metadado é descrito por nome, tipo, finalidade e exemplos. Um LLM interpreta a pergunta e gera:

- `query`: busca semântica;
- `filter`: restrição por metadados;
- `limit`/`k`: quantidade de resultados.

**Dev 1:** Exemplos?

**Dev 2:**

- “O que diz a Súmula 100?” → filtro `numero_sumula == 100`, sem busca semântica necessária;
- “Qual súmula fala sobre folha de pagamento da Câmara Municipal?” → query semântica, sem filtro obrigatório;
- “Cite três súmulas revogadas.” → filtro `status_atual == "revogada"` e `k = 3`.

**Dev 1:** Filtro e conteúdo têm papéis diferentes.

**Dev 2:** Exato. O filtro escolhe o subconjunto; o retrieval compara o conteúdo. A consulta pode usar um, outro ou ambos.

## 11. `top_k`, contexto e reranking

**Dev 1:** Por que `k = 10`?

**Dev 2:** Foi um valor demonstrativo, não uma regra. Mais chunks aumentam recall, mas também tokens, custo, latência e ruído.

**Dev 1:** Uma janela de contexto muito grande resolve isso?

**Dev 2:** Não. Mesmo modelos com janelas extensas se beneficiam de contexto selecionado.

**Dev 1:** Quando usar reranking?

**Dev 2:** Pode-se recuperar, por exemplo, 100 chunks e aplicar um reranker para reordenar e selecionar os mais relevantes. O valor final de `k` deve ser calibrado com perguntas reais, métricas e avaliação humana.

## 12. Prompt e resposta

**Dev 1:** O que entra no prompt final?

**Dev 2:** Persona, tarefa, regras, pergunta e contexto recuperado. Cada chunk é concatenado com metadados e conteúdo, preservando origem e separação.

**Dev 1:** Como as fontes são apresentadas?

**Dev 2:** O prompt exige resposta direta e referências padronizadas, incluindo número e status da súmula. Output estruturado reduz ambiguidades de parsing.

**Dev 1:** `invoke` ou `stream`?

**Dev 2:** `invoke` retorna tudo ao final; `stream` entrega tokens progressivamente.

## 13. LangGraph

**Dev 1:** Por que usar LangGraph se duas funções em sequência resolveriam?

**Dev 2:** Para explicitar estado, nós, transições e observabilidade. O estado contém pergunta, documentos, query, filtro, resposta e mensagens.

**Dev 1:** Quais nós foram criados?

**Dev 2:**

1. `retrieve`: gera consulta estruturada e recupera documentos;
2. `generate`: monta o contexto e produz a resposta.

Fluxo:

`START -> retrieve -> generate -> END`

**Dev 1:** Ele serve somente para IA?

**Dev 2:** Não. Também pode organizar funções convencionais quando estado e fluxo precisam ser rastreados.

## 14. Observabilidade

**Dev 1:** Como o Langfuse recebe os dados?

**Dev 2:** Por callback handler incluído no `RunnableConfig`, junto de `run_name`, tags, metadados, usuário e sessão.

**Dev 1:** O que foi observado em uma execução?

**Dev 2:** Aproximadamente 23 segundos no total: cerca de 6,22 segundos no retrieval e 15 segundos na geração, além de overhead. Outra tela indicava que aproximadamente 12 execuções custaram perto de US$ 0,01 na configuração da aula.

**Dev 1:** Por que isso é obrigatório em produção?

**Dev 2:** Porque permite identificar falhas, consultas geradas, fontes recuperadas, latência por nó, tokens, custo, usuário e sessão.

## 15. Interface e desacoplamento

**Dev 1:** Como foi construída a interface?

**Dev 2:** Com Streamlit, exibindo resposta em streaming, query semântica e filtros gerados.

**Dev 1:** Qual o papel do Context7?

**Dev 2:** Fornecer documentação atualizada e consumível por modelos, acelerando prototipação baseada em APIs reais.

**Dev 1:** Chainlit é alternativa?

**Dev 2:** Sim, especialmente para interfaces conversacionais mais especializadas. No caso real, foi integrado a React para maior customização.

**Dev 1:** Como integrar WhatsApp, Teams ou n8n?

**Dev 2:** Expondo a função do grafo por FastAPI. Assim, front-end e canais externos consomem endpoints sem acoplamento à implementação. Para WhatsApp, a recomendação foi usar a API oficial da Meta; integrações não oficiais tendem a sofrer bloqueios.

## 16. Testes demonstrados

**Dev 1:** O que ocorreu com “O que diz a Súmula 100?”?

**Dev 2:** Filtro exato pelo número, sem query semântica relevante.

**Dev 1:** E “Qual súmula fala sobre folha de pagamento da Câmara Municipal?”?

**Dev 2:** Busca semântica localizou a Súmula 100 pelo significado.

**Dev 1:** E “Súmula 126 de Marte”?

**Dev 2:** Não houve correspondência adequada. Sem “de Marte”, a busca pelo número funcionou.

## 17. Guardrails

**Dev 1:** Qual foi o exemplo mais importante?

**Dev 2:** “Qual é o entendimento do tribunal sobre licitação em Marte?”. Um sistema sem guardrail recuperou trechos reais sobre licitação e fabricou uma resposta plausível para a premissa absurda. O projeto do TCE rejeitou a pergunta como fora de domínio.

**Dev 1:** Então retrieval correto não basta.

**Dev 2:** Não. Guardrails devem:

- classificar domínio e intenção;
- rejeitar perguntas irrelevantes ou proibidas;
- validar se as fontes realmente sustentam a resposta;
- limitar custo, abuso e concorrência;
- registrar recusas e tentativas;
- preservar confiabilidade institucional.

## 18. Limitação de schema

**Dev 1:** Qual erro de modelagem apareceu?

**Dev 2:** `data_status` foi armazenada como string. Igualdade funcionava, mas perguntas como “depois de 2020” exigiam comparação de faixa.

**Dev 1:** Como corrigir?

**Dev 2:** Armazenar ano, mês e dia como inteiros ou utilizar tipo temporal compatível. O schema deve ser definido pelas operações futuras, não apenas pela facilidade de ingestão.

## 19. Ferramentas alternativas

**Dev 1:** LangSmith ou Langfuse?

**Dev 2:** A escolha prática foi Langfuse por self-hosting e pelos limites disponíveis na época.

**Dev 1:** Qdrant ou Pinecone?

**Dev 2:** Não houve afirmação de superioridade. Requisitos de operação, custo, implantação e familiaridade devem decidir.

**Dev 1:** Groq, PydanticAI e Agno?

**Dev 2:** Groq foi citado como possível alternativa de inferência; PydanticAI, como opção forte para outputs estruturados; Agno, como framework mais simples para agentes e integrações. LangChain e LlamaIndex permanecem ecossistemas mais amplos.

## 20. Caso real e conclusão

**Dev 1:** Como o sistema real era usado?

**Dev 2:** Analistas pesquisavam jurisprudência, processos, votos e entendimentos em aproximadamente 20 mil PDFs, distribuídos em várias collections e enriquecidos por metadados dos sistemas internos.

**Dev 1:** Qual a principal lição da aula?

**Dev 2:** RAG não é apenas enviar contexto a um LLM. É uma pipeline de engenharia cuja qualidade depende de:

- parser e chunking adequados ao domínio;
- metadados úteis e corretamente tipados;
- embeddings e collection compatíveis;
- combinação de semântica, léxico e filtros;
- `top_k` e reranking calibrados;
- prompt e fontes estruturados;
- orquestração explícita;
- observabilidade de custo, tokens e latência;
- guardrails;
- avaliação com perguntas reais.

**Dev 1:** Em uma frase?

**Dev 2:** Um modelo forte não compensa ingestão ruim, chunks quebrados, schema inadequado, retrieval ruidoso ou ausência de controle operacional.
