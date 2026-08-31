# Contrato analítico da camada ANALYTICS

## 1. Finalidade

Este documento define o problema de negócio, os stakeholders, as decisões,
as demandas, os casos de uso e o catálogo preliminar de indicadores que
orientam a fase M06 — Camada Analítica e Extração de Inteligência.

O contrato antecede a implementação das consultas e estruturas analíticas. Ele
deve orientar a exploração da CORE sem transformar as issues da fase em uma
sequência mecânica. Exploração, validação de requisitos e definição de métricas
podem se retroalimentar, desde que alterações sejam sustentadas por evidência e
registradas de forma rastreável.

## 2. Natureza do cenário

O Brazilian E-Commerce Public Dataset by Olist não identifica uma empresa
demandante nem sua estrutura organizacional. Por isso, os stakeholders e as
decisões descritos neste documento constituem **personas analíticas
hipotéticas**, utilizadas para organizar um caso de uso coerente com os dados
disponíveis.

Os resultados não devem ser apresentados como diagnóstico da operação atual da
Olist nem como representação de sua estrutura real de gestão.

## 3. Cenário e problema de negócio

Uma empresa operadora de marketplace precisa compreender seu desempenho
histórico para orientar decisões financeiras, comerciais e operacionais. Embora
possua dados integrados sobre pedidos, clientes, itens, produtos, vendedores,
pagamentos, avaliações e entregas, ainda não dispõe de uma visão analítica
consolidada e rastreável.

O problema de negócio adotado é:

> A gestão do marketplace não dispõe de informações consolidadas e rastreáveis
> para avaliar prioritariamente o desempenho financeiro e a contribuição dos
> vendedores, considerando também os riscos logísticos e de experiência do
> cliente associados aos resultados observados.

O produto analítico apoiará a compreensão e a priorização de decisões. O
dataset não oferece informações suficientes para executar ações operacionais ou
atribuir causalidade aos padrões encontrados.

## 4. Objetivo analítico

Construir uma camada analítica que transforme os dados históricos do
marketplace em indicadores financeiros e de desempenho dos vendedores,
permitindo:

- acompanhar a geração, a composição e a evolução dos valores observados;
- reconciliar as representações financeiras presentes em itens e pagamentos;
- identificar vendedores relevantes e mensurar a concentração da base;
- comparar categorias, regiões e períodos;
- contextualizar o desempenho com aspectos logísticos e de experiência;
- preparar estruturas reproduzíveis para consumo por SQL e ferramentas de BI.

A pergunta executiva central é:

> Quanto valor foi movimentado em pedidos entregues, como esse valor evoluiu e
> foi composto, quais vendedores mais contribuíram e quais riscos operacionais
> ou de experiência estão associados a essa contribuição?

## 5. Pilares do produto analítico

### 5.1. Desempenho financeiro — foco principal

Compreender a geração, a composição, a evolução e a concentração dos valores
observados no marketplace. Inclui valores dos itens, frete, pagamentos,
parcelamento, reconciliação e recortes por período, categoria, vendedor e
região.

### 5.2. Desempenho dos vendedores — foco secundário

Avaliar a contribuição financeira, a concentração, o alcance comercial e a
qualidade operacional associada aos vendedores.

### 5.3. Logística e experiência — pilares complementares

Utilizar prazos, atrasos, frete e avaliações para contextualizar riscos e
diferenças de desempenho. Associação estatística ou descritiva não será tratada
como evidência de causalidade.

## 6. Stakeholders e decisões apoiadas

| Prioridade | Stakeholder hipotético | Interesse | Decisões apoiadas |
|---:|---|---|---|
| 1 | Gestão financeira e executiva | Valores, composição, evolução e concentração | Priorizar períodos, segmentos e riscos para investigação |
| 2 | Gestão de vendedores | Contribuição e qualidade da base | Priorizar acompanhamento e desenvolvimento de vendedores |
| 3 | Gestão comercial | Categorias, regiões e comportamento dos pedidos | Identificar fontes de valor e segmentos relevantes |
| 4 | Operações e logística | Frete, prazos e atrasos | Priorizar investigações operacionais |
| 5 | Experiência do cliente | Avaliações e fatores associados | Identificar jornadas e segmentos insatisfatórios |
| 6 | BI e dados | Definições, rastreabilidade e consumo | Disponibilizar indicadores reproduzíveis |

## 7. Demandas e perguntas analíticas

