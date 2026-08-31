/* Pergunta: quais combinações de vendedor e categoria geram maior valor? */
SELECT i.id_vendedor, COALESCE(pr.nome_categoria, 'sem_categoria') AS categoria,
    COUNT(*) AS itens, COUNT(DISTINCT i.id_pedido) AS pedidos,
    SUM(i.preco_item) AS valor_itens, SUM(i.valor_frete) AS valor_frete,
    ROUND(100.0 * SUM(i.preco_item) /
        SUM(SUM(i.preco_item)) OVER (PARTITION BY i.id_vendedor), 2)
        AS participacao_categoria_no_vendedor_percentual,
    ROUND(100.0 * SUM(i.preco_item) /
        SUM(SUM(i.preco_item)) OVER (PARTITION BY pr.nome_categoria), 2)
        AS participacao_vendedor_na_categoria_percentual
FROM core.item_pedido i
INNER JOIN core.pedido p USING (id_pedido)
INNER JOIN core.produto pr USING (id_produto)
WHERE p.status_pedido = 'delivered'
GROUP BY i.id_vendedor, COALESCE(pr.nome_categoria, 'sem_categoria'),
    pr.nome_categoria
ORDER BY valor_itens DESC, i.id_vendedor, categoria;
