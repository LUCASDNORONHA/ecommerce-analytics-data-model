# Instruções para agentes

## Objetivo do projeto

Este repositório desenvolve um modelo de dados relacional para sustentar análises multidimensionais de e-commerce usando o Brazilian E-Commerce Public Dataset by Olist.

O modelo integra dados de clientes, pedidos, itens, produtos, vendedores, pagamentos, avaliações e geolocalização, permitindo análises comerciais, comportamentais, financeiras, geográficas e relacionadas ao processo de entrega.

O desenvolvimento segue uma sequência progressiva de etapas:

1. análise de requisitos;
2. entendimento e validação dos dados;
3. modelagem conceitual;
4. modelagem lógica;
5. modelagem física;
6. implementação do banco de dados;
7. carga e preparação dos dados;
8. consultas e análises;
9. construção da camada analítica e preparação para consumo em BI.

A análise de requisitos, as modelagens conceitual, lógica e física, a implementação do banco de dados e o processo de carga e preparação dos dados estão concluídos e constituem a base aprovada para as etapas seguintes.

A arquitetura física foi implementada e validada no PostgreSQL 18 utilizando os schemas `raw`, `core` e `analytics`. O processo ELT também está concluído e validado, contemplando preparação do banco, ingestão dos arquivos de origem na RAW, transformação para a CORE, reconciliação de volumes, validações de integridade e regras de qualidade.

A etapa atualmente em desenvolvimento é a **Camada Analítica e Extração de Inteligência**, com foco na exploração do modelo CORE, desenvolvimento de consultas SQL, definição de métricas, validação dos requisitos analíticos, criação de estruturas de consumo no schema `analytics` e preparação dos dados para utilização em ferramentas de Business Intelligence.

Consulte o GitHub Project nº 6 antes de iniciar qualquer tarefa.

Antes de iniciar trabalho, confirme no GitHub Project qual issue está efetivamente marcada como **Em Andamento** e utilize a issue ativa para determinar objetivo, escopo, dependências, artefatos esperados e critérios de aceitação.

## Fontes de verdade

As fontes devem ser consultadas nesta ordem de responsabilidade:

- **GitHub Project nº 6:** prioridade, status e ordem de execução;
- **issue ativa:** contexto, objetivo, escopo, dependências, artefatos esperados e critérios de aceitação;
- **repositório:** código, notebooks, modelos e documentação já aprovados;
- `docs/requirements/`: requisitos e delimitação do domínio;
- `docs/modeling/conceptual/`: documentação da modelagem conceitual;
- `models/conceptual/`: artefato técnico editável do modelo conceitual;
- `docs/modeling/logical/`: documentação aprovada da modelagem lógica;
- `models/logical/`: representação técnica consolidada do modelo lógico;
- `docs/modeling/physical/`: documentação consolidada da modelagem física;
- `models/physical/`: artefatos técnicos dependentes do PostgreSQL;
- `docs/data-loading/`: documentação consolidada da carga, transformações e validação do ELT;
- `database/`: preparação e implementação da estrutura do banco;
- `elt/`: ingestão RAW, transformação CORE e orquestração do ELT;
- `validation/`: reconciliação, integridade e qualidade da carga;
- `notebooks/`: evidências empíricas versionadas;
- `tests/`: testes automatizados do projeto;
- `docs/WORKFLOW.md`: regras de gestão do trabalho;
- `CONTRIBUTING.md`: convenções de branch, commit e pull request.

O modelo conceitual aprovado deve ser tratado como referência semântica do domínio.

O modelo lógico aprovado deve ser tratado como referência estrutural, preservando tabelas, granularidade, chaves, relacionamentos, cardinalidades, restrições lógicas e decisões de normalização.

O modelo físico aprovado deve ser tratado como referência concreta da implementação no PostgreSQL, preservando schemas, tabelas, colunas, tipos, chaves, constraints e índices.

A CORE populada e validada constitui a referência de dados para as atividades analíticas. As etapas de análise não devem alterar silenciosamente decisões conceituais, lógicas, físicas ou de transformação já aprovadas.

