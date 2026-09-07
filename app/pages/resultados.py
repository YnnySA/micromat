# Implements: specs/01-visualizacion-resultados.md
# Implements: specs/02-espacio-teoria-analisis.md
"""Vista Streamlit de resultados micromecánicos."""

from __future__ import annotations

import streamlit as st

from components.results_tables import (
    render_elastic_table,
    render_strength_table,
    render_validation_table,
)
from components.rve_display import render_rve
from components.theory_panel import (
    render_interpretation,
    render_reliability_table,
    render_theory_panel,
)
from core.calculations import (
    InvalidResultsFileError,
    MATERIALS,
    elastic_properties,
    load_results_file,
    strength_properties,
    validation_rows,
)


def render_results_page() -> None:
    st.title("Resultados micromecánicos")
    selected_name = st.segmented_control(
        "Sistema de material",
        options=list(MATERIALS),
        default="IM7/8552 (CFRP)",
        key="results_material_system",
    )
    material = MATERIALS[selected_name or "IM7/8552 (CFRP)"]
    st.caption(f"Fracción volumétrica de referencia: Vf = {material.vf_reference:.2f}")

    with st.container(border=True):
        st.subheader("Propiedades elásticas")
        render_elastic_table(elastic_properties(material))
        render_interpretation(material.name)

    with st.container(border=True):
        st.subheader("Propiedades de resistencia")
        render_strength_table(strength_properties(material))
        st.caption("La confiabilidad se expresa con estrellas según el modelo utilizado.")
        render_reliability_table()

    with st.container(border=True):
        render_theory_panel()

    compare = st.toggle("Comparar con valores experimentales", key="results_compare_experimental")
    if compare:
        with st.container(border=True):
            st.subheader("Validación experimental")
            render_validation_table(validation_rows(material))
            st.info(
                "Los errores superiores al 20 % se resaltan. Barbero, Rosen y las "
                "estimaciones empíricas son modelos de prediseño y requieren validación experimental."
            )

    with st.expander("Visualización RVE", expanded=True):
        render_rve(material)

    with st.expander("Cargar archivo de resultados JSON"):
        uploaded = st.file_uploader("Archivo JSON", type=["json"], key="results_file")
        if uploaded is not None:
            temporary_path = None
            try:
                temporary_path = _write_uploaded_file(uploaded)
                payload = load_results_file(temporary_path)
                st.success(f"Archivo válido para {payload['system']}.")
            except InvalidResultsFileError as exc:
                st.error(str(exc))
            finally:
                if temporary_path is not None:
                    temporary_path.unlink(missing_ok=True)


def _write_uploaded_file(uploaded_file):
    import tempfile
    from pathlib import Path

    handle = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    handle.write(uploaded_file.getvalue())
    handle.close()
    return Path(handle.name)
