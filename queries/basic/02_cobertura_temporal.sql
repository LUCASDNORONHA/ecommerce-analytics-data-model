/*
Objetivo: identificar a cobertura temporal e meses potencialmente incompletos.
Pergunta: qual período está disponível e quantos dias e pedidos há em cada mês?
Entrada: core.pedido, uma linha por pedido.
Saída: uma linha por mês de data_compra.
Data de referência: core.pedido.data_compra.
Filtros: todos os pedidos.
Limitação: poucos dias observados sinalizam mês parcial, mas não provam ausência
de dados sem comparação com o calendário e com a fonte.
*/

WITH cobertura_mensal AS (
    SELECT
        DATE_TRUNC('month', data_compra)::date AS mes_compra,
        MIN(data_compra)::date AS primeira_data_observada,
        MAX(data_compra)::date AS ultima_data_observada,
        COUNT(DISTINCT data_compra::date) AS dias_com_pedidos,
        COUNT(*) AS quantidade_pedidos,
        COUNT(*) FILTER (WHERE status_pedido = 'delivered')
            AS pedidos_entregues
    FROM core.pedido
    GROUP BY DATE_TRUNC('month', data_compra)::date
)
SELECT
    mes_compra,
    primeira_data_observada,
    ultima_data_observada,
    dias_com_pedidos,
    EXTRACT(
        DAY FROM (
            mes_compra + INTERVAL '1 month - 1 day'
        )
    )::integer AS dias_no_mes,
    quantidade_pedidos,
    pedidos_entregues,
    dias_com_pedidos < EXTRACT(
        DAY FROM (
            mes_compra + INTERVAL '1 month - 1 day'
        )
    )::integer AS nao_cobre_todos_dias_mes
FROM cobertura_mensal
ORDER BY mes_compra;
