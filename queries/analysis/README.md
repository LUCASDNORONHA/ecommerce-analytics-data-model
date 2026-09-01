# Consultas analíticas

Consultas que combinam entidades do modelo `core` com granularidade e regras de
agregação explícitas.

## Coleção M06-02

1. `01_evolucao_financeira_mensal.sql`: evolução e reconciliação financeira.
2. `02_concentracao_vendedores.sql`: participação, curva ABC e HHI.
3. `03_desempenho_vendedor_categoria.sql`: contribuição por vendedor e categoria.
4. `04_alcance_geografico_vendedores.sql`: origem e alcance estadual.
5. `05_risco_operacional_vendedores.sql`: desempenho financeiro, atraso e avaliação associados.
6. `06_perfil_pagamentos_pedido.sql`: formas, parcelamento e faixas de valor.
7. `07_resumo_indicadores_executivos.sql`: síntese histórica dos indicadores
   financeiros e de concentração.

## Coleção M06-04

8. `08_metricas_cancelamento.sql`: taxa de cancelamento por quantidade e
   valores de itens, frete, bruto e pagamento associados aos pedidos
   cancelados.

Todas as medidas financeiras principais utilizam pedidos entregues e
`core.pedido.data_compra`. Pagamentos, itens e avaliações são pré-agregados na
granularidade de pedido antes de combinações que poderiam multiplicar valores.
