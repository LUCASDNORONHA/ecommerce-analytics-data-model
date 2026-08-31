# Matriz de validação dos requisitos funcionais

## 1. Finalidade

Esta matriz registra como os requisitos funcionais RF01 a RF12 são sustentados
pelo modelo CORE e pelas consultas versionadas nas etapas M06-01 e M06-02. A
validação comprova capacidade analítica e cobertura observada; não declara que
toda análise possível já foi implementada nem antecipa as estruturas de BI das
etapas posteriores.

Classificações utilizadas:

- **atendido**: há estrutura, consulta e resultado reproduzível suficientes
  para demonstrar a capacidade;
- **atendido com limitação**: a capacidade existe, mas a cobertura ou a
  interpretação é restringida pelos dados;
- **preparado para etapa futura**: a base está disponível, mas a entrega final
  pertence explicitamente a uma issue posterior.

## 2. Matriz requisito → consulta → evidência

| Requisito | Capacidade validada | Consulta ou artefato | Evidência observada | Resultado |
|---|---|---|---|---|
| RF01 | Integração de clientes, pedidos, itens, produtos, vendedores, pagamentos, avaliações e geolocalização | `queries/validation/05_cobertura_requisitos_funcionais.sql`, bloco RF01 | Pedidos se relacionam integralmente a clientes e itens a produtos e vendedores. Pagamentos, avaliações e geolocalização possuem cobertura parcial da fonte, preservada sem fabricação de registros. | Atendido com limitação |
| RF02 | Recuperação do histórico de pedidos e relações | `queries/basic/01_pedidos_por_status.sql`, `queries/validation/03_cobertura_relacoes_pedido.sql` e bloco RF02/RF04 da consulta 05 | 99.441 pedidos entre 2016-09-04 e 2018-10-17; exceções de itens e pagamentos permanecem identificáveis por status. | Atendido |
| RF03 | Análise multidimensional por período, produto, categoria, cliente, vendedor e localização | `queries/basic/09_valor_por_categoria_regiao.sql`, `queries/analysis/01_evolucao_financeira_mensal.sql`, `03_desempenho_vendedor_categoria.sql` e `04_alcance_geografico_vendedores.sql` | Resultados reproduzíveis nas granularidades mês, categoria-estado, vendedor-categoria e vendedor, com dimensões ligadas ao pedido. | Atendido |
| RF04 | Comportamento de compra a partir do histórico disponível | Bloco RF02/RF04 de `queries/validation/05_cobertura_requisitos_funcionais.sql` | O identificador persistente permite contar recorrência, intervalo de compras e máximo de pedidos por cliente observado. Não há navegação, abandono ou conversão. | Atendido com limitação |
| RF05 | Desempenho comercial de produtos, categorias e vendedores | `queries/basic/09_valor_por_categoria_regiao.sql`, `queries/analysis/02_concentracao_vendedores.sql` e `03_desempenho_vendedor_categoria.sql` | Valor, itens, pedidos, participação, ranking, concentração e recortes por categoria são calculáveis sem atribuir pagamentos ao vendedor. | Atendido |
| RF06 | Formas, valores e condições de pagamento | `queries/basic/06_composicao_pagamentos.sql` e `queries/analysis/06_perfil_pagamentos_pedido.sql` | Tipos, valores, parcelas e composição de meios de pagamento são preservados; pedidos com múltiplas sequências são agregados antes da análise. | Atendido |
| RF07 | Relação entre avaliações e demais informações do pedido | `queries/analysis/05_risco_operacional_vendedores.sql` e bloco RF07/RF08 da consulta 05 | Avaliações podem ser pré-agregadas por pedido e associadas a itens e vendedores. A associação não comprova responsabilidade ou causalidade. | Atendido com limitação |
| RF08 | Análise de datas previstas e efetivas de processamento e entrega | `queries/analysis/05_risco_operacional_vendedores.sql` e bloco RF07/RF08 da consulta 05 | Aprovação, envio, entrega, estimativa e envio após limite permitem medir cobertura e atrasos quando as datas estão disponíveis. | Atendido com limitação |
| RF09 | Análises geográficas de clientes e vendedores | `queries/analysis/04_alcance_geografico_vendedores.sql`, `queries/basic/09_valor_por_categoria_regiao.sql` e bloco RF09 da consulta 05 | Estados e cidades permitem recortes comerciais; prefixos podem ser relacionados à geolocalização quando cobertos. Coordenadas representam aproximações do prefixo, não rotas. | Atendido com limitação |
| RF10 | Combinação de entidades com integridade dos relacionamentos | `queries/validation/01_reconciliacao_financeira.sql`, `02_controle_join_itens_pagamentos.sql` e `04_granularidade_vendedor.sql` | A pré-agregação por pedido evita multiplicar itens e pagamentos; a atribuição de itens e valor aos vendedores reconciliou sem diferença. | Atendido |
| RF11 | Agregações e filtros temporais, comerciais, geográficos e de pedido | Coleções `queries/basic/` e `queries/analysis/` | Consultas filtram status, controlam meses parciais e agregam por mês, categoria, região, vendedor, pagamento e pedido. | Atendido |
| RF12 | Base estruturada para ferramentas analíticas e BI | Schemas `core` e `analytics`, contrato analítico e consultas versionadas | A CORE validada e as regras reproduzíveis formam a base de consumo. Views, marts e datasets finais serão materializados nas issues M06-05 e M06-06. | Preparado para etapa futura |

