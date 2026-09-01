"""Preparação automatizada da estrutura física do PostgreSQL."""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse

import psycopg
from dotenv import load_dotenv
from psycopg import sql

LOGGER = logging.getLogger("database.setup")

ROOT = Path(__file__).resolve().parents[1]
PHYSICAL_MODEL = ROOT / "models" / "physical"
ANALYTICS_MODEL = ROOT / "models" / "analytics"
ANALYTICS_VIEWS_DIR = ANALYTICS_MODEL / "views"

CREATE_SCHEMA = PHYSICAL_MODEL / "create_schema.sql"
CREATE_INDEXES = PHYSICAL_MODEL / "create_indexes.sql"
VALIDATE_SCHEMA = PHYSICAL_MODEL / "validate_schema.sql"
DROP_SCHEMA = PHYSICAL_MODEL / "drop_schema.sql"
VALIDATE_ANALYTICS = ANALYTICS_MODEL / "validate_views.sql"


def analytics_view_scripts() -> list[Path]:
    """Retorna as views analíticas na ordem explícita de dependência."""

    return sorted(ANALYTICS_VIEWS_DIR.glob("[0-9][0-9]_*.sql"))


def execute_sql(connection: psycopg.Connection, path: Path) -> None:
    """Executa um script SQL versionado."""

    if not path.is_file():
        raise FileNotFoundError(f"Script SQL não encontrado: {path}")

    LOGGER.info("Executando %s", path.relative_to(ROOT))

    script = path.read_text(encoding="utf-8")

    with connection.cursor() as cursor:
        cursor.execute(script)


def get_database_name(database_url: str) -> str:
    """Obtém o nome do banco definido na DATABASE_URL."""

    parsed = urlparse(database_url)
    database_name = parsed.path.lstrip("/")

    if not database_name:
        raise ValueError("DATABASE_URL não informa o banco de destino")

    return database_name


def build_admin_url(database_url: str) -> str:
    """Cria uma URL equivalente apontando para o banco administrativo postgres."""

    parsed = urlparse(database_url)

    return urlunparse(parsed._replace(path="/postgres"))


def database_exists(database_url: str) -> bool:
    """Verifica no catálogo do PostgreSQL se o banco de destino existe."""

    database_name = get_database_name(database_url)
    admin_url = build_admin_url(database_url)

    with psycopg.connect(admin_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM pg_database
                    WHERE datname = %s
                )
                """,
                (database_name,),
            )

            return bool(cursor.fetchone()[0])


def create_database(database_url: str) -> None:
    """Cria o banco definido na DATABASE_URL."""

    database_name = get_database_name(database_url)
    admin_url = build_admin_url(database_url)

    LOGGER.info("Banco %s não existe", database_name)
    LOGGER.info("Criando banco %s", database_name)

    with psycopg.connect(admin_url, autocommit=True) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name))
            )


def ensure_database(database_url: str) -> bool:
    """Garante que o banco de destino exista.

    Retorna True quando o banco foi criado nesta execução.
    """

    if database_exists(database_url):
        return False

    create_database(database_url)
    return True


def setup_database(database_url: str, reset: bool = False) -> None:
    """Cria e valida a estrutura física do banco."""

    database_name = get_database_name(database_url)

    LOGGER.info("Banco de destino: %s", database_name)

    database_created = ensure_database(database_url)

    with psycopg.connect(database_url, autocommit=True) as connection:
        if reset and not database_created:
            LOGGER.info("Removendo estrutura existente")
            execute_sql(connection, DROP_SCHEMA)

        LOGGER.info("Criando estrutura física")
        execute_sql(connection, CREATE_SCHEMA)

        LOGGER.info("Criando índices")
        execute_sql(connection, CREATE_INDEXES)

        LOGGER.info("Validando estrutura")
        execute_sql(connection, VALIDATE_SCHEMA)

        LOGGER.info("Criando views analíticas")
        for view_script in analytics_view_scripts():
            execute_sql(connection, view_script)

        LOGGER.info("Validando views analíticas")
        execute_sql(connection, VALIDATE_ANALYTICS)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Prepara a estrutura física do banco PostgreSQL."
    )

    parser.add_argument(
        "--reset",
        action="store_true",
        help="Remove a estrutura existente antes de recriá-la.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    load_dotenv()

    args = build_parser().parse_args(argv)
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        LOGGER.error("DATABASE_URL não configurada")
        return 1

    try:
        setup_database(database_url, reset=args.reset)
    except Exception as exc:
        LOGGER.error("Preparação do banco reprovada: %s", exc)
        return 1

    LOGGER.info("Estrutura do banco preparada e validada com sucesso")
    return 0


if __name__ == "__main__":
    sys.exit(main())
