# Implements: specs/09-teoria-curso.md
"""Pestaña "Teoría": render nativo del contenido conceptual y las fórmulas (U1 + U2)."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.course_theory import COURSE_THEORY, MODEL_MAP, RELIABILITY


def render_theory_tab() -> None:
    st.markdown(
        "Aspectos conceptuales y **fórmulas utilizadas en los cálculos**, extraídos de las "
        "Unidades 1 y 2 del curso (constituyentes, micromecánica y resistencia de la lámina UD)."
    )

    for block in COURSE_THEORY:
        with st.expander(block.title, expanded=(block.key == "porque")):
            for paragraph in block.paragraphs:
                st.markdown(paragraph)
            for bullet in block.bullets:
                st.markdown(f"- {bullet}")
            for caption, latex in block.formulas:
                st.caption(caption)
                st.latex(latex)
            for note in block.notes:
                st.info(note)

    with st.expander("Modelos usados en esta aplicación", expanded=False):
        for prop, model, latex in MODEL_MAP:
            st.markdown(f"**{prop}** — {model}")
            st.latex(latex)

    with st.expander("Confiabilidad de los modelos de resistencia", expanded=False):
        table = pd.DataFrame(
            RELIABILITY,
            columns=["Propiedad", "Modelo", "Confiabilidad", "Limitación"],
        )
        st.dataframe(table, hide_index=True)
