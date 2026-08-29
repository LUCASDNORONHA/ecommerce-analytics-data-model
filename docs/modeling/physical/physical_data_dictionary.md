# Dicionário de dados físico

## Identificação

- **Issue:** #35 — [M04-02] Definir tipos de dados e restrições
- **SGBD:** PostgreSQL 18
- **Data:** 28 de agosto de 2026
- **Base estrutural:** modelo lógico relacional aprovado

## Escopo

Este documento converte os domínios do modelo lógico em tipos concretos do
PostgreSQL e define nulabilidade, geração de valores e restrições. Ele orientará
a criação do DDL na issue #36, mas não contém o script executável.

As nove tabelas, suas granularidades e seus relacionamentos permanecem
inalterados. Nenhuma decisão física deste documento modifica silenciosamente o
modelo lógico.

## Evidência utilizada

Os nove CSVs locais em `data/raw/` foram perfilados como texto para evitar
inferência indevida de tipos. A validação considerou nulidade, comprimento,
domínio observado, mínimo, máximo, escala decimal, formato temporal e unicidade
das chaves. Os principais resultados foram:

| Domínio | Evidência observada | Decisão física |
|---|---|---|
| Identificadores da fonte | 32 caracteres hexadecimais em todas as ocorrências | `varchar(32)`, preservado como texto; não convertido para `uuid` |
| Prefixo de CEP | exatamente 5 dígitos quando lido como texto | `char(5)` com validação de cinco dígitos |
| UF | exatamente 2 caracteres; 27 valores no conjunto completo | `char(2)` com domínio das UFs brasileiras |
| Cidades | maior ocorrência com 40 caracteres | `varchar(50)` |
| Categoria de produto | maior ocorrência com 46 caracteres | `varchar(50)` |
| Valores monetários | escala máxima de 2; maior valor igual a 13.664,08 | `numeric(12,2)` |
| Contadores e dimensões | valores inteiros; maior peso igual a 40.425 g | `smallint` ou `integer`, conforme a faixa |
| Datas e horas | formato válido, sem deslocamento de fuso horário | `timestamp without time zone` |
| Coordenadas | até 20 casas na representação textual e presença de pontos fora do Brasil | `double precision`, limitado apenas às faixas globais |

O perfil também confirmou a ausência de nulos e duplicidades nas chaves
primárias lógicas. As nulabilidades observadas estão de acordo com o modelo
lógico: datas intermediárias do pedido e atributos de produto podem ser nulos.

## Convenções físicas

- nomes de tabelas, colunas e constraints usam `snake_case`;
- identificadores externos permanecem textuais e sem valor padrão;
- `numeric` é usado para valores monetários, evitando ponto flutuante;
- datas da fonte usam `timestamp without time zone`, pois os CSVs não informam
  fuso ou deslocamento UTC;
- não há valores padrão implícitos para dados de negócio;
- somente `geolocalizacao.id_geolocalizacao`, chave substituta sem coluna na
  fonte, é gerada pelo banco;
- exclusões referenciadas usam `ON DELETE RESTRICT` e atualizações usam
  `ON UPDATE NO ACTION`;
- nulabilidade é declarada explicitamente no DDL futuro;
- constraints recebem nomes estáveis para facilitar diagnóstico e manutenção.

## Tabela `cliente`

**Fonte:** `olist_customers_dataset.csv`  
**Granularidade:** uma ocorrência por `customer_id`.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `id_cliente` | `customer_id` | `varchar(32)` | não | nenhum | PK; formato hexadecimal com 32 caracteres |
| `id_cliente_unico` | `customer_unique_id` | `varchar(32)` | não | nenhum | formato hexadecimal com 32 caracteres |
| `prefixo_cep` | `customer_zip_code_prefix` | `char(5)` | não | nenhum | FK; exatamente cinco dígitos |
| `cidade` | `customer_city` | `varchar(50)` | não | nenhum | texto não vazio |
| `estado` | `customer_state` | `char(2)` | não | nenhum | UF brasileira válida |

Constraints de tabela:

- `pk_cliente` em (`id_cliente`);
- `fk_cliente_prefixo_cep` para `prefixo_cep(prefixo_cep)`.

## Tabela `pedido`

