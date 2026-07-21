# Preâmbulo

Leia integralmente `./AGENTS.md`, seus associados, o RCF vigente, o conteúdo sob o título **Prompt** e o estado real do repositório antes de analisar ou alterar qualquer artefato.

NOTA: se este arquivo não for o próprio `RCF.md` E o título "Prompt" não possuir um texto de prompt reale útil, então, considere que o prompt real estará contido dentro do arquivo `RCF.md`.

Preserve todas as regras, restrições, exceções, precedências, nuances, decisões e contratos válidos já existentes.

Analise antes de implementar.

# 1. Objetivo

Inicialize, construa ou refatore integralmente este repositório e seu `RCF.md` conforme:

1. as diretrizes de edição e operação definidas em `./AGENTS.md`;
2. seus arquivos associados;
3. este pedido;
4. o conteúdo Markdown contido sob o título **Prompt**;
5. os ajustes adicionais declarados antes desse título, quando existirem.

O conteúdo sob o título **Prompt** DEVE ser tratado como fonte primária dos requisitos de negócio específicos a serem normatizados no novo `RCF.md`, subordinado apenas à precedência já estabelecida por `./AGENTS.md`.

# 2. Eficiência Contextual

A IA DEVE compactar progressivamente o contexto durante toda a execução.

A compactação DEVE minimizar:

- tokens lidos;
- tokens emitidos;
- memória contextual;
- repetição;
- custo computacional;
- tempo de processamento.

A compactação NÃO DEVE reduzir:

- precisão;
- cobertura;
- qualidade;
- rastreabilidade;
- regras;
- exceções;
- dependências;
- decisões;
- pendências;
- contexto necessário à etapa atual;
- capacidade de retomada determinística.

Conteúdo já consolidado DEVE ser substituído por referência compacta sempre que isso reduzir o custo líquido sem perda informacional.

# 3. Ordem Obrigatória

A execução DEVE seguir estritamente esta sequência:

1. carregar integralmente no contexto o conteúdo Markdown sob o título **Prompt**;
2. ler `./AGENTS.md`, seus associados, o RCF existente e o estado real do repositório;
3. analisar requisitos, conflitos, lacunas, precedências, artefatos existentes e impactos;
4. criar ou atualizar as FTs;
5. separar claramente:
   - normatização do projeto;
   - futura implementação do código;

6. detalhar as FTs em etapas, tarefas, dependências, riscos, arquivos previstos, testes e critérios de aceite;
7. compactar o contexto;
8. criar ou reescrever integralmente `RCF.md`;
9. criar ou refatorar `README.md`;
10. validar somente a etapa normativa;
11. remover o artefato transitório que contenha esta solicitação, quando aplicável;
12. criar commit documental;
13. executar push;
14. compactar novamente o contexto;
15. encerrar sem implementar código;
16. informar explicitamente que a continuidade depende de autorização do desenvolvedor.

# 4. Separação entre Norma e Código

As FTs DEVEM distinguir inequivocamente:

## 4.1 Frente normativa

DEVE abranger:

- análise;
- taxonomia;
- contratos;
- RCF global;
- sub-RCFs indispensáveis;
- README;
- schemas declarativos indispensáveis;
- validação documental;
- commit;
- push.

## 4.2 Frente de implementação

DEVE permanecer planejada, mas NÃO iniciada.

Ela PODE prever:

- arquitetura;
- código;
- bibliotecas;
- dependências;
- testes;
- builds;
- integrações;
- automações;
- CI/CD;
- publicação.

A simples criação da FT de implementação NÃO autoriza sua execução.

# 5. Tratamento do Arquivo que Contém esta Solicitação

Quando esta solicitação estiver inserida no próprio `RCF.md`:

1. seu conteúdo DEVE ser integralmente lido;
2. seus requisitos DEVEM ser consolidados no contexto;
3. o arquivo real DEVE ser totalmente reescrito;
4. esta solicitação transitória DEVE ser substituída pelo novo conteúdo normativo;
5. nenhum fragmento instrucional transitório DEVE permanecer no RCF final, salvo quando convertido em norma aplicável.

Quando esta solicitação estiver contida em outro arquivo do repositório:

1. o arquivo DEVE permanecer disponível até a conclusão e validação do novo `RCF.md`;
2. depois disso, DEVE ser eliminado quando sua única finalidade for transportar esta solicitação;
3. ele NÃO DEVE ser eliminado se possuir outra função válida;
4. a exclusão DEVE integrar o commit documental.

Arquivos externos ao repositório NÃO DEVEM ser excluídos.

# 6. Construção do `RCF.md`

O `RCF.md` DEVE ser integralmente criado ou reescrito para:

