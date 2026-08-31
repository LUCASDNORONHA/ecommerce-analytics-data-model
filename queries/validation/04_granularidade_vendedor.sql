/*
Controle: validar que itens e valores atribuídos aos vendedores reconciliam com
a base de pedidos entregues.
Granularidade: uma única linha de controle.
Resultado esperado: diferencas iguais a zero. Pedidos com participação pode
superar pedidos distintos porque um pedido pode conter vários vendedores.
*/

WITH base_entregue AS (
    SELECT i.*
    FROM core.item_pedido AS i
    INNER JOIN core.pedido AS p USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
),
totais_base AS (
    SELECT
        COUNT(*) AS itens_base,
        COUNT(DISTINCT id_pedido) AS pedidos_base,
        SUM(preco_item) AS valor_itens_base
    FROM base_entregue
),
por_vendedor AS (
    SELECT
        id_vendedor,
        COUNT(*) AS itens,
        COUNT(DISTINCT id_pedido) AS pedidos_com_participacao,
        SUM(preco_item) AS valor_itens
    FROM base_entregue
    GROUP BY id_vendedor
),
totais_vendedor AS (
    SELECT
        SUM(itens) AS itens_atribuidos,
        SUM(pedidos_com_participacao) AS participacoes_em_pedidos,
        SUM(valor_itens) AS valor_itens_atribuido
    FROM por_vendedor
)
SELECT
    b.itens_base,
    v.itens_atribuidos,
    v.itens_atribuidos - b.itens_base AS diferenca_itens,
    b.pedidos_base,
    v.participacoes_em_pedidos,
    v.participacoes_em_pedidos - b.pedidos_base
        AS participacoes_adicionais_multivendedor,
    b.valor_itens_base,
    v.valor_itens_atribuido,
    v.valor_itens_atribuido - b.valor_itens_base AS diferenca_valor_itens
FROM totais_base AS b
CROSS JOIN totais_vendedor AS v;
