# Pipeline RAG completa — aula sintetizada como bate-papo entre dois desenvolvedores

- Termos da aula foram inferidos a partir de legenda gerada automaticamente, por conter erros.
- Video aula original: https://www.youtube.com/watch?v=9i6r90i17iA
- Repositório usado na aula:
  - https://github.com/caio-moliveira/rag-project
  - https://github.com/lvgalvao/data-engineering-roadmap
- NOTA: um revisão suscinta e rápida pode ser lida em `pipeline-rag-aula-revisao-rapida.md`.

> **Nota editorial:** o diálogo abaixo preserva o conteúdo técnico, as demonstrações, os exemplos, as ressalvas e as respostas relevantes da live, mas remove saudações prolongadas, sorteios, divulgação comercial e interrupções sem valor técnico. Termos inferidos incorretamente pela legenda automática foram normalizados, entre eles: **RAG, Qdrant, LangChain, LangGraph, Langfuse, LlamaIndex, MarkItDown, Context7, Chainlit, FastAPI, PydanticAI, Groq, dense, sparse, retrieval, query, reranking e `__init__.py`**.

## 1. O problema e a arquitetura

**Luciano:** Caio, três oportunidades de projeto chegaram praticamente juntas: uma empresa quer consultar, por linguagem natural, valores equivalentes aos que já apresenta em DAX no Power BI; outra quer conversar com informações internas; e uma terceira quer transformar RAG em produto revendável. Isso confirma que existe demanda real.

**Caio:** Existe porque praticamente toda empresa precisa analisar documentos, dados ou conhecimento interno. E RAG não precisa ser tratado como um bicho de sete cabeças. É uma pipeline parecida com ETL ou ELT: extraímos conteúdo, transformamos, armazenamos, recuperamos o que é relevante e usamos esse contexto para gerar a resposta.

**Luciano:** Então “conversar com PDF” é apenas um caso particular.

**Caio:** Exato. A fonte pode ser PDF, Word, TXT, JSON, banco de dados, planilha ou qualquer outra base externa. O fluxo da aula será:

1. carregar 126 PDFs de súmulas públicas do TCE;
2. converter e extrair o conteúdo;
3. dividir os documentos em chunks;
4. enriquecer cada chunk com metadados;
5. gerar embeddings;
6. armazenar tudo no Qdrant;
7. recuperar chunks por busca semântica, palavra-chave e filtros;
8. gerar a resposta com um LLM;
9. orquestrar o fluxo no LangGraph;
10. observar custo, latência, tokens e etapas no Langfuse;
11. expor uma interface em Streamlit.

**Luciano:** Qual stack?

**Caio:** Python, `uv` para projeto e dependências, OpenAI para geração e embeddings, Qdrant como banco vetorial, LangChain para abstrações de retrieval, LangGraph para orquestração, Langfuse para observabilidade, MarkItDown para converter os PDFs em Markdown e Streamlit para o front-end. Também aparecem LlamaIndex, Chainlit, Context7, FastAPI, PydanticAI, Groq, Pinecone e Agno como alternativas ou extensões.

---

## 2. Setup: Qdrant, Langfuse e OpenAI

**Luciano:** Comecemos pelo banco vetorial. O Qdrant exige uma instalação complicada?

**Caio:** Não. Para a demonstração, basta obter a imagem no Docker Desktop, executar o container na porta configurada e abrir o endpoint com `/dashboard`. O repositório da aula também contém o comando de terminal. Quando o serviço inicia, o dashboard mostra as collections e os points armazenados.

**Luciano:** “Point” no Qdrant corresponde ao quê?

**Caio:** Ao registro vetorial associado ao chunk. Na demonstração, os 126 PDFs produziram 356 chunks. A maioria das súmulas foi dividida em três partes; algumas, em duas.

**Luciano:** E o Langfuse?

**Caio:** Usamos o Langfuse Cloud por conveniência, mas ele também pode ser executado de forma self-hosted. Criamos uma organização, um projeto e uma credencial com `public key`, `secret key` e `host`. Essas variáveis, o host e a porta do Qdrant e a chave da OpenAI ficam no `.env`.

**Luciano:** O que ele mostra?

