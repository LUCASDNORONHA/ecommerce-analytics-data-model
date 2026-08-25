# Gestão do projeto

O [GitHub Project](https://github.com/users/LUCASDNORONHA/projects/6) é o quadro operacional deste repositório. Milestones representam fases do projeto; issues representam entregas verificáveis; iterações organizam o trabalho em janelas curtas.

## Estados do quadro

- **Backlog:** demanda registrada, mas ainda não refinada para execução.
- **Pronto para desenvolvimento:** tarefa compreendida, sem bloqueios e com critérios de aceitação.
- **Em andamento:** tarefa que está sendo executada. O limite é uma tarefa por vez.
- **Em validação:** implementação concluída, aguardando revisão ou merge.
- **Concluído:** critérios atendidos, pull request integrado e issue encerrada.

## Prioridade

- **P0:** trabalho ativo ou bloqueio que impede a continuidade;
- **P1:** próximo trabalho preparado;
- **P2:** trabalho futuro, ainda sem urgência operacional.

A prioridade é relativa ao momento atual. Ela deve ser revista quando uma tarefa termina; não representa a importância geral da fase.

## Estimativa

Use pontos para comparar esforço e incerteza, não horas:

- 1: alteração pequena e conhecida;
- 2: tarefa curta com pouca incerteza;
- 3: tarefa média;
- 5: tarefa maior ou com investigação;
- 8: tarefa extensa que deve ser considerada para divisão.

O campo de dificuldade complementa a estimativa: XS, S, M, L e XL.

## Cadência

As iterações duram oito dias. Somente o trabalho pronto e previsto para a janela recebe uma iteração. Datas passadas de tarefas concluídas são mantidas como histórico; datas de tarefas abertas devem refletir o plano vigente.

Ao concluir uma tarefa:

1. mova o item para **Em validação** ao abrir o pull request;
2. faça o merge somente após a CI passar e os critérios serem revisados;
3. encerre a issue e confirme **Concluído** no quadro;
4. atualize a prioridade da próxima tarefa e crie sua branch a partir da `main`.

## Responsabilidades do PO

O papel de PO neste projeto consiste em manter o objetivo da fase claro, ordenar o backlog, validar critérios de aceitação, evitar trabalho simultâneo e registrar decisões. A execução técnica permanece rastreada em issues e pull requests, preservando a relação entre planejamento, código e entrega.
