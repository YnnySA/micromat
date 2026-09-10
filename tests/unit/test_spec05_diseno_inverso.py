# Implements: specs/05-diseno-inverso.md
"""Tests unitarios para SPEC-05."""

import pytest
import os
from streamlit.testing.v1 import AppTest
from app.core.calculations import MATERIALS, inverse_design_search

def test_inverse_design_logic():
    # Verifica que el diseño inverso encuentre una solución factible
    res = inverse_design_search(MATERIALS["IM7/8552 (CFRP)"], 40000.0, 700.0, 0.65)
    assert res.factible
    assert res.vf_min is not None
    assert 0.01 <= res.vf_min <= 0.65

def test_infeasible_design_logic():
    # Verifica que el diseño inverso reporte no factible
    res = inverse_design_search(MATERIALS["IM7/8552 (CFRP)"], 300000.0, 7000.0, 0.65)
    assert not res.factible

def test_ui_diseno_inverso_page_load():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    at = AppTest.from_file(os.path.join(root, "app/pages/02_diseno_inverso.py")).run()
    assert not at.exception
    # Verifica campos de entrada
    assert len(at.number_input) >= 2
    assert len(at.slider) >= 1
    assert len(at.button) >= 1