| Prioridade | Stakeholder | Decisão | Pergunta | Indicadores principais |
|---:|---|---|---|---|
| P0 | Financeiro/executivo | Acompanhar desempenho | Quanto foi movimentado e como evoluiu? | Valores dos itens, frete, valor bruto, valor pago e crescimento |
| P0 | Financeiro/executivo | Validar consistência | O valor pago é compatível com itens mais frete? | Diferenças absoluta e percentual |
| P0 | Gestão de vendedores | Identificar vendedores estratégicos | Quais vendedores mais contribuem? | Valor dos itens, participação e posição |
| P0 | Gestão de vendedores | Avaliar dependência | O resultado está concentrado? | Top N, curva ABC e HHI |
| P1 | Financeiro | Entender a composição | Qual é a participação do frete? | Frete e participação no valor bruto |
| P1 | Financeiro | Entender pagamentos | Quais meios e condições são utilizados? | Valor e pedidos por tipo e parcelamento |
| P1 | Comercial | Identificar fontes de valor | Quais categorias e regiões contribuem mais? | Valor, pedidos, itens e participação |
| P1 | Gestão de vendedores | Avaliar produtividade | Quem combina valor, pedidos e itens? | Valores, volumes e médias por vendedor |
| P1 | Gestão de vendedores | Avaliar qualidade associada | Quem participa de pedidos com atraso ou avaliação ruim? | Taxas associadas de atraso e avaliação negativa |
| P2 | Operações | Investigar riscos logísticos | Onde estão atrasos e fretes elevados? | Taxa de atraso, prazo e frete |
| P2 | Experiência | Investigar insatisfação | Como avaliações variam por entrega e segmento? | Nota média, distribuição e avaliações negativas |
| P2 | BI e dados | Preparar consumo recorrente | Quais definições precisam ser estabilizadas? | Catálogo, queries, views e marts |

## 8. Casos de uso priorizados

### 8.1. Produto mínimo

#### UC01 — Resumo financeiro executivo

Apresentar, por mês, pedidos entregues, valor dos itens, frete, valor bruto,
valor pago registrado, diferença de reconciliação, valor médio por pedido e
crescimento.

#### UC02 — Composição dos pagamentos

Analisar participação por tipo de pagamento, valor médio por modalidade,
parcelamento, pedidos com múltiplas formas de pagamento e ocorrências não
definidas.

#### UC03 — Desempenho financeiro dos vendedores

Analisar vendedores ativos, valores, itens, pedidos, participação individual e
acumulada, rankings, curva ABC e concentração.

#### UC04 — Reconciliação financeira

Comparar o valor bruto calculado nos itens com o valor registrado nos
pagamentos, preservando a granularidade de pedido e identificando exceções.

### 8.2. Diagnósticos importantes

#### UC05 — Perfil e alcance dos vendedores

Analisar categorias comercializadas, origem, regiões atendidas, amplitude
geográfica e dependência de categorias ou regiões.

#### UC06 — Risco operacional associado aos vendedores

Combinar contribuição financeira, envio após o limite, atraso, frete e
avaliação. O resultado deve separar responsabilidade direta de mera associação.

#### UC07 — Categorias e regiões financeiras

Identificar segmentos com maior valor, evolução mensal, valor médio, peso do
frete, concentração de vendedores e qualidade logística associada.

### 8.3. Análises condicionadas à evidência

- segmentação de vendedores em quadrantes;
- curva ABC por período;
- HHI mensal;
- estimativas geográficas de distância;
- estruturas persistentes específicas para BI.

Essas análises somente serão consolidadas se a distribuição dos dados e a
necessidade de consumo justificarem sua implementação.

## 9. Política financeira

### 9.1. Data de referência

A dimensão temporal principal das métricas financeiras e comerciais será
`core.pedido.data_compra`. As demais datas serão utilizadas para finalidades
específicas:

- `data_aprovacao`: processo de aprovação;
- `data_envio_transportador`: processo logístico;
- `data_entrega`: realização da entrega;
- `data_estimada`: cumprimento do prazo.

Uma métrica não deve alternar entre datas sem registrar explicitamente a
mudança de significado.

### 9.2. Política de status

A visão principal utilizará pedidos com `status_pedido = 'delivered'`. Essa
base representa pedidos concluídos, mas não comprova reconhecimento contábil de
receita.

Uma visão ampla poderá incluir todos os pedidos com registros financeiros para
reconciliação e investigação. Pedidos cancelados, indisponíveis ou ainda não
concluídos serão analisados separadamente.

### 9.3. Medidas observadas

