"""Validação independente de reconciliação e qualidade do ELT."""

from __future__ import annotations

import json
import logging
import os
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import psycopg
from dotenv import load_dotenv
from psycopg import sql

from etl.raw_loader import find_repository_root

LOGGER = logging.getLogger("validation.elt")

ROOT = find_repository_root(Path.cwd())
DEFAULT_OUTPUT_DIR = ROOT / "outputs" / "data-loading" / "validation"


RECONCILIATION_RULES = (
    {
        "rule": "reconciliation.cliente",
        "expected_sql": "SELECT count(*)::bigint FROM raw.olist_customers",
        "actual_sql": "SELECT count(*)::bigint FROM core.cliente",
    },
    {
        "rule": "reconciliation.produto",
        "expected_sql": "SELECT count(*)::bigint FROM raw.olist_products",
        "actual_sql": "SELECT count(*)::bigint FROM core.produto",
    },
    {
        "rule": "reconciliation.vendedor",
        "expected_sql": "SELECT count(*)::bigint FROM raw.olist_sellers",
        "actual_sql": "SELECT count(*)::bigint FROM core.vendedor",
    },
    {
        "rule": "reconciliation.pedido",
        "expected_sql": "SELECT count(*)::bigint FROM raw.olist_orders",
        "actual_sql": "SELECT count(*)::bigint FROM core.pedido",
    },
    {
        "rule": "reconciliation.item_pedido",
        "expected_sql": "SELECT count(*)::bigint FROM raw.olist_order_items",
        "actual_sql": "SELECT count(*)::bigint FROM core.item_pedido",
    },
    {
        "rule": "reconciliation.pagamento",
        "expected_sql": "SELECT count(*)::bigint FROM raw.olist_order_payments",
        "actual_sql": "SELECT count(*)::bigint FROM core.pagamento",
    },
    {
        "rule": "reconciliation.avaliacao",
        "expected_sql": "SELECT count(*)::bigint FROM raw.olist_order_reviews",
        "actual_sql": "SELECT count(*)::bigint FROM core.avaliacao",
    },
    {
        "rule": "reconciliation.prefixo_cep",
        "expected_sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT customer_zip_code_prefix AS prefixo
                FROM raw.olist_customers
                WHERE customer_zip_code_prefix IS NOT NULL

                UNION

                SELECT seller_zip_code_prefix
                FROM raw.olist_sellers
                WHERE seller_zip_code_prefix IS NOT NULL

                UNION

                SELECT geolocation_zip_code_prefix
                FROM raw.olist_geolocation
                WHERE geolocation_zip_code_prefix IS NOT NULL
            ) AS prefixos
        """,
        "actual_sql": "SELECT count(*)::bigint FROM core.prefixo_cep",
    },
    {
        "rule": "reconciliation.geolocalizacao",
        "expected_sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT DISTINCT
                    geolocation_zip_code_prefix,
                    geolocation_lat,
                    geolocation_lng,
                    geolocation_city,
                    geolocation_state
                FROM raw.olist_geolocation
            ) AS geolocalizacoes
        """,
        "actual_sql": "SELECT count(*)::bigint FROM core.geolocalizacao",
    },
)

