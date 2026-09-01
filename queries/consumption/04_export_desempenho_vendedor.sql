-- Dataset: resumo_desempenho_vendedor
-- Granularidade: uma linha por vendedor com item em pedido entregue.
-- Chave: id_vendedor.
SELECT
    id_vendedor,
    cidade_vendedor,
    estado_vendedor,
    posicao_valor_itens,
    pedidos_com_participacao,
    quantidade_itens,
    valor_itens,
    valor_frete,
    valor_bruto,
    valor_medio_por_item,
    valor_medio_por_pedido_com_participacao,
    participacao_valor_itens_percentual,
    participacao_acumulada_percentual,
    classe_abc,
    hhi_base_observada,
    categorias_comercializadas,
    estados_clientes_atendidos,
    cidades_clientes_atendidas,
    itens_com_envio_observado,
    itens_enviados_apos_limite,
    taxa_itens_enviados_apos_limite_percentual,
    pedidos_com_prazo_entrega_observado,
    pedidos_atrasados_associados,
    taxa_pedidos_atrasados_associados_percentual,
    pedidos_com_avaliacao_associada,
    nota_media_associada,
    pedidos_com_avaliacao_negativa_associada,
    taxa_avaliacao_negativa_associada_percentual
FROM analytics.vw_desempenho_vendedor;
