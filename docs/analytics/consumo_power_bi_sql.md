# Contrato de consumo no Power BI e SQL

## 1. Objetivo

Este documento consolida o contrato de consumo da M06-06. Ele organiza as views
aprovadas do schema `analytics` como datasets para exploração SQL e construção
futura de um modelo semântico no Power BI, sem copiar dados da CORE nem criar
novas estruturas sem necessidade demonstrada.

O contrato cobre nomes, granularidades, chaves, relacionamentos, medidas,
filtros, atualização, controles e limitações. A criação de um arquivo `.pbix`,
de páginas ou de visuais não faz parte desta entrega.

## 2. Decisão de arquitetura

As quatro views criadas na M06-05 já estabilizam as regras recorrentes e são as
fontes canônicas de consumo. A M06-06 não cria marts adicionais porque:

- as granularidades de pedido, mês, vendedor-pedido e vendedor já estão
  explícitas;
- as combinações de itens, pagamentos e avaliações já são protegidas contra
  multiplicação de medidas;
- não existe evidência de requisito de desempenho que justifique
  materialização;
- novas cópias aumentariam o risco de divergência sem acrescentar semântica.

Para exportações controladas, `queries/consumption/` expõe listas explícitas de
colunas. Consumidores com acesso direto ao PostgreSQL podem consultar as views
ou usar essas consultas como instruções SQL no conector.

## 3. Datasets

| Nome recomendado no BI | Fonte canônica | Granularidade | Chave | Uso principal |
|---|---|---|---|---|
| `fato_pedido_financeiro` | `analytics.vw_pedido_financeiro` | Um pedido, incluindo todos os status | `id_pedido` | Detalhe financeiro, operacional e reconciliação |
| `agregado_financeiro_mensal` | `analytics.vw_financeiro_mensal` | Um mês de compra | `mes_compra` | Série executiva pronta para SQL e controles mensais |
| `fato_vendedor_pedido` | `analytics.vw_vendedor_pedido` | Um vendedor em um pedido entregue | `id_vendedor`, `id_pedido` | Evolução, alcance e risco associado ao vendedor |
| `resumo_desempenho_vendedor` | `analytics.vw_desempenho_vendedor` | Um vendedor ativo no histórico entregue | `id_vendedor` | Ranking, curva ABC e perfil histórico |

Os valores de `fato_vendedor_pedido` são contribuições diretas dos itens do
vendedor. Entrega e avaliação são apenas associadas ao pedido. Pagamentos não
são alocados ao vendedor.

## 4. Perfil recomendado de importação

### 4.1. Modelo semântico principal

Importar:

- `fato_pedido_financeiro` para análises financeiras e operacionais;
- `fato_vendedor_pedido` para análises temporais de vendedores;
- `resumo_desempenho_vendedor` para ranking e segmentação histórica.

Criar no Power BI uma dimensão calendário contínua entre as datas mínima e
máxima de compra. A coluna de data deve ser relacionada, com direção única, a
`data_compra` das duas tabelas fato. Para uso mensal, a dimensão deve expor ano,
mês, número do mês e uma chave `AAAA-MM` com ordenação cronológica.

Relacionamento permitido:

```text
dim_calendario[data]
    1 ─── * fato_pedido_financeiro[data_compra_data]
    1 ─── * fato_vendedor_pedido[data_compra_data]

resumo_desempenho_vendedor[id_vendedor]
    1 ─── * fato_vendedor_pedido[id_vendedor]
```

`data_compra_data` representa uma coluna derivada somente com a data de
`data_compra`. O filtro deve fluir da dimensão para os fatos. Não usar direção
bidirecional como configuração padrão.

### 4.2. Agregado mensal

`agregado_financeiro_mensal` é opcional no modelo Power BI. Ele é recomendado
para consulta SQL direta, validação e protótipos executivos. Quando importado no
mesmo modelo, deve permanecer separado ou ser relacionado por uma dimensão de
mês com chave única.

Não somar suas medidas com medidas calculadas a partir de
`fato_pedido_financeiro`; ambas representam o mesmo domínio em granularidades
diferentes.

