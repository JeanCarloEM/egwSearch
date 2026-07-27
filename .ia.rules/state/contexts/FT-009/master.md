# Contexto mestre - FT-009

## Identidade

- FT: `FT-009`.
- tipo: `implementacao_normativa`.
- escopo: bootstrap local de dependências do repositório, iniciado por ciclos npm.
- fonte: `.ia.rules/state/requests/FT-009/source.md`.
- fonte_sha256: `E9885C5770F68D6C482E240AA165A6CD4E152E79FB917F343A83FD9BDB80FCC5`.
- estado: em análise normativa.

## Objetivo

Especificar um bootstrap explícito, seguro e idempotente que faça `npm install` e
o fluxo de atualização correspondente prepararem as dependências declaradas de
outros runtimes necessárias aos comandos suportados pelo repositório, incluindo
os requisitos Python do coletor em `scripts/publications/requirements.txt`.

## Limites e decisões pendentes

- Não instalar dependências implícitas, não declaradas ou de ferramentas sem
  comando suportado.
- Não executar o coletor, coleta remota, navegador ou qualquer operação de
  aquisição durante a instalação.
- Definir no RCF a matriz de runtimes, a detecção de Python/pip, o ambiente de
  instalação, a política de falhas e a semântica de `npm install`/atualização.
- Avaliar se o hook npm deve delegar a um subscript versionado e testável, sem
  alterar scripts gerenciados fora de extensão autorizada.

## Plano da fase normativa

1. Inventariar comandos e dependências de runtime efetivamente suportados.
2. Atualizar o RCF aplicável e o RCF especializado do coletor com contrato de
   bootstrap multi-runtime, idempotência, segurança e diagnósticos.
3. Validar o RCF e registrar a conclusão da fase normativa em commit próprio.
4. Interromper e aguardar autorização humana explícita para implementar hooks,
   subscripts e testes da fase de código.

## Aceite da fase normativa

- contrato determina quais dependências externas são elegíveis e quando;
- a instalação não executa coleta nem usa sessão/navegador;
- falhas de runtime ou de instalação possuem diagnóstico e saída segura;
- a fase de código permanece explicitamente pendente de autorização.
