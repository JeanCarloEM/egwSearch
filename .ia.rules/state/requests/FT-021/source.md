# Fonte da FT-021

- origem: prompt humano no Codex Desktop
- recebido_em: `2026-08-08`
- incorporacao: imediata
- destinos: RCF de publicacoes, RCF especializado, estado canonico,
  downloader, analisador, apresentacao compartilhada, transacao e testes

## Solicitacao integral

> O script `baixar.py` encerra prematuramente sem percorrer todas as publicações; por exemplo, a execução observada permaneceu restrita a livros em `pt-BR`. Além disso, o delay normalmente aplicado após requisições, destinado a evitar problemas com mecanismos de proteção contra DDoS e controles análogos, permanece ativo mesmo quando nenhuma requisição de rede é efetivamente realizada. Esse delay, que naturalmente aumenta o tempo de execução, DEVE ser aplicado somente quando houver requisição que justifique a espera. O script já conhece previamente os catálogos e seus respectivos conteúdos — ou, no mínimo, possui condições de determiná-los antes de iniciar a varredura efetiva. Entretanto, não apresenta informações adequadas de progresso. A execução DEVE exibir, de forma sucinta e integrada ao padrão visual já definido, o progresso global e corrente, incluindo percentual concluído, quantidade total de publicações, quantidade já processada, quantidade restante e estimativa de tempo para conclusão com base na média observada durante a execução. Essas informações são fundamentais para permitir o acompanhamento objetivo da execução. Ambos os script deveriam exibir estas informações, mas é claro, quando são executados independentes, quando são em cadeia, apenas o que é principal, mostra as informações.

## Evidencia anexada

A captura apresentada registra 84 itens descobertos, 82 falhas com
`PublicationTransactionError: transação exige publication-source/v3`, nenhum
download e encerramento logo depois da coleção `pt-br-livros`.
