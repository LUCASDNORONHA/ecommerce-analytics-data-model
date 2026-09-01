/*
Controle: validar granularidade e reconciliação das views ANALYTICS.
Resultado esperado: zero em todas as colunas de diferença.
*/
WITH granularidades AS (
    SELECT
        (SELECT COUNT(*) FROM analytics.vw_pedido_financeiro)
            - (SELECT COUNT(*) FROM core.pedido)
            AS diferenca_pedidos,
        (SELECT COUNT(*) FROM analytics.vw_pedido_financeiro)
            - (SELECT COUNT(DISTINCT id_pedido)
               FROM analytics.vw_pedido_financeiro)
            AS duplicacoes_pedido,
        (SELECT COUNT(*) FROM analytics.vw_financeiro_mensal)
            - (SELECT COUNT(DISTINCT DATE_TRUNC('month', data_compra))
               FROM core.pedido)
            AS diferenca_meses,
        (SELECT COUNT(*) FROM analytics.vw_vendedor_pedido)
            - (SELECT COUNT(*) FROM (
                SELECT i.id_vendedor, i.id_pedido
                FROM core.item_pedido AS i
                INNER JOIN core.pedido AS p USING (id_pedido)
                WHERE p.status_pedido = 'delivered'
                GROUP BY i.id_vendedor, i.id_pedido
            ) AS vendedor_pedido)
            AS diferenca_vendedor_pedido,
        (SELECT COUNT(*) FROM analytics.vw_desempenho_vendedor)
            - (SELECT COUNT(DISTINCT i.id_vendedor)
               FROM core.item_pedido AS i
               INNER JOIN core.pedido AS p USING (id_pedido)
               WHERE p.status_pedido = 'delivered')
            AS diferenca_vendedores
),
valores_core AS (
    SELECT
        SUM(i.preco_item) AS valor_itens,
        SUM(i.valor_frete) AS valor_frete,
        SUM(i.preco_item + i.valor_frete) AS valor_bruto
    FROM core.item_pedido AS i
    INNER JOIN core.pedido AS p USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
),
valores_analytics AS (
    SELECT
        SUM(valor_itens) AS valor_itens,
        SUM(valor_frete) AS valor_frete,
        SUM(valor_bruto) AS valor_bruto
    FROM analytics.vw_desempenho_vendedor
)
SELECT
    g.*,
    a.valor_itens - c.valor_itens AS diferenca_valor_itens,
    a.valor_frete - c.valor_frete AS diferenca_valor_frete,
    a.valor_bruto - c.valor_bruto AS diferenca_valor_bruto
FROM granularidades AS g
CROSS JOIN valores_core AS c
CROSS JOIN valores_analytics AS a;
