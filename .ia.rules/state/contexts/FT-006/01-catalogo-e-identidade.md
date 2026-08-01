# FT-006/01 - Catálogo e identidade

- tipo: código.
- objetivo: implementar descoberta pública estruturada, normalização de
  `pt-BR`/`en`, múltiplos autores/tipos e identidade remota estável.
- testes: contratos por fixture; idiomas inelegíveis; homônimos e variantes.
- rede: nenhuma durante teste unitário.
- implementação: `acquisition.py`, configuração v2 e fixture multiautor.
- evidência: normalização exclusiva `pt-BR`/`en`, chave autoral por slug URI,
  múltiplos autores/formatos e rejeição de item inelegível cobertos pela suíte.
- estado: concluído.
