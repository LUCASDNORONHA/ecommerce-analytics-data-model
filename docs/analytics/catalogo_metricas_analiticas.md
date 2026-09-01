# Catálogo de métricas analíticas

## 1. Finalidade e escopo

Este catálogo consolida as métricas aprovadas para responder prioritariamente
ao desempenho financeiro e, em seguida, ao desempenho dos vendedores. As
definições utilizam exclusivamente a CORE validada e correspondem ao período
histórico do dataset.

Os valores observados não representam receita contábil, lucro, margem,
liquidação financeira nem a operação atual da Olist. Todas as métricas são
descritivas e não demonstram causalidade.

## 2. Políticas comuns

- **Data financeira e comercial:** `core.pedido.data_compra`.
- **Base principal:** pedidos com `status_pedido = 'delivered'`.
- **Base financeira completa:** pedidos entregues com itens e pagamentos, quando
  a métrica compara essas duas representações.
- **Cancelamento:** todos os pedidos compõem o denominador; o numerador contém
  somente `status_pedido = 'canceled'`.
- **Granularidade:** itens e pagamentos são agregados separadamente por pedido
  antes de qualquer combinação.
- **Vendedores:** valor dos itens, frete e quantidade de itens são diretamente
  atribuíveis. Entrega final e avaliação são apenas associadas ao pedido com
  participação do vendedor.
- **Percentuais:** são expressos na escala de 0 a 100. HHI permanece na escala
  de 0 a 1.
- **Valores monetários:** BRL com precisão exata; arredondamento é aplicado
  somente à apresentação de médias, taxas e percentuais.

## 3. Métricas financeiras

| ID | Nome e finalidade | Fórmula e unidade | Granularidade e tempo | Filtros e exclusões | Fontes e SQL | Interpretação e limitações |
|---|---|---|---|---|---|---|
| FIN01 | **Valor dos itens entregues** — medir o valor comercial dos produtos | `SUM(preco_item)`; BRL | Origem item; saída histórica, mensal ou segmento; `data_compra` | Pedidos entregues; na comparação financeira, exige item e pagamento | `core.item_pedido.preco_item`; consultas 01 e 07 de `queries/analysis/` | Valor observado dos itens; não é receita líquida, margem ou lucro. |
| FIN02 | **Valor de frete entregue** — medir o frete cobrado nos itens | `SUM(valor_frete)`; BRL | Origem item; saída histórica, mensal ou segmento; `data_compra` | Mesma base da FIN01 | `core.item_pedido.valor_frete`; consultas 01 e 07 | Frete cobrado, não custo logístico real. |
| FIN03 | **Valor bruto entregue** — medir itens mais frete | `SUM(preco_item + valor_frete)`; BRL | Item, pré-agregado por pedido; saída histórica, mensal ou segmento | Mesma base da FIN01 | `core.item_pedido`; consultas 01 e 07 | Valor bruto observado; não comprova reconhecimento contábil. |
| FIN04 | **Valor pago registrado** — medir pagamentos associados aos pedidos | `SUM(valor_pagamento)`; BRL | Sequência de pagamento, pré-agregada por pedido; saída histórica ou mensal | Pedidos entregues com itens e pagamentos | `core.pagamento.valor_pagamento`; consultas 01 e 07 | Registro da fonte; não comprova liquidação, estorno ou recebimento. |
| FIN05 | **Diferença de reconciliação** — comparar pagamento e valor bruto | `valor_pago_registrado - valor_bruto`; BRL por pedido, com soma e classificação | Origem e controle por pedido; saída mensal ou histórica; `data_compra` | Somente pedidos presentes em itens e pagamentos; tolerância de R$ 0,01 apenas na classificação | `core.item_pedido`, `core.pagamento`; análise 01 e validação 01 | Divergência para investigação; somas positivas e negativas podem se compensar. |
| FIN06 | **Valor bruto médio por pedido entregue** — medir valor bruto médio da base | `SUM(valor_bruto) / COUNT(DISTINCT id_pedido)`; BRL/pedido | Pedido; saída histórica, mensal ou segmento; `data_compra` | Pedidos entregues com itens e pagamentos | Análises 01 e 07 | Não utilizar o nome ambíguo “ticket médio”; a base monetária é explícita. |
| FIN07 | **Participação do frete** — medir o peso do frete no valor bruto | `100 × SUM(valor_frete) / SUM(valor_bruto)`; percentual | Saída histórica, mensal ou segmento; `data_compra` | Pedidos entregues; denominador diferente de zero | Análises 01 e 07 | Mede composição do valor cobrado, não eficiência ou custo logístico. |
| FIN08 | **Crescimento mensal do valor dos itens** — comparar evolução mensal | `100 × (valor_itens_mês / valor_itens_mês_anterior - 1)`; percentual | Mês de compra | Mês atual e anterior devem possuir cobertura diária completa; pedidos entregues com itens e pagamentos | `queries/analysis/01_evolucao_financeira_mensal.sql` | Meses parciais retornam nulo; variação não explica causa. |
| FIN09 | **Taxa de cancelamento por quantidade** — medir participação de pedidos cancelados | `100 × pedidos_cancelados / todos_pedidos`; percentual | Pedido, com saída mensal ou histórica; `data_compra` | Todos os status no denominador; `canceled` no numerador | `core.pedido.status_pedido`; análise 08 | Mede registros cancelados na base, não probabilidade futura. Meses parciais devem ser sinalizados. |
| FIN10 | **Valores associados a pedidos cancelados** — dimensionar registros financeiros presentes | Somas separadas de itens, frete, bruto e pagamento; BRL | Itens e pagamentos pré-agregados por pedido; saída mensal ou histórica | Somente pedidos cancelados; ausências preservadas como cobertura | `queries/analysis/08_metricas_cancelamento.sql` | Não representa perda, estorno ou receita cancelada; as representações não devem ser fundidas. |

