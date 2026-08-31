/*
Pergunta: quanto cada vendedor contribui e qual é a concentração financeira?
Saída: uma linha por vendedor ativo em pedidos entregues.
HHI mede concentração na base observada, não participação de mercado.
*/
WITH base AS (
    SELECT i.id_vendedor, COUNT(*) AS itens,
        COUNT(DISTINCT i.id_pedido) AS pedidos,
        SUM(i.preco_item) AS valor_itens
    FROM core.item_pedido i
    INNER JOIN core.pedido p USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
    GROUP BY i.id_vendedor
), participacao AS (
    SELECT *, valor_itens / SUM(valor_itens) OVER () AS participacao,
        SUM(valor_itens) OVER (ORDER BY valor_itens DESC, id_vendedor) /
            SUM(valor_itens) OVER () AS participacao_acumulada,
        ROW_NUMBER() OVER (ORDER BY valor_itens DESC, id_vendedor) AS posicao
    FROM base
)
SELECT id_vendedor, posicao, itens, pedidos, valor_itens,
    ROUND(100.0 * participacao, 4) AS participacao_percentual,
    ROUND(100.0 * participacao_acumulada, 4) AS acumulado_percentual,
    CASE WHEN participacao_acumulada <= 0.80 THEN 'A'
        WHEN participacao_acumulada <= 0.95 THEN 'B' ELSE 'C' END AS classe_abc,
    ROUND(SUM(POWER(participacao, 2)) OVER (), 6) AS hhi_base_observada
FROM participacao ORDER BY posicao;