**Caio:** Cada execução pode registrar:

- input e output;
- nós executados;
- latência total e por etapa;
- quantidade de tokens de entrada e saída;
- custo estimado conforme o modelo;
- tags, metadados, nome da execução, usuário e sessão;
- traces, spans e grafo do fluxo;
- dashboards agregados por projeto, modelo, período e custo.

Na época da aula, foi mencionado um free tier de aproximadamente 50 mil registros no Langfuse Cloud. Como planos mudam, isso deve ser entendido como a condição apresentada na live, não como garantia atual. A vantagem decisiva para o projeto do TCE foi poder hospedar o Langfuse internamente.

**Luciano:** E a OpenAI?

**Caio:** É a parte paga da demonstração. O instrutor comenta que poucos dólares permitem muitos testes e mostra um consumo muito baixo no exemplo. As demais peças podem ser usadas gratuitamente quando executadas localmente, embora serviços cloud tenham seus próprios limites e preços.

---

## 3. RAG, chunks e a inexistência de uma estratégia universal

**Luciano:** Antes do código: o que exatamente é um chunk?

**Caio:** É um fragmento do conteúdo original criado para ser indexado e recuperado de forma independente. Em vez de enviar um PDF inteiro ao modelo, dividimos o texto em unidades que ainda preservem contexto suficiente para responder perguntas.

**Luciano:** Todos os documentos precisam ter o mesmo layout?

**Caio:** Não existe resposta universal. A estratégia depende da estrutura real dos documentos. Em um projeto com processos de 40 a 60 páginas, tentaram splitters recursivos, semânticos, por parágrafo e outras estratégias nativas. Várias falharam porque abreviações como “pág.”, “art.” e outros pontos internos eram interpretados como fim de sentença ou parágrafo. O melhor resultado foi obtido com uma expressão regular altamente específica.

**Luciano:** Ou seja, um splitter sofisticado não é automaticamente melhor que regex.

**Caio:** Exatamente. Em documentos financeiros, notas de corretagem e extratos, regras determinísticas também podem ser superiores a um LLM, especialmente quando não se pode errar vírgula, valor ou separador. Além de reduzir custo, isso aumenta previsibilidade.

**Luciano:** Quais opções os frameworks oferecem?

**Caio:** LangChain e LlamaIndex têm splitters por:

- quantidade de caracteres;
- parágrafos e sentenças;
- estrutura Markdown;
- HTML e JSON;
- código-fonte, incluindo classes e funções;
- semântica;
- separadores customizados;
- regex.

O `SentenceSplitter` do LlamaIndex foi destacado porque permitiu controlar separadores e expressões regulares com mais flexibilidade naquele projeto.

**Luciano:** E quando há vários layouts incompatíveis?

**Caio:** Uma estratégia robusta é criar collections distintas, cada uma com seu pipeline de chunking. No projeto real foram usadas seis collections, porque havia seis tipos de documento e cada tipo exigia tratamento próprio.

**Luciano:** Isso conduz a um RAG agêntico.

**Caio:** Sim. Um agente classifica a intenção da pergunta, escolhe a collection apropriada e utiliza um prompt especializado para aquele domínio. É possível manter muitas bases separadas sem obrigar uma única estratégia a servir para tudo.

---

## 4. Estratégia usada nos 126 PDFs

**Luciano:** Para as súmulas, por que não usar um splitter nativo?

**Caio:** Porque cada PDF é curto e tem uma estrutura relativamente estável: conteúdo principal, referências normativas e precedentes. Nesse caso, foi prático pedir ao LLM que identificasse essas três partes e devolvesse uma estrutura JSON.

**Luciano:** Então o próprio modelo faz o chunking.

**Caio:** Faz o chunking semântico orientado por prompt. O fluxo é:

1. MarkItDown converte o PDF em Markdown, preservando melhor a estrutura;
2. o texto é enviado ao LLM com instruções explícitas;
3. o LLM retorna três blocos: `conteudo_principal`, `referencias_normativas` e `precedentes`;
4. o JSON é limpo e validado;
5. cada bloco vira um documento com `page_content` e `metadata`;
6. os documentos são enviados ao Qdrant.

