# RCF — Governança da TO-DO

Esta seção de governança DEVE permanecer no topo do arquivo, NÃO PODE ser removida nem editada e rege todas as TO-DOs posteriores até o marcador explícito de início das TO-DOs operacionais.

## 1. Estrutura normativa do arquivo

Este arquivo constitui uma lista normativa e operacional de TO-DOs convergentes.

Todo item de topo DEVE:

- iniciar exatamente com `- [ ]` ou `- [x]`;
- começar sem indentação;
- representar uma frente autônoma subordinada às normas deste RCF.

Todo conteúdo imediatamente posterior a um item de topo, enquanto não houver outro item iniciado sem indentação por `- [ ]` ou `- [x]`, DEVE ser interpretado como subordinado ao item de topo imediatamente anterior.

A forma interna dessa subordinação é livre: PODE conter subtítulos, subitens, regras em estilo RCF, ordens, critérios, listas de afazeres, etapas, notas ou estruturas equivalentes. A semântica hierárquica prevalece sobre a forma.

A formatação do arquivo DEVE preservar indentação visual coerente e inequívoca de todo conteúdo subordinado. Títulos, listas, blocos e demais conteúdos pertencentes a um item de topo DEVEM permanecer visualmente aninhados a ele.

## 2. Status, andamento e conclusão

A marcação `[x]` NÃO significa conclusão: indica apenas que o item foi lido, teve sua FT criada e encontra-se em andamento. Itens NÃO iniciados DEVEM permanecer como `[ ]`.

TO-DOs integralmente concluídas DEVEM ser removidas, mantendo o arquivo limpo.

## 3. Regra perene de convergência

- [ ] Equalizar e executar as TO-DOs como frentes convergentes de um único objetivo
  - Este item rege todas as demais TO-DOs. Cada uma DEVE ser tratada como frente complementar de uma única execução, conciliada com as demais e convergente ao objetivo principal do projeto.

  - Contradições aparentes DEVEM ser presumidas como imprecisão redacional e resolvidas por equalização, sem perda de intenção, requisito, restrição ou nuance. Havendo conflito material não solucionável pelas normas e pelo contexto, o desenvolvedor DEVE ser consultado.

  - Considerações, comparações ou solicitações PODEM não ser plenamente aderentes ao projeto, especialmente quando previamente processadas por IA. Salvo dúvida material, a IA DEVE interpretá-las conforme o contexto já normatizado no RCF e no `README.md`; persistindo ambiguidade ou incompatibilidade, DEVE consultar o desenvolvedor antes de prosseguir.

  - O `AGENTS.md` prevalece absolutamente; o RCF vigente prevalece sobre as demais fontes subordinadas. Toda alteração DEVE aprimorar o projeto, ampliar capacidades e recursos, preservar compatibilidade e força normativa e NÃO PODE introduzir regressão.

  - Antes de executar qualquer TO-DO, a IA DEVE:
    1. ler integralmente todas as TO-DOs e normas aplicáveis;
    2. equalizar objetivos, requisitos, dependências, precedências e terminologia;
    3. resolver incompatibilidades, ambiguidades, sobreposições e lacunas;
    4. adaptar, consolidar, desmembrar, reordenar ou eliminar itens somente quando isso aumentar a coerência sem reduzir o objetivo material.

  - Toda TO-DO DEVE ser separada em:
    - **Normatização (RCF):** atualização de RCFs, contratos, precedências e documentação normativa necessária;
    - **Implementação:** código, migrações, testes, validações e alterações funcionais.

  - Após a equalização, a IA DEVE iniciar e concluir imediatamente a **Normatização RCF de todas as TO-DOs**, mantendo rastreabilidade entre cada regra e sua implementação futura.

  - Concluída a normatização, a IA DEVE INTERROMPER antes de qualquer implementação e solicitar autorização expressa do desenvolvedor, informando sucintamente:
    - implementações pendentes;
    - dependências e ordem recomendada;
    - impedimentos materiais identificados.

  - Somente quando aplicável ao contexto do repositório, toda alteração que modifique o modo de codificar Markdown DEVE ser documentada no respectivo modo de uso.

  - Este item e toda a seção `# RCF — Governança da TO-DO` são perenes: NÃO PODEM ser marcados como concluídos, removidos ou alterados. Sua contabilização somente é necessária enquanto existir ao menos uma TO-DO por eles regida.

---

# TO-DOs

Este marcador encerra a seção de governança e inicia exclusivamente as TO-DOs operacionais. Todo item de topo abaixo dele está sujeito integralmente ao RCF acima.

---

