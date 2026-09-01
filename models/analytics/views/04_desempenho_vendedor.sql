CREATE OR REPLACE VIEW analytics.vw_desempenho_vendedor AS
WITH categorias AS (
    SELECT
        i.id_vendedor,
        COUNT(DISTINCT pr.nome_categoria) AS categorias_comercializadas
    FROM core.item_pedido AS i
    INNER JOIN core.pedido AS p USING (id_pedido)
    INNER JOIN core.produto AS pr USING (id_produto)
    WHERE p.status_pedido = 'delivered'
    GROUP BY i.id_vendedor
),
base AS (
    SELECT
        vp.id_vendedor,
        MIN(vp.cidade_vendedor) AS cidade_vendedor,
        MIN(vp.estado_vendedor) AS estado_vendedor,
        COUNT(*) AS pedidos_com_participacao,
        SUM(vp.quantidade_itens) AS quantidade_itens,
        SUM(vp.valor_itens) AS valor_itens,
        SUM(vp.valor_frete) AS valor_frete,
        SUM(vp.valor_bruto) AS valor_bruto,
        SUM(vp.itens_com_envio_observado) AS itens_com_envio_observado,
        SUM(vp.itens_enviados_apos_limite) AS itens_enviados_apos_limite,
        COUNT(vp.entrega_atrasada_associada)
            AS pedidos_com_prazo_entrega_observado,
        COUNT(*) FILTER (WHERE vp.entrega_atrasada_associada)
            AS pedidos_atrasados_associados,
        COUNT(vp.nota_media_associada) AS pedidos_com_avaliacao_associada,
        AVG(vp.nota_media_associada) AS nota_media_associada,
        COUNT(*) FILTER (WHERE vp.nota_media_associada <= 2)
            AS pedidos_com_avaliacao_negativa_associada,
        COUNT(DISTINCT vp.estado_cliente) AS estados_clientes_atendidos,
        COUNT(DISTINCT vp.cidade_cliente) AS cidades_clientes_atendidas
    FROM analytics.vw_vendedor_pedido AS vp
    GROUP BY vp.id_vendedor
),
participacao AS (
    SELECT
        b.*,
        c.categorias_comercializadas,
        b.valor_itens / SUM(b.valor_itens) OVER () AS participacao,
        SUM(b.valor_itens) OVER (
            ORDER BY b.valor_itens DESC, b.id_vendedor
        ) / SUM(b.valor_itens) OVER () AS participacao_acumulada,
        ROW_NUMBER() OVER (
            ORDER BY b.valor_itens DESC, b.id_vendedor
        ) AS posicao_valor_itens
    FROM base AS b
    INNER JOIN categorias AS c USING (id_vendedor)
)
SELECT
    id_vendedor,
    cidade_vendedor,
    estado_vendedor,
    posicao_valor_itens,
    pedidos_com_participacao,
    quantidade_itens,
    valor_itens,
    valor_frete,
    valor_bruto,
    ROUND(valor_itens / NULLIF(quantidade_itens, 0), 2)
        AS valor_medio_por_item,
    ROUND(valor_itens / NULLIF(pedidos_com_participacao, 0), 2)
        AS valor_medio_por_pedido_com_participacao,
    ROUND(100.0 * participacao, 4) AS participacao_valor_itens_percentual,
    ROUND(100.0 * participacao_acumulada, 4)
        AS participacao_acumulada_percentual,
    CASE
        WHEN participacao_acumulada <= 0.80 THEN 'A'
        WHEN participacao_acumulada <= 0.95 THEN 'B'
        ELSE 'C'
    END AS classe_abc,
    ROUND(SUM(POWER(participacao, 2)) OVER (), 6) AS hhi_base_observada,
    categorias_comercializadas,
    estados_clientes_atendidos,
    cidades_clientes_atendidas,
    itens_com_envio_observado,
    itens_enviados_apos_limite,
    ROUND(
        100.0 * itens_enviados_apos_limite
            / NULLIF(itens_com_envio_observado, 0),
        2
    ) AS taxa_itens_enviados_apos_limite_percentual,
    pedidos_com_prazo_entrega_observado,
    pedidos_atrasados_associados,
    ROUND(
        100.0 * pedidos_atrasados_associados
            / NULLIF(pedidos_com_prazo_entrega_observado, 0),
        2
    ) AS taxa_pedidos_atrasados_associados_percentual,
    pedidos_com_avaliacao_associada,
    ROUND(nota_media_associada, 2) AS nota_media_associada,
    pedidos_com_avaliacao_negativa_associada,
    ROUND(
        100.0 * pedidos_com_avaliacao_negativa_associada
            / NULLIF(pedidos_com_avaliacao_associada, 0),
        2
    ) AS taxa_avaliacao_negativa_associada_percentual
FROM participacao;

COMMENT ON VIEW analytics.vw_desempenho_vendedor IS
'Uma linha por vendedor ativo em pedidos entregues, com contribuição direta, concentração e indicadores associados.';
