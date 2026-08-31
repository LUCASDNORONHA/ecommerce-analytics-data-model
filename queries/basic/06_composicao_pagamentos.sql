/*
Objetivo: descrever formas, valores e condições de pagamento.
Pergunta: como os registros de pagamento se distribuem por tipo e parcelas?
Entradas: core.pagamento e core.pedido.
Saída: uma linha por mês, tipo_pagamento e numero_parcelas.
Data de referência: core.pedido.data_compra.
Filtros: pedidos entregues.
Limitação: um pedido pode aparecer em mais de um grupo se possuir múltiplas
sequências, tipos ou condições. Participações financeiras usam registros de
pagamento, não pedidos exclusivos entre grupos.
*/

SELECT
    DATE_TRUNC('month', p.data_compra)::date AS mes_compra,
    pg.tipo_pagamento,
    pg.numero_parcelas,
    COUNT(*) AS registros_pagamento,
    COUNT(DISTINCT pg.id_pedido) AS pedidos_distintos,
    SUM(pg.valor_pagamento) AS valor_pago_registrado,
    ROUND(AVG(pg.valor_pagamento), 2) AS valor_medio_registro_pagamento
FROM core.pagamento AS pg
INNER JOIN core.pedido AS p USING (id_pedido)
WHERE p.status_pedido = 'delivered'
GROUP BY
    DATE_TRUNC('month', p.data_compra)::date,
    pg.tipo_pagamento,
    pg.numero_parcelas
ORDER BY mes_compra, pg.tipo_pagamento, pg.numero_parcelas;
