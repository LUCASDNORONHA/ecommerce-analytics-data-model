# Modelo físico

Este diretório contém os scripts PostgreSQL que materializam a arquitetura
física nos schemas `raw`, `core` e `analytics`.

## Arquivos

- `create_schema.sql`: cria os três schemas, nove tabelas RAW e nove tabelas CORE com suas constraints;
- `create_indexes.sql`: cria os seis índices adicionais aprovados no CORE;
- `drop_indexes.sql`: remove somente os índices adicionais;
- `drop_schema.sql`: remove as tabelas e os schemas em ordem segura;
- `validate_schema.sql`: valida catálogo e comportamento sem persistir dados de teste.

## Execução no DBeaver

1. conecte o DBeaver a uma instância PostgreSQL 18;
2. abra um editor SQL associado ao banco de destino;
3. carregue e execute `create_schema.sql` como script;
4. execute `create_indexes.sql` após a criação do modelo;
5. execute `validate_schema.sql` para validar a estrutura;
6. confirme o `COMMIT` e atualize a árvore de objetos;
7. inspecione os schemas `raw`, `core` e `analytics` e suas tabelas RAW e CORE.

Para remover o modelo, execute `drop_schema.sql` no mesmo banco. O script de
remoção elimina objetos e deve ser usado somente em um ambiente descartável ou
com autorização explícita.

## Comportamento esperado

- a criação deve ocorrer em um banco no qual os schemas `raw`, `core` e `analytics` ainda não existam;
- uma falha durante a criação aborta a transação e evita um modelo parcial;
- a repetição de `create_schema.sql` sem remoção prévia falha intencionalmente,
  protegendo objetos existentes contra redefinição silenciosa;
- o script de schema não cria banco, usuário, credenciais, índices adicionais ou dados;
- PKs e a constraint `UNIQUE` criam os índices necessários à sua implementação;
  outros índices dependem de evidência produzida nas etapas de carga e análise.

## Referências

- [Documentação consolidada da modelagem física](../../docs/modeling/physical/physical_model.pdf)
- [Fonte LaTeX da documentação](../../docs/modeling/physical/physical_model.tex)
- [Modelo lógico aprovado](../logical/logical_schema.dbml)