Quando houver divergência entre requisitos, modelo conceitual, modelo lógico, modelo físico, dataset, CORE ou issue ativa, não invente uma decisão de domínio. Registre a inconsistência, apresente a evidência e preserve a rastreabilidade da decisão adotada.

## Estrutura relevante

- `data/raw/`: CSVs originais utilizados localmente e não versionados;
- `docs/requirements/`: análise de requisitos aprovada;
- `docs/modeling/conceptual/`: documentação da modelagem conceitual;
- `docs/modeling/conceptual/mer/`: representação exportada do MER utilizada na documentação;
- `docs/modeling/logical/`: documentação da modelagem lógica;
- `docs/modeling/physical/`: documentação da modelagem física;
- `docs/data-loading/`: documentação consolidada do processo de carga e transformação;
- `models/conceptual/`: fonte técnica editável do modelo conceitual;
- `models/conceptual/mer-olist-conceitual.drawio`: fonte editável do MER conceitual;
- `models/logical/`: artefatos técnicos do modelo lógico relacional;
- `models/logical/logical_schema.dbml`: representação técnica consolidada do modelo lógico;
- `models/physical/`: DDL e demais artefatos dependentes do PostgreSQL;
- `database/`: preparação da estrutura física no banco;
- `elt/`: implementação do fluxo Extract → Load → Transform;
- `elt/sql/`: SQL responsável pelas transformações RAW → CORE;
- `validation/`: validações independentes de reconciliação, integridade e qualidade;
- `config/`: contratos e configurações operacionais do ELT;
- `notebooks/data-modeling/`: evidências da modelagem;
- `notebooks/data-loading/`: evidências da carga e da qualidade dos dados;
- `tests/`: testes automatizados;
- `scripts/`: fontes Python locais pareadas por Jupytext e ignoradas pelo Git.

Não crie arquivos na raiz quando já existir um diretório próprio para o artefato.

Não duplique o mesmo artefato desnecessariamente entre `docs/`, `models/` e diretórios de implementação.

Use `docs/` para documentação destinada à leitura humana, como `.tex`, `.pdf`, justificativas, relatórios e representações explicativas.

Use `models/` para fontes editáveis de modelos, esquemas, definições estruturais, DDL e demais artefatos técnicos relacionados à modelagem.

Use `database/`, `elt/` e `validation/` para código executável responsável, respectivamente, pela preparação do banco, pelo processamento dos dados e pela validação independente do resultado.

## Estado consolidado da modelagem conceitual

A Modelagem Conceitual foi concluída e validada.

O modelo aprovado contém nove entidades:

- Cliente;
- Pedido;
- Item do Pedido;
- Produto;
- Vendedor;
- Pagamento;
- Avaliação;
- Prefixo CEP;
- Geolocalização.

A fonte editável do MER consolidado encontra-se em:

`models/conceptual/mer-olist-conceitual.drawio`

A representação exportada utilizada na documentação encontra-se em:

`docs/modeling/conceptual/mer/`

A documentação correspondente encontra-se em:

`docs/modeling/conceptual/conceptual_model.tex`

e:

`docs/modeling/conceptual/conceptual_model.pdf`

As decisões conceituais foram sustentadas pelos seguintes notebooks:

- `01_validacao_entidades.ipynb`;
- `02_validacao_atributos.ipynb`;
- `03_validacao_relacionamentos.ipynb`;
- `04_validacao_cardinalidades.ipynb`;
- `05_validacao_prefixo_cep.ipynb`.

Esses artefatos devem ser consultados quando uma decisão posterior depender da justificativa empírica adotada durante a modelagem conceitual.

Não altere o modelo conceitual apenas para facilitar consultas ou estruturas analíticas. Caso uma etapa posterior revele uma inconsistência conceitual real, registre-a explicitamente antes de modificar artefatos aprovados.

## Estado consolidado da modelagem lógica

A Modelagem Lógica foi concluída e validada.

