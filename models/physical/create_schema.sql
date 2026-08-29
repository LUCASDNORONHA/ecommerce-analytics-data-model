BEGIN;

CREATE SCHEMA raw;
CREATE SCHEMA core;
CREATE SCHEMA analytics;

-- RAW: uma tabela por CSV, com valores da fonte preservados como texto.
CREATE TABLE raw.olist_customers (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'olist_customers_dataset.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    customer_id text, customer_unique_id text, customer_zip_code_prefix text,
    customer_city text, customer_state text
);
CREATE TABLE raw.olist_geolocation (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'olist_geolocation_dataset.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    geolocation_zip_code_prefix text, geolocation_lat text,
    geolocation_lng text, geolocation_city text, geolocation_state text
);
CREATE TABLE raw.olist_order_items (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'olist_order_items_dataset.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    order_id text, order_item_id text, product_id text, seller_id text,
    shipping_limit_date text, price text, freight_value text
);
CREATE TABLE raw.olist_order_payments (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'olist_order_payments_dataset.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    order_id text, payment_sequential text, payment_type text,
    payment_installments text, payment_value text
);
CREATE TABLE raw.olist_order_reviews (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'olist_order_reviews_dataset.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    review_id text, order_id text, review_score text, review_comment_title text,
    review_comment_message text, review_creation_date text,
    review_answer_timestamp text
);
CREATE TABLE raw.olist_orders (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'olist_orders_dataset.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    order_id text, customer_id text, order_status text,
    order_purchase_timestamp text, order_approved_at text,
    order_delivered_carrier_date text, order_delivered_customer_date text,
    order_estimated_delivery_date text
);
CREATE TABLE raw.olist_products (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'olist_products_dataset.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    product_id text, product_category_name text, product_name_lenght text,
    product_description_lenght text, product_photos_qty text,
    product_weight_g text, product_length_cm text, product_height_cm text,
    product_width_cm text
);
CREATE TABLE raw.olist_sellers (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'olist_sellers_dataset.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    seller_id text, seller_zip_code_prefix text, seller_city text,
    seller_state text
);
CREATE TABLE raw.product_category_name_translation (
    _id_raw bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    _arquivo_origem text NOT NULL DEFAULT 'product_category_name_translation.csv',
    _carregado_em timestamp with time zone NOT NULL DEFAULT CURRENT_TIMESTAMP,
    product_category_name text, product_category_name_english text
);

CREATE TABLE core.prefixo_cep (
    prefixo_cep character(5) NOT NULL,
    CONSTRAINT pk_prefixo_cep PRIMARY KEY (prefixo_cep),
    CONSTRAINT ck_prefixo_cep_formato
        CHECK (prefixo_cep ~ '^[0-9]{5}$')
);

