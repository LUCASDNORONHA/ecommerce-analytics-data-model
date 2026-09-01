CREATE OR REPLACE VIEW analytics.vw_financeiro_mensal AS
WITH mensal AS (
    SELECT
        mes_compra,
        COUNT(*) AS pedidos,
        COUNT(*) FILTER (WHERE status_pedido = 'delivered')
            AS pedidos_entregues,
        COUNT(*) FILTER (
            WHERE status_pedido = 'delivered'
              AND possui_itens
              AND possui_pagamentos
        ) AS pedidos_entregues_completos,
        COUNT(*) FILTER (WHERE status_pedido = 'canceled')
            AS pedidos_cancelados,
        COUNT(DISTINCT data_compra::date) AS dias_com_pedidos,
        SUM(valor_itens) FILTER (
            WHERE status_pedido = 'delivered'
              AND possui_itens
              AND possui_pagamentos
        ) AS valor_itens_entregues,
        SUM(valor_frete) FILTER (
            WHERE status_pedido = 'delivered'
              AND possui_itens
              AND possui_pagamentos
        ) AS valor_frete_entregue,
        SUM(valor_bruto) FILTER (
            WHERE status_pedido = 'delivered'
              AND possui_itens
              AND possui_pagamentos
        ) AS valor_bruto_entregue,
        SUM(valor_pago_registrado) FILTER (
            WHERE status_pedido = 'delivered'
              AND possui_itens
              AND possui_pagamentos
        ) AS valor_pago_registrado_entregue,
        SUM(diferenca_reconciliacao) FILTER (
            WHERE status_pedido = 'delivered'
              AND possui_itens
              AND possui_pagamentos
        ) AS diferenca_reconciliacao_entregue,
        SUM(COALESCE(valor_itens, 0)) FILTER (
            WHERE status_pedido = 'canceled'
        ) AS valor_itens_associado_cancelados,
        SUM(COALESCE(valor_frete, 0)) FILTER (
            WHERE status_pedido = 'canceled'
        ) AS valor_frete_associado_cancelados,
        SUM(COALESCE(valor_bruto, 0)) FILTER (
            WHERE status_pedido = 'canceled'
        ) AS valor_bruto_associado_cancelados,
        SUM(COALESCE(valor_pago_registrado, 0)) FILTER (
            WHERE status_pedido = 'canceled'
        ) AS valor_pago_registrado_associado_cancelados
    FROM analytics.vw_pedido_financeiro
    GROUP BY mes_compra
),
cobertura AS (
    SELECT
        *,
        dias_com_pedidos = EXTRACT(
            DAY FROM mes_compra + INTERVAL '1 month - 1 day'
        ) AS cobertura_diaria_completa
    FROM mensal
),
comparacao AS (
    SELECT
        *,
        LAG(valor_itens_entregues) OVER (ORDER BY mes_compra)
            AS valor_itens_mes_anterior,
        LAG(cobertura_diaria_completa) OVER (ORDER BY mes_compra)
            AS cobertura_anterior_completa
    FROM cobertura
)
SELECT
    mes_compra,
    cobertura_diaria_completa,
    pedidos,
    pedidos_entregues,
    pedidos_entregues_completos,
    pedidos_cancelados,
    ROUND(100.0 * pedidos_cancelados / NULLIF(pedidos, 0), 4)
        AS taxa_cancelamento_quantidade_percentual,
    valor_itens_entregues,
    valor_frete_entregue,
    valor_bruto_entregue,
    valor_pago_registrado_entregue,
    diferenca_reconciliacao_entregue,
    ROUND(
        valor_bruto_entregue / NULLIF(pedidos_entregues_completos, 0),
        2
    ) AS valor_bruto_medio_pedido_entregue,
    ROUND(
        100.0 * valor_frete_entregue / NULLIF(valor_bruto_entregue, 0),
        2
    ) AS participacao_frete_percentual,
    CASE
        WHEN cobertura_diaria_completa AND cobertura_anterior_completa
            THEN ROUND(
                100.0 * (
                    valor_itens_entregues
                    / NULLIF(valor_itens_mes_anterior, 0) - 1
                ),
                2
            )
    END AS crescimento_mensal_valor_itens_percentual,
    valor_itens_associado_cancelados,
    valor_frete_associado_cancelados,
    valor_bruto_associado_cancelados,
    valor_pago_registrado_associado_cancelados
FROM comparacao;

COMMENT ON VIEW analytics.vw_financeiro_mensal IS
'Uma linha por mês de compra, com métricas financeiras entregues, cancelamento e sinalização de cobertura temporal.';
