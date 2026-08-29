# Arquitetura física em camadas

## Decisão

O banco PostgreSQL adotará um processo ELT organizado em três schemas:

```text
Dataset Olist → RAW → CORE → ANALYTICS → Power BI / SQL
```

## Responsabilidades

### `raw`

Recebe uma representação fiel dos nove CSVs. Existe uma tabela por arquivo, os
nomes originais das colunas são preservados e os valores da fonte são recebidos
como `text`. Falhas de conversão não impedem a ingestão nem eliminam a evidência
original.

Cada tabela adiciona somente `_id_raw`, `_arquivo_origem` e `_carregado_em` como
metadados técnicos. Campos da fonte permanecem anuláveis e não recebem regras de
negócio. A chave técnica não afirma unicidade sobre o dado original.

### `core`

Materializa as nove tabelas do modelo lógico aprovado. Renomeações, conversões,
deduplicação e validações ocorrem na transformação RAW → CORE. Tipos,
nulabilidade e constraints seguem o dicionário físico aprovado.

### `analytics`

É criado vazio durante a modelagem física. Views, marts e métricas serão
introduzidos na M06, derivados do CORE e documentados por granularidade e
finalidade.

## Fluxo

1. a etapa EL lê os CSVs e insere seus valores na RAW;
2. transformações SQL validam e convertem RAW para CORE;
3. reconciliações comparam fonte, RAW, rejeições e CORE;
4. estruturas ANALYTICS são derivadas do CORE;
5. Power BI e consumidores SQL consultam preferencialmente ANALYTICS.

## Tabelas RAW

| CSV | Tabela |
|---|---|
| `olist_customers_dataset.csv` | `raw.olist_customers` |
| `olist_geolocation_dataset.csv` | `raw.olist_geolocation` |
| `olist_order_items_dataset.csv` | `raw.olist_order_items` |
| `olist_order_payments_dataset.csv` | `raw.olist_order_payments` |
| `olist_order_reviews_dataset.csv` | `raw.olist_order_reviews` |
| `olist_orders_dataset.csv` | `raw.olist_orders` |
| `olist_products_dataset.csv` | `raw.olist_products` |
| `olist_sellers_dataset.csv` | `raw.olist_sellers` |
| `product_category_name_translation.csv` | `raw.product_category_name_translation` |

O DDL não implementa carga, transformação, estruturas analíticas ou permissões.
Essas responsabilidades permanecem nas milestones M05 e M06.

## Referências

- [Decisão do SGBD](database_selection.md)
- [Dicionário físico do CORE](physical_data_dictionary.md)
- [Modelo lógico do CORE](../../../models/logical/logical_schema.dbml)
