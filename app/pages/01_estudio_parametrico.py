# Implements: specs/04-estudio-parametrico.md
"""Página UI de Estudio Paramétrico."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from components.parametric_charts import plot_e1_e2, plot_g12_nu12, plot_strength_im7
from core.calculations import MATERIALS, optimal_vf


def render_parametric_page() -> None:
    st.title("Estudio Paramétrico")
    st.markdown("""
    Explore la variación de las propiedades elásticas y de resistencia en función de la fracción volumétrica de fibra ($V_f$).
    """)
    
    # Selector de rango con validación
    columns = st.columns(2)
    vf_min = columns[0].slider("Vf mínimo", min_value=0.0, max_value=1.0, value=0.30, step=0.01)
    vf_max = columns[1].slider("Vf máximo", min_value=0.0, max_value=1.0, value=0.65, step=0.01)
    
    # Validaciones del rango
    is_valid = True
    if vf_min >= vf_max:
        st.error("Error: El rango de Vf es inválido (Vf_min debe ser menor que Vf_max)")
        is_valid = False
        
    if vf_max > 0.65:
        st.warning("Vf > 0.65 puede no ser físicamente alcanzable en la práctica.")
        
    if is_valid:
        # Pestañas para organizar la visualización
        tab_elastic, tab_strength, tab_opt = st.tabs([
            "Módulos Elásticos (E1, E2, G12, ν12)", 
            "Resistencias (F1t, F1c)", 
            "Rigidez Específica & Vf Óptimo"
        ])
        
        with tab_elastic:
            st.plotly_chart(plot_e1_e2(vf_min, vf_max))
            st.markdown("""
            **Interpretación:**
            - $E_1$ crece de forma estrictamente lineal con $V_f$ en ambos sistemas bajo la Regla de Mezclas (ROM). El compuesto con fibra IM7 exhibe una pendiente mucho mayor debido a la extrema rigidez longitudinal de la fibra de carbono frente al vidrio.
            - $E_2$ calculado por Halpin-Tsai muestra un comportamiento no lineal donde la matriz tiene un papel predominante. Nótese que la simple interpolación lineal (ROM) para $E_2$ sobreestima drásticamente la propiedad transversal, por lo que Halpin-Tsai es el modelo físicamente adecuado.
            """)
            st.plotly_chart(plot_g12_nu12(vf_min, vf_max))
            st.markdown("""
            **Interpretación:**
            - $G_{12}$ exhibe crecimiento parabólico bajo el modelo de Halpin-Tsai.
            - $\\nu_{12}$ decrece de forma perfectamente lineal ya que el coeficiente de Poisson de las fibras es menor que el de la matriz.
            """)
            
        with tab_strength:
            st.plotly_chart(plot_strength_im7(vf_min, vf_max))
            st.markdown("""
            **Interpretación (IM7/8552):**
            - Las resistencias longitudinales $F_{1t}$ y $F_{1c}$ aumentan linealmente con $V_f$.
            - El microbuckling práctico ($F_{1c}$) es significativamente menor que la resistencia a tracción longitudinal ($F_{1t}$), siendo usualmente el criterio crítico en diseño.
            """)
            
        with tab_opt:
            st.subheader("Optimización de Rigidez Específica ($E1/\\rho$)")
            
            opt_data = []
            for name, material in MATERIALS.items():
                v_opt, max_stiff = optimal_vf(material, vf_min, vf_max)
                opt_data.append({
                    "Sistema": name,
                    "Vf Óptimo": round(v_opt, 3),
                    "Rigidez Esp. Máxima [MPa*m³/kg]": round(max_stiff, 2)
                })
                
            st.dataframe(pd.DataFrame(opt_data), hide_index=True)
            st.info(
                "La rigidez específica máxima ($E_1/\\rho$) se maximiza en el límite superior del rango de Vf debido a la alta rigidez longitudinal de la fibra en relación con su densidad."
            )


if __name__ == "__main__":
    render_parametric_page()
