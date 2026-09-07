# Power BI — M07

Implementação versionável da issue #97, composta por um projeto PBIP, relatório PBIR e modelo semântico TMDL.

## Abrir localmente

1. Garanta que o PostgreSQL 18 contenha os schemas `raw`, `core` e `analytics`, com as quatro views canônicas da M06 instaladas.
2. Abra `EcommerceAnalytics.pbip` no Power BI Desktop.
3. No modelo semântico, ajuste os parâmetros `p_servidor` e `p_banco` caso o PostgreSQL não esteja em `localhost:5432/ecommerce_analytics`.
4. Configure a autenticação do PostgreSQL exclusivamente no Power BI Desktop. Credenciais não são armazenadas neste repositório.
5. Atualize o modelo e confronte os totais com `queries/validation/`, `models/analytics/validate_views.sql` e com os controles descritos em `docs/analytics/camada_analitica.pdf`.

## Fontes

O modelo utiliza modo Importação e lê diretamente:

- `analytics.vw_pedido_financeiro` → `fato_pedido_financeiro`;
- `analytics.vw_financeiro_mensal` → `agregado_financeiro_mensal`;
- `analytics.vw_vendedor_pedido` → `fato_vendedor_pedido`;
- `analytics.vw_desempenho_vendedor` → `resumo_desempenho_vendedor`.

Dimensões de calendário, mês e estado são derivadas dessas mesmas views.

## Modelo semântico e granularidade

O modelo preserva a separação entre a granularidade de pedido e a granularidade vendedor-pedido. Não existe relacionamento direto entre `fato_pedido_financeiro` e `fato_vendedor_pedido` por `id_pedido`; essa ausência é deliberada e impede a multiplicação de medidas de pedido em pedidos com múltiplos vendedores.

`resumo_desempenho_vendedor` filtra `fato_vendedor_pedido` por `id_vendedor`. Dimensões de estado são separadas por papel (`cliente` e `vendedor`) para evitar ambiguidade semântica.

## Páginas

1. Visão Executiva;
2. Financeiro e Reconciliação;
3. Vendedores e Concentração;
4. Operação e Experiência;
5. Detalhe do Vendedor — drillthrough por `id_vendedor`.

Ano e mês usam grupos de sincronização entre páginas. As páginas de vendedores usam filtro de UF do vendedor; Operação e Experiência usa UF do cliente.

## Limitações analíticas

- atraso associado a vendedor não demonstra causalidade;
- avaliação associada a vendedor não demonstra causalidade;
- geografia é cadastral e não representa rota física;
- valores de pedidos cancelados permanecem associados ao status e não devem ser interpretados automaticamente como receita realizada;
- diferenças entre valor bruto e pagamento são preservadas para reconciliação, sem ajuste automático.

Consulte `VALIDATION.md` para a validação final no Power BI Desktop.
