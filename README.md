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
│   ├── physical/                    # DDL, índices e validações para PostgreSQL
│   └── analytics/                   # Views, marts e estruturas persistentes
│
├── notebooks/
│   ├── data-modeling/               # Validações e evidências da modelagem
│   │   ├── 01_validacao_entidades.ipynb
│   │   ├── 02_validacao_atributos.ipynb
│   │   ├── 03_validacao_relacionamentos.ipynb
│   │   ├── 04_validacao_cardinalidades.ipynb
│   │   └── 05_validacao_prefixo_cep.ipynb
│   │
│   ├── data-loading/                # Evidências reproduzíveis da carga
│   │   ├── 01_raw_source_profiling.ipynb
│   │   └── 02_raw_to_core_quality_validation.ipynb
│   └── analytics/                   # Exploração e evidências analíticas
│
├── config/
│   ├── raw_load.toml                # Contrato operacional da ingestão RAW
│   └── core_load.toml               # Configuração da transformação CORE
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
├── queries/                         # Consultas SQL sobre a CORE
│   ├── basic/
│   ├── analysis/
│   └── validation/
│
├── scripts/                         # Utilitários necessários e versionados
│   └── maintenance/
│
├── tests/
│   ├── test_core_loader.py
│   ├── test_database_setup.py
│   ├── test_elt_validation.py
│   ├── test_pipeline.py
│   └── test_raw_loader.py
│
├── .github/
├── .env.example                    # Exemplo canônico de configuração
├── .gitignore
├── .python-version
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── pyproject.toml                   # Metadados e dependências do projeto
└── uv.lock                          # Dependências com versões reproduzíveis
```

A estrutura poderá evoluir conforme novos artefatos forem desenvolvidos, especialmente durante a construção da camada analítica.

## Roadmap

<img src="./assets/project-roadmap.png" alt="Roadmap do projeto" width="100%">

## Configuração do ambiente

O projeto utiliza [uv](https://docs.astral.sh/uv/) para gerenciar o ambiente Python e as dependências.

Com o `uv` instalado, sincronize o ambiente:

```bash
uv sync --locked --all-groups
```

Para abrir os notebooks:

```bash
uv run jupyter lab
```

### Trabalho com notebooks

Os notebooks são criados e editados diretamente em `notebooks/`, no diretório correspondente à etapa do projeto. O diretório `scripts/` é reservado a utilitários necessários e versionados; notebooks não possuem cópias Python pareadas.

### Limpeza de artefatos locais

Inspecione os artefatos regeneráveis que seriam removidos:

```bash
uv run python scripts/maintenance/clean.py
```

Confirme a limpeza explicitamente com `--apply`. O utilitário recusa alvos que contenham arquivos versionados:

```bash
uv run python scripts/maintenance/clean.py --apply
```

## Dados

Os arquivos CSV originais não são armazenados no Git.

Consulte [data/README.md](data/README.md) para obter as instruções de download do dataset e preparação do diretório `data/raw/`.

Fonte: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## Banco de dados e processo ELT

A implementação utiliza PostgreSQL 18 e organiza os dados em três schemas:

```text
raw
 ↓
core
 ↓
analytics
```

A camada `raw` preserva os dados provenientes dos arquivos de origem.

A camada `core` materializa o modelo relacional consolidado, aplicando transformações, restrições e regras de integridade.

A camada `analytics` é destinada às estruturas de consumo analítico desenvolvidas nas etapas posteriores do projeto.

### Preparação do banco

Configure `DATABASE_URL` no ambiente local e execute:

```bash
uv run python -m database.setup
```

Quando for necessário reconstruir a estrutura do projeto no banco:

```bash
uv run python -m database.setup --reset
```

### Validação dos arquivos de origem

Para validar os arquivos CSV antes de acessar o banco:

```bash
uv run python -m elt.raw_loader --validate-only
```

### Execução do ELT

Para executar a ingestão da RAW e as transformações para a CORE:

```bash
uv run python -m elt.pipeline
```

O pipeline executa a carga de forma transacional, reconcilia os volumes processados e registra informações sobre cada execução.

A carga RAW segue uma estratégia de substituição da carga anterior, evitando a acumulação de múltiplas cópias do mesmo dataset.

### Validação da carga

Após a execução do pipeline, a reconciliação e as regras de qualidade podem ser executadas independentemente:

```bash
uv run python -m validation.elt_validation
```

A validação verifica, entre outros aspectos:

- Reconciliação de volumes entre origem e destino;
- Integridade de chaves primárias;
- Integridade referencial;
- Restrições de unicidade;
- Nulabilidade;
- Domínios de valores;
- Formatos de identificadores e prefixos de CEP;
- Valores monetários;
- Coordenadas geográficas;
- Transformações realizadas entre RAW e CORE.

A documentação consolidada da carga e das transformações encontra-se em:

- [carga_transformacao_dados.pdf](docs/data-loading/carga_transformacao_dados.pdf)
- [carga_transformacao_dados.tex](docs/data-loading/carga_transformacao_dados.tex)

## Testes e qualidade

O projeto possui testes automatizados para a preparação do banco, ingestão da RAW, transformação da CORE, orquestração do pipeline e validação do ELT.

Execute a suíte localmente com:

```bash
uv run python -m unittest discover -s tests -v
```

A integração contínua executada pelo GitHub Actions verifica:

- Sincronização do ambiente por meio do lockfile;
- Consistência do `uv.lock`;
- Lint e formatação com Ruff;
- Testes automatizados do projeto.

## Metodologia

O desenvolvimento segue uma abordagem incremental, na qual cada etapa deriva das decisões, modelos e evidências produzidos anteriormente:

```text
Análise de requisitos
        ↓
Entendimento e validação dos dados
        ↓
Modelo conceitual
        ↓
Modelo lógico relacional
        ↓
Modelo físico
        ↓
Implementação do banco de dados
        ↓
Carga e preparação dos dados
        ↓
Validação do ELT
        ↓
Consultas e análises
        ↓
Camada analítica e consumo em BI
```

A modelagem conceitual estabelece as entidades, atributos, identificadores, relacionamentos e cardinalidades do domínio.

A modelagem lógica converte essa estrutura para o paradigma relacional, definindo tabelas, chaves, restrições de integridade, nomenclatura e dependências entre os dados sem vinculá-la às particularidades de um SGBD.

A modelagem física traduz o modelo lógico para PostgreSQL 18 e materializa a arquitetura de dados nos schemas `raw`, `core` e `analytics`.

O processo ELT extrai os dados dos arquivos de origem, carrega-os na camada RAW e executa as transformações necessárias dentro do banco para produzir a camada CORE. A carga é acompanhada por reconciliação de volumes, testes automatizados e validações independentes de integridade e qualidade.

Com a preparação e a validação dos dados concluídas, a etapa atual concentra-se na exploração do modelo CORE e na construção da camada ANALYTICS. Essa fase inclui consultas SQL, métricas analíticas, validação dos requisitos funcionais, criação de estruturas de consumo e preparação dos dados para utilização em ferramentas de Business Intelligence.

O trabalho é planejado no [GitHub Project](https://github.com/users/LUCASDNORONHA/projects/6). As regras de status, prioridade, iteração e conclusão estão descritas em [docs/WORKFLOW.md](docs/WORKFLOW.md), enquanto o fluxo de contribuição está documentado em [CONTRIBUTING.md](CONTRIBUTING.md).

## Autor

Lucas Dias Noronha

## Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).
