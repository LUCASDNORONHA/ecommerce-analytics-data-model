# ---
# jupyter:
#   jupytext:
#     formats: notebooks///ipynb,scripts///py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: sgli-data-model (3.12.3)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Validação das entidades
#
# ## Introdução
#
# Após a conclusão da análise de requisitos, faz-se necessária a transição para a
# modelagem conceitual de dados. Nesta etapa, a identificação das entidades
# constitui o primeiro passo para a formalização estrutural do domínio, assegurando
# que os principais elementos do problema de negócio sejam corretamente
# representados no modelo.
#
# Embora o documento de requisitos já apresente uma lista preliminar de entidades,
# é imprescindível validá-las e refiná-las à luz do dataset e das regras de negócio
# estabelecidas, evitando redundâncias, omissões ou inconsistências conceituais.
#
# ## Objetivo
#
# Definir, de forma precisa e consistente, o conjunto final de entidades que
# compõem o domínio do modelo de dados, garantindo aderência ao problema de
# negócio e ao dataset utilizado.

# %%
from pathlib import Path

import pandas as pd
from IPython.display import Markdown, display

data_directories = (Path("data/raw"), Path("../../data/raw"))
data_dir = next((path for path in data_directories if path.is_dir()), None)

if data_dir is None:
    raise FileNotFoundError(
        "Diretório data/raw não encontrado. Consulte data/README.md para obter os dados."
    )

customers = pd.read_csv(data_dir / "olist_customers_dataset.csv")
geolocation = pd.read_csv(data_dir / "olist_geolocation_dataset.csv")
order_items = pd.read_csv(data_dir / "olist_order_items_dataset.csv")
order_payments = pd.read_csv(data_dir / "olist_order_payments_dataset.csv")
order_reviews = pd.read_csv(data_dir / "olist_order_reviews_dataset.csv")
orders = pd.read_csv(data_dir / "olist_orders_dataset.csv")
products = pd.read_csv(data_dir / "olist_products_dataset.csv")
sellers = pd.read_csv(data_dir / "olist_sellers_dataset.csv")
product_category_name_translation = pd.read_csv(
    data_dir / "product_category_name_translation.csv"
)

# %% [markdown]
# ## 1. Inventário das fontes de dados
#
# O dataset é composto por nove arquivos. Sete representam diretamente entidades
# previstas nos requisitos; os outros dois apoiam o enriquecimento geográfico e a
# tradução das categorias de produtos.

# %%
tabelas = {
    "Clientes": customers,
    "Pedidos": orders,
    "Itens do Pedido": order_items,
    "Produtos": products,
    "Vendedores": sellers,
    "Pagamentos": order_payments,
    "Avaliações": order_reviews,
    "Geolocalização": geolocation,
    "Tradução de Categorias": product_category_name_translation,
}

entidades_do_dominio = {
    "Clientes",
    "Pedidos",
    "Itens do Pedido",
    "Produtos",
    "Vendedores",
    "Pagamentos",
    "Avaliações",
}

resumo_fontes = pd.DataFrame(
    [
        {
            "Fonte": nome,
            "Classificação": (
                "Entidade do domínio"
                if nome in entidades_do_dominio
                else "Tabela auxiliar"
            ),
            "Registros": len(df),
            "Atributos": df.shape[1],
            "Valores ausentes": int(df.isna().sum().sum()),
        }
        for nome, df in tabelas.items()
    ]
)

display(
    resumo_fontes.style.format(
        {
            "Registros": "{:,.0f}",
            "Atributos": "{:,.0f}",
            "Valores ausentes": "{:,.0f}",
        }
    ).hide(axis="index")
)

# %% [markdown]
# ## 2. Validação das entidades previstas
#
# A validação compara as entidades definidas na análise de requisitos com as
# fontes efetivamente disponíveis. Uma entidade é considerada validada quando há
# uma fonte correspondente no dataset.

# %%
validacao_entidades = pd.DataFrame(
    {
        "Entidade prevista": sorted(entidades_do_dominio),
    }
)

validacao_entidades["Fonte encontrada"] = validacao_entidades[
    "Entidade prevista"
].isin(tabelas)
validacao_entidades["Resultado"] = validacao_entidades["Fonte encontrada"].map(
    {True: "Validada", False: "Não encontrada"}
)

display(
    validacao_entidades.drop(columns="Fonte encontrada")
    .style.hide(axis="index")
    .map(
        lambda valor: (
            "color: #137333; font-weight: bold"
            if valor == "Validada"
            else "color: #b3261e; font-weight: bold"
        ),
        subset=["Resultado"],
    )
)

quantidade_prevista = len(entidades_do_dominio)
quantidade_validada = int(validacao_entidades["Fonte encontrada"].sum())

display(
    Markdown(
        f"**Resultado:** {quantidade_validada} de {quantidade_prevista} "
        "entidades previstas foram encontradas no dataset."
    )
)

# %% [markdown]
# ## 3. Atributos identificados
#
# A visão abaixo apresenta cada atributo em uma linha, facilitando a comparação
# com o dicionário de dados e apoiando as próximas decisões sobre chaves,
# relacionamentos e tipos de dados.

# %%
atributos_identificados = pd.DataFrame(
    [
        {
            "Fonte": nome,
            "Atributo": coluna,
            "Tipo inferido": str(df[coluna].dtype),
            "Valores ausentes": int(df[coluna].isna().sum()),
            "Valores únicos": int(df[coluna].nunique(dropna=True)),
        }
        for nome, df in tabelas.items()
        for coluna in df.columns
    ]
)

display(
    atributos_identificados.style.format(
        {
            "Valores ausentes": "{:,.0f}",
            "Valores únicos": "{:,.0f}",
        }
    ).hide(axis="index")
)

# %% [markdown]
# ## 4. Conclusão
#
# As sete entidades previstas no documento de requisitos possuem representação no
# dataset. Geolocalização e Tradução de Categorias foram classificadas como
# tabelas auxiliares, pois complementam outras entidades sem representar processos
# centrais do domínio.
#
# Com a identificação das entidades concluída, a próxima etapa consiste em validar
# seus atributos e definir quais campos atuarão como identificadores e chaves no
# modelo conceitual.
