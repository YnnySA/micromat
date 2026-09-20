# Implements: specs/08-interfaz-vintage-unificada.md
"""Pruebas de la interfaz nativa, el tema y la unificación de cálculos."""

from pathlib import Path

from core.calculations import elastic_from_props, strength_from_props
from core.micromechanics import (
    elastic_properties_from_sidebar,
    strength_properties_from_sidebar,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
APP_ROOT = PROJECT_ROOT / "app"


def test_no_html_injection():
    offenders = []
    for path in APP_ROOT.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "unsafe_allow_html" in text or "<style>" in text or "@import" in text:
            offenders.append(path.relative_to(APP_ROOT).as_posix())
    assert offenders == []


def test_charts_labels_unicode():
    from components import charts

    source = (APP_ROOT / "components" / "charts.py").read_text(encoding="utf-8")
    assert "$" not in source
    assert all("$" not in label for label in charts.LABELS)
    assert charts.LINE_WIDTH <= 1.5


def test_theme_config():
    config = PROJECT_ROOT / ".streamlit" / "config.toml"
    assert config.exists()
    text = config.read_text(encoding="utf-8")
    assert 'base = "light"' in text
    assert 'font = "monospace"' in text


def test_layers_agree():
    fiber = {"E1": 230.0, "E2": 15.0, "G12": 9.0, "nu12": 0.20, "F1t": 3500.0, "etu": 0.0152, "density": 1760.0}
    matrix = {"E": 4.2, "nu": 0.35, "G": 1.56, "Ft": 69.0, "density": 1200.0}

    assert elastic_properties_from_sidebar(fiber, matrix, 0.6) == elastic_from_props(fiber, matrix, 0.6)
    assert strength_properties_from_sidebar(fiber, matrix, 0.6) == strength_from_props(fiber, matrix, 0.6)


def test_strength_models_match_course():
    fiber = {"E1": 276.0, "E2": 19.0, "G12": 27.0, "nu12": 0.20, "F1t": 5180.0, "etu": 0.0187, "density": 1780.0}
    matrix = {"E": 4.67, "nu": 0.36, "G": 1.72, "Ft": 121.0, "density": 1300.0}
    strength = strength_from_props(fiber, matrix, 0.6)

    assert round(strength["F1t"], 3) == 3142.932
    assert round(strength["F1c"], 3) == 1807.186
    assert round(strength["F2t"], 3) == 95.991
    assert round(strength["F6"], 3) == 51.935
    assert strength["F2c"] == 4 * strength["F2t"]
    assert strength["F1c_rosen"] == 1.72 * 1000.0 / 0.4
