# Contexto mestre - FT-029/FT-030

## Identidade

- objetivo: equalizar e executar a frente de no-op material da cadeia de
  publicações sem antecipar implementação;
- fonte local integral: `TODO.ia.md:67`;
- TODO canônico: `.ia.rules/state/TODO.ia.md`;
- fase normativa: FT-029;
- fase técnica: FT-030;
- criado_em: `2026-08-25T22:30:43-03:00`.

## Estado real auditado

- análise e índice já possuem helpers locais que comparam o payload antes da
  escrita, enquanto o writer comum sempre substitui o destino;
- o manifesto de análise é regravado após recálculo obrigatório para renovar a
  prova temporal, inclusive quando os bytes calculados coincidem;
- o gate da FT-027/028 já decide antes do parsing por `force`, existência, hash
  e ordem de `mtime` e deve ser preservado;
- a finalização Git já retorna sem commit quando não encontra paths alterados,
  mas a cadeia não possui contrato uniforme de `changed/no-op` entre etapas;
- o RCF subordinado de publicações ainda contém a regra obsoleta de 24 horas,
  embora o RCF operacional e a implementação já usem hash+`mtime`.

## Equalização

A nova demanda especializa, sem substituir, os contratos das FTs 020, 024, 027
e 028. Reuso válido é no-op físico. Recálculo obrigatório continua ocorrendo
quando a fórmula incremental o exigir; se seu resultado for byte-equivalente,
a renovação temporal estritamente necessária da prova pode tocar esse artefato,
mas deve propagar `changed=false`, manter diff Git vazio e impedir commit.

As pendências amplas da FT-002 permanecem independentes. As FTs 009 e 010 não
estavam realmente pendentes: foram concluídas pela FT-011 e o estado foi
reconciliado nesta equalização.

## Ordem e aceite

1. consolidar fontes, FTs e estado em commit exclusivo;
2. atualizar os três níveis de RCF sem duplicação normativa;
3. validar rastreabilidade e coerência documental;
4. interromper antes de código e solicitar autorização para a FT-030;
5. após autorização, implementar abstração comum, propagação, logs e testes;
6. validar no-op físico, alteração material, composição e regressões.

Nenhuma publicação, índice, manifesto operacional, aprendizado, cache, diário,
log ou saída concorrente pertence aos commits desta fase.

## Resultado normativo

- equalização e FT registradas em `df5bd44`;
- RCF principal, subordinado e operacional atualizados em `26f65e1`;
- 14 cláusulas implementáveis vinculadas à FT-030;
- `agent:rcf` aprovado com 1.079 entradas e 936 cláusulas materiais;
- FT-029 concluída; FT-030 aguarda autorização humana expressa.
