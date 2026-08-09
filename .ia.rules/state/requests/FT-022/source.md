# Fonte da FT-022

- origem: prompt humano no Codex Desktop
- recebido_em: `2026-08-09`
- incorporacao: imediata
- destinos: RCF de publicacoes, RCF especializado, estado canonico,
  configuracao, downloader, contrato de conteudo estruturado, indexador e testes

## Solicitacao integral

> Implemente e normatize no RCF a ampliação do `baixar.py`, preservando
> integralmente o fluxo vigente e priorizando UTF-8 em todos os artefatos
> textuais; somente use outra codificação quando houver impedimento técnico
> comprovado, escolhendo a alternativa mais adequada e registrando-a
> explicitamente.
>
> Novas coleções: REFERENCE (`en`, `/allCollection/en/6`), incluindo equivalente
> em `pt` quando houver; BIBLE (`en`, `/allCollection/en/22`), distinguindo
> versões bíblicas de dicionários, léxicos, concordâncias, comentários e demais
> obras; Bíblias obrigatoriamente em JSON e, quando disponível/adequado, EPUB,
> sem exigir PDF; dicionários, léxicos e conteúdos indexados por palavra ou
> expressão, inclusive `en/1370`, em JSON e EPUB, sem exigir PDF; concordâncias,
> inclusive `en/1369`, estruturadas conforme sua semântica.
>
> Versões bíblicas e corpora equivalentes exigem criticidade máxima contra
> omissão, deleção, concatenação indevida e conteúdo estranho; análise prévia
> da estrutura real; um item JSON isolado por versículo; preservação de marcas
> semânticas; e validação por múltiplas fontes independentes confiáveis, APIs
> públicas autorizadas quando úteis, sem evasão e respeitando termos e limites.
>
> Quando houver fonte legítima, utilizável e juridicamente permitida, incluir
> LXX, Textus Receptus, Tanakh, Texto Massorético, Qumran, Codex Sinaiticus,
> Codex Vaticanus e Texto Majoritário/Bizantino. `https://tanach.us/` pode ser
> fonte ou contraprova confiável para o Tanakh.
>
> Normatizar um JSON bíblico universal, ultrassucinto, determinístico,
> autoexplicativo e hierárquico, capaz de individualizar versão, coleção ou
> testamento, livro, capítulo e versículo, com nomes e abreviações, diferentes
> cânones e organizações sem mudar o esquema fundamental.
>
> Normatizar JSON lexical universal curto, com lema/original, idioma/escrita,
> transliteração, pronúncia/identificadores, definição original em inglês,
> tradução `pt-BR`, referências, índices e relações. Preservar sempre o
> original e identificar tradução automática como tradução, usando apenas
> mecanismo local ou serviço/API autorizado e suficiente.
>
> Tratar todo material como dado crítico: não confiar em título, extensão,
> metadado ou classificação de origem; verificar tipo, estrutura, conteúdo,
> identidade, completude e integridade; detectar omissões e agregações;
> aplicar hashes; validar amostras por fontes independentes; preservar
> rastreabilidade; e respeitar direitos autorais, licenças, termos, APIs,
> limites e proteções. Centralizar as regras no RCF e implementar abstrações
> universais em `baixar.py` e consumidores relacionados, evitando tratamento
> ad hoc por obra.

## Evidencia observada na triagem

- `en/6` é o agrupador `Reference`, com subcoleções de autoria e natureza
  heterogêneas, inclusive `Dictionary` e `EGW Reference Works`;
- `en/22` é o agrupador `Bible`, com subcoleções separadas `Versions` (`1368`),
  `Commentaries` (`1371`), `Concordances` (`1369`), `Dictionaries` (`1370`),
  `Reading Plans` (`1476`) e `SDA Scripture Index` (`1414`);
- `en/1368` contém 18 itens, inclusive `King James Bible With Strong's
  Dictionary`, cuja classificação não pode depender somente do título;
- `en/1370` contém léxicos e dicionários hebraicos/gregos e gerais;
- `en/1369` contém concordâncias e índices, e a leitura observada da
  concordância grega estrutura lema, romanização, formas e referências;
- o agrupador português é `pt`, com Bíblia própria em `pt/68` (`Almeida
  Corrigida Fiel`); não foi observado equivalente português direto de
  `Reference` no catálogo raiz.
