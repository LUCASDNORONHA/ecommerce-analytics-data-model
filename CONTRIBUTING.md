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
5. Sincronize o notebook a partir do script local e versione somente o `.ipynb`.
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

## Scripts e notebooks

Os arquivos Python em `scripts/` são fontes locais de trabalho e não são versionados. Cada script deve estar pareado por Jupytext com um notebook em `notebooks/`, que é a entrega oficial.

Antes do commit:

```bash
uv sync --locked
uv run jupytext --sync scripts/<caminho>/<arquivo>.py
uv run jupytext --to py:percent --test notebooks/**/*.ipynb
```

Não versione CSVs de origem, bancos locais, credenciais, ambientes virtuais ou saídas geradas.

## Definição de pronto

Uma tarefa só pode ser concluída quando:

- todos os critérios de aceitação estiverem atendidos e marcados;
- o artefato final estiver versionado no diretório correto;
- a documentação afetada estiver atualizada;
- as verificações automáticas estiverem aprovadas;
- o pull request estiver vinculado à issue e integrado à `main`.
