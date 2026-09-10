# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
"""Componente para mostrar tarjetas de resultados."""

import streamlit as st
from styles.theme import CYAN, GREEN, ORANGE, PURPLE, RED, GRAY

def render_result_cards(props: dict):
    # Fila 1: Elásticas
    cols1 = st.columns(5)
    cards_elastic = [
        ("E1",   props["E1"],   "GPa", CYAN),
        ("E2",   props["E2"],   "GPa", GREEN),
        ("G12",  props["G12"],  "GPa", ORANGE),
        ("nu12", props["nu12"], "",    PURPLE),
        ("nu21", props["nu21"], "",    GRAY),
    ]
    for col, (label, value, unit, color) in zip(cols1, cards_elastic):
        with col:
            decimals = 4 if label in ("nu12", "nu21") else 2
            st.markdown(f'''
            <div style="background:#111827; border:1px solid #1e3a5f; border-top:2px solid {color};
                        border-radius:6px; padding:12px 10px; text-align:center; margin-bottom:8px;">
              <div style="color:#4a6080;font-size:9px;letter-spacing:0.1em;margin-bottom:4px;">{label}</div>
              <div style="color:{color};font-size:18px;font-weight:600;font-family:'JetBrains Mono',monospace;">
                {value:.{decimals}f}
              </div>
              <div style="color:#4a6080;font-size:9px;">{unit}</div>
            </div>
            ''', unsafe_allow_html=True)

    # Fila 2: Resistencia
    cols2 = st.columns(5)
    cards_strength = [
        ("F1t",  props["F1t"],  "MPa", CYAN),
        ("F1c",  props["F1c"],  "MPa", RED),
        ("F2t",  props["F2t"],  "MPa", GREEN),
        ("F2c",  props["F2c"],  "MPa", PURPLE),
        ("F12s", props["F12s"], "MPa", ORANGE),
    ]
    for col, (label, value, unit, color) in zip(cols2, cards_strength):
        with col:
            st.markdown(f'''
            <div style="background:#111827; border:1px solid #1e3a5f; border-top:2px solid {color};
                        border-radius:6px; padding:12px 10px; text-align:center; margin-bottom:8px;">
              <div style="color:#4a6080;font-size:9px;letter-spacing:0.1em;margin-bottom:4px;">{label}</div>
              <div style="color:{color};font-size:18px;font-weight:600;font-family:'JetBrains Mono',monospace;">
                {value:.1f}
              </div>
              <div style="color:#4a6080;font-size:9px;">{unit}</div>
            </div>
            ''', unsafe_allow_html=True)
