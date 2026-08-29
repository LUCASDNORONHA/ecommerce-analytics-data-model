# Contrato de Ingestão da Camada RAW

## 1. Objetivo

Este documento define o contrato técnico para ingestão dos arquivos do Brazilian E-Commerce Public Dataset by Olist na camada `raw` do PostgreSQL.

A camada RAW tem como responsabilidade preservar os dados recebidos da fonte com o mínimo de interferência possível, fornecendo rastreabilidade, reprocessamento e base confiável para as transformações posteriores em direção ao `core`.

Este documento consolida decisões já aprovadas na modelagem física e complementa essas decisões com regras operacionais de ingestão, reconciliação e recarga.

## 2. Escopo

A ingestão contempla exclusivamente os nove arquivos CSV utilizados pelo projeto:

1. `olist_customers_dataset.csv`
2. `olist_geolocation_dataset.csv`
3. `olist_order_items_dataset.csv`
4. `olist_order_payments_dataset.csv`
5. `olist_order_reviews_dataset.csv`
6. `olist_orders_dataset.csv`
7. `olist_products_dataset.csv`
8. `olist_sellers_dataset.csv`
9. `product_category_name_translation.csv`

Arquivos adicionais não devem ser ingeridos automaticamente. A inclusão de uma nova fonte exige atualização explícita deste contrato e dos artefatos físicos correspondentes.

## 3. Princípios da ingestão RAW

A ingestão deve obedecer aos seguintes princípios:

- uma tabela RAW corresponde a um arquivo de origem;
- os nomes das colunas provenientes do dataset são preservados;
- os valores da fonte são armazenados como `text`;
- não são aplicadas regras de negócio durante a ingestão;
- não são realizadas conversões para tipos do CORE durante a ingestão;
- duplicidades existentes na fonte são preservadas;
- inconsistências de domínio não devem impedir o registro na RAW;
- campos ausentes no CSV podem ser representados como `NULL`;
- valores textuais como `NA`, `null`, `None` ou equivalentes não devem ser convertidos em `NULL` por interpretação adicional da aplicação;
- cada ocorrência carregada recebe `_id_raw`;
- `_arquivo_origem` identifica o arquivo correspondente;
- `_carregado_em` registra o instante da carga.

A RAW não declara unicidade sobre os dados de negócio da fonte. `_id_raw` identifica exclusivamente a ocorrência armazenada.

## 4. Semântica de recarga

A política aprovada para recarga é **substitutiva**.

Uma nova carga válida do dataset substitui integralmente a carga RAW anterior. A ingestão não deve acumular uma segunda cópia dos mesmos arquivos sobre os registros existentes.

A substituição deve ser atômica:

1. validar previamente a presença e a estrutura dos nove arquivos;
2. iniciar uma única transação de banco de dados;
3. esvaziar as nove tabelas RAW com reinício das identidades técnicas;
4. carregar os nove arquivos;
5. executar as verificações de reconciliação;
6. efetivar a transação somente se todas as verificações forem aprovadas;
7. em qualquer falha, executar `ROLLBACK`, preservando integralmente a carga anterior.

A remoção da carga anterior não deve ser confirmada antes da conclusão bem-sucedida da nova carga.

Essa política permite que uma falha em um único arquivo não deixe a RAW em um estado parcialmente atualizado.

## 5. Contrato estrutural geral dos arquivos

Os arquivos analisados apresentam as seguintes características gerais:

- formato: CSV;
- delimitador: vírgula (`,`);
- caractere de aspas: aspas duplas (`"`);
- cabeçalho: presente;
- codificação predominante: UTF-8;
- os nomes dos arquivos e cabeçalhos devem corresponder ao inventário definido neste documento;
- linhas malformadas, erro de decodificação ou quantidade inesperada de colunas devem interromper a carga antes da substituição da RAW.

O arquivo `product_category_name_translation.csv` contém BOM UTF-8. A rotina de leitura deve tratá-lo sem incorporar o BOM ao nome da primeira coluna.