## 3. Evidências complementares da consulta de cobertura

### 3.1. Integração e cobertura

As chaves estrangeiras asseguram as relações obrigatórias. Relações opcionais
ou incompletas refletem a fonte: a ausência de pagamento, avaliação ou
geolocalização não deve ser preenchida artificialmente. A consulta registra a
quantidade relacionada e não relacionada para tornar essa cobertura auditável.

| Relação validada | Origem | Relacionados | Sem relação |
|---|---:|---:|---:|
| Item → produto e vendedor | 112.650 | 112.650 | 0 |
| Pedido → cliente | 99.441 | 99.441 | 0 |
| Pedido → pagamento | 99.441 | 99.440 | 1 |
| Pedido → avaliação | 99.441 | 98.673 | 768 |
| Prefixo de CEP → geolocalização | 19.177 | 19.015 | 162 |

### 3.2. Histórico e comportamento de clientes

O histórico usa `core.cliente.id_cliente_unico` como identidade persistente e
`core.pedido.data_compra` como referência temporal. A análise fica limitada a
clientes com transações observadas; não existem dados de sessão, visita,
abandono ou exposição comercial.

Foram observados 96.096 clientes persistentes; 2.997 (3,12%) possuem mais de um
pedido, e o máximo observado é 17 pedidos por cliente. O histórico varia de
2016-09-04 a 2018-10-17.

### 3.3. Avaliação, entrega e geografia

Avaliações e datas são associadas ao pedido somente quando disponíveis. Cidade,
estado e prefixo de CEP representam os atributos cadastrais presentes na base.
As múltiplas ocorrências de geolocalização por prefixo não devem ser ligadas
diretamente a fatos sem agregação prévia.

Entre os 99.441 pedidos, 98.673 possuem avaliação, 99.281 possuem data de
aprovação, 97.658 possuem envio ao transportador, 96.476 possuem entrega e
todos possuem estimativa. Foram observados 7.827 pedidos entregues após a data
estimada, sem atribuição causal.

A geolocalização cobre 99.163 de 99.441 registros de cliente e 3.088 de 3.095
vendedores. Os cadastros abrangem 27 estados e 4.119 cidades de clientes, além
de 23 estados e 611 cidades de vendedores.

## 4. Decisões e impacto nas próximas etapas

- RF01 a RF11 possuem cobertura suficiente para prosseguir à definição formal
  das métricas, respeitadas as limitações registradas.
- RF04 não autoriza métricas de conversão, abandono ou navegação.
- RF07 e RF08 sustentam indicadores associados ao vendedor, mas não atribuição
  causal de avaliações ou atraso final.
- RF09 não sustenta distância percorrida nem cobertura logística formal.
- RF12 somente será classificado como entrega final após a criação das
  estruturas reutilizáveis e dos datasets de consumo das issues M06-05 e
  M06-06.
- Nenhuma evidência exige alterar os modelos conceitual, lógico, físico ou a
  transformação CORE já aprovados.

## 5. Reprodutibilidade

As evidências devem ser reproduzidas no PostgreSQL 18 sobre a CORE aprovada,
executando as consultas referenciadas nesta matriz. As contagens documentadas
correspondem à carga local validada e podem variar somente se a fonte ou o ELT
forem formalmente alterados.
