# Contexto mestre — FT-018

## Identidade

- FT: `FT-018`.
- tipo: `implementação de código com evolução normativa causal`.
- fonte: `.ia.rules/state/requests/FT-018/source.md`.
- estado: concluída e validada.
- prioridade: alta.

## Objetivo

Impedir reexecução redundante do avaliador experimental de chunking quando a
última análise aplicável tiver sido concluída com sucesso há menos de 24 horas,
independentemente de a invocação ser direta, pelo indexador, pelo downloader ou
por wrapper npm; permitir somente override explícito de recálculo forçado,
propagado sem perda por toda a cadeia.

## Escopo e invariantes

- a prova de frescor DEVE representar conclusão bem-sucedida, identidade do
  recurso, gerador/configuração causal e instante confiável;
- execução incompleta, falha, mudança material do ativo/configuração ou prova
  incompatível NÃO PODE ser reutilizada;
- o intervalo é de 24 horas e precisa ser testável com relógio controlado;
- o parâmetro de força DEVE possuir uma única semântica e alcançar todos os
  intermediários sem reimplementação;
- skip fresco não pode alterar manifesto, timestamp, índice ou checkpoint;
- execução direta e indireta DEVEM emitir diagnóstico sucinto e inequívoco;
- a FT-017 será concluída antes da implementação material desta FT.

## Ordem

1. concluir a FT-017 sem misturar mudanças;
2. inspecionar todos os entrypoints e o contrato de validade atual;
3. evoluir o RCF aplicável;
4. implementar o gate central e a opção de força;
5. propagar por analisador, indexador, downloader, TypeScript/npm e ajuda;
6. testar fresco, expirado, falho, alterado, direto, indireto e forçado;
7. validar, rastrear e concluir em commits isolados.

## Fechamento

- gate central implementado com prova `completed`, relógio UTC controlável e
  janela estrita inferior a 24 horas;
- ativo, hashes integrais, versão do analisador, catálogo e contexto editorial
  são revalidados antes de qualquer skip;
- prova ausente, falha, futura, inválida, expirada ou materialmente divergente
  recalcula; `--force-recalculate` sempre prevalece;
- propagação comprovada no analisador, no indexador com `--analyze`, no
  downloader e no wrapper npm que encaminha argumentos integralmente;
- skip fresco não reescreve manifesto nem aprendizado agregado;
- 46 testes Python, cinco testes documentais, rastreabilidade e diff aprovados;
- commits causais: `c9c4f44` e `0a47d86`.
- fechamento canônico: `a80a65d`; `dev` e `main` publicados e convergentes;
- GitHub Pages: workflow `30777046483` concluído com sucesso.
