# Mapeamento de Dados RAW → CORE

## 1. Objetivo

Este documento define a correspondência entre as colunas preservadas no schema
`raw` e as colunas do modelo relacional no schema `core`.

O mapeamento deriva do contrato de ingestão RAW, do modelo lógico aprovado e do
DDL PostgreSQL consolidado. Ele descreve destinos, renomeações, conversões de
tipo, nulabilidade, derivações e dependências, sem implementar a carga e sem
antecipar as regras operacionais de qualidade da etapa M05-03.

## 2. Convenções de transformação

As regras a seguir são comuns aos mapeamentos:

- os valores da RAW são `text` e devem ser convertidos explicitamente para o
  tipo físico do CORE;
- campos vazios já representados como `NULL` na RAW permanecem `NULL` quando o
  destino admite ausência;
- identificadores de 32 caracteres permanecem textuais e não são convertidos
  para `uuid`;
- prefixos de CEP são convertidos para `character(5)` sem perda de zeros à
  esquerda;
- valores monetários usam `numeric(12,2)`, sem ponto flutuante;
- datas usam `timestamp without time zone`, pois a fonte não declara fuso;
- conversões inválidas, violações de domínio, rejeições e contabilização de
  exceções serão especificadas na M05-03; nenhum valor deve ser corrigido ou
  descartado silenciosamente;
- os metadados `_id_raw`, `_arquivo_origem` e `_carregado_em` não possuem
  destino no CORE e permanecem disponíveis para rastreabilidade da ingestão.

## 3. Divergências identificadas entre artefatos aprovados

O cruzamento dos artefatos revelou duas divergências documentais:

- o modelo lógico e o DDL usam `core.pedido.data_estimada`, enquanto o
  dicionário em `physical_model.tex` apresenta `data_entrega_estimada`;
- o DDL define `produto.comprimento_cm`, `produto.altura_cm` e
  `produto.largura_cm` como `smallint`, enquanto o dicionário em LaTeX os
  descreve como `integer`.

Este mapeamento adota os nomes e tipos do DDL, pois ele materializa a estrutura
validada no PostgreSQL e, nesses pontos, permanece consistente com o modelo
lógico. A divergência fica registrada para correção documental controlada e não
altera o schema físico durante a carga.

## 4. Resumo de cobertura

| Categoria | Quantidade | Tratamento |
|---|---:|---|
| Colunas CORE com origem direta | 48 | Renomeação e conversão explícita |
| Coluna CORE derivada | 1 | `core.prefixo_cep.prefixo_cep` |
| Coluna CORE gerada | 1 | `core.geolocalizacao.id_geolocalizacao` |
| Colunas de negócio sem destino no CORE | 4 | Permanecem na RAW |
| Metadados técnicos sem destino no CORE | 27 | Três por tabela RAW |

## 5. Mapeamento por tabela

### 5.1 `raw.olist_customers` → `core.cliente`

Granularidade preservada: uma ocorrência de cliente associada ao pedido.

| Origem RAW | Destino CORE | Tipo CORE | Nulo | Transformação prevista |
|---|---|---|---|---|
| `customer_id` | `id_cliente` | `varchar(32)` | Não | Conversão textual; validar 32 hexadecimais; PK |
| `customer_unique_id` | `id_cliente_unico` | `varchar(32)` | Não | Conversão textual; validar 32 hexadecimais; repetição permitida |
| `customer_zip_code_prefix` | `prefixo_cep` | `char(5)` | Não | Preservar cinco dígitos e zeros à esquerda; FK |
| `customer_city` | `cidade` | `varchar(50)` | Não | Conversão textual; validar texto não vazio e tamanho |
| `customer_state` | `estado` | `char(2)` | Não | Conversão textual; validar domínio de UF |

O `prefixo_cep` correspondente deve existir antes em `core.prefixo_cep`.

### 5.2 `raw.olist_orders` → `core.pedido`

Granularidade preservada: um pedido.

| Origem RAW | Destino CORE | Tipo CORE | Nulo | Transformação prevista |
|---|---|---|---|---|
| `order_id` | `id_pedido` | `varchar(32)` | Não | Conversão textual; validar identificador; PK |
| `customer_id` | `id_cliente` | `varchar(32)` | Não | Conversão textual; FK e `UNIQUE` |
| `order_status` | `status_pedido` | `varchar(20)` | Não | Validar domínio aprovado de oito estados |
| `order_purchase_timestamp` | `data_compra` | `timestamp without time zone` | Não | Conversão temporal estrita |
| `order_approved_at` | `data_aprovacao` | `timestamp without time zone` | Sim | Conversão temporal; preservar ausência |
| `order_delivered_carrier_date` | `data_envio_transportador` | `timestamp without time zone` | Sim | Conversão temporal; preservar ausência |
| `order_delivered_customer_date` | `data_entrega` | `timestamp without time zone` | Sim | Conversão temporal; preservar ausência |
| `order_estimated_delivery_date` | `data_estimada` | `timestamp without time zone` | Não | Conversão temporal estrita |

