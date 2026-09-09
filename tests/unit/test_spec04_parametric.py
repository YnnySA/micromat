# Implements: specs/04-estudio-parametrico.md
"""Tests unitarios para SPEC-04."""

import pytest
import os
from streamlit.testing.v1 import AppTest
from core.calculations import MATERIALS, optimal_vf, parametric_sweep

def test_parametric_sweep_logic():
    # Verifica la lógica básica del barrido
    sweep = parametric_sweep(MATERIALS["IM7/8552 (CFRP)"], 0.3, 0.65, steps=10)
    assert len(sweep["vf"]) == 10
    assert len(sweep["e1"]) == 10
    assert sweep["e1"][0] < sweep["e1"][-1] # E1 aumenta con Vf

def test_optimal_vf():
    # Verifica el cálculo del Vf óptimo
    vf_opt, _ = optimal_vf(MATERIALS["IM7/8552 (CFRP)"], 0.3, 0.65)
    assert 0.3 <= vf_opt <= 0.65

def test_ui_parametric_page_load():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    at = AppTest.from_file(os.path.join(root, "app/pages/01_estudio_parametrico.py")).run()
    # Verifica que la página cargue sin excepciones
    assert not at.exception
    # Verifica elementos básicos de la UI
    assert len(at.slider) >= 2
    assert len(at.tabs) >= 3
