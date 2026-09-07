"""Pruebas de contrato de SPEC-02: espacio de teoría y análisis."""

import pytest

from app.components.theory_panel import reliability_dataframe
from app.core.theory import (
    THEORY_SECTIONS,
    TheoryUnavailableError,
    get_theory_section,
    interpretation_for_system,
    theory_section_keys,
)


def test_theory_sections_exist():
    assert theory_section_keys() == ("rom", "halpin_tsai", "barbero", "rosen")
    assert all(get_theory_section(key).title.startswith("Teoría:") for key in theory_section_keys())


def test_theory_contains_formulas():
    assert all(section.formulas for section in THEORY_SECTIONS.values())
    assert any("E_1" in formula for formula in THEORY_SECTIONS["rom"].formulas)
    assert any(r"\xi" in formula for formula in THEORY_SECTIONS["halpin_tsai"].formulas)


def test_interpretation_contextual():
    cfrp = "\n".join(interpretation_for_system("IM7/8552 (CFRP)"))
    gfrp = "\n".join(interpretation_for_system("E-glass/Epoxi (GFRP)"))
    assert "CFRP" in cfrp and "IM7" in cfrp
    assert "fibra de vidrio" in gfrp
    assert cfrp != gfrp


def test_reliability_table():
    dataframe = reliability_dataframe()
    assert len(dataframe) >= 4
    assert {"Modelo", "Propiedades", "Confiabilidad", "Limitación"} <= set(dataframe.columns)
    assert dataframe["Confiabilidad"].str.len().eq(5).all()
    assert "★★★★★" in set(dataframe["Confiabilidad"])


def test_theory_persistence():
    assert "theory_expanded_halpin_tsai" in "theory_expanded_halpin_tsai"
    assert "halpin_tsai" in theory_section_keys()


def test_missing_theory_section():
    with pytest.raises(TheoryUnavailableError, match="Información teórica no disponible temporalmente"):
        get_theory_section("missing")
