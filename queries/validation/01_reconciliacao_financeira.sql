/*
Controle: reconciliar valor bruto dos itens e valor pago registrado.
Granularidade: uma linha por classificação da diferença, após agregação por
pedido.
Base: todos os pedidos que possuem simultaneamente itens e pagamentos.
Interpretação: diferenças não provam erro, estorno ou perda. Elas identificam
pedidos que exigem investigação. A tolerância de R$ 0,01 absorve somente
diferenças de centavos.
*/

WITH itens_por_pedido AS (
    SELECT
        id_pedido,
        SUM(preco_item + valor_frete) AS valor_bruto
    FROM core.item_pedido
    GROUP BY id_pedido
),
pagamentos_por_pedido AS (
    SELECT
        id_pedido,
        SUM(valor_pagamento) AS valor_pago_registrado
    FROM core.pagamento
    GROUP BY id_pedido
),
reconciliacao AS (
    SELECT
        p.id_pedido,
        p.status_pedido,
        i.valor_bruto,
        pg.valor_pago_registrado,
        pg.valor_pago_registrado - i.valor_bruto AS diferenca
    FROM core.pedido AS p
    INNER JOIN itens_por_pedido AS i USING (id_pedido)
    INNER JOIN pagamentos_por_pedido AS pg USING (id_pedido)
)
SELECT
    status_pedido,
    CASE
        WHEN ABS(diferenca) <= 0.01 THEN 'conciliado'
        WHEN diferenca > 0.01 THEN 'pagamento_maior'
        ELSE 'valor_bruto_maior'
    END AS classificacao_reconciliacao,
    COUNT(*) AS quantidade_pedidos,
    SUM(valor_bruto) AS valor_bruto,
    SUM(valor_pago_registrado) AS valor_pago_registrado,
    SUM(diferenca) AS diferenca_total,
    MAX(ABS(diferenca)) AS maior_diferenca_absoluta
FROM reconciliacao
GROUP BY status_pedido, classificacao_reconciliacao
ORDER BY status_pedido, classificacao_reconciliacao;