INTEGRITY_RULES = (
    # Chaves primárias simples
    {
        "rule": "integrity.pk_prefixo_cep",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT prefixo_cep
                FROM core.prefixo_cep
                GROUP BY prefixo_cep
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    {
        "rule": "integrity.pk_cliente",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_cliente
                FROM core.cliente
                GROUP BY id_cliente
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    {
        "rule": "integrity.pk_produto",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_produto
                FROM core.produto
                GROUP BY id_produto
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    {
        "rule": "integrity.pk_vendedor",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_vendedor
                FROM core.vendedor
                GROUP BY id_vendedor
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    {
        "rule": "integrity.pk_pedido",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_pedido
                FROM core.pedido
                GROUP BY id_pedido
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    # Chaves primárias compostas
    {
        "rule": "integrity.pk_item_pedido",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_pedido, id_item
                FROM core.item_pedido
                GROUP BY id_pedido, id_item
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    {
        "rule": "integrity.pk_pagamento",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_pedido, sequencial_pagamento
                FROM core.pagamento
                GROUP BY id_pedido, sequencial_pagamento
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    {
        "rule": "integrity.pk_avaliacao",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_avaliacao, id_pedido
                FROM core.avaliacao
                GROUP BY id_avaliacao, id_pedido
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    {
        "rule": "integrity.pk_geolocalizacao",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_geolocalizacao
                FROM core.geolocalizacao
                GROUP BY id_geolocalizacao
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    # UNIQUE
    {
        "rule": "integrity.uq_pedido_id_cliente",
        "sql": """
            SELECT count(*)::bigint
            FROM (
                SELECT id_cliente
                FROM core.pedido
                GROUP BY id_cliente
                HAVING count(*) > 1
            ) AS duplicados
        """,
    },
    # Chaves estrangeiras
    {
        "rule": "integrity.fk_cliente_prefixo_cep",
        "sql": """
            SELECT count(*)::bigint
            FROM core.cliente AS c
            LEFT JOIN core.prefixo_cep AS p
                ON p.prefixo_cep = c.prefixo_cep
            WHERE p.prefixo_cep IS NULL
        """,
    },
    {
        "rule": "integrity.fk_vendedor_prefixo_cep",
        "sql": """
            SELECT count(*)::bigint
            FROM core.vendedor AS v
            LEFT JOIN core.prefixo_cep AS p
                ON p.prefixo_cep = v.prefixo_cep
            WHERE p.prefixo_cep IS NULL
        """,
    },
    {
        "rule": "integrity.fk_pedido_cliente",
        "sql": """
            SELECT count(*)::bigint
            FROM core.pedido AS p
            LEFT JOIN core.cliente AS c
                ON c.id_cliente = p.id_cliente
            WHERE c.id_cliente IS NULL
        """,
    },
    {
        "rule": "integrity.fk_item_pedido_pedido",
        "sql": """
            SELECT count(*)::bigint
            FROM core.item_pedido AS i
            LEFT JOIN core.pedido AS p
                ON p.id_pedido = i.id_pedido
            WHERE p.id_pedido IS NULL
        """,
    },
    {
        "rule": "integrity.fk_item_pedido_produto",
        "sql": """
            SELECT count(*)::bigint
            FROM core.item_pedido AS i
            LEFT JOIN core.produto AS p
                ON p.id_produto = i.id_produto
            WHERE p.id_produto IS NULL
        """,
    },
    {
        "rule": "integrity.fk_item_pedido_vendedor",
        "sql": """
            SELECT count(*)::bigint
            FROM core.item_pedido AS i
            LEFT JOIN core.vendedor AS v
                ON v.id_vendedor = i.id_vendedor
            WHERE v.id_vendedor IS NULL
        """,
    },
    {
        "rule": "integrity.fk_pagamento_pedido",
        "sql": """
            SELECT count(*)::bigint
            FROM core.pagamento AS pg
            LEFT JOIN core.pedido AS p
                ON p.id_pedido = pg.id_pedido
            WHERE p.id_pedido IS NULL
        """,
    },
    {
        "rule": "integrity.fk_avaliacao_pedido",
        "sql": """
            SELECT count(*)::bigint
            FROM core.avaliacao AS a
            LEFT JOIN core.pedido AS p
                ON p.id_pedido = a.id_pedido
            WHERE p.id_pedido IS NULL
        """,
    },
    {
        "rule": "integrity.fk_geolocalizacao_prefixo_cep",
        "sql": """
            SELECT count(*)::bigint
            FROM core.geolocalizacao AS g
            LEFT JOIN core.prefixo_cep AS p
                ON p.prefixo_cep = g.prefixo_cep
            WHERE p.prefixo_cep IS NULL
        """,
    },
)

QUALITY_RULES = (
    {
        "rule": "quality.identificadores_formato",
        "sql": """
            SELECT (
                (SELECT count(*) FROM core.cliente
                 WHERE id_cliente !~ '^[0-9a-f]{32}$'
                    OR id_cliente_unico !~ '^[0-9a-f]{32}$')
                +
                (SELECT count(*) FROM core.produto
                 WHERE id_produto !~ '^[0-9a-f]{32}$')
                +
                (SELECT count(*) FROM core.vendedor
                 WHERE id_vendedor !~ '^[0-9a-f]{32}$')
                +
                (SELECT count(*) FROM core.pedido
                 WHERE id_pedido !~ '^[0-9a-f]{32}$'
                    OR id_cliente !~ '^[0-9a-f]{32}$')
                +
                (SELECT count(*) FROM core.item_pedido
                 WHERE id_pedido !~ '^[0-9a-f]{32}$'
                    OR id_produto !~ '^[0-9a-f]{32}$'
                    OR id_vendedor !~ '^[0-9a-f]{32}$')
                +
                (SELECT count(*) FROM core.pagamento
                 WHERE id_pedido !~ '^[0-9a-f]{32}$')
                +
                (SELECT count(*) FROM core.avaliacao
                 WHERE id_avaliacao !~ '^[0-9a-f]{32}$'
                    OR id_pedido !~ '^[0-9a-f]{32}$')
            )::bigint
        """,
    },
    {
        "rule": "quality.prefixo_cep_formato",
        "sql": """
            SELECT (
                (SELECT count(*) FROM core.prefixo_cep
                 WHERE prefixo_cep !~ '^[0-9]{5}$')
                +
                (SELECT count(*) FROM core.cliente
                 WHERE prefixo_cep !~ '^[0-9]{5}$')
                +
                (SELECT count(*) FROM core.vendedor
                 WHERE prefixo_cep !~ '^[0-9]{5}$')
                +
                (SELECT count(*) FROM core.geolocalizacao
                 WHERE prefixo_cep !~ '^[0-9]{5}$')
            )::bigint
        """,
    },
    {
        "rule": "quality.uf_dominio",
        "sql": """
            SELECT (
                (SELECT count(*) FROM core.cliente
                 WHERE estado NOT IN (
                    'AC','AL','AM','AP','BA','CE','DF','ES','GO',
                    'MA','MG','MS','MT','PA','PB','PE','PI','PR',
                    'RJ','RN','RO','RR','RS','SC','SE','SP','TO'
                 ))
                +
                (SELECT count(*) FROM core.vendedor
                 WHERE estado NOT IN (
                    'AC','AL','AM','AP','BA','CE','DF','ES','GO',
                    'MA','MG','MS','MT','PA','PB','PE','PI','PR',
                    'RJ','RN','RO','RR','RS','SC','SE','SP','TO'
                 ))
                +
                (SELECT count(*) FROM core.geolocalizacao
                 WHERE estado NOT IN (
                    'AC','AL','AM','AP','BA','CE','DF','ES','GO',
                    'MA','MG','MS','MT','PA','PB','PE','PI','PR',
                    'RJ','RN','RO','RR','RS','SC','SE','SP','TO'
                 ))
            )::bigint
        """,
    },
    {
        "rule": "quality.status_pedido_dominio",
        "sql": """
            SELECT count(*)::bigint
            FROM core.pedido
            WHERE status_pedido NOT IN (
                'approved',
                'canceled',
                'created',
                'delivered',
                'invoiced',
                'processing',
                'shipped',
                'unavailable'
            )
        """,
    },
    {
        "rule": "quality.tipo_pagamento_dominio",
        "sql": """
            SELECT count(*)::bigint
            FROM core.pagamento
            WHERE tipo_pagamento NOT IN (
                'boleto',
                'credit_card',
                'debit_card',
                'not_defined',
                'voucher'
            )
        """,
    },
    {
        "rule": "quality.nota_avaliacao_dominio",
        "sql": """
            SELECT count(*)::bigint
            FROM core.avaliacao
            WHERE nota_avaliacao NOT BETWEEN 1 AND 5
        """,
    },
    {
        "rule": "quality.valores_monetarios_nao_negativos",
        "sql": """
            SELECT (
                (SELECT count(*) FROM core.item_pedido
                 WHERE preco_item < 0 OR valor_frete < 0)
                +
                (SELECT count(*) FROM core.pagamento
                 WHERE valor_pagamento < 0)
            )::bigint
        """,
    },
    {
        "rule": "quality.sequenciais_validos",
        "sql": """
            SELECT (
                (SELECT count(*) FROM core.item_pedido
                 WHERE id_item <= 0)
                +
                (SELECT count(*) FROM core.pagamento
                 WHERE sequencial_pagamento <= 0
                    OR numero_parcelas < 0)
            )::bigint
        """,
    },
    {
        "rule": "quality.dimensoes_produto_nao_negativas",
        "sql": """
            SELECT count(*)::bigint
            FROM core.produto
            WHERE comprimento_nome < 0
               OR comprimento_descricao < 0
               OR quantidade_fotos < 0
               OR peso_g < 0
               OR comprimento_cm < 0
               OR altura_cm < 0
               OR largura_cm < 0
        """,
    },
    {
        "rule": "quality.coordenadas_geograficas",
        "sql": """
            SELECT count(*)::bigint
            FROM core.geolocalizacao
            WHERE latitude NOT BETWEEN -90 AND 90
               OR longitude NOT BETWEEN -180 AND 180
        """,
    },
    {
        "rule": "quality.textos_obrigatorios_nao_vazios",
        "sql": """
            SELECT (
                (SELECT count(*) FROM core.cliente
                 WHERE btrim(cidade) = '')
                +
                (SELECT count(*) FROM core.vendedor
                 WHERE btrim(cidade) = '')
                +
                (SELECT count(*) FROM core.geolocalizacao
                 WHERE btrim(cidade) = '')
            )::bigint
        """,
    },
)

TRANSFORMATION_RULES = (
    {
        "rule": "transformation.prefixo_cep",
        "sql": """
            WITH esperado AS (
                SELECT customer_zip_code_prefix::character(5) AS prefixo_cep
                FROM raw.olist_customers
                WHERE customer_zip_code_prefix IS NOT NULL

                UNION

                SELECT seller_zip_code_prefix::character(5)
                FROM raw.olist_sellers
                WHERE seller_zip_code_prefix IS NOT NULL

                UNION

                SELECT geolocation_zip_code_prefix::character(5)
                FROM raw.olist_geolocation
                WHERE geolocation_zip_code_prefix IS NOT NULL
            ),
            diferencas AS (
                (
                    SELECT prefixo_cep FROM esperado
                    EXCEPT
                    SELECT prefixo_cep FROM core.prefixo_cep
                )
                UNION ALL
                (
                    SELECT prefixo_cep FROM core.prefixo_cep
                    EXCEPT
                    SELECT prefixo_cep FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
    {
        "rule": "transformation.cliente",
        "sql": """
            WITH esperado AS (
                SELECT
                    customer_id::varchar(32) AS id_cliente,
                    customer_unique_id::varchar(32) AS id_cliente_unico,
                    customer_zip_code_prefix::character(5) AS prefixo_cep,
                    customer_city::varchar(50) AS cidade,
                    customer_state::character(2) AS estado
                FROM raw.olist_customers
            ),
            diferencas AS (
                (
                    SELECT * FROM esperado
                    EXCEPT
                    SELECT
                        id_cliente,
                        id_cliente_unico,
                        prefixo_cep,
                        cidade,
                        estado
                    FROM core.cliente
                )
                UNION ALL
                (
                    SELECT
                        id_cliente,
                        id_cliente_unico,
                        prefixo_cep,
                        cidade,
                        estado
                    FROM core.cliente
                    EXCEPT
                    SELECT * FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
    {
        "rule": "transformation.produto",
        "sql": """
            WITH esperado AS (
                SELECT
                    product_id::varchar(32) AS id_produto,
                    product_category_name::varchar(50) AS nome_categoria,
                    product_name_lenght::smallint AS comprimento_nome,
                    product_description_lenght::smallint
                        AS comprimento_descricao,
                    product_photos_qty::smallint AS quantidade_fotos,
                    product_weight_g::integer AS peso_g,
                    product_length_cm::smallint AS comprimento_cm,
                    product_height_cm::smallint AS altura_cm,
                    product_width_cm::smallint AS largura_cm
                FROM raw.olist_products
            ),
            diferencas AS (
                (
                    SELECT * FROM esperado
                    EXCEPT
                    SELECT
                        id_produto,
                        nome_categoria,
                        comprimento_nome,
                        comprimento_descricao,
                        quantidade_fotos,
                        peso_g,
                        comprimento_cm,
                        altura_cm,
                        largura_cm
                    FROM core.produto
                )
                UNION ALL
                (
                    SELECT
                        id_produto,
                        nome_categoria,
                        comprimento_nome,
                        comprimento_descricao,
                        quantidade_fotos,
                        peso_g,
                        comprimento_cm,
                        altura_cm,
                        largura_cm
                    FROM core.produto
                    EXCEPT
                    SELECT * FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
    {
        "rule": "transformation.vendedor",
        "sql": """
            WITH esperado AS (
                SELECT
                    seller_id::varchar(32) AS id_vendedor,
                    seller_zip_code_prefix::character(5) AS prefixo_cep,
                    seller_city::varchar(50) AS cidade,
                    seller_state::character(2) AS estado
                FROM raw.olist_sellers
            ),
            diferencas AS (
                (
                    SELECT * FROM esperado
                    EXCEPT
                    SELECT
                        id_vendedor,
                        prefixo_cep,
                        cidade,
                        estado
                    FROM core.vendedor
                )
                UNION ALL
                (
                    SELECT
                        id_vendedor,
                        prefixo_cep,
                        cidade,
                        estado
                    FROM core.vendedor
                    EXCEPT
                    SELECT * FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
    {
        "rule": "transformation.pedido",
        "sql": """
            WITH esperado AS (
                SELECT
                    order_id::varchar(32) AS id_pedido,
                    customer_id::varchar(32) AS id_cliente,
                    order_status::varchar(20) AS status_pedido,
                    order_purchase_timestamp::timestamp AS data_compra,
                    order_approved_at::timestamp AS data_aprovacao,
                    order_delivered_carrier_date::timestamp
                        AS data_envio_transportador,
                    order_delivered_customer_date::timestamp
                        AS data_entrega,
                    order_estimated_delivery_date::timestamp
                        AS data_estimada
                FROM raw.olist_orders
            ),
            diferencas AS (
                (
                    SELECT * FROM esperado
                    EXCEPT
                    SELECT
                        id_pedido,
                        id_cliente,
                        status_pedido,
                        data_compra,
                        data_aprovacao,
                        data_envio_transportador,
                        data_entrega,
                        data_estimada
                    FROM core.pedido
                )
                UNION ALL
                (
                    SELECT
                        id_pedido,
                        id_cliente,
                        status_pedido,
                        data_compra,
                        data_aprovacao,
                        data_envio_transportador,
                        data_entrega,
                        data_estimada
                    FROM core.pedido
                    EXCEPT
                    SELECT * FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
    {
        "rule": "transformation.item_pedido",
        "sql": """
            WITH esperado AS (
                SELECT
                    order_id::varchar(32) AS id_pedido,
                    order_item_id::smallint AS id_item,
                    product_id::varchar(32) AS id_produto,
                    seller_id::varchar(32) AS id_vendedor,
                    shipping_limit_date::timestamp AS data_limite_envio,
                    price::numeric(12, 2) AS preco_item,
                    freight_value::numeric(12, 2) AS valor_frete
                FROM raw.olist_order_items
            ),
            diferencas AS (
                (
                    SELECT * FROM esperado
                    EXCEPT
                    SELECT
                        id_pedido,
                        id_item,
                        id_produto,
                        id_vendedor,
                        data_limite_envio,
                        preco_item,
                        valor_frete
                    FROM core.item_pedido
                )
                UNION ALL
                (
                    SELECT
                        id_pedido,
                        id_item,
                        id_produto,
                        id_vendedor,
                        data_limite_envio,
                        preco_item,
                        valor_frete
                    FROM core.item_pedido
                    EXCEPT
                    SELECT * FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
    {
        "rule": "transformation.pagamento",
        "sql": """
            WITH esperado AS (
                SELECT
                    order_id::varchar(32) AS id_pedido,
                    payment_sequential::smallint AS sequencial_pagamento,
                    payment_type::varchar(20) AS tipo_pagamento,
                    payment_installments::smallint AS numero_parcelas,
                    payment_value::numeric(12, 2) AS valor_pagamento
                FROM raw.olist_order_payments
            ),
            diferencas AS (
                (
                    SELECT * FROM esperado
                    EXCEPT
                    SELECT
                        id_pedido,
                        sequencial_pagamento,
                        tipo_pagamento,
                        numero_parcelas,
                        valor_pagamento
                    FROM core.pagamento
                )
                UNION ALL
                (
                    SELECT
                        id_pedido,
                        sequencial_pagamento,
                        tipo_pagamento,
                        numero_parcelas,
                        valor_pagamento
                    FROM core.pagamento
                    EXCEPT
                    SELECT * FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
    {
        "rule": "transformation.avaliacao",
        "sql": """
            WITH esperado AS (
                SELECT
                    review_id::varchar(32) AS id_avaliacao,
                    order_id::varchar(32) AS id_pedido,
                    review_score::smallint AS nota_avaliacao,
                    review_creation_date::timestamp AS data_criacao,
                    review_answer_timestamp::timestamp AS data_resposta
                FROM raw.olist_order_reviews
            ),
            diferencas AS (
                (
                    SELECT * FROM esperado
                    EXCEPT
                    SELECT
                        id_avaliacao,
                        id_pedido,
                        nota_avaliacao,
                        data_criacao,
                        data_resposta
                    FROM core.avaliacao
                )
                UNION ALL
                (
                    SELECT
                        id_avaliacao,
                        id_pedido,
                        nota_avaliacao,
                        data_criacao,
                        data_resposta
                    FROM core.avaliacao
                    EXCEPT
                    SELECT * FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
    {
        "rule": "transformation.geolocalizacao",
        "sql": """
            WITH esperado AS (
                SELECT DISTINCT
                    geolocation_zip_code_prefix::character(5)
                        AS prefixo_cep,
                    geolocation_lat::double precision AS latitude,
                    geolocation_lng::double precision AS longitude,
                    geolocation_city::varchar(50) AS cidade,
                    geolocation_state::character(2) AS estado
                FROM raw.olist_geolocation
            ),
            atual AS (
                SELECT
                    prefixo_cep,
                    latitude,
                    longitude,
                    cidade,
                    estado
                FROM core.geolocalizacao
            ),
            diferencas AS (
                (
                    SELECT * FROM esperado
                    EXCEPT
                    SELECT * FROM atual
                )
                UNION ALL
                (
                    SELECT * FROM atual
                    EXCEPT
                    SELECT * FROM esperado
                )
            )
            SELECT count(*)::bigint
            FROM diferencas
        """,
    },
)


def run_transformation_quality(
    connection: psycopg.Connection,
) -> list[dict[str, object]]:
    """Valida a correspondência de conteúdo entre RAW e CORE."""
    results: list[dict[str, object]] = []

    with connection.cursor() as cursor:
        for rule in TRANSFORMATION_RULES:
            violations = _execute_scalar(cursor, rule["sql"])

            results.append(
                {
                    "rule": rule["rule"],
                    "category": "transformation",
                    "expected": 0,
                    "actual": violations,
                    "difference": violations,
                    "approved": violations == 0,
                }
            )

    return results


def run_not_null_quality(
    connection: psycopg.Connection,
) -> list[dict[str, object]]:
    """Valida todas as colunas NOT NULL declaradas no CORE."""
    results: list[dict[str, object]] = []

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT table_name, column_name
            FROM information_schema.columns
            WHERE table_schema = 'core'
              AND is_nullable = 'NO'
            ORDER BY table_name, ordinal_position
            """
        )

        columns = cursor.fetchall()

        for table_name, column_name in columns:
            query = sql.SQL(
                "SELECT count(*)::bigint FROM core.{} WHERE {} IS NULL"
            ).format(
                sql.Identifier(table_name),
                sql.Identifier(column_name),
            )

            cursor.execute(query)
            violations = int(cursor.fetchone()[0])

            results.append(
                {
                    "rule": (f"quality.not_null.{table_name}.{column_name}"),
                    "category": "quality",
                    "expected": 0,
                    "actual": violations,
                    "difference": violations,
                    "approved": violations == 0,
                }
            )

    return results


def run_quality(
    connection: psycopg.Connection,
) -> list[dict[str, object]]:
    """Valida domínios e regras de qualidade dos dados no CORE."""
    results: list[dict[str, object]] = []

    with connection.cursor() as cursor:
        for rule in QUALITY_RULES:
            violations = _execute_scalar(cursor, rule["sql"])

            results.append(
                {
                    "rule": rule["rule"],
                    "category": "quality",
                    "expected": 0,
                    "actual": violations,
                    "difference": violations,
                    "approved": violations == 0,
                }
            )

    return results


def run_integrity(
    connection: psycopg.Connection,
) -> list[dict[str, object]]:
    """Valida unicidade e integridade referencial no CORE."""
    results: list[dict[str, object]] = []

    with connection.cursor() as cursor:
        for rule in INTEGRITY_RULES:
            violations = _execute_scalar(cursor, rule["sql"])

            results.append(
                {
                    "rule": rule["rule"],
                    "category": "integrity",
                    "expected": 0,
                    "actual": violations,
                    "difference": violations,
                    "approved": violations == 0,
                }
            )

    return results


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _database_name(database_url: str) -> str:
    """Obtém somente o nome do banco, sem expor credenciais."""
    return urlparse(database_url).path.lstrip("/")


def _execute_scalar(cursor: psycopg.Cursor, query: str) -> int:
    """Executa uma consulta que retorna um único número."""
    cursor.execute(query)
    return int(cursor.fetchone()[0])


def run_reconciliation(
    connection: psycopg.Connection,
) -> list[dict[str, object]]:
    """Compara os volumes esperados da RAW com os volumes do CORE."""
    results: list[dict[str, object]] = []

    with connection.cursor() as cursor:
        for rule in RECONCILIATION_RULES:
            expected = _execute_scalar(cursor, rule["expected_sql"])
            actual = _execute_scalar(cursor, rule["actual_sql"])
            approved = expected == actual

            results.append(
                {
                    "rule": rule["rule"],
                    "category": "reconciliation",
                    "expected": expected,
                    "actual": actual,
                    "difference": actual - expected,
                    "approved": approved,
                }
            )

    return results


def build_summary(results: list[dict[str, object]]) -> dict[str, int]:
    """Resume o resultado das regras executadas."""
    approved = sum(bool(result["approved"]) for result in results)
    total = len(results)

    return {
        "total_rules": total,
        "approved": approved,
        "failed": total - approved,
    }


def write_report(
    output_dir: Path,
    payload: dict[str, object],
) -> Path:
    """Persiste o relatório da validação em JSON."""
    output_dir.mkdir(parents=True, exist_ok=True)

    path = output_dir / f"elt_validation_{payload['run_id']}.json"

    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return path


def run_validation(
    database_url: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, object]:
    """Executa a validação independente do banco já carregado."""
    run_id = str(uuid.uuid4())

    payload: dict[str, object] = {
        "run_id": run_id,
        "started_at": _utc_now(),
        "finished_at": None,
        "status": "running",
        "database": _database_name(database_url),
        "summary": {},
        "results": [],
    }

    try:
        with psycopg.connect(database_url) as connection:
            results = [
                *run_reconciliation(connection),
                *run_integrity(connection),
                *run_not_null_quality(connection),
                *run_quality(connection),
                *run_transformation_quality(connection),
            ]

        summary = build_summary(results)

        payload["results"] = results
        payload["summary"] = summary
        payload["status"] = "approved" if summary["failed"] == 0 else "failed"

    except Exception as exc:
        payload["status"] = "failed"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)

    finally:
        payload["finished_at"] = _utc_now()
        report_path = write_report(output_dir, payload)
        LOGGER.info("Relatório de validação: %s", report_path)

    return payload


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    load_dotenv()

    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        LOGGER.error("DATABASE_URL não configurada")
        return 1

    result = run_validation(database_url)

    summary = result.get("summary", {})

    if summary:
        LOGGER.info(
            "Validação do ELT: %s — %s de %s regras aprovadas",
            str(result["status"]).upper(),
            summary["approved"],
            summary["total_rules"],
        )
    else:
        LOGGER.info(
            "Validação do ELT: %s",
            str(result["status"]).upper(),
        )

    return 0 if result["status"] == "approved" else 1


if __name__ == "__main__":
    sys.exit(main())