**Luciano:** Isso é mais lento do que somente aplicar um splitter.

**Caio:** Sim. A ingestão baseada em LLM tem custo e latência. Ela foi escolhida porque os PDFs eram pequenos e o objetivo era mostrar uma extração estruturada. Para milhares de documentos longos, é necessário avaliar se regex, parser, OCR, regras de layout ou splitters nativos oferecem melhor relação entre custo, precisão e escala.

---

## 5. Metadados: o componente que simplifica a recuperação

**Luciano:** Quais metadados foram extraídos?

**Caio:** Para cada chunk:

- número da súmula;
- data do status;
- ano;
- status atual;
- nome do PDF;
- tipo do chunk: conteúdo principal, referência normativa ou precedente;
- índice do chunk.

**Luciano:** Por que repetir os mesmos metadados em cada fragmento?

**Caio:** Porque cada chunk precisa ser filtrável de forma autônoma. Quanto mais metadados úteis e confiáveis existirem, menor será o espaço de busca e mais determinística será a recuperação.

**Luciano:** Dê um exemplo real.

**Caio:** No projeto do TCE, o banco relacional já continha número do processo, relator, data, natureza, páginas e diversos outros atributos. Isso permitia restringir buscas em uma base com cerca de 20 mil PDFs. Se o usuário informa um número de processo único, não faz sentido executar uma busca semântica em tudo: aplicamos um filtro direto.

**Luciano:** E quando uma informação não está explicitamente marcada no documento?

**Caio:** Eles usaram conhecimento do domínio como regra. A ementa geralmente estava nas primeiras páginas, embora documentos antigos nem sempre tivessem o rótulo “ementa”. Assim, quando alguém perguntava pela ementa, o retriever era instruído a priorizar ou filtrar as páginas 1 e 2. Isso reduz dezenas de páginas a um contexto muito menor.

**Luciano:** Logo, metadado não é apenas “data de criação” ou informação decorativa.

**Caio:** Não. Ele funciona como mecanismo de particionamento lógico, controle de escopo, redução de custo e aumento de precisão.

---

## 6. Inicialização do projeto Python

**Luciano:** Como o projeto foi preparado?

**Caio:** Foi criado um repositório e inicializado com `uv init`. A aula usou Python 3.13.3 e um ambiente virtual criado pelo `uv`. As dependências foram declaradas no `pyproject.toml` e sincronizadas com o `uv`, que se destacou pela instalação paralela e pelo desempenho decorrente de sua implementação em Rust. A biblioteca `tiktoken` aparece para contagem de tokens.

**Luciano:** Qual estrutura de diretórios foi adotada?

**Caio:** Dentro de `app`, o código foi separado aproximadamente em:

- `ingest/`: extração, transformação, embeddings e carga no Qdrant;
- `retrieval/`: configuração dos metadados e recuperação;
- `graph/`: prompt, estado e grafo RAG;
- `utils/`: configurações e utilidades;
- aplicação Streamlit.

Também foi criado um módulo central de settings para ler as variáveis do `.env`, evitando espalhar acessos diretos às variáveis de ambiente por todo o código.

**Luciano:** Houve um erro de importação no final.

**Caio:** Sim. A aplicação não reconheceu `app` como package. A demonstração passou a funcionar após a inclusão de `__init__.py`. A live atribuiu a opcionalidade desse arquivo ao Python 3.9, mas a nuance correta é: namespace packages sem `__init__.py` existem desde o Python 3.3; ainda assim, ferramentas, modos de execução, imports e estruturas de projeto podem exigir ou se beneficiar do arquivo. Na prática, incluí-lo resolveu aquele ambiente.

**Luciano:** E a afirmação de que uma versão nova do Python sempre executa código antigo?

**Caio:** Deve ser tratada com cautela. Python busca preservar compatibilidade, mas bibliotecas, extensões nativas, APIs removidas e mudanças de comportamento podem quebrar projetos. A compatibilidade precisa ser testada, especialmente em versões recém-lançadas.

---

## 7. Modelos, temperatura e embeddings

**Luciano:** Quais modelos foram configurados?

