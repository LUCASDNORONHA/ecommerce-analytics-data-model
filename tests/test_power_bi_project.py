import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BI = ROOT / "bi" / "power-bi"
REPORT = BI / "EcommerceAnalytics.Report"
MODEL = BI / "EcommerceAnalytics.SemanticModel"


class PowerBIProjectTests(unittest.TestCase):
    def test_pbip_and_bindings_exist(self):
        self.assertTrue((BI / "EcommerceAnalytics.pbip").exists())
        binding = json.loads((REPORT / "definition.pbir").read_text(encoding="utf-8"))
        self.assertEqual(binding["version"], "4.0")
        self.assertEqual(
            binding["datasetReference"]["byPath"]["path"],
            "../EcommerceAnalytics.SemanticModel",
        )
        self.assertEqual(
            json.loads((MODEL / "definition.pbism").read_text(encoding="utf-8"))[
                "version"
            ],
            "4.2",
        )

    def test_four_canonical_analytics_views_are_sources(self):
        texts = "\n".join(
            p.read_text(encoding="utf-8")
            for p in (MODEL / "definition" / "tables").glob("*.tmdl")
        )
        for view in [
            "vw_pedido_financeiro",
            "vw_financeiro_mensal",
            "vw_vendedor_pedido",
            "vw_desempenho_vendedor",
        ]:
            self.assertIn(view, texts)

    def test_report_has_five_pages_and_42_visuals(self):
        pages = json.loads(
            (REPORT / "definition" / "pages" / "pages.json").read_text(encoding="utf-8")
        )
        self.assertEqual(len(pages["pageOrder"]), 5)
        visual_files = list(
            (REPORT / "definition" / "pages").glob("*/visuals/*/visual.json")
        )
        self.assertEqual(len(visual_files), 42)

    def test_drillthrough_and_topn_exist(self):
        page_texts = [
            json.loads(p.read_text(encoding="utf-8"))
            for p in (REPORT / "definition" / "pages").glob("*/page.json")
        ]
        self.assertTrue(
            any(
                p.get("pageBinding", {}).get("type") == "Drillthrough"
                for p in page_texts
            )
        )
        visuals = [
            json.loads(p.read_text(encoding="utf-8"))
            for p in (REPORT / "definition" / "pages").glob("*/visuals/*/visual.json")
        ]
        self.assertTrue(
            any(
                any(
                    f.get("type") == "TopN"
                    for f in v.get("filterConfig", {}).get("filters", [])
                )
                for v in visuals
            )
        )

    def test_no_direct_fact_to_fact_relationship(self):
        rel = (MODEL / "definition" / "relationships.tmdl").read_text(encoding="utf-8")
        self.assertNotIn("fato_pedido_financeiro.id_pedido", rel)
        self.assertNotIn("fato_vendedor_pedido.id_pedido", rel)
        self.assertIn("fato_vendedor_pedido.id_vendedor", rel)
        self.assertIn("resumo_desempenho_vendedor.id_vendedor", rel)

    def test_no_binary_or_local_powerbi_artifacts_committed(self):
        forbidden = {".pbix", ".pbit", ".abf"}
        self.assertFalse(
            [p for p in BI.rglob("*") if p.is_file() and p.suffix.lower() in forbidden]
        )
        self.assertFalse(list(BI.rglob("localSettings.json")))
        self.assertFalse(list(BI.rglob(".pbi")))

    def test_visuals_stay_inside_canvas(self):
        for path in (REPORT / "definition" / "pages").glob("*/visuals/*/visual.json"):
            visual = json.loads(path.read_text(encoding="utf-8"))
            position = visual["position"]
            self.assertGreaterEqual(position["x"], 0)
            self.assertGreaterEqual(position["y"], 0)
            self.assertLessEqual(position["x"] + position["width"], 1280)
            self.assertLessEqual(position["y"] + position["height"], 720)


if __name__ == "__main__":
    unittest.main()