## 4. Métricas de vendedores

| ID | Nome e finalidade | Fórmula e unidade | Granularidade e tempo | Filtros e exclusões | Fontes e SQL | Interpretação e limitações |
|---|---|---|---|---|---|---|
| VEN01 | **Vendedores ativos** — medir a base com atividade observada | `COUNT(DISTINCT id_vendedor)`; vendedores | Item, saída histórica ou por período; `data_compra` | Ao menos um item em pedido entregue no período | `core.item_pedido`, `core.pedido`; análises 02 e 07 | Atividade no dataset, não situação contratual ou operacional atual. |
| VEN02 | **Valor dos itens por vendedor** — medir contribuição comercial direta | `SUM(preco_item)`; BRL/vendedor | Vendedor; histórica, período ou segmento; `data_compra` | Itens de pedidos entregues | Análise 02 e consulta básica 07 | Diretamente atribuível ao vendedor; não é receita, lucro ou pagamento recebido. |
| VEN03 | **Participação financeira do vendedor** — medir relevância relativa | `100 × valor_itens_vendedor / valor_itens_total`; percentual | Vendedor no mesmo período e população | Mesma base da VEN02; denominador diferente de zero | `queries/analysis/02_concentracao_vendedores.sql` | Participação na base observada, não participação de mercado. |
| VEN04 | **Participação acumulada dos maiores vendedores** — medir concentração | Soma das participações ordenadas por valor; percentual Top 5, 10, 20 e 10% da base | Ranking de vendedor por período | Mesma base da VEN02; desempate por `id_vendedor` | Análises 02 e 07 | Curva descritiva; classes ABC usam inicialmente 80% e 95%. |
| VEN05 | **Pedidos com participação do vendedor** — medir alcance em pedidos | `COUNT(DISTINCT id_pedido)`; pedidos/vendedor | Vendedor; histórica ou por período; `data_compra` | Pedidos entregues com item do vendedor | Consulta básica 07 | Em pedido multivendedor, cada vendedor recebe uma participação; a soma excede pedidos do marketplace. |
| VEN06 | **Itens por vendedor** — medir volume comercializado | `COUNT(*)`; itens/vendedor | Vendedor; histórica ou por período; `data_compra` | Itens de pedidos entregues | Consulta básica 07 | Mede linhas de item, não quantidade física além da representação da fonte. |
| VEN07 | **Valor médio do vendedor por pedido com participação** — medir contribuição média | `valor_itens_vendedor / pedidos_distintos_com_participação`; BRL/pedido participante | Vendedor; histórica ou por período; `data_compra` | Mesma base da VEN02 | Consulta básica 07 | Considera somente a parcela de itens do vendedor; não é o valor total nem o pagamento do pedido. |
| VEN08 | **Taxa de itens enviados após o limite** — medir cumprimento do prazo diretamente relacionado ao item | `100 × itens após data_limite_envio / itens com observação`; percentual | Vendedor-item, consolidada por vendedor; `data_compra` | Pedidos entregues; somente observações não nulas | `core.item_pedido.data_limite_envio`, `core.pedido.data_envio_transportador`; análise 05 | O envio é comparado ao limite do item; não explica a causa do atraso. |
| VEN09 | **Taxa de pedidos atrasados associados ao vendedor** — contextualizar risco de entrega | `100 × pedidos entregues após estimativa / pedidos com datas`; percentual | Vendedor-pedido; histórica ou por período; `data_compra` | Pedidos entregues com datas de entrega e estimativa | `core.pedido`; `queries/analysis/05_risco_operacional_vendedores.sql` | Atraso pertence ao pedido; usar “associado”, sem atribuir responsabilidade ao vendedor. |
| VEN10 | **Nota média associada ao vendedor** — contextualizar experiência | Média da nota média pré-agregada por pedido; pontos de 1 a 5 | Vendedor-pedido; histórica ou por período; `data_compra` | Pedidos entregues com avaliação | `core.avaliacao.nota_avaliacao`; análise 05 | Avaliação pertence ao pedido e pode envolver vários vendedores; não mede causalidade. |

