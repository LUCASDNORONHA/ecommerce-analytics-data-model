/*
Controle: verificar a cobertura de itens e pagamentos em relação aos pedidos.
Granularidade: uma linha por status e classificação de cobertura.
Interpretação: ausências podem refletir a fonte e o status do pedido; não devem
ser descartadas nem classificadas como erro sem investigação.
*/

WITH cobertura AS (
    SELECT
        p.id_pedido,
        p.status_pedido,
        EXISTS (
            SELECT 1
            FROM core.item_pedido AS i
            WHERE i.id_pedido = p.id_pedido
        ) AS possui_item,
        EXISTS (
            SELECT 1
            FROM core.pagamento AS pg
            WHERE pg.id_pedido = p.id_pedido
        ) AS possui_pagamento
    FROM core.pedido AS p
)
SELECT
    status_pedido,
    CASE
        WHEN possui_item AND possui_pagamento THEN 'itens_e_pagamentos'
        WHEN possui_item THEN 'somente_itens'
        WHEN possui_pagamento THEN 'somente_pagamentos'
        ELSE 'sem_itens_e_sem_pagamentos'
    END AS classificacao_cobertura,
    COUNT(*) AS quantidade_pedidos
FROM cobertura
GROUP BY status_pedido, classificacao_cobertura
ORDER BY status_pedido, classificacao_cobertura;
