BEGIN;

DROP SCHEMA IF EXISTS analytics;

DROP TABLE IF EXISTS core.geolocalizacao;
DROP TABLE IF EXISTS core.avaliacao;
DROP TABLE IF EXISTS core.pagamento;
DROP TABLE IF EXISTS core.item_pedido;
DROP TABLE IF EXISTS core.pedido;
DROP TABLE IF EXISTS core.vendedor;
DROP TABLE IF EXISTS core.produto;
DROP TABLE IF EXISTS core.cliente;
DROP TABLE IF EXISTS core.prefixo_cep;

DROP SCHEMA IF EXISTS core;

DROP TABLE IF EXISTS raw.product_category_name_translation;
DROP TABLE IF EXISTS raw.olist_sellers;
DROP TABLE IF EXISTS raw.olist_products;
DROP TABLE IF EXISTS raw.olist_orders;
DROP TABLE IF EXISTS raw.olist_order_reviews;
DROP TABLE IF EXISTS raw.olist_order_payments;
DROP TABLE IF EXISTS raw.olist_order_items;
DROP TABLE IF EXISTS raw.olist_geolocation;
DROP TABLE IF EXISTS raw.olist_customers;
DROP SCHEMA IF EXISTS raw;

COMMIT;
