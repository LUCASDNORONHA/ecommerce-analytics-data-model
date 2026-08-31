/*
Controle: quantificar a multiplicação causada pelo join direto entre itens e
pagamentos.
Granularidade: uma única linha de controle.
Resultado esperado: linhas_join_direto pode superar itens e pagamentos. Os
valores do join direto não devem ser usados como métricas financeiras.
*/

WITH pedidos_com_ambas_relacoes AS (
    SELECT i.id_pedido
    FROM core.item_pedido AS i
    INNER JOIN core.pagamento AS pg USING (id_pedido)
    GROUP BY i.id_pedido
),
totais_origem AS (
    SELECT
        (
            SELECT COUNT(*)
            FROM core.item_pedido AS i
            INNER JOIN pedidos_com_ambas_relacoes AS c USING (id_pedido)
        ) AS linhas_itens,
        (
            SELECT COUNT(*)
            FROM core.pagamento AS pg
            INNER JOIN pedidos_com_ambas_relacoes AS c USING (id_pedido)
        ) AS linhas_pagamentos,
        (
            SELECT SUM(i.preco_item)
            FROM core.item_pedido AS i
            INNER JOIN pedidos_com_ambas_relacoes AS c USING (id_pedido)
        ) AS valor_itens_correto,
        (
            SELECT SUM(pg.valor_pagamento)
            FROM core.pagamento AS pg
            INNER JOIN pedidos_com_ambas_relacoes AS c USING (id_pedido)
        ) AS valor_pagamentos_correto
),
join_direto AS (
    SELECT
        COUNT(*) AS linhas_join_direto,
        SUM(i.preco_item) AS valor_itens_apos_join,
        SUM(pg.valor_pagamento) AS valor_pagamentos_apos_join
    FROM core.item_pedido AS i
    INNER JOIN core.pagamento AS pg USING (id_pedido)
)
SELECT
    o.linhas_itens,
    o.linhas_pagamentos,
    j.linhas_join_direto,
    o.valor_itens_correto,
    j.valor_itens_apos_join,
    j.valor_itens_apos_join - o.valor_itens_correto
        AS duplicacao_valor_itens,
    o.valor_pagamentos_correto,
    j.valor_pagamentos_apos_join,
    j.valor_pagamentos_apos_join - o.valor_pagamentos_correto
        AS duplicacao_valor_pagamentos
FROM totais_origem AS o
CROSS JOIN join_direto AS j;