**Fonte:** `olist_orders_dataset.csv`  
**Granularidade:** uma ocorrência por `order_id`.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `id_pedido` | `order_id` | `varchar(32)` | não | nenhum | PK; formato hexadecimal com 32 caracteres |
| `id_cliente` | `customer_id` | `varchar(32)` | não | nenhum | FK; `UNIQUE`; formato hexadecimal com 32 caracteres |
| `status_pedido` | `order_status` | `varchar(20)` | não | nenhum | um dos estados de pedido documentados |
| `data_compra` | `order_purchase_timestamp` | `timestamp without time zone` | não | nenhum | data e hora válidas |
| `data_aprovacao` | `order_approved_at` | `timestamp without time zone` | sim | nenhum | — |
| `data_envio_transportador` | `order_delivered_carrier_date` | `timestamp without time zone` | sim | nenhum | — |
| `data_entrega` | `order_delivered_customer_date` | `timestamp without time zone` | sim | nenhum | — |
| `data_estimada` | `order_estimated_delivery_date` | `timestamp without time zone` | não | nenhum | data e hora válidas |

Constraints de tabela:

- `pk_pedido` em (`id_pedido`);
- `uq_pedido_id_cliente` em (`id_cliente`), preservando a cardinalidade lógica;
- `fk_pedido_cliente` para `cliente(id_cliente)`;
- `ck_pedido_status` limitado a `approved`, `canceled`, `created`, `delivered`,
  `invoiced`, `processing`, `shipped` e `unavailable`.

Não são impostas comparações entre datas. Pedidos cancelados ou indisponíveis
podem não percorrer todas as etapas, e a qualidade de sequências temporais será
tratada na carga sem transformar observações da fonte em regra universal.

## Tabela `item_pedido`

**Fonte:** `olist_order_items_dataset.csv`  
**Granularidade:** um item numerado dentro de um pedido.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `id_pedido` | `order_id` | `varchar(32)` | não | nenhum | parte da PK; FK; formato hexadecimal com 32 caracteres |
| `id_item` | `order_item_id` | `smallint` | não | nenhum | parte da PK; maior que zero |
| `id_produto` | `product_id` | `varchar(32)` | não | nenhum | FK; formato hexadecimal com 32 caracteres |
| `id_vendedor` | `seller_id` | `varchar(32)` | não | nenhum | FK; formato hexadecimal com 32 caracteres |
| `data_limite_envio` | `shipping_limit_date` | `timestamp without time zone` | não | nenhum | data e hora válidas |
| `preco_item` | `price` | `numeric(12,2)` | não | nenhum | maior ou igual a zero |
| `valor_frete` | `freight_value` | `numeric(12,2)` | não | nenhum | maior ou igual a zero |

Constraints de tabela:

- `pk_item_pedido` em (`id_pedido`, `id_item`);
- `fk_item_pedido_pedido` para `pedido(id_pedido)`;
- `fk_item_pedido_produto` para `produto(id_produto)`;
- `fk_item_pedido_vendedor` para `vendedor(id_vendedor)`;
- `ck_item_pedido_id_item_positivo`, `ck_item_pedido_preco_nao_negativo` e
  `ck_item_pedido_frete_nao_negativo`.

## Tabela `produto`

**Fonte:** `olist_products_dataset.csv`  
**Granularidade:** uma ocorrência por `product_id`.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `id_produto` | `product_id` | `varchar(32)` | não | nenhum | PK; formato hexadecimal com 32 caracteres |
| `nome_categoria` | `product_category_name` | `varchar(50)` | sim | nenhum | texto não vazio quando informado |
| `comprimento_nome` | `product_name_lenght` | `smallint` | sim | nenhum | maior ou igual a zero |
| `comprimento_descricao` | `product_description_lenght` | `smallint` | sim | nenhum | maior ou igual a zero |
| `quantidade_fotos` | `product_photos_qty` | `smallint` | sim | nenhum | maior ou igual a zero |
| `peso_g` | `product_weight_g` | `integer` | sim | nenhum | maior ou igual a zero |
| `comprimento_cm` | `product_length_cm` | `smallint` | sim | nenhum | maior ou igual a zero |
| `altura_cm` | `product_height_cm` | `smallint` | sim | nenhum | maior ou igual a zero |
| `largura_cm` | `product_width_cm` | `smallint` | sim | nenhum | maior ou igual a zero |

Constraints de tabela:

