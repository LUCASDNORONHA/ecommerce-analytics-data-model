"""Transformação transacional da RAW para o CORE."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import sys
import tomllib
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import psycopg

from etl.raw_loader import RawLoadError, find_repository_root


LOGGER = logging.getLogger("core_loader")


@dataclass(frozen=True)
class CoreSettings:
    repository_root: Path
    sql_path: Path
    log_dir: Path
    lock_timeout_seconds: int
    statement_timeout_seconds: int


EXPECTED_QUERIES = {
    "prefixo_cep": """
        SELECT count(*)::bigint
        FROM (
            SELECT customer_zip_code_prefix AS prefixo
            FROM raw.olist_customers
            WHERE customer_zip_code_prefix IS NOT NULL
            UNION
            SELECT seller_zip_code_prefix
            FROM raw.olist_sellers
            WHERE seller_zip_code_prefix IS NOT NULL
            UNION
            SELECT geolocation_zip_code_prefix
            FROM raw.olist_geolocation
            WHERE geolocation_zip_code_prefix IS NOT NULL
        ) AS prefixos
    """,
    "cliente": "SELECT count(*)::bigint FROM raw.olist_customers",
    "produto": "SELECT count(*)::bigint FROM raw.olist_products",
    "vendedor": "SELECT count(*)::bigint FROM raw.olist_sellers",
    "pedido": "SELECT count(*)::bigint FROM raw.olist_orders",
    "item_pedido": "SELECT count(*)::bigint FROM raw.olist_order_items",
    "pagamento": "SELECT count(*)::bigint FROM raw.olist_order_payments",
    "avaliacao": "SELECT count(*)::bigint FROM raw.olist_order_reviews",
    "geolocalizacao": """
        SELECT count(*)::bigint
        FROM (
            SELECT DISTINCT
                geolocation_zip_code_prefix,
                geolocation_lat,
                geolocation_lng,
                geolocation_city,
                geolocation_state
            FROM raw.olist_geolocation
        ) AS ocorrencias_unicas
    """,
}


def _resolve_from_root(root: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else root / path


def load_core_settings(config_path: Path) -> CoreSettings:
    root = find_repository_root(Path.cwd())
    resolved_config = config_path if config_path.is_absolute() else Path.cwd() / config_path
    if not resolved_config.is_file() and not config_path.is_absolute():
        resolved_config = root / config_path
    try:
        with resolved_config.open("rb") as stream:
            config = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise RawLoadError(f"Não foi possível ler {resolved_config}: {exc}") from exc

    raw = config.get("core_load", {})
    sql_path = _resolve_from_root(root, str(raw.get("sql_path", "etl/sql/load_core.sql")))
    if not sql_path.is_file():
        raise RawLoadError(f"SQL de transformação ausente: {sql_path}")
    return CoreSettings(
        repository_root=root,
        sql_path=sql_path,
        log_dir=_resolve_from_root(
            root, str(raw.get("log_dir", "outputs/data-loading/logs"))
        ),
        lock_timeout_seconds=int(raw.get("lock_timeout_seconds", 30)),
        statement_timeout_seconds=int(raw.get("statement_timeout_seconds", 0)),
    )


def _sql_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_raw_tables(cursor: psycopg.Cursor[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table, query in {
        "olist_customers": "SELECT count(*)::bigint FROM raw.olist_customers",
        "olist_geolocation": "SELECT count(*)::bigint FROM raw.olist_geolocation",
        "olist_order_items": "SELECT count(*)::bigint FROM raw.olist_order_items",
        "olist_order_payments": "SELECT count(*)::bigint FROM raw.olist_order_payments",
        "olist_order_reviews": "SELECT count(*)::bigint FROM raw.olist_order_reviews",
        "olist_orders": "SELECT count(*)::bigint FROM raw.olist_orders",
        "olist_products": "SELECT count(*)::bigint FROM raw.olist_products",
        "olist_sellers": "SELECT count(*)::bigint FROM raw.olist_sellers",
        "product_category_name_translation": (
            "SELECT count(*)::bigint FROM raw.product_category_name_translation"
        ),
    }.items():
        cursor.execute(query)
        count = int(cursor.fetchone()[0])
        if count == 0:
            raise RawLoadError(f"Tabela RAW vazia: raw.{table}")
        counts[table] = count
    return counts


def _load_core_transaction(
    connection: psycopg.Connection[Any], settings: CoreSettings
) -> tuple[dict[str, int], list[dict[str, object]]]:
    """Transforma e reconcilia o CORE dentro da transação corrente."""
    transformation_sql = settings.sql_path.read_text(encoding="utf-8")
    reconciliation: list[dict[str, object]] = []
    with connection.cursor() as cursor:
        cursor.execute(f"SET LOCAL lock_timeout = '{settings.lock_timeout_seconds}s'")
        if settings.statement_timeout_seconds > 0:
            cursor.execute(
                f"SET LOCAL statement_timeout = '{settings.statement_timeout_seconds}s'"
            )
        raw_counts = _validate_raw_tables(cursor)
        LOGGER.info("Transformando RAW para CORE")
        cursor.execute(transformation_sql)

        for table, expected_query in EXPECTED_QUERIES.items():
            cursor.execute(expected_query)
            expected = int(cursor.fetchone()[0])
            cursor.execute(f"SELECT count(*)::bigint FROM core.{table}")
            loaded = int(cursor.fetchone()[0])
            approved = loaded == expected
            item = {
                "table": f"core.{table}",
                "expected_rows": expected,
                "loaded_rows": loaded,
                "approved": approved,
            }
            reconciliation.append(item)
            if not approved:
                raise RawLoadError(f"Reconciliação reprovada em core.{table}: {item}")
    return raw_counts, reconciliation


def _utc_now() -> str:
    return datetime.now(UTC).isoformat()


def _write_log(settings: CoreSettings, payload: dict[str, object]) -> Path:
    settings.log_dir.mkdir(parents=True, exist_ok=True)
    path = settings.log_dir / f"core_load_{payload['run_id']}.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_core_load(
    settings: CoreSettings, database_url: str | None
) -> dict[str, object]:
    run_id = str(uuid.uuid4())
    payload: dict[str, object] = {
        "run_id": run_id,
        "started_at": _utc_now(),
        "finished_at": None,
        "status": "running",
        "transformation_sql": str(settings.sql_path),
        "transformation_sha256": _sql_sha256(settings.sql_path),
        "raw_counts": {},
        "reconciliation": [],
    }
    try:
        if not database_url:
            raise RawLoadError("DATABASE_URL não configurada")
        with psycopg.connect(database_url) as connection:
            raw_counts, reconciliation = _load_core_transaction(connection, settings)
            payload["raw_counts"] = raw_counts
            payload["reconciliation"] = reconciliation
        payload["status"] = "approved"
    except Exception as exc:
        payload["status"] = "failed"
        payload["error_type"] = type(exc).__name__
        payload["error"] = str(exc)
        raise
    finally:
        payload["finished_at"] = _utc_now()
        log_path = _write_log(settings, payload)
        LOGGER.info("Log da execução: %s", log_path)
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/core_load.toml"),
        help="Arquivo TOML de configuração do CORE",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    args = build_parser().parse_args(argv)
    try:
        settings = load_core_settings(args.config)
        result = run_core_load(settings, os.getenv("DATABASE_URL"))
    except Exception as exc:
        LOGGER.error("Carga CORE reprovada: %s", exc)
        return 1
    LOGGER.info("Carga CORE %s", str(result["status"]).upper())
    return 0


if __name__ == "__main__":
    sys.exit(main())
