# Estratégia inicial de índices

## Identificação

- Issue: #37 — [M04-04] Definir índices iniciais da arquitetura física
- SGBD: PostgreSQL 18
- Data: 28 de agosto de 2026

## Objetivo

Definir o conjunto mínimo de índices físicos antes da carga, distinguindo os
índices criados por constraints daqueles que precisam ser declarados. O foco é
suportar integridade referencial e junções estruturais sem antecipar otimizações
analíticas.

## Princípios

- PostgreSQL cria índices B-tree para PKs e constraints UNIQUE;
- PostgreSQL não cria automaticamente índices nas colunas que referenciam FKs;
- uma FK está coberta quando suas colunas formam o prefixo à esquerda de um
  índice existente;
- índices adicionais aumentam armazenamento e custo de escrita;
- índices de filtros analíticos dependem de consultas e planos reais;
- ANALYTICS será avaliado quando suas views e marts forem definidos.

## Índices implícitos no CORE

| Tabela | Constraint | Colunas | Cobertura |
|---|---|---|---|
| prefixo_cep | pk_prefixo_cep | prefixo_cep | lado referenciado das FKs geográficas |
| cliente | pk_cliente | id_cliente | lado referenciado por pedido |
| produto | pk_produto | id_produto | lado referenciado por itens |
| vendedor | pk_vendedor | id_vendedor | lado referenciado por itens |
| pedido | pk_pedido | id_pedido | lado referenciado por itens, pagamentos e avaliações |
| pedido | uq_pedido_id_cliente | id_cliente | cobre a FK pedido → cliente |
| item_pedido | pk_item_pedido | id_pedido, id_item | cobre a FK item → pedido |
| pagamento | pk_pagamento | id_pedido, sequencial_pagamento | cobre a FK pagamento → pedido |
| avaliacao | pk_avaliacao | id_avaliacao, id_pedido | não cobre busca iniciada por id_pedido |
| geolocalizacao | pk_geolocalizacao | id_geolocalizacao | identidade da ocorrência |

## Índices adicionais aprovados

| Índice | Colunas | Justificativa |
|---|---|---|
| idx_cliente_prefixo_cep | core.cliente(prefixo_cep) | junção geográfica e manutenção da FK |
| idx_vendedor_prefixo_cep | core.vendedor(prefixo_cep) | junção geográfica e manutenção da FK |
| idx_item_pedido_id_produto | core.item_pedido(id_produto) | relacionamento produto → itens |
| idx_item_pedido_id_vendedor | core.item_pedido(id_vendedor) | relacionamento vendedor → itens |
| idx_avaliacao_id_pedido | core.avaliacao(id_pedido) | a PK começa por id_avaliacao e não cobre a FK isolada |
| idx_geolocalizacao_prefixo_cep | core.geolocalizacao(prefixo_cep) | agrupamento e relacionamento por CEP |

Todos usam B-tree, método padrão apropriado para igualdade, junções e manutenção
das FKs consideradas.

## Decisões por camada

### RAW

Cada tabela já possui a PK técnica em _id_raw. Nenhum índice adicional é criado
antes da implementação das transformações. Indexar todas as chaves textuais
aumentaria o custo da carga e presumiria padrões ainda não definidos. A M05
deverá avaliar índices com base nas consultas RAW → CORE e em planos reais.

### CORE

São adicionados somente os seis índices que completam a cobertura das FKs. Não
são criados índices em status, datas, UF, categoria ou tipo de pagamento sem
evidência de seletividade e padrão de consulta.

### ANALYTICS

Nenhum índice é criado porque o schema permanece vazio. Eventuais tabelas ou
materialized views serão avaliadas na M06.

## Operação

create_indexes.sql deve ser executado após create_schema.sql. O script falha se
um índice de mesmo nome já existir. drop_indexes.sql remove somente os seis
índices adicionais; índices de PK e UNIQUE permanecem vinculados às constraints.

## Validação futura

Após a carga, a estratégia deverá ser revisada com estatísticas, consultas reais
e planos de execução. Índices redundantes ou pouco utilizados devem ser
removidos.

## Referências

- [Arquitetura física em camadas](layered_architecture.md)
- [Dicionário físico do CORE](physical_data_dictionary.md)
- [Índices do PostgreSQL 18](https://www.postgresql.org/docs/18/indexes.html)
- [Foreign keys no PostgreSQL 18](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-FK)
