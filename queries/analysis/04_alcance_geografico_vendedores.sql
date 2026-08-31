/*
Pergunta: qual é a origem, o alcance estadual e o valor dos vendedores?
Estado atendido representa o cadastro do cliente, não o local exato da entrega.
*/
SELECT i.id_vendedor, v.estado AS estado_vendedor,
    COUNT(DISTINCT c.estado) AS estados_clientes_atendidos,
    COUNT(DISTINCT c.cidade) AS cidades_clientes_atendidas,
    COUNT(DISTINCT i.id_pedido) AS pedidos,
    COUNT(*) AS itens, SUM(i.preco_item) AS valor_itens,
    SUM(i.valor_frete) AS valor_frete,
    ROUND(100.0 * SUM(i.valor_frete) /
        NULLIF(SUM(i.preco_item + i.valor_frete), 0), 2)
        AS percentual_frete
FROM core.item_pedido i
INNER JOIN core.pedido p USING (id_pedido)
INNER JOIN core.cliente c USING (id_cliente)
INNER JOIN core.vendedor v USING (id_vendedor)
WHERE p.status_pedido = 'delivered'
GROUP BY i.id_vendedor, v.estado
ORDER BY valor_itens DESC, i.id_vendedor;