## 6. Inventário técnico da fonte

Os números desta seção representam o snapshot dos arquivos analisados para esta versão do projeto. Uma substituição intencional do dataset por outra versão exige novo profiling e atualização deste inventário.

| Arquivo | Tabela RAW | Linhas | Colunas | Tamanho aproximado | Codificação | Chave aparente / granularidade |
|---|---|---:|---:|---:|---|---|
| `olist_customers_dataset.csv` | `raw.olist_customers` | 99.441 | 5 | 8,62 MiB | UTF-8 | `customer_id` único; uma ocorrência de cliente associada ao pedido |
| `olist_geolocation_dataset.csv` | `raw.olist_geolocation` | 1.000.163 | 5 | 58,44 MiB | UTF-8 | sem chave natural de linha; múltiplas ocorrências por prefixo de CEP |
| `olist_order_items_dataset.csv` | `raw.olist_order_items` | 112.650 | 7 | 14,72 MiB | UTF-8 | (`order_id`, `order_item_id`) único; um item dentro de um pedido |
| `olist_order_payments_dataset.csv` | `raw.olist_order_payments` | 103.886 | 5 | 5,51 MiB | UTF-8 | (`order_id`, `payment_sequential`) único; uma ocorrência de pagamento do pedido |
| `olist_order_reviews_dataset.csv` | `raw.olist_order_reviews` | 99.224 | 7 | 13,78 MiB | UTF-8 | (`review_id`, `order_id`) único; uma avaliação associada a um pedido |
| `olist_orders_dataset.csv` | `raw.olist_orders` | 99.441 | 8 | 16,84 MiB | UTF-8 | `order_id` único; um pedido |
| `olist_products_dataset.csv` | `raw.olist_products` | 32.951 | 9 | 2,27 MiB | UTF-8 | `product_id` único; um produto |
| `olist_sellers_dataset.csv` | `raw.olist_sellers` | 3.095 | 4 | 0,17 MiB | UTF-8 | `seller_id` único; um vendedor |
| `product_category_name_translation.csv` | `raw.product_category_name_translation` | 71 | 2 | 0,003 MiB | UTF-8 com BOM | `product_category_name` único; uma tradução de categoria |

## 7. Contrato por arquivo

### 7.1 `olist_customers_dataset.csv`

**Destino:** `raw.olist_customers`

**Colunas esperadas:**

- `customer_id`
- `customer_unique_id`
- `customer_zip_code_prefix`
- `customer_city`
- `customer_state`

**Profiling observado:**

- 99.441 linhas;
- `customer_id`: 99.441 valores distintos, sem duplicidade;
- `customer_unique_id`: 96.096 valores distintos;
- 3.345 ocorrências adicionais de `customer_unique_id` em relação à unicidade;
- nenhum valor ausente nas cinco colunas;
- nenhuma linha integralmente duplicada.

**Interpretação para ingestão:** `customer_id` funciona como identificador aparente da ocorrência. `customer_unique_id` não deve ser tratado como chave da tabela RAW.

### 7.2 `olist_geolocation_dataset.csv`

**Destino:** `raw.olist_geolocation`

**Colunas esperadas:**

- `geolocation_zip_code_prefix`
- `geolocation_lat`
- `geolocation_lng`
- `geolocation_city`
- `geolocation_state`

**Profiling observado:**

- 1.000.163 linhas;
- 19.015 prefixos de CEP distintos;
- nenhum valor ausente;
- 261.831 linhas integralmente duplicadas;
- latitude observada entre aproximadamente -36,6054 e 45,0659;
- longitude observada entre aproximadamente -101,4668 e 121,1054.

**Interpretação para ingestão:** não existe chave natural de linha adequada na fonte. As duplicidades devem ser preservadas na RAW. Qualquer deduplicação necessária pertence ao processamento posterior.

### 7.3 `olist_order_items_dataset.csv`

**Destino:** `raw.olist_order_items`

