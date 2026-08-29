# Regras de Qualidade e Saneamento RAW → CORE

## 1. Objetivo

Este documento define as regras reproduzíveis de qualidade aplicadas entre os
schemas `raw` e `core`. As regras complementam o contrato de ingestão e o
mapeamento de colunas, sem alterar os CSVs de origem nem flexibilizar as
constraints do modelo físico aprovado.

O notebook `02_raw_to_core_quality_validation.ipynb` executa as regras sobre o
snapshot local do dataset e constitui a evidência empírica desta especificação.

## 2. Princípios

- a RAW permanece imutável depois de uma ingestão aprovada;
- nenhuma inconsistência é corrigida ou descartada silenciosamente;
- conversões são explícitas, determinísticas e compatíveis com o DDL;
- ausências aceitas pelo CORE permanecem `NULL` e não recebem valores padrão;
- valores válidos incomuns são preservados;
- cada violação bloqueante deve ser contabilizada e associada à regra que
  falhou;
- a publicação do CORE é atômica: violações bloqueantes impedem o `COMMIT` da
  nova versão;
- transformações que alteram quantidade de linhas exigem reconciliação própria.

## 3. Classificação e tratamento

| Classificação | Significado | Tratamento |
|---|---|---|
| Bloqueante | O valor não pode satisfazer o modelo físico ou sua integridade | Registrar exceção, interromper a publicação e preservar o CORE anterior |
| Transformação | Alteração aprovada e reproduzível entre RAW e CORE | Aplicar deterministicamente e reconciliar entradas e saídas |
| Informativa | Característica válida, ausência permitida ou dado fora do escopo CORE | Preservar o valor aplicável e registrar a ocorrência |

Um registro com falha bloqueante não deve ser simplesmente omitido de um
`INSERT`. A execução deve registrar no mínimo: identificação da carga, tabela e
arquivo de origem, `_id_raw`, coluna, valor original, identificador da regra,
motivo e instante da validação.

## 4. Regras bloqueantes comuns

### 4.1 Nulabilidade

- colunas `NOT NULL` do CORE não aceitam ausência na origem;
- campos vazios convertidos em `NULL` pela ingestão seguem a mesma regra;
- colunas anuláveis de produto e eventos temporais anuláveis de pedido preservam
  a ausência.

### 4.2 Identificadores

- identificadores provenientes da fonte devem corresponder a
  `^[0-9a-f]{32}$`;
- identificadores permanecem textuais e não são convertidos para `uuid`;
- PKs simples e compostas devem ser únicas na granularidade aprovada;
- `customer_unique_id` não é PK e pode se repetir;
- `review_id` não é globalmente único; a chave de avaliação é
  (`review_id`, `order_id`).

### 4.3 Prefixos de CEP

- o formato válido é `^[0-9]{5}$`;
- zeros à esquerda devem ser preservados;
- não se converte o prefixo para inteiro em nenhuma etapa intermediária;
- `core.prefixo_cep` é derivada pela união distinta dos prefixos de clientes,
  vendedores e geolocalização.

### 4.4 Textos e domínios

- cidades devem ser não vazias após `btrim` e possuir no máximo 50 caracteres;
- categorias não nulas devem ser não vazias e possuir no máximo 50 caracteres;
- UFs devem pertencer ao domínio das 27 unidades federativas brasileiras;
- status de pedido aceitos: `approved`, `canceled`, `created`, `delivered`,
  `invoiced`, `processing`, `shipped` e `unavailable`;
- tipos de pagamento aceitos: `boleto`, `credit_card`, `debit_card`,
  `not_defined` e `voucher`.

Não são aplicadas correções automáticas de caixa, acentuação, espaços ou
categorias. Um valor fora do domínio é uma exceção, não uma autorização para
alterar o dado.

### 4.5 Datas e horas

- valores não nulos devem corresponder ao formato `%Y-%m-%d %H:%M:%S`;
- a conversão produz `timestamp without time zone`;
- datas ausentes permitidas continuam `NULL`;
- não são impostas comparações temporais universais além das constraints físicas
  aprovadas.

### 4.6 Números e valores monetários

- inteiros devem conter somente dígitos e caber no tipo físico de destino;
- `id_item` e `sequencial_pagamento` devem ser maiores que zero;
- medidas, contagens, parcelas e valores monetários não podem ser negativos;
- notas de avaliação devem estar entre 1 e 5;
- valores monetários aceitam no máximo duas casas decimais e são convertidos
  para `numeric(12,2)`;
- coordenadas devem ser conversíveis e permanecer nos limites globais:
  latitude `[-90,90]` e longitude `[-180,180]`.

### 4.7 Integridade referencial

Devem ser verificadas antes da inserção:

- pedido → cliente;
- item do pedido → pedido, produto e vendedor;
- pagamento → pedido;
- avaliação → pedido;
- cliente, vendedor e geolocalização → prefixo de CEP derivado.

Referências ausentes bloqueiam a publicação do CORE. Constraints não são
desabilitadas como mecanismo de saneamento.

## 5. Transformações aprovadas