O cliente referenciado deve ser carregado antes do pedido. Não são impostas
comparações temporais universais adicionais entre os eventos do pedido.

### 5.3 `raw.olist_order_items` → `core.item_pedido`

Granularidade preservada: um item dentro de um pedido.

| Origem RAW | Destino CORE | Tipo CORE | Nulo | Transformação prevista |
|---|---|---|---|---|
| `order_id` | `id_pedido` | `varchar(32)` | Não | Conversão textual; parte da PK e FK |
| `order_item_id` | `id_item` | `smallint` | Não | Conversão inteira; validar valor positivo; parte da PK |
| `product_id` | `id_produto` | `varchar(32)` | Não | Conversão textual; FK |
| `seller_id` | `id_vendedor` | `varchar(32)` | Não | Conversão textual; FK |
| `shipping_limit_date` | `data_limite_envio` | `timestamp without time zone` | Não | Conversão temporal estrita |
| `price` | `preco_item` | `numeric(12,2)` | Não | Conversão decimal exata; validar valor não negativo |
| `freight_value` | `valor_frete` | `numeric(12,2)` | Não | Conversão decimal exata; validar valor não negativo |

Pedido, produto e vendedor devem existir antes da carga dos itens.

### 5.4 `raw.olist_products` → `core.produto`

Granularidade preservada: um produto.

| Origem RAW | Destino CORE | Tipo CORE | Nulo | Transformação prevista |
|---|---|---|---|---|
| `product_id` | `id_produto` | `varchar(32)` | Não | Conversão textual; validar identificador; PK |
| `product_category_name` | `nome_categoria` | `varchar(50)` | Sim | Preservar categoria original em português e ausência |
| `product_name_lenght` | `comprimento_nome` | `smallint` | Sim | Conversão inteira; validar valor não negativo |
| `product_description_lenght` | `comprimento_descricao` | `smallint` | Sim | Conversão inteira; validar valor não negativo |
| `product_photos_qty` | `quantidade_fotos` | `smallint` | Sim | Conversão inteira; validar valor não negativo |
| `product_weight_g` | `peso_g` | `integer` | Sim | Conversão inteira; validar valor não negativo |
| `product_length_cm` | `comprimento_cm` | `smallint` | Sim | Conversão inteira; validar valor não negativo |
| `product_height_cm` | `altura_cm` | `smallint` | Sim | Conversão inteira; validar valor não negativo |
| `product_width_cm` | `largura_cm` | `smallint` | Sim | Conversão inteira; validar valor não negativo |

Os quatro atributos descritivos ausentes em 610 produtos e as duas ausências
nas medidas físicas permanecem `NULL`; não recebem zero ou valor padrão.

### 5.5 `raw.olist_sellers` → `core.vendedor`

Granularidade preservada: um vendedor.

| Origem RAW | Destino CORE | Tipo CORE | Nulo | Transformação prevista |
|---|---|---|---|---|
| `seller_id` | `id_vendedor` | `varchar(32)` | Não | Conversão textual; validar identificador; PK |
| `seller_zip_code_prefix` | `prefixo_cep` | `char(5)` | Não | Preservar cinco dígitos e zeros à esquerda; FK |
| `seller_city` | `cidade` | `varchar(50)` | Não | Conversão textual; validar texto não vazio e tamanho |
| `seller_state` | `estado` | `char(2)` | Não | Conversão textual; validar domínio de UF |

O `prefixo_cep` correspondente deve existir antes em `core.prefixo_cep`.

### 5.6 `raw.olist_order_payments` → `core.pagamento`

Granularidade preservada: uma ocorrência de pagamento dentro de um pedido.

| Origem RAW | Destino CORE | Tipo CORE | Nulo | Transformação prevista |
|---|---|---|---|---|
| `order_id` | `id_pedido` | `varchar(32)` | Não | Conversão textual; parte da PK e FK |
| `payment_sequential` | `sequencial_pagamento` | `smallint` | Não | Conversão inteira; validar valor positivo; parte da PK |
| `payment_type` | `tipo_pagamento` | `varchar(20)` | Não | Validar domínio aprovado, incluindo `not_defined` |
| `payment_installments` | `numero_parcelas` | `smallint` | Não | Conversão inteira; validar valor não negativo |
| `payment_value` | `valor_pagamento` | `numeric(12,2)` | Não | Conversão decimal exata; validar valor não negativo |

As duas ocorrências com `payment_installments = 0` são compatíveis com o
`CHECK` físico e não devem ser corrigidas ou rejeitadas apenas por esse valor.
O pedido referenciado deve existir antes do pagamento.

### 5.7 `raw.olist_order_reviews` → `core.avaliacao`

Granularidade preservada: uma avaliação associada a um pedido.

