# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
# Implements: specs/08-interfaz-vintage-unificada.md
"""Componente de cabecera para la aplicación (100% Streamlit nativo)."""

import streamlit as st


def render_header(fiber_name: str, matrix_name: str, vf: float) -> None:
    title_col, badge_col = st.columns([5, 1], vertical_alignment="center")
    with title_col:
        st.subheader(":material/science: Micromecánica de Materiales Compuestos")
    with badge_col:
        st.badge("v1.0")
    st.caption(
        f"PROPIEDADES CALCULADAS — Vf = {vf:.0%} · {fiber_name} / {matrix_name}"
        "   |   Halpin-Tsai · Regla de Mezclas · Tsai-Wu"
    )
