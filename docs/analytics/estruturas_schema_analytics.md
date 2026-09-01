# Estruturas do schema ANALYTICS

## 1. Finalidade

As views do schema `analytics` estabilizam combinações e regras recorrentes
validadas nas etapas M06-01 a M06-04. Elas reduzem repetição, tornam explícita a
granularidade de consumo e preservam rastreabilidade até a CORE.

Não são cópias das tabelas de origem, não alteram a CORE e não materializam
dados. A seleção final de campos, relacionamentos e visuais para Power BI
pertence à etapa M06-06.

## 2. Mapa de dependências

```text
core.pedido ─┬─ core.cliente
             ├─ core.item_pedido
             ├─ core.pagamento
             └─ core.avaliacao
                      │
                      ▼
        analytics.vw_pedido_financeiro
                      │
                      ▼
        analytics.vw_financeiro_mensal

core.item_pedido ─┬─ core.pedido ─ core.cliente
                  ├─ core.vendedor
                  └─ core.avaliacao
                           │
                           ▼
           analytics.vw_vendedor_pedido
                           │
              core.produto ┤
                           ▼
        analytics.vw_desempenho_vendedor
```

## 3. `analytics.vw_pedido_financeiro`

**Finalidade:** fornecer a base financeira e operacional reutilizável de
pedido, evitando o join direto entre itens, pagamentos e avaliações.

**Granularidade:** uma linha por `id_pedido`, incluindo todos os status.

**População observada:** 99.441 linhas, sem duplicação de pedido.

| Grupo | Campos | Definição |
|---|---|---|
| Identidade | `id_pedido`, `id_cliente`, `id_cliente_unico` | Chaves do pedido e identidade persistente do cliente. |
| Cliente | `cidade_cliente`, `estado_cliente` | Localização cadastral, não endereço exato da entrega. |
| Pedido | `status_pedido`, `data_compra`, `mes_compra`, `data_aprovacao`, `data_envio_transportador`, `data_entrega`, `data_estimada` | Estado e marcos temporais preservados da CORE. |
| Entrega | `entrega_atrasada` | `data_entrega > data_estimada`; nulo quando não calculável. |
| Cobertura | `possui_itens`, `possui_pagamentos`, `possui_avaliacao` | Flags que impedem interpretar ausência como valor zero. |
| Itens | `quantidade_itens`, `quantidade_vendedores`, `valor_itens`, `valor_frete`, `valor_bruto` | Itens pré-agregados por pedido; valores ficam nulos quando não há item. |
| Pagamentos | `quantidade_pagamentos`, `quantidade_tipos_pagamento`, `maximo_parcelas`, `valor_pago_registrado` | Sequências pré-agregadas por pedido; valores ficam nulos quando não há pagamento. |
| Reconciliação | `diferenca_reconciliacao` | Pagamento menos bruto, somente quando ambas as relações existem. |
| Avaliação | `quantidade_avaliacoes`, `nota_media_pedido` | Avaliações pré-agregadas por pedido. |

## 4. `analytics.vw_financeiro_mensal`

**Finalidade:** disponibilizar os KPIs financeiros recorrentes por mês de
compra, incluindo cobertura temporal e cancelamentos.

**Granularidade:** uma linha por `mes_compra`.

**População observada:** 25 meses.

| Grupo | Campos | Definição |
|---|---|---|
| Tempo | `mes_compra`, `cobertura_diaria_completa` | Mês de compra e sinalização de presença de pedidos em todos os dias do mês. |
| Pedidos | `pedidos`, `pedidos_entregues`, `pedidos_entregues_completos`, `pedidos_cancelados` | Volumes total, entregue, entregue com itens e pagamentos, e cancelado. |
| Cancelamento | `taxa_cancelamento_quantidade_percentual` | Cancelados divididos por todos os pedidos do mês. |
| Financeiro entregue | `valor_itens_entregues`, `valor_frete_entregue`, `valor_bruto_entregue`, `valor_pago_registrado_entregue` | Somas sobre pedidos entregues com itens e pagamentos. |
| Reconciliação | `diferenca_reconciliacao_entregue` | Soma das diferenças por pedido; não substitui o controle individual. |
| Médias e composição | `valor_bruto_medio_pedido_entregue`, `participacao_frete_percentual` | Média explícita do bruto e participação do frete. |
| Evolução | `crescimento_mensal_valor_itens_percentual` | Calculado apenas quando mês atual e anterior têm cobertura diária completa. |
| Cancelados | `valor_itens_associado_cancelados`, `valor_frete_associado_cancelados`, `valor_bruto_associado_cancelados`, `valor_pago_registrado_associado_cancelados` | Representações separadas; não significam perda ou estorno. |

