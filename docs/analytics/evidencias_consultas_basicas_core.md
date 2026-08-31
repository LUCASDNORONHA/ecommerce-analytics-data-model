# Evidências das consultas básicas sobre a CORE

## 1. Finalidade

Este documento registra os principais resultados de controle obtidos durante a
implementação das consultas básicas da etapa M06-01. Os resultados foram
produzidos sobre a CORE local validada e servem para confirmar decisões de
granularidade do contrato analítico.

As evidências não substituem os SQLs versionados em `queries/` e não transformam
características observadas no dataset em regras de negócio.

## 2. Base executada

| Relação CORE | Registros |
|---|---:|
| `core.pedido` | 99.441 |
| `core.item_pedido` | 112.650 |
| `core.pagamento` | 103.886 |
| `core.vendedor` | 3.095 |

As consultas foram executadas no PostgreSQL 18 contra o resultado aprovado do
ELT.

## 3. Status dos pedidos

| Status | Pedidos | Participação |
|---|---:|---:|
| delivered | 96.478 | 97,02% |
| shipped | 1.107 | 1,11% |
| canceled | 625 | 0,63% |
| unavailable | 609 | 0,61% |
| invoiced | 314 | 0,32% |
| processing | 301 | 0,30% |
| created | 5 | 0,01% |
| approved | 2 | menor que 0,01% |

Decisão: os KPIs financeiros principais utilizarão pedidos entregues. Os demais
status permanecerão disponíveis para cobertura, reconciliação e investigação.

## 4. Cobertura temporal

`core.pedido.data_compra` varia de setembro de 2016 a outubro de 2018. Os meses
de borda e transição que não possuem pedidos em todos os dias são:

- setembro, outubro e dezembro de 2016;
- janeiro de 2017;
- setembro e outubro de 2018.

Fevereiro de 2017 a agosto de 2018 possuem ao menos um pedido em todos os dias
do respectivo mês. A ausência de pedidos em parte de um mês é um sinal de
cobertura parcial, não uma prova isolada de perda de dados.

Decisão: comparações mensais e taxas de crescimento devem destacar ou excluir
meses sem cobertura diária completa, conforme o objetivo da análise.

## 5. Cobertura das relações de pedido

A maior parte dos pedidos possui itens e pagamentos. Foram observadas exceções:

- um pedido entregue possui itens e não possui pagamento;
- 164 pedidos cancelados possuem pagamentos e não possuem itens;
- 603 pedidos indisponíveis possuem pagamentos e não possuem itens;
- ocorrências menores também existem nos status `created`, `invoiced` e
  `shipped`.

Decisão: métricas que exigem itens e pagamentos devem utilizar `INNER JOIN` após
pré-agregação e declarar que sua população exclui pedidos sem uma das relações.
Consultas de cobertura devem preservar as exceções.

## 6. Risco de multiplicação entre itens e pagamentos

O join direto entre `core.item_pedido` e `core.pagamento` produziu 117.601
linhas. Sem pré-agregação, itens são repetidos pela quantidade de pagamentos e
pagamentos são repetidos pela quantidade de itens do pedido.

A consulta de controle compara o join direto somente com pedidos presentes nas
duas relações. O resultado comprova que somas financeiras realizadas após esse
join não são válidas.

Decisão: itens e pagamentos devem ser agregados separadamente por `id_pedido`
antes da combinação.

## 7. Reconciliação financeira

Entre os pedidos entregues que possuem itens e pagamentos:

- 96.178 estão conciliados dentro da tolerância de R$ 0,01;
- 260 possuem pagamento registrado maior que o valor bruto;
- 39 possuem valor bruto maior que o pagamento registrado;
- a maior diferença absoluta observada é R$ 182,81.

A tolerância absorve somente diferenças de centavos. Divergências maiores não
comprovam erro, estorno ou perda financeira, pois a fonte não contém todo o
ciclo contábil.

Decisão: a reconciliação será mantida como indicador de qualidade e investigação,
não como ajuste automático dos valores.

## 8. Pedidos com múltiplos vendedores

Na base de pedidos entregues com itens:

| Classificação | Pedidos | Participação |
|---|---:|---:|
| Um vendedor | 95.203 | 98,6785% |
| Múltiplos vendedores | 1.275 | 1,3215% |

Os pedidos multivendedor contêm 3.097 itens e R$ 268.630,76 em valor dos itens.

Decisão: pagamentos, avaliações, cancelamentos e atrasos de entrega não serão
atribuídos integralmente a cada vendedor. Quando usados, serão descritos como
indicadores associados ao pedido com participação do vendedor.

## 9. Reconciliação da atribuição aos vendedores

Para pedidos entregues:

- 110.197 itens da base foram atribuídos a vendedores;
- a diferença entre itens da base e itens atribuídos foi zero;
- R$ 13.221.498,11 em valor dos itens foram atribuídos;
- a diferença monetária da atribuição foi R$ 0,00;
- existem 1.341 participações adicionais em pedidos devido a pedidos com mais
  de um vendedor.

Decisão: valores e itens podem ser atribuídos diretamente aos vendedores. A
contagem de participações por vendedor não deve ser confundida com pedidos
distintos do marketplace.

## 10. Consultas relacionadas

- `queries/basic/01_pedidos_por_status.sql`;
- `queries/basic/02_cobertura_temporal.sql`;
- `queries/basic/08_pedidos_multivendedor.sql`;
- `queries/validation/01_reconciliacao_financeira.sql`;
- `queries/validation/02_controle_join_itens_pagamentos.sql`;
- `queries/validation/03_cobertura_relacoes_pedido.sql`;
- `queries/validation/04_granularidade_vendedor.sql`.