CREATE TABLE core.cliente (
    id_cliente character varying(32) NOT NULL,
    id_cliente_unico character varying(32) NOT NULL,
    prefixo_cep character(5) NOT NULL,
    cidade character varying(50) NOT NULL,
    estado character(2) NOT NULL,
    CONSTRAINT pk_cliente PRIMARY KEY (id_cliente),
    CONSTRAINT ck_cliente_id_cliente_formato
        CHECK (id_cliente ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_cliente_id_cliente_unico_formato
        CHECK (id_cliente_unico ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_cliente_prefixo_cep_formato
        CHECK (prefixo_cep ~ '^[0-9]{5}$'),
    CONSTRAINT ck_cliente_cidade_nao_vazia
        CHECK (btrim(cidade) <> ''),
    CONSTRAINT ck_cliente_estado
        CHECK (estado IN (
            'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR',
            'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
        )),
    CONSTRAINT fk_cliente_prefixo_cep
        FOREIGN KEY (prefixo_cep)
        REFERENCES core.prefixo_cep (prefixo_cep)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

CREATE TABLE core.produto (
    id_produto character varying(32) NOT NULL,
    nome_categoria character varying(50),
    comprimento_nome smallint,
    comprimento_descricao smallint,
    quantidade_fotos smallint,
    peso_g integer,
    comprimento_cm smallint,
    altura_cm smallint,
    largura_cm smallint,
    CONSTRAINT pk_produto PRIMARY KEY (id_produto),
    CONSTRAINT ck_produto_id_produto_formato
        CHECK (id_produto ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_produto_categoria_nao_vazia
        CHECK (btrim(nome_categoria) <> ''),
    CONSTRAINT ck_produto_comprimento_nome_nao_negativo
        CHECK (comprimento_nome >= 0),
    CONSTRAINT ck_produto_comprimento_descricao_nao_negativo
        CHECK (comprimento_descricao >= 0),
    CONSTRAINT ck_produto_quantidade_fotos_nao_negativa
        CHECK (quantidade_fotos >= 0),
    CONSTRAINT ck_produto_peso_nao_negativo
        CHECK (peso_g >= 0),
    CONSTRAINT ck_produto_comprimento_nao_negativo
        CHECK (comprimento_cm >= 0),
    CONSTRAINT ck_produto_altura_nao_negativa
        CHECK (altura_cm >= 0),
    CONSTRAINT ck_produto_largura_nao_negativa
        CHECK (largura_cm >= 0)
);

CREATE TABLE core.vendedor (
    id_vendedor character varying(32) NOT NULL,
    prefixo_cep character(5) NOT NULL,
    cidade character varying(50) NOT NULL,
    estado character(2) NOT NULL,
    CONSTRAINT pk_vendedor PRIMARY KEY (id_vendedor),
    CONSTRAINT ck_vendedor_id_vendedor_formato
        CHECK (id_vendedor ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_vendedor_prefixo_cep_formato
        CHECK (prefixo_cep ~ '^[0-9]{5}$'),
    CONSTRAINT ck_vendedor_cidade_nao_vazia
        CHECK (btrim(cidade) <> ''),
    CONSTRAINT ck_vendedor_estado
        CHECK (estado IN (
            'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR',
            'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
        )),
    CONSTRAINT fk_vendedor_prefixo_cep
        FOREIGN KEY (prefixo_cep)
        REFERENCES core.prefixo_cep (prefixo_cep)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

CREATE TABLE core.pedido (
    id_pedido character varying(32) NOT NULL,
    id_cliente character varying(32) NOT NULL,
    status_pedido character varying(20) NOT NULL,
    data_compra timestamp without time zone NOT NULL,
    data_aprovacao timestamp without time zone,
    data_envio_transportador timestamp without time zone,
    data_entrega timestamp without time zone,
    data_estimada timestamp without time zone NOT NULL,
    CONSTRAINT pk_pedido PRIMARY KEY (id_pedido),
    CONSTRAINT uq_pedido_id_cliente UNIQUE (id_cliente),
    CONSTRAINT ck_pedido_id_pedido_formato
        CHECK (id_pedido ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_pedido_id_cliente_formato
        CHECK (id_cliente ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_pedido_status
        CHECK (status_pedido IN (
            'approved', 'canceled', 'created', 'delivered', 'invoiced',
            'processing', 'shipped', 'unavailable'
        )),
    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES core.cliente (id_cliente)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

CREATE TABLE core.item_pedido (
    id_pedido character varying(32) NOT NULL,
    id_item smallint NOT NULL,
    id_produto character varying(32) NOT NULL,
    id_vendedor character varying(32) NOT NULL,
    data_limite_envio timestamp without time zone NOT NULL,
    preco_item numeric(12, 2) NOT NULL,
    valor_frete numeric(12, 2) NOT NULL,
    CONSTRAINT pk_item_pedido PRIMARY KEY (id_pedido, id_item),
    CONSTRAINT ck_item_pedido_id_pedido_formato
        CHECK (id_pedido ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_item_pedido_id_item_positivo
        CHECK (id_item > 0),
    CONSTRAINT ck_item_pedido_id_produto_formato
        CHECK (id_produto ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_item_pedido_id_vendedor_formato
        CHECK (id_vendedor ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_item_pedido_preco_nao_negativo
        CHECK (preco_item >= 0),
    CONSTRAINT ck_item_pedido_frete_nao_negativo
        CHECK (valor_frete >= 0),
    CONSTRAINT fk_item_pedido_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES core.pedido (id_pedido)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT,
    CONSTRAINT fk_item_pedido_produto
        FOREIGN KEY (id_produto)
        REFERENCES core.produto (id_produto)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT,
    CONSTRAINT fk_item_pedido_vendedor
        FOREIGN KEY (id_vendedor)
        REFERENCES core.vendedor (id_vendedor)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

CREATE TABLE core.pagamento (
    id_pedido character varying(32) NOT NULL,
    sequencial_pagamento smallint NOT NULL,
    tipo_pagamento character varying(20) NOT NULL,
    numero_parcelas smallint NOT NULL,
    valor_pagamento numeric(12, 2) NOT NULL,
    CONSTRAINT pk_pagamento PRIMARY KEY (id_pedido, sequencial_pagamento),
    CONSTRAINT ck_pagamento_id_pedido_formato
        CHECK (id_pedido ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_pagamento_sequencial_positivo
        CHECK (sequencial_pagamento > 0),
    CONSTRAINT ck_pagamento_tipo
        CHECK (tipo_pagamento IN (
            'boleto', 'credit_card', 'debit_card', 'not_defined', 'voucher'
        )),
    CONSTRAINT ck_pagamento_parcelas_nao_negativas
        CHECK (numero_parcelas >= 0),
    CONSTRAINT ck_pagamento_valor_nao_negativo
        CHECK (valor_pagamento >= 0),
    CONSTRAINT fk_pagamento_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES core.pedido (id_pedido)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

CREATE TABLE core.avaliacao (
    id_avaliacao character varying(32) NOT NULL,
    id_pedido character varying(32) NOT NULL,
    nota_avaliacao smallint NOT NULL,
    data_criacao timestamp without time zone NOT NULL,
    data_resposta timestamp without time zone NOT NULL,
    CONSTRAINT pk_avaliacao PRIMARY KEY (id_avaliacao, id_pedido),
    CONSTRAINT ck_avaliacao_id_avaliacao_formato
        CHECK (id_avaliacao ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_avaliacao_id_pedido_formato
        CHECK (id_pedido ~ '^[0-9a-f]{32}$'),
    CONSTRAINT ck_avaliacao_nota
        CHECK (nota_avaliacao BETWEEN 1 AND 5),
    CONSTRAINT fk_avaliacao_pedido
        FOREIGN KEY (id_pedido)
        REFERENCES core.pedido (id_pedido)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

CREATE TABLE core.geolocalizacao (
    id_geolocalizacao bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
    prefixo_cep character(5) NOT NULL,
    latitude double precision NOT NULL,
    longitude double precision NOT NULL,
    cidade character varying(50) NOT NULL,
    estado character(2) NOT NULL,
    CONSTRAINT pk_geolocalizacao PRIMARY KEY (id_geolocalizacao),
    CONSTRAINT ck_geolocalizacao_prefixo_cep_formato
        CHECK (prefixo_cep ~ '^[0-9]{5}$'),
    CONSTRAINT ck_geolocalizacao_latitude
        CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT ck_geolocalizacao_longitude
        CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT ck_geolocalizacao_cidade_nao_vazia
        CHECK (btrim(cidade) <> ''),
    CONSTRAINT ck_geolocalizacao_estado
        CHECK (estado IN (
            'AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO',
            'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR',
            'RJ', 'RN', 'RO', 'RR', 'RS', 'SC', 'SE', 'SP', 'TO'
        )),
    CONSTRAINT fk_geolocalizacao_prefixo_cep
        FOREIGN KEY (prefixo_cep)
        REFERENCES core.prefixo_cep (prefixo_cep)
        ON UPDATE NO ACTION
        ON DELETE RESTRICT
);

COMMIT;
