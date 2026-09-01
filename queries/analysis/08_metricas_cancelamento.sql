/*
Pergunta: qual é a taxa de cancelamento e quais valores observados estão
associados aos pedidos cancelados?

Saída: uma linha por mês de compra, considerando todos os pedidos no
denominador da taxa. Itens e pagamentos são pré-agregados por pedido.

Limitação: valor associado não representa perda, estorno ou receita cancelada.
Pedidos cancelados podem não possuir itens, pagamentos ou o ciclo financeiro
completo na fonte.
*/
WITH itens AS (
    SELECT
        id_pedido,
        SUM(preco_item) AS valor_itens,
        SUM(valor_frete) AS valor_frete,
        SUM(preco_item + valor_frete) AS valor_bruto
    FROM core.item_pedido
    GROUP BY id_pedido
),
pagamentos AS (
    SELECT
        id_pedido,
        SUM(valor_pagamento) AS valor_pago_registrado
    FROM core.pagamento
    GROUP BY id_pedido
)
SELECT
    DATE_TRUNC('month', p.data_compra)::date AS mes_compra,
    COUNT(*) AS pedidos,
    COUNT(*) FILTER (WHERE p.status_pedido = 'canceled') AS pedidos_cancelados,
    ROUND(
        100.0 * COUNT(*) FILTER (WHERE p.status_pedido = 'canceled')
            / NULLIF(COUNT(*), 0),
        4
    ) AS taxa_cancelamento_quantidade_percentual,
    SUM(COALESCE(i.valor_itens, 0))
        FILTER (WHERE p.status_pedido = 'canceled')
        AS valor_itens_associado_cancelados,
    SUM(COALESCE(i.valor_frete, 0))
        FILTER (WHERE p.status_pedido = 'canceled')
        AS valor_frete_associado_cancelados,
    SUM(COALESCE(i.valor_bruto, 0))
        FILTER (WHERE p.status_pedido = 'canceled')
        AS valor_bruto_associado_cancelados,
    SUM(COALESCE(pg.valor_pago_registrado, 0))
        FILTER (WHERE p.status_pedido = 'canceled')
        AS valor_pago_registrado_associado_cancelados,
    COUNT(*) FILTER (
        WHERE p.status_pedido = 'canceled' AND i.id_pedido IS NULL
    ) AS cancelados_sem_itens,
    COUNT(*) FILTER (
        WHERE p.status_pedido = 'canceled' AND pg.id_pedido IS NULL
    ) AS cancelados_sem_pagamentos
FROM core.pedido AS p
LEFT JOIN itens AS i USING (id_pedido)
LEFT JOIN pagamentos AS pg USING (id_pedido)
GROUP BY DATE_TRUNC('month', p.data_compra)::date
ORDER BY mes_compra;