| Origem RAW | Destino CORE | Tipo CORE | Nulo | Transformação prevista |
|---|---|---|---|---|
| `review_id` | `id_avaliacao` | `varchar(32)` | Não | Conversão textual; parte da PK composta |
| `order_id` | `id_pedido` | `varchar(32)` | Não | Conversão textual; parte da PK e FK |
| `review_score` | `nota_avaliacao` | `smallint` | Não | Conversão inteira; validar intervalo de 1 a 5 |
| `review_creation_date` | `data_criacao` | `timestamp without time zone` | Não | Conversão temporal estrita |
| `review_answer_timestamp` | `data_resposta` | `timestamp without time zone` | Não | Conversão temporal estrita |

`review_comment_title` e `review_comment_message` não possuem destino no CORE
aprovado. Eles permanecem na RAW e não são descartados da arquitetura. O pedido
referenciado deve existir antes da avaliação.

### 5.8 Derivação de `core.prefixo_cep`

Granularidade: um prefixo de CEP distinto utilizado pelo domínio.

| Origem RAW | Destino CORE | Tipo CORE | Transformação prevista |
|---|---|---|---|
| `raw.olist_customers.customer_zip_code_prefix` | `prefixo_cep` | `char(5)` | Projetar prefixos válidos |
| `raw.olist_sellers.seller_zip_code_prefix` | `prefixo_cep` | `char(5)` | Projetar prefixos válidos |
| `raw.olist_geolocation.geolocation_zip_code_prefix` | `prefixo_cep` | `char(5)` | Projetar prefixos válidos |

As três projeções são combinadas por união e deduplicadas pelo próprio valor do
prefixo. O resultado deve conter somente valores de cinco dígitos e ser
carregado antes de cliente, vendedor e geolocalização.

### 5.9 `raw.olist_geolocation` → `core.geolocalizacao`

Granularidade preservada: uma ocorrência geográfica observada na fonte.

| Origem RAW | Destino CORE | Tipo CORE | Nulo | Transformação prevista |
|---|---|---|---|---|
| Sem origem | `id_geolocalizacao` | `bigint` | Não | Gerado pelo PostgreSQL como identity; PK substituta |
| `geolocation_zip_code_prefix` | `prefixo_cep` | `char(5)` | Não | Preservar cinco dígitos; FK |
| `geolocation_lat` | `latitude` | `double precision` | Não | Conversão numérica; validar intervalo global `[-90, 90]` |
| `geolocation_lng` | `longitude` | `double precision` | Não | Conversão numérica; validar intervalo global `[-180, 180]` |
| `geolocation_city` | `cidade` | `varchar(50)` | Não | Conversão textual; validar texto não vazio e tamanho |
| `geolocation_state` | `estado` | `char(2)` | Não | Conversão textual; validar domínio de UF |

O modelo físico permite múltiplas ocorrências para o mesmo prefixo. As linhas
integralmente repetidas na fonte não são eliminadas por este mapeamento: uma
eventual política de deduplicação exige regra explícita na M05-03 e reconciliação
das ocorrências afetadas.

### 5.10 `raw.product_category_name_translation`

`product_category_name` e `product_category_name_english` não possuem destino
no modelo CORE aprovado. `core.produto.nome_categoria` recebe diretamente
`raw.olist_products.product_category_name`, preservando o valor original em
português. A tradução permanece disponível na RAW para eventual estrutura
analítica futura, sem alterar silenciosamente o modelo CORE.

## 6. Ordem de carga por dependências

A ordem mínima que respeita as chaves estrangeiras é:

1. `core.prefixo_cep`;
2. `core.cliente`, `core.produto` e `core.vendedor`;
3. `core.pedido` e `core.geolocalizacao`;
4. `core.item_pedido`, `core.pagamento` e `core.avaliacao`.

Tabelas listadas na mesma etapa não possuem dependência entre si e podem ser
processadas separadamente dentro da estratégia transacional definida depois.

## 7. Controles exigidos para a implementação

A implementação posterior deve contabilizar, por tabela e regra:

- registros recebidos da RAW;
- registros convertidos com sucesso;
- registros rejeitados ou colocados em exceção;
- violações de formato, domínio, nulabilidade, chave e referência;
- efeito de qualquer deduplicação formalmente aprovada;
- contagens finais inseridas no CORE.

Nenhuma conversão com falha pode resultar em descarte silencioso. A política de
atomicidade, registro de exceções e continuidade da carga será definida nas
entregas de qualidade e implementação.

## 8. Fronteiras e decisões reservadas

Este mapeamento não define:

- a sintaxe SQL final das transformações;
- a política operacional de rejeição ou quarentena;
- correções de valores fora de formato ou domínio;
- deduplicações além da chave derivada de `core.prefixo_cep`;
- estruturas no schema `analytics`;
- materialização da tradução de categorias no CORE.

Esses pontos permanecem separados para evitar que o mapeamento altere decisões
conceituais, lógicas ou físicas já aprovadas.

## 9. Próximo passo

Com a correspondência RAW → CORE consolidada, a M05-03 deve definir e testar as
regras reproduzíveis para conversões inválidas, ausências incompatíveis,
duplicidades, violações de domínio e inconsistências referenciais.
