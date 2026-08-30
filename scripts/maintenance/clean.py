"""Remove artefatos locais regeneráveis sem tocar em arquivos versionados."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE_NAMES = {
    ".cache",
    ".ipynb_checkpoints",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "__pycache__",
}
LATEX_SUFFIXES = (
    ".aux",
    ".bbl",
    ".blg",
    ".fdb_latexmk",
    ".fls",
    ".lof",
    ".log",
    ".lot",
    ".nav",
    ".out",
    ".snm",
    ".synctex.gz",
    ".toc",
    ".vrb",
    ".xdv",
)


def tracked_paths() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return set(result.stdout.splitlines())


def collect_targets() -> list[Path]:
    targets = {
        path
        for path in ROOT.rglob("*")
        if (path.name in CACHE_NAMES or path.name == "dbml-error.log")
        and not any(
            part in {".git", ".venv", "data"} for part in path.relative_to(ROOT).parts
        )
    }
    outputs = ROOT / "outputs"
    if outputs.exists():
        targets.add(outputs)
    docs = ROOT / "docs"
    if docs.exists():
        targets.update(
            path
            for path in docs.rglob("*")
            if path.is_file() and path.name.endswith(LATEX_SUFFIXES)
        )

    ordered = sorted(targets, key=lambda path: (len(path.parts), str(path)))
    selected: list[Path] = []
    for target in ordered:
        if not any(parent == target or parent in target.parents for parent in selected):
            selected.append(target)
    return selected


def ensure_untracked(targets: list[Path]) -> None:
    tracked = tracked_paths()
    conflicts = []
    for target in targets:
        relative = target.relative_to(ROOT).as_posix()
        if any(path == relative or path.startswith(f"{relative}/") for path in tracked):
            conflicts.append(relative)
    if conflicts:
        joined = ", ".join(conflicts)
        raise RuntimeError(
            f"limpeza recusada: alvo contém arquivo versionado: {joined}"
        )


def remove(target: Path) -> None:
    if target.is_symlink() or target.is_file():
        target.unlink()
    elif target.is_dir():
        shutil.rmtree(target)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply",
        action="store_true",
        help="executa a limpeza; sem esta opção apenas lista os alvos",
    )
    args = parser.parse_args()

    targets = collect_targets()
    ensure_untracked(targets)
    action = "Removendo" if args.apply else "Removeria"
    for target in targets:
        print(f"{action}: {target.relative_to(ROOT)}")
        if args.apply:
            remove(target)
    if not targets:
        print("Nenhum artefato regenerável encontrado.")


if __name__ == "__main__":
    main()
