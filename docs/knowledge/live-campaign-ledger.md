# Ledger local de campanha — P02

## Aprendizado

Registre a reserva antes de qualquer despacho. Se a resposta não informar tokens ou custo, mantenha a reserva integral para não subestimar consumo acumulado. Cada caso/trial reservado, inclusive resultado semântico ruim, permanece imutável e não pode ser enviado novamente por `--resume`.

O ledger do P02 usa SQLite append-only, transações `BEGIN IMMEDIATE` para limitar corridas entre processos, e um lease do sistema operacional. A inspeção `--resume CAMPAIGN_ID --dry-run` abre o estado em modo somente leitura e mostra apenas campos operacionais sanitizados.

## Limites atuais

A fase não implementa despacho Groq nem conecta o lease a uma execução live aprovada. Não há quota, teto cumulativo, autorização de gasto, revisão independente de casos/rubrica ou preflight de catálogo. A campanha segue bloqueada; USD 0 permanece o limite do perfil. Não há contabilização compartilhada entre os seis repositórios.

## Resposta de entrevista (PT-BR)

Implementei um ledger append-only com reserva atômica, proteção contra repetição de tentativas incertas e inspeção read-only de retomada. O sistema operacional bloqueia duas campanhas P02 simultâneas. A infraestrutura foi validada offline, mas não autoriza execução live: o perfil continua em USD 0 e os limites e revisões da campanha permanecem pendentes.

## Interview answer (English)

I added an append-only ledger with atomic reservations, protection against replaying uncertain attempts, and read-only resume inspection. An OS process lease prevents concurrent P02 campaigns. The offline foundation does not authorize live execution: the project profile remains at USD 0 and campaign limits and reviews are still pending.