**Colunas esperadas:**

- `order_id`
- `order_item_id`
- `product_id`
- `seller_id`
- `shipping_limit_date`
- `price`
- `freight_value`

**Profiling observado:**

- 112.650 linhas;
- 98.666 pedidos distintos;
- 21 valores distintos de `order_item_id`;
- a combinação (`order_id`, `order_item_id`) é única;
- nenhum valor ausente;
- nenhuma linha integralmente duplicada.

**Interpretação para ingestão:** a combinação (`order_id`, `order_item_id`) é a chave aparente da fonte, mas não deve ser imposta como constraint na RAW.

### 7.4 `olist_order_payments_dataset.csv`

**Destino:** `raw.olist_order_payments`

**Colunas esperadas:**

- `order_id`
- `payment_sequential`
- `payment_type`
- `payment_installments`
- `payment_value`

**Profiling observado:**

- 103.886 linhas;
- 99.440 pedidos distintos;
- a combinação (`order_id`, `payment_sequential`) é única;
- nenhum valor ausente;
- nenhuma linha integralmente duplicada;
- tipos de pagamento observados: `credit_card`, `boleto`, `voucher`, `debit_card` e `not_defined`;
- existem 2 registros com `payment_installments = 0`.

**Interpretação para ingestão:** o valor zero de parcelas e o tipo `not_defined` devem ser preservados na RAW, sem correção ou rejeição durante a ingestão.

### 7.5 `olist_order_reviews_dataset.csv`

**Destino:** `raw.olist_order_reviews`

**Colunas esperadas:**

- `review_id`
- `order_id`
- `review_score`
- `review_comment_title`
- `review_comment_message`
- `review_creation_date`
- `review_answer_timestamp`

**Profiling observado:**

- 99.224 linhas;
- 98.410 `review_id` distintos;
- 98.673 `order_id` distintos;
- `review_id` isolado não é único;
- a combinação (`review_id`, `order_id`) é única;
- 87.656 valores ausentes em `review_comment_title`;
- 58.247 valores ausentes em `review_comment_message`;
- nenhuma ausência nas demais colunas;
- notas observadas de 1 a 5;
- nenhuma linha integralmente duplicada.

**Interpretação para ingestão:** campos de comentário ausentes devem permanecer ausentes. `review_id` não deve ser utilizado isoladamente como chave de negócio.

### 7.6 `olist_orders_dataset.csv`

**Destino:** `raw.olist_orders`

**Colunas esperadas:**

- `order_id`
- `customer_id`
- `order_status`
- `order_purchase_timestamp`
- `order_approved_at`
- `order_delivered_carrier_date`
- `order_delivered_customer_date`
- `order_estimated_delivery_date`

**Profiling observado:**

- 99.441 linhas;
- `order_id` único;
- `customer_id` único no arquivo;
- nenhuma linha integralmente duplicada;
- 160 ausências em `order_approved_at`;
- 1.783 ausências em `order_delivered_carrier_date`;
- 2.965 ausências em `order_delivered_customer_date`;
- oito status observados: `approved`, `canceled`, `created`, `delivered`, `invoiced`, `processing`, `shipped` e `unavailable`.

**Interpretação para ingestão:** ausências em eventos temporais são preservadas e não devem ser preenchidas artificialmente na RAW.

### 7.7 `olist_products_dataset.csv`

**Destino:** `raw.olist_products`

**Colunas esperadas:**

- `product_id`
- `product_category_name`
- `product_name_lenght`
- `product_description_lenght`
- `product_photos_qty`
- `product_weight_g`
- `product_length_cm`
- `product_height_cm`
- `product_width_cm`

**Profiling observado:**

- 32.951 linhas;
- `product_id` único;
- 610 ausências simultâneas em `product_category_name`, `product_name_lenght`, `product_description_lenght` e `product_photos_qty`;
- 2 ausências em cada medida física (`product_weight_g`, `product_length_cm`, `product_height_cm`, `product_width_cm`);
- nenhuma linha integralmente duplicada.

