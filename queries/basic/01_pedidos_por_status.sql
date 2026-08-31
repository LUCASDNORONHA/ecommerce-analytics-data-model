/*
Objetivo: descrever a composição dos pedidos por status.
Pergunta: quantos pedidos existem em cada status e qual é sua participação?
Entrada: core.pedido, uma linha por pedido.
Saída: uma linha por status_pedido.
Data de referência: não aplicável ao total histórico.
Filtros: todos os pedidos.
Limitação: status não comprova liquidação ou estorno financeiro.
*/

SELECT
    status_pedido,
    COUNT(*) AS quantidade_pedidos,
    ROUND(
        100.0 * COUNT(*) / SUM(COUNT(*)) OVER (),
        2
    ) AS percentual_pedidos
FROM core.pedido
GROUP BY status_pedido
ORDER BY quantidade_pedidos DESC, status_pedido;
