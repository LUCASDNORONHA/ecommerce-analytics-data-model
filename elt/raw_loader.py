"""Ingestão transacional dos CSVs Olist no schema RAW."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import os
import re
import sys
import tomllib
import uuid
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable

import psycopg


LOGGER = logging.getLogger("raw_loader")
IDENTIFIER = re.compile(r"^[a-z_][a-z0-9_]*$")
BUFFER_SIZE = 1024 * 1024


class RawLoadError(RuntimeError):
    """Falha controlada de configuração, validação ou reconciliação."""


@dataclass(frozen=True)
class SourceContract:
    filename: str
    table: str
    columns: tuple[str, ...]


@dataclass(frozen=True)
class LoadSettings:
    repository_root: Path
    data_dir: Path
    log_dir: Path
    lock_timeout_seconds: int
    statement_timeout_seconds: int
    sources: tuple[SourceContract, ...]


@dataclass(frozen=True)
class SourceProfile:
    filename: str
    table: str
    rows: int
    columns: int
    size_bytes: int
    sha256: str
    encoding: str
    has_utf8_bom: bool


def find_repository_root(start: Path) -> Path:
    """Localiza a raiz sem depender do diretório de execução."""
    for candidate in (start, *start.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "models").is_dir():
            return candidate
    raise RawLoadError(f"Raiz do repositório não encontrada a partir de {start.resolve()}")


def _resolve_from_root(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def _validate_identifier(value: str, context: str) -> None:
    if not IDENTIFIER.fullmatch(value):
        raise RawLoadError(f"Identificador SQL inválido em {context}: {value!r}")


def load_settings(config_path: Path) -> LoadSettings:
    """Lê e valida a configuração TOML versionada."""
    root = find_repository_root(Path.cwd())
    resolved_config = config_path if config_path.is_absolute() else Path.cwd() / config_path
    if not resolved_config.is_file() and not config_path.is_absolute():
        resolved_config = root / config_path
    try:
        with resolved_config.open("rb") as stream:
            config = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RawLoadError(f"Não foi possível ler {resolved_config}: {exc}") from exc

    raw = config.get("raw_load", {})
    source_rows = config.get("sources", [])
    if not isinstance(source_rows, list) or not source_rows:
        raise RawLoadError("A configuração deve declarar ao menos uma fonte em [[sources]]")

    sources: list[SourceContract] = []
    filenames: set[str] = set()
    tables: set[str] = set()
    for index, item in enumerate(source_rows, start=1):
        try:
            filename = str(item["filename"])
            table = str(item["table"])
            columns = tuple(str(column) for column in item["columns"])
        except (KeyError, TypeError) as exc:
            raise RawLoadError(f"Fonte {index} incompleta na configuração") from exc
        if Path(filename).name != filename:
            raise RawLoadError(f"Nome de arquivo inválido: {filename!r}")
        _validate_identifier(table, f"sources[{index}].table")
        if not columns:
            raise RawLoadError(f"Fonte {filename} não declara colunas")
        for column in columns:
            _validate_identifier(column, f"{filename}.columns")
        if filename in filenames or table in tables:
            raise RawLoadError(f"Fonte ou tabela duplicada na configuração: {filename}/{table}")
        filenames.add(filename)
        tables.add(table)
        sources.append(SourceContract(filename, table, columns))

    expected_sources = int(raw.get("expected_sources", len(sources)))
    if len(sources) != expected_sources:
        raise RawLoadError(
            "Quantidade de fontes divergente: "
            f"esperadas {expected_sources}, declaradas {len(sources)}"
        )

    return LoadSettings(
        repository_root=root,
        data_dir=_resolve_from_root(root, str(raw.get("data_dir", "data/raw"))),
        log_dir=_resolve_from_root(root, str(raw.get("log_dir", "outputs/data-loading/logs"))),
        lock_timeout_seconds=int(raw.get("lock_timeout_seconds", 30)),
        statement_timeout_seconds=int(raw.get("statement_timeout_seconds", 0)),
        sources=tuple(sources),
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(BUFFER_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_source(path: Path, contract: SourceContract) -> SourceProfile:
    """Valida presença, UTF-8, cabeçalho e largura de todas as linhas."""
    if not path.is_file():
        raise RawLoadError(f"Arquivo obrigatório ausente: {path}")

    has_bom = path.read_bytes()[:3] == b"\xef\xbb\xbf"
    rows = 0
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            header = next(reader, None)
            if header != list(contract.columns):
                raise RawLoadError(
                    f"Cabeçalho inválido em {contract.filename}: "
                    f"esperado {list(contract.columns)!r}, recebido {header!r}"
                )
            for line_number, row in enumerate(reader, start=2):
                if len(row) != len(contract.columns):
                    raise RawLoadError(
                        f"Linha {line_number} de {contract.filename} possui {len(row)} campos; "
                        f"esperados {len(contract.columns)}"
                    )
                rows += 1
    except UnicodeDecodeError as exc:
        raise RawLoadError(f"Codificação inválida em {contract.filename}: {exc}") from exc
    except csv.Error as exc:
        raise RawLoadError(f"CSV malformado em {contract.filename}: {exc}") from exc

    return SourceProfile(
        filename=contract.filename,
        table=contract.table,
        rows=rows,
        columns=len(contract.columns),
        size_bytes=path.stat().st_size,
        sha256=_sha256(path),
        encoding="utf-8-sig" if has_bom else "utf-8",
        has_utf8_bom=has_bom,
    )


def validate_sources(settings: LoadSettings) -> tuple[SourceProfile, ...]:
    """Pré-valida todas as fontes antes de qualquer conexão ou truncamento."""
    profiles: list[SourceProfile] = []
    errors: list[str] = []
    for contract in settings.sources:
        try:
            profiles.append(validate_source(settings.data_dir / contract.filename, contract))
        except RawLoadError as exc:
            errors.append(str(exc))
    if errors:
        details = "\n- ".join(errors)
        raise RawLoadError(f"Pré-validação reprovada:\n- {details}")
    return tuple(profiles)


def _copy_sql(contract: SourceContract) -> str:
    columns = ", ".join(contract.columns)
    return (
        f"COPY raw.{contract.table} ({columns}) FROM STDIN WITH ("
        f"FORMAT CSV, HEADER TRUE, ENCODING 'UTF8', FORCE_NULL ({columns}))"
    )


def _truncate_sql(sources: Iterable[SourceContract]) -> str:
    tables = ", ".join(f"raw.{source.table}" for source in sources)
    return f"TRUNCATE TABLE {tables} RESTART IDENTITY"


def _load_transaction(
    connection: psycopg.Connection[Any],
    settings: LoadSettings,
    profiles: tuple[SourceProfile, ...],
) -> list[dict[str, object]]:
    """Substitui a RAW e reconcilia dentro de uma única transação."""
    profile_by_file = {profile.filename: profile for profile in profiles}
    reconciliation: list[dict[str, object]] = []
    with connection.cursor() as cursor:
        cursor.execute(f"SET LOCAL lock_timeout = '{settings.lock_timeout_seconds}s'")
        if settings.statement_timeout_seconds > 0:
            cursor.execute(
                f"SET LOCAL statement_timeout = '{settings.statement_timeout_seconds}s'"
            )
        cursor.execute(_truncate_sql(settings.sources))

        for contract in settings.sources:
            path = settings.data_dir / contract.filename
            LOGGER.info("Carregando %s em raw.%s", contract.filename, contract.table)
            with path.open("rb") as stream, cursor.copy(_copy_sql(contract)) as copy:
                for block in iter(lambda: stream.read(BUFFER_SIZE), b""):
                    copy.write(block)

            cursor.execute(
                f"""
                SELECT
                    count(*)::bigint,
                    count(*) FILTER (WHERE _arquivo_origem = %s)::bigint,
                    count(*) FILTER (
                        WHERE _id_raw IS NULL
                           OR _arquivo_origem IS NULL
                           OR _carregado_em IS NULL
                    )::bigint,
                    count(DISTINCT _id_raw)::bigint
                FROM raw.{contract.table}
                """,
                (contract.filename,),
            )
            loaded, correct_source, null_metadata, distinct_ids = cursor.fetchone()
            expected = profile_by_file[contract.filename].rows
            approved = (
                loaded == expected
                and correct_source == expected
                and null_metadata == 0
                and distinct_ids == expected
            )
            item = {
                "filename": contract.filename,
                "table": f"raw.{contract.table}",
                "expected_rows": expected,
                "loaded_rows": loaded,
                "correct_source_rows": correct_source,
                "null_metadata_rows": null_metadata,
                "distinct_raw_ids": distinct_ids,
                "approved": approved,
            }
            reconciliation.append(item)
            if not approved:
                raise RawLoadError(f"Reconciliação reprovada em raw.{contract.table}: {item}")
    return reconciliation


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _write_log(settings: LoadSettings, payload: dict[str, object]) -> Path:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    run_id = str(payload["run_id"])
    path = settings.log_dir / f"raw_load_{run_id}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_load(
    settings: LoadSettings, database_url: str | None, validate_only: bool
) -> dict[str, object]:
    """Executa pré-validação e, opcionalmente, a substituição transacional."""
    run_id = str(uuid.uuid4())
    started_at = _utc_now()
    payload: dict[str, object] = {
        "run_id": run_id,
        "started_at": started_at,
        "finished_at": None,
        "mode": "validate-only" if validate_only else "load",
        "status": "running",
        "sources": [],
        "reconciliation": [],
    }
    try:
        profiles = validate_sources(settings)
        payload["sources"] = [asdict(profile) for profile in profiles]
        LOGGER.info(
            "Pré-validação aprovada: %d arquivos, %d registros",
            len(profiles),
            sum(profile.rows for profile in profiles),
        )
        if validate_only:
            payload["status"] = "approved"
        else:
            if not database_url:
                raise RawLoadError("DATABASE_URL não configurada")
            with psycopg.connect(database_url) as connection:
                payload["reconciliation"] = _load_transaction(
                    connection, settings, profiles
                )
            payload["status"] = "approved"
    except Exception as exc:
        payload["status"] = "failed"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
        raise
    finally:
        payload["finished_at"] = _utc_now()
        log_path = _write_log(settings, payload)
        payload["log_path"] = str(log_path)
        LOGGER.info("Log da execução: %s", log_path)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/raw_load.toml"),
        help="Arquivo TOML de configuração (padrão: config/raw_load.toml)",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Executa somente a pré-validação, sem conectar ao PostgreSQL",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    try:
        settings = load_settings(args.config)
        result = run_load(settings, os.getenv("DATABASE_URL"), args.validate_only)
    except Exception as exc:
        LOGGER.error("Carga RAW reprovada: %s", exc)
        return 1
    LOGGER.info("Carga RAW %s", str(result["status"]).upper())
    return 0


if __name__ == "__main__":
    sys.exit(main())