- [x] Impedir escrita e commits espúrios quando `baixar.py`, indexador ou calculador de chunks não produzirem alteração material
  - Inspecione integralmente `baixar.py`, indexador, calculador de chunks, chamadas em cadeia, lógica de cache/hash/`mtime`, geração de manifestos/índices e fluxo de commit antes de alterar qualquer artefato.
  - Trate este requisito como correção estrutural de idempotência e não como exceção pontual para uma publicação específica.

  - **Regra nuclear**
    - Se hash, `mtime` e demais invariantes relevantes comprovarem que os dados já estão atuais e nenhuma saída material precisar mudar, o processo DEVE:
      - reutilizar o estado existente;
      - NÃO reescrever arquivos;
      - NÃO alterar metadata desnecessariamente;
      - NÃO tocar no filesystem sem necessidade;
      - NÃO produzir diferença na árvore Git;
      - NÃO gerar commit.
    - Somente alterações que modifiquem efetivamente o conteúdo/estado versionado DEVEM produzir efeitos persistentes e, consequentemente, commit.

  - **No-op real**
    - "Nada mudou" DEVE significar **no-op efetivo**, não apenas conteúdo final equivalente após reescrita.
    - É PROIBIDO abrir/salvar novamente, regenerar, truncar/regravar ou substituir atomicamente um arquivo cujo conteúdo final seria idêntico, salvo necessidade técnica comprovada.
    - Antes de qualquer escrita, compare o resultado candidato com o estado existente usando mecanismo confiável, preferencialmente hash/conteúdo já disponível.
    - Se forem idênticos, preserve o arquivo original intacto, inclusive seu `mtime`, quando possível.

  - **Hash e `mtime`**
    - Quando hash e `mtime` atuais já comprovarem reutilização válida, NÃO executar etapas de escrita apenas para "confirmar" o mesmo estado.
    - `mtime` NÃO DEVE ser alterado artificialmente por leitura, reserialização ou substituição sem mudança material.
    - Hashes/metadata auxiliares somente DEVEM ser atualizados quando o dado que representam realmente mudar ou quando houver inconsistência comprovada que exija reconciliação.

  - **Execução em cadeia**
    - A regra vale igualmente quando:
      - `baixar.py` for executado diretamente;
      - indexador for executado diretamente;
      - calculador de chunks for executado diretamente;
      - forem invocados em cadeia;
      - uma etapa chamar outra internamente.
    - Cada etapa DEVE propagar corretamente a informação de `changed/no-op`, evitando que uma etapa posterior gere escrita ou commit apenas porque foi executada.

  - **Indexação e chunks**
    - Recalcular em memória PODE ocorrer quando necessário para validação, mas persistência somente DEVE ocorrer se o resultado diferir materialmente.
    - `index.json`, manifestos, chunks e arquivos derivados NÃO DEVEM ser regravados quando o conteúdo calculado for idêntico ao existente.
    - Ordem de serialização, whitespace, timestamps internos, campos voláteis ou qualquer outro detalhe NÃO DEVE provocar alteração espúria.
    - Saídas determinísticas DEVEM ser byte-a-byte estáveis para o mesmo estado de entrada, quando tecnicamente aplicável.

  - **Commits**
    - A criação de commit DEVE depender de alteração real na árvore versionada, não de:
      - execução bem-sucedida;
      - publicação processada;
      - etapa de indexação concluída;
      - arquivo aberto/regravado;
      - alteração somente de `mtime`;
      - status interno `PUBLICATION_COMMITTED` presumido.
    - Antes de commitar, verifique objetivamente se há diff versionado material relativo ao escopo processado.
    - Se não houver diff real, NÃO criar commit vazio, sintético ou equivalente.
    - O log DEVE distinguir claramente:
      - processamento reutilizado;
      - processamento com alteração material;
      - commit efetivamente criado;
      - no-op sem commit.

  - **Caso exemplificativo**
    - Fluxos como:
      ```text
      Análise reutilizada ... · hash e mtime atuais
      Análise reutilizada ... · hash e mtime atuais
      Indexação
      ...
      PUBLICATION_COMMITTED ...
      ```
      são incorretos quando nenhuma saída versionada mudou.
    - Nesse cenário, o comportamento esperado é reutilização integral e finalização sem tocar em arquivos e sem commit.

  - **Prevenção de falsos positivos Git**
    - Audite todas as operações capazes de gerar falso `modified`, incluindo:
      - reserialização idêntica;
      - normalização de EOL;
      - encoding/BOM;
      - ordenação não determinística;
      - timestamps embutidos;
      - chmod/mode;
      - rename temporário;
      - escrita atômica sobre conteúdo idêntico;
      - formatação variável;
      - metadata gerada a cada execução.
    - Elimine qualquer variação não semântica que provoque divergência da árvore atual.
    - NÃO use `git checkout`, reset ou limpeza destrutiva para mascarar o problema; corrija a causa da escrita espúria.

  - **Eficiência**
    - Evitar escrita desnecessária é requisito funcional e de desempenho.
    - Use cache/hash/metadata já existentes para interromper cedo etapas comprovadamente desnecessárias.
    - NÃO recalcular ou regravar grandes índices/chunks quando os inputs relevantes permanecem invariáveis, salvo validação necessária e proporcional.
    - Preserve correção antes de otimização: nenhuma etapa PODE ser ignorada apenas por inferência não comprovada.

  - **Validação obrigatória**
    - Teste, no mínimo:
      - execução totalmente atualizada;
      - hash e `mtime` atuais;
      - apenas um arquivo realmente alterado;
      - índice sem alteração;
      - índice com alteração;
      - chunks sem alteração;
      - chunks com alteração;
      - execução direta de cada script;
      - execução completa em cadeia;
      - múltiplas publicações consecutivas sem mudança;
      - alteração somente de timestamp não semântico;
      - serialização repetida determinística;
      - working tree limpa antes/depois de no-op.
    - Para cenários sem alteração, valide simultaneamente:
      - zero arquivos regravados quando evitável;
      - `mtime` preservado;
      - `git diff` vazio;
      - nenhum commit novo.
    - Para cenários com alteração real, valide que somente os arquivos efetivamente modificados entram no commit.

  - **Critérios de aceite**
    - Execução sobre estado já atual converge para no-op real.
    - Arquivo sem mudança material NÃO é tocado.
    - Hash/`mtime` atuais impedem reprocessamento/escrita desnecessária conforme o contrato existente.
    - Índices, manifestos e chunks idênticos permanecem byte-a-byte intactos.
    - Nenhum commit é criado sem diff material.
    - Alterações reais continuam sendo persistidas e commitadas normalmente.
    - A inundação de commits causada por falsos positivos é eliminada na origem, sem mascaramento posterior.
