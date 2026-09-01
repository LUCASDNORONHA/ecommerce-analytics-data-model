# Consultas de validação

Consultas de controle utilizadas para reconciliar métricas, volumes e riscos de
duplicação entre granularidades diferentes.

## Controles da etapa M06-01

1. `01_reconciliacao_financeira.sql`: compara valor bruto e valor pago por
   pedido.
2. `02_controle_join_itens_pagamentos.sql`: demonstra e quantifica o risco de
   multiplicação em um join direto.
3. `03_cobertura_relacoes_pedido.sql`: identifica pedidos sem itens, pagamentos
   ou ambos.
4. `04_granularidade_vendedor.sql`: valida a atribuição de itens e valores a
   vendedores.

## Controles da etapa M06-03

5. `05_cobertura_requisitos_funcionais.sql`: consolida evidências de integração
   das entidades, histórico de clientes, avaliações, marcos temporais e
   cobertura geográfica para a matriz de requisitos funcionais.

## Controles da etapa M06-05

6. `06_views_analytics.sql`: valida as granularidades das quatro views e
   reconcilia os valores atribuídos aos vendedores contra a CORE.

Resultados diferentes de zero não representam automaticamente erro. Cada
consulta registra a interpretação apropriada para o controle.