O modelo relacional consolidado contém nove tabelas:

- `cliente`;
- `pedido`;
- `item_pedido`;
- `produto`;
- `vendedor`;
- `pagamento`;
- `avaliacao`;
- `prefixo_cep`;
- `geolocalizacao`.

A representação técnica consolidada encontra-se em:

`models/logical/logical_schema.dbml`

A documentação correspondente encontra-se em:

`docs/modeling/logical/logical_model.tex`

e:

`docs/modeling/logical/logical_model.pdf`

O modelo lógico é independente de SGBD. Seus tipos representam domínios lógicos e não devem ser interpretados automaticamente como tipos físicos do PostgreSQL.

As principais decisões consolidadas são:

- `prefixo_cep` foi promovido a tabela própria para representar de forma explícita a referência geográfica compartilhada;
- `geolocalizacao` utiliza a chave substituta `id_geolocalizacao`, permitindo representar múltiplas ocorrências associadas ao mesmo prefixo de CEP;
- `item_pedido` utiliza chave primária composta por `id_pedido` e `id_item`;
- `pagamento` utiliza chave primária composta por `id_pedido` e `sequencial_pagamento`;
- `avaliacao` utiliza chave primária composta por `id_avaliacao` e `id_pedido`, pois `id_avaliacao` isoladamente não apresenta unicidade global no dataset;
- `pedido.id_cliente` possui restrição de unicidade para preservar a cardinalidade adotada entre Cliente e Pedido no modelo orientado à estrutura da fonte;
- todas as relações entre tabelas são representadas explicitamente por chaves estrangeiras;
- exclusões em cascata não foram adotadas;
- o modelo foi revisado quanto às dependências funcionais e consolidado até a Terceira Forma Normal;
- decisões de índices, armazenamento, particionamento e tipos específicos do PostgreSQL foram deliberadamente reservadas para a modelagem física.

Não altere silenciosamente essas decisões durante consultas, criação de views ou desenvolvimento da camada analítica.

Caso uma limitação comprovada, uma necessidade analítica ou uma característica do dataset exija mudança estrutural, documente a divergência, sua justificativa e seu impacto sobre os modelos aprovados.

## Estado consolidado da modelagem física

A Modelagem Física foi concluída, implementada e validada no PostgreSQL 18.

O modelo lógico permanece como referência estrutural, e os artefatos consolidados em `models/physical/` materializam a arquitetura com os schemas:

- `raw`;
- `core`;
- `analytics`.

A camada `raw` representa os dados provenientes das fontes.

A camada `core` implementa o modelo relacional consolidado, com tipos, chaves, constraints e índices aprovados.

A camada `analytics` permanece destinada às estruturas derivadas utilizadas para análise e consumo.

As principais diretrizes físicas consolidadas são:

- utilizar PostgreSQL como SGBD de referência;
- preservar identificadores provenientes da fonte quando não houver justificativa explícita para transformá-los;
- não converter automaticamente identificadores textuais em `UUID`;
- representar valores monetários com tipos de precisão exata;
- preservar prefixos de CEP com zeros à esquerda;
- respeitar a semântica dos atributos temporais;
- manter PKs, FKs, restrições `UNIQUE`, nulabilidade e `CHECK` definidos pelo modelo;
- não utilizar `ON DELETE CASCADE` sem decisão formal;
- não criar índices indiscriminadamente;
- não desnormalizar preventivamente por desempenho;
- não introduzir particionamento ou outras otimizações sem necessidade demonstrável;
- preservar a rastreabilidade entre os modelos conceitual, lógico e físico.

A documentação consolidada encontra-se em:

`docs/modeling/physical/physical_model.tex`

e:

`docs/modeling/physical/physical_model.pdf`

Os artefatos técnicos encontram-se em:

`models/physical/`

## Estado consolidado da carga e do ELT

A etapa de carga e preparação dos dados foi concluída e validada.

O processo segue a arquitetura:

```text
CSV
 ↓
RAW
 ↓
CORE
 ↓
validação independente
