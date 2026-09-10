# Implements: specs/06-seleccion-materiales.md
"""Componente para la selección e interacción con materiales."""

from __future__ import annotations

import streamlit as st
from core.materials_db import MATERIALS

def render_material_selector() -> None:
    st.sidebar.subheader("Selección de Material")
    
    # Inicializar estado si no existe
    if "selected_fiber" not in st.session_state:
        st.session_state.selected_fiber = "IM7/8552 (CFRP)"
    if "selected_matrix" not in st.session_state:
        st.session_state.selected_matrix = "IM7/8552 (CFRP)"
        
    def on_change():
        st.session_state.selected_fiber = st.session_state.fiber_selector
        st.session_state.selected_matrix = st.session_state.matrix_selector
        
    st.sidebar.selectbox(
        "Fibra",
        options=list(MATERIALS.keys()) + ["Personalizado"],
        key="fiber_selector",
        index=list(MATERIALS.keys()).index(st.session_state.selected_fiber) 
        if st.session_state.selected_fiber in MATERIALS else len(MATERIALS),
        on_change=on_change
    )
    
    st.sidebar.selectbox(
        "Matriz",
        options=list(MATERIALS.keys()) + ["Personalizado"],
        key="matrix_selector",
        index=list(MATERIALS.keys()).index(st.session_state.selected_matrix) 
        if st.session_state.selected_matrix in MATERIALS else len(MATERIALS),
        on_change=on_change
    )
    
    st.sidebar.info(f"Fibra: {st.session_state.selected_fiber}\nMatriz: {st.session_state.selected_matrix}")

