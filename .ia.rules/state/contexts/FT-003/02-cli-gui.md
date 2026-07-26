# Subcontexto 02 - CLI, GUI local e perfis operacionais

- ordem: 2 de 3
- fase: normatizacao
- fonte: `TODO.id.md:69`
- objetivo: preservar CLI/local como contrato primario e definir GUI leve, offline e preparada para evolucao publica aditiva.
- entradas: capacidades de busca compartilhadas, configuracao central e contratos entre runtimes.
- dependencias: nucleo independente de DOM/HTTP, perfis operacionais e limites de recursos.
- restricoes: servidor publico, autenticacao massiva, multi-tenant, quotas distribuidas e infraestrutura de producao permanecem fora do escopo atual.
- entregaveis: secoes RCF de arquitetura, perfis, configuracao, GUI, dependencias seletivas, CDN/fallback, cross-platform e integracao multilíngue.
- validacoes: CLI sem navegador/rede; GUI offline; ausencia de regra de negocio duplicada; limites centrais; pontos de extensao futuros.
- efeitos posteriores: FT-002 implementa o contrato apos a fase publica e autorizacao.
- estado: pronto para consolidacao.
