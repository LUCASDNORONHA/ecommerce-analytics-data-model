-- Dataset: agregado_financeiro_mensal
-- Granularidade: uma linha por mês de compra.
-- Chave: mes_compra.
SELECT
    mes_compra,
    cobertura_diaria_completa,
    pedidos,
    pedidos_entregues,
    pedidos_entregues_completos,
    pedidos_cancelados,
    taxa_cancelamento_quantidade_percentual,
    valor_itens_entregues,
    valor_frete_entregue,
    valor_bruto_entregue,
    valor_pago_registrado_entregue,
    diferenca_reconciliacao_entregue,
    valor_bruto_medio_pedido_entregue,
    participacao_frete_percentual,
    crescimento_mensal_valor_itens_percentual,
    valor_itens_associado_cancelados,
    valor_frete_associado_cancelados,
    valor_bruto_associado_cancelados,
    valor_pago_registrado_associado_cancelados
FROM analytics.vw_financeiro_mensal;
