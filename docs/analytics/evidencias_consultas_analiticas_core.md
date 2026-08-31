# Evidências das consultas analíticas sobre a CORE

## 1. Escopo

Este documento registra evidências da etapa M06-02, orientada prioritariamente
ao desempenho financeiro e à contribuição dos vendedores. As consultas-fonte
estão em `queries/analysis/` e utilizam pedidos entregues como base principal.

Os resultados descrevem o período histórico do dataset. Não representam a
operação atual, receita contábil, lucro ou participação no mercado brasileiro.

## 2. Resumo financeiro histórico

A população que possui simultaneamente pedido entregue, itens e pagamentos
contém 96.477 pedidos e 110.194 itens.

| Indicador | Resultado |
|---|---:|
| Valor dos itens | R$ 13.221.363,14 |
| Valor de frete | R$ 2.198.267,15 |
| Valor bruto | R$ 15.419.630,29 |
| Valor pago registrado | R$ 15.422.461,77 |
| Diferença agregada de reconciliação | R$ 2.831,48 |
| Valor bruto médio por pedido | R$ 159,83 |
| Participação do frete | 14,26% |

A diferença agregada não significa que todos os pedidos estejam conciliados.
Diferenças positivas e negativas podem se compensar; a validação por pedido
permanece necessária.

## 3. Evolução mensal

A consulta mensal:

- utiliza `core.pedido.data_compra`;
- agrega itens e pagamentos separadamente por pedido;
- sinaliza meses sem pedidos em todos os dias do calendário;
- calcula crescimento somente quando o mês atual e o anterior possuem cobertura
  diária completa.

Essa regra evita comparar automaticamente os meses de borda ou transição já
identificados na etapa M06-01.

## 4. Concentração dos vendedores

Foram observados 2.970 vendedores ativos em pedidos entregues.

| Indicador | Resultado |
|---|---:|
| Participação acumulada dos 5 maiores | 7,71% |
| Participação acumulada dos 10 maiores | 13,27% |
| HHI da base observada | 0,003631 |

Os resultados indicam dispersão do valor dos itens entre muitos vendedores no
período completo. O HHI é utilizado somente como medida descritiva interna. Não
permite concluir sobre concentração concorrencial ou participação de mercado.

A curva ABC usa inicialmente os limites acumulados de 80% e 95%. Esses limites
são parâmetros analíticos e poderão ser revistos na definição final das
métricas.

## 5. Pedidos com múltiplos vendedores

Entre os pedidos entregues com itens e pagamentos, 1.275 possuem mais de um
vendedor. Por isso:

- valor dos itens e frete podem ser atribuídos diretamente ao vendedor;
- pagamentos não são repetidos nem integralmente atribuídos aos vendedores;
- atrasos e avaliações são descritos como associados ao pedido com participação
  do vendedor.

## 6. Formas e condições de pagamento

| Tipo | Registros | Pedidos distintos | Valor pago registrado | Parcelas médias |
|---|---:|---:|---:|---:|
| Cartão de crédito | 74.586 | 74.304 | R$ 12.101.094,88 | 3,50 |
| Boleto | 19.191 | 19.191 | R$ 2.769.932,58 | 1,00 |
| Voucher | 5.493 | 3.679 | R$ 343.013,19 | 1,00 |
| Cartão de débito | 1.486 | 1.485 | R$ 208.421,12 | 1,00 |

Um pedido pode possuir vários registros e tipos de pagamento. As contagens por
tipo não formam grupos mutuamente exclusivos de pedidos. A consulta de perfil
consolida as sequências por pedido antes de classificá-lo por faixa de valor,
parcelamento e composição dos meios de pagamento.

## 7. Risco operacional associado aos vendedores

Na granularidade vendedor-pedido foram observadas 97.819 participações.

| Indicador associado | Resultado |
|---|---:|
| Envio após o limite do item | 8,97% |
| Pedido entregue após a estimativa | 8,02% |
| Nota média | 4,14 |
| Avaliação negativa, nota menor ou igual a 2 | 13,25% |

As taxas usam somente observações com informação disponível no denominador.
Envio após o limite é diretamente relacionado aos itens do vendedor. Atraso da
entrega e avaliação pertencem ao pedido e não comprovam responsabilidade nem
causalidade do vendedor.

## 8. Recortes de categoria e geografia

As consultas de vendedor-categoria e alcance geográfico permitem:

- medir a participação de uma categoria no valor do vendedor;
- medir a participação do vendedor dentro da categoria;
- contar estados e cidades de clientes atendidos;
- comparar o peso do frete no valor bruto por vendedor.

O estado e a cidade do cliente representam seu cadastro, não o endereço exato
da entrega. Alcance geográfico não equivale a cobertura operacional formal.

## 9. Decisões para as próximas etapas

- manter as bases de item, pagamento e avaliação pré-agregadas;
- preservar meses parciais, mas impedir seu uso automático em crescimento;
- tratar concentração como característica interna da base;
- separar medidas diretamente atribuíveis de indicadores apenas associados;
- validar fórmulas e cobertura contra os requisitos na M06-03;
- consolidar como métricas somente os indicadores aprovados na M06-04.
