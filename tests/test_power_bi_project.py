import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BI = ROOT / "bi" / "power-bi"
REPORT = BI / "EcommerceAnalytics.Report"
MODEL = BI / "EcommerceAnalytics.SemanticModel"


def test_pbip_and_bindings_exist():
    assert (BI / "EcommerceAnalytics.pbip").exists()
    binding = json.loads((REPORT / "definition.pbir").read_text(encoding="utf-8"))
    assert binding["version"] == "4.0"
    assert (
        binding["datasetReference"]["byPath"]["path"]
        == "../EcommerceAnalytics.SemanticModel"
    )
    assert (
        json.loads((MODEL / "definition.pbism").read_text(encoding="utf-8"))["version"]
        == "4.2"
    )


def test_four_canonical_analytics_views_are_sources():
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
        assert view in texts


def test_report_has_five_pages_and_42_visuals():
    pages = json.loads(
        (REPORT / "definition" / "pages" / "pages.json").read_text(encoding="utf-8")
    )
    assert len(pages["pageOrder"]) == 5
    visual_files = list(
        (REPORT / "definition" / "pages").glob("*/visuals/*/visual.json")
    )
    assert len(visual_files) == 42


def test_drillthrough_and_topn_exist():
    page_texts = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in (REPORT / "definition" / "pages").glob("*/page.json")
    ]
    assert any(
        p.get("pageBinding", {}).get("type") == "Drillthrough" for p in page_texts
    )
    visuals = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in (REPORT / "definition" / "pages").glob("*/visuals/*/visual.json")
    ]
    assert any(
        any(
            f.get("type") == "TopN"
            for f in v.get("filterConfig", {}).get("filters", [])
        )
        for v in visuals
    )


def test_no_direct_fact_to_fact_relationship():
    rel = (MODEL / "definition" / "relationships.tmdl").read_text(encoding="utf-8")
    assert "fato_pedido_financeiro.id_pedido" not in rel
    assert "fato_vendedor_pedido.id_pedido" not in rel
    assert "fato_vendedor_pedido.id_vendedor" in rel
    assert "resumo_desempenho_vendedor.id_vendedor" in rel


def test_no_binary_or_local_powerbi_artifacts_committed():
    forbidden = {".pbix", ".pbit", ".abf"}
    assert not [
        p for p in BI.rglob("*") if p.is_file() and p.suffix.lower() in forbidden
    ]
    assert not list(BI.rglob("localSettings.json"))
    assert not list(BI.rglob(".pbi"))


def test_visuals_stay_inside_canvas():
    for path in (REPORT / "definition" / "pages").glob("*/visuals/*/visual.json"):
        v = json.loads(path.read_text(encoding="utf-8"))
        p = v["position"]
        assert p["x"] >= 0 and p["y"] >= 0
        assert p["x"] + p["width"] <= 1280
        assert p["y"] + p["height"] <= 720
