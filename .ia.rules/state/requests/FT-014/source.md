# Fonte canônica - FT-014

- origem: solicitação humana desta conversa.
- recebido em: `2026-08-02`.
- incorporação: concluída.
- precedente: FT-013 concluída, porém reprovada por evidência funcional superveniente.

## Solicitação integral

> Corrigir e aprimorar os manifestos de chunking para que benefícios, riscos,
> parâmetros, métodos e textos repetitivos não comprovados para o recurso não
> sejam copiados em cada arquivo, mas referenciados por norma global.
>
> O analisador deve testar empiricamente cada recurso EPUB/PDF, em execução
> ultrarrápida porém real, e recomendar somente métodos comprovadamente
> funcionais naquele ativo. Deve verificar fronteiras de frase, parágrafo,
> página, capítulo, meditação, dia e outras unidades; excluir cabeçalhos,
> rodapés e números de página; reconstruir conteúdo que atravesse páginas sem
> perda, duplicação ou segmentação indevida; e registrar evidência verificável.
>
> O aprendizado por recurso deve ser agregado de forma coesa, deduplicada e
> não redundante para orientar a multiplicidade global de formatos e padrões.
> Pesquisas acadêmicas recentes, preferencialmente desde 2024, devem fundamentar
> no RCF todos os modelos potencialmente avaliáveis, com notas e referências
> sobre eficiência, aplicabilidade, limitações e condições. Regex deve integrar
> o catálogo de hipóteses e obedecer aos mesmos ensaios.
>
> A implementação deve preferir algoritmos e bibliotecas open source mantidos e
> consolidados de NPM ou ecossistema equivalente. APIs gratuitas de IA ou
> modelos locais podem auxiliar; antes disso, qualquer dado deve ser
> normalizado, condensado e agressivamente otimizado, preservando apenas a
> informação necessária e minimizando tokens, computação e exposição.

## Aceite derivado

1. manifesto por ativo contém somente observações, experimentos, métricas,
   provas e decisões específicas do recurso, referenciando catálogo global;
2. nenhuma estratégia é recomendada sem ensaio executado e critérios objetivos
   aprovados no próprio ativo;
3. extração e reconstrução medem cobertura, ordem, perda, duplicação,
   contaminação de cabeçalho/rodapé/paginação e aderência às fronteiras;
4. EPUB e PDF possuem ensaios adequados às evidências realmente observáveis;
5. conhecimento compartilhado é agregado em artefato global deduplicado e
   versionado, sem copiar conteúdo editorial nem conclusões genéricas;
6. RCF mantém catálogo referenciado de hipóteses testáveis, incluindo regex,
   com literatura acadêmica primária recente e limitações explícitas;
7. integração no downloader permanece síncrona, local, retomável e sem rede;
8. testes demonstram recomendação por evidência e rejeição/inconclusão quando
   a prova for insuficiente.

## Adição de escopo - saída humana integrada

> A saída de cada teste deve ser visualmente sucinta, agradável,
> preferencialmente colorida e tabular. O mesmo padrão deve ser aplicado ao
> `baixar.py` e ao indexador, com cada recurso claramente distinto e duas linhas
> em branco ou separador visual equivalente entre publicações.
>
> Rich ou biblioteca equivalente deve planejar larguras, evitar quebras
> acidentais e truncar paths longos previsivelmente sem perder identificação.
> A síntese por método deve mostrar eficiência, erros e percentuais de acerto e
> erro sem inundar o console. Em execução isolada, cada script deve ser completo
> e equilibrado; em cadeia, a saída deve ser integrada, coesa e não redundante,
> preservando limites de etapa sem duplicar cabeçalhos, separadores ou resumos.

9. uma camada visual compartilhada produz tabelas determinísticas e legíveis em
   TTY, com fallback textual estável quando cor/terminal não estiver disponível;
10. paths e títulos variáveis são truncados pelo meio ou pela cauda com largura
    previamente calculada e identidade preservada;
11. analisador resume por método status, eficiência, acerto, erro e diagnóstico;
12. downloader e indexador compõem etapas sob um único contexto visual quando
    encadeados, sem repetir cabeçalhos/resumos e mantendo separação inequívoca.
