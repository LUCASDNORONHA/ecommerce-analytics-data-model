# Consultas de consumo

Consultas de exportação da M06-06 destinadas a consumidores SQL e à importação
no Power BI. Cada arquivo seleciona explicitamente as colunas de uma view do
schema `analytics`, evitando contratos dependentes de `SELECT *`.

| Ordem | Dataset de consumo | Fonte | Granularidade |
|---:|---|---|---|
| 01 | `fato_pedido_financeiro` | `analytics.vw_pedido_financeiro` | Uma linha por pedido |
| 02 | `agregado_financeiro_mensal` | `analytics.vw_financeiro_mensal` | Uma linha por mês de compra |
| 03 | `fato_vendedor_pedido` | `analytics.vw_vendedor_pedido` | Uma linha por vendedor e pedido entregue |
| 04 | `resumo_desempenho_vendedor` | `analytics.vw_desempenho_vendedor` | Uma linha por vendedor ativo |

Os nomes à esquerda são nomes recomendados para as tabelas no modelo semântico;
as views permanecem como fontes canônicas. O contrato de importação,
relacionamentos e medidas está documentado em
[`../../docs/analytics/consumo_power_bi_sql.md`](../../docs/analytics/consumo_power_bi_sql.md).

As consultas não devem ser combinadas por joins ad hoc. Em especial, medidas
de pedido não podem ser somadas após relacionamento ou join com
`fato_vendedor_pedido`, pois pedidos com múltiplos vendedores seriam repetidos.
