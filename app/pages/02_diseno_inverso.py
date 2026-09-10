# Implements: specs/05-diseno-inverso.md
# Implements: specs/06-seleccion-materiales.md
"""Página UI de Diseño Inverso."""

from __future__ import annotations

import streamlit as st
import pandas as pd
from components.material_selector import render_material_selector

from core.calculations import MATERIALS, inverse_design_search


def render_inverse_design_page() -> None:
    render_material_selector()
    st.title("Diseño Inverso")
    st.markdown("""
    Encuentre la fracción volumétrica de fibra ($V_f$) mínima necesaria para cumplir con requisitos de rigidez y resistencia.
    """)
    
    with st.form("design_params"):
        col1, col2, col3 = st.columns(3)
        e1_req = col1.number_input("E1 mínimo [GPa]", min_value=1.0, value=40.0, step=1.0)
        f1t_req = col2.number_input("F1t mínimo [MPa]", min_value=10.0, value=700.0, step=10.0)
        vf_max = col3.slider("Vf máximo permitido", min_value=0.1, max_value=1.0, value=0.65, step=0.01)
        
        submitted = st.form_submit_button("Ejecutar diseño inverso")
    
    if submitted:
        results = []
        for name, material in MATERIALS.items():
            res = inverse_design_search(material, e1_req * 1000.0, f1t_req, vf_max)
            results.append({
                "Sistema": name,
                "¿Factible?": "Sí" if res.factible else "No",
                "Vf mínimo": round(res.vf_min, 4) if res.factible else "N/A",
                "E1 [GPa]": round(res.e1_at_vf / 1000.0, 2) if res.factible else "N/A",
                "F1t [MPa]": round(res.f1t_at_vf, 1) if res.factible else "N/A",
                "ρ [kg/m³]": round(res.density, 1) if res.factible else "N/A",
                "E1/ρ": round(res.specific_stiffness, 2) if res.factible else "N/A",
                "Restricción Activa": res.active_constraint if res.factible else "N/A"
            })
            
        st.subheader("Resultados de la búsqueda")
        st.dataframe(pd.DataFrame(results), hide_index=True)
        
        # Recomendación simple
        feasible = [r for r in results if r["¿Factible?"] == "Sí"]
        if feasible:
            st.success("Se encontraron soluciones factibles.")
            # Simple lógica para elegir la mejor rigidez específica
            best = max(feasible, key=lambda x: x["E1/ρ"])
            st.write(f"Recomendación: El sistema **{best['Sistema']}** es preferible por su mayor rigidez específica.")
        else:
            st.error("No se encontraron soluciones factibles para los requisitos indicados.")

if __name__ == "__main__":
    render_inverse_design_page()
