"""Testes unitários do pipeline completo CSV → RAW → CORE."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from elt.pipeline import run_pipeline
from elt.raw_loader import RawLoadError, SourceProfile


class TestPipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.root = Path(self.temp_dir.name)
        self.log_dir = self.root / "logs"
        self.sql_path = self.root / "load_core.sql"
        self.sql_path.write_text("-- teste\n", encoding="utf-8")

        self.raw_settings = SimpleNamespace(log_dir=self.log_dir)
        self.core_settings = SimpleNamespace(sql_path=self.sql_path)

        self.profiles = (
            SourceProfile(
                filename="arquivo.csv",
                table="tabela",
                rows=10,
                columns=2,
                size_bytes=100,
                sha256="abc123",
                encoding="utf-8",
                has_utf8_bom=False,
            ),
        )

    def _base_patches(self):
        return (
            patch("elt.pipeline.load_settings", return_value=self.raw_settings),
            patch("elt.pipeline.load_core_settings", return_value=self.core_settings),
            patch("elt.pipeline._sql_sha256", return_value="sql-hash"),
            patch("elt.pipeline.validate_sources", return_value=self.profiles),
        )

    def test_validate_only_nao_abre_conexao(self) -> None:
        p1, p2, p3, p4 = self._base_patches()

        with p1, p2, p3, p4, patch("elt.pipeline.psycopg.connect") as connect:
            result = run_pipeline(
                Path("config/raw_load.toml"),
                Path("config/core_load.toml"),
                database_url=None,
                validate_only=True,
            )

        self.assertEqual(result["status"], "approved")
        self.assertEqual(result["mode"], "validate-only")
        self.assertEqual(len(result["sources"]), 1)
        connect.assert_not_called()

    def test_sem_database_url_reprova_carga_completa(self) -> None:
        p1, p2, p3, p4 = self._base_patches()

        with p1, p2, p3, p4, patch("elt.pipeline.psycopg.connect") as connect:
            with self.assertRaisesRegex(RawLoadError, "DATABASE_URL não configurada"):
                run_pipeline(
                    Path("config/raw_load.toml"),
                    Path("config/core_load.toml"),
                    database_url=None,
                    validate_only=False,
                )

        connect.assert_not_called()

        logs = list(self.log_dir.glob("full_load_*.json"))
        self.assertEqual(len(logs), 1)

        payload = json.loads(logs[0].read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["error_type"], "RawLoadError")

    def test_raw_e_core_usam_a_mesma_conexao(self) -> None:
        p1, p2, p3, p4 = self._base_patches()

        connection = object()
        connection_context = MagicMock()
        connection_context.__enter__.return_value = connection
        connection_context.__exit__.return_value = False

        raw_reconciliation = [{"table": "raw.tabela", "status": "approved"}]
        core_raw_counts = {"raw.tabela": 10}
        core_reconciliation = [{"table": "core.tabela", "status": "approved"}]

        with (
            p1,
            p2,
            p3,
            p4,
            patch("elt.pipeline.psycopg.connect", return_value=connection_context),
            patch(
                "elt.pipeline._load_transaction",
                return_value=raw_reconciliation,
            ) as raw_load,
            patch(
                "elt.pipeline._load_core_transaction",
                return_value=(core_raw_counts, core_reconciliation),
            ) as core_load,
        ):
            result = run_pipeline(
                Path("config/raw_load.toml"),
                Path("config/core_load.toml"),
                database_url="postgresql://teste",
            )

        raw_load.assert_called_once_with(connection, self.raw_settings, self.profiles)
        core_load.assert_called_once_with(connection, self.core_settings)
        self.assertEqual(result["status"], "approved")

    def test_falha_no_core_propaga_erro_e_registra_pipeline_reprovado(self) -> None:
        p1, p2, p3, p4 = self._base_patches()

        connection = object()
        connection_context = MagicMock()
        connection_context.__enter__.return_value = connection
        connection_context.__exit__.return_value = False

        with (
            p1,
            p2,
            p3,
            p4,
            patch("elt.pipeline.psycopg.connect", return_value=connection_context),
            patch("elt.pipeline._load_transaction", return_value=[]),
            patch(
                "elt.pipeline._load_core_transaction",
                side_effect=RuntimeError("falha simulada no CORE"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "falha simulada no CORE"):
                run_pipeline(
                    Path("config/raw_load.toml"),
                    Path("config/core_load.toml"),
                    database_url="postgresql://teste",
                )

        logs = list(self.log_dir.glob("full_load_*.json"))
        self.assertEqual(len(logs), 1)

        payload = json.loads(logs[0].read_text(encoding="utf-8"))
        self.assertEqual(payload["status"], "failed")
        self.assertEqual(payload["error_type"], "RuntimeError")
        self.assertEqual(payload["error"], "falha simulada no CORE")

    def test_resultado_contem_reconciliacao_raw_e_core(self) -> None:
        p1, p2, p3, p4 = self._base_patches()

        connection = object()
        connection_context = MagicMock()
        connection_context.__enter__.return_value = connection
        connection_context.__exit__.return_value = False

        raw_reconciliation = [
            {"table": "raw.olist_customers", "expected": 99441, "actual": 99441}
        ]
        core_raw_counts = {"raw.olist_customers": 99441}
        core_reconciliation = [
            {"table": "core.cliente", "expected": 99441, "actual": 99441}
        ]

        with (
            p1,
            p2,
            p3,
            p4,
            patch("elt.pipeline.psycopg.connect", return_value=connection_context),
            patch(
                "elt.pipeline._load_transaction",
                return_value=raw_reconciliation,
            ),
            patch(
                "elt.pipeline._load_core_transaction",
                return_value=(core_raw_counts, core_reconciliation),
            ),
        ):
            result = run_pipeline(
                Path("config/raw_load.toml"),
                Path("config/core_load.toml"),
                database_url="postgresql://teste",
            )

        self.assertEqual(result["raw_reconciliation"], raw_reconciliation)
        self.assertEqual(result["core_raw_counts"], core_raw_counts)
        self.assertEqual(result["core_reconciliation"], core_reconciliation)
        self.assertEqual(result["status"], "approved")


if __name__ == "__main__":
    unittest.main()