### 4.3. Relacionamentos proibidos

- não relacionar diretamente `fato_pedido_financeiro` e
  `fato_vendedor_pedido` por `id_pedido` para calcular valores financeiros;
- não usar `id_cliente` como dimensão persistente de pessoa; a identidade
  recorrente disponível é `id_cliente_unico`;
- não combinar as tabelas por cidade sem estado;
- não expandir geolocalização por prefixo de CEP, pois ela possui múltiplas
  ocorrências e multiplicaria linhas.

## 5. Propriedade das medidas

| Tema | Dataset proprietário | Regra |
|---|---|---|
| Valores e contagens de pedido | `fato_pedido_financeiro` | Agregar uma vez por `id_pedido` |
| Evolução financeira pronta | `agregado_financeiro_mensal` | Usar somente como agregado mensal |
| Valores e volumes do vendedor | `fato_vendedor_pedido` | Somar contribuições diretas do vendedor |
| Ranking e concentração histórica | `resumo_desempenho_vendedor` | Não recalcular como série temporal |
| Pagamentos | `fato_pedido_financeiro` | Nunca atribuir integralmente ao vendedor |
| Entrega e avaliação por vendedor | `fato_vendedor_pedido` | Nomear como informação associada |

Medidas de pedido devem ser calculadas em `fato_pedido_financeiro`; medidas de
vendedor devem ser calculadas em `fato_vendedor_pedido`. Essa separação evita
que um pedido multivendedor repita valor bruto, pagamento ou avaliação.

## 6. Medidas mínimas no Power BI

As medidas abaixo são referências para o modelo semântico. Os percentuais são
razões e devem receber formatação percentual no Power BI, sem multiplicação
adicional por 100.

```DAX
Pedidos =
DISTINCTCOUNT ( fato_pedido_financeiro[id_pedido] )

Pedidos Entregues =
CALCULATE (
    [Pedidos],
    fato_pedido_financeiro[status_pedido] = "delivered"
)

Pedidos Entregues Completos =
CALCULATE (
    [Pedidos Entregues],
    fato_pedido_financeiro[possui_itens] = TRUE (),
    fato_pedido_financeiro[possui_pagamentos] = TRUE ()
)

Valor dos Itens Entregues =
CALCULATE (
    SUM ( fato_pedido_financeiro[valor_itens] ),
    fato_pedido_financeiro[status_pedido] = "delivered",
    fato_pedido_financeiro[possui_itens] = TRUE (),
    fato_pedido_financeiro[possui_pagamentos] = TRUE ()
)

Valor Bruto Entregue =
CALCULATE (
    SUM ( fato_pedido_financeiro[valor_bruto] ),
    fato_pedido_financeiro[status_pedido] = "delivered",
    fato_pedido_financeiro[possui_itens] = TRUE (),
    fato_pedido_financeiro[possui_pagamentos] = TRUE ()
)

Valor Pago Registrado Entregue =
CALCULATE (
    SUM ( fato_pedido_financeiro[valor_pago_registrado] ),
    fato_pedido_financeiro[status_pedido] = "delivered",
    fato_pedido_financeiro[possui_itens] = TRUE (),
    fato_pedido_financeiro[possui_pagamentos] = TRUE ()
)

Diferença de Reconciliação Entregue =
[Valor Pago Registrado Entregue] - [Valor Bruto Entregue]

Valor Bruto Médio por Pedido Entregue =
DIVIDE (
    [Valor Bruto Entregue],
    [Pedidos Entregues Completos]
)

Participação do Frete =
DIVIDE (
    CALCULATE (
        SUM ( fato_pedido_financeiro[valor_frete] ),
        fato_pedido_financeiro[status_pedido] = "delivered",
        fato_pedido_financeiro[possui_itens] = TRUE (),
        fato_pedido_financeiro[possui_pagamentos] = TRUE ()
    ),
    [Valor Bruto Entregue]
)

Taxa de Cancelamento =
VAR PedidosCancelados =
    CALCULATE (
        [Pedidos],
        REMOVEFILTERS ( fato_pedido_financeiro[status_pedido] ),
        fato_pedido_financeiro[status_pedido] = "canceled"
    )
VAR TodosPedidos =
    CALCULATE (
        [Pedidos],
        REMOVEFILTERS ( fato_pedido_financeiro[status_pedido] )
    )
RETURN
    DIVIDE ( PedidosCancelados, TodosPedidos )

Valor dos Itens por Vendedor =
SUM ( fato_vendedor_pedido[valor_itens] )

Taxa de Itens Enviados Após o Limite =
DIVIDE (
    SUM ( fato_vendedor_pedido[itens_enviados_apos_limite] ),
    SUM ( fato_vendedor_pedido[itens_com_envio_observado] )
)
```