**Caio:** O GPT-4.1 mini foi usado para geração de respostas e para algumas tarefas de interpretação. O `text-embedding-3-large`, com 3.072 dimensões, foi usado para embeddings. O `text-embedding-3-small`, com 1.536 dimensões, foi citado como alternativa menor.

**Luciano:** Para que serve a temperatura?

**Caio:** Ela controla a aleatoriedade da geração. Em uma aplicação jurídica ou documental, a orientação foi usar temperatura `0` ou muito próxima de zero para reduzir variação e evitar reformulações criativas de conteúdo normativo. Em textos criativos, como posts ou poemas, uma temperatura maior pode ser adequada.

**Luciano:** Temperatura alta é sinônimo de alucinação?

**Caio:** Não diretamente. Ela aumenta variabilidade; dependendo da tarefa e do prompt, isso pode ampliar o risco de respostas menos aderentes. Em aplicações factuais, a recomendação é privilegiar consistência.

**Luciano:** E embedding?

**Caio:** É a representação numérica do texto. Cada chunk é convertido em um vetor, e a pergunta do usuário também. O banco compara esses vetores para localizar conteúdos semanticamente próximos.

**Luciano:** Mais dimensões significam automaticamente melhor resultado?

**Caio:** A live simplifica isso como “mais granularidade”. Em termos práticos, um vetor maior pode carregar maior capacidade representacional, mas qualidade não depende apenas da dimensão. Modelo, domínio, idioma, normalização, métrica, chunking e avaliação importam. O requisito incontornável é que a dimensão configurada na collection coincida com a dimensão produzida pelo modelo; trocar de 3.072 para 1.536 sem recriar ou reconfigurar a collection quebra a indexação.

---

## 8. Qdrant: dense, sparse e busca híbrida

**Luciano:** A collection usa dois bancos separados para busca semântica e palavra-chave?

**Caio:** Não. Uma única collection pode armazenar as representações necessárias para os dois mecanismos.

**Luciano:** Explique `dense` e `sparse`.

**Caio:** O vetor dense é usado para similaridade semântica: “carro” pode se aproximar de “automóvel” mesmo sem correspondência literal. O sparse privilegia termos e frequência, sendo útil para busca lexical e palavras exatas. A combinação forma uma busca híbrida.

**Luciano:** É possível dar pesos diferentes?

**Caio:** Sim. Dependendo da integração e da estratégia, podemos pedir, por exemplo, sete resultados semânticos e três lexicais em um total de dez, ou inverter a proporção quando termos exatos forem mais importantes.

**Luciano:** Qual métrica foi usada?

**Caio:** Similaridade por cosseno. A aula ressalta que Qdrant oferece outras métricas e configurações, mas o exemplo usa cosseno e vetores de 3.072 dimensões.

**Luciano:** Se o conteúdo exige exatamente a palavra “carro”, a busca lexical deve pesar mais.

**Caio:** Isso. Se o objetivo é capturar conceitos equivalentes, a busca semântica deve pesar mais. A escolha precisa ser validada contra perguntas reais.

---

## 9. Ingestão e criação da collection

**Luciano:** Como a collection é criada?

**Caio:** O código inicializa o cliente Qdrant com host e porta. Antes de carregar os documentos, verifica se a collection existe. Se não existir, cria-a com a dimensão, a métrica e as configurações dense/sparse esperadas.

**Luciano:** Depois percorre a pasta inteira?

**Caio:** Sim. Para cada PDF:

1. converte o arquivo;
2. extrai texto;
3. pede ao LLM chunks e metadados estruturados;
4. transforma cada item em documento;
5. gera embeddings;
6. grava os points no Qdrant.

**Luciano:** O payload contém o quê?

**Caio:** `page_content` e `metadata`. O dashboard permite inspecionar tanto o texto quanto os atributos associados.

**Luciano:** Para adaptar o projeto a outro catálogo, bastaria trocar os PDFs?

**Caio:** Não apenas. Em documentos semelhantes e curtos, troca-se a fonte e reescreve-se o prompt de extração para a estrutura desejada. Se os documentos tiverem outro layout, extensão ou complexidade, a estratégia de parser, chunking e metadados também deve mudar.

---

## 10. Self-query retrieval: consulta semântica mais filtros

