# Implements: specs/03-interfaz-limpia.md
"""Punto de entrada principal de la aplicacion Streamlit."""

import streamlit as st

# Configuración de navegación automatizada
pg = st.navigation([
    st.Page("pages/00_inicio.py", title="Inicio", icon="🏠"),
    st.Page("pages/resultados.py", title="Resultados", icon="📊"),
    st.Page("pages/01_estudio_parametrico.py", title="Estudio Paramétrico", icon="📈"),
])
pg.run()
