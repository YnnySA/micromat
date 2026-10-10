# Implements: specs/01-visualizacion-resultados.md
# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
# Implements: specs/08-interfaz-vintage-unificada.md
"""Vista Streamlit de resultados micromecánicos."""

import pandas as pd
import streamlit as st

from components.sidebar_inputs import render_sidebar
from components.header import render_header
from components.result_cards import render_result_cards
from components.charts import (
    render_elastic_chart,
    render_strength_chart,
    render_validation_chart,
)
from components.theory_tab import render_theory_tab
from components.rve_view import render_rve_tab
from components.results_tables import render_validation_editor
from components.design_case import render_design_case_tab
from core.calculations import validation_rows_from_props
from core.micromechanics import (
    elastic_properties_from_sidebar,
    strength_properties_from_sidebar,
)


def render_results_page() -> None:
    # 1. Sidebar y cabecera
    fiber_props, matrix_props, vf, fiber_name, matrix_name = render_sidebar()
    render_header(fiber_name, matrix_name, vf)

    # 2. Cálculos (modelos exclusivos del curso)
    elastic = elastic_properties_from_sidebar(fiber_props, matrix_props, vf)
    strength = strength_properties_from_sidebar(fiber_props, matrix_props, vf)

    # 3. Tarjetas de resultados y exportación rápida
    render_result_cards({**elastic, **strength})

    export_df = pd.DataFrame([
        {"Propiedad": "E1", "Valor": round(elastic["E1"], 2), "Unidad": "GPa", "Modelo": "ROM"},
        {"Propiedad": "E2", "Valor": round(elastic["E2"], 2), "Unidad": "GPa", "Modelo": "Halpin-Tsai"},
        {"Propiedad": "G12", "Valor": round(elastic["G12"], 2), "Unidad": "GPa", "Modelo": "Halpin-Tsai"},
        {"Propiedad": "nu12", "Valor": round(elastic["nu12"], 4), "Unidad": "-", "Modelo": "ROM"},
        {"Propiedad": "nu21", "Valor": round(elastic["nu21"], 4), "Unidad": "-", "Modelo": "Reciprocidad"},
        {"Propiedad": "F1t", "Valor": round(strength["F1t"], 1), "Unidad": "MPa", "Modelo": "ROM dominancia fibra"},
        {"Propiedad": "F1c", "Valor": round(strength["F1c"], 1), "Unidad": "MPa", "Modelo": "0.575 x F1t"},
        {"Propiedad": "F2t", "Valor": round(strength["F2t"], 1), "Unidad": "MPa", "Modelo": "Barbero"},
        {"Propiedad": "F2c", "Valor": round(strength["F2c"], 1), "Unidad": "MPa", "Modelo": "4.0 x F2t"},
        {"Propiedad": "F6", "Valor": round(strength["F6"], 1), "Unidad": "MPa", "Modelo": "Barbero"},
    ])
    st.download_button(
        "Descargar resultados actuales (CSV)",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name=f"micromat_{fiber_name}_{matrix_name}_Vf_{int(vf*100)}.csv",
        mime="text/csv",
        key="btn_download_results",
    )

    # 4. Pestañas
    tab_elastic, tab_strength, tab_rve, tab_validation, tab_design, tab_theory = st.tabs(
        ["Módulos Elásticos", "Resistencias", "RVE", "Validación", "Caso práctico", "Teoría"]
    )

    with tab_elastic:
        render_elastic_chart(fiber_props, matrix_props, vf)

    with tab_strength:
        render_strength_chart(fiber_props, matrix_props, vf, fiber_name, matrix_name)

    with tab_rve:
        render_rve_tab(fiber_props, matrix_props, vf)

    with tab_validation:
        st.markdown(
            "Validación del compuesto seleccionado. El valor **Experimental** es editable; "
            "el error se recalcula como |Calculado − Experimental| / Experimental × 100. "
            "Las referencias con error superior al 20% se interpretan como una alerta de "
            "discrepancia del modelo, no como un error de entrada."
        )
        default_experimental = {
            ("IM7", "Epoxi 8552"): {
                "E1": 164.0, "E2": 8.98, "G12": 5.29, "nu12": 0.30,
                "F1t": 2326.0, "F1c": 1200.0, "F2t": 62.3, "F2c": 254.0, "F6": 92.0,
            },
            ("E-glass", "Epoxi GFRP"): {
                "E1": 41.0, "E2": 10.5, "G12": 4.2, "nu12": 0.28,
            },
        }
        experimental = default_experimental.get(
            (fiber_name, matrix_name),
            {name: 0.0 for name in ("E1", "E2", "G12", "nu12", "F1t", "F1c", "F2t", "F2c", "F6")},
        )
        state_key = f"experimental_{fiber_name}_{matrix_name}".replace(" ", "_")
        experimental = st.session_state.setdefault(state_key, experimental.copy())
        validation_rows_selected = validation_rows_from_props(elastic, strength, experimental)
        render_validation_chart(validation_rows_selected)
        edited = render_validation_editor(validation_rows_selected, key=f"validation_{state_key}")
        edited_experimental = {
            row["Propiedad"]: float(row["Experimental"])
            for _, row in edited.iterrows()
        }
        if edited_experimental != experimental:
            st.session_state[state_key] = edited_experimental
            st.rerun()

    with tab_design:
        render_design_case_tab()

    with tab_theory:
        render_theory_tab()
