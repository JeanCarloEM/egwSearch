# Contexto mestre - FT-019

## Identidade

- FT: `FT-019`.
- tipo: `correcao normativa e implementacao de codigo`.
- fonte: `.ia.rules/state/requests/FT-019/source.md`.
- estado: FT criada; evolucao normativa pendente.
- prioridade: alta.

## Problema comprovado

O checkpoint da colecao conserva IDs confirmados durante uma execucao
interrompida, mas a retomada ainda percorre o prefixo concluido item a item. Ao
concluir a colecao, o fluxo remove seu checkpoint; uma nova invocacao perde o
cursor duravel, reabre o catalogo e volta a iterar publicacoes ja concluidas.
Esse comportamento contraria a retomada eficiente agora exigida e torna
obsoleta a regra anterior que mandava apagar o checkpoint concluido.

## Objetivo

Persistir um cursor verificavel do primeiro item pendente por escopo de colecao
e retomá-lo diretamente, sem abrir navegador, emitir requisicao especifica,
reprocessar, reanalisar ou reindexar o prefixo confirmado. Publicacoes locais
integrais e commitadas permanecem a autoridade material para validar o salto.

## Escopo e invariantes

- evoluir o RCF antes do codigo, substituindo a remocao do checkpoint concluido
  por estado duravel e atomicamente validado;
- derivar cursor seguro para checkpoints legados a partir do maior prefixo
  contiguo confirmado, sem confiar em lacunas;
- iniciar a iteracao diretamente no primeiro pendente;
- preservar checkpoint de colecao concluida e reutiliza-lo sem abrir navegador;
- `--restart` continua sendo a unica forma de descartar o cursor do escopo;
- `--revalidate` invalida o salto integral e aplica sua politica explicita;
- checkpoint ambiguo, corrompido ou divergente bloqueia, sem reinicio silencioso;
- preservar ativos, publicacoes, manifestos gerados e alteracoes alheias.

## Aceite

1. retomada de checkpoint interrompido com 1.105 itens confirmados chama o
   processamento somente para o primeiro pendente e seguintes;
2. colecao concluida e inalterada e reutilizada sem navegador, HTTP, analise ou
   indexacao por publicacao;
3. checkpoint legado e migrado de modo deterministico;
4. lacuna entre confirmados impede salto alem do primeiro pendente;
5. `--restart` e `--revalidate` preservam suas semanticas explicitas;
6. testes pequenos e direcionados comprovam ausencia das chamadas proibidas.

## Ordem

1. registrar FT e contexto em commit exclusivo;
2. evoluir e validar o RCF aplicavel em commit normativo;
3. interromper e aguardar autorizacao humana exigida pela Norma;
4. implementar cursor duravel, migracao e atalhos;
5. validar regressao, rastreabilidade e integracao.

