CREATE OR REPLACE VIEW analytics.vw_pedido_financeiro AS
WITH itens AS (
    SELECT
        id_pedido,
        COUNT(*) AS quantidade_itens,
        COUNT(DISTINCT id_vendedor) AS quantidade_vendedores,
        SUM(preco_item) AS valor_itens,
        SUM(valor_frete) AS valor_frete,
        SUM(preco_item + valor_frete) AS valor_bruto
    FROM core.item_pedido
    GROUP BY id_pedido
),
pagamentos AS (
    SELECT
        id_pedido,
        COUNT(*) AS quantidade_pagamentos,
        COUNT(DISTINCT tipo_pagamento) AS quantidade_tipos_pagamento,
        MAX(numero_parcelas) AS maximo_parcelas,
        SUM(valor_pagamento) AS valor_pago_registrado
    FROM core.pagamento
    GROUP BY id_pedido
),
avaliacoes AS (
    SELECT
        id_pedido,
        COUNT(*) AS quantidade_avaliacoes,
        AVG(nota_avaliacao) AS nota_media_pedido
    FROM core.avaliacao
    GROUP BY id_pedido
)
SELECT
    p.id_pedido,
    p.id_cliente,
    c.id_cliente_unico,
    c.cidade AS cidade_cliente,
    c.estado AS estado_cliente,
    p.status_pedido,
    p.data_compra,
    DATE_TRUNC('month', p.data_compra)::date AS mes_compra,
    p.data_aprovacao,
    p.data_envio_transportador,
    p.data_entrega,
    p.data_estimada,
    p.data_entrega > p.data_estimada AS entrega_atrasada,
    i.id_pedido IS NOT NULL AS possui_itens,
    pg.id_pedido IS NOT NULL AS possui_pagamentos,
    a.id_pedido IS NOT NULL AS possui_avaliacao,
    COALESCE(i.quantidade_itens, 0) AS quantidade_itens,
    COALESCE(i.quantidade_vendedores, 0) AS quantidade_vendedores,
    i.valor_itens,
    i.valor_frete,
    i.valor_bruto,
    COALESCE(pg.quantidade_pagamentos, 0) AS quantidade_pagamentos,
    COALESCE(pg.quantidade_tipos_pagamento, 0) AS quantidade_tipos_pagamento,
    pg.maximo_parcelas,
    pg.valor_pago_registrado,
    CASE
        WHEN i.id_pedido IS NOT NULL AND pg.id_pedido IS NOT NULL
            THEN pg.valor_pago_registrado - i.valor_bruto
    END AS diferenca_reconciliacao,
    COALESCE(a.quantidade_avaliacoes, 0) AS quantidade_avaliacoes,
    a.nota_media_pedido
FROM core.pedido AS p
INNER JOIN core.cliente AS c USING (id_cliente)
LEFT JOIN itens AS i USING (id_pedido)
LEFT JOIN pagamentos AS pg USING (id_pedido)
LEFT JOIN avaliacoes AS a USING (id_pedido);

COMMENT ON VIEW analytics.vw_pedido_financeiro IS
'Uma linha por pedido, com itens, pagamentos e avaliações pré-agregados. Valores nulos preservam relações ausentes.';