## 5. Resultados históricos de referência

Na base de 96.477 pedidos entregues com itens e pagamentos:

| Métrica | Resultado |
|---|---:|
| FIN01 — valor dos itens | R$ 13.221.363,14 |
| FIN02 — valor de frete | R$ 2.198.267,15 |
| FIN03 — valor bruto | R$ 15.419.630,29 |
| FIN04 — valor pago registrado | R$ 15.422.461,77 |
| FIN05 — diferença agregada | R$ 2.831,48 |
| FIN06 — valor bruto médio por pedido | R$ 159,83 |
| FIN07 — participação do frete | 14,26% |

No histórico completo, 625 de 99.441 pedidos estão cancelados (FIN09:
0,6285%). Para esses pedidos, foram observados R$ 95.235,27 em itens,
R$ 10.650,45 em frete, R$ 105.885,72 em valor bruto e R$ 143.255,60 em
pagamentos registrados. Há 164 cancelados sem itens e nenhum sem pagamento, o
que impede tratar as representações como equivalentes.

Para vendedores, foram observados 2.970 ativos. Os 5, 10 e 20 maiores
representam, respectivamente, 7,71%, 13,27% e 21,28% do valor dos itens; os 10%
maiores representam 67,11%. Na granularidade vendedor-pedido, a taxa de envio
após o limite é 8,97%, a taxa de atraso associado é 8,02% e a nota média
associada é 4,14.

## 6. Validação e controles

| Risco | Controle | Resultado |
|---|---|---|
| Multiplicação de itens e pagamentos | `queries/validation/02_controle_join_itens_pagamentos.sql` | O join direto multiplica linhas e não pode sustentar somas. |
| Diferenças entre bruto e pagamento | `queries/validation/01_reconciliacao_financeira.sql` | Reconciliação preservada por pedido e classificada com tolerância de R$ 0,01. |
| Cobertura de itens e pagamentos | `queries/validation/03_cobertura_relacoes_pedido.sql` | Exceções permanecem visíveis e determinam a população de cada métrica. |
| Atribuição a vendedores | `queries/validation/04_granularidade_vendedor.sql` | Itens e valor atribuído reconciliam sem diferença; participações adicionais refletem pedidos multivendedor. |
| Requisitos e relações | `queries/validation/05_cobertura_requisitos_funcionais.sql` | Cobertura e limitações das relações estão documentadas por requisito. |

## 7. Decisões para ANALYTICS e BI

- A base financeira por pedido deve estabilizar as pré-agregações de itens e
  pagamentos e informar flags de cobertura.
- A estrutura de vendedor deve preservar as granularidades vendedor e
  vendedor-pedido, sem repetir o pagamento integral.
- Métricas mensais devem expor a completude da cobertura antes de permitir
  comparação temporal.
- Valores de pedidos cancelados devem permanecer em colunas separadas por
  representação financeira.
- Nomes de campos de BI devem incluir a medida-base e, para vendedor, o termo
  `associado` quando a informação pertencer ao pedido.
- HHI e classe ABC são diagnósticos complementares à VEN04, não métricas de
  mercado nem critérios regulatórios.