| Métrica | Fórmula | Unidade | Granularidade de origem | Fonte |
|---|---|---|---|---|
| Valor dos itens | `SUM(preco_item)` | BRL | Item | `core.item_pedido.preco_item` |
| Valor de frete | `SUM(valor_frete)` | BRL | Item | `core.item_pedido.valor_frete` |
| Valor bruto | `SUM(preco_item + valor_frete)` | BRL | Item, agregado por pedido | `core.item_pedido` |
| Valor pago registrado | `SUM(valor_pagamento)` | BRL | Sequência, agregada por pedido | `core.pagamento.valor_pagamento` |
| Diferença de reconciliação | `valor_pago - valor_bruto` | BRL | Pedido | Itens e pagamentos pré-agregados |
| Diferença percentual | `(valor_pago - valor_bruto) / valor_bruto` | Percentual | Pedido | Itens e pagamentos pré-agregados |
| Participação do frete | `valor_frete / valor_bruto` | Percentual | Período ou segmento | `core.item_pedido` |
| Valor médio por pedido | `valor agregado / pedidos distintos` | BRL/pedido | Período ou segmento | Pedido e medida escolhida |
| Itens por pedido | `itens / pedidos distintos` | Itens/pedido | Período ou segmento | `core.item_pedido` |

A medida utilizada no numerador do valor médio deve aparecer em seu nome ou em
sua definição. Não será adotado um “ticket médio” sem especificar se a base é o
valor dos itens, o valor bruto ou o valor pago.

### 9.4. Reconciliação

`core.item_pedido` e `core.pagamento` devem ser agregadas separadamente por
`id_pedido` antes de qualquer combinação. A existência de divergências não
autoriza concluir que uma representação esteja incorreta sem investigação.

### 9.5. Atribuição aos vendedores

Podem ser atribuídos diretamente ao vendedor:

- valor dos itens;
- frete associado aos itens;
- valor bruto dos itens;
- quantidade de itens;
- quantidade de pedidos distintos com participação.

O valor de pagamento pertence ao pedido. Ele não será atribuído integralmente a
cada vendedor. Um eventual rateio proporcional deverá ser nomeado como
**valor alocado**, acompanhado da fórmula e sem ser confundido com pagamento
observado.

## 10. Política de análise dos vendedores

### 10.1. Métricas fundamentais

| Métrica | Fórmula resumida | Interpretação |
|---|---|---|
| Vendedores com pedidos | `COUNT(DISTINCT id_vendedor)` | Vendedores presentes na base selecionada |
| Vendedores ativos | Vendedores com item em pedido entregue no período | Base efetivamente ativa segundo a definição adotada |
| Pedidos por vendedor | `COUNT(DISTINCT id_pedido)` | Pedidos com participação |
| Itens por vendedor | Contagem de itens | Volume comercializado |
| Valor dos itens | Soma de `preco_item` | Contribuição comercial direta |
| Frete associado | Soma de `valor_frete` | Frete cobrado nos itens |
| Valor bruto | Itens mais frete | Valor bruto associado |
| Valor médio por item | Valor dos itens dividido pelos itens | Perfil de preço |
| Valor médio por pedido com participação | Valor dos itens dividido pelos pedidos distintos | Contribuição média nos pedidos |
| Participação financeira | Valor do vendedor dividido pelo total | Relevância relativa |
| Categorias comercializadas | Categorias distintas | Diversidade observada |
| Estados atendidos | Estados distintos dos clientes | Alcance geográfico observado |

### 10.2. Concentração

Devem ser avaliadas a participação individual e as participações acumuladas dos
5, 10 e 20 maiores vendedores e dos 10% maiores vendedores.

A curva ABC poderá utilizar inicialmente os limites acumulados de 80% para a
classe A e 95% para as classes A+B. Esses limites são parâmetros descritivos e
podem ser revistos após a análise da distribuição.

O índice HHI será calculado pela soma dos quadrados das participações. Ele mede
concentração na base observada e não deve ser interpretado como concentração do
mercado brasileiro nem como avaliação regulatória.

### 10.3. Indicadores operacionais

São diretamente atribuíveis ao vendedor:

- cumprimento da `data_limite_envio` do item;
- valor dos itens e frete;
- categorias comercializadas;
- origem e alcance geográfico observados.

São apenas associados ao vendedor:

- atraso da entrega final;
- tempo total de entrega;
- avaliação;
- cancelamento do pedido.

Quando houver múltiplos vendedores no mesmo pedido, deve-se utilizar a expressão
“pedido associado” ou “pedido com participação do vendedor”.

### 10.4. Segmentação diagnóstica

Uma análise posterior poderá classificar vendedores nos quadrantes estratégico,
atenção prioritária, potencial e baixa contribuição crítica, combinando
desempenho financeiro e qualidade operacional. Os limites de alto, médio e baixo
serão definidos somente após examinar a distribuição, por percentis ou faixas
justificadas.

## 11. Catálogo mínimo de KPIs

### 11.1. Financeiros

1. Valor dos itens de pedidos entregues.
2. Valor de frete de pedidos entregues.
3. Valor bruto de pedidos entregues.
4. Valor pago registrado em pedidos entregues.
5. Diferença de reconciliação financeira.
6. Valor médio por pedido entregue, com medida-base explícita.
7. Participação do frete no valor bruto.
8. Crescimento mensal do valor dos itens.
9. Taxa de cancelamento por quantidade.
10. Valor associado a pedidos cancelados.

