BEGIN;

DO $validation$
DECLARE
    actual integer;
BEGIN
    IF current_setting('server_version_num')::integer / 10000 <> 18 THEN
        RAISE EXCEPTION 'PostgreSQL 18 esperado; versão encontrada: %',
            current_setting('server_version');
    END IF;

    SELECT count(*) INTO actual
    FROM information_schema.schemata
    WHERE schema_name IN ('raw', 'core', 'analytics');
    IF actual <> 3 THEN
        RAISE EXCEPTION 'Esperados 3 schemas; encontrados: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM information_schema.tables
    WHERE table_schema = 'raw' AND table_type = 'BASE TABLE';
    IF actual <> 9 THEN
        RAISE EXCEPTION 'Esperadas 9 tabelas RAW; encontradas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM information_schema.tables
    WHERE table_schema = 'core' AND table_type = 'BASE TABLE';
    IF actual <> 9 THEN
        RAISE EXCEPTION 'Esperadas 9 tabelas CORE; encontradas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM information_schema.tables
    WHERE table_schema = 'analytics' AND table_type = 'BASE TABLE';
    IF actual <> 0 THEN
        RAISE EXCEPTION 'ANALYTICS deveria estar vazio; tabelas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM information_schema.columns
    WHERE table_schema = 'raw';
    IF actual <> 79 THEN
        RAISE EXCEPTION 'Esperadas 79 colunas RAW; encontradas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM information_schema.columns
    WHERE table_schema = 'core';
    IF actual <> 50 THEN
        RAISE EXCEPTION 'Esperadas 50 colunas CORE; encontradas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM information_schema.columns
    WHERE table_schema = 'raw'
      AND column_name NOT LIKE '\_%' ESCAPE '\'
      AND data_type <> 'text';
    IF actual <> 0 THEN
        RAISE EXCEPTION 'Colunas de origem RAW não textuais: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM information_schema.columns
    WHERE table_schema IN ('raw', 'core') AND is_identity = 'YES';
    IF actual <> 10 THEN
        RAISE EXCEPTION 'Esperadas 10 identities; encontradas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM pg_constraint c
    JOIN pg_namespace n ON n.oid = c.connamespace
    WHERE n.nspname IN ('raw', 'core') AND c.contype = 'p';
    IF actual <> 18 THEN
        RAISE EXCEPTION 'Esperadas 18 PKs; encontradas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM pg_constraint c
    JOIN pg_namespace n ON n.oid = c.connamespace
    WHERE n.nspname = 'core' AND c.contype = 'f';
    IF actual <> 9 THEN
        RAISE EXCEPTION 'Esperadas 9 FKs CORE; encontradas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM pg_constraint c
    JOIN pg_namespace n ON n.oid = c.connamespace
    WHERE n.nspname = 'core'
      AND c.contype = 'f'
      AND c.confdeltype = 'r'
      AND c.confupdtype = 'a';
    IF actual <> 9 THEN
        RAISE EXCEPTION 'Política referencial divergente em alguma FK';
    END IF;

    SELECT count(*) INTO actual
    FROM pg_constraint c
    JOIN pg_namespace n ON n.oid = c.connamespace
    WHERE n.nspname = 'core' AND c.contype = 'u';
    IF actual <> 1 THEN
        RAISE EXCEPTION 'Esperada 1 UNIQUE CORE; encontradas: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM pg_indexes
    WHERE schemaname = 'raw';
    IF actual <> 9 THEN
        RAISE EXCEPTION 'Esperados 9 índices RAW implícitos; encontrados: %',
            actual;
    END IF;

    SELECT count(*) INTO actual
    FROM pg_indexes
    WHERE schemaname = 'core';
    IF actual <> 16 THEN
        RAISE EXCEPTION 'Esperados 16 índices CORE; encontrados: %', actual;
    END IF;

    SELECT count(*) INTO actual
    FROM pg_indexes
    WHERE schemaname = 'core' AND indexname LIKE 'idx_%';
    IF actual <> 6 THEN
        RAISE EXCEPTION 'Esperados 6 índices adicionais; encontrados: %',
            actual;
    END IF;
END
$validation$;

DO $behavior$
BEGIN
    INSERT INTO raw.olist_customers (
        customer_id,
        customer_zip_code_prefix,
        customer_state
    ) VALUES ('valor-invalido', 'x', '??');

    BEGIN
        INSERT INTO core.prefixo_cep (prefixo_cep) VALUES ('x');
        RAISE EXCEPTION 'CORE aceitou prefixo de CEP inválido';
    EXCEPTION
        WHEN check_violation THEN NULL;
    END;

    INSERT INTO core.prefixo_cep (prefixo_cep) VALUES ('00000');
    BEGIN
        INSERT INTO core.prefixo_cep (prefixo_cep) VALUES ('00000');
        RAISE EXCEPTION 'CORE aceitou chave primária duplicada';
    EXCEPTION
        WHEN unique_violation THEN NULL;
    END;

    BEGIN
        INSERT INTO core.cliente (
            id_cliente,
            id_cliente_unico,
            prefixo_cep,
            cidade,
            estado
        ) VALUES (
            '00000000000000000000000000000000',
            '11111111111111111111111111111111',
            '99999',
            'cidade',
            'SP'
        );
        RAISE EXCEPTION 'CORE aceitou referência órfã';
    EXCEPTION
        WHEN foreign_key_violation THEN NULL;
    END;
END
$behavior$;

ROLLBACK;

SELECT 'VALIDAÇÃO DA ARQUITETURA FÍSICA: APROVADA' AS resultado;
