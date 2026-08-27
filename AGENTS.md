# Instruções para agentes

## Objetivo do projeto

Este repositório desenvolve um modelo de dados relacional para sustentar análises multidimensionais de e-commerce usando o Brazilian E-Commerce Public Dataset by Olist.

O modelo integra dados de clientes, pedidos, itens, produtos, vendedores, pagamentos, avaliações e geolocalização, permitindo análises comerciais, comportamentais, financeiras, geográficas e relacionadas ao processo de entrega.

O trabalho evolui pelas milestones M01 a M06:

1. M01 — Análise de Requisitos;
2. M02 — Modelagem Conceitual;
3. M03 — Modelagem Lógica;
4. M04 — Modelagem Física;
5. M05 — Carga de Dados;
6. M06 — Análise.

Consulte o GitHub Project nº 6 antes de iniciar qualquer tarefa.

A milestone atualmente em execução é **M03 — Modelagem Lógica**.

A Modelagem Conceitual está concluída e constitui a referência semântica para a transformação do domínio em estruturas relacionais.

A primeira entrega prevista da M03 é a issue **#27 — [M03-01] Converter entidades em tabelas**, seguida pelas tarefas de definição de chaves, nomenclatura, normalização, integridade referencial e revisão final do modelo lógico.

Antes de iniciar trabalho, confirme no GitHub Project qual issue está efetivamente marcada como **Em Andamento**.

## Fontes de verdade

As fontes devem ser consultadas nesta ordem de responsabilidade:

- **GitHub Project nº 6:** prioridade, status, sprint e ordem de execução;
- **issue ativa:** contexto, objetivo, escopo, dependências, artefatos esperados e critérios de aceitação;
- **repositório:** código, notebooks, modelos e documentação já aprovados;
- `docs/requirements/`: requisitos e delimitação do domínio;
- `docs/modeling/conceptual/`: documentação e MER conceitual aprovados;
- `docs/modeling/logical/`: documentação produzida durante a modelagem lógica;
- `docs/modeling/physics/`: documentação produzida durante a modelagem física;
- `docs/WORKFLOW.md`: regras de gestão do trabalho;
- `CONTRIBUTING.md`: convenções de branch, commit e pull request.

Durante a M03, o modelo conceitual aprovado deve ser tratado como referência para preservar semântica, granularidade, relacionamentos e cardinalidades.

A transformação para o modelo lógico pode introduzir tabelas, chaves estrangeiras, restrições e outras estruturas relacionais, mas não deve alterar silenciosamente decisões conceituais já aprovadas.

Quando houver divergência entre requisitos, modelo conceitual, dataset ou issue, não invente uma decisão de domínio. Registre a inconsistência, apresente a evidência e preserve a rastreabilidade da decisão adotada.

## Estrutura relevante

- `data/raw/`: CSVs originais utilizados localmente e não versionados;
- `docs/requirements/`: análise de requisitos aprovada;
- `docs/modeling/conceptual/`: documento de modelagem conceitual, PDF e MER aprovado;
- `docs/modeling/conceptual/mer/`: fonte editável e exportações do MER conceitual;
- `docs/modeling/logical/`: documentação da modelagem lógica;
- `docs/modeling/physics/`: documentação da modelagem física;
- `models/conceptual/`: artefatos técnicos de modelagem conceitual quando aplicável;
- `models/logical/`: esquemas e artefatos técnicos do modelo lógico relacional;
- `models/physical/`: DDL e demais artefatos dependentes do SGBD;
- `notebooks/data-modeling/`: notebooks versionados de validação e apoio às decisões de modelagem;
- `scripts/`: fontes Python locais pareadas por Jupytext e ignoradas pelo Git.

Não crie arquivos na raiz quando já existir um diretório próprio para o artefato.

Não duplique o mesmo artefato desnecessariamente entre `docs/` e `models/`.

Use `docs/` para documentação destinada à leitura humana, como `.tex`, `.pdf`, justificativas e diagramas explicativos.

Use `models/` para representações técnicas do modelo, esquemas, definições estruturais e artefatos destinados às etapas posteriores de implementação.

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

O MER consolidado encontra-se em:

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

Esses artefatos devem ser consultados quando uma decisão da M03 depender da justificativa empírica adotada durante a M02.

Não altere o modelo conceitual apenas para facilitar a implementação lógica. Caso a M03 revele uma inconsistência conceitual real, registre-a explicitamente antes de modificar artefatos aprovados.

## Diretrizes para a Modelagem Lógica

A M03 deve transformar o modelo conceitual aprovado em um modelo relacional independente dos detalhes físicos do SGBD.

A sequência prevista é:

1. converter entidades em tabelas;
2. definir chaves primárias lógicas;
3. definir chaves estrangeiras;
4. padronizar nomenclatura SQL;
5. normalizar o modelo até a Terceira Forma Normal;
6. validar integridade referencial;
7. revisar redundâncias e consolidar o modelo lógico.

Durante essa transformação:

- preserve a granularidade conceitual das entidades;
- não introduza tipos de dados específicos do PostgreSQL antes da modelagem física, salvo quando necessários apenas para documentação comparativa;
- diferencie chave conceitual, chave lógica e implementação física;
- documente qualquer chave substituta introduzida;
- não elimine chaves naturais ou compostas sem justificativa;
- represente explicitamente todas as chaves estrangeiras;
- preserve rastreabilidade entre entidade conceitual e tabela lógica;
- avalie dependências funcionais antes de afirmar que uma tabela está em 2FN ou 3FN;
- não desnormalize preventivamente por desempenho;
- não antecipe índices, particionamento ou decisões específicas de armazenamento para a M03;
- registre exceções e decisões que afetem a futura M04.

O produto final da M03 deve permitir compreender a estrutura relacional completa sem depender da implementação física do PostgreSQL.

## Ambiente e dependências

O projeto usa Python 3.12 e `uv`.

Não use `pip`, Poetry ou Conda para alterar o ambiente do projeto.

```bash
uv sync --locked --all-groups
uv lock --check
