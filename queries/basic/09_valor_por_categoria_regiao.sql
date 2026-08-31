/*
Objetivo: analisar valor dos itens por categoria e estado do cliente.
Pergunta: quais combinações de categoria e estado concentram valor observado?
Entradas: item_pedido (item), pedido, produto e cliente.
Saída: uma linha por categoria e estado do cliente.
Data de referência: core.pedido.data_compra, agregada no histórico completo.
Filtros: pedidos entregues.
Limitação: categorias nulas são preservadas como 'sem_categoria'. A região é o
estado associado ao cadastro do cliente do pedido, não o local exato da entrega.
*/

SELECT
    COALESCE(pr.nome_categoria, 'sem_categoria') AS categoria_produto,
    c.estado AS estado_cliente,
    COUNT(*) AS quantidade_itens,
    COUNT(DISTINCT i.id_pedido) AS pedidos_distintos,
    COUNT(DISTINCT i.id_vendedor) AS vendedores_distintos,
    SUM(i.preco_item) AS valor_itens,
    SUM(i.valor_frete) AS valor_frete,
    SUM(i.preco_item + i.valor_frete) AS valor_bruto,
    ROUND(
        100.0 * SUM(i.preco_item) / SUM(SUM(i.preco_item)) OVER (),
        4
    ) AS participacao_valor_itens_percentual
FROM core.item_pedido AS i
INNER JOIN core.pedido AS p USING (id_pedido)
INNER JOIN core.cliente AS c USING (id_cliente)
INNER JOIN core.produto AS pr USING (id_produto)
WHERE p.status_pedido = 'delivered'
GROUP BY COALESCE(pr.nome_categoria, 'sem_categoria'), c.estado
ORDER BY valor_itens DESC, categoria_produto, estado_cliente;
