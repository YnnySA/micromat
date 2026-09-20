# Implements: specs/09-teoria-curso.md
"""Pruebas del contenido teórico del curso (U1 + U2)."""

from core.course_theory import COURSE_THEORY, MODEL_MAP, RELIABILITY, theory_keys


def test_theory_blocks():
    assert len(COURSE_THEORY) >= 8
    assert all(block.title for block in COURSE_THEORY)
    assert len(set(theory_keys())) == len(COURSE_THEORY)
    for block in COURSE_THEORY:
        assert block.paragraphs or block.bullets or block.formulas


def test_theory_has_course_formulas():
    latex = "\n".join(formula for block in COURSE_THEORY for _, formula in block.formulas)
    assert "V_f" in latex
    assert "E_1" in latex
    assert "G_{12}" in latex
    assert "\\eta" in latex
    assert "F_{2t}" in latex


def test_model_map():
    properties = {prop for prop, _, _ in MODEL_MAP}
    assert {"E₁", "E₂", "G₁₂", "ν₁₂", "ν₂₁", "F₁ₜ", "F₁c", "F₂ₜ", "F₆", "F₂c"} <= properties


def test_reliability_rows():
    assert len(RELIABILITY) >= 4
    assert all(len(row[2]) == 5 for row in RELIABILITY)
    assert "★★★★☆" in {row[2] for row in RELIABILITY}
