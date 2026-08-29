# Pipeline Completo RAW → CORE

## 1. Objetivo

Esta implementação transforma as nove tabelas RAW no modelo relacional CORE e
oferece um comando único para executar CSV → RAW → CORE em uma transação
PostgreSQL. Uma falha em qualquer arquivo, tabela, conversão, constraint ou
reconciliação reverte as duas camadas e preserva a versão anterior.

## 2. Artefatos

- `etl/sql/load_core.sql`: transformações SQL na ordem de dependências;
- `etl/core_loader.py`: execução e reconciliação do CORE a partir da RAW atual;
- `etl/pipeline.py`: orquestração atômica dos CSVs até o CORE;
- `config/core_load.toml`: caminhos, logs e timeouts do CORE;
- `tests/test_core_loader.py`: testes automatizados das transformações.

## 3. Transformações implementadas

O SQL executa:

1. substituição conjunta das nove tabelas CORE com `RESTART IDENTITY`;
2. derivação de `core.prefixo_cep` por união distinta de três origens;
3. carga de cliente, produto e vendedor;
4. carga de pedido e geolocalização;
5. carga de item do pedido, pagamento e avaliação;
6. conversões explícitas para inteiros, decimais, timestamps e coordenadas;
7. consolidação das duplicidades integrais de geolocalização;
8. geração de `id_geolocalizacao` pelo PostgreSQL.

Textos não utilizam casts explícitos para `varchar(n)` ou `char(n)`. A coerção
de atribuição das colunas rejeita valores longos, evitando a truncagem que um
cast explícito poderia realizar silenciosamente.

Título e mensagem de avaliações e a tabela de tradução de categorias permanecem
na RAW, pois não possuem destino no modelo CORE aprovado.

## 4. Comandos

Pré-validação sem banco:

```bash
uv run python -m etl.pipeline --validate-only
```

Pipeline completo e atômico:

```bash
export DATABASE_URL="postgresql://usuario:senha@localhost:5432/ecommerce"
uv run python -m etl.pipeline
```

Transformação somente da RAW já carregada para o CORE:

```bash
uv run python -m etl.core_loader
```

O banco deve ter recebido previamente `create_schema.sql` e
`create_indexes.sql`. Credenciais são fornecidas somente pelo ambiente local.

## 5. Atomicidade

O comando completo:

1. pré-valida os nove CSVs;
2. abre uma conexão;
3. substitui e reconcilia a RAW;
4. verifica a presença das nove tabelas RAW carregadas;
5. substitui e transforma o CORE;
6. reconcilia as nove tabelas CORE;
7. confirma a transação.

O contexto transacional é controlado pelo `psycopg`. Os arquivos SQL não
possuem `BEGIN` ou `COMMIT`, evitando confirmações intermediárias.

Se o CORE falhar depois da recarga da RAW, o rollback restaura tanto a RAW
quanto o CORE anteriores.

## 6. Reconciliação CORE

As contagens esperadas são calculadas a partir da RAW da própria execução:

- tabelas com mapeamento direto usam o volume da fonte correspondente;
- `prefixo_cep` usa a união distinta dos três atributos de CEP;
- `geolocalizacao` usa a quantidade de combinações distintas das cinco colunas
  de negócio.

| Tabela CORE | Volume do snapshot validado |
|---|---:|
| `prefixo_cep` | 19.177 |
| `cliente` | 99.441 |
| `produto` | 32.951 |
| `vendedor` | 3.095 |
| `pedido` | 99.441 |
| `item_pedido` | 112.650 |
| `pagamento` | 103.886 |
| `avaliacao` | 99.224 |
| `geolocalizacao` | 738.332 |
| **Total físico** | **1.308.197** |

Constraints do modelo físico permanecem habilitadas durante toda a carga.

## 7. Logs

O pipeline completo grava:

```text
outputs/data-loading/logs/full_load_<run_id>.json
```

O registro contém:

- perfil e hashes das nove fontes;
- reconciliação das nove tabelas RAW;
- hash SHA-256 do SQL de transformação;
- volumes RAW utilizados pelo CORE;
- reconciliação das nove tabelas CORE;
- início, término, modo, status e erro, quando houver.

Logs operacionais permanecem locais e não incluem a `DATABASE_URL`.

## 8. Evidência de validação integrada

A implementação foi exercitada em PostgreSQL 18.6 temporário e isolado:

- `create_schema.sql` executado com sucesso;
- `create_indexes.sql` executado com sucesso;
- 1.550.922 registros reconciliados na RAW;
- 1.308.197 registros reconciliados no CORE;
- duas execuções completas consecutivas aprovadas, sem acumulação;
- 261.831 duplicidades integrais de geolocalização consolidadas;
- zero constraints desabilitadas.

Também foi adicionada deliberadamente uma divisão por zero ao final de uma cópia
temporária do SQL. A falha ocorreu depois de RAW e todas as inserções CORE terem
sido executadas. O timestamp máximo de `_carregado_em` da RAW permaneceu
inalterado e `core.cliente` preservou seus 99.441 registros anteriores,
confirmando o rollback conjunto.

Essa instância temporária valida tecnicamente a implementação, mas não substitui
o registro da execução na base alvo persistente. Essa execução requer a
`DATABASE_URL` fornecida pelo ambiente responsável pelo banco.

## 9. Falhas esperadas

- conversão inválida: aborta antes do commit e registra o erro do PostgreSQL;
- violação de PK, FK, `UNIQUE` ou `CHECK`: aborta e preserva as duas camadas;
- tabela RAW vazia: impede a transformação do CORE;
- contagem divergente: reprova a reconciliação e executa rollback;
- SQL ausente ou alterado: o caminho é validado e seu hash aparece no log;
- lock indisponível: respeita o timeout configurado.

## 10. Testes

Execute:

```bash
uv run python -m unittest discover -s tests -v
```

Além dos testes anteriores da RAW, a suíte verifica:

- leitura da configuração CORE;
- presença das nove inserções;
- ausência de controle transacional dentro do SQL;
- deduplicação pelas cinco colunas de geolocalização;
- ausência de casts textuais truncantes;
- execução e reconciliação das nove tabelas.

## 11. Próximo passo

Depois da execução registrada na base alvo, a M05-06 deve validar volumes,
chaves, referências, constraints, exceções e regras de qualidade pós-carga,
produzindo o relatório final de reconciliação do ELT.
