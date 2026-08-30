"""Pipeline atômico completo: CSV → RAW → CORE."""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import uuid
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from elt.core_loader import (
    _load_core_transaction,
    _sql_sha256,
    load_core_settings,
)
from elt.raw_loader import (
    RawLoadError,
    _load_transaction,
    load_settings,
    validate_sources,
)

LOGGER = logging.getLogger("pipeline")


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _write_log(log_dir: Path, payload: dict[str, object]) -> Path:
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / f"full_load_{payload['run_id']}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_pipeline(
    raw_config: Path,
    core_config: Path,
    database_url: str | None,
    validate_only: bool = False,
) -> dict[str, object]:
    """Executa as duas camadas em uma única transação PostgreSQL."""
    raw_settings = load_settings(raw_config)
    core_settings = load_core_settings(core_config)
    run_id = str(uuid.uuid4())
    payload: dict[str, object] = {
        "run_id": run_id,
        "started_at": _utc_now(),
        "finished_at": None,
        "mode": "validate-only" if validate_only else "full-load",
        "status": "running",
        "sources": [],
        "raw_reconciliation": [],
        "core_raw_counts": {},
        "core_reconciliation": [],
        "transformation_sql": str(core_settings.sql_path),
        "transformation_sha256": _sql_sha256(core_settings.sql_path),
    }
    try:
        profiles = validate_sources(raw_settings)
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
                payload["raw_reconciliation"] = _load_transaction(
                    connection, raw_settings, profiles
                )
                raw_counts, core_reconciliation = _load_core_transaction(
                    connection, core_settings
                )
                payload["core_raw_counts"] = raw_counts
                payload["core_reconciliation"] = core_reconciliation
            payload["status"] = "approved"
    except Exception as exc:
        payload["status"] = "failed"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
        raise
    finally:
        payload["finished_at"] = _utc_now()
        log_path = _write_log(raw_settings.log_dir, payload)
        LOGGER.info("Log da execução completa: %s", log_path)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--raw-config",
        type=Path,
        default=Path("config/raw_load.toml"),
        help="Configuração da ingestão RAW",
    )
    parser.add_argument(
        "--core-config",
        type=Path,
        default=Path("config/core_load.toml"),
        help="Configuração da transformação CORE",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Pré-valida os CSVs sem conectar ou alterar o PostgreSQL",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
    )
    load_dotenv()
    args = build_parser().parse_args(argv)
    try:
        result = run_pipeline(
            args.raw_config,
            args.core_config,
            os.getenv("DATABASE_URL"),
            args.validate_only,
        )
    except Exception as exc:
        LOGGER.error("Pipeline completo reprovado: %s", exc)
        return 1
    LOGGER.info("Pipeline completo %s", str(result["status"]).upper())
    return 0


if __name__ == "__main__":
    sys.exit(main())