**Luciano:** Como o sistema decide se deve buscar por significado ou filtrar metadados?

**Caio:** A aula usa `SelfQueryRetriever`, do LangChain. Primeiro declaramos cada metadado com `AttributeInfo`:

- nome do campo;
- tipo;
- descrição;
- exemplos;
- instruções de uso.

Também fornecemos uma descrição geral do conteúdo dos documentos.

**Luciano:** Essas descrições funcionam como prompt para o retriever.

**Caio:** Exato. O LLM interpreta a pergunta do usuário e produz uma consulta estruturada composta por:

- `query`: texto para busca semântica;
- `filter`: expressão sobre metadados;
- `limit` ou `k`: quantidade de resultados.

**Luciano:** Mostre os três casos centrais.

**Caio:**

- Pergunta: “O que diz a Súmula 100?”  
  Resultado: `query` sem conteúdo relevante e filtro `numero_sumula == 100`.

- Pergunta: “Qual súmula fala sobre folha de pagamento da Câmara Municipal?”  
  Resultado: consulta semântica com o núcleo “folha de pagamento Câmara Municipal” e nenhum filtro obrigatório.

- Pergunta: “Cite três súmulas com status revogada.”  
  Resultado: filtro `status_atual == "revogada"` e `k = 3`; a busca semântica pode ficar vazia.

**Luciano:** Então o metadado não substitui o conteúdo.

**Caio:** Não. O filtro escolhe o subconjunto de documentos; a busca lexical ou vetorial compara o conteúdo dos chunks. Uma pergunta pode usar somente filtro, somente semântica ou ambos.

**Luciano:** E para buscar um documento específico?

**Caio:** Use um atributo único, como número da súmula ou número do processo. Isso reduz o universo a um único documento ou conjunto previsível.

---

## 11. Top K, janela de contexto e reranking

**Luciano:** O exemplo usa `k = 10`. Por quê?

**Caio:** Apenas como valor demonstrativo. Não existe número universal. Cada chunk recuperado será enviado ao modelo como contexto, portanto aumentar `k` aumenta tokens, custo, latência e risco de ultrapassar a janela de contexto.

**Luciano:** A aula cita uma janela de um milhão de tokens para o GPT-4.1 mini.

**Caio:** Sim, mas uma janela grande não elimina a necessidade de seleção. Contexto excessivo pode introduzir ruído e encarecer a resposta.

**Luciano:** Como melhorar a seleção?

**Caio:** Uma estratégia é recuperar um conjunto maior, como 100 chunks, e aplicar reranking com um modelo especializado. O reranker atribui scores de relevância e reordena os resultados antes da geração. Também foram citados enriquecimento de contexto e outras etapas intermediárias.

**Luciano:** Portanto `top_k` deve ser calibrado com testes.

**Caio:** Com perguntas reais, métricas e avaliação humana. O valor precisa equilibrar recall, precisão, custo e tempo.

---

## 12. Prompt final e resposta estruturada

**Luciano:** Depois do retrieval, como o modelo recebe os dados?

**Caio:** O prompt final contém persona, tarefa, regras, pergunta do usuário e contexto recuperado. As variáveis `question` e `context` são interpoladas em um `ChatPromptTemplate`.

**Luciano:** Como o contexto é montado?

**Caio:** Para cada um dos até dez documentos, o código concatena metadados e `page_content`, separando os chunks de forma explícita. Isso permite ao modelo saber qual conteúdo pertence a qual súmula, status e fonte.

**Luciano:** Há regras de citação?

**Caio:** Sim. O prompt pede resposta direta e lista de fontes em formato padronizado, incluindo número e status da súmula. O fluxo usa output estruturado para evitar respostas difíceis de parsear.

**Luciano:** `invoke` ou `stream`?

**Caio:** Ambos são possíveis. `invoke` aguarda a resposta completa. `stream` envia tokens progressivamente, reproduzindo o comportamento visual de um chat.

---

## 13. LangGraph: estado, nós e fluxo

**Luciano:** O que o LangGraph adiciona? Não poderíamos chamar funções em sequência?

