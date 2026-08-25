<!-- Cabeçalho -->

<img src="./assets/project-banner.png" alt="Capa projeto" width="100%">

<h2 align="center">
<em>Modelo Analítico de Dados para E-commerce</em>
</h2>

## Descrição

Este projeto tem como objetivo desenvolver um modelo de dados relacional para apoiar a exploração e a análise multidimensional de operações de comércio eletrônico.

A partir do conjunto de dados público **Brazilian E-Commerce Public Dataset by Olist**, o projeto busca organizar e relacionar informações de clientes, pedidos, itens, produtos, vendedores, pagamentos, avaliações e geolocalização. A estrutura resultante deverá fornecer uma base consistente para análises comerciais, comportamentais, financeiras, geográficas e relacionadas ao processo de entrega.

O trabalho simula as etapas de um projeto profissional de dados, partindo da análise de requisitos e do entendimento dos dados até a modelagem e a futura implementação do banco de dados.

## Objetivos

- Levantar e documentar os requisitos do domínio de e-commerce;
- Compreender a estrutura, a granularidade e a qualidade dos dados disponibilizados;
- Identificar as entidades, seus atributos, relacionamentos e regras de negócio;
- Desenvolver os modelos conceitual, lógico e físico do banco de dados;
- Garantir integridade, consistência e rastreabilidade dos dados;
- Integrar as diferentes entidades do dataset em uma estrutura relacional coerente;
- Preparar uma base adequada para consultas e análises multidimensionais de e-commerce.

## Escopo

O projeto contempla a modelagem de dados relacionados a:

- Clientes;
- Pedidos e seus status;
- Itens dos pedidos;
- Produtos e categorias;
- Vendedores;
- Pagamentos;
- Avaliações de clientes;
- Datas e prazos associados ao processamento e à entrega dos pedidos;
- Informações geográficas e dados de geolocalização associados aos prefixos de CEP.

Não fazem parte do escopo atual o desenvolvimento de uma plataforma transacional de e-commerce, o processamento em tempo real, o gerenciamento operacional de estoque, o rastreamento físico de pedidos ou a gestão de transportadoras, veículos, motoristas e rotas. Também não são utilizados dados pessoais sensíveis ou informações que permitam a identificação direta dos consumidores.

## Etapa atual

O projeto encontra-se na fase de **modelagem conceitual**. A identificação das entidades e a validação dos atributos foram concluídas; a próxima entrega é a definição das chaves primárias conceituais.

As próximas atividades previstas são:

1. Definir chaves primárias, relacionamentos e cardinalidades;
2. Concluir o modelo conceitual;
3. Desenvolver o modelo lógico relacional;
4. Definir tipos de dados e restrições de integridade;
5. Implementar o modelo físico em um SGBD relacional;
6. Carregar e validar os dados no banco;
7. Desenvolver consultas e análises sobre as diferentes dimensões do e-commerce.

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

O trabalho é planejado no [GitHub Project](https://github.com/users/LUCASDNORONHA/projects/6). As regras de status, prioridade, iteração e conclusão estão descritas em [docs/WORKFLOW.md](docs/WORKFLOW.md), e o fluxo de contribuição está em [CONTRIBUTING.md](CONTRIBUTING.md).

## Autor

Lucas Dias Noronha

## Licença

Este projeto está licenciado sob os termos da [MIT License](LICENSE).
