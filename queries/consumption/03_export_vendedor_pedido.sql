-- Dataset: fato_vendedor_pedido
-- Granularidade: uma linha por vendedor e pedido entregue.
-- Chave composta: id_vendedor, id_pedido.
SELECT
    id_vendedor,
    id_pedido,
    data_compra,
    mes_compra,
    cidade_vendedor,
    estado_vendedor,
    cidade_cliente,
    estado_cliente,
    quantidade_itens,
    itens_com_envio_observado,
    itens_enviados_apos_limite,
    possui_item_enviado_apos_limite,
    valor_itens,
    valor_frete,
    valor_bruto,
    entrega_atrasada_associada,
    nota_media_associada
FROM analytics.vw_vendedor_pedido;
