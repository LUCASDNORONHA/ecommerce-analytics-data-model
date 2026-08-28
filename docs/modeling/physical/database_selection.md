# Decisão técnica do SGBD

## Identificação

- **Issue:** #34 — [M04-01] Selecionar o SGBD
- **Status da decisão:** aceita
- **Data:** 28 de agosto de 2026
- **Etapa:** M04 — Modelagem Física

## Decisão

O modelo físico será implementado no **PostgreSQL 18**, sempre utilizando a
revisão secundária mais recente disponível da versão principal 18.

O **DBeaver** será utilizado como cliente gráfico para administrar a conexão,
executar e inspecionar scripts SQL e consultar os objetos criados no PostgreSQL.
Ele não substitui o SGBD nem integra a especificação do modelo físico.

## Contexto

O projeto trabalha com dados estruturados de e-commerce distribuídos em nove
tabelas relacionadas. O modelo lógico aprovado exige chaves primárias simples e
compostas, chaves estrangeiras, unicidade, nulabilidade e preservação da
integridade referencial. A solução também deverá sustentar cargas reproduzíveis,
junções, agregações e análises comerciais, financeiras, temporais e geográficas.

A análise de requisitos já estabelece PostgreSQL como tecnologia da
implementação física. Portanto, esta decisão formaliza e versiona uma diretriz
previamente aprovada, sem alterar o modelo conceitual ou o modelo lógico.

## Critérios considerados

| Critério | Avaliação |
|---|---|
| Adequação ao modelo relacional | Suporta nativamente tabelas, PKs, FKs, `UNIQUE`, `CHECK` e transações. |
| Integridade | Permite materializar as restrições definidas no modelo lógico e manter a política de exclusão restritiva. |
| Tipos físicos | Oferece tipos adequados para identificadores textuais, valores monetários exatos, coordenadas e informações temporais. |
| Consultas analíticas | Suporta junções, agregações, funções de janela, CTEs e recursos SQL úteis às etapas analíticas posteriores. |
| Automação | Disponibiliza ferramentas de linha de comando que permitem criar e testar o esquema de forma reproduzível. |
| Ecossistema | Possui documentação oficial, manutenção ativa, ampla adoção e integração direta com Python e DBeaver. |
| Custo e portabilidade | É software livre e pode ser executado localmente ou em serviços gerenciados. |

## Versão adotada

A versão principal adotada é a **PostgreSQL 18**, versão estável atual na data
desta decisão e com suporte oficial previsto até novembro de 2030.

A revisão secundária deverá ser atualizada dentro da série 18 para incorporar
correções de segurança e estabilidade. Uma mudança futura de versão principal
exigirá revisão desta decisão e validação do DDL, pois versões principais podem
introduzir incompatibilidades.

## Uso do DBeaver

O DBeaver será o ambiente gráfico de trabalho para:

- configurar e testar a conexão com o servidor PostgreSQL;
- executar os scripts DDL produzidos em `models/physical/`;
- inspecionar tabelas, colunas, chaves, restrições e índices;
- apoiar consultas e verificações manuais durante o desenvolvimento.

A conexão utilizará o driver PostgreSQL do DBeaver. Endereço, porta, banco,
usuário e credenciais dependerão do ambiente criado nas tarefas de implementação.
Credenciais e configurações locais do DBeaver não serão versionadas.

O DBeaver complementará, mas não substituirá, os testes automatizados ou os
scripts reproduzíveis exigidos pelo projeto. A validade do modelo físico não
dependerá de metadados privados mantidos pelo cliente gráfico.

## Consequências

- os tipos lógicos serão mapeados para tipos concretos do PostgreSQL nas tarefas
  seguintes;
- o DDL e as restrições poderão utilizar sintaxe específica do PostgreSQL;
- scripts de criação e validação deverão declarar e verificar a versão do
  servidor utilizada;
- tipos, índices e `CHECK` constraints continuarão dependendo de justificativa e
  evidência, não sendo definidos por esta decisão;
- o modelo lógico aprovado permanece inalterado;
- a configuração do servidor, a criação do banco e o teste da conexão ficam fora
  do escopo desta issue.

## Referências

- [Análise de requisitos](../../requirements/analise_requisito_ecommerce_v2_0.pdf)
- [Modelo lógico aprovado](../../../models/logical/logical_schema.dbml)
- [Política oficial de versões do PostgreSQL](https://www.postgresql.org/support/versioning/)
- [Documentação do PostgreSQL 18](https://www.postgresql.org/docs/18/)
- [Documentação do driver PostgreSQL no DBeaver](https://dbeaver.com/docs/dbeaver/Database-driver-PostgreSQL/)
