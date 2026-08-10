# Contexto mestre - FT-025

## Identidade

- FT: `FT-025`.
- tipo: `evolução normativa e implementação de código`.
- fonte: `.ia.rules/state/requests/FT-025/source.md`.
- estado: concluída e sincronizada.

## Objetivo

Integrar os schemas `scripture-corpus/v1`, `lexical-corpus/v1` e
`concordance-corpus/v1` às capacidades canônicas de análise e indexação, usando
um modelo comum de unidades semânticas e adaptadores estritamente específicos
por domínio.

## Invariantes

- JSON estruturado é validado pelo schema antes de qualquer análise e nunca é
  serializado ou tokenizado como prosa genérica;
- versículo e entrada são unidades atômicas: nenhuma estratégia admissível os
  fragmenta, funde ou remove;
- hierarquia, identidade, ordem, referências, relações e metadados participam
  da prova estrutural, sem copiar o corpus para manifestos ou índice;
- estratégias bíblicas podem projetar versículo, capítulo e livro somente a
  partir da hierarquia explícita e mantendo as unidades-filhas recuperáveis;
- léxicos/dicionários e concordâncias usam uma entrada completa por chunk
  semântico, incluindo suas relações e referências;
- EPUB/PDF e invocadores existentes mantêm comportamento e compatibilidade;
- análise, aprendizado agregado, índice, transação e CLI aceitam JSON
  estruturado com validação equivalente e escrita determinística;
- artefatos operacionais e alterações concorrentes em `src/publications/` não
  integram os commits desta FT.

## Aceite

1. fixtures dos três schemas geram manifestos de análise com parser, modelo,
   hierarquia, contagens, hashes e recomendação próprios do domínio;
2. contraprovas detectam perda, duplicação, reordenação, fragmentação ou fusão
   de versículos/entradas e rejeitam JSON genérico ou schema divergente;
3. o índice expõe modelo/schema/path/hash, manifesto de chunking e síntese
   estrutural, sem copiar texto, definições ou referências integrais;
4. publicação exclusivamente estruturada é analisável/indexável quando seu
   contrato não exige EPUB/PDF;
5. transação exige manifesto válido para cada derivação estruturada;
6. suítes legadas de EPUB/PDF continuam aprovadas, e benchmarks comparam
   cardinalidade, fidelidade, fronteiras e tempo por domínio.

## Resultado

- adaptador comum de unidades semânticas e adaptadores dos três schemas
  implementados em `publication_analysis.py`;
- estratégias `scripture-verse`, `scripture-chapter`, `scripture-book`,
  `lexical-entry` e `concordance-entry` executadas e aferidas;
- índice v1 ampliado de modo compatível e manifesto estrutural elevado a v2;
- transação aceita publicação somente-JSON e exige análise semântica íntegra;
- fingerprint v4 preserva explicitamente o analisador histórico v2;
- 123 testes Python, 12 testes Node, compilação TypeScript, `git diff --check`
  e mapa RCF com 924 cláusulas materiais aprovados;
- commits faseados: estado `4ffad98`, norma `68a0d9e`, implementação
  `71f0569` e sincronização pendente do presente fechamento.
