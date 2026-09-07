# Implements: specs/02-espacio-teoria-analisis.md
"""Componentes UI para el espacio de teoría y análisis."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.theory import (
    RELIABILITY_NOTES,
    TheorySection,
    TheoryUnavailableError,
    get_theory_section,
    interpretation_for_system,
)


def render_theory_section(section: TheorySection, expanded: bool = True) -> None:
    with st.expander(section.title, expanded=expanded):
        st.markdown(section.definition)
        for formula in section.formulas:
            st.latex(formula)
        for detail in section.details:
            st.markdown(f"- {detail}")
        if section.properties:
            st.caption(f"Propiedades relacionadas: {', '.join(section.properties)}")


def render_theory_panel() -> None:
    st.subheader("Espacio de teoría y análisis")
    for key in ("rom", "halpin_tsai", "barbero", "rosen"):
        state_key = f"theory_expanded_{key}"
        expanded = st.session_state.setdefault(state_key, True)
        try:
            render_theory_section(get_theory_section(key), expanded=expanded)
        except TheoryUnavailableError as exc:
            st.error(str(exc))
            if st.button("Reintentar carga", key=f"retry_theory_{key}"):
                st.rerun()


def render_interpretation(system_name: str) -> None:
    with st.expander("Interpretación", expanded=True):
        for explanation in interpretation_for_system(system_name):
            st.markdown(f"- {explanation}")


def reliability_dataframe() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Modelo": note.model,
                "Propiedades": note.properties,
                "Confiabilidad": note.reliability,
                "Limitación": note.limitation,
            }
            for note in RELIABILITY_NOTES
        ]
    )


def render_reliability_table() -> None:
    with st.expander("Confiabilidad de modelos", expanded=True):
        st.dataframe(reliability_dataframe(), hide_index=True, width="stretch")
