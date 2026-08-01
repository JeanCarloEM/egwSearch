# Contexto mestre - FT-007

## Identidade

- FT: `FT-007`.
- tipo: `implementacao_codigo`.
- criado em: `2026-07-26T22:49:34.6550184-03:00`.
- fonte: `.ia.rules/state/requests/FT-007/source.md`.
- estado: concluído.
- autorização: explícita no prompt de origem.

## Objetivo e escopo

Retirar o coletor e unidades correlatas da árvore pública `src/`, realocando-os
em `scripts/publications/`, com requisitos em
`scripts/publications/requirements.txt`. Atualizar imports, resolução da raiz,
testes, migrador, configuração, README, RCF, estado e mapa de rastreabilidade.

O acervo sob `src/publications/` permanece intocado. A mudança preserva
comportamento, CLI, hashes do acervo e contratos de aquisição.

O namespace é deliberadamente neutro quanto a autor: o mesmo coletor incorpora
Ellen G. White e autores pioneiros; `egw` permanece apenas onde identificar
autor legado ou origem/provedor de forma não ambígua.

## Classificação

Correção física e arquitetural autorizada, sem mudança funcional: aplica fluxo
reduzido registrado. `src/` fica reservado ao conteúdo que integra o artefato
público; automação operacional fica sob `scripts/`.

## Aceite

- nenhum `.py`, RCF específico ou requisitos do coletor permanece sob `src/`;
- nenhum caminho antigo ativo permanece em código, configuração ou docs;
- imports funcionam independentemente do cwd;
- 37 testes continuam aprovados;
- RCF e mapa causal ficam válidos;
- nenhuma publicação é movida ou regravada.

## Evidências de encerramento

- contrato normativo: `768e17c`;
- commit material: `ce230029828a4bc398d24590c992357db3301a97`;
- movimentos Git reconhecidos com similaridade de 99-100%;
- 37 testes aprovados após a relocalização;
- compilação dos quatro módulos Python aprovada;
- CLI `python scripts/publications/baixar.py --help` aprovada;
- `pip check` sem dependência quebrada;
- `RCF_OK`, com 85 entradas e 85 sentenças materiais;
- auditoria textual sem referência ativa aos caminhos antigos;
- acervo sob `src/publications/` inalterado.