### 5.1 Conversões RAW → CORE

As conversões seguem os tipos e renomeações do documento de mapeamento. O valor
original permanece disponível na RAW. Falhas de conversão são bloqueantes e não
resultam em `NULL` artificial.

### 5.2 Consolidação de prefixos de CEP

São projetados os três atributos de prefixo da RAW, validados pelo formato de
cinco dígitos e combinados com semântica de `UNION`. O snapshot atual produz
19.177 prefixos distintos.

Essa deduplicação ocorre pela chave da entidade `prefixo_cep`; ela não elimina
linhas das tabelas de cliente, vendedor ou geolocalização.

### 5.3 Duplicidades integrais de geolocalização

O arquivo contém 261.831 ocorrências adicionais integralmente idênticas nas
cinco colunas de negócio. Para o CORE:

1. particionar pelas cinco colunas de negócio;
2. ordenar por `_id_raw` crescente;
3. manter a ocorrência com menor `_id_raw`;
4. contabilizar as demais como duplicidades consolidadas;
5. gerar `id_geolocalizacao` pelo PostgreSQL somente após a consolidação.

A regra remove apenas repetições integrais. Diferentes coordenadas, cidades ou
estados para o mesmo prefixo permanecem como ocorrências distintas, preservando
a cardinalidade do modelo aprovado.

## 6. Características válidas preservadas

| Evidência observada | Ocorrências | Tratamento |
|---|---:|---|
| Ausências em atributos anuláveis de produto | 2.448 campos | Preservar `NULL` |
| Ausências temporais anuláveis de pedido | 4.908 campos | Preservar `NULL` |
| `payment_installments = 0` | 2 registros | Preservar; valor permitido pelo `CHECK` |
| `payment_type = not_defined` | 3 registros | Preservar; valor pertencente ao domínio |
| Repetições adicionais de `customer_unique_id` | 3.345 | Preservar; atributo não é chave |
| Repetições adicionais de `review_id` | 814 | Preservar; PK é composta com pedido |
| Ausências nos campos de comentário de avaliação | 145.903 campos | Manter na RAW; campos não pertencem ao CORE |
| Produtos em categorias sem tradução | 13 produtos, 2 categorias | Manter categoria original em português |

As categorias sem tradução são `pc_gamer` e
`portateis_cozinha_e_preparadores_de_alimentos`. Como a tabela de tradução não
possui destino no CORE aprovado, essa ausência não bloqueia `core.produto`.

## 7. Resultado da validação do snapshot

Foram avaliadas 113 regras sobre os nove CSVs:

| Resultado | Valor |
|---|---:|
| Violações bloqueantes | 0 |
| Duplicidades integrais consolidadas em geolocalização | 261.831 |
| Prefixos de CEP distintos derivados | 19.177 |
| Resultado geral | APROVADO |

Os volumes esperados no CORE após as transformações são:

| Tabela CORE | Registros esperados |
|---|---:|
| `prefixo_cep` | 19.177 |
| `cliente` | 99.441 |
| `produto` | 32.951 |
| `vendedor` | 3.095 |
| `pedido` | 99.441 |
| `item_pedido` | 112.650 |
| `pagamento` | 103.886 |
| `avaliacao` | 99.224 |
| `geolocalizacao` | 738.332 |
| **Total físico entre as nove tabelas** | **1.308.197** |

O total CORE não deve ser comparado diretamente ao total RAW como se ambas as
camadas tivessem a mesma granularidade. A diferença decorre da entidade derivada
de prefixos, da consolidação documentada de geolocalização, da tabela de
tradução sem destino e das diferentes granularidades das nove entidades.

## 8. Contrato para a implementação

A futura rotina de carga deve produzir, por execução:

- contagem RAW recebida por tabela;
- contagem aprovada por cada regra bloqueante;
- exceções com o contexto mínimo definido neste documento;
- contagem de duplicidades de geolocalização consolidadas;
- contagem dos prefixos derivados;
- contagem inserida por tabela CORE;
- verificação das PKs, FKs, `UNIQUE` e `CHECK` após a carga;
- resultado final `APROVADO` ou `REPROVADO`.

Se qualquer regra bloqueante falhar, a nova versão do CORE não deve ser
publicada. A implementação deverá usar uma fronteira transacional que preserve
integralmente o estado anterior.

## 9. Fronteiras

Esta entrega não implementa:

- conexão com PostgreSQL;
- ingestão dos CSVs na RAW;
- comandos de inserção no CORE;
- estrutura definitiva de tabelas ou arquivos de exceção;
- agendamento ou observabilidade operacional;
- objetos no schema `analytics`.

Esses elementos pertencem às próximas entregas e devem consumir as regras aqui
definidas sem reinterpretá-las silenciosamente.

## 10. Próximo passo

A M05-04 deve implementar a ingestão reproduzível na RAW com configuração,
pré-validação, logs, metadados, reconciliação e controle transacional. As regras
deste documento devem permanecer testáveis e serão consumidas na implementação
posterior das transformações RAW → CORE, sem antecipar essa carga na M05-04.