**Interpretação para ingestão:** as grafias originais `lenght` presentes no dataset devem ser preservadas na RAW. Ausências não recebem valores padrão.

### 7.8 `olist_sellers_dataset.csv`

**Destino:** `raw.olist_sellers`

**Colunas esperadas:**

- `seller_id`
- `seller_zip_code_prefix`
- `seller_city`
- `seller_state`

**Profiling observado:**

- 3.095 linhas;
- `seller_id` único;
- nenhum valor ausente;
- nenhuma linha integralmente duplicada.

**Interpretação para ingestão:** `seller_id` é o identificador aparente da fonte.

### 7.9 `product_category_name_translation.csv`

**Destino:** `raw.product_category_name_translation`

**Colunas esperadas:**

- `product_category_name`
- `product_category_name_english`

**Profiling observado:**

- 71 linhas;
- ambas as colunas possuem 71 valores distintos;
- nenhum valor ausente;
- nenhuma linha integralmente duplicada;
- arquivo codificado em UTF-8 com BOM.

**Interpretação para ingestão:** o BOM deve ser tratado pela rotina de leitura sem alterar o nome da primeira coluna.

## 8. Política para campos vazios e valores ausentes

Um campo sintaticamente vazio no CSV representa ausência de valor e pode ser carregado como SQL `NULL`.

Não deve haver normalização adicional na RAW. Em especial:

- espaços não devem ser removidos automaticamente;
- caixa de texto não deve ser alterada;
- valores categóricos não devem ser corrigidos;
- números não devem ser convertidos;
- datas não devem ser interpretadas como timestamps;
- strings que pareçam marcadores de ausência não devem ser transformadas em `NULL` sem que estejam efetivamente vazias na fonte.

Conversões, padronizações e validações pertencem ao fluxo RAW → CORE.

## 9. Pré-validação dos arquivos

Antes de qualquer alteração na RAW, a rotina de ingestão deve confirmar:

- presença dos nove arquivos obrigatórios;
- nome exato de cada arquivo;
- leitura válida como CSV;
- codificação compatível com UTF-8;
- cabeçalho presente;
- quantidade esperada de colunas;
- nomes e ordem das colunas compatíveis com este contrato;
- inexistência de linhas estruturalmente malformadas.

A ausência ou falha estrutural de qualquer arquivo deve impedir o início da substituição.

## 10. Reconciliação CSV → RAW

Uma carga somente pode ser considerada aprovada quando, para cada arquivo:

- a quantidade de registros de dados no CSV for igual à quantidade de registros da respectiva tabela RAW;
- todas as linhas possuírem `_arquivo_origem` correspondente ao arquivo carregado;
- `_carregado_em` estiver preenchido em todas as linhas;
- `_id_raw` estiver preenchido e sem duplicidade;
- nenhuma coluna da fonte tiver sido omitida;
- nenhuma coluna adicional de negócio tiver sido criada na RAW;
- duplicidades presentes na fonte tiverem sido preservadas;
- não houver registros remanescentes de uma carga anterior.

Para o snapshot atualmente analisado, a quantidade total esperada após uma carga completa é de **1.550.922 registros RAW**, distribuídos entre as nove tabelas conforme o inventário deste documento.

## 11. Rastreabilidade da versão da fonte

Para permitir auditoria da carga, o profiling atual registrou os hashes SHA-256 dos arquivos analisados:

