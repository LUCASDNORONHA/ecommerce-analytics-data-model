/*
Objetivo: resumir o desempenho financeiro mensal de pedidos entregues.
Pergunta: como evoluíram pedidos, itens, frete, valor bruto e pagamentos?
Entradas: pedido (pedido), item_pedido e pagamento (pré-agregadas por pedido).
Saída: uma linha por mês de compra.
Data de referência: core.pedido.data_compra.
Filtros: status_pedido = 'delivered' e presença simultânea de itens e pagamentos.
Limitação: os valores não representam receita líquida ou lucro. Meses parciais
devem ser excluídos de comparações de crescimento após validação da cobertura.
*/

WITH itens_por_pedido AS (
    SELECT
        id_pedido,
        COUNT(*) AS quantidade_itens,
        SUM(preco_item) AS valor_itens,
        SUM(valor_frete) AS valor_frete,
        SUM(preco_item + valor_frete) AS valor_bruto
    FROM core.item_pedido
    GROUP BY id_pedido
),
pagamentos_por_pedido AS (
    SELECT
        id_pedido,
        SUM(valor_pagamento) AS valor_pago_registrado
    FROM core.pagamento
    GROUP BY id_pedido
),
resumo_mensal AS (
    SELECT
        DATE_TRUNC('month', p.data_compra)::date AS mes_compra,
        COUNT(*) AS pedidos_entregues,
        SUM(i.quantidade_itens) AS quantidade_itens,
        SUM(i.valor_itens) AS valor_itens,
        SUM(i.valor_frete) AS valor_frete,
        SUM(i.valor_bruto) AS valor_bruto,
        SUM(pg.valor_pago_registrado) AS valor_pago_registrado
    FROM core.pedido AS p
    INNER JOIN itens_por_pedido AS i USING (id_pedido)
    INNER JOIN pagamentos_por_pedido AS pg USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
    GROUP BY DATE_TRUNC('month', p.data_compra)::date
)
SELECT
    mes_compra,
    pedidos_entregues,
    quantidade_itens,
    valor_itens,
    valor_frete,
    valor_bruto,
    valor_pago_registrado,
    valor_pago_registrado - valor_bruto AS diferenca_reconciliacao,
    ROUND(valor_bruto / NULLIF(pedidos_entregues, 0), 2)
        AS valor_bruto_medio_por_pedido,
    ROUND(100.0 * valor_frete / NULLIF(valor_bruto, 0), 2)
        AS percentual_frete,
    ROUND(
        100.0 * (
            valor_itens / NULLIF(LAG(valor_itens) OVER (ORDER BY mes_compra), 0)
            - 1
        ),
        2
    ) AS crescimento_mensal_valor_itens_percentual
FROM resumo_mensal
ORDER BY mes_compra;
