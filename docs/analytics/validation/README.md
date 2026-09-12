# Validação da documentação analítica

Revisão realizada em 9 de setembro de 2026 sobre `camada_analitica.tex` e o
[PDF consolidado](../camada_analitica.pdf), compilado com XeLaTeX via latexmk.
O resultado possui 45 páginas. A compilação terminou sem avisos de largura,
referências ou fontes. O ambiente utilizou as fontes alternativas declaradas
na fonte quando Arial e Consolas não estavam disponíveis.

As tabelas receberam cabeçalhos azuis, texto branco e linhas alternadas.
A matriz de requisitos e os catálogos financeiro e de vendedores utilizam
páginas em paisagem, larguras específicas e cabeçalhos repetidos. Seus títulos
permanecem junto às tabelas. Foram corrigidos espaços excedentes no cabeçalho
e a quebra de linha de Financeiro/executivo.

A revisão visual abrangeu a paginação geral e a inspeção ampliada das tabelas
mais densas, sem cortes, sobreposições ou invasão de colunas observados.
As imagens abaixo registram as primeiras páginas das três tabelas principais:

- [Matriz de requisitos, página 24](matriz-requisitos.jpg).
- [Métricas financeiras, página 29](metricas-financeiras.jpg).
- [Métricas de vendedores, página 31](metricas-vendedores.jpg).

As referências a tarefas de gestão foram substituídas por descrições das
atividades. Fórmulas, valores, granularidades e referências aos artefatos
analíticos foram preservados. SQL, ELT, DAX, PBIR e TMDL não foram alterados.

A validação local aprovou sincronização do ambiente, lockfile, lint,
formatação e 57 testes automatizados. Os três testes de integridade de
artefatos são descobertos pelo comando já utilizado na CI; verificam links
locais Markdown, sintaxe JSON de arquivos e notebooks e marcadores básicos
dos PDFs. Esses marcadores não substituem a revisão visual ou a compilação.

O checklist Power BI recebeu somente evidências dos testes estáticos
existentes; itens manuais sem evidência específica não foram marcados.

## Segurança do repositório

A consulta à API do GitHub confirmou a proteção da main: PR obrigatório,
verificação `Validar projeto`, branch atualizada, aplicação a administradores,
force push e exclusão desabilitados. Foram habilitados e confirmados:

- alertas de vulnerabilidades;
- atualizações de segurança do Dependabot;
- detecção de segredos;
- proteção contra envio de segredos.

Essas configurações residem no GitHub e não são reproduzidas por um clone.
A revisão registra sua ativação, não a ausência de vulnerabilidades.
Branches locais obsoletas não foram removidas: essa organização depende da
confirmação específica prevista no escopo da auditoria.
