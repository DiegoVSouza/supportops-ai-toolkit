# Toolkit de IA em produção — P02

## Structured outputs e contratos de tools

Validar a entrada antes da execução reduz chamadas malformadas e impede que campos extras escapem do contrato. Validar também a saída detecta violações no próprio handler. Um schema deve especificar campos obrigatórios, tipos, enumerações e limites úteis. Compatibilidade é parte da API: mudanças incompatíveis precisam de ADR, versão e atualização dos consumidores.

O registry P02 implementa um subconjunto local de JSON Schema para não introduzir dependências externas. Não deve ser apresentado como validador JSON Schema completo.

## Desenho de evals

Evals offline medem casos reproduzíveis com rótulos revisáveis. Separar acerto da decisão, seleção de tool, groundedness por evidência e escalonamento torna falhas acionáveis. Evals online podem representar tráfego real, mas exigem privacidade, amostragem, revisão humana e monitoramento de deriva.

Um LLM-as-judge pode avaliar critérios abertos, porém tem viés de posição, preferência por respostas longas e inconsistência. Calibrar o juiz contra exemplos revisados por pessoas e permitir `unknown`. Use graders determinísticos quando possível. Os resultados fake deste projeto validam apenas o encanamento do runner e ficam explicitamente distintos de qualidade de um modelo.

## Prompt injection direta e indireta

Injeção direta aparece na mensagem do usuário. Injeção indireta chega por páginas, documentos, tickets, e saídas de tools. Todo conteúdo externo é dado não confiável, mesmo quando recuperado de uma base interna. Heurísticas por palavras são úteis como sensor, mas podem ter falsos positivos e não substituem separação de privilégios, allowlists, validação de argumentos e aprovação humana para efeitos irreversíveis.

## Custo e latência

Cache exato é previsível, mas só reutiliza entradas idênticas após normalização. Cache semântico aumenta hits potenciais, com risco de reutilizar resposta inadequada; escopo, namespace, limiar alto e validade são essenciais. Roteamento barato→caro deve considerar complexidade, risco e requisito de qualidade e ser avaliado por tarefa. Streaming melhora tempo até o primeiro texto visível, mas não reduz necessariamente tokens nem custo total. Um orçamento local de tokens é um limite de controle, não uma estimativa de custo em USD.

## Respostas para entrevista

### EN — How do you evaluate an agent toolkit without a live model?

I test the evaluation pipeline with versioned synthetic fixtures and a deliberately degraded runner. This proves that graders and regression thresholds behave as intended, but it does not estimate real model quality. A live or replay evaluation needs separately approved data, a traceable cassette or provider configuration, and a recorded budget.

### PT — Como avaliar um toolkit de agente sem um modelo live?

Eu testo o pipeline com fixtures sintéticas versionadas e um runner deliberadamente degradado. Isso verifica os graders e os limites de regressão, mas não estima a qualidade real do modelo. Uma avaliação live ou replay exige dados aprovados, cassette rastreável ou configuração do provedor e orçamento registrado.

### EN — What is the difference between direct and indirect prompt injection?

Direct injection is supplied in the user message. Indirect injection is embedded in retrieved or tool-provided content. Both are untrusted data; controls should combine screening with least-privilege tool authorization and bounded execution rather than trusting a prompt instruction alone.

### PT — Qual a diferença entre injeção direta e indireta?

Na direta, a instrução maliciosa vem na mensagem do usuário. Na indireta, ela está em conteúdo recuperado ou retornado por uma tool. Ambos são dados não confiáveis; os controles devem combinar triagem, autorização de menor privilégio e limites de execução, sem depender somente do prompt.

### EN — When is semantic caching unsafe?

When similar wording can imply different tenants, policies, dates, or actions. Namespace by relevant context and version, use a conservative similarity threshold, and measure misses and false hits on reviewed cases before relying on it.

### PT — Quando o cache semântico é inseguro?

Quando textos parecidos podem representar tenants, políticas, datas ou ações diferentes. Separe por contexto e versão, use limiar conservador e meça falsos hits em casos revisados antes de depender do cache.
