# Notebooks de modelagem de dados

Este diretório reúne as evidências empíricas que sustentam a modelagem
conceitual aprovada. Os notebooks devem ser lidos na ordem numérica:

1. `01_validacao_entidades.ipynb`;
2. `02_validacao_atributos.ipynb`;
3. `03_validacao_relacionamentos.ipynb`;
4. `04_validacao_cardinalidades.ipynb`;
5. `05_validacao_prefixo_cep.ipynb`.

As análises dependem dos CSVs originais em `data/raw/`. Esses arquivos não são
versionados e devem ser tratados como imutáveis.

Os notebooks são editados diretamente, sem cópias Python pareadas. Suas
conclusões sustentam os artefatos em `models/conceptual/` e a documentação em
`docs/modeling/conceptual/`; mudanças em decisões aprovadas exigem justificativa
e rastreabilidade próprias.