**Caio:** Poderíamos, mas o LangGraph torna o estado e a arquitetura explícitos. A aplicação define um estado compartilhado contendo, entre outros campos:

- pergunta;
- documentos recuperados;
- resposta;
- query semântica;
- filtro gerado;
- mensagens.

Cada nó lê e atualiza partes desse estado.

**Luciano:** Quais nós existem no exemplo?

**Caio:** Dois:

1. `retrieve`: recebe a pergunta, executa o self-query retriever e devolve documentos, query e filtros;
2. `generate`: recebe pergunta e documentos, monta o contexto e gera a resposta final.

O grafo fica:

`START -> retrieve -> generate -> END`

**Luciano:** Depois ele é compilado.

**Caio:** Sim. O construtor adiciona os nós, define o ponto de entrada, liga as arestas e compila o grafo. A comparação feita na live é que ele se parece visualmente com um fluxo de n8n, mas sua função aqui é controlar estado, transições e execução programática.

**Luciano:** Ele serve apenas para IA?

**Caio:** Não necessariamente. Foi citado um exemplo em que o LangGraph organizava funções comuns de uma aplicação, sem modelo de IA, para tornar o caminho dos dados observável.

---

## 14. Observabilidade no Langfuse

**Luciano:** Como o Langfuse é integrado?

**Caio:** O código instancia um callback handler do Langfuse e o inclui em um `RunnableConfig`. Nessa configuração podem ser enviados:

- `run_name`;
- tags;
- metadados;
- identificador do usuário;
- identificador da sessão;
- outros atributos de rastreamento.

**Luciano:** E o LangGraph aparece automaticamente?

**Caio:** Os callbacks registram as etapas executadas. No trace mostrado, era possível abrir o nó de retrieval, ver a consulta estruturada, os filtros, os dez documentos retornados e, depois, o nó de geração com pergunta, contexto, saída, tokens, custo e latência.

**Luciano:** Quais números apareceram na demonstração?

**Caio:** Uma execução levou aproximadamente 23 segundos: cerca de 6,22 segundos no retrieval e aproximadamente 15 segundos na geração final. O restante corresponde ao encadeamento e overhead. Em outra tela, o instrutor mostra que cerca de 12 execuções do pequeno projeto custaram aproximadamente um centavo de dólar.

**Luciano:** Isso é o que permite defender o projeto em produção.

**Caio:** Exato. Não basta responder. É preciso saber:

- qual etapa falhou;
- qual consulta foi construída;
- quais fontes foram recuperadas;
- quanto tempo cada nó consumiu;
- quantos tokens entraram e saíram;
- quanto custou;
- qual usuário e sessão geraram a execução.

Sem isso, fica difícil depurar, medir qualidade ou controlar gasto.

---

## 15. Interface: Streamlit, Context7 e Chainlit

**Luciano:** Como o front-end foi montado?

**Caio:** Em Streamlit. A interface recebe a pergunta, chama a função que executa todo o grafo e apresenta a resposta em streaming, além de exibir a query e os filtros produzidos pelo retriever.

**Luciano:** A live dá uma dica para aprender APIs de front-end rapidamente.

**Caio:** Usar o Context7, que disponibiliza documentações de frameworks em formato amigável para modelos. O desenvolvedor pode obter a documentação atualizada do Streamlit, fornecê-la ao modelo e pedir uma interface baseada em requisitos concretos. Isso não substitui compreender o framework, mas acelera prototipação.

**Luciano:** E Chainlit?

**Caio:** Foi apresentado como alternativa mais especializada em interfaces conversacionais. No projeto do TCE, a integração com React permitiu um front-end mais customizado e visualmente profissional. Streamlit aceita HTML, CSS e JavaScript, mas Chainlit ofereceu melhor encaixe naquele caso.

---

## 16. Demonstrações da recuperação

**Luciano:** O que aconteceu ao perguntar “O que diz a Súmula 100?”?

**Caio:** O sistema aplicou somente o filtro de metadado para o número 100. Não criou uma query semântica porque o número já identificava o documento de forma determinística.

**Luciano:** E “Qual súmula fala sobre folha de pagamento da Câmara Municipal?”?

