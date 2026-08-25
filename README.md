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

Antes da definição final das tabelas, chaves primárias, chaves estrangeiras e cardinalidades, está sendo realizado o entendimento dos arquivos de origem. O notebook de validação é utilizado para identificar as entidades presentes no dataset, examinar seus atributos e verificar se sua estrutura está de acordo com os requisitos e as regras de negócio documentados.

As próximas atividades previstas incluem:

1. Validar entidades, atributos, chaves e relacionamentos;
2. Concluir o modelo conceitual;
3. Desenvolver o modelo lógico relacional;
4. Definir tipos de dados e restrições de integridade;
5. Implementar o modelo físico em um SGBD relacional;
6. Carregar e validar os dados no banco;
7. Desenvolver consultas e indicadores de desempenho logístico.

## Estrutura do projeto

A estrutura do repositório ainda está em definição e poderá evoluir conforme o avanço da modelagem.

```text
.
├── data/
│   └── raw/                  # Arquivos CSV originais do dataset Olist
├── docs/                     # Documentação e análise de requisitos
├── notebooks/
│   └── data_understanding/   # Exploração e validação das entidades
├── main.py                   # Ponto de entrada inicial do projeto
├── pyproject.toml            # Configuração do projeto Python
├── LICENSE
└── README.md
```

Novos diretórios destinados aos modelos de dados, scripts SQL e processos de carga serão adicionados quando esses artefatos forem desenvolvidos.

## Fonte dos dados

O projeto utiliza o [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), conjunto de dados público com informações sobre pedidos realizados em diferentes marketplaces brasileiros.

## Metodologia

O desenvolvimento segue uma abordagem incremental, com refinamento contínuo dos requisitos e evolução progressiva da modelagem. O fluxo planejado é:

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
