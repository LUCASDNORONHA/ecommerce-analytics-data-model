# Modelo de Dados para Análise de Desempenho Logístico em E-commerce

## Descrição

Este projeto tem como objetivo desenvolver um modelo de dados relacional para apoiar a análise do desempenho logístico em operações de comércio eletrônico.

A partir do conjunto de dados público **Brazilian E-Commerce Public Dataset by Olist**, o projeto busca organizar e relacionar informações de clientes, pedidos, itens, produtos, vendedores, pagamentos e avaliações. Essa estrutura deverá permitir a análise de prazos de entrega, atrasos, status dos pedidos, desempenho de vendedores e satisfação dos clientes.

O trabalho simula as etapas de um projeto profissional de dados, partindo da análise de requisitos e do entendimento dos dados até a modelagem e a futura implementação do banco de dados.

## Objetivos

- Levantar e documentar os requisitos do domínio logístico de e-commerce;
- Compreender a estrutura e a qualidade dos dados disponibilizados;
- Identificar as entidades, seus atributos e relacionamentos;
- Desenvolver os modelos conceitual, lógico e físico do banco de dados;
- Garantir integridade, consistência e rastreabilidade dos dados;
- Preparar uma base adequada para consultas analíticas e indicadores logísticos.

## Escopo

O projeto contempla a modelagem de dados relacionados a:

- Clientes;
- Pedidos e seus status;
- Itens dos pedidos;
- Produtos e categorias;
- Vendedores;
- Pagamentos;
- Avaliações de clientes;
- Datas e prazos associados ao processo de entrega;
- Informações geográficas agregadas.

Não fazem parte do escopo atual o desenvolvimento de uma interface gráfica, a construção de um sistema transacional completo, o processamento em tempo real ou o uso de dados pessoais sensíveis.

## Etapa atual

O projeto encontra-se na etapa de **desenvolvimento do modelo relacional**.

Antes da definição final das tabelas, chaves primárias, chaves estrangeiras e cardinalidades, está sendo realizado o entendimento dos arquivos de origem. O notebook de validação identifica as entidades presentes no dataset, examina seus atributos e verifica se sua estrutura está de acordo com os requisitos e as regras de negócio documentados.

As próximas atividades previstas são:

1. Validar entidades, atributos, chaves e relacionamentos;
2. Concluir o modelo conceitual;
3. Desenvolver o modelo lógico relacional;
4. Definir tipos de dados e restrições de integridade;
5. Implementar o modelo físico em um SGBD relacional;
6. Carregar e validar os dados no banco;
7. Desenvolver consultas e indicadores de desempenho logístico.

## Estrutura do repositório

```text
.
├── data/
│   ├── README.md
│   └── raw/                         # CSVs originais, não versionados
├── docs/
│   └── requirements/                # Análise e documentação de requisitos
├── models/
│   ├── conceptual/                  # Modelo conceitual e MER
│   ├── logical/                     # Modelo lógico relacional
│   └── physical/                    # Modelo físico do banco de dados
├── notebooks/
│   └── data_understanding/          # Notebooks de exploração e validação
├── scripts/                         # Fontes Jupytext locais, não versionadas
├── .python-version
├── pyproject.toml                   # Metadados e dependências do projeto
├── uv.lock                          # Versões reproduzíveis das dependências
└── README.md
```

A estrutura poderá evoluir conforme novos artefatos forem desenvolvidos. O diretório `scripts/` existe apenas no ambiente local e é ignorado pelo Git; os notebooks sincronizados em `notebooks/` são os artefatos versionados e entregues com o projeto.

## Configuração do ambiente

O projeto utiliza [uv](https://docs.astral.sh/uv/) para gerenciar a versão do Python, o ambiente virtual e as dependências.

Com o uv instalado, sincronize o ambiente:

```bash
uv sync
```

Para abrir os notebooks:

```bash
uv run jupyter lab
```

### Fluxo de trabalho com Jupytext

Os notebooks possuem uma representação pareada em Python no formato `py:percent`. O desenvolvimento é feito localmente nos arquivos de `scripts/`, usando células `# %%` no VS Code.

Após alterar um script, sincronize seu notebook correspondente:

```bash
uv run jupytext --sync scripts/data_understanding/01_validacao_entidades.py
```

O pareamento mantém a seguinte correspondência:

```text
scripts/data_understanding/<arquivo>.py
                    ↕ Jupytext
notebooks/data_understanding/<arquivo>.ipynb
```

Somente o arquivo `.ipynb` deve ser incluído nos commits.

## Dados

Os CSVs não são armazenados no Git. Consulte [data/README.md](data/README.md) para baixar o dataset e preparar o diretório `data/raw/`.

Fonte: [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

## Metodologia

O desenvolvimento segue uma abordagem incremental, com refinamento contínuo dos requisitos e evolução progressiva da modelagem:

```text
Análise de requisitos
        ↓
Entendimento e validação dos dados
        ↓
Modelo conceitual
        ↓
Modelo lógico relacional
        ↓
Modelo físico e implementação
        ↓
Consultas e análises
```

## Autor

Lucas Dias Noronha

## Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).
