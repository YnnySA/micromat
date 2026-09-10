# Implements: specs/03-interfaz-limpia.md
# Implements: specs/06-seleccion-materiales.md
"""Página de inicio y configuración de navegación."""

import streamlit as st
from components.material_selector import render_material_selector

render_material_selector()

st.title("Micromecánica de Materiales Compuestos")
st.markdown("""
Esta aplicación permite analizar propiedades elásticas y de resistencia de sistemas CFRP y GFRP.
Utilice la barra lateral para navegar entre las funcionalidades:
- **Resultados**: Visualización detallada y validación experimental.
- **Estudio Paramétrico**: Análisis de sensibilidad del Vf.
- **Diseño Inverso**: Optimización para requisitos de diseño.
""")