| Arquivo | SHA-256 |
|---|---|
| `olist_customers_dataset.csv` | `983a422239e1712ded753b3bf9ecf47dc73f144d306029dcfa99e70a226883d2` |
| `olist_geolocation_dataset.csv` | `b514f6fc991b9566aeba02aa5d67e2c3630f034b60a0e05aa0d082a3b66d88d6` |
| `olist_order_items_dataset.csv` | `0bc4d068c4fe38cbb01bd90e8746e3c613fe7b4baef75fab7b0e329701c3e279` |
| `olist_order_payments_dataset.csv` | `4f713964f2815dbbaa40b9488268c55aac3627bfce5aa96cf58d1f3616de3cc0` |
| `olist_order_reviews_dataset.csv` | `012b61c7593e34f51fa614efdf802b9c7056ce6aae5307ddb93236e7cfc797d7` |
| `olist_orders_dataset.csv` | `8df58ef3d2d7e9944010f7beecd9b75367f5588ec6e3c91cec19ae3345ef9ecf` |
| `olist_products_dataset.csv` | `3e6569628a17fbc75fd206ee357b59e20364b9afa90f5b6cd5b4d624c58aa9cc` |
| `olist_sellers_dataset.csv` | `1f643d2b950373b85735e7794b20986f528d7a000432e7c6f9bcbb44d0846a0e` |
| `product_category_name_translation.csv` | `a81f0d1f27b27e7293f761bc79e3ce8f348ee39c4b3ed3e49bde38f478586278` |

Os hashes não precisam ser transformados em regra rígida permanente de aceitação. Eles identificam o snapshot utilizado para esta versão do contrato. Uma alteração intencional da fonte exige novo profiling e atualização documental.

## 12. Problemas e particularidades conhecidos

As seguintes características devem ser consideradas no processamento posterior, mas não corrigidas durante a ingestão RAW:

- duplicidades integrais no arquivo de geolocalização;
- múltiplas ocorrências para um mesmo prefixo de CEP;
- coordenadas de geolocalização com valores observados fora dos limites territoriais brasileiros;
- `customer_unique_id` repetido entre diferentes ocorrências de cliente;
- `review_id` não globalmente único;
- mais de uma avaliação possível para um mesmo pedido;
- comentários de avaliações frequentemente ausentes;
- datas de aprovação, envio e entrega ausentes em parte dos pedidos;
- atributos descritivos e medidas físicas ausentes em parte dos produtos;
- `payment_installments = 0` em duas ocorrências;
- presença de `payment_type = not_defined`;
- BOM UTF-8 no arquivo de tradução de categorias.

## 13. Fronteira entre RAW e CORE

A ingestão RAW termina após a preservação e reconciliação dos arquivos de origem.

Não fazem parte deste contrato:

- conversão de identificadores para os tipos físicos do CORE;
- transformação de datas;
- conversão de valores monetários;
- normalização de CEP;
- validação de domínio de UF;
- aplicação de PKs e FKs de negócio;
- deduplicação;
- criação da tabela `core.prefixo_cep`;
- geração de `id_geolocalizacao`;
- tradução de categorias;
- regras de integridade relacional;
- regras analíticas.

Essas operações pertencem ao fluxo posterior RAW → CORE ou à camada ANALYTICS.

## 14. Critérios de aceite desta especificação

O contrato está pronto para sustentar a implementação quando:

- os nove arquivos estiverem inventariados;
- os cabeçalhos e tabelas destino estiverem definidos;
- volumes e granularidades estiverem registrados;
- chaves aparentes e exceções relevantes estiverem documentadas;
- a política de recarga substitutiva estiver definida;
- a estratégia de rollback estiver estabelecida;
- os critérios de reconciliação CSV → RAW estiverem definidos;
- não houver decisão pendente que impeça a implementação da carga.

## 15. Próximo passo

Com este contrato aprovado, a etapa seguinte é mapear as colunas e transformações
da RAW para a CORE, conforme a issue M05-02. Esse mapeamento deve:

1. relacionar cada coluna de origem ao destino físico correspondente;
2. explicitar conversões de tipos, nulabilidade e regras de saneamento previstas;
3. registrar colunas sem destino direto e atributos derivados;
4. respeitar as dependências entre as tabelas do CORE;
5. preservar a rastreabilidade das decisões e exceções identificadas neste contrato.

A implementação da ingestão RAW e das transformações RAW → CORE permanece em
entregas posteriores, após a aprovação do mapeamento e das regras de qualidade.
