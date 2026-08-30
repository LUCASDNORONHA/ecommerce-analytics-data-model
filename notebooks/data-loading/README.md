# Notebooks de carga e qualidade dos dados

Este diretório reúne evidências reproduzíveis da preparação e da validação dos
dados. Os notebooks devem ser lidos na ordem numérica:

1. `01_raw_source_profiling.ipynb`: inventário e perfil estrutural das fontes;
2. `02_raw_to_core_quality_validation.ipynb`: validação das regras adotadas na
   transformação da RAW para a CORE.

As análises dependem dos CSVs originais em `data/raw/`. Resultados gerados
localmente pertencem a `outputs/data-loading/` e não são versionados.

Os notebooks são editados diretamente, sem cópias Python pareadas. Eles
registram evidências da etapa consolidada de carga; as regras reutilizáveis e
operacionais permanecem em `elt/`, `validation/` e `config/`, e não devem existir
apenas nos notebooks.
