DO $$
DECLARE
    view_name text;
    expected_views text[] := ARRAY[
        'vw_pedido_financeiro',
        'vw_financeiro_mensal',
        'vw_vendedor_pedido',
        'vw_desempenho_vendedor'
    ];
BEGIN
    FOREACH view_name IN ARRAY expected_views LOOP
        IF to_regclass('analytics.' || view_name) IS NULL THEN
            RAISE EXCEPTION 'View analytics.% não encontrada', view_name;
        END IF;
    END LOOP;

    IF (
        SELECT COUNT(*)
        FROM information_schema.views
        WHERE table_schema = 'analytics'
          AND table_name = ANY(expected_views)
    ) <> CARDINALITY(expected_views) THEN
        RAISE EXCEPTION 'Conjunto de views do schema analytics está incompleto';
    END IF;
END
$$;