**Caio:** Foi executada busca semântica. O sistema encontrou a Súmula 100 pelo significado da pergunta, sem depender do número.

**Luciano:** E ao pedir súmulas com status “mantida”?

**Caio:** O retriever aplicou `status_atual == "mantida"`, trouxe até dez documentos por causa do `top_k` e a resposta listou as fontes.

**Luciano:** Tentaram quebrar com “Súmula 126 de Marte”.

**Caio:** A consulta não encontrou resultado compatível, porque “de Marte” introduziu uma intenção sem respaldo na base. Ao perguntar somente “O que diz a Súmula 126?”, o filtro exato funcionou.

**Luciano:** Isso já é um guardrail?

**Caio:** Não. É apenas uma consequência da recuperação. Guardrails precisam ser explícitos.

---

## 17. Guardrails: custo, confiabilidade e abuso

**Luciano:** Qual foi o exemplo mais crítico da aula?

**Caio:** O teste “Qual é o entendimento do tribunal sobre licitação em Marte?”. O projeto do TCE possuía um guardrail que rejeitou a pergunta por estar fora do domínio. Outra ferramenta, premiada e com RAG funcional, recuperou processos que falavam genericamente de licitação e produziu uma resposta plausível, com referências, afirmando que seria possível realizar licitação em Marte.

**Luciano:** Como isso acontece?

**Caio:** O retriever encontra trechos semanticamente relacionados a “licitação”. O gerador recebe esses trechos como contexto autorizado e tenta satisfazer a pergunta. Se não houver regra de escopo, validação de relevância ou mecanismo de recusa, ele combina um contexto verdadeiro com uma premissa absurda e fabrica uma conclusão convincente.

**Luciano:** E usuários tentam quebrar o sistema.

**Caio:** Frequentemente. Perguntam sobre futebol, NASA, política, piadas, pessoas ou qualquer tema externo. Isso não é apenas problema de imagem: cada tentativa pode disparar retrieval, consumo de tokens, latência e concorrência.

**Luciano:** Então guardrails devem:

- classificar se a pergunta pertence ao domínio;
- rejeitar intenções proibidas ou irrelevantes;
- impedir que fontes fracamente relacionadas sejam tratadas como resposta;
- limitar custo e abuso;
- registrar recusas e tentativas;
- preservar confiabilidade institucional.

**Caio:** Exatamente. Em produção, guardrail não é acessório.

---

## 18. Limitação encontrada: datas armazenadas como string

**Luciano:** Qual falha o próprio autor não corrigiu antes da live?

**Caio:** `data_status` foi armazenada como string. Assim, o filtro de igualdade funcionava para uma data exata, mas perguntas como “Quais súmulas foram publicadas depois de 2020?” falhavam porque a consulta precisava de operadores `>`, `<`, `>=` ou `<=`.

**Luciano:** Qual solução foi proposta?

**Caio:** Armazenar valores comparáveis numericamente: ano, mês e dia como inteiros, ou um tipo temporal apropriado suportado pela estratégia escolhida. Com `ano = 2020` como inteiro, filtros de faixa tornam-se possíveis. A regra geral é definir o schema de metadados de acordo com as operações que a aplicação precisa executar.

---

## 19. Perguntas finais sobre ferramentas e arquitetura

**Luciano:** LangSmith ou Langfuse?

**Caio:** No projeto, começaram com LangSmith, mas o limite gratuito citado na aula foi atingido. Migraram para Langfuse principalmente por permitir self-hosting. A live compara aproximadamente 5 mil registros gratuitos no LangSmith com 50 mil no Langfuse Cloud naquele momento. Esses números são históricos e precisam ser verificados antes de qualquer decisão atual.

**Luciano:** Qdrant ou Pinecone?

**Caio:** O apresentador não havia usado Pinecone em produção e não afirmou superioridade técnica do Qdrant. Comparou a decisão a escolher PostgreSQL ou MySQL: há diferenças, mas requisitos, familiaridade, implantação, custo e operação determinam a escolha. Para a aula, Qdrant foi conveniente por ser simples de executar localmente.

**Luciano:** Groq em vez de OpenAI?