- aderir ao padrão de `./AGENTS.md`;
- normatizar todo o projeto;
- incorporar os requisitos sob **Prompt**;
- incorporar os ajustes adicionais aplicáveis;
- preservar regras válidas existentes;
- corrigir conflitos, ambiguidades e lacunas;
- remover redundâncias com normas superiores;
- permanecer determinístico, autossuficiente e rastreável;
- separar regras globais de especializações;
- evitar detalhes internos de implementação quando múltiplas soluções puderem cumprir o contrato.

Conteúdo do RCF anterior PODE ser:

- preservado;
- condensado;
- reorganizado;
- especializado;
- transferido ao README;
- removido quando já estiver integralmente coberto por `./AGENTS.md`.

A remoção NÃO DEVE eliminar:

- regra específica;
- restrição;
- exceção;
- decisão arquitetural;
- contrato;
- requisito funcional;
- requisito não funcional;
- compatibilidade;
- rastreabilidade;
- nuance válida.

# 7. `README.md`

Um `README.md` DEVE existir na raiz.

Quando inexistente, DEVE ser criado.

Quando existente, DEVE ser refatorado somente quando necessário para cumprir este contrato.

Ele DEVE ser ultrassucinto, informativo e não normativo.

## 7.1 Descrição

O início do README DEVE conter descrição compacta do repositório, adequada também ao campo **About** do GitHub.

A descrição DEVE:

- identificar claramente o projeto;
- explicar sua finalidade;
- evitar prolixidade;
- não anunciar como implementado o que ainda for apenas planejado.

## 7.2 Referências normativas

O README DEVE conter links para:

- `RCF.md`;
- `AGENTS.md`.

Cada link DEVE possuir explicação ultrassucinta:

- `RCF.md`: normas, contratos e requisitos do projeto;
- `AGENTS.md`: processo, precedência e modus operandi da IA no repositório.

## 7.3 Badges e indicadores

O README DEVE conter badges ou indicadores adequados ao contexto do projeto.

Eles DEVEM representar, quando aplicável:

- validações do repositório;
- status `pass` ou `fail`;
- licença;
- linguagens;
- versões;
- sistemas operacionais;
- client-side;
- server-side;
- workers;
- runtimes;
- builds;
- cobertura;
- pacote;
- release;
- manutenção;
- compatibilidade;
- outros indicadores relevantes.

Badges referentes a capacidades ainda não implementadas DEVEM ser:

- omitidos;
- ou identificados inequivocamente como planejados, pendentes ou não disponíveis.

Nenhum badge DEVE indicar aprovação, cobertura, compatibilidade ou disponibilidade não verificada.

O badge principal de validação DEVE apontar para o workflow ou mecanismo real correspondente quando este existir.

## 7.4 Evolução dos badges

O RCF DEVE normatizar que badges e indicadores do README:

- DEVEM acompanhar a evolução do escopo;
- DEVEM ser atualizados quando linguagens, runtimes, plataformas, builds, testes, licenças ou status mudarem;
- NÃO DEVEM permanecer obsoletos;
- NÃO DEVEM apresentar informação enganosa;
- DEVEM ser removidos quando deixarem de representar o estado real.

## 7.5 Autoria e licença

Ao final, o README DEVE conter seção apropriada com:

- nome do autor;
- link para seu site;
- e-mail, quando disponível e autorizado;
- nome da licença;
- link para o texto integral da licença;
- texto ultrassucinto de licença ou atribuição comumente usado em cabeçalhos de código.

A IA NÃO DEVE inventar:

- nome;
- e-mail;
- site;
- licença;
- URL;
- titularidade.

Dados ausentes DEVEM ser recuperados do repositório ou registrados como pendência.

# 8. Badges Antes da Implementação

Quando workflows, testes, pacotes ou builds ainda não existirem:

- o README NÃO DEVE exibir status de aprovação fictício;
- o RCF DEVE normatizar os badges futuros;
- as FTs de implementação DEVEM prever sua criação;
- indicadores estáticos PODEM informar estado documental, planejamento ou licença quando verdadeiros;
- indicadores dinâmicos somente DEVEM ser adicionados após existir fonte real verificável.

# 9. FTs

As FTs DEVEM ser criadas ou atualizadas antes da edição normativa.

Elas DEVEM contemplar, quando aplicável:

- leitura e consolidação;
- análise do repositório;
- refatoração do RCF;
- sub-RCFs;
- README;
- badges;
- autoria;
- licença;
- schemas;
- validação documental;
- remoção do arquivo transitório;
- commit documental;
- push;
- futura implementação;
- testes;
- workflows;
- bibliotecas;
- builds;
- publicação.

Cada FT DEVE declarar:

- identificador;
- nome;
- objetivo;
- prioridade;
- status;
- escopo;
- não escopo;
- dependências;
- etapas;
- tarefas;
- arquivos previstos;
- riscos;
- testes;
- critérios de aceite;
- ordem de execução;
- vínculo com o RCF.

A FT normativa DEVE ser concluída nesta execução.

A FT de código DEVE permanecer pendente de autorização explícita.

