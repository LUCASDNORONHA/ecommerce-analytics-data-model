/*
Objetivo: dimensionar pedidos que envolvem mais de um vendedor.
Pergunta: qual parcela dos pedidos e valores envolve múltiplos vendedores?
Entradas: core.item_pedido e core.pedido.
Saída: uma linha por classificação de quantidade de vendedores.
Data de referência: core.pedido.data_compra, agregada no histórico completo.
Filtros: pedidos entregues com itens.
Limitação: a consulta descreve composição e não atribui pagamentos ou avaliações
a vendedores individuais.
*/

WITH pedidos AS (
    SELECT
        i.id_pedido,
        COUNT(DISTINCT i.id_vendedor) AS quantidade_vendedores,
        COUNT(*) AS quantidade_itens,
        SUM(i.preco_item) AS valor_itens,
        SUM(i.valor_frete) AS valor_frete
    FROM core.item_pedido AS i
    INNER JOIN core.pedido AS p USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
    GROUP BY i.id_pedido
)
SELECT
    CASE
        WHEN quantidade_vendedores = 1 THEN 'um_vendedor'
        ELSE 'multiplos_vendedores'
    END AS classificacao_pedido,
    COUNT(*) AS quantidade_pedidos,
    SUM(quantidade_itens) AS quantidade_itens,
    SUM(valor_itens) AS valor_itens,
    SUM(valor_frete) AS valor_frete,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 4)
        AS percentual_pedidos
FROM pedidos
GROUP BY classificacao_pedido
ORDER BY classificacao_pedido;
