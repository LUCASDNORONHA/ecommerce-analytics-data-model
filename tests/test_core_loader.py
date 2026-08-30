from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from elt.core_loader import (
    EXPECTED_QUERIES,
    CoreSettings,
    _load_core_transaction,
    load_core_settings,
)


class CoreConfigurationTests(unittest.TestCase):
    def test_loads_versioned_configuration(self) -> None:
        root = Path(__file__).resolve().parents[1]

        settings = load_core_settings(root / "config/core_load.toml")

        self.assertEqual(settings.repository_root, root)
        self.assertEqual(settings.sql_path, root / "elt/sql/load_core.sql")
        self.assertEqual(settings.lock_timeout_seconds, 30)


class TransformationSqlTests(unittest.TestCase):
    def setUp(self) -> None:
        root = Path(__file__).resolve().parents[1]
        self.sql = (root / "elt/sql/load_core.sql").read_text(encoding="utf-8")

    def test_loads_all_nine_core_tables(self) -> None:
        self.assertEqual(self.sql.count("INSERT INTO core."), 9)
        self.assertEqual(len(EXPECTED_QUERIES), 9)

    def test_keeps_transaction_control_in_python(self) -> None:
        upper_sql = self.sql.upper()
        self.assertNotIn("BEGIN;", upper_sql)
        self.assertNotIn("COMMIT;", upper_sql)
        self.assertIn("TRUNCATE TABLE", upper_sql)

    def test_deduplicates_only_exact_geolocation_rows(self) -> None:
        self.assertIn("SELECT DISTINCT ON", self.sql)
        for column in (
            "geolocation_zip_code_prefix",
            "geolocation_lat",
            "geolocation_lng",
            "geolocation_city",
            "geolocation_state",
        ):
            self.assertIn(column, self.sql)

    def test_does_not_use_truncating_text_casts(self) -> None:
        self.assertNotIn("::character", self.sql)
        self.assertIn("::numeric(12, 2)", self.sql)
        self.assertIn("::timestamp without time zone", self.sql)


class FakeCursor:
    def __init__(self) -> None:
        self.executed: list[str] = []

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def execute(self, query: str) -> None:
        self.executed.append(query)

    def fetchone(self) -> tuple[int]:
        return (1,)


class FakeConnection:
    def __init__(self) -> None:
        self.fake_cursor = FakeCursor()

    def cursor(self) -> FakeCursor:
        return self.fake_cursor


class CoreTransactionTests(unittest.TestCase):
    def test_executes_transformation_and_reconciles_nine_tables(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sql_path = root / "load_core.sql"
            sql_path.write_text("SELECT 1;", encoding="utf-8")
            settings = CoreSettings(
                repository_root=root,
                sql_path=sql_path,
                log_dir=root / "logs",
                lock_timeout_seconds=5,
                statement_timeout_seconds=0,
            )
            connection = FakeConnection()

            raw_counts, reconciliation = _load_core_transaction(
                connection, settings
            )

        self.assertEqual(len(raw_counts), 9)
        self.assertEqual(len(reconciliation), 9)
        self.assertTrue(all(item["approved"] for item in reconciliation))
        self.assertIn("SELECT 1;", connection.fake_cursor.executed)


if __name__ == "__main__":
    unittest.main()
