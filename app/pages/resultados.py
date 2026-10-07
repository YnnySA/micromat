# Implements: specs/01-visualizacion-resultados.md
# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
# Implements: specs/08-interfaz-vintage-unificada.md
"""Vista Streamlit de resultados micromecánicos."""

import streamlit as st

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
from components.theory_tab import render_theory_tab
from components.rve_view import render_rve_tab
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
    props_flat = {**elastic, **strength}

    # 3. Tarjetas de resultados
    render_result_cards(props_flat)

    # 4. Pestañas
    tab_elastic, tab_strength, tab_rve, tab_offaxis, tab_envelope, tab_compare, tab_theory = st.tabs(
        ["Módulos Elásticos", "Resistencias", "RVE", "Off-Axis", "Envolvente", "Comparación", "Teoría"]
    )

    with tab_elastic:
        render_elastic_chart(fiber_props, matrix_props, vf)

    with tab_strength:
        render_strength_chart(fiber_props, matrix_props, vf, fiber_name, matrix_name)

    with tab_rve:
        render_rve_tab(fiber_props, matrix_props, vf)

    with tab_offaxis:
        render_offaxis_chart(props_flat)

    with tab_envelope:
        render_envelope_chart(props_flat)

    with tab_compare:
        render_comparison_chart(matrix_props, vf)

    with tab_theory:
        render_theory_tab()
