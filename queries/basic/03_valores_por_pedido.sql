/*
Objetivo: formar a base financeira de itens sem duplicar valores.
Pergunta: qual é o valor de itens, frete e valor bruto de cada pedido?
Entrada: core.item_pedido, uma linha por item.
Saída: uma linha por id_pedido.
Data de referência: não incluída; combinar com core.pedido após esta agregação.
Filtros: pedidos que possuem itens.
Limitação: valor bruto não representa receita, margem ou lucro.
*/

SELECT
    id_pedido,
    COUNT(*) AS quantidade_itens,
    COUNT(DISTINCT id_vendedor) AS quantidade_vendedores,
    SUM(preco_item) AS valor_itens,
    SUM(valor_frete) AS valor_frete,
    SUM(preco_item + valor_frete) AS valor_bruto
FROM core.item_pedido
GROUP BY id_pedido
ORDER BY id_pedido;
