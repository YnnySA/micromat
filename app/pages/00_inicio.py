# Implements: specs/03-interfaz-limpia.md
"""Página de inicio y configuración de navegación."""

import streamlit as st

st.set_page_config(page_title="Materiales Compuestos", layout="wide")

st.title("Micromecánica de Materiales Compuestos")
st.markdown("""
Esta aplicación permite analizar propiedades elásticas y de resistencia de sistemas CFRP y GFRP.
Utilice la barra lateral para navegar entre las funcionalidades:
- **Resultados**: Visualización detallada y validación experimental.
- **Estudio Paramétrico**: Análisis de sensibilidad del Vf.
- **Diseño Inverso**: Optimización para requisitos de diseño.
""")
