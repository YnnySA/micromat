"""Pruebas unitarias de SPEC-01."""

import json

import pytest

from app.core.calculations import (
    InvalidResultsFileError,
    MATERIALS,
    elastic_properties,
    load_results_file,
    strength_properties,
    validation_rows,
)


def test_elastic_properties_table_contract():
    properties = elastic_properties(MATERIALS["IM7/8552 (CFRP)"])
    assert properties.e1_gpa == pytest.approx(167.468)
    assert properties.e2_gpa == pytest.approx(10.7716, rel=1e-3)
    assert properties.g12_gpa == pytest.approx(5.5702, rel=1e-3)
    assert properties.nu21 == pytest.approx(properties.nu12 * properties.e2_gpa / properties.e1_gpa)


def test_strength_properties_table_contract():
    properties = strength_properties(MATERIALS["IM7/8552 (CFRP)"])
    assert properties.f1t.value_mpa == pytest.approx(3142.932)
    assert properties.f1c.value_mpa == pytest.approx(1807.186)
    assert properties.f2t.value_mpa == pytest.approx(95.991, rel=1e-3)
    assert properties.f2c.value_mpa == pytest.approx(4 * properties.f2t.value_mpa)
    assert properties.f6.value_mpa == pytest.approx(51.935, rel=1e-3)


def test_validation_table():
    rows = validation_rows(MATERIALS["IM7/8552 (CFRP)"])
    assert len(rows) == 9
    e1 = next(row for row in rows if row.property_name == "E1")
    assert e1.error_percent == pytest.approx(2.1146, rel=1e-3)
    assert any(row.exceeds_twenty_percent for row in rows)


def test_invalid_results_file(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{not-json", encoding="utf-8")
    with pytest.raises(InvalidResultsFileError, match="JSON válido"):
        load_results_file(invalid)

    missing_system = tmp_path / "missing-system.json"
    missing_system.write_text(json.dumps({"results": {}}), encoding="utf-8")
    with pytest.raises(InvalidResultsFileError, match="system"):
        load_results_file(missing_system)