### 11.2. Vendedores

11. Vendedores ativos.
12. Valor dos itens por vendedor.
13. Participação financeira por vendedor.
14. Participação acumulada dos maiores vendedores.
15. Pedidos com participação do vendedor.
16. Itens por vendedor.
17. Valor médio do vendedor por pedido com participação.
18. Taxa de itens enviados após o limite.
19. Taxa de pedidos atrasados associados ao vendedor.
20. Nota média dos pedidos associados ao vendedor.

O catálogo é preliminar. A exploração deve validar disponibilidade, qualidade,
distribuição e utilidade antes de promover uma métrica a estrutura persistente
ou KPI de consumo.

## 12. Limitações

### 12.1. Financeiras

O dataset não contém custos dos produtos, comissões, impostos, descontos
explicitamente separados, tarifas de pagamento, custos logísticos reais,
estornos completos, margem ou lucro. Valores registrados não comprovam
liquidação contábil.

### 12.2. Temporais

Os dados representam um período histórico encerrado. Não permitem monitoramento
em tempo real e não representam a operação atual. Meses incompletos devem ser
identificados antes de comparações ou cálculos de crescimento.

### 12.3. Vendedores

Um pedido pode envolver vários vendedores. Pagamentos e avaliações pertencem ao
pedido. O atraso final também pode depender de fatores não representados. Não há
custos, contratos, comissões ou metas individuais.

### 12.4. Clientes e mercado

Somente clientes com transações observadas estão presentes. Não há visitantes,
abandono, conversão ou dimensão completa do mercado. Participação no dataset não
equivale a participação de mercado.

### 12.5. Logística e geografia

Não há transportadora, rota, veículo nem rastreamento detalhado. Coordenadas são
associadas a prefixos de CEP e podem possuir múltiplos registros. Distâncias
derivadas serão aproximações geográficas, não distâncias percorridas.

## 13. Convenções de nomenclatura

| Evitar | Utilizar |
|---|---|
| Receita | Valor dos itens ou valor movimentado, com definição |
| Faturamento | Valor bruto dos pedidos |
| Lucro | Não disponível |
| Rentabilidade do vendedor | Desempenho financeiro do vendedor |
| Ticket médio do vendedor | Valor médio do vendedor por pedido com participação |
| Custo de frete | Valor de frete cobrado |
| Vendas concluídas | Pedidos entregues |
| Atraso do vendedor | Pedido atrasado associado ao vendedor |
| Cliente ativo | Cliente com pedido no período, quando definido |
| Participação de mercado | Participação no valor observado no dataset |

## 14. Regras de qualidade analítica

Toda métrica consolidada deve informar, quando aplicável:

- nome e objetivo;
- fórmula e unidade;
- granularidade;
- data de referência;
- filtros e status incluídos;
- regras de inclusão e exclusão;
- dimensões permitidas;
- tabelas e colunas de origem;
- interpretação e limitações.

Toda consulta financeira deve:

- declarar a granularidade final;
- agregar pagamentos antes de combiná-los com itens;
- contar pedidos distintos após joins 1:N;
- impedir a repetição de valores de pedido por item ou pagamento;
- declarar se utiliza todos os pedidos ou apenas entregues;
- possuir consulta de controle;
- separar medidas observadas de medidas alocadas.

## 15. Rastreabilidade com os requisitos aprovados

| Demanda deste contrato | Requisito existente | Evidência futura |
|---|---|---|
| Desempenho financeiro multidimensional | RF03 | Queries financeiras e estruturas de consumo |
| Desempenho de produtos, categorias e vendedores | RF05 | Queries e catálogo de vendedores |
| Formas, valores e condições de pagamento | RF06 | Análise de pagamentos e parcelamento |
| Análises geográficas | RF09 | Recortes de origem e alcance |
| Consumo por BI | RF12 | Views, marts ou consultas de exportação justificadas |
| Preservação de granularidade | Regra aprovada de joins analíticos | Consultas de controle e validação |

## 16. Impacto no fluxo M06

- M06-01 deve explorar a CORE a partir das perguntas priorizadas neste contrato.
- M06-02 deve combinar entidades para responder aos casos de uso aprovados.
- M06-03 deve validar a cobertura dos requisitos e registrar evidências.
- M06-04 deve validar e consolidar o catálogo preliminar de métricas.
- M06-05 deve persistir somente regras reutilizáveis e semanticamente estáveis.
- M06-06 deve preparar datasets com nomes, granularidade e métricas explícitos.

O contrato pode ser refinado durante essas entregas. Qualquer mudança deve
registrar a evidência, a decisão e o impacto sobre consultas, métricas e
estruturas já produzidas.