## 5. `analytics.vw_vendedor_pedido`

**Finalidade:** estabilizar a combinação entre contribuição direta do vendedor
e informações apenas associadas ao pedido.

**Granularidade:** uma linha por par `id_vendedor`, `id_pedido`, somente para
pedidos entregues.

**População observada:** 97.819 linhas.

| Grupo | Campos | Definição |
|---|---|---|
| Identidade e tempo | `id_vendedor`, `id_pedido`, `data_compra`, `mes_compra` | Participação do vendedor no pedido e referência temporal. |
| Geografia | `cidade_vendedor`, `estado_vendedor`, `cidade_cliente`, `estado_cliente` | Origem cadastral do vendedor e destino cadastral do cliente. |
| Itens diretos | `quantidade_itens`, `valor_itens`, `valor_frete`, `valor_bruto` | Medidas diretamente atribuíveis aos itens do vendedor. |
| Envio direto | `itens_com_envio_observado`, `itens_enviados_apos_limite`, `possui_item_enviado_apos_limite` | Contagens por item e flag de presença no par vendedor-pedido. |
| Pedido associado | `entrega_atrasada_associada`, `nota_media_associada` | Entrega final e avaliação pertencem ao pedido; não atribuem responsabilidade. |

## 6. `analytics.vw_desempenho_vendedor`

**Finalidade:** fornecer uma visão histórica consolidada de contribuição,
concentração, alcance e qualidade associada dos vendedores.

**Granularidade:** uma linha por vendedor com item em pedido entregue.

**População observada:** 2.970 linhas.

| Grupo | Campos | Definição |
|---|---|---|
| Identidade | `id_vendedor`, `cidade_vendedor`, `estado_vendedor` | Vendedor e localização cadastral de origem. |
| Ranking | `posicao_valor_itens`, `participacao_valor_itens_percentual`, `participacao_acumulada_percentual`, `classe_abc`, `hhi_base_observada` | Concentração interna da base; não representa mercado ou avaliação regulatória. |
| Volumes e valores | `pedidos_com_participacao`, `quantidade_itens`, `valor_itens`, `valor_frete`, `valor_bruto` | Contribuição direta histórica em pedidos entregues. |
| Médias | `valor_medio_por_item`, `valor_medio_por_pedido_com_participacao` | Médias com numerador e denominador explícitos. |
| Diversidade e alcance | `categorias_comercializadas`, `estados_clientes_atendidos`, `cidades_clientes_atendidas` | Diversidade e alcance observados, não cobertura comercial formal. |
| Envio | `itens_com_envio_observado`, `itens_enviados_apos_limite`, `taxa_itens_enviados_apos_limite_percentual` | VEN08 na granularidade correta de item. |
| Entrega associada | `pedidos_com_prazo_entrega_observado`, `pedidos_atrasados_associados`, `taxa_pedidos_atrasados_associados_percentual` | Atraso final associado à participação do vendedor. |
| Avaliação associada | `pedidos_com_avaliacao_associada`, `nota_media_associada`, `pedidos_com_avaliacao_negativa_associada`, `taxa_avaliacao_negativa_associada_percentual` | Avaliações do pedido, sem atribuição causal ao vendedor. |

## 7. Instalação e validação

O `database.setup` executa as views na ordem numérica de dependência e valida a
existência das quatro estruturas com `models/analytics/validate_views.sql`.

Após a carga, `queries/validation/06_views_analytics.sql` compara as
granularidades e os valores atribuídos aos vendedores contra a CORE. Na carga
aprovada, todas as diferenças de contagem e valor resultaram em zero.

As views são normais, não materializadas. Essa decisão evita duplicar dados e
criar política de atualização antes de existir evidência de necessidade de
desempenho. Materialização ou índices específicos exigirão medição própria.

## 8. Decisões e limitações

- Valores nulos em relações ausentes são preservados; contagens usam zero.
- Pagamentos não são alocados aos vendedores.
- A visão mensal principal compara itens e pagamentos somente na população
  entregue que possui ambas as relações.
- O crescimento mensal permanece nulo em comparações com cobertura parcial.
- A taxa VEN08 é calculada por item (9,32%). O indicador exploratório anterior
  de 8,97% representa pares vendedor-pedido com algum item fora do limite.
- As estruturas são adequadas ao consumo SQL recorrente. O contrato final de
  importação, relacionamentos e medidas do Power BI está documentado em
  [`consumo_power_bi_sql.md`](consumo_power_bi_sql.md).
