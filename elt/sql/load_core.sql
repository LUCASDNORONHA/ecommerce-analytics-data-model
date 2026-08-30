-- Transformação substitutiva da RAW para o CORE.
-- A transação, os timeouts e a reconciliação são controlados pelo Python.

TRUNCATE TABLE
    core.item_pedido,
    core.pagamento,
    core.avaliacao,
    core.pedido,
    core.cliente,
    core.produto,
    core.vendedor,
    core.geolocalizacao,
    core.prefixo_cep
RESTART IDENTITY;

INSERT INTO core.prefixo_cep (prefixo_cep)
SELECT customer_zip_code_prefix
FROM raw.olist_customers
WHERE customer_zip_code_prefix IS NOT NULL
UNION
SELECT seller_zip_code_prefix
FROM raw.olist_sellers
WHERE seller_zip_code_prefix IS NOT NULL
UNION
SELECT geolocation_zip_code_prefix
FROM raw.olist_geolocation
WHERE geolocation_zip_code_prefix IS NOT NULL;

INSERT INTO core.cliente (
    id_cliente,
    id_cliente_unico,
    prefixo_cep,
    cidade,
    estado
)
SELECT
    customer_id,
    customer_unique_id,
    customer_zip_code_prefix,
    customer_city,
    customer_state
FROM raw.olist_customers;

INSERT INTO core.produto (
    id_produto,
    nome_categoria,
    comprimento_nome,
    comprimento_descricao,
    quantidade_fotos,
    peso_g,
    comprimento_cm,
    altura_cm,
    largura_cm
)
SELECT
    product_id,
    product_category_name,
    product_name_lenght::smallint,
    product_description_lenght::smallint,
    product_photos_qty::smallint,
    product_weight_g::integer,
    product_length_cm::smallint,
    product_height_cm::smallint,
    product_width_cm::smallint
FROM raw.olist_products;

INSERT INTO core.vendedor (
    id_vendedor,
    prefixo_cep,
    cidade,
    estado
)
SELECT
    seller_id,
    seller_zip_code_prefix,
    seller_city,
    seller_state
FROM raw.olist_sellers;

INSERT INTO core.pedido (
    id_pedido,
    id_cliente,
    status_pedido,
    data_compra,
    data_aprovacao,
    data_envio_transportador,
    data_entrega,
    data_estimada
)
SELECT
    order_id,
    customer_id,
    order_status,
    order_purchase_timestamp::timestamp without time zone,
    order_approved_at::timestamp without time zone,
    order_delivered_carrier_date::timestamp without time zone,
    order_delivered_customer_date::timestamp without time zone,
    order_estimated_delivery_date::timestamp without time zone
FROM raw.olist_orders;

INSERT INTO core.geolocalizacao (
    prefixo_cep,
    latitude,
    longitude,
    cidade,
    estado
)
SELECT
    geolocation_zip_code_prefix,
    geolocation_lat::double precision,
    geolocation_lng::double precision,
    geolocation_city,
    geolocation_state
FROM (
    SELECT DISTINCT ON (
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state
    )
        _id_raw,
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state
    FROM raw.olist_geolocation
    ORDER BY
        geolocation_zip_code_prefix,
        geolocation_lat,
        geolocation_lng,
        geolocation_city,
        geolocation_state,
        _id_raw
) AS ocorrencias_unicas
ORDER BY _id_raw;

INSERT INTO core.item_pedido (
    id_pedido,
    id_item,
    id_produto,
    id_vendedor,
    data_limite_envio,
    preco_item,
    valor_frete
)
SELECT
    order_id,
    order_item_id::smallint,
    product_id,
    seller_id,
    shipping_limit_date::timestamp without time zone,
    price::numeric(12, 2),
    freight_value::numeric(12, 2)
FROM raw.olist_order_items;

INSERT INTO core.pagamento (
    id_pedido,
    sequencial_pagamento,
    tipo_pagamento,
    numero_parcelas,
    valor_pagamento
)
SELECT
    order_id,
    payment_sequential::smallint,
    payment_type,
    payment_installments::smallint,
    payment_value::numeric(12, 2)
FROM raw.olist_order_payments;

INSERT INTO core.avaliacao (
    id_avaliacao,
    id_pedido,
    nota_avaliacao,
    data_criacao,
    data_resposta
)
SELECT
    review_id,
    order_id,
    review_score::smallint,
    review_creation_date::timestamp without time zone,
    review_answer_timestamp::timestamp without time zone
FROM raw.olist_order_reviews;
