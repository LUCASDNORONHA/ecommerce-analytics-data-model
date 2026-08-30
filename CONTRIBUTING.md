# Guia de contribuição

Este projeto usa o GitHub Project como fonte de verdade do trabalho e o repositório como fonte de verdade dos artefatos. Antes de iniciar uma alteração, confirme que existe uma issue com objetivo e critérios de aceitação claros.

## Fluxo de trabalho

1. Selecione a primeira issue em **Pronto para desenvolvimento**.
2. Mova somente essa issue para **Em andamento** (limite de trabalho em progresso: 1).
3. Atualize a `main` e crie a branch a partir dela:

   ```bash
   git switch main
   git pull --ff-only
   git switch -c <tipo>/<numero>-<descricao-curta>
   ```

4. Faça commits pequenos no padrão `<tipo>: <descrição>`.
5. Crie e edite notebooks diretamente em `notebooks/`, quando necessários.
6. Abra um pull request vinculado à issue com `Closes #<numero>`.
7. Após as verificações automáticas, revise os critérios de aceitação e faça squash merge.

Não crie antecipadamente branches de tarefas futuras. Cada branch nasce da `main` atual quando o trabalho começa e é excluída após o merge.

## Convenções

Tipos de branch e commit:

- `feat`: novo artefato ou capacidade;
- `fix`: correção de comportamento ou conteúdo;
- `docs`: documentação;
- `chore`: manutenção, organização e automação.

Exemplo: `feat/10-definir-chaves-primarias` e `feat: documentar chaves primárias conceituais`.

### Numeração de artefatos

Use prefixos de dois dígitos (`01_`, `02_`, `03_`) somente quando os arquivos formarem uma sequência real de leitura ou execução. Notebooks sequenciais e coleções SQL ordenadas devem seguir essa convenção.

Não numere diretórios arquiteturais, módulos Python, testes ou arquivos independentes apenas para reproduzir a cronologia geral do projeto. A ordem das etapas é documentada no README principal; os nomes no repositório devem continuar representando a responsabilidade técnica de cada artefato.

## Consultas, scripts e notebooks

Consultas SQL exploratórias e analíticas devem ser versionadas em `queries/`. Estruturas persistentes do schema `analytics` pertencem a `models/analytics/`. Notebooks são criados e editados diretamente em `notebooks/`.

O diretório `scripts/` é reservado a utilitários necessários e versionados. Não duplique notebooks em scripts Python pareados.

Antes do commit, execute:

```bash
uv sync --locked --all-groups
uv lock --check
uv run ruff check .
uv run ruff format --check .
uv run python -m unittest discover -s tests -v
```

Não versione CSVs de origem, bancos locais, credenciais, ambientes virtuais ou saídas geradas.

## Definição de pronto

Uma tarefa só pode ser concluída quando:

- todos os critérios de aceitação estiverem atendidos e marcados;
- o artefato final estiver versionado no diretório correto;
- a documentação afetada estiver atualizada;
- as verificações automáticas estiverem aprovadas;
- o pull request estiver vinculado à issue e integrado à `main`.