# 10. Validação Documental

Antes do commit, a IA DEVE validar:

- aderência a `./AGENTS.md`;
- precedência;
- cobertura do conteúdo sob **Prompt**;
- incorporação dos ajustes anteriores;
- preservação das regras válidas;
- ausência de redundância desnecessária;
- ausência de contradições;
- separação entre norma e implementação;
- completude do RCF;
- existência e concisão do README;
- validade dos links internos;
- veracidade dos badges;
- autoria;
- licença;
- rastreabilidade entre requisitos, FTs e RCF;
- ausência da solicitação transitória no artefato final;
- ausência de implementação antecipada.

A IA NÃO DEVE declarar como realizada qualquer validação não executada.

# 11. Commit e Push

Após concluir e validar a etapa normativa, a IA DEVE obrigatoriamente:

1. revisar o diff;
2. confirmar que somente alterações documentais e normativas autorizadas foram incluídas;
3. criar commit;
4. utilizar mensagem sucinta e descritiva;
5. executar push para o destino configurado;
6. verificar o resultado;
7. registrar hash, branch, remote e status.

A IA NÃO DEVE:

- incluir implementação de código no commit;
- incluir segredos;
- ignorar falha do push;
- declarar sucesso quando o push não tiver sido confirmado.

Se commit ou push forem impedidos por:

- ausência de repositório Git;
- falta de remote;
- autenticação;
- proteção de branch;
- permissão;
- conflito;
- indisponibilidade externa;

a IA DEVE:

- preservar todo o trabalho;
- registrar o impedimento exato;
- fornecer os comandos necessários;
- NÃO simular conclusão.

# 12. Compactação Após o Push

Após commit e push, ou após registrar impedimento externo, a IA DEVE compactar novamente o contexto.

A compactação final DEVE preservar:

- FTs;
- estado da norma;
- decisões;
- arquivos alterados;
- commit;
- push;
- impedimentos;
- pendências;
- ponto exato de retomada;
- condição para iniciar a implementação.

# 13. Proibição de Implementação Antecipada

Nesta execução, a IA NÃO DEVE:

- implementar código funcional;
- escolher definitivamente bibliotecas;
- instalar dependências;
- importar bibliotecas;
- alterar arquitetura executável;
- criar builds;
- criar pacote;
- implementar testes de código;
- implementar workflows de código;
- iniciar CI/CD funcional;
- publicar releases;
- executar a FT de implementação.

Bibliotecas e tecnologias PODEM ser mencionadas nas FTs ou no RCF apenas como:

- requisitos de avaliação;
- alternativas;
- critérios;
- decisões pendentes;
- direções não vinculantes.

# 14. Continuidade

A implementação de código, seleção definitiva de tecnologia, instalação de dependências, importação de bibliotecas, criação de builds e execução das FTs técnicas somente PODEM começar após solicitação nova, explícita e inequívoca do desenvolvedor.

Ao término desta execução, a IA DEVE informar expressamente:

> A etapa normativa foi concluída. Para prosseguir, o desenvolvedor deve autorizar explicitamente o início da etapa de implementação do código.

Essa mensagem NÃO DEVE ser interpretada como autorização automática.

# 15. Saída Final

A resposta final DEVE ser ultrassucinta e conter:

- RCF criado ou refatorado;
- sub-RCFs criados, quando existirem;
- README criado ou refatorado;
- FTs criadas ou atualizadas;
- arquivo transitório removido, quando aplicável;
- validações executadas;
- commit;
- push;
- impedimentos;
- pendências;
- confirmação de que nenhum código funcional foi implementado;
- solicitação explícita de autorização para continuar.

# Prompt

<INSERIR AQUI O PROMPT MARKDOWN ESPECÍFICO DO PROJETO>

# Prompt

