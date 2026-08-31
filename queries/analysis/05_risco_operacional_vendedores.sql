/*
Pergunta: quais vendedores combinam contribuição financeira e riscos associados?
Atraso de entrega e avaliação pertencem ao pedido e não provam responsabilidade
do vendedor. Avaliações são pré-agregadas por pedido.
*/
WITH avaliacao AS (
    SELECT id_pedido, AVG(nota_avaliacao) AS nota_media_pedido
    FROM core.avaliacao GROUP BY id_pedido
), vendedor_pedido AS (
    SELECT i.id_vendedor, i.id_pedido, SUM(i.preco_item) AS valor_itens,
        BOOL_OR(p.data_envio_transportador > i.data_limite_envio)
            AS envio_apos_limite,
        p.data_entrega > p.data_estimada AS entrega_atrasada,
        a.nota_media_pedido
    FROM core.item_pedido i
    INNER JOIN core.pedido p USING (id_pedido)
    LEFT JOIN avaliacao a USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
    GROUP BY i.id_vendedor, i.id_pedido, p.data_entrega, p.data_estimada,
        a.nota_media_pedido
)
SELECT id_vendedor, COUNT(*) AS pedidos_com_participacao,
    SUM(valor_itens) AS valor_itens,
    ROUND(100.0 * COUNT(*) FILTER (WHERE envio_apos_limite) /
        NULLIF(COUNT(envio_apos_limite), 0), 2)
        AS taxa_envio_apos_limite_percentual,
    ROUND(100.0 * COUNT(*) FILTER (WHERE entrega_atrasada) /
        NULLIF(COUNT(entrega_atrasada), 0), 2)
        AS taxa_pedidos_atrasados_associados_percentual,
    ROUND(AVG(nota_media_pedido), 2) AS nota_media_associada,
    ROUND(100.0 * COUNT(*) FILTER (WHERE nota_media_pedido <= 2) /
        NULLIF(COUNT(nota_media_pedido), 0), 2)
        AS taxa_avaliacao_negativa_associada_percentual
FROM vendedor_pedido GROUP BY id_vendedor
ORDER BY valor_itens DESC, id_vendedor;
