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
- `queries/`: consultas SQL exploratórias, analíticas e de validação sobre a CORE;
- `models/analytics/`: fontes SQL das estruturas persistentes do schema `analytics`;
- `docs/analytics/`: métricas, decisões, limitações e rastreabilidade analítica;
- `notebooks/analytics/`: exploração e evidências empíricas da camada analítica;
- `notebooks/data-modeling/`: evidências da modelagem;
- `notebooks/data-loading/`: evidências da carga e da qualidade dos dados;
- `tests/`: testes automatizados;
- `scripts/`: utilitários necessários e versionados; não replica notebooks.

Não crie arquivos na raiz quando já existir um diretório próprio para o artefato.

Não duplique o mesmo artefato desnecessariamente entre `docs/`, `models/` e diretórios de implementação.

Use `docs/` para documentação destinada à leitura humana, como `.tex`, `.pdf`, justificativas, relatórios e representações explicativas.

Use `models/` para fontes editáveis de modelos, esquemas, definições estruturais, DDL e demais artefatos técnicos relacionados à modelagem.

Use `database/`, `elt/` e `validation/` para código executável responsável, respectivamente, pela preparação do banco, pelo processamento dos dados e pela validação independente do resultado.

Utilize prefixos numéricos de dois dígitos apenas em coleções com ordem real de leitura ou execução, como notebooks sequenciais e consultas SQL ordenadas. Não numere diretórios arquiteturais, módulos Python, testes ou arquivos independentes para representar a cronologia geral; essa sequência deve permanecer documentada no README principal.

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
```

A implementação está organizada da seguinte forma:

- `database/setup.py`: prepara e valida a estrutura do banco;
- `elt/raw_loader.py`: valida os arquivos de origem e executa a ingestão na RAW;
- `elt/core_loader.py`: executa as transformações e a reconciliação da CORE;
- `elt/pipeline.py`: orquestra o fluxo completo;
- `elt/sql/load_core.sql`: materializa as transformações RAW → CORE;
- `validation/elt_validation.py`: valida reconciliação, integridade e qualidade após a carga.

Os nove arquivos CSV utilizados como fonte devem ser tratados como imutáveis durante a execução da carga e não devem ser versionados.

A camada RAW preserva os valores provenientes da origem conforme os contratos de ingestão aprovados.

A transformação RAW → CORE deve permanecer explícita, determinística e reproduzível.

A carga substitui a execução anterior da RAW, em vez de acumular múltiplas cópias do mesmo dataset.

Não altere as regras de transformação apenas para facilitar uma consulta analítica. Caso uma análise revele uma limitação real da transformação, registre a evidência e trate a alteração como mudança própria do ELT.

## Validação consolidada do ELT

O resultado da carga foi aprovado por validações independentes de:

- reconciliação de volumes;
- chaves primárias;
- restrições de unicidade;
- integridade referencial;
- nulabilidade;
- domínio dos identificadores;
- formato dos prefixos de CEP;
- domínio das UFs;
- domínio dos status de pedido;
- domínio dos tipos de pagamento;
- notas de avaliação;
- valores monetários não negativos;
- sequenciais;
- dimensões de produto;
- coordenadas geográficas;
- textos obrigatórios;
- equivalência das transformações RAW → CORE.

A implementação dessas regras encontra-se em:

`validation/elt_validation.py`

Os testes automatizados correspondentes encontram-se em:

`tests/test_elt_validation.py`

A documentação consolidada da etapa encontra-se em:

`docs/data-loading/carga_transformacao_dados.tex`

e:

`docs/data-loading/carga_transformacao_dados.pdf`

A CORE aprovada deve ser tratada como ponto de partida da etapa analítica.

## Diretrizes para a Camada Analítica

A etapa atual deve utilizar a CORE validada para responder aos requisitos analíticos do projeto.

O trabalho deve evoluir de consultas exploratórias para estruturas de consumo reproduzíveis, respeitando a ordem definida pela issue ativa.

A sequência prevista inclui:

1. desenvolver consultas SQL fundamentais sobre o modelo CORE;
2. combinar as entidades em consultas analíticas;
3. validar requisitos funcionais por meio de dados e resultados reproduzíveis;
4. definir métricas com fórmula, granularidade, dimensão temporal e interpretação explícitas;
5. identificar consultas e regras recorrentes que justifiquem estruturas no schema `analytics`;
6. criar views, marts ou outras estruturas derivadas quando houver necessidade concreta;
7. preparar os dados para consumo por SQL e ferramentas de Business Intelligence;
8. documentar resultados, premissas, limitações e decisões analíticas.

Durante essa etapa:

- utilize a CORE como fonte principal para análise;
- não consulte diretamente a RAW para produzir métricas finais, salvo investigação de qualidade ou rastreabilidade;
- não altere a CORE apenas para simplificar uma análise;
- não duplique regras de negócio em múltiplas consultas quando uma estrutura analítica reutilizável for justificável;
- defina explicitamente a granularidade de cada métrica;
- diferencie valor absoluto, percentual, proporção, taxa, média e mediana;
- registre filtros e condições que alterem a interpretação de um indicador;
- documente o período temporal considerado;
- não trate correlação como causalidade;
- não invente dimensões, atributos ou relações ausentes do dataset;
- não atribua ao dataset capacidades operacionais que ele não possui;
- preserve a diferença entre pedido, item, cliente, vendedor, pagamento e avaliação ao realizar agregações;
- valide o risco de duplicação de medidas ao realizar joins entre relações `1:N`;
- evite somar valores monetários após joins que multipliquem a granularidade dos registros;
- valide métricas contra consultas de controle antes de consolidá-las;
- mantenha SQL analítico legível, reproduzível e versionado;
- documente estruturas criadas no schema `analytics`;
- não introduza uma view ou mart apenas porque uma consulta é longa; reutilização, semântica e frequência devem justificar a estrutura.

Consultas exploratórias podem permanecer direcionadas à CORE.

Views, marts e demais estruturas reutilizáveis destinadas ao consumo recorrente devem utilizar o schema `analytics`, quando justificadas pela issue ativa.

## Granularidade e joins analíticos

Antes de combinar tabelas, determine explicitamente a granularidade de cada uma.

Exemplos:

- `pedido`: um registro por pedido;
- `item_pedido`: um registro por item do pedido;
- `pagamento`: um registro por pagamento ou sequência de pagamento;
- `avaliacao`: um registro por par de avaliação e pedido;
- `geolocalizacao`: múltiplos registros podem estar associados ao mesmo prefixo de CEP.

Ao combinar tabelas com granularidades diferentes, valide se o join multiplica linhas.

Não calcule medidas agregadas após um join `1:N` ou `N:N` sem verificar se os valores foram duplicados.

Quando necessário:

- agregue previamente a tabela de maior granularidade;
- utilize CTEs ou subconsultas para controlar a granularidade;
- valide contagens antes e depois do join;
- mantenha explícita a unidade analítica de cada resultado.

Essa regra é especialmente importante ao combinar pedidos com itens, pagamentos, avaliações ou geolocalização.

## Métricas

Toda métrica consolidada deve possuir, quando aplicável:

- nome;
- objetivo;
- fórmula;
- unidade;
- granularidade;
- dimensão temporal;
- filtros;
- regras de inclusão e exclusão;
- fonte das colunas;
- interpretação;
- limitações.

Não use nomes ambíguos como `receita`, `vendas`, `clientes ativos` ou `ticket médio` sem definir exatamente como são calculados.

Quando houver mais de uma interpretação válida para uma métrica, registre a decisão adotada.

## Camada ANALYTICS

O schema `analytics` existe para encapsular estruturas destinadas ao consumo analítico.

Pode conter, quando justificado:

- views;
- tabelas derivadas;
- marts;
- agregações recorrentes;
- estruturas de consumo para BI.

Não utilize o schema `analytics` como local para copiar tabelas da CORE sem transformação ou finalidade analítica.

Uma estrutura analítica deve existir porque reduz repetição, estabiliza uma regra, organiza uma granularidade de consumo ou facilita uma necessidade recorrente.

A criação de qualquer estrutura nesse schema deve preservar a rastreabilidade até as tabelas CORE utilizadas em sua origem.

## Documentação e evidências

Use `docs/` para:

- documentação destinada à leitura humana;
- definição e interpretação de métricas;
- decisões analíticas;
- matrizes de rastreabilidade;
- relatórios consolidados.

Use `notebooks/` para:

- exploração;
- validação empírica;
- comparação de resultados;
- evidências reproduzíveis.

Use `queries/` para consultas direcionadas à CORE e `models/analytics/` para estruturas persistentes do schema `analytics`.

Não utilize notebooks como única fonte de uma regra de negócio que deva ser reutilizada em produção ou pela camada analítica.

## Ambiente e dependências

O projeto usa Python 3.12 e `uv`.

Não use `pip`, Poetry ou Conda para alterar o ambiente do projeto.

Use:

```bash
uv sync --locked --all-groups
uv lock --check
```

O arquivo `.python-version` define a versão de referência do Python.

O `pyproject.toml` define as dependências do projeto.

O `uv.lock` deve permanecer sincronizado com o `pyproject.toml`.

Não altere dependências sem necessidade concreta da issue ativa.

## Execução e validação local

Para preparar o banco:

```bash
uv run python -m database.setup
```

Para reconstruir a estrutura do projeto no banco:

```bash
uv run python -m database.setup --reset
```

Para validar os arquivos de origem sem acessar o banco:

```bash
uv run python -m elt.raw_loader --validate-only
```

Para executar o ELT completo:

```bash
uv run python -m elt.pipeline
```

Para executar a validação independente da carga:

```bash
uv run python -m validation.elt_validation
```

Para executar os testes automatizados:

```bash
uv run python -m unittest discover -s tests -v
```

Para validar o lockfile:

```bash
uv lock --check
```

Para validar lint e formatação:

```bash
uv run ruff check .
uv run ruff format --check .
```

Não considere uma alteração pronta caso as verificações pertinentes à tarefa apresentem erro.

## Fluxo de trabalho

Antes de iniciar uma tarefa:

1. consulte o GitHub Project nº 6;
2. identifique a issue marcada como **Em Andamento**;
3. leia integralmente seu objetivo, dependências, artefatos e critérios de aceitação;
4. confirme que a `main` local está sincronizada;
5. crie uma branch específica para a issue;
6. limite o trabalho ao escopo definido.

Durante o desenvolvimento:

- faça alterações pequenas e rastreáveis;
- mantenha os artefatos nos diretórios corretos;
- atualize testes e documentação quando necessário;
- não antecipe trabalho pertencente a issues posteriores;
- não altere modelos aprovados sem evidência e justificativa;
- preserve compatibilidade com o estado consolidado do projeto.

Ao concluir:

1. execute as validações aplicáveis;
2. revise os critérios de aceitação;
3. abra um pull request vinculado à issue;
4. utilize `Closes #<numero>` corretamente;
5. faça o merge somente após aprovação da CI;
6. encerre a issue;
7. confirme seu estado como **Concluído** no GitHub Project;
8. exclua a branch após o merge.

Não deixe `Closes #` vazio no pull request.

Não faça merge de uma alteração com verificações automáticas falhando.

## Princípios gerais

Preserve a rastreabilidade do projeto.

Não altere uma camada anterior apenas para tornar uma camada posterior mais conveniente.

Não transforme um padrão encontrado nos dados em regra de negócio sem justificativa.

Não descarte inconsistências silenciosamente.

Não esconda limitações dos dados.

Não antecipe complexidade.

Prefira soluções simples, reproduzíveis, explícitas e sustentadas por evidência.

Quando houver dúvida entre implementar uma suposição e registrar uma incerteza, registre a incerteza.
