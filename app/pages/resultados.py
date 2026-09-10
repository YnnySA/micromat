# Implements: specs/01-visualizacion-resultados.md
# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
"""Vista Streamlit de resultados micromecanicos."""

import streamlit as st
import numpy as np
from components.sidebar_inputs import render_sidebar
from components.header import render_header
from components.result_cards import render_result_cards
from components.charts import (
    render_elastic_chart,
    render_strength_chart,
    render_offaxis_chart,
    render_envelope_chart,
    render_comparison_chart,
)
from core.micromechanics import elastic_properties_from_sidebar, strength_properties_from_sidebar


def render_results_page() -> None:
    # 1. Sidebar y Header
    fiber_props, matrix_props, Vf, fiber_name, matrix_name = render_sidebar()
    render_header(fiber_name, matrix_name, Vf)

    # 2. Calculos
    elastic = elastic_properties_from_sidebar(fiber_props, matrix_props, Vf)
    strength = strength_properties_from_sidebar(fiber_props, matrix_props, Vf)

    props_flat = {**elastic, **strength}

    # 3. Layout
    render_result_cards(props_flat)

    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["Módulos Elásticos", "Resistencias", "Off-Axis", "Envolvente", "Comparación"]
    )

    # Datos para graficos de barrido
    vf_data = np.arange(0.05, 0.81, 0.01)

    with tab1:
        elastic_sweep = {"E1": [], "E2": [], "G12": [], "nu12": []}
        for v in vf_data:
            e = elastic_properties_from_sidebar(fiber_props, matrix_props, v)
            elastic_sweep["E1"].append(e["E1"])
            elastic_sweep["E2"].append(e["E2"])
            elastic_sweep["G12"].append(e["G12"])
            elastic_sweep["nu12"].append(e["nu12"])
        render_elastic_chart(vf_data, elastic_sweep, Vf)

    with tab2:
        strength_sweep = {"F1t": [], "F1c": [], "F2t": [], "F2c": [], "F12s": []}
        for v in vf_data:
            s = strength_properties_from_sidebar(fiber_props, matrix_props, v)
            strength_sweep["F1t"].append(s["F1t"])
            strength_sweep["F1c"].append(s["F1c"])
            strength_sweep["F2t"].append(s["F2t"])
            strength_sweep["F2c"].append(s["F2c"])
            strength_sweep["F12s"].append(s["F12s"])
        render_strength_chart(vf_data, strength_sweep, Vf)

    with tab3:
        render_offaxis_chart(props_flat)

    with tab4:
        render_envelope_chart(props_flat)

    with tab5:
        render_comparison_chart(matrix_props, Vf)
