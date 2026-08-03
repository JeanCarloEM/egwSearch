# Contexto mestre - FT-020

## Identidade

- FT: `FT-020`.
- tipo: `evolucao normativa e implementacao de codigo`.
- fonte: `.ia.rules/state/requests/FT-020/source.md`.
- estado: normativa em andamento; implementacao bloqueada pelo gate de fase.
- prioridade: alta.

## Evolucao requerida

O contrato atual torna o commit por publicacao opt-in. A solicitacao superveniente
o transforma em pos-condicao obrigatoria de qualquer ciclo que crie ou altere
uma publicacao, seus metadados, analises de chunking ou sua entrada no indice,
quer o ciclo seja executado pelo downloader, pelo analisador, pelo indexador com
analise ou por composicao entre eles.

## Objetivo

Depois do enriquecimento, da validacao dos ativos, dos experimentos de chunking
aplicaveis e da atualizacao incremental do indice, criar imediatamente um unico
commit Git atomico e exclusivo para a publicacao. A conclusao operacional so
existe depois de o hash desse commit ser confirmado no ledger.

Em modo global, downloader e analisador tambem devem persistir um diario de
progresso com escopo, ordem, publicacao, ativo, fase e ultimo limite atomico
confirmado. Uma execucao subsequente retoma automaticamente desse limite, sem
repetir publicacoes ou calculos concluidos; somente reset explicito descarta o
cursor aplicavel.

## Escopo e invariantes

- usar uma unica capacidade transacional compartilhada por downloader,
  analisador, indexador e wrappers, sem duplicar staging ou validacao;
- calcular allowlist positiva pela identidade da publicacao, incluindo ativos,
  capa, metadados, derivados, manifestos de chunking e somente os artefatos
  globais efetivamente alterados pela indexacao/aprendizado dessa publicacao;
- proibir `git add .`, `git add -A`, glob aberto, runtime, cache, temporarios,
  localstores, checkpoints, perfis e qualquer alteracao alheia;
- serializar enriquecimento final, analise, indexacao, staging e commit para que
  cada commit represente exatamente uma publicacao;
- preservar alteracoes concorrentes de outras publicacoes na worktree e
  bloquear conflito nos mesmos artefatos globais em vez de incorpora-las;
- tornar o commit obrigatorio por padrao nas execucoes canonicas, sem depender
  de flag de ativacao; eventual modo sem commit somente PODE existir para
  fixture/teste segregado e explicitamente nao canonico;
- execucao sem alteracao validada permanece `skipped` e nao cria commit vazio;
- falha Git mantem a unidade integra em `commit_pending`, impede `completed` e
  permite retomada idempotente sem novo download ou novo calculo valido;
- push permanece separado e nao e efeito implicito por publicacao;
- diario global e estado de runtime, nunca artefato da publicacao nem conteudo
  elegivel a Git, e deve ser escrito atomicamente depois de cada limite
  confirmado;
- retomada global valida configuracao, escopo, ordenacao, fingerprint do
  corpus/catalogo e versao do algoritmo antes de confiar no cursor;
- alteracao compativel do conjunto retoma pelo identificador estavel, enquanto
  cursor ambiguo, corrompido ou incompatível bloqueia com diagnostico e exige
  reset explicito; reinicio silencioso e proibido;
- o reset do downloader preserva o nome canônico `--restart`; o analisador deve
  expor `--reset` ou equivalente unico propagado por wrappers e indexador;
- preservar integralmente as publicacoes e demais mudancas ja presentes na
  worktree durante esta FT.

## Aceite

1. download isolado ou composto cria um commit logo apos analise e indexacao;
2. analise isolada de uma publicacao cria um commit quando alterar manifestos,
   aprendizado ou indice correspondente;
3. indexador com analise reutiliza a mesma finalizacao e nao duplica commits;
4. cada commit contem uma unica arvore de publicacao e somente os globais
   causalmente alterados por ela;
5. alteracoes alheias, inclusive de outras publicacoes, permanecem unstaged;
6. falha antes, durante ou depois do staging nao produz conclusao falsa e
   deixa retomada deterministica;
7. testes pequenos comprovam allowlist exata, execucao isolada/composta,
   `skipped`, conflito, retomada e ausencia de runtime/cache.
8. modos globais retomam exatamente do ultimo limite confirmado e nao executam
   novamente publicacao/ativo concluido;
9. reset explicito descarta somente o cursor do escopo solicitado, e estado
   ausente, corrompido ou incompativel possui comportamento deterministico.

## Ordem

1. registrar fonte, FT e contexto em commit exclusivo;
2. evoluir e validar os RCFs aplicaveis em commit normativo;
3. interromper e aguardar autorizacao humana explicita para a fase material;
4. implementar a capacidade unica e integra-la aos tres invocadores;
5. validar, criar commit material, sincronizar rastreabilidade e concluir.
