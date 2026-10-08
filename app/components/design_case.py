# Implements: specs/05-diseno-inverso.md
"""Visualización del caso práctico de diseño inverso de la Tarea 1."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from core.calculations import MATERIALS, inverse_design_search, inverse_design_sweep

from components.charts import (
    ACCENT,
    INK,
    LINE_WIDTH,
    OLIVE,
    PLOTLY_LAYOUT,
    RUST,
    VIOLET,
)


SYSTEM_COLORS = {
    "IM7/8552 (CFRP)": ACCENT,
    "E-glass/Epoxi (GFRP)": VIOLET,
}


def _result_row(name: str, result) -> dict[str, object]:
    if not result.factible:
        return {
            "Sistema": name,
            "Factible": "No",
            "Vf mínimo": "—",
            "E₁ en Vf mínimo [GPa]": "—",
            "F₁ₜ en Vf mínimo [MPa]": "—",
            "ρ [kg/m³]": "—",
            "E₁/ρ [MPa·m³/kg]": "—",
            "Restricción activa": "—",
        }

    return {
        "Sistema": name,
        "Factible": "Sí",
        "Vf mínimo": round(result.vf_min, 4),
        "E₁ en Vf mínimo [GPa]": round(result.e1_at_vf / 1000.0, 2),
        "F₁ₜ en Vf mínimo [MPa]": round(result.f1t_at_vf, 1),
        "ρ [kg/m³]": round(result.density, 1),
        "E₁/ρ [MPa·m³/kg]": round(result.specific_stiffness, 2),
        "Restricción activa": result.active_constraint,
    }


def _render_design_chart(
    sweeps: dict[str, dict],
    e1_req_mpa: float,
    f1t_req_mpa: float,
) -> None:
    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Rigidez longitudinal", "Resistencia longitudinal"),
        horizontal_spacing=0.10,
    )

    for name, sweep in sweeps.items():
        color = SYSTEM_COLORS.get(name, OLIVE)
        vf = sweep["vf"]
        result_index = sweep["first_index"]
        fig.add_trace(
            go.Scatter(
                x=vf,
                y=sweep["e1_mpa"] / 1000.0,
                name=f"E₁ {name}",
                line=dict(color=color, width=LINE_WIDTH),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=vf,
                y=sweep["f1t_mpa"],
                name=f"F₁ₜ {name}",
                line=dict(color=color, width=LINE_WIDTH, dash="dash"),
                showlegend=True,
            ),
            row=1,
            col=2,
        )
        if result_index is not None:
            vf_design = float(vf[result_index])
            fig.add_trace(
                go.Scatter(
                    x=[vf_design],
                    y=[float(sweep["e1_mpa"][result_index] / 1000.0)],
                    mode="markers+text",
                    marker=dict(
                        color=color,
                        size=15,
                        symbol="diamond",
                        line=dict(color=INK, width=2),
                    ),
                    text=[f"Vf = {vf_design:.3f}"],
                    textposition="top center",
                    textfont=dict(color=INK, size=10),
                    cliponaxis=False,
                    name=f"Punto de diseño E₁ — {name}",
                    showlegend=True,
                ),
                row=1,
                col=1,
            )
            fig.add_trace(
                go.Scatter(
                    x=[vf_design],
                    y=[float(sweep["f1t_mpa"][result_index])],
                    mode="markers+text",
                    marker=dict(
                        color=color,
                        size=15,
                        symbol="diamond",
                        line=dict(color=INK, width=2),
                    ),
                    text=[f"Vf = {vf_design:.3f}"],
                    textposition="top center",
                    textfont=dict(color=INK, size=10),
                    cliponaxis=False,
                    name=f"Punto de diseño F₁ₜ — {name}",
                    showlegend=False,
                ),
                row=1,
                col=2,
            )
            fig.add_vline(
                x=vf_design,
                line=dict(color=color, width=1, dash="dot"),
                row=1,
                col=1,
            )
            fig.add_vline(
                x=vf_design,
                line=dict(color=color, width=1, dash="dot"),
                row=1,
                col=2,
            )

    fig.add_hline(
        y=e1_req_mpa / 1000.0,
        line=dict(color=INK, width=1, dash="dash"),
        annotation_text=f"E₁ requerido = {e1_req_mpa / 1000.0:g} GPa",
        row=1,
        col=1,
    )
    fig.add_hline(
        y=f1t_req_mpa,
        line=dict(color=RUST, width=1, dash="dash"),
        annotation_text=f"F₁ₜ requerido = {f1t_req_mpa:g} MPa",
        row=1,
        col=2,
    )
    layout = dict(PLOTLY_LAYOUT)
    layout["legend"] = dict(
        bgcolor=PLOTLY_LAYOUT["paper_bgcolor"],
        bordercolor=PLOTLY_LAYOUT["legend"]["bordercolor"],
        borderwidth=1,
        orientation="h",
        y=-0.20,
    )
    fig.update_layout(**layout, title="Caso práctico: requisitos del tubo de bicicleta")
    fig.update_xaxes(title_text="Vf [-]", range=[0.0, None])
    fig.update_yaxes(title_text="E₁ [GPa]", row=1, col=1)
    fig.update_yaxes(title_text="F₁ₜ [MPa]", row=1, col=2)
    st.plotly_chart(fig, width="stretch")
    st.caption(
        "◆ Punto de diseño: primer Vf que cumple simultáneamente los requisitos. "
        "La etiqueta junto al rombo muestra el Vf mínimo de cada sistema."
    )


def render_design_case_tab() -> None:
    st.markdown(
        "Determine el Vf mínimo para un tubo UD orientado a 0° que cumpla "
        "simultáneamente E₁ ≥ 40 GPa, F₁ₜ ≥ 700 MPa y Vf ≤ 0.65. "
        "Los requisitos son editables y se evalúan para IM7/8552 y E-glass/Epoxi."
    )

    col1, col2, col3 = st.columns(3)
    e1_req_gpa = col1.number_input(
        "E₁ mínimo [GPa]",
        min_value=0.1,
        value=40.0,
        step=1.0,
        format="%.2f",
        key="design_e1_req",
    )
    f1t_req_mpa = col2.number_input(
        "F₁ₜ mínimo [MPa]",
        min_value=0.1,
        value=700.0,
        step=10.0,
        format="%.1f",
        key="design_f1t_req",
    )
    vf_max = col3.number_input(
        "Vf máximo permitido",
        min_value=0.01,
        max_value=0.65,
        value=0.65,
        step=0.01,
        format="%.2f",
        key="design_vf_max",
    )

    e1_req_mpa = e1_req_gpa * 1000.0
    sweeps = {
        name: inverse_design_sweep(
            material,
            e1_req_mpa,
            f1t_req_mpa,
            vf_max,
        )
        for name, material in MATERIALS.items()
    }
    results = {
        name: inverse_design_search(material, e1_req_mpa, f1t_req_mpa, vf_max)
        for name, material in MATERIALS.items()
    }

    st.subheader("Resultados comparativos")
    st.dataframe(
        pd.DataFrame(
            [_result_row(name, result) for name, result in results.items()]
        ),
        hide_index=True,
        width="stretch",
    )

    _render_design_chart(sweeps, e1_req_mpa, f1t_req_mpa)

    feasible = [
        (name, result)
        for name, result in results.items()
        if result.factible
    ]
    if not feasible:
        st.error(
            "No se encontró una solución factible con Vf ≤ "
            f"{vf_max:.2f}. Relaje los requisitos o cambie el sistema de material."
        )
        return

    best = max(feasible, key=lambda item: item[1].specific_stiffness)
    st.info(
        f"El sistema recomendado por rigidez específica es **{best[0]}** "
        f"(E₁/ρ = {best[1].specific_stiffness:.2f} MPa·m³/kg). "
        "El rombo del gráfico marca el primer Vf que satisface ambos requisitos; "
        "la línea vertical identifica el punto mínimo de diseño."
    )
