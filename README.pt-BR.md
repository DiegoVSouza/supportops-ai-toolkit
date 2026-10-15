# Toolkit de IA SupportOps

A versão `0.1.0` oferece controles locais para fluxos determinísticos de SupportOps: contratos de tools, execução resiliente, avaliações por código, segurança e utilitários de custo. Os dados de exemplo e resultados fake são fixtures, não medições de produção.

## Requisitos e configuração

- Python `3.13+` (o ambiente verificado está registrado em `docs/harness/sources.lock.json`).
- O runtime não tem dependências de terceiros. A ferramenta de build está fixada em `requirements-build.lock`.
- O modo padrão é `LLM_MODE=fake`; não há adaptador de modelo live nem conectores externos.

Execute o gate determinístico completo na raiz:

```powershell
$env:LLM_MODE = 'fake'
python scripts/check_full.py
```

Execute um exemplo de tool local:

```powershell
python -c "from supportops_toolkit.sample_tools import lookup_invoice; print(lookup_invoice(invoice_id='inv-100'))"
```

## Como definir uma tool

Use o decorator `tool` com o subconjunto de JSON Schema documentado no README em inglês. Keywords não suportadas falham no registro; booleanos não são números e valores numéricos precisam ser finitos. O registry rejeita nomes duplicados e valida argumentos e resultados.

Retries automáticos exigem `ToolError(retryable=True)` explícito. Timeout e erro genérico de transporte têm resultado ambíguo e não são repetidos, pois a thread pode continuar ou já ter aplicado um efeito. O timeout em thread interrompe a espera do chamador, mas Python não encerra uma thread que continua executando. Passe `execution_limits=limits` à tool para contar uma etapa e limitar a espera ao tempo restante; use processo ou serviço isolado para cancelamento forçado.

## Executar avaliações e entender regressões

```powershell
$env:LLM_MODE = 'fake'
python -m supportops_toolkit.evals.runner --dataset evals/datasets/v1/supportops.jsonl --baseline evals/baseline/v1.json
```

O runner calcula acurácia de decisão e tool, groundedness por regra e acerto de escalonamento. Uma queda acima de `--max-drop` falha o gate e os casos com erro aparecem no relatório. Os resultados atuais refletem apenas rótulos sintéticos determinísticos; não representam qualidade de modelo.

## Estender guardrails

`guard` detecta instruções suspeitas, permite, bloqueia ou devolve texto com PII mascarada. `authorize_tool` valida a role contra a lista permitida. `ExecutionLimits` limita passos e tempo no caminho de execução; o runtime que possui a chamada LLM deve registrar o uso por `limits.consume(tokens=...)`. Como P02 não integra um runtime de agente/LLM, o limite total de tokens permanece INCOMPLETE. A suíte com 35 exemplos cobre injeção direta e indireta via conteúdo recuperado, exfiltração, abuso de tools e reembolsos acima do limite. Os misses são listados.

Heurísticas são uma camada de defesa, não garantia contra ataques novos. O reembolso termina como `approved_pending_human`; não existe integração de pagamento.

## Interpretar o relatório de custo

`ExactCache` usa chave JSON canônica; `SemanticCache` compara conjuntos de palavras por Jaccard, dentro de um namespace. Esse cache pode considerar semelhantes textos com sentidos diferentes. `ModelRouter` escolhe apenas um nome de modelo a partir do perfil; não chama provedor. `TokenBudget` aplica um contador local e `stream_text` encaminha blocos de texto.

`python cost/report.py` mostra `PENDING`, pois ainda não há execuções comparáveis registradas. Com dois registros reais, `build_report` calcula diferenças. Não apresentamos economias ou latências simuladas como medições verdadeiras.

## Tipos de validação e evidência

- Unitários/contrato: `python -m unittest discover -s tests -v`.
- Gate offline fake: `LLM_MODE=fake python -m supportops_toolkit.evals.runner`.
- Suite adversarial: `python -m supportops_toolkit.adversarial`.
- Gate completo determinístico: `python scripts/check_full.py`.
- Integração externa, avaliação live e E2E: `INCOMPLETE`, pois não há conectores aprovados nem credenciais.

Os comandos, códigos de saída e resultados ficam em `artifacts/evidence/`. O escopo está em `.planning/phases/001-production-toolkit/`.
