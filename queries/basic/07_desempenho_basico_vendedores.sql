/*
Objetivo: medir a contribuição financeira diretamente atribuível aos vendedores.
Pergunta: quais vendedores concentram itens, pedidos e valor dos itens?
Entradas: core.item_pedido e core.pedido.
Saída: uma linha por id_vendedor no período histórico.
Data de referência: core.pedido.data_compra.
Filtros: pedidos entregues.
Limitação: pedido e avaliação pertencem ao pedido; valor de pagamento não é
atribuído ao vendedor. O valor médio considera somente a parcela de itens do
vendedor nos pedidos em que ele participou.
*/

WITH vendedores AS (
    SELECT
        i.id_vendedor,
        COUNT(*) AS quantidade_itens,
        COUNT(DISTINCT i.id_pedido) AS pedidos_com_participacao,
        SUM(i.preco_item) AS valor_itens,
        SUM(i.valor_frete) AS valor_frete,
        SUM(i.preco_item + i.valor_frete) AS valor_bruto
    FROM core.item_pedido AS i
    INNER JOIN core.pedido AS p USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
    GROUP BY i.id_vendedor
)
SELECT
    id_vendedor,
    quantidade_itens,
    pedidos_com_participacao,
    valor_itens,
    valor_frete,
    valor_bruto,
    ROUND(valor_itens / NULLIF(quantidade_itens, 0), 2)
        AS valor_medio_por_item,
    ROUND(valor_itens / NULLIF(pedidos_com_participacao, 0), 2)
        AS valor_medio_por_pedido_com_participacao,
    ROUND(100.0 * valor_itens / SUM(valor_itens) OVER (), 4)
        AS participacao_valor_itens_percentual,
    ROUND(
        100.0 * SUM(valor_itens) OVER (
            ORDER BY valor_itens DESC, id_vendedor
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) / SUM(valor_itens) OVER (),
        4
    ) AS participacao_acumulada_percentual
FROM vendedores
ORDER BY valor_itens DESC, id_vendedor;
