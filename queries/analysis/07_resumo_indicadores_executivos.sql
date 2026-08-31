/*
Pergunta: quais são os principais indicadores históricos do produto analítico?
Saída: uma única linha para pedidos entregues com itens e pagamentos.
Data de referência: data_compra; período histórico completo.
Limitação: valores representam registros observados, não receita ou lucro.
*/
WITH itens AS (
    SELECT id_pedido, COUNT(*) AS itens, COUNT(DISTINCT id_vendedor) AS vendedores,
        SUM(preco_item) AS valor_itens, SUM(valor_frete) AS valor_frete,
        SUM(preco_item + valor_frete) AS valor_bruto
    FROM core.item_pedido GROUP BY id_pedido
), pagamentos AS (
    SELECT id_pedido, SUM(valor_pagamento) AS valor_pago
    FROM core.pagamento GROUP BY id_pedido
), base AS (
    SELECT p.id_pedido, i.*, pg.valor_pago
    FROM core.pedido p
    INNER JOIN itens i USING (id_pedido)
    INNER JOIN pagamentos pg USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
), vendedor AS (
    SELECT i.id_vendedor, SUM(i.preco_item) AS valor_itens
    FROM core.item_pedido i INNER JOIN core.pedido p USING (id_pedido)
    WHERE p.status_pedido = 'delivered' GROUP BY i.id_vendedor
), vendedor_rank AS (
    SELECT *, ROW_NUMBER() OVER (ORDER BY valor_itens DESC, id_vendedor) AS posicao,
        valor_itens / SUM(valor_itens) OVER () AS participacao
    FROM vendedor
), vendedor_resumo AS (
    SELECT COUNT(*) AS vendedores_ativos,
        SUM(participacao) FILTER (WHERE posicao <= 5) AS participacao_top_5,
        SUM(participacao) FILTER (WHERE posicao <= 10) AS participacao_top_10,
        SUM(POWER(participacao, 2)) AS hhi
    FROM vendedor_rank
)
SELECT COUNT(*) AS pedidos_entregues_completos,
    SUM(b.itens) AS itens, SUM(b.valor_itens) AS valor_itens,
    SUM(b.valor_frete) AS valor_frete, SUM(b.valor_bruto) AS valor_bruto,
    SUM(b.valor_pago) AS valor_pago_registrado,
    SUM(b.valor_pago - b.valor_bruto) AS diferenca_reconciliacao,
    ROUND(SUM(b.valor_bruto) / COUNT(*), 2) AS valor_bruto_medio_pedido,
    ROUND(100.0 * SUM(b.valor_frete) / SUM(b.valor_bruto), 2)
        AS percentual_frete,
    COUNT(*) FILTER (WHERE b.vendedores > 1) AS pedidos_multivendedor,
    vr.vendedores_ativos,
    ROUND(100.0 * vr.participacao_top_5, 2) AS participacao_top_5_percentual,
    ROUND(100.0 * vr.participacao_top_10, 2) AS participacao_top_10_percentual,
    ROUND(vr.hhi, 6) AS hhi_base_observada
FROM base b CROSS JOIN vendedor_resumo vr
GROUP BY vr.vendedores_ativos, vr.participacao_top_5,
    vr.participacao_top_10, vr.hhi;
