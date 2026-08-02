- [ ] Corrigir o posicionamento público e reorganizar a documentação do **egwSearch**.
  - Ler integralmente, antes de qualquer edição, o `AGENTS.md` — na extensão efetivamente aplicável —, o RCF vigente, o `README.md`, a página pública e todos os respectivos fontes, processos de build e assets responsáveis pelo conteúdo publicado.

  - Identificar e distinguir inequivocamente:
    - funcionalidades implementadas;
    - funcionalidades parcialmente implementadas;
    - funcionalidades planejadas.

  - É PROIBIDO apresentar intenção, planejamento, protótipo ou implementação parcial como recurso disponível; funcionalidades futuras DEVEM ser declaradas exclusivamente como potencial ou planejamento.

  - O RCF, seus documentos subordinados e o `README.md` DEVEM utilizar UTF-8 e acentuação correta em português brasileiro.

  - Reposicionar a página pública e o `README.md` conforme o propósito central:

    > **egwSearch é uma ferramenta planejada para pesquisar conceitos, palavras e expressões e conversar de forma probatória com coleções textuais em PDF e EPUB, preservando resultados e evidências documentais verificáveis. Seu corpus prioritário compreende a Bíblia, o Espírito de Profecia — escritos de Ellen G. White —, os pioneiros adventistas e demais artigos e livros relevantes à investigação hermenêutica.**

  - A redação PODE ser aprimorada, desde que preserve integralmente esta hierarquia:
    - **finalidade:** pesquisa e conversação probatória, hermenêutica e documental;
    - **corpus prioritário:** Bíblia, escritos de Ellen G. White, pioneiros adventistas e literatura pertinente;
    - **meios instrumentais:** obtenção, gestão, preparação e indexação do acervo, bem como avaliação de algoritmos, métodos e estratégias aplicáveis às fases de RAG.

  - A página pública NÃO DEVE posicionar o produto como acervo, catálogo, downloader, gerenciador de publicações ou laboratório de RAG, entre outros. Tais funções constituem meios instrumentais necessários, não a finalidade principal.

  - A publicação no GitHub Pages PODE conter — e provavelmente conterá, quando solicitado ou determinado pelo RCF — assets como manifestos, metadados, EPUBs e PDFs para download, sem obrigação de mencioná-los explicitamente ou disponibilizar links diretos na apresentação pública.

  - Corrigir integralmente a página efetivamente publicada, incluindo fontes, configuração, geração, build, implantação e assets responsáveis pelo conteúdo. A validação DEVE abranger o resultado público implantado, não apenas os arquivos locais ou intermediários.

  - Refatorar o `README.md` para que seja ultrassucinto, autossuficiente, tecnicamente preciso e fiel ao estado real do projeto, distinguindo expressamente o disponível do planejado e contendo somente:
    - badges pertinentes, verificáveis e verdadeiros;
    - descrição curta compatível com o campo _About_ do GitHub;
    - propósito, corpus prioritário e objetivo;
    - recursos efetivamente disponíveis;
    - recursos futuros, inequivocamente identificados como tais;
    - uso e instalação, quando existentes e funcionais;
    - links mínimos para documentação aprofundada e normas relevantes;
    - autoria e licença.

  - Reorganizar o RCF sem alterar sua substância ou semântica:
    - manter no arquivo principal o propósito, o corpus prioritário, o escopo, a precedência, os conceitos fundamentais e os contratos centrais;
    - mover especializações secundárias para `.RCFs/`;
    - preservar integralmente força normativa, regras, restrições, exceções, dependências, detalhes, exemplos e nuances;
    - aplicar microconceitos, segregação, roteamento e referenciação conforme o `AGENTS.md`;
    - declarar explicitamente subordinação, precedência, ordem de leitura e referências entre documentos;
    - eliminar duplicações sem separar conceitos inseparáveis, introduzir ambiguidades ou criar dependência de contexto implícito.

  - É PROIBIDO editar normas apenas para legitimar ou acomodar a comunicação pública. Divergências entre documentação, implementação e RCF DEVEM ser corrigidas na camada efetivamente responsável pelo desvio.

  - Validar:
    - coerência entre página pública, `README.md`, RCFs e estado real da implementação;
    - clareza da primazia bíblica, profética, pioneira e hermenêutica do corpus;
    - distinção inequívoca entre finalidade, corpus prioritário e meios instrumentais;
    - correta separação entre recursos disponíveis, parciais e planejados;
    - inexistência de perda normativa;
    - integridade de links, âncoras, referências, builds e assets;
    - testes e verificações documentais aplicáveis;
    - correspondência entre os arquivos versionados e o conteúdo efetivamente publicado.

  - O modus operandi das LLMs nos domínios cuja epistemologia envolva hermenêutica, exegese, interpretação e disciplinas correlatas DEVE ser definido por `.RCFs/RCF.epistemologia.md` e pelos documentos a ele associados, respeitando sua subordinação, precedência e escopo normativo.

  - Concluir somente quando a comunicação pública representar corretamente o **egwSearch** como ferramenta de investigação probatória, documental e hermenêutica centrada na Bíblia, no Espírito de Profecia, nos pioneiros adventistas e na literatura correlata, sem confundir sua finalidade com os meios instrumentais empregados para realizá-la.
