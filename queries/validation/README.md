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

Resultados diferentes de zero não representam automaticamente erro. Cada
consulta registra a interpretação apropriada para o controle.
