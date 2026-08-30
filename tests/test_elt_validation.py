from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from validation.elt_validation import (
    INTEGRITY_RULES,
    QUALITY_RULES,
    RECONCILIATION_RULES,
    TRANSFORMATION_RULES,
    build_summary,
    run_integrity,
    run_not_null_quality,
    run_quality,
    run_reconciliation,
    run_transformation_quality,
    run_validation,
)


class FakeCursor:
    def __init__(self, values: list[int]) -> None:
        self.values = iter(values)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return None

    def execute(self, query: str) -> None:
        pass

    def fetchone(self) -> tuple[int]:
        return (next(self.values),)


class FakeConnection:
    def __init__(self, values: list[int]) -> None:
        self.cursor_instance = FakeCursor(values)

    def cursor(self) -> FakeCursor:
        return self.cursor_instance


class ReconciliationTests(unittest.TestCase):
    def test_declara_nove_regras_de_reconciliacao(self) -> None:
        self.assertEqual(len(RECONCILIATION_RULES), 9)

    def test_aprova_quando_origem_e_destino_possuem_mesmo_volume(
        self,
    ) -> None:
        values: list[int] = []

        for _ in RECONCILIATION_RULES:
            values.extend([100, 100])

        connection = FakeConnection(values)

        results = run_reconciliation(connection)

        self.assertEqual(len(results), 9)
        self.assertTrue(all(result["approved"] for result in results))
        self.assertTrue(all(result["difference"] == 0 for result in results))

    def test_reprova_quando_existe_divergencia(self) -> None:
        values: list[int] = []

        for index, _ in enumerate(RECONCILIATION_RULES):
            if index == 0:
                values.extend([100, 99])
            else:
                values.extend([100, 100])

        connection = FakeConnection(values)

        results = run_reconciliation(connection)

        self.assertFalse(results[0]["approved"])
        self.assertEqual(results[0]["difference"], -1)

    def test_summary_contabiliza_aprovacoes_e_falhas(self) -> None:
        results = [
            {"approved": True},
            {"approved": True},
            {"approved": False},
        ]

        summary = build_summary(results)

        self.assertEqual(summary["total_rules"], 3)
        self.assertEqual(summary["approved"], 2)
        self.assertEqual(summary["failed"], 1)


class IntegrityTests(unittest.TestCase):
    def test_declara_dezenove_regras_de_integridade(self) -> None:
        self.assertEqual(len(INTEGRITY_RULES), 19)

    def test_aprova_quando_nao_existirem_violacoes(self) -> None:
        connection = FakeConnection([0] * len(INTEGRITY_RULES))

        results = run_integrity(connection)

        self.assertEqual(len(results), 19)
        self.assertTrue(all(result["approved"] for result in results))
        self.assertTrue(all(result["actual"] == 0 for result in results))

    def test_reprova_regra_com_violacoes(self) -> None:
        values = [0] * len(INTEGRITY_RULES)
        values[0] = 2

        connection = FakeConnection(values)

        results = run_integrity(connection)

        self.assertFalse(results[0]["approved"])
        self.assertEqual(results[0]["actual"], 2)
        self.assertEqual(results[0]["expected"], 0)
        self.assertEqual(results[0]["difference"], 2)


