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
8. consultas e análises.

A análise de requisitos, a modelagem conceitual e a modelagem lógica estão concluídas e constituem a base aprovada para as etapas seguintes.

A etapa atualmente em desenvolvimento é a **Modelagem Física**, tendo o PostgreSQL como SGBD de destino.

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
- `docs/modeling/physical/`: documentação produzida durante a modelagem física;
- `models/physical/`: artefatos técnicos dependentes do SGBD;
- `docs/WORKFLOW.md`: regras de gestão do trabalho;
- `CONTRIBUTING.md`: convenções de branch, commit e pull request.

O modelo conceitual aprovado deve ser tratado como referência semântica do domínio.

O modelo lógico aprovado deve ser tratado como referência estrutural para a implementação física, preservando tabelas, granularidade, chaves, relacionamentos, cardinalidades, restrições lógicas e decisões de normalização.

A modelagem física pode introduzir tipos de dados concretos, constraints específicas do PostgreSQL, índices e outras estruturas dependentes do SGBD, mas não deve alterar silenciosamente decisões conceituais ou lógicas já aprovadas.

Quando houver divergência entre requisitos, modelo conceitual, modelo lógico, dataset ou issue ativa, não invente uma decisão de domínio. Registre a inconsistência, apresente a evidência e preserve a rastreabilidade da decisão adotada.

## Estrutura relevante

- `data/raw/`: CSVs originais utilizados localmente e não versionados;
- `docs/requirements/`: análise de requisitos aprovada;
- `docs/modeling/conceptual/`: documentação da modelagem conceitual;
- `docs/modeling/conceptual/mer/`: representação exportada do MER utilizada na documentação;
- `docs/modeling/logical/`: documentação da modelagem lógica;
- `docs/modeling/physical/`: documentação da modelagem física;
- `models/conceptual/`: fonte técnica editável do modelo conceitual;
- `models/conceptual/mer-olist-conceitual.drawio`: fonte editável do MER conceitual;
- `models/logical/`: artefatos técnicos do modelo lógico relacional;
- `models/logical/logical_schema.dbml`: representação técnica consolidada do modelo lógico;
- `models/physical/`: DDL e demais artefatos dependentes do PostgreSQL;
- `notebooks/data-modeling/`: notebooks versionados de validação e apoio às decisões de modelagem;
- `scripts/`: fontes Python locais pareadas por Jupytext e ignoradas pelo Git.

Não crie arquivos na raiz quando já existir um diretório próprio para o artefato.

Não duplique o mesmo artefato desnecessariamente entre `docs/` e `models/`.

Use `docs/` para documentação destinada à leitura humana, como `.tex`, `.pdf`, justificativas e representações explicativas dos modelos.

Use `models/` para fontes editáveis dos modelos, esquemas, definições estruturais, DDL e demais artefatos técnicos destinados à implementação ou reutilização.

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

Não altere o modelo conceitual apenas para facilitar a implementação física. Caso uma etapa posterior revele uma inconsistência conceitual real, registre-a explicitamente antes de modificar artefatos aprovados.

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

Não altere silenciosamente essas decisões durante a implementação física.

Caso uma limitação do PostgreSQL, uma característica comprovada do dataset ou uma necessidade técnica exija mudança estrutural, documente a divergência, sua justificativa e seu impacto sobre o modelo lógico.

## Diretrizes para a Modelagem Física

A Modelagem Física deve transformar o modelo lógico aprovado em uma especificação concreta e implementável no PostgreSQL.

O modelo lógico é a referência estrutural desta etapa. A modelagem física deve definir como essa estrutura será materializada no SGBD sem modificar silenciosamente sua semântica.

A sequência de trabalho deve considerar:

1. validar os valores reais do dataset relevantes para decisões físicas;
2. mapear os domínios lógicos para tipos concretos do PostgreSQL;
3. definir tamanhos, precisão e escala quando aplicáveis;
4. implementar chaves primárias e estrangeiras;
5. implementar restrições de unicidade;
6. definir nulabilidade;
7. definir restrições `CHECK` quando justificadas pelo domínio;
8. avaliar índices com base em integridade, relacionamentos e padrões previstos de acesso;
9. revisar a integridade estrutural do modelo físico;
10. produzir o DDL correspondente;
11. documentar decisões físicas e eventuais divergências em relação ao modelo lógico.

Durante essa transformação:

- utilize PostgreSQL como SGBD de referência;
- não escolha tipos físicos apenas pela aparência dos valores;
- valide o dataset antes de definir tamanho, precisão, escala ou domínio de uma coluna;
- preserve identificadores provenientes da fonte quando não houver justificativa explícita para transformá-los;
- não converta automaticamente identificadores textuais em `UUID`;
- represente valores monetários com tipos de precisão exata, evitando tipos de ponto flutuante;
- preserve prefixos de CEP como valores capazes de manter zeros à esquerda;
- avalie explicitamente a semântica das datas antes de decidir entre os tipos temporais disponíveis no PostgreSQL;
- implemente todas as PKs, FKs, restrições `UNIQUE` e regras de nulabilidade definidas pelo modelo lógico;
- introduza restrições `CHECK` somente quando sustentadas pelo domínio ou por uma regra explicitamente documentada;
- não utilize `ON DELETE CASCADE` sem uma nova decisão formal que justifique a alteração da política definida no modelo lógico;
- não crie índices indiscriminadamente;
- justifique índices adicionais por integridade, padrão de consulta, relacionamento ou necessidade concreta de desempenho;
- não desnormalize preventivamente por desempenho;
- não introduza particionamento, materialized views ou outras otimizações sem necessidade demonstrável;
- preserve a rastreabilidade entre entidade conceitual, tabela lógica e implementação física;
- registre qualquer decisão física que possa afetar carga, consultas ou etapas analíticas posteriores.

A definição de um tipo físico deve considerar simultaneamente:

- semântica do atributo;
- valores efetivamente encontrados no dataset;
- domínio lógico definido anteriormente;
- restrições do PostgreSQL;
- precisão necessária;
- integridade dos dados;
- custo e finalidade analítica.

Sempre que houver dúvida sobre uma decisão física dependente dos dados, valide primeiro os arquivos em `data/raw/` ou produza evidência em notebook apropriado antes de consolidar a decisão.

## Artefatos da Modelagem Física

Os artefatos técnicos dependentes do PostgreSQL devem ser armazenados em:

`models/physical/`

O DDL que representar a estrutura física consolidada deve permanecer nesse diretório.

A documentação das decisões físicas deve ser armazenada em:

`docs/modeling/physical/`

Mantenha separadas:

- a **modelagem física**, que define como o modelo lógico será representado concretamente no PostgreSQL;
- a **implementação**, que executa o DDL e cria efetivamente os objetos no banco;
- a **carga e preparação dos dados**, que insere e transforma os dados provenientes da fonte;
- a **camada analítica**, que poderá posteriormente introduzir views, tabelas derivadas, marts ou outras estruturas destinadas ao consumo analítico.

Não antecipe estruturas analíticas apenas para simplificar a modelagem física.

## Ambiente e dependências

O projeto usa Python 3.12 e `uv`.

Não use `pip`, Poetry ou Conda para alterar o ambiente do projeto.

```bash
uv sync --locked --all-groups
uv lock --check