- `pk_produto` em (`id_produto`);
- checks não negativos individuais para comprimentos, quantidade, peso e
  dimensões quando os valores estiverem presentes.

Os 610 nulos simultâneos nos atributos descritivos e os dois nulos nas medidas
físicas são preservados; não há preenchimento padrão capaz de representar seu
significado sem inventar dados.

## Tabela `vendedor`

**Fonte:** `olist_sellers_dataset.csv`  
**Granularidade:** uma ocorrência por `seller_id`.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `id_vendedor` | `seller_id` | `varchar(32)` | não | nenhum | PK; formato hexadecimal com 32 caracteres |
| `prefixo_cep` | `seller_zip_code_prefix` | `char(5)` | não | nenhum | FK; exatamente cinco dígitos |
| `cidade` | `seller_city` | `varchar(50)` | não | nenhum | texto não vazio |
| `estado` | `seller_state` | `char(2)` | não | nenhum | UF brasileira válida |

Constraints de tabela:

- `pk_vendedor` em (`id_vendedor`);
- `fk_vendedor_prefixo_cep` para `prefixo_cep(prefixo_cep)`.

## Tabela `pagamento`

**Fonte:** `olist_order_payments_dataset.csv`  
**Granularidade:** uma sequência de pagamento dentro de um pedido.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `id_pedido` | `order_id` | `varchar(32)` | não | nenhum | parte da PK; FK; formato hexadecimal com 32 caracteres |
| `sequencial_pagamento` | `payment_sequential` | `smallint` | não | nenhum | parte da PK; maior que zero |
| `tipo_pagamento` | `payment_type` | `varchar(20)` | não | nenhum | um dos meios documentados na fonte |
| `numero_parcelas` | `payment_installments` | `smallint` | não | nenhum | maior ou igual a zero |
| `valor_pagamento` | `payment_value` | `numeric(12,2)` | não | nenhum | maior ou igual a zero |

Constraints de tabela:

- `pk_pagamento` em (`id_pedido`, `sequencial_pagamento`);
- `fk_pagamento_pedido` para `pedido(id_pedido)`;
- `ck_pagamento_tipo` limitado a `boleto`, `credit_card`, `debit_card`,
  `not_defined` e `voucher`;
- checks para sequência positiva, parcelas não negativas e valor não negativo.

O valor zero de `numero_parcelas` é mantido porque existe na fonte e pode
representar meios sem parcelamento; não será corrigido silenciosamente para um.

## Tabela `avaliacao`

**Fonte:** `olist_order_reviews_dataset.csv`  
**Granularidade:** uma ocorrência identificada pelo par de avaliação e pedido.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `id_avaliacao` | `review_id` | `varchar(32)` | não | nenhum | parte da PK; formato hexadecimal com 32 caracteres |
| `id_pedido` | `order_id` | `varchar(32)` | não | nenhum | parte da PK; FK; formato hexadecimal com 32 caracteres |
| `nota_avaliacao` | `review_score` | `smallint` | não | nenhum | entre 1 e 5 |
| `data_criacao` | `review_creation_date` | `timestamp without time zone` | não | nenhum | data e hora válidas |
| `data_resposta` | `review_answer_timestamp` | `timestamp without time zone` | não | nenhum | data e hora válidas |

Constraints de tabela:

- `pk_avaliacao` em (`id_avaliacao`, `id_pedido`);
- `fk_avaliacao_pedido` para `pedido(id_pedido)`;
- `ck_avaliacao_nota` entre 1 e 5.

Os campos de título e mensagem da avaliação existentes no CSV não pertencem ao
modelo lógico aprovado e, portanto, não são introduzidos nesta etapa.

## Tabela `prefixo_cep`

**Fonte derivada:** união dos prefixos presentes em clientes, vendedores e
geolocalizações.  
**Granularidade:** um prefixo de CEP brasileiro com cinco dígitos.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `prefixo_cep` | prefixos das três fontes | `char(5)` | não | nenhum | PK; exatamente cinco dígitos |

Constraint de tabela:

- `pk_prefixo_cep` em (`prefixo_cep`).

O pipeline de carga deverá ler os prefixos como texto e completar zeros à
esquerda quando uma ferramenta intermediária os tiver interpretado como número.

## Tabela `geolocalizacao`

**Fonte:** `olist_geolocation_dataset.csv`  
**Granularidade:** uma ocorrência geográfica da fonte; um prefixo pode possuir
várias ocorrências.