O crescimento mensal deve ser calculado apenas entre meses de cobertura diária
completa. A definição canônica já está em
`agregado_financeiro_mensal[crescimento_mensal_valor_itens_percentual]`;
reimplementações em DAX devem reproduzir essa condição.

## 7. Tipos e formatação

| Grupo | Tratamento recomendado |
|---|---|
| Identificadores | Texto; nunca resumir |
| Datas e timestamps | Data ou data/hora conforme a coluna original |
| Valores monetários | Número decimal fixo, moeda BRL |
| Contagens | Número inteiro |
| Flags | Booleano |
| Taxas das views | Número decimal já expresso em pontos percentuais |
| Taxas DAX com `DIVIDE` | Número decimal formatado como percentual |
| Notas | Número decimal, sem formatação percentual |

As colunas percentuais das views SQL já estão multiplicadas por 100. Por
exemplo, `9.32` significa `9,32%`. Medidas DAX baseadas em `DIVIDE` retornam
`0.0932` e devem apenas receber o formato percentual.

## 8. Filtros e interpretação

- a data principal é `data_compra`;
- a visão financeira principal usa pedidos `delivered` com itens e pagamentos;
- meses sem cobertura diária completa não sustentam comparações de crescimento;
- valores associados a cancelados não representam perda, estorno ou receita;
- `cidade_cliente` e `estado_cliente` representam localização cadastral, não o
  endereço exato da entrega;
- alcance geográfico é observado na base, não cobertura comercial formal;
- atraso e avaliação associados ao vendedor não demonstram responsabilidade ou
  causalidade;
- HHI e participação representam somente a base histórica observada.

## 9. Atualização e segurança

As views são normais e refletem o estado corrente da CORE. A sequência de
atualização é:

```text
CSV → RAW → CORE → validações do ELT → views ANALYTICS → atualização do BI
```

O Power BI deve usar uma credencial PostgreSQL de leitura com acesso apenas aos
objetos necessários. `DATABASE_URL`, senhas e arquivos locais não devem ser
incorporados ao repositório ou às consultas versionadas.

O modo **Importação** é o padrão recomendado para esta base histórica. O uso de
DirectQuery, atualização incremental, agregações automáticas ou views
materializadas depende de medição de desempenho e de um requisito operacional
futuro.

## 10. Controles antes da publicação

Antes de atualizar ou publicar um modelo semântico:

1. executar o ELT e a validação independente;
2. executar `queries/validation/06_views_analytics.sql`;
3. confirmar unicidade de `id_pedido`, `mes_compra` e `id_vendedor` nas fontes
   correspondentes;
4. confirmar unicidade do par `id_vendedor`, `id_pedido`;
5. comparar totais financeiros do BI com `vw_financeiro_mensal`;
6. verificar tipos, formatos, direção de filtros e relacionamentos ativos;
7. registrar data da atualização e período coberto.

## 11. Limitações e evolução

Este contrato prepara o consumo, mas não entrega monitoramento em tempo real,
governança de workspace, gateway, política de acesso, atualização agendada ou
design visual. Esses elementos dependem do ambiente Power BI de destino.

Também não há evidência atual para materializar views ou criar índices
específicos. Qualquer evolução deve partir de medição reproduzível e preservar
a rastreabilidade até as tabelas CORE.
