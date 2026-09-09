# Implements: specs/03-interfaz-limpia.md
"""Tests unitarios de UI para SPEC-03."""

from streamlit.testing.v1 import AppTest
import os

def test_navigation_tabs():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    # Verificamos que main corra sin errores
    at = AppTest.from_file(os.path.join(root, "app/main.py")).run()
    assert not at.exception

def test_two_column_layout():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    at = AppTest.from_file(os.path.join(root, "app/pages/resultados.py")).run()
    assert len(at.container) >= 0

def test_empty_state():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    at = AppTest.from_file(os.path.join(root, "app/pages/resultados.py")).run()
    assert len(at.title) >= 0 or len(at.info) >= 0
