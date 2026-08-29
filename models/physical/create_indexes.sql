BEGIN;

CREATE INDEX idx_cliente_prefixo_cep
    ON core.cliente (prefixo_cep);
CREATE INDEX idx_vendedor_prefixo_cep
    ON core.vendedor (prefixo_cep);
CREATE INDEX idx_item_pedido_id_produto
    ON core.item_pedido (id_produto);
CREATE INDEX idx_item_pedido_id_vendedor
    ON core.item_pedido (id_vendedor);
CREATE INDEX idx_avaliacao_id_pedido
    ON core.avaliacao (id_pedido);
CREATE INDEX idx_geolocalizacao_prefixo_cep
    ON core.geolocalizacao (prefixo_cep);

COMMIT;
