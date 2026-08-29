# Pipeline de Ingestão da Camada RAW

## 1. Objetivo

O pipeline implementa a ingestão reproduzível e observável dos nove CSVs Olist
nas tabelas do schema `raw`. A rotina preserva os valores da fonte, adiciona os
metadados definidos pelo DDL, reconcilia a carga e publica a nova versão somente
quando todas as verificações são aprovadas.

Esta entrega não transforma dados para o CORE. As regras RAW → CORE permanecem
documentadas e serão consumidas pela etapa posterior.

## 2. Artefatos

- `etl/raw_loader.py`: linha de comando, pré-validação, carga e reconciliação;
- `config/raw_load.toml`: contrato operacional das nove fontes;
- `config/raw_load.env.example`: exemplo sem credenciais;
- `tests/test_raw_loader.py`: testes unitários do pipeline;
- `outputs/data-loading/logs/`: logs JSON locais e não versionados.

## 3. Pré-requisitos

- Python 3.12 e ambiente sincronizado com `uv`;
- PostgreSQL 18 acessível;
- schemas e tabelas criados por `models/physical/create_schema.sql`;
- nove CSVs disponíveis em `data/raw/`;
- usuário de banco autorizado a executar `TRUNCATE`, `COPY` e `SELECT` nas
  tabelas RAW;
- variável `DATABASE_URL` configurada somente no ambiente local.

Sincronize o ambiente:

```bash
uv sync --locked --all-groups
```

## 4. Configuração

O arquivo `config/raw_load.toml` declara:

- diretório dos CSVs;
- diretório local dos logs;
- quantidade obrigatória de fontes;
- tempos máximos para obtenção de locks e execução;
- nome de cada arquivo;
- tabela RAW correspondente;
- nomes e ordem exata das colunas.

Os caminhos relativos são resolvidos a partir da raiz do repositório. Nomes de
tabelas e colunas são validados antes de compor qualquer SQL.

A conexão não é armazenada no TOML. Configure-a no processo que executará a
carga:

```bash
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/ecommerce"
```

Não inclua senhas em commits, logs, notebooks ou argumentos da linha de comando.

## 5. Pré-validação sem banco

Execute:

```bash
uv run python -m etl.raw_loader --validate-only
```

Para cada fonte, a rotina verifica:

- presença do arquivo;
- leitura UTF-8 ou UTF-8 com BOM;
- cabeçalho exato e na ordem contratada;
- quantidade de campos em todas as linhas;
- sintaxe CSV válida;
- quantidade de registros;
- tamanho e hash SHA-256.

Todos os arquivos são validados antes de qualquer conexão ou alteração no
banco. Uma falha em qualquer fonte reprova a execução completa.

## 6. Execução da carga

Com `DATABASE_URL` configurada, execute:

```bash
uv run python -m etl.raw_loader
```

O fluxo é:

1. carregar e validar a configuração;
2. pré-validar integralmente os nove arquivos;
3. abrir uma conexão PostgreSQL;
4. iniciar a transação;
5. truncar conjuntamente as nove tabelas RAW com `RESTART IDENTITY`;
6. carregar cada CSV com `COPY FROM STDIN`;
7. reconciliar volume, origem e metadados de cada tabela;
8. efetivar o commit somente após a nona reconciliação aprovada;
9. gravar o log local da execução.

As colunas técnicas não são fornecidas ao `COPY`. O PostgreSQL gera `_id_raw` e
preenche `_arquivo_origem` e `_carregado_em` pelos defaults definidos no DDL.

O `COPY` usa `FORCE_NULL` para que campos CSV vazios, inclusive quando entre
aspas, sejam representados como SQL `NULL`. Strings não vazias que se pareçam
com marcadores de ausência não são reinterpretadas.

## 7. Atomicidade e recarga

A política é substitutiva. `TRUNCATE` e os nove `COPY` pertencem à mesma
transação PostgreSQL.

Se ocorrer erro de conexão, lock, parsing, `COPY`, metadado ou reconciliação, a
transação é revertida. A carga RAW anterior permanece integralmente disponível.

O tempo padrão para aguardar locks é 30 segundos. O `statement_timeout` fica
desabilitado por padrão para não interromper arquivos grandes, mas pode ser
configurado no TOML quando houver requisito operacional.

## 8. Reconciliação

Para cada tabela, a execução confirma:

- registros carregados iguais às linhas de dados do CSV;
- `_arquivo_origem` igual ao arquivo contratado em todas as linhas;
- `_id_raw`, `_arquivo_origem` e `_carregado_em` sem `NULL`;
- `_id_raw` distinto para todas as ocorrências.

Qualquer divergência lança erro dentro da transação e impede o commit.

No snapshot aprovado, o total esperado na RAW é 1.550.922 registros. O pipeline
não fixa esse número como regra permanente: a contagem observada na
pré-validação é a base da reconciliação da própria execução. Uma mudança
intencional da fonte continua exigindo novo profiling e atualização dos
contratos.

## 9. Logs e observabilidade

Cada execução recebe um UUID e grava:

```text
outputs/data-loading/logs/raw_load_<run_id>.json
```

O log contém:

- início, término, modo e resultado;
- perfil técnico e SHA-256 de cada fonte;
- contagens de reconciliação por tabela;
- tipo e mensagem da falha, quando aplicável.

O diretório `outputs/` é ignorado pelo Git. A `DATABASE_URL` nunca é adicionada
ao log. Mensagens resumidas também são emitidas no terminal.

## 10. Testes

Execute:

```bash
uv run python -m unittest discover -s tests -v
```

Os testes cobrem:

- UTF-8 com BOM;
- cabeçalho divergente;
- quantidade incorreta de colunas;
- encoding inválido;
- resolução de caminhos da configuração;
- rejeição de identificadores SQL inseguros;
- opções obrigatórias do `COPY`;
- truncamento, envio do CSV e reconciliação.

O teste automatizado não necessita de credenciais nem altera PostgreSQL. A
execução integrada na instância alvo deve ocorrer na M05-05, utilizando uma
conexão fornecida pelo ambiente e registrando a evidência real da carga.

Como validação desta implementação, uma instância PostgreSQL 18 temporária e
isolada recebeu o DDL aprovado e duas cargas completas consecutivas. Ambas
reconciliaram 1.550.922 registros sem acumulação. Uma falha deliberada no nono
`COPY`, após as oito tabelas anteriores terem sido recarregadas, confirmou o
rollback e preservou integralmente a versão previamente aprovada.

## 11. Diagnóstico de falhas

- `DATABASE_URL não configurada`: exporte a variável somente no ambiente local;
- `Arquivo obrigatório ausente`: confira `data/raw/` e o TOML;
- `Cabeçalho inválido`: não altere a fonte; compare-a ao contrato de ingestão;
- `CSV malformado` ou `Codificação inválida`: substitua a fonte pelo snapshot
  correto ou registre formalmente a divergência;
- erro de objeto inexistente: execute e valide o DDL físico antes da carga;
- timeout de lock: verifique sessões concorrentes antes de repetir;
- reconciliação reprovada: preserve o log e não force o commit.

## 12. Próximo passo

A M05-05 deve executar o pipeline na base alvo, registrar a carga RAW aprovada e
implementar as transformações para o CORE na ordem de dependências definida no
mapeamento, aplicando as regras de qualidade sem desabilitar constraints.
