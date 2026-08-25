# Dados

Este diretório armazena os dados utilizados no projeto.

## Estrutura

- `raw/`: arquivos originais, mantidos sem alterações;
- `processed/`: dados tratados ou derivados, quando essa etapa for implementada.

Os arquivos CSV não são versionados por causa do tamanho e para manter o repositório leve. Baixe o [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) e extraia os arquivos em `data/raw/`.

O conteúdo de `data/raw/` deve preservar os nomes e a estrutura originais do dataset, pois os notebooks utilizam esses caminhos como entrada.
