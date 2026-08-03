# RCF — egwSearch

Este RCF é a especificação normativa principal do **egwSearch**. O
[AGENTS.md](AGENTS.md) governa processo, precedência e operação de IA; esta
suíte RCF governa produto, requisitos, contratos, critérios de aceite e
restrições de negócio e arquitetura.

Aplicam-se o [AGENTS.md](AGENTS.md), os microconceitos `MN-2119`, `MN-DENS`,
`MN-PRES`, `MN-REF`, `MN-STATE`, `MN-VAL`, `MN-CLI` e `MN-CMD`, e
os contratos da Norma Operacional. Em divergência, este arquivo prevalece sobre
os RCFs subordinados; o RCF subordinado mais específico prevalece em seu escopo
quando não contrariar esta raiz.

## 1. Identidade, finalidade e corpus prioritário

O **egwSearch** é uma ferramenta planejada para pesquisar conceitos, palavras,
expressões e formulações semanticamente equivalentes e conversar de forma
probatória com coleções textuais em PDF e EPUB, preservando resultados,
citações, referências, localizações e evidências documentais verificáveis.

Sua finalidade é a investigação documental e hermenêutica: localizar,
comparar, interpretar e relacionar fontes sem fabricar prova nem apresentar
inferência como conteúdo documental.

O corpus prioritário compreende a **Bíblia**, o **Espírito de Profecia —
escritos de Ellen G. White**, os **pioneiros adventistas** e demais artigos,
periódicos e livros pertinentes à investigação hermenêutica. Essa prioridade
não atribui equivalência de autoridade entre fontes; a relação depende do
domínio, da pergunta e do
[RCF epistemológico](.RCFs/RCF.epistemologia.md).

Obtenção, gestão, preparação e indexação do acervo, assim como a avaliação de
algoritmos, métodos de chunking e estratégias de RAG, são meios instrumentais.
Eles não constituem a finalidade pública do produto.

A ferramenta DEVE suportar livros, compilações, devocionais, revistas, jornais,
periódicos, edições, traduções e títulos simultaneamente disponíveis em PDF e
EPUB, em árvores recursivas de profundidade ilimitada.

Precisão, rastreabilidade, reutilização de tecnologia existente, resiliência,
processamento incremental, abstinência diante de prova insuficiente e revisão
controlada de ambiguidades DEVEM prevalecer sobre conveniência de implementação.

## 2. Estado material e limites de comunicação

Nenhuma capacidade DEVE ser declarada disponível sem validação material
proporcional e registrada. Intenção, requisito, protótipo, infraestrutura
preparatória e implementação parcial DEVEM ser identificados como planejados ou
parciais.

No estado validado desta versão:

- **disponíveis:** aquisição responsável de publicações elegíveis; preparação e
  validação de EPUB/PDF; estrutura canônica; capas; metadados; índice global e
  seu manifesto estrutural; laboratório experimental de chunking por recurso;
  build estático; e publicação do artefato pelo GitHub Pages;
- **parciais:** cobertura do corpus prioritário e preparação de estratégias para
  futura recuperação; o acervo atual não comprova presença integral da Bíblia
  nem conformidade final de toda publicação potencial;
- **planejados:** núcleo de pesquisa, índices de recuperação, busca lexical,
  semântica e híbrida, equivalência numérica, Modo Pesquisa, Modo Conversa
  probatório, CLI de pesquisa e GUI local.

A existência de publicações e automações não pode ser apresentada como busca,
conversa, RAG operacional ou conformidade integral do produto.

## 3. Direção tecnológica e operação local

Nenhuma linguagem, biblioteca, motor, índice, modelo, banco, runtime ou
arquitetura DEVE ser escolhido por preferência, reputação ou conveniência
isolada. A seleção DEVE comparar qualidade, manutenção, licença,
compatibilidade, portabilidade, precisão, desempenho, memória, instalação,
segurança, operação local, integração, maturidade, testes, custo e
substituibilidade.

Node.js com TypeScript DEVE ser o eixo principal de integração, orquestração,
configuração e interfaces quando adequado. Python e outros runtimes PODEM ser
usados em segmentos especializados quando houver ganho técnico demonstrável.

O perfil local é primário. Serviço, API, modelo ou IA remotos somente PODEM
receber conteúdo por autorização e configuração explícitas, com minimização,
privacidade, limites e fallback. A indisponibilidade de componente avançado não
pode inutilizar capacidade independente.

Bootstrap multi-runtime DEVE ser local, idempotente, versionado, segregado,
reproduzível e incapaz de iniciar coleta, modificar runtime global ou expor
credencial. Reexecução inalterada DEVE reutilizar ambiente válido; falha ou
incompatibilidade DEVE produzir diagnóstico acionável sem sucesso falso.

## 4. Reutilização, evidência e contratos centrais

A implementação NÃO DEVE recriar algoritmo, extrator, parser, tokenizador,
modelo, índice, tradutor ou função já oferecida por solução adequada. Código
próprio somente DEVE cobrir integração, adaptação, composição, regra editorial
específica ou lacuna funcional comprovada.

Texto original, estrutura, normalização, tokens, derivados e evidências DEVEM
permanecer distinguíveis e rastreáveis. Metadado, citação, referência,
localização, tradução, relação ou autoridade NÃO DEVEM ser inventados.
Inferência e interpretação DEVEM ser identificadas como tais.

Toda escrita material DEVE ser incremental, determinística, validada,
retomável e segura contra perda, duplicação, sobrescrita e estado parcial.
Entrada remota, EPUB, PDF e arquivo compactado são não confiáveis até validação.

## Arquitetura normativa e ordem de leitura

A numeração histórica dos §§5–58 permanece global nesta suíte para preservar
referências. A leitura começa por este arquivo e continua somente pelos módulos
aplicáveis:

1. [RCF de pesquisa](.RCFs/RCF.pesquisa.md) — §§5–39 e §50: corpus,
   extração, reconstrução, busca, segmentação, RAG, avaliação, CLI/GUI e Modo
   Pesquisa;
2. [RCF de publicações](.RCFs/RCF.publicacoes.md) — §§40–49: site, cadeia
   pública, acervo, downloader, índice, dados formativos, capas, build e aceite;
3. [RCF de conversa](.RCFs/RCF.conversa.md) — §§51–58: Modo Conversa, prova,
   referências, sessão, arquitetura, degradação e validação;
4. [RCF epistemológico](.RCFs/RCF.epistemologia.md) — interpretação,
   hermenêutica, exegese e modus operandi de LLMs nesses domínios;
5. [RCF operacional de publicações](scripts/publications/RCF.md) — especializa
   o downloader e subordina-se a esta raiz e ao RCF de publicações.

Cada módulo é normativo somente em seu escopo. Uma regra deslocada conserva a
mesma força; referências a seção resolvem-se pela numeração global e pelo mapa
acima. Exemplo, nota de rodapé e nuance continuam vinculados à regra que
especializam.

## Implementação faseada e aceite global

Mudança material DEVE partir do estado real, possuir FT rastreável e validação
proporcional. Fase concluída não comprova capacidade posterior nem autoriza
comunicação antecipada.

O produto somente será integralmente conforme quando o corpus aplicável, a
cadeia documental, o Modo Pesquisa, o Modo Conversa probatório, a operação
local/CLI, a GUI aplicável, segurança, privacidade, desempenho, acessibilidade,
rastreabilidade e conjuntos de avaliação satisfizerem conjuntamente esta suíte.

Até esse aceite, toda superfície pública DEVE distinguir o disponível, o
parcial e o planejado.
