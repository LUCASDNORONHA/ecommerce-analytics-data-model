/*
Pergunta: como evoluíram os valores dos pedidos entregues e sua reconciliação?
Saída: uma linha por mês de compra. Meses sem cobertura diária completa são
sinalizados e não recebem crescimento comparável.
*/
WITH itens AS (
    SELECT id_pedido, COUNT(*) AS itens,
        SUM(preco_item) AS valor_itens, SUM(valor_frete) AS valor_frete,
        SUM(preco_item + valor_frete) AS valor_bruto
    FROM core.item_pedido GROUP BY id_pedido
), pagamentos AS (
    SELECT id_pedido, SUM(valor_pagamento) AS valor_pago
    FROM core.pagamento GROUP BY id_pedido
), mensal AS (
    SELECT DATE_TRUNC('month', p.data_compra)::date AS mes_compra,
        COUNT(*) AS pedidos, SUM(i.itens) AS itens,
        SUM(i.valor_itens) AS valor_itens, SUM(i.valor_frete) AS valor_frete,
        SUM(i.valor_bruto) AS valor_bruto, SUM(pg.valor_pago) AS valor_pago,
        COUNT(DISTINCT p.data_compra::date) AS dias_com_pedidos
    FROM core.pedido p
    INNER JOIN itens i USING (id_pedido)
    INNER JOIN pagamentos pg USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
    GROUP BY DATE_TRUNC('month', p.data_compra)::date
), mensal_cobertura AS (
    SELECT *, dias_com_pedidos = EXTRACT(DAY FROM
        mes_compra + INTERVAL '1 month - 1 day') AS cobertura_diaria_completa
    FROM mensal
), comparacao AS (
    SELECT *, LAG(valor_itens) OVER (ORDER BY mes_compra) AS valor_itens_anterior,
        LAG(cobertura_diaria_completa) OVER (ORDER BY mes_compra)
            AS cobertura_anterior_completa
    FROM mensal_cobertura
)
SELECT mes_compra, cobertura_diaria_completa, pedidos, itens, valor_itens,
    valor_frete, valor_bruto, valor_pago,
    valor_pago - valor_bruto AS diferenca_reconciliacao,
    ROUND(valor_bruto / NULLIF(pedidos, 0), 2) AS valor_bruto_medio_pedido,
    ROUND(100.0 * valor_frete / NULLIF(valor_bruto, 0), 2) AS percentual_frete,
    CASE WHEN cobertura_diaria_completa AND cobertura_anterior_completa THEN
        ROUND(100.0 * (valor_itens / NULLIF(valor_itens_anterior, 0) - 1), 2)
    END AS crescimento_mensal_comparavel_percentual
FROM comparacao ORDER BY mes_compra;