class QualityTests(unittest.TestCase):
    def test_declara_onze_regras_de_qualidade(self) -> None:
        self.assertEqual(len(QUALITY_RULES), 11)

    def test_aprova_quando_nao_existirem_violacoes_de_qualidade(
        self,
    ) -> None:
        connection = FakeConnection([0] * len(QUALITY_RULES))

        results = run_quality(connection)

        self.assertEqual(len(results), 11)
        self.assertTrue(all(result["approved"] for result in results))

    def test_reprova_regra_de_qualidade_com_violacao(
        self,
    ) -> None:
        values = [0] * len(QUALITY_RULES)
        values[3] = 4

        connection = FakeConnection(values)

        results = run_quality(connection)

        self.assertFalse(results[3]["approved"])
        self.assertEqual(results[3]["actual"], 4)
        self.assertEqual(results[3]["expected"], 0)

    def test_not_null_aprova_colunas_sem_nulos(self) -> None:
        cursor = MagicMock()

        cursor.fetchall.return_value = [
            ("cliente", "id_cliente"),
            ("pedido", "id_pedido"),
        ]

        cursor.fetchone.side_effect = [
            (0,),
            (0,),
        ]

        cursor_context = MagicMock()
        cursor_context.__enter__.return_value = cursor
        cursor_context.__exit__.return_value = False

        connection = MagicMock()
        connection.cursor.return_value = cursor_context

        results = run_not_null_quality(connection)

        self.assertEqual(len(results), 2)
        self.assertTrue(all(result["approved"] for result in results))

    def test_not_null_reprova_coluna_com_nulos(self) -> None:
        cursor = MagicMock()

        cursor.fetchall.return_value = [
            ("cliente", "id_cliente"),
        ]

        cursor.fetchone.return_value = (3,)

        cursor_context = MagicMock()
        cursor_context.__enter__.return_value = cursor
        cursor_context.__exit__.return_value = False

        connection = MagicMock()
        connection.cursor.return_value = cursor_context

        results = run_not_null_quality(connection)

        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]["approved"])
        self.assertEqual(results[0]["actual"], 3)
        self.assertEqual(results[0]["expected"], 0)
        self.assertEqual(results[0]["difference"], 3)


class ValidationReportTests(unittest.TestCase):
    def test_execucao_aprovada_grava_relatorio_json(self) -> None:
        connection = MagicMock()

        connection_context = MagicMock()
        connection_context.__enter__.return_value = connection
        connection_context.__exit__.return_value = False

        results = [
            {
                "rule": "reconciliation.cliente",
                "category": "reconciliation",
                "expected": 10,
                "actual": 10,
                "difference": 0,
                "approved": True,
            }
        ]

        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)

            with (
                patch(
                    "validation.elt_validation.psycopg.connect",
                    return_value=connection_context,
                ),
                patch(
                    "validation.elt_validation.run_reconciliation",
                    return_value=results,
                ),
                patch(
                    "validation.elt_validation.run_integrity",
                    return_value=[],
                ),
                patch(
                    "validation.elt_validation.run_not_null_quality",
                    return_value=[],
                ),
                patch(
                    "validation.elt_validation.run_quality",
                    return_value=[],
                ),
                patch(
                    "validation.elt_validation.run_transformation_quality",
                    return_value=[],
                ),
            ):
                result = run_validation(
                    ("postgresql://usuario:senha@localhost/ecommerce_analytics"),
                    output_dir=output_dir,
                )

            reports = list(output_dir.glob("elt_validation_*.json"))

            self.assertEqual(len(reports), 1)
            self.assertEqual(result["status"], "approved")
            self.assertEqual(
                result["database"],
                "ecommerce_analytics",
            )

            payload = json.loads(reports[0].read_text(encoding="utf-8"))

            self.assertEqual(
                payload["summary"]["total_rules"],
                1,
            )
            self.assertEqual(
                payload["summary"]["approved"],
                1,
            )
            self.assertEqual(
                payload["summary"]["failed"],
                0,
            )


class TransformationTests(unittest.TestCase):
    def test_declara_nove_regras_de_transformacao(self) -> None:
        self.assertEqual(len(TRANSFORMATION_RULES), 9)

    def test_aprova_transformacoes_sem_divergencias(self) -> None:
        connection = FakeConnection([0] * len(TRANSFORMATION_RULES))

        results = run_transformation_quality(connection)

        self.assertEqual(len(results), 9)
        self.assertTrue(all(result["approved"] for result in results))
        self.assertTrue(all(result["actual"] == 0 for result in results))

    def test_reprova_transformacao_com_divergencia(self) -> None:
        values = [0] * len(TRANSFORMATION_RULES)
        values[4] = 3

        connection = FakeConnection(values)

        results = run_transformation_quality(connection)

        self.assertFalse(results[4]["approved"])
        self.assertEqual(results[4]["actual"], 3)
        self.assertEqual(results[4]["expected"], 0)
        self.assertEqual(results[4]["difference"], 3)


if __name__ == "__main__":
    unittest.main()