**Caio:** Ele havia testado apenas a interface, não a API em projeto. Comentou que o TCE avaliava servidores próprios e modelos open source, cenário em que provedores de inferência rápida ou modelos hospedados internamente poderiam ser considerados.

**Luciano:** PydanticAI?

**Caio:** Pydantic já era usado como boa prática para tipar e validar outputs estruturados. PydanticAI foi visto como uma extensão natural dessa especialidade. A avaliação da live é que ele pode ser muito bom para saídas estruturadas, enquanto LangChain e LlamaIndex ainda oferecem ecossistemas mais amplos de módulos e integrações. A escolha depende do problema.

**Luciano:** Agno?

**Caio:** Foi descrito como framework mais simples e amigável, capaz de montar agentes com poucas linhas. LangChain e LlamaIndex são poderosos, porém extensos; CrewAI também teria se tornado mais complexo ao evoluir. Agno foi citado como alternativa para produtividade e integração, inclusive com exemplos de FastAPI e WhatsApp.

---

## 20. Exposição por FastAPI, WhatsApp e desacoplamento

**Luciano:** Como disponibilizar o agente para WhatsApp?

**Caio:** A parte específica de integração Python com WhatsApp não foi demonstrada. A recomendação arquitetural foi separar o pipeline do front-end: a função que executa o LangGraph pode ser exposta como endpoint FastAPI.

**Luciano:** Assim, Streamlit deixa de chamar a implementação diretamente.

**Caio:** Isso. O front-end, WhatsApp, Teams, n8n ou outro consumidor chama a API. É possível ter vários agentes, cada um em um endpoint, e compor fluxos sem acoplar interface, regras e recuperação.

**Luciano:** Para WhatsApp, deve-se preferir a API oficial da Meta.

**Caio:** Sim. A live alerta que integrações não oficiais tendem a ser bloqueadas e que o uso oficial impõe preços, limites e boas práticas de envio. n8n foi citado como alternativa pragmática para a automação externa.

---

## 21. Caso real no TCE

**Luciano:** Quem usa o sistema real?

**Caio:** Analistas da área de negócio. Eles precisam pesquisar jurisprudência, localizar processos relacionados a determinado tema, ler votos e compreender o entendimento consolidado do tribunal.

**Luciano:** O fluxo recupera processos semanticamente relacionados e produz uma resposta estruturada.

**Caio:** Sim. O prompt final foi definido em conjunto com a área de negócio para apresentar o que realmente importa: processos, referências, entendimentos e elementos relevantes para análise. A base tinha aproximadamente 20 mil PDFs, diversas collections e muitos metadados provenientes dos sistemas internos.

**Luciano:** Isso mostra que o projeto da aula é deliberadamente simples.

**Caio:** É uma versão reduzida, mas cobre a espinha dorsal de uma solução real: ingestão, chunking, metadados, embeddings, retrieval, geração, grafo, interface, observabilidade e guardrails.

---

## 22. Conclusão técnica

**Luciano:** Resuma a principal lição.

**Caio:** RAG é uma pipeline de engenharia, não apenas uma chamada ao LLM. A qualidade final depende de decisões anteriores à geração:

- compreender o documento;
- escolher parser e chunking adequados;
- modelar metadados conforme as consultas;
- configurar embeddings e banco vetorial coerentemente;
- combinar semântica, palavra-chave e filtros;
- calibrar `top_k` e reranking;
- estruturar prompt e fontes;
- controlar estado e fluxo;
- observar custo, latência e execução;
- impor guardrails;
- avaliar com perguntas reais.

**Luciano:** Portanto, o modelo não corrige uma ingestão ruim.

**Caio:** Nem metadados ausentes, chunks quebrados, schema inadequado, retrieval ruidoso ou falta de observabilidade. Um RAG confiável nasce da pipeline inteira.

**Luciano:** E a implementação mínima demonstrada fica assim:

`PDFs -> MarkItDown -> extração estruturada -> chunks + metadados -> embeddings -> Qdrant -> SelfQueryRetriever -> LangGraph -> LLM -> Streamlit`

Com Langfuse observando o fluxo e guardrails protegendo domínio, custo e confiabilidade.

**Caio:** Exatamente. Esse é o projeto completo em sua forma essencial.
