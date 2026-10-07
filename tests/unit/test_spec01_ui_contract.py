"""Pruebas de contrato de UI para los criterios AC-01-01 a AC-01-05."""

import pytest

from app.components.results_tables import (
    elastic_dataframe,
    strength_dataframe,
    validation_dataframe,
)
from app.components.rve_display import _rve_svg
from app.core.calculations import MATERIALS, elastic_properties, strength_properties, validation_rows


def test_ui_system_selector():
    assert list(MATERIALS) == ["IM7/8552 (CFRP)", "E-glass/Epoxi (GFRP)"]
    assert elastic_properties(MATERIALS["E-glass/Epoxi (GFRP)"]).e1_gpa == pytest.approx(41.175)


def test_elastic_properties_table():
    dataframe = elastic_dataframe(elastic_properties(MATERIALS["IM7/8552 (CFRP)"]))
    assert list(dataframe["Propiedad"]) == ["E1", "E2", "G12", "nu12", "nu21"]
    assert set(dataframe["Unidad"]) == {"GPa", "Adimensional"}


def test_strength_properties_table():
    dataframe = strength_dataframe(strength_properties(MATERIALS["IM7/8552 (CFRP)"]))
    assert len(dataframe) == 5
    assert set(dataframe["Unidad"]) == {"MPa"}
    assert dataframe["Modelo"].notna().all()
    assert dataframe["Confiabilidad"].str.len().eq(5).all()


def test_validation_table():
    dataframe = validation_dataframe(validation_rows(MATERIALS["IM7/8552 (CFRP)"]))
    assert {"Propiedad", "Calculado", "Experimental", "Error %"}.issubset(dataframe.columns)
    assert dataframe.loc[dataframe["Propiedad"] == "E1", "Error %"].iloc[0] > 2.0


def test_rve_display():
    svg = _rve_svg(MATERIALS["IM7/8552 (CFRP)"])
    assert "<svg" in svg
    assert "RVE generado por RSA" in svg
    assert svg.count("<circle") == MATERIALS["IM7/8552 (CFRP)"].rve["fibers"]