````markdown
```text
# 1. Objetivo

Projete e implemente uma ferramenta capaz de pesquisar conceitos, palavras ou expressões em uma coleção arbitrária de publicações textuais PDF e EPUB, distribuídas em diretórios de profundidade ilimitada.

As publicações PODEM incluir livros, compilações, devocionais, revistas, jornais, periódicos, edições distintas, traduções e títulos disponíveis simultaneamente em PDF e EPUB.

Cada pesquisa individual DEVE gerar ou atualizar exatamente um arquivo Markdown consolidado, contendo todas as ocorrências encontradas em toda a coleção, agrupadas, deduplicadas, referenciadas e traduzidas conforme este contrato.

A busca DEVE localizar:

- correspondências literais;
- variantes ortográficas e morfológicas;
- flexões;
- traduções;
- sinônimos;
- locuções;
- paráfrases;
- expressões semanticamente equivalentes;
- formulações em `pt-BR` e `en-US`.

A implementação DEVE priorizar precisão, rastreabilidade, reutilização de tecnologia existente, resiliência, processamento incremental e revisão controlada de casos ambíguos.

# 2. Direção Tecnológica sem Predeterminação

Nenhuma linguagem, biblioteca, motor, índice, modelo ou arquitetura DEVE ser escolhida por preferência, reputação ou conveniência isolada.

A seleção DEVE resultar de comparação objetiva quanto a:

- qualidade;
- manutenção;
- licença;
- compatibilidade;
- portabilidade;
- precisão;
- desempenho;
- memória;
- instalação;
- segurança;
- funcionamento local;
- capacidade de integração;
- maturidade;
- testes;
- custo operacional;
- substituibilidade.

Node.js, Python, Ruby, Rust, Java, C#, shell ou arquitetura híbrida PODEM ser utilizados.

Quando houver implementação própria em Node.js, ela DEVE ser escrita em TypeScript. Essa obrigação NÃO se aplica a dependências de terceiros.

Direções prováveis, não obrigatórias:

- TypeScript para CLI, orquestração, configuração, persistência e geração Markdown;
- Python para extração documental, NLP, embeddings, reranking ou tradução;
- Rust ou mecanismos nativos para indexação ou processamento intensivo;
- SQLite ou banco equivalente para persistência;
- índice invertido para busca lexical;
- índice vetorial para busca semântica.

A arquitetura híbrida somente DEVE ser adotada quando o benefício superar a complexidade adicional.

# 3. Reutilização Obrigatória

A implementação NÃO DEVE recriar algoritmos, extratores, parsers, tokenizadores, modelos, índices, mecanismos de tradução ou funções já oferecidas por solução adequada.

Antes de implementar qualquer capacidade, DEVE avaliar bibliotecas ou componentes existentes quanto a:

- funcionalidade;
- manutenção;
- cobertura de testes;
- licença;
- segurança;
- precisão;
- desempenho;
- tamanho;
- compatibilidade;
- adequação ao corpus;
- possibilidade de substituição.

Código próprio somente DEVE ser criado para:

- integração;
- adaptação;
- composição;
- regras editoriais específicas;
- lacuna funcional comprovada;
- incompatibilidade técnica;
- dependência desproporcional;
- ausência de solução mantida.

Tecnologias potencialmente avaliáveis incluem, sem obrigação de adoção:

- PyMuPDF ou equivalentes para PDF;
- parsers EPUB estruturais;
- Hugging Face Tokenizers;
- spaCy, Stanza ou equivalentes;
- SQLite FTS5, Lucene, Xapian, Tantivy ou equivalentes;
- Sentence Transformers ou modelos multilíngues equivalentes;
- Cross-Encoders;
- FAISS, HNSW, Qdrant, LanceDB ou equivalentes;
- RapidFuzz;
- MinHash, SimHash ou LSH;
- Argos Translate, MarianMT, NLLB ou equivalentes.

# 4. Escopo e Descoberta

A ferramenta DEVE:

- receber diretório `target` configurável;
- percorrer recursivamente toda a árvore;
- suportar profundidade arbitrária;
- processar qualquer quantidade de arquivos;
- funcionar fora da raiz;
- tolerar nomes não padronizados;
- detectar arquivos novos, alterados, removidos ou duplicados.

Ela NÃO DEVE depender de:

- estrutura fixa;
- profundidade conhecida;
- nome específico de diretório;
- quantidade predeterminada;
- execução no diretório dos livros;
- importação prévia em software externo.

OCR NÃO DEVE ser executado por padrão em arquivos textuais.

Quando a extração falhar, a ferramenta DEVE tentar rotas alternativas limitadas, registrar o problema, continuar os demais arquivos e NÃO inventar conteúdo.

# 5. Publicação Lógica

PDF e EPUB equivalentes DEVEM representar uma única publicação lógica, sem gerar citações duplicadas.

A associação DEVE considerar, quando disponíveis:

- título;
- autor;
- idioma;
- editora;
- edição;
- ISBN;
- ISSN;
- volume;
- número;
- data;
- metadados;
- nome normalizado;
- hash;
- fingerprint;
- similaridade textual;
- estrutura e ordem dos capítulos.

Arquivos de mesmo título NÃO DEVEM ser fundidos quando houver diferença material de:

- edição;
- tradução;
- data;
- conteúdo;
- paginação;
- revisão.

Quando PDF e EPUB forem equivalentes, RECOMENDA-SE:

- EPUB para estrutura, capítulos, seções e parágrafos;
- PDF para paginação e representação editorial;
- alinhamento textual entre ambos;
- fallback recíproco.

Associações incertas DEVEM permanecer separadas ou marcadas para revisão.

# 6. Extração de PDF

A extração DEVE preservar, quando disponíveis:

- páginas físicas;
- números impressos;
- palavras;
- linhas;
- blocos;
- coordenadas;
- fontes;
- estilos;
- colunas;
- títulos;
- subtítulos;
- notas;
- cabeçalhos;
- rodapés;
- datas;
- volume;
- número;
- edição.

A reconstrução NÃO DEVE concatenar indiscriminadamente o texto da página.

Cabeçalhos, rodapés e números de página DEVEM ser identificados por combinação de:

- repetição;
- posição;
- frequência;
- tipografia;
- baixa variação;
- padrões;
- distância do corpo.

Um elemento somente DEVE ser removido quando a confiança for suficiente.

# 7. Extração de EPUB

A extração DEVE respeitar:

- container;
- manifesto;
- spine;
- XHTML;
- `nav`;
- NCX;
- landmarks;
- page list;
- headings;
- capítulos;
- seções;
- parágrafos;
- notas;
- metadados;
- datas;
- edição;
- volume;
- número.

A ordem DEVE seguir o spine.

Estrutura semântica DEVE ser preservada.

Sem paginação estável:

- NÃO DEVE inventar páginas;
- DEVE usar página do PDF equivalente quando houver alinhamento confiável;
- caso contrário, DEVE usar localização EPUB determinística e indicar ausência de página.

# 8. Reconstrução Editorial

A unidade de citação é o parágrafo semântico integral.

A ferramenta DEVE reconstruir parágrafos:

- quebrados por linhas;
- atravessando páginas;
- com hifenização editorial;
- divididos por blocos;
- interrompidos por cabeçalho ou rodapé;
- distribuídos em colunas.

DEVE distinguir:

- quebra visual de linha;
- quebra real de parágrafo;
- mudança de página;
- mudança de coluna;
- título;
- subtítulo;
- lista;
- nota;
- bloco de citação;
- unidade editorial;
- mudança de data.

A decisão DEVERIA combinar:

- geometria;
- pontuação;
- capitalização;
- recuo;
- espaçamento;
- tipografia;
- continuidade sintática;
- segmentação linguística;
- estrutura EPUB;
- contexto anterior e posterior.

Parágrafos distintos NÃO DEVEM ser unidos por heurística isolada.

Parágrafo entre páginas DEVE referenciar todas elas, preferencialmente como intervalo.

# 9. Referências

Cada citação DEVE preservar, quando aplicável:

- título;
- autor;
- capítulo;
- seção;
- página ou intervalo;
- edição;
- volume;
- número;
- data;
- idioma;
- localização EPUB;
- fonte PDF ou EPUB.

A identificação DEVE usar evidência em ordem de confiança:

1. estrutura explícita;
2. metadados confiáveis;
3. conteúdo editorial;
4. página de rosto, sumário ou expediente;
5. filename;
6. diretório;
7. fallback marcado.

Metadados NÃO DEVEM ser inventados.

# 10. Publicações Datadas

Devocionais, revistas, jornais e periódicos DEVEM incluir data editorial ou de destinação na referência.

Exemplos:

- devocional: dia e mês da meditação;
- revista semanal: semana ou intervalo;
- revista mensal: mês e ano;
- jornal: data completa;
- periódico: volume, número e período;
- fascículo: edição e data.

A data DEVE ser associada à unidade textual vigente, não apenas ao arquivo.

A ferramenta NÃO DEVE confundir data editorial com:

- criação do arquivo;
- modificação;
- extração;
- execução;
- indexação.

Datas de filesystem somente PODEM ser usadas com configuração explícita ou confirmação adicional.

# 11. Consulta e Expansão

A consulta PODE ser:

- palavra;
- expressão;
- frase;
- conceito em linguagem natural;
- termos obrigatórios;
- exclusões.

A expansão DEVE considerar, de forma controlada:

- tradução;
- flexão;
- lematização;
- singular e plural;
- gênero;
- conjugação;
- variantes ortográficas;
- sinônimos;
- locuções;
- paráfrases;
- expressões equivalentes;
- formas correlatas;
- termos configurados manualmente.

A expansão NÃO DEVE tornar a consulta excessivamente ampla.

Cada variante DEVE registrar:

- texto;
- idioma;
- origem;
- método;
- peso;
- confiança;
- relação com a consulta original.

O usuário DEVE poder:

- revisar;
- incluir;
- excluir;
- fixar expressões;
- limitar idiomas;
- definir thresholds;
- usar busca literal;
- usar busca híbrida.

# 12. Registro da Pesquisa

No início do Markdown DEVE constar:

- termo original;
- idioma original;
- idiomas pesquisados;
- modo de busca;
- thresholds;
- inclusões;
- exclusões;
- traduções;
- flexões;
- sinônimos;
- expressões equivalentes;
- paráfrases;
- todas as variantes efetivamente pesquisadas.

Variantes efetivamente usadas NÃO DEVEM ser omitidas.

Variantes geradas e rejeitadas PODEM permanecer apenas no relatório técnico.

# 13. Busca Híbrida

A recuperação DEVE combinar, quando proporcional:

1. correspondência literal;
2. normalização;
3. busca por frase;
4. análise morfológica;
5. sinônimos;
6. fuzzy matching;
7. busca semântica multilíngue;
8. reranking contextual;
9. filtros linguísticos;
10. classificação por confiança.

A busca lexical NÃO DEVE ser substituída pela semântica.

A busca semântica NÃO DEVE decidir isoladamente.

RECOMENDA-SE pipeline:

1. expansão da consulta;
2. geração lexical de candidatos;
3. geração vetorial de candidatos;
4. união;
5. fusão de rankings;
6. reranking;
7. análise de negação, modalidade, números, datas e termos críticos;
8. threshold;
9. classificação;
10. evidência.

Reciprocal Rank Fusion ou técnica equivalente PODE combinar rankings heterogêneos.

# 14. Tokenização e Representações

A ferramenta DEVE preservar separadamente:

- texto original;
- texto estrutural;
- texto normalizado;
- tokens;
- lemas;
- offsets;
- fingerprints;
- embeddings, quando usados.

A normalização DEVE permitir localizar a correspondência e recuperar exatamente o texto original.

Tokenização, normalização e segmentação NÃO DEVEM destruir:

- acentuação original;
- pontuação relevante;
- grafia editorial;
- localização;
- referência;
- offsets.

# 15. Indexação

A ferramenta DEVERIA manter índice persistente e incremental.

O índice DEVE permitir:

- processamento incremental;
- consultas repetidas;
- retomada;
- atualização;
- remoção de dados obsoletos;
- associação PDF–EPUB;
- busca lexical;
- busca semântica;
- deduplicação;
- rastreabilidade.

O modelo DEVE armazenar:

- publicações;
- formatos;
- edições;
- capítulos;
- seções;
- parágrafos;
- páginas;
- datas;
- referências;
- texto original;
- texto normalizado;
- tokens;
- fingerprints;
- embeddings;
- hashes;
- confiança;
- versão do extrator;
- checkpoints;
- pesquisas.

O Markdown NÃO DEVE ser a fonte primária de persistência.

# 16. Deduplicação

## 16.1 Exata

Textos equivalentes após normalização segura DEVEM compartilhar uma única citação lógica.

A normalização PODE tratar:

- espaços;
- quebras visuais;
- hifenização;
- Unicode;
- aspas;
- travessões;
- capitalização;
- pontuação não material;
- artefatos editoriais.

## 16.2 Aproximada

Variações mínimas PODEM ser consolidadas mediante combinação de:

- n-gramas;
- Jaccard;
- MinHash;
- SimHash;
- Levenshtein;
- Damerau–Levenshtein;
- Jaro–Winkler;
- LCS;
- RapidFuzz ou equivalente;
- embeddings;
- alinhamento de tokens.

A ferramenta DEVE verificar diferenças críticas, incluindo:

- negação;
- modalidade;
- condição;
- agente;
- objeto;
- datas;
- números;
- nomes;
- intensidade;
- conclusão;
- significado.

Diferença pequena em caracteres NÃO DEVE implicar equivalência semântica.

Resultados DEVEM poder ser classificados como:

- consolidar automaticamente;
- manter separados;
- revisão recomendada.

## 16.3 Referências

Antes de adicionar uma citação, DEVE verificar se ela já existe no resultado ou no Markdown da mesma pesquisa.

Se já existir:

- NÃO DEVE criar novo bloco;
- DEVE adicionar somente referência ausente;
- NÃO DEVE repetir referência.

Compilações, antologias e republicações DEVEM gerar múltiplas referências sob uma única citação quando o texto for equivalente.

# 17. Alinhamento PDF–EPUB

Quando ambos existirem, a ferramenta DEVERIA alinhar estrutura EPUB e paginação PDF.

O alinhamento PODE combinar:

- hashes;
- âncoras exatas;
- n-gramas;
- fingerprints;
- similaridade lexical;
- embeddings;
- LCS;
- programação dinâmica;
- Needleman–Wunsch;
- Smith–Waterman;
- Dynamic Time Warping;
- alinhamento monotônico.

A ordem textual DEVERIA ser explorada para reduzir ambiguidades.

Cada associação DEVE possuir confiança.

# 18. Identificação de Idioma

O idioma DEVE ser inferido por combinação de:

- metadados;
- detecção documental;
- detecção por parágrafo;
- vocabulário;
- modelo de identificação;
- contexto.

A ferramenta DEVE suportar conteúdo misto.

A identificação de idioma NÃO DEVE depender exclusivamente de filename.

# 19. Tradução

Toda citação original em `en-US` DEVE ser imediatamente seguida por tradução `pt-BR`.

A tradução DEVE:

- abranger somente o texto;
- NÃO traduzir referência;
- usar bloco de citação;
- ser identificada como **Tradução livre**;
- preservar sentido e tom;
- permanecer separada do original.

Tradução local open source DEVERIA ser preferida quando possuir qualidade suficiente.

API pública e gratuita PODE ser usada quando:

- autorizada;
- estável;
- adequada ao volume;
- compatível com privacidade;
- configurável;
- resiliente.

Conteúdo NÃO DEVE ser enviado a terceiros sem autorização explícita.

Traduções DEVEM usar cache por hash, idiomas e versão do tradutor.

Falha de tradução NÃO DEVE remover a citação original.

# 20. Arquivo Único por Pesquisa

Cada pesquisa individual DEVE possuir exatamente um Markdown principal.

Ele DEVE consolidar:

- consulta;
- variantes;
- metadados;
- resultados em `pt-BR`;
- resultados em `en-US`;
- traduções;
- referências;
- contagens;
- resumo.

A identidade da pesquisa DEVE considerar:

- consulta original;
- idiomas;
- inclusões;
- exclusões;
- modo;
- modelos;
- configurações;
- thresholds.

O arquivo NÃO DEVE misturar pesquisas materialmente distintas.

Atualizações DEVEM ser:

- idempotentes;
- atômicas;
- recuperáveis;
- determinísticas.

RECOMENDA-SE escrever em arquivo temporário validado antes da substituição.

# 21. Estrutura Markdown

Estrutura equivalente:

# Resultados da pesquisa: <consulta>

## Consulta e variantes

- termo original;
- idioma;
- modo;
- thresholds;
- variantes por idioma e categoria;
- exclusões.

## Português — Brasil

### <Publicação>

#### Citação <n>

> <parágrafo>

**Referências:**

- *<Livro>*, cap. “<Capítulo>”, p. <página>.
- *<Devocional>*, meditação de <data>, p. <página>.
- *<Revista>*, v. <volume>, n. <número>, <período>, p. <página>.
- *<Jornal>*, <data>, p. <página>.

---

## Inglês — Estados Unidos

### <Publicação>

#### Citação <n> — Original

> <texto>

**Referências:**

- ...

##### Tradução livre

> <tradução>

---

A referência DEVE aparecer somente junto ao original.

Citações DEVEM possuir separação visual consistente.

# 22. Atualização de Markdown Existente

Quando o arquivo da mesma pesquisa existir, a ferramenta DEVE:

1. validar identidade;
2. analisar estruturalmente o Markdown;
3. recuperar citações;
4. recuperar referências;
5. reconstruir fingerprints;
6. comparar novos resultados;
7. adicionar apenas conteúdo ausente;
8. preservar conteúdo válido;
9. atualizar contagens;
10. ordenar deterministicamente.

A análise NÃO DEVE depender apenas de busca textual bruta.

Identificadores PODEM ser preservados por:

- front matter;
- comentários HTML;
- sidecar;
- índice;
- mecanismo equivalente.

Metadados técnicos NÃO DEVEM prejudicar a leitura.

# 23. Confiança e Auditabilidade

Cada inferência relevante DEVE possuir evidência e confiança separadas, incluindo:

- extração;
- estrutura;
- título;
- capítulo;
- página;
- data;
- idioma;
- associação PDF–EPUB;
- correspondência lexical;
- correspondência semântica;
- deduplicação;
- tradução.

Classificações PODEM incluir:

- confirmado;
- alta confiança;
- provável;
- revisão recomendada;
- indeterminado;
- rejeitado.

A ferramenta NÃO DEVE apresentar inferência como certeza sem evidência.

# 24. Failsafe

Failsafe significa concluir todo o trabalho processável, isolar falhas, preservar resultados válidos e informar precisamente o que não pôde ser concluído.

A ferramenta DEVE possuir:

- isolamento por arquivo;
- checkpoints;
- retomada;
- cache;
- timeouts;
- tentativas limitadas;
- backoff limitado;
- fallbacks;
- fila de problemas;
- logs estruturados;
- escrita atômica;
- recuperação;
- resumo final.

Ela NÃO DEVE:

- entrar em loop infinito;
- tentar indefinidamente;
- interromper toda a coleção por falha isolada;
- ocultar falhas;
- inventar dados;
- descartar arquivo silenciosamente;
- duplicar resultados após retomada;
- corromper saída existente.

Cada fallback DEVE declarar:

- condição;
- limite;
- resultado;
- motivo;
- próximo estado.

# 25. Desempenho

A ferramenta DEVE evitar carregar toda a coleção simultaneamente.

RECOMENDA-SE:

- streaming;
- lotes;
- filas;
- concorrência limitada;
- workers;
- cache;
- indexação incremental;
- persistência;
- processamento por fases.

A concorrência DEVE respeitar:

- CPU;
- memória;
- disco;
- APIs;
- estabilidade dos extratores.

Configurações DEVEM incluir:

- workers;
- lotes;
- cache;
- memória;
- timeout;
- tentativas;
- thresholds;
- idiomas;
- tradutor;
- logs;
- rede.

# 26. Segurança e Privacidade

A operação DEVE ser local por padrão.

A ferramenta NÃO DEVE:

- enviar publicações completas externamente;
- executar JavaScript de EPUB;
- confiar em filenames;
- permitir path traversal;
- extrair fora de área controlada;
- sobrescrever sem validação;
- registrar conteúdo integral desnecessariamente;
- expor paths ou dados sensíveis.

EPUBs DEVEM ser tratados como arquivos não confiáveis.

A extração DEVE proteger contra:

- Zip Slip;
- expansão excessiva;
- bomba de compressão;
- entidades externas;
- conteúdo malformado;
- loops;
- arquivos abusivos.

# 27. CLI e Configuração

Interface equivalente:

search-publications \
  --target <diretório> \
  --query "<termo ou conceito>" \
  --languages pt-BR,en-US \
  --output <pesquisa.md>

A CLI DEVERIA permitir:

- indexar;
- pesquisar;
- reconstruir índice;
- listar publicações;
- inspecionar associações;
- exibir variantes;
- definir thresholds;
- selecionar tradutor;
- operar offline;
- retomar;
- atualizar resultado;
- filtrar autor;
- filtrar idioma;
- filtrar data;
- filtrar tipo;
- gerar diagnóstico.

A configuração DEVE aceitar, em precedência explícita:

1. CLI;
2. arquivo;
3. ambiente;
4. padrões seguros.

A saída DEVE ser:

- sucinta;
- colorida quando suportado;
- desativável;
- legível por humanos;
- processável por IA;
- disponível em formato estruturado;
- sem inundação de logs.

# 28. Testes

A implementação DEVE possuir testes para:

- PDF simples;
- cabeçalho e rodapé;
- múltiplas colunas;
- página atravessada;
- hifenização;
- paginação romana;
- EPUB com `nav`;
- EPUB com NCX;
- EPUB sem página;
- associação PDF–EPUB;
- edições distintas;
- diretórios profundos;
- busca literal;
- morfologia;
- sinônimos;
- paráfrases;
- busca bilíngue;
- polissemia;
- negação;
- ranking híbrido;
- deduplicação exata;
- variação mínima;
- diferença material;
- múltiplas referências;
- compilações;
- devocionais;
- revistas;
- jornais;
- tradução;
- cache;
- retomada;
- escrita atômica;
- Markdown existente;
- falhas de extrator;
- falhas de tradução;
- timeout;
- arquivo corrompido;
- Zip Slip;
- bomba de compressão;
- segurança;
- desempenho.

Fixtures DEVEM incluir:

- arquivos reais autorizados;
- arquivos emulados;
- arquivos gerados automaticamente.

Testes externos DEVEM permanecer separados e opcionais.

# 29. Critérios de Aceite

A implementação somente DEVE ser considerada concluída quando:

- percorre diretórios arbitrários;
- processa PDF e EPUB textuais;
- associa formatos equivalentes;
- distingue edições;
- reconstrói parágrafos;
- identifica título, capítulo, página e data;
- registra variantes pesquisadas;
- combina busca lexical e semântica;
- traduz citações inglesas;
- gera um único Markdown por pesquisa;
- consolida citações repetidas;
- acumula referências;
- preserva diferenças materiais;
- atualiza idempotentemente;
- retoma após falhas;
- não entra em loop;
- não fabrica metadados;
- registra confiança;
- registra arquivos não processados;
- executa testes verificáveis.

# 30. Ordem de Implementação

Execute em etapas:

1. análise do corpus;
2. avaliação de linguagens, bibliotecas e modelos;
3. contratos;
4. descoberta;
5. modelo de publicação;
6. extração EPUB;
7. extração PDF;
8. limpeza;
9. reconstrução;
10. referências e datas;
11. alinhamento;
12. persistência;
13. tokenização;
14. indexação lexical;
15. indexação semântica;
16. expansão bilíngue;
17. recuperação híbrida;
18. reranking;
19. deduplicação;
20. consolidação;
21. tradução;
22. Markdown;
23. failsafe;
24. testes;
25. otimização;
26. documentação;
27. validação.

Cada etapa DEVE ser validada antes da seguinte.

# 31. Entrega

Entregue:

1. projeto funcional;
2. fontes;
3. configuração;
4. CLI;
5. persistência e índices;
6. testes;
7. fixtures;
8. documentação;
9. exemplo de Markdown consolidado;
10. relatório sucinto contendo:
    - tecnologia escolhida;
    - alternativas avaliadas;
    - bibliotecas reutilizadas;
    - código próprio e justificativa;
    - arquitetura;
    - modelos;
    - índices;
    - comandos;
    - testes;
    - resultados;
    - limitações;
    - níveis de confiança;
    - fallbacks;
    - arquivos não processados.

Não declare como executado qualquer teste, validação ou capacidade não verificada.
```
````
