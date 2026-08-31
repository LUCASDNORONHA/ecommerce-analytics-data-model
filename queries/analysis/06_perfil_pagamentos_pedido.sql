/*
Pergunta: como forma, parcelamento e valor se combinam em pedidos entregues?
Saída: uma linha por perfil agregado de pedido; múltiplas sequências são
consolidadas antes da classificação.
*/
WITH pagamentos AS (
    SELECT id_pedido, SUM(valor_pagamento) AS valor_pago,
        MAX(numero_parcelas) AS max_parcelas,
        COUNT(*) AS registros_pagamento,
        COUNT(DISTINCT tipo_pagamento) AS tipos_distintos,
        STRING_AGG(DISTINCT tipo_pagamento, ', ' ORDER BY tipo_pagamento)
            AS composicao_pagamento
    FROM core.pagamento GROUP BY id_pedido
), perfil AS (
    SELECT pg.*,
        CASE WHEN valor_pago < 100 THEN 'ate_99_99'
            WHEN valor_pago < 250 THEN '100_a_249_99'
            WHEN valor_pago < 500 THEN '250_a_499_99'
            ELSE '500_ou_mais' END AS faixa_valor
    FROM pagamentos pg
    INNER JOIN core.pedido p USING (id_pedido)
    WHERE p.status_pedido = 'delivered'
)
SELECT faixa_valor, composicao_pagamento,
    CASE WHEN max_parcelas <= 1 THEN 'avista_ou_sem_parcelamento'
        WHEN max_parcelas <= 3 THEN '2_a_3_parcelas'
        WHEN max_parcelas <= 6 THEN '4_a_6_parcelas'
        ELSE '7_ou_mais_parcelas' END AS faixa_parcelamento,
    COUNT(*) AS pedidos, SUM(valor_pago) AS valor_pago,
    ROUND(AVG(valor_pago), 2) AS valor_medio_pedido,
    COUNT(*) FILTER (WHERE registros_pagamento > 1) AS pedidos_multiplos_registros,
    COUNT(*) FILTER (WHERE tipos_distintos > 1) AS pedidos_multiplos_tipos
FROM perfil GROUP BY faixa_valor, composicao_pagamento, faixa_parcelamento
ORDER BY faixa_valor, valor_pago DESC;
