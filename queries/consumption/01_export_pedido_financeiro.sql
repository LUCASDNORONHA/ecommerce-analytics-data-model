-- Dataset: fato_pedido_financeiro
-- Granularidade: uma linha por pedido, incluindo todos os status.
-- Chave: id_pedido.
SELECT
    id_pedido,
    id_cliente,
    id_cliente_unico,
    cidade_cliente,
    estado_cliente,
    status_pedido,
    data_compra,
    mes_compra,
    data_aprovacao,
    data_envio_transportador,
    data_entrega,
    data_estimada,
    entrega_atrasada,
    possui_itens,
    possui_pagamentos,
    possui_avaliacao,
    quantidade_itens,
    quantidade_vendedores,
    valor_itens,
    valor_frete,
    valor_bruto,
    quantidade_pagamentos,
    quantidade_tipos_pagamento,
    maximo_parcelas,
    valor_pago_registrado,
    diferenca_reconciliacao,
    quantidade_avaliacoes,
    nota_media_pedido
FROM analytics.vw_pedido_financeiro;
