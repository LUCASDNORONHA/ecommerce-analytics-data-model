# Instruções para agentes

## Objetivo do projeto

Este repositório desenvolve um modelo de dados relacional para analisar o desempenho logístico de um e-commerce usando o Brazilian E-Commerce Public Dataset by Olist.

O trabalho evolui pelas milestones M01 a M06: análise de requisitos, modelagem conceitual, modelagem lógica, modelagem física, carga de dados e análise. Consulte o GitHub Project nº 6 antes de iniciar uma tarefa. No momento, a milestone ativa é M02 — Modelagem Conceitual.

## Fontes de verdade

- GitHub Project: prioridade, status, sprint e ordem de execução;
- issue: contexto, objetivo, escopo e critérios de aceitação da entrega;
- repositório: código, notebooks e documentação aprovados;
- `docs/requirements/`: requisitos do domínio;
- `docs/WORKFLOW.md`: regras de gestão do trabalho;
- `CONTRIBUTING.md`: convenções de branch, commit e pull request.

Quando houver divergência, não invente uma decisão de domínio. Registre a inconsistência na issue e preserve a rastreabilidade da escolha.

## Estrutura relevante

- `data/raw/`: CSVs locais e não versionados;
- `docs/requirements/`: análise de requisitos aprovada;
- `models/conceptual/`: artefatos do modelo conceitual e MER;
- `models/logical/`: artefatos do modelo lógico relacional;
- `models/physical/`: DDL e artefatos do modelo físico;
- `notebooks/`: entregas versionadas de exploração e validação;
- `scripts/`: fontes Python locais pareadas por Jupytext, ignoradas pelo Git.

Não crie arquivos na raiz quando já existir um diretório próprio para o artefato.

## Ambiente e dependências

O projeto usa Python 3.12 e `uv`. Não use `pip`, Poetry ou Conda para alterar o ambiente do projeto.

```bash
uv sync --locked --all-groups
uv lock --check
```

Ao adicionar ou remover dependências, edite `pyproject.toml` com `uv add` ou `uv remove` e versione também o `uv.lock` atualizado.

## Regra obrigatória para notebooks

O desenvolvimento interativo ocorre em arquivos Python no formato `py:percent`, dentro de `scripts/`. A entrega oficial é sempre o notebook correspondente em `notebooks/`.

- toda célula de código começa com `# %%`;
- toda célula Markdown começa com `# %% [markdown]`;
- todo script deve possuir um notebook pareado por Jupytext;
- sincronize o par depois de alterar o script;
- nunca adicione `scripts/` ao Git;
- versione o `.ipynb` resultante;
- não deixe erros de execução, rastros de depuração ou saídas excessivas no notebook entregue.

Exemplo:

```bash
uv run jupytext --sync scripts/data_understanding/01_validacao_entidades.py
uv run jupytext --to py:percent --test 'notebooks/**/*.ipynb'
```

Se uma tarefa não for adequada a notebook, justifique na issue e use o diretório correspondente em `models/` ou `docs/`.

## Dados e segurança

- nunca versione os CSVs de `data/raw/`;
- não altere dados brutos para fazer uma validação passar;
- trate a origem como imutável e faça transformações de modo reproduzível;
- não inclua credenciais, tokens, caminhos pessoais ou conteúdo da `.env`;
- não versione bancos locais, caches, ambientes virtuais ou arquivos gerados;
- use caminhos relativos à raiz do repositório nos artefatos entregues.

## Fluxo de trabalho

1. Leia a issue ativa e confirme seus critérios de aceitação.
2. Trabalhe em apenas uma issue com status **Em andamento**.
3. Crie a branch somente quando a tarefa começar, sempre a partir da `main` atualizada.
4. Use o padrão `<tipo>/<numero>-<descricao-curta>` para branches.
5. Faça mudanças limitadas ao escopo da issue e preserve alterações do usuário.
6. Sincronize os notebooks e execute as verificações locais.
7. Abra um pull request com `Closes #<numero>` e mova a issue para **Em validação**.
8. Faça squash merge somente depois da CI aprovada e dos critérios revisados.
9. Confirme o fechamento da issue e o status **Concluído**; a branch deve ser excluída.

Não crie branches para tarefas futuras. Não inicie uma tarefa P1 ou P2 enquanto houver uma P0 ativa sem registrar a mudança de prioridade no Project.

## GitHub Project

Use estes significados:

- **Backlog:** demanda registrada, ainda fora da execução;
- **Pronto para Desenvolvimento:** escopo compreendido e sem bloqueios;
- **Em Andamento:** única tarefa ativa;
- **Em Validação:** entrega implementada, aguardando revisão ou merge;
- **Concluído:** critérios atendidos, PR integrado e issue encerrada;
- **P0:** trabalho ativo ou bloqueio;
- **P1:** próximo trabalho preparado;
- **P2:** trabalho futuro.

Não atribua datas, sprint, pontos ou dificuldade sem refinar a tarefa. Não marque critérios como concluídos sem evidência no repositório ou no pull request. Mantenha milestones como fases e issues como entregas verificáveis.

## Qualidade e validação

Antes de abrir ou atualizar um pull request, execute:

```bash
uv sync --locked --all-groups
uv lock --check
uv run jupytext --to py:percent --test 'notebooks/**/*.ipynb'
git diff --check
```

Valide também o artefato específico da tarefa. Análises devem apresentar resultados legíveis, conclusões coerentes com os dados e explicações suficientes para serem compreendidas sem consultar o script local.

Não execute notebooks na CI quando eles dependerem dos CSVs locais ignorados. Nesse caso, valide estrutura, pareamento e ausência de erro nos artefatos versionados.

## Convenções de alteração

Use commits no padrão:

- `feat:` para nova entrega;
- `fix:` para correção;
- `docs:` para documentação;
- `chore:` para manutenção e automação.

Prefira commits pequenos e descritivos. Não reescreva histórico publicado, não force push e não use comandos destrutivos sem solicitação explícita.

## Critério de conclusão do agente

Uma solicitação só está concluída quando o artefato foi produzido no local correto, as verificações relevantes passaram, a documentação afetada foi atualizada e o estado do GitHub corresponde ao estado real do trabalho. Ao entregar, informe objetivamente o que mudou, como foi validado e qual é a próxima tarefa priorizada.
