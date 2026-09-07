# Validação manual da M07 no Power BI Desktop

A validação abaixo deve ser executada após abrir `EcommerceAnalytics.pbip` e atualizar o modelo.

## Estrutura

- [ ] O PBIP abre sem erro estrutural.
- [ ] O modelo semântico é carregado em TMDL.
- [ ] As quatro views do schema `analytics` são importadas.
- [ ] Não há solicitação de credenciais armazenadas no projeto; a autenticação ocorre pelo Desktop.
- [ ] Não existe relacionamento entre `fato_pedido_financeiro` e `fato_vendedor_pedido` por `id_pedido`.
- [ ] `resumo_desempenho_vendedor` relaciona-se 1:N com `fato_vendedor_pedido` por `id_vendedor`.

## Controles históricos esperados

Para o histórico completo documentado na M06, antes de aplicar filtros adicionais:

| Indicador | Controle |
|---|---:|
| Pedidos entregues | 96.478 |
| Pedidos entregues com itens e pagamentos | 96.477 |
| Valor dos itens | R$ 13.221.363,14 |
| Valor de frete | R$ 2.198.267,15 |
| Valor bruto | R$ 15.419.630,29 |
| Valor pago registrado | R$ 15.422.461,77 |
| Diferença agregada de reconciliação | R$ 2.831,48 |
| Valor bruto médio por pedido | R$ 159,83 |
| Participação do frete | 14,26% |
| Pedidos cancelados | 625 de 99.441 (0,6285%) |
| Vendedores ativos | 2.970 |
| Participação acumulada Top 10 vendedores | 13,27% |
| HHI da base observada | 0,003631 |
| Participações vendedor-pedido | 97.819 |
| Taxa por item enviado após o limite | 9,32% |
| Participações vendedor-pedido com item após o limite | 8,97% |
| Atraso de entrega associado ao vendedor | 8,02% |
| Nota média associada ao vendedor | 4,14 |
| Avaliação negativa associada | 13,25% |

Os controles acima são referências históricas da documentação consolidada; filtros por período, estado ou vendedor alteram naturalmente os resultados. A taxa de 9,32% possui granularidade de item, enquanto 8,97% descreve participações vendedor-pedido com ao menos um item fora do limite.

## Totais e reconciliação

- [ ] `Pedidos Entregues` = 96.478 no histórico completo.
- [ ] `Pedidos Entregues Completos` = 96.477 no histórico completo.
- [ ] `Valor dos Itens Entregues` coincide com o controle SQL da M06.
- [ ] `Valor Bruto Entregue` coincide com `analytics.vw_financeiro_mensal` quando agregado sobre meses completos equivalentes.
- [ ] `Valor Pago Registrado Entregue` e `Diferença de Reconciliação Entregue` coincidem com a camada analítica.
- [ ] métricas de vendedores reconciliam com `analytics.vw_desempenho_vendedor`.

## Interação e apresentação

- [ ] Ano e mês sincronizam corretamente entre as páginas.
- [ ] O Top 10 de vendedores exibe apenas posições 1–10.
- [ ] O drillthrough para `Detalhe do Vendedor` filtra um único `id_vendedor`.
- [ ] Tooltips apresentam as medidas auxiliares previstas.
- [ ] Nenhuma interação entre fatos duplica valor de pedido.
- [ ] Títulos e observações deixam explícitas as limitações de causalidade, população e granularidade.
- [ ] Não há corte de rótulos, sobreposição ou visual vazio inesperado.

Se o Desktop regravar versões de schema ou metadados ao abrir/salvar, revise o diff antes de versionar: atualizações automáticas legítimas do formato podem ser preservadas, mas caches e configurações locais devem continuar fora do Git.
