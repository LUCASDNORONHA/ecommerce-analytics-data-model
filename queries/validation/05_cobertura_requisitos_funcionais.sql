/*
Objetivo: produzir evidências reproduzíveis para requisitos funcionais que não
possuem uma consulta analítica dedicada.

Cada bloco retorna um resultado independente. As contagens comprovam
capacidade e cobertura do modelo; não transformam padrões do dataset em regras
de negócio.
*/

/* RF01 — integração das nove entidades do modelo. */
WITH cobertura AS (
    SELECT
        'pedido_cliente' AS relacao,
        COUNT(*) AS registros_origem,
        COUNT(*) FILTER (WHERE c.id_cliente IS NOT NULL) AS registros_relacionados
    FROM core.pedido AS p
    LEFT JOIN core.cliente AS c USING (id_cliente)

    UNION ALL

    SELECT
        'item_produto_vendedor',
        COUNT(*),
        COUNT(*) FILTER (
            WHERE pr.id_produto IS NOT NULL AND v.id_vendedor IS NOT NULL
        )
    FROM core.item_pedido AS i
    LEFT JOIN core.produto AS pr USING (id_produto)
    LEFT JOIN core.vendedor AS v USING (id_vendedor)

    UNION ALL

    SELECT
        'pedido_pagamento',
        COUNT(*),
        COUNT(*) FILTER (WHERE pg.id_pedido IS NOT NULL)
    FROM core.pedido AS p
    LEFT JOIN (
        SELECT DISTINCT id_pedido FROM core.pagamento
    ) AS pg USING (id_pedido)

    UNION ALL

    SELECT
        'pedido_avaliacao',
        COUNT(*),
        COUNT(*) FILTER (WHERE a.id_pedido IS NOT NULL)
    FROM core.pedido AS p
    LEFT JOIN (
        SELECT DISTINCT id_pedido FROM core.avaliacao
    ) AS a USING (id_pedido)

    UNION ALL

    SELECT
        'prefixo_geolocalizacao',
        COUNT(*),
        COUNT(*) FILTER (WHERE g.prefixo_cep IS NOT NULL)
    FROM core.prefixo_cep AS pc
    LEFT JOIN (
        SELECT DISTINCT prefixo_cep FROM core.geolocalizacao
    ) AS g USING (prefixo_cep)
)
SELECT
    relacao,
    registros_origem,
    registros_relacionados,
    registros_origem - registros_relacionados AS registros_sem_relacao,
    ROUND(100.0 * registros_relacionados / NULLIF(registros_origem, 0), 2)
        AS cobertura_percentual
FROM cobertura
ORDER BY relacao;

/* RF02 e RF04 — histórico de pedidos por identidade persistente de cliente. */
WITH historico_cliente AS (
    SELECT
        c.id_cliente_unico,
        COUNT(*) AS pedidos,
        MIN(p.data_compra) AS primeira_compra,
        MAX(p.data_compra) AS ultima_compra
    FROM core.cliente AS c
    INNER JOIN core.pedido AS p USING (id_cliente)
    GROUP BY c.id_cliente_unico
)
SELECT
    COUNT(*) AS clientes_observados,
    COUNT(*) FILTER (WHERE pedidos > 1) AS clientes_recorrentes,
    ROUND(100.0 * COUNT(*) FILTER (WHERE pedidos > 1) / COUNT(*), 2)
        AS clientes_recorrentes_percentual,
    MAX(pedidos) AS maximo_pedidos_cliente,
    MIN(primeira_compra) AS inicio_historico,
    MAX(ultima_compra) AS fim_historico
FROM historico_cliente;

/* RF07 e RF08 — cobertura de avaliação e marcos temporais dos pedidos. */
WITH avaliacao_pedido AS (
    SELECT DISTINCT id_pedido FROM core.avaliacao
)
SELECT
    COUNT(*) AS pedidos,
    COUNT(a.id_pedido) AS pedidos_com_avaliacao,
    COUNT(p.data_aprovacao) AS pedidos_com_aprovacao,
    COUNT(p.data_envio_transportador) AS pedidos_com_envio,
    COUNT(p.data_entrega) AS pedidos_com_entrega,
    COUNT(p.data_estimada) AS pedidos_com_estimativa,
    COUNT(*) FILTER (
        WHERE p.data_entrega IS NOT NULL
          AND p.data_estimada IS NOT NULL
          AND p.data_entrega > p.data_estimada
    ) AS pedidos_entregues_apos_estimativa
FROM core.pedido AS p
LEFT JOIN avaliacao_pedido AS a USING (id_pedido);

/* RF09 — cobertura geográfica de clientes e vendedores por prefixo de CEP. */
WITH prefixos_georreferenciados AS (
    SELECT DISTINCT prefixo_cep FROM core.geolocalizacao
), cobertura AS (
    SELECT
        'cliente' AS entidade,
        COUNT(*) AS registros,
        COUNT(g.prefixo_cep) AS registros_com_geolocalizacao,
        COUNT(DISTINCT c.estado) AS estados,
        COUNT(DISTINCT c.cidade) AS cidades
    FROM core.cliente AS c
    LEFT JOIN prefixos_georreferenciados AS g USING (prefixo_cep)

    UNION ALL

    SELECT
        'vendedor',
        COUNT(*),
        COUNT(g.prefixo_cep),
        COUNT(DISTINCT v.estado),
        COUNT(DISTINCT v.cidade)
    FROM core.vendedor AS v
    LEFT JOIN prefixos_georreferenciados AS g USING (prefixo_cep)
)
SELECT
    entidade,
    registros,
    registros_com_geolocalizacao,
    registros - registros_com_geolocalizacao AS registros_sem_geolocalizacao,
    ROUND(100.0 * registros_com_geolocalizacao / NULLIF(registros, 0), 2)
        AS cobertura_geolocalizacao_percentual,
    estados,
    cidades
FROM cobertura
ORDER BY entidade;
