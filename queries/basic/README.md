# Consultas básicas

Consultas fundamentais sobre o modelo `core`, organizadas e documentadas por
finalidade analítica.

## Ordem de execução

1. `01_pedidos_por_status.sql`: distribuição e participação dos status.
2. `02_cobertura_temporal.sql`: período disponível e cobertura mensal.
3. `03_valores_por_pedido.sql`: itens e frete agregados por pedido.
4. `04_pagamentos_por_pedido.sql`: pagamentos agregados por pedido.
5. `05_resumo_financeiro_mensal.sql`: visão financeira de pedidos entregues.
6. `06_composicao_pagamentos.sql`: tipos e condições de pagamento.
7. `07_desempenho_basico_vendedores.sql`: contribuição direta dos vendedores.
8. `08_pedidos_multivendedor.sql`: frequência de pedidos com vários vendedores.
9. `09_valor_por_categoria_regiao.sql`: valor por categoria e estado do cliente.

As consultas utilizam `core.pedido.data_compra` como referência temporal. As
métricas principais de desempenho utilizam pedidos entregues; consultas de
cobertura ou composição informam explicitamente quando adotam outra base.

As validações de reconciliação e de risco de duplicação estão em
[`../validation/`](../validation/).
