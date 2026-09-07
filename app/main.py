# Implements: specs/01-visualizacion-resultados.md
"""Punto de entrada principal de la aplicación Streamlit."""

import streamlit as st

st.set_page_config(page_title="Micromecánica — Resultados", page_icon="📊", layout="wide")

page = st.navigation(
    [
        st.Page("pages/resultados.py", title="Resultados", icon=":material/analytics:"),
    ],
    position="top",
)
page.run()
