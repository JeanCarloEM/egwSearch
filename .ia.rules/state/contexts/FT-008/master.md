# Contexto mestre - FT-008

- criado_em: `2026-07-27T13:04:50-03:00`.
- FT: `FT-008`.
- tipo: `implementacao_codigo`.
- escopo: cadeia de aquisição pública em `scripts/publications/`.
- fonte: `.ia.rules/state/requests/FT-008/source.txt`.
- fonte_sha256: `3D811F33720D0B6F794420323ABC9A7A752542EC969E9B3E9E74216BB95BA582`.
- dependências: FT-006 concluída; FT-007 concluída; decisão editorial da FT-004/03 permanece fora de escopo.
- autorização: solicitação humana anexada em `2026-07-27` para adaptar e normatizar `baixar.py` e componentes associados com sessão/guia persistente visível, espera humana legítima e retomada.

## Objetivo

Normatizar e implementar o uso preferencial de uma única instância visível de navegador, com perfil persistente local e uma única guia operacional reutilizada durante a descoberta remota do coletor de publicações, sem bypass de CAPTCHA ou mecanismos antirrobô.

## Baseline inspecionada

- `baixar.py` carregava Selenium somente na CLI, criava `webdriver.Firefox` dentro de `_process_collection`, ativava `--headless`, navegava uma coleção por vez, rolava a página e encerrava o driver no `finally`.
- A sessão HTTP de `requests` era separada por coleção; ativos nativos continuam baixados pelo cliente HTTP responsável.
- Detecção de bloqueio existia por `contains_block_marker`, `HTTP 403` e parada por `OriginBlocked`, mas a descoberta falhava ou encerrava em desafio, sem espera humana.
- Reexecução por fixture/no-network não dependia de navegador e já preservava idempotência.

## Plano

1. Capturar fonte e registrar contexto da FT.
2. Incorporar ao RCF global e ao RCF específico o contrato de navegador visível, perfil persistente, guia única, espera humana cooperativa, retomada e limites de recuperação.
3. Centralizar o lifecycle Selenium em `BrowserSessionManager`.
4. Reutilizar o mesmo manager nas coleções sequenciais e rejeitar concorrência quando navegador persistente for exigido.
5. Ampliar marcadores de desafio sem automatizar solução.
6. Configurar visibilidade, perfil, intervalos, espera, recuperação e janela.
7. Testar reuso de guia e espera humana simulada sem CAPTCHA real.
8. Validar compilação, testes offline, ajuda da CLI e RCF.

## Decisões

- Selenium/Firefox foi preservado por ser a tecnologia real já usada no coletor.
- Perfil persistente fica em `constructor/.state/publications-browser-profile`, já segregado de commits por `.gitignore`.
- O modo visível é padrão; headless só permanece disponível por configuração explícita.
- `workers=1` é obrigatório quando a descoberta real depende de navegador, pois múltiplas coleções concorrentes criariam múltiplas sessões/guias.
- A espera humana usa intervalo configurável de baixa frequência e limite opcional; padrão sem timeout curto.
- `requests` continua responsável por ativos nativos; `403` que não puder ser liberado legitimamente pela guia visível preserva estado e interrompe a unidade/coleção sem evasão.

## Aceite local

- `baixar.py` reutiliza uma única instância/guia em descoberta real sequencial.
- perfil persistente local configurável e fora de commits.
- desafio simulado pausa e retoma sem loop ocupado.
- fechamento/invalidação da guia aciona recuperação finita.
- fixtures e fluxo no-network continuam sem navegador.
- testes automatizados não acessam CAPTCHA real.
