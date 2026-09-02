from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from elt.raw_loader import (
    LoadSettings,
    RawLoadError,
    SourceContract,
    SourceProfile,
    _copy_sql,
    _load_transaction,
    load_settings,
    validate_source,
)


class SourceValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = SourceContract(
            filename="source.csv",
            table="source_table",
            columns=("id", "value"),
        )

    def test_validates_utf8_bom_and_counts_rows(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / self.contract.filename
            path.write_bytes(b"\xef\xbb\xbfid,value\r\n1,a\r\n2,b\r\n")

            profile = validate_source(path, self.contract)

            self.assertEqual(profile.rows, 2)
            self.assertEqual(profile.columns, 2)
            self.assertTrue(profile.has_utf8_bom)
            self.assertEqual(profile.encoding, "utf-8-sig")
            self.assertEqual(len(profile.sha256), 64)

    def test_rejects_unexpected_header(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / self.contract.filename
            path.write_text("other,value\n1,a\n", encoding="utf-8")

            with self.assertRaisesRegex(RawLoadError, "Cabeçalho inválido"):
                validate_source(path, self.contract)

    def test_rejects_wrong_column_count(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / self.contract.filename
            path.write_text("id,value\n1,a,extra\n", encoding="utf-8")

            with self.assertRaisesRegex(RawLoadError, "possui 3 campos"):
                validate_source(path, self.contract)

    def test_rejects_invalid_utf8(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / self.contract.filename
            path.write_bytes(b"id,value\n1,\xff\n")

            with self.assertRaisesRegex(RawLoadError, "Codificação inválida"):
                validate_source(path, self.contract)


class ConfigurationTests(unittest.TestCase):
    def test_loads_relative_paths_from_repository_root(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".toml",
            dir=root,
            encoding="utf-8",
            delete=False,
        ) as stream:
            stream.write(
                """
[raw_load]
data_dir = "data/raw"
log_dir = "outputs/test-logs"
expected_sources = 1

[[sources]]
filename = "source.csv"
table = "source_table"
columns = ["id", "value"]
"""
            )
            path = Path(stream.name)
        try:
            settings = load_settings(path)
        finally:
            path.unlink()

        self.assertEqual(settings.repository_root, root)
        self.assertEqual(settings.data_dir, root / "data/raw")
        self.assertEqual(settings.log_dir, root / "outputs/test-logs")
        self.assertEqual(len(settings.sources), 1)

    def test_loads_configuration_outside_repository(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "raw_load.toml"
            path.write_text(
                """
[raw_load]
data_dir = "data/raw"
log_dir = "outputs/test-logs"
expected_sources = 1

[[sources]]
filename = "source.csv"
table = "source_table"
columns = ["id", "value"]
""",
                encoding="utf-8",
            )

            settings = load_settings(path)

        self.assertEqual(settings.repository_root, root)
        self.assertEqual(settings.data_dir, root / "data/raw")
        self.assertEqual(len(settings.sources), 1)

    def test_rejects_unsafe_sql_identifier(self) -> None:
        root = Path(__file__).resolve().parents[1]
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".toml",
            dir=root,
            encoding="utf-8",
            delete=False,
        ) as stream:
            stream.write(
                """
[raw_load]
expected_sources = 1

[[sources]]
filename = "source.csv"
table = "source;drop_table"
columns = ["id"]
"""
            )
            path = Path(stream.name)
        try:
            with self.assertRaisesRegex(RawLoadError, "Identificador SQL inválido"):
                load_settings(path)
        finally:
            path.unlink()


class FakeCopy:
    def __init__(self) -> None:
        self.data = bytearray()

    def __enter__(self) -> FakeCopy:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def write(self, block: bytes) -> None:
        self.data.extend(block)


class FakeCursor:
    def __init__(self, expected_rows: int) -> None:
        self.expected_rows = expected_rows
        self.executed: list[tuple[str, object]] = []
        self.copies: list[tuple[str, FakeCopy]] = []

    def __enter__(self) -> FakeCursor:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def execute(self, query: str, params: object = None) -> None:
        self.executed.append((query, params))

    def copy(self, query: str) -> FakeCopy:
        copy = FakeCopy()
        self.copies.append((query, copy))
        return copy

    def fetchone(self) -> tuple[int, int, int, int]:
        return (
            self.expected_rows,
            self.expected_rows,
            0,
            self.expected_rows,
        )


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.fake_cursor = cursor

    def cursor(self) -> FakeCursor:
        return self.fake_cursor


class TransactionTests(unittest.TestCase):
    def test_copy_uses_header_utf8_and_force_null(self) -> None:
        contract = SourceContract("source.csv", "source_table", ("id", "value"))
        sql = _copy_sql(contract)

        self.assertIn("COPY raw.source_table (id, value)", sql)
        self.assertIn("HEADER TRUE", sql)
        self.assertIn("ENCODING 'UTF8'", sql)
        self.assertIn("FORCE_NULL (id, value)", sql)

    def test_transaction_truncates_copies_and_reconciles(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            data_dir = root / "data"
            data_dir.mkdir()
            source_path = data_dir / "source.csv"
            source_path.write_bytes(b"id,value\n1,a\n2,\n")
            contract = SourceContract("source.csv", "source_table", ("id", "value"))
            settings = LoadSettings(
                repository_root=root,
                data_dir=data_dir,
                log_dir=root / "logs",
                lock_timeout_seconds=5,
                statement_timeout_seconds=0,
                sources=(contract,),
            )
            profile = SourceProfile(
                filename="source.csv",
                table="source_table",
                rows=2,
                columns=2,
                size_bytes=source_path.stat().st_size,
                sha256="0" * 64,
                encoding="utf-8",
                has_utf8_bom=False,
            )
            cursor = FakeCursor(expected_rows=2)

            result = _load_transaction(FakeConnection(cursor), settings, (profile,))

        self.assertTrue(result[0]["approved"])
        self.assertIn(
            "TRUNCATE TABLE raw.source_table RESTART IDENTITY", cursor.executed[1][0]
        )
        self.assertEqual(bytes(cursor.copies[0][1].data), b"id,value\n1,a\n2,\n")


if __name__ == "__main__":
    unittest.main()
