<!-- Cabeçalho -->

<img src="./assets/project-banner.png" alt="Capa do projeto" width="100%">

<h2 align="center">
<em>Modelo Analítico de Dados para E-commerce</em>
</h2>

## Descrição

Este projeto tem como objetivo desenvolver um modelo de dados relacional para apoiar a exploração e a análise multidimensional de operações de comércio eletrônico.

A partir do conjunto de dados público **Brazilian E-Commerce Public Dataset by Olist**, o projeto organiza e relaciona informações de clientes, pedidos, itens, produtos, vendedores, pagamentos, avaliações e geolocalização. A estrutura resultante fornece uma base consistente para análises comerciais, comportamentais, financeiras, geográficas e relacionadas ao processo de entrega.

O trabalho reproduz, em escala de projeto, etapas recorrentes no desenvolvimento profissional de soluções de dados: análise de requisitos, compreensão e validação das fontes, modelagem conceitual, modelagem lógica, modelagem física, implementação do banco de dados, carga e preparação dos dados e disponibilização das informações para consultas e análises.

As etapas de análise de requisitos, modelagem, implementação do banco de dados e carga dos dados estão concluídas. O processo ELT foi implementado e validado, contemplando ingestão na camada RAW, transformação para a camada CORE, reconciliação de volumes, validações de integridade e regras de qualidade.

O projeto encontra-se atualmente na etapa de **análise de dados e construção da camada analítica**, na qual serão desenvolvidas consultas, métricas, estruturas de consumo e artefatos destinados à exploração dos dados e à futura integração com ferramentas de Business Intelligence.

## Objetivos

- Levantar e documentar os requisitos do domínio de e-commerce;
- Compreender a estrutura, a granularidade e a qualidade dos dados disponibilizados;
- Identificar entidades, atributos, relacionamentos, cardinalidades e regras de negócio;
- Desenvolver os modelos conceitual, lógico e físico do banco de dados;
- Garantir integridade, consistência e rastreabilidade das decisões de modelagem;
- Integrar as diferentes entidades do dataset em uma estrutura relacional coerente;
- Implementar um processo reproduzível de ingestão, transformação e validação dos dados;
- Disponibilizar uma base de dados adequada para consultas e análises multidimensionais de e-commerce;
- Estruturar uma camada analítica destinada ao consumo por SQL e ferramentas de Business Intelligence.

## Escopo

O projeto contempla dados relacionados a:

- Clientes;
- Pedidos e seus status;
- Itens dos pedidos;
- Produtos e categorias;
- Vendedores;
- Pagamentos;
- Avaliações de clientes;
- Datas e prazos associados ao processamento e à entrega dos pedidos;
- Informações geográficas e dados de geolocalização associados aos prefixos de CEP.

Não fazem parte do escopo o desenvolvimento de uma plataforma transacional de e-commerce, o processamento em tempo real, o gerenciamento operacional de estoque, o rastreamento físico de pedidos ou a gestão de transportadoras, veículos, motoristas e rotas.

Também não são utilizados dados pessoais sensíveis nem informações que permitam a identificação direta dos consumidores.

## Estrutura do repositório

```text
.
├── data/
│   ├── README.md
│   └── raw/                         # CSVs originais, não versionados
│
├── docs/
│   ├── WORKFLOW.md                  # Regras do fluxo de desenvolvimento
│   ├── requirements/                # Análise e documentação de requisitos
│   ├── data-loading/                # Documentação consolidada da carga e do ELT
│   │   ├── carga_transformacao_dados.tex
│   │   └── carga_transformacao_dados.pdf
│   │
│   └── modeling/
│       ├── conceptual/              # Documentação da modelagem conceitual
│       │   ├── conceptual_model.tex
│       │   ├── conceptual_model.pdf
│       │   └── mer/                 # Representação exportada do MER
│       │
│       ├── logical/                 # Documentação da modelagem lógica
│       │   ├── logical_model.tex
│       │   ├── logical_model.pdf
│       │   └── model/               # Representação gráfica do modelo lógico
│       │
│       └── physical/                # Documentação consolidada da modelagem física
│           ├── physical_model.tex
│           └── physical_model.pdf
│
├── models/
│   ├── README.md
│   ├── conceptual/                  # Artefatos técnicos do modelo conceitual
│   │   └── mer-olist-conceitual.drawio
│   ├── logical/                     # Artefatos técnicos do modelo lógico
│   │   └── logical_schema.dbml
│   └── physical/                    # DDL, índices e validações para PostgreSQL
│
├── notebooks/
│   ├── data-modeling/               # Validações e evidências da modelagem
│   │   ├── 01_validacao_entidades.ipynb
│   │   ├── 02_validacao_atributos.ipynb
│   │   ├── 03_validacao_relacionamentos.ipynb
│   │   ├── 04_validacao_cardinalidades.ipynb
│   │   └── 05_validacao_prefixo_cep.ipynb
│   │
│   └── data-loading/                # Evidências reproduzíveis da carga
│       ├── 01_raw_source_profiling.ipynb
│       └── 02_raw_to_core_quality_validation.ipynb
│
├── config/
│   ├── raw_load.toml                # Contrato operacional da ingestão RAW
│   ├── core_load.toml               # Configuração da transformação CORE
│   └── raw_load.env.example         # Exemplo de variável de conexão
│
├── database/
│   ├── __init__.py
│   └── setup.py                     # Preparação e validação da estrutura do banco
│
├── elt/
│   ├── __init__.py
│   ├── raw_loader.py                # Extração e carga transacional na RAW
│   ├── core_loader.py               # Transformação e reconciliação da CORE
│   ├── pipeline.py                  # Orquestração completa do ELT
│   └── sql/
│       └── load_core.sql            # Transformações RAW → CORE
│
├── validation/
│   ├── __init__.py
│   └── elt_validation.py            # Reconciliação, integridade e qualidade do ELT
│
├── scripts/                         # Fontes Jupytext locais, não versionadas
│   ├── data-modeling/
│   └── data-loading/
│
├── tests/
│   ├── test_core_loader.py
│   ├── test_database_setup.py
│   ├── test_elt_validation.py
│   ├── test_pipeline.py
│   └── test_raw_loader.py
│
├── .github/
├── .gitignore
├── .python-version
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── pyproject.toml                   # Metadados e dependências do projeto
└── uv.lock                          # Dependências com versões reproduzíveis
