# Relatório de teste da arquitetura física

## Identificação

- Issue: #38 — [M04-05] Testar a criação da arquitetura física
- Data: 28 de agosto de 2026
- SGBD validado: PostgreSQL 18.3
- Ambiente: contêiner oficial PostgreSQL descartável, sem porta exposta
- Resultado: aprovado

## Escopo

O teste executou os scripts aprovados em uma instância limpa, validou o catálogo
e o comportamento das constraints, confirmou a estratégia de repetição e removeu
todos os objetos ao final.

## Sequência executada

1. inicialização de uma instância PostgreSQL 18 limpa;
2. execução de create_schema.sql;
3. execução de create_indexes.sql;
4. execução de validate_schema.sql;
5. nova execução de create_schema.sql para testar proteção contra redefinição;
6. verificação de que as 18 tabelas originais permaneceram intactas;
7. execução de drop_schema.sql;
8. repetição de drop_schema.sql;
9. confirmação de ausência dos três schemas;
10. remoção do ambiente temporário.

## Validações estruturais

| Verificação | Esperado | Resultado |
|---|---:|---:|
| versão principal do PostgreSQL | 18 | 18 |
| schemas físicos | 3 | 3 |
| tabelas RAW | 9 | 9 |
| tabelas CORE | 9 | 9 |
| tabelas ANALYTICS | 0 | 0 |
| colunas RAW | 79 | 79 |
| colunas CORE | 50 | 50 |
| colunas identity | 10 | 10 |
| chaves primárias | 18 | 18 |
| chaves estrangeiras CORE | 9 | 9 |
| constraints UNIQUE CORE | 1 | 1 |
| índices RAW, todos implícitos por PK | 9 | 9 |
| índices CORE totais | 16 | 16 |
| índices CORE adicionais | 6 | 6 |

As nove FKs foram confirmadas com ON DELETE RESTRICT e ON UPDATE NO ACTION.
Todas as colunas de origem da RAW foram confirmadas como textuais.

## Validações comportamentais

O validador executou inserções dentro de uma transação revertida ao final:

- RAW aceitou deliberadamente strings fora dos domínios de negócio;
- CORE rejeitou prefixo de CEP fora do formato;
- CORE rejeitou chave primária duplicada;
- CORE rejeitou referência órfã;
- nenhuma ocorrência de teste permaneceu após o ROLLBACK.

Esse comportamento confirma a fronteira aprovada: RAW preserva a entrada e CORE
aplica tipos e integridade.

## Reprodutibilidade e repetição

A segunda execução de create_schema.sql foi rejeitada porque o schema RAW já
existia. A falha é intencional: impede redefinição silenciosa e preservou as 18
tabelas criadas anteriormente.

drop_schema.sql foi executado duas vezes. A primeira removeu todas as tabelas e
schemas; a segunda terminou com avisos de objetos ausentes, sem erro. Ao final,
zero schemas entre RAW, CORE e ANALYTICS permaneceram no catálogo.

## Execução no DBeaver

Os scripts são SQL compatível com o editor do DBeaver e devem ser executados na
ordem:

1. create_schema.sql;
2. create_indexes.sql;
3. validate_schema.sql.

O validador termina com a mensagem:

VALIDAÇÃO DA ARQUITETURA FÍSICA: APROVADA

Para um ambiente descartável, drop_schema.sql remove a arquitetura. A operação
é destrutiva e não deve ser executada em ambiente com dados sem autorização.

## Conclusão

A arquitetura física está aprovada para a implementação do processo ELT e para
a carga inicial na RAW. Não foram identificadas pendências estruturais que
impeçam a M05. Avaliações de desempenho após a carga permanecem previstas e não
constituem bloqueio para a criação do banco.

## Artefatos

- [Arquitetura em camadas](layered_architecture.md)
- [Dicionário físico](physical_data_dictionary.md)
- [Estratégia de índices](index_strategy.md)
- [Scripts e instruções](../../../models/physical/README.md)
