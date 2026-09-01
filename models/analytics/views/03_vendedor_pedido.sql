CREATE OR REPLACE VIEW analytics.vw_vendedor_pedido AS
WITH avaliacoes AS (
    SELECT
        id_pedido,
        AVG(nota_avaliacao) AS nota_media_pedido
    FROM core.avaliacao
    GROUP BY id_pedido
)
SELECT
    i.id_vendedor,
    i.id_pedido,
    p.data_compra,
    DATE_TRUNC('month', p.data_compra)::date AS mes_compra,
    v.cidade AS cidade_vendedor,
    v.estado AS estado_vendedor,
    c.cidade AS cidade_cliente,
    c.estado AS estado_cliente,
    COUNT(*) AS quantidade_itens,
    COUNT(*) FILTER (
        WHERE p.data_envio_transportador IS NOT NULL
    ) AS itens_com_envio_observado,
    COUNT(*) FILTER (
        WHERE p.data_envio_transportador > i.data_limite_envio
    ) AS itens_enviados_apos_limite,
    BOOL_OR(p.data_envio_transportador > i.data_limite_envio)
        AS possui_item_enviado_apos_limite,
    SUM(i.preco_item) AS valor_itens,
    SUM(i.valor_frete) AS valor_frete,
    SUM(i.preco_item + i.valor_frete) AS valor_bruto,
    p.data_entrega > p.data_estimada AS entrega_atrasada_associada,
    a.nota_media_pedido AS nota_media_associada
FROM core.item_pedido AS i
INNER JOIN core.pedido AS p USING (id_pedido)
INNER JOIN core.vendedor AS v USING (id_vendedor)
INNER JOIN core.cliente AS c USING (id_cliente)
LEFT JOIN avaliacoes AS a USING (id_pedido)
WHERE p.status_pedido = 'delivered'
GROUP BY
    i.id_vendedor,
    i.id_pedido,
    p.data_compra,
    v.cidade,
    v.estado,
    c.cidade,
    c.estado,
    p.data_entrega,
    p.data_estimada,
    a.nota_media_pedido;

COMMENT ON VIEW analytics.vw_vendedor_pedido IS
'Uma linha por vendedor e pedido entregue. Valores de itens são diretos; entrega e avaliação são apenas associadas.';
