# Fonte humana - FT-024

Em `2026-08-09`, durante a execução de `npm run publications:baixar`, foi
observado que itens independentes falhavam repetidamente por causa de dois
manifestos modificados de outra publicação:

```text
ITEM_FAIL collection=en-pioneers item=140 error=PublicationTransactionError:outra publicação possui alterações: src/publications/egw/pt-br/livros/a-ciencia-do-bom-viver/acdbv.epub.chunking.json, src/publications/egw/pt-br/livros/a-ciencia-do-bom-viver/acdbv.pdf.chunking.json
```

O processo em execução não deve ser interrompido. Alteração pertencente a outra
publicação não deve impedir o processamento da unidade corrente: o fluxo deve
preservá-la, excluí-la do commit corrente e continuar de forma fail-safe.

Solicitou-se também criar e invocar posteriormente um comando que, sem acesso
HTTP, materialize apenas o que já foi consultado e persistido em arquivos,
caches ou checkpoints. A invocação pode deixar de ser acompanhada se ultrapassar
cinco minutos; se terminar em menos de cinco minutos, as mudanças válidas devem
ser commitadas.

## Ampliação autorresolutiva

Em `2026-08-09`, após a primeira materialização offline, solicitou-se
explicitamente normatizar e implementar `baixar.py` e o indexador como fluxos
autorresolutivos, resilientes e não regressivos. Eles devem detectar e corrigir
autonomamente pendências, inconsistências, corrupção, estados parciais e
divergências; preservar dados válidos; refazer cirurgicamente somente downloads,
cálculos, índices ou etapas afetadas; e validar novamente. É vedado apenas
orientar correção manual quando o próprio sistema puder resolvê-la de modo
seguro e determinístico. Intervenção humana fica restrita ao materialmente
irresolúvel.

A execução offline durou `761.005` segundos, encerrou com código `1`, 389 falhas
e 18 coleções pendentes. A auditoria comprovou ainda colisão física entre os IDs
remotos `1034` e `1333`: o segundo substituiu metadado, texto, capa, EPUB e
análise da unidade já commitada do primeiro. Essa evidência integra o aceite da
correção e não autoriza tocar nos dois manifestos preexistentes de
`a-ciencia-do-bom-viver`.