| Coluna | Coluna de origem | Tipo PostgreSQL | Nulo | Padrão/geração | Restrições |
|---|---|---|---|---|---|
| `id_geolocalizacao` | sem equivalente | `bigint` | não | `GENERATED ALWAYS AS IDENTITY` | PK |
| `prefixo_cep` | `geolocation_zip_code_prefix` | `char(5)` | não | nenhum | FK; exatamente cinco dígitos |
| `latitude` | `geolocation_lat` | `double precision` | não | nenhum | entre -90 e 90 |
| `longitude` | `geolocation_lng` | `double precision` | não | nenhum | entre -180 e 180 |
| `cidade` | `geolocation_city` | `varchar(50)` | não | nenhum | texto não vazio |
| `estado` | `geolocation_state` | `char(2)` | não | nenhum | UF brasileira válida |

Constraints de tabela:

- `pk_geolocalizacao` em (`id_geolocalizacao`);
- `fk_geolocalizacao_prefixo_cep` para `prefixo_cep(prefixo_cep)`;
- `ck_geolocalizacao_latitude` e `ck_geolocalizacao_longitude` para os limites
  globais das coordenadas.

Foram observadas latitudes entre aproximadamente -36,61 e 45,07 e longitudes
entre -101,47 e 121,11. Embora algumas ocorrências estejam fora do território
brasileiro, elas são coordenadas globais válidas. A modelagem física não as
descartará nem imporá limites brasileiros; a qualidade geográfica será tratada
explicitamente na etapa de carga.

## Checks reutilizados no DDL

Para evitar interpretações diferentes na implementação, os formatos comuns
deverão corresponder às seguintes expressões:

- identificador externo: `VALUE ~ '^[0-9a-f]{32}$'`;
- prefixo de CEP: `VALUE ~ '^[0-9]{5}$'`;
- texto obrigatório: `btrim(VALUE) <> ''`;
- UF válida: `VALUE IN ('AC', 'AL', 'AM', 'AP', 'BA', 'CE', 'DF', 'ES', 'GO',
  'MA', 'MG', 'MS', 'MT', 'PA', 'PB', 'PE', 'PI', 'PR', 'RJ', 'RN', 'RO',
  'RR', 'RS', 'SC', 'SE', 'SP', 'TO')`.

No DDL, cada check terá nome associado à sua tabela e coluna; não serão criados
domínios globais nesta fase para evitar acoplamento adicional não previsto no
modelo lógico.

## Mapeamento consolidado dos domínios lógicos

| Domínio lógico | Tipo físico PostgreSQL | Observação |
|---|---|---|
| `identificador` externo | `varchar(32)` | texto hexadecimal preservado da fonte |
| `identificador` substituto | `bigint generated always as identity` | somente em `geolocalizacao` |
| `prefixo_postal` | `char(5)` | cinco dígitos, incluindo zeros à esquerda |
| `sigla_uf` | `char(2)` | domínio das UFs brasileiras |
| `texto` | `varchar(20)` ou `varchar(50)` | tamanho definido pela semântica e pelo perfil |
| `inteiro` | `smallint` ou `integer` | faixa escolhida por coluna |
| `valor_monetario` | `numeric(12,2)` | precisão exata e escala de centavos |
| `data_hora` | `timestamp without time zone` | fonte sem informação de fuso |
| `coordenada_geografica` | `double precision` | cálculo e representação de coordenadas |

## Decisões postergadas

Permanecem para as tarefas seguintes:

- sintaxe e ordem completas do DDL;
- estratégia de índices além dos criados implicitamente por PK e `UNIQUE`;
- execução do esquema em uma instância PostgreSQL;
- configuração da conexão no DBeaver;
- tratamento e carga dos dados;
- regras de qualidade que não constituem integridade estrutural do domínio.

## Referências

- [Decisão técnica do SGBD](database_selection.md)
- [Modelo lógico aprovado](../../../models/logical/logical_schema.dbml)
- [Tipos de dados do PostgreSQL 18](https://www.postgresql.org/docs/18/datatype.html)
- [Constraints do PostgreSQL 18](https://www.postgresql.org/docs/18/ddl-constraints.html)
- [Colunas identity do PostgreSQL 18](https://www.postgresql.org/docs/18/ddl-identity-columns.html)
