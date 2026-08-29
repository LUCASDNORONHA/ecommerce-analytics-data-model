BEGIN;

DROP INDEX IF EXISTS core.idx_geolocalizacao_prefixo_cep;
DROP INDEX IF EXISTS core.idx_avaliacao_id_pedido;
DROP INDEX IF EXISTS core.idx_item_pedido_id_vendedor;
DROP INDEX IF EXISTS core.idx_item_pedido_id_produto;
DROP INDEX IF EXISTS core.idx_vendedor_prefixo_cep;
DROP INDEX IF EXISTS core.idx_cliente_prefixo_cep;

COMMIT;
