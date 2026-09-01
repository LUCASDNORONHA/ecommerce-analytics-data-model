# Modelos analíticos

Fontes SQL editáveis das estruturas persistentes do schema `analytics`, como
views, tabelas derivadas e marts. A criação de cada estrutura exige necessidade
analítica demonstrada e rastreabilidade até o modelo `core`.

As definições de views devem ser armazenadas em `views/`.

O `database.setup` executa os arquivos de `views/` em ordem lexicográfica e,
em seguida, executa `validate_views.sql`. Os prefixos numéricos representam
dependências reais entre as estruturas, não uma cronologia geral do projeto.
