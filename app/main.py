# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
# Implements: specs/08-interfaz-vintage-unificada.md
"""Punto de entrada único de la aplicación Streamlit.

El tema (papel sepia, tipografía monoespaciada) se define íntegramente en
`.streamlit/config.toml`; no se inyecta CSS ni HTML desde Python.
"""

import streamlit as st

st.set_page_config(layout="wide", page_title="Micromecánica v1.0", page_icon="🔬")

from pages.resultados import render_results_page


navigation = st.navigation(
    [st.Page(render_results_page, title="Micromecánica", icon="🔬")],
    position="hidden",
)
navigation.run()
