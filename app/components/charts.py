# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md (Section 8)
"""Componentes de graficos Plotly para la vista de resultados."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.calculations import offAxisStiffness, calcProps
from components.sidebar_inputs import FIBER_PRESETS
from styles.theme import (
    BG_CHART, BORDER_DIM, CYAN, GREEN, ORANGE, PURPLE, RED, GRAY,
    TEXT_PRIMARY, TEXT_LABEL, TEXT_MUTED, FONT_MONO,
)

PLOTLY_LAYOUT = dict(
    paper_bgcolor=BG_CHART,
    plot_bgcolor=BG_CHART,
    font=dict(family="JetBrains Mono, monospace", size=11, color=TEXT_PRIMARY),
    xaxis=dict(gridcolor=BORDER_DIM, linecolor=BORDER_DIM, zerolinecolor=BORDER_DIM),
    yaxis=dict(gridcolor=BORDER_DIM, linecolor=BORDER_DIM, zerolinecolor=BORDER_DIM),
    legend=dict(bgcolor=BG_CHART, bordercolor=BORDER_DIM, borderwidth=1),
    margin=dict(l=50, r=20, t=40, b=40),
    height=380,
)


def render_elastic_chart(vf_data: np.ndarray, elastic_data: dict, vf_current: float) -> None:
    """Tab 'Modulos Elasticos': E1/E2/G12 vs Vf + nu12 vs Vf."""
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vf_data, y=elastic_data["E1"], name="E1", line=dict(color=CYAN, width=2.5)))
        fig.add_trace(go.Scatter(x=vf_data, y=elastic_data["E2"], name="E2", line=dict(color=GREEN, width=2.5)))
        fig.add_trace(go.Scatter(x=vf_data, y=elastic_data["G12"], name="G12", line=dict(color=ORANGE, width=2.5)))
        fig.add_vline(x=vf_current, line=dict(color=TEXT_MUTED, width=1, dash="dash"))
        fig.update_layout(**PLOTLY_LAYOUT, title="Módulos vs Fracción de Volumen", xaxis_title="Vf", yaxis_title="Módulo [GPa]")
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=vf_data, y=elastic_data["nu12"], name="nu12", line=dict(color=PURPLE, width=2.5)))
        fig2.add_vline(x=vf_current, line=dict(color=TEXT_MUTED, width=1, dash="dash"))
        fig2.update_layout(**PLOTLY_LAYOUT, title="Coeficiente de Poisson nu12 vs Vf", xaxis_title="Vf", yaxis_title="nu12")
        st.plotly_chart(fig2, width="stretch")


def render_strength_chart(vf_data: np.ndarray, strength_data: dict, vf_current: float) -> None:
    """Tab 'Resistencias': F1t/F1c vs Vf + F2t/F2c/F12s vs Vf."""
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=vf_data, y=strength_data["F1t"], name="F1t", line=dict(color=CYAN, width=2.5)))
        fig.add_trace(go.Scatter(x=vf_data, y=strength_data["F1c"], name="F1c", line=dict(color=RED, width=2.5)))
        fig.add_vline(x=vf_current, line=dict(color=TEXT_MUTED, width=1, dash="dash"))
        fig.update_layout(**PLOTLY_LAYOUT, title="Resistencias Longitudinales vs Vf", xaxis_title="Vf", yaxis_title="Resistencia [MPa]")
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=vf_data, y=strength_data["F2t"], name="F2t", line=dict(color=GREEN, width=2.5)))
        fig2.add_trace(go.Scatter(x=vf_data, y=strength_data["F2c"], name="F2c", line=dict(color=ORANGE, width=2.5)))
        fig2.add_trace(go.Scatter(x=vf_data, y=strength_data["F12s"], name="F12s", line=dict(color=PURPLE, width=2.5)))
        fig2.add_vline(x=vf_current, line=dict(color=TEXT_MUTED, width=1, dash="dash"))
        fig2.update_layout(**PLOTLY_LAYOUT, title="Resistencias Transversales vs Vf", xaxis_title="Vf", yaxis_title="Resistencia [MPa]")
        st.plotly_chart(fig2, width="stretch")


def render_offaxis_chart(props: dict):
    """Tab 'Off-Axis': Ex(theta) + tabla de valores destacados."""
    thetas = np.arange(0, 91, 2)
    ex_vals = [offAxisStiffness(props["E1"], props["E2"], props["G12"], props["nu12"], t) for t in thetas]

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=thetas, y=ex_vals, name="Ex(θ)", line=dict(color=CYAN, width=2.5)))
        fig.add_trace(go.Scatter(
            x=[0, 15, 30, 45, 60, 75, 90],
            y=[offAxisStiffness(props["E1"], props["E2"], props["G12"], props["nu12"], t)
               for t in [0, 15, 30, 45, 60, 75, 90]],
            mode="markers",
            marker=dict(color=CYAN, size=7),
            name="Puntos destacados",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, title="Módulo Longitudinal Off-Axis Ex(θ)",
                          xaxis_title="θ (°)", yaxis_title="Ex (GPa)")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.markdown(f'''
        <div style="background:#111827; padding:10px; border:1px solid {BORDER_DIM}; border-radius:4px;">
            <div style="color:{TEXT_LABEL}; font-size:10px; margin-bottom:5px;">VALORES DESTACADOS</div>
            {''.join(f'<div style="display:flex; justify-content:space-between; font-family:{FONT_MONO}; font-size:11px; margin-bottom:2px;"><span style="color:{TEXT_PRIMARY};">θ={t}°</span><span style="color:{CYAN};">{offAxisStiffness(props["E1"], props["E2"], props["G12"], props["nu12"], t):.2f} GPa</span></div>' for t in [0, 15, 30, 45, 60, 75, 90])}
        </div>
        ''', unsafe_allow_html=True)


def render_envelope_chart(props: dict):
    """Tab 'Envolvente': Tsai-Wu failure envelope + panel de parametros."""
    f1t, f1c, f2t, f2c = props["F1t"], props["F1c"], props["F2t"], props["F2c"]
    f1 = 1 / f1t - 1 / f1c
    f2 = 1 / f2t - 1 / f2c
    f11 = 1 / (f1t * f1c)
    f22 = 1 / (f2t * f2c)
    f12 = -0.5 * np.sqrt(f11 * f22)

    pts = []
    for phi in np.linspace(0, 2 * np.pi, 360):
        c, s = np.cos(phi), np.sin(phi)
        a = f11 * c**2 + f22 * s**2 + 2 * f12 * c * s
        b = f1 * c + f2 * s
        disc = b**2 + 4 * a
        if disc >= 0 and a != 0:
            r = (-b + np.sqrt(disc)) / (2 * a)
            if 0 < r < 10000:
                pts.append((r * c, r * s))

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[p[0] for p in pts], y=[p[1] for p in pts],
                                 fill="toself", fillcolor="rgba(34,211,238,0.08)",
                                 line=dict(color=CYAN), name="Tsai-Wu"))
        fig.add_vline(x=0, line=dict(color=BORDER_DIM))
        fig.add_hline(y=0, line=dict(color=BORDER_DIM))
        fig.update_layout(**PLOTLY_LAYOUT, title="Envolvente de Fallo — Criterio Tsai-Wu",
                          xaxis_title="σ1 (MPa)", yaxis_title="σ2 (MPa)")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.markdown(f'''
        <div style="background:#111827; padding:10px; border:1px solid {BORDER_DIM}; border-radius:4px;">
            <div style="color:{TEXT_LABEL}; font-size:10px; margin-bottom:5px;">CRITERIO TSAI-WU</div>
            <div style="color:{TEXT_PRIMARY}; font-family:{FONT_MONO}; font-size:10px; margin-bottom:8px;">
                F1·σ1 + F2·σ2 + F11·σ1² + F22·σ2² + 2·F12·σ1·σ2 = 1
            </div>
            <div style="color:{TEXT_LABEL}; font-size:10px; margin-bottom:5px;">PARAMETROS</div>
            {''.join(f'<div style="display:flex; justify-content:space-between; font-family:{FONT_MONO}; font-size:11px; margin-bottom:2px;"><span style="color:{TEXT_PRIMARY};">{label}</span><span style="color:{CYAN};">{val:.1f} MPa</span></div>' for label, val in [("F1t", f1t), ("F1c", f1c), ("F2t", f2t), ("F2c", f2c)])}
        </div>
        ''', unsafe_allow_html=True)


def render_comparison_chart(matrix_props: dict, vf: float):
    """Tab 'Comparacion': modulos y F1t por fibra con la matriz/Vf actual."""
    data = []
    for name, f in FIBER_PRESETS.items():
        p = calcProps(f, matrix_props, vf)
        data.append({"name": name, "E1": p["E1"], "E2": p["E2"], "G12": p["G12"], "F1t": f["F1t"] * vf + matrix_props["Ft"] * (1 - vf)})

    df = pd.DataFrame(data)
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=df["name"], y=df["E1"], name="E1", marker_color=CYAN))
        fig.add_trace(go.Bar(x=df["name"], y=df["E2"], name="E2", marker_color=GREEN))
        fig.add_trace(go.Bar(x=df["name"], y=df["G12"], name="G12", marker_color=ORANGE))
        fig.update_layout(**PLOTLY_LAYOUT, title="Módulos Elásticos — Comparación de Fibras (Vf actual)", barmode="group",
                          yaxis_title="Módulo [GPa]")
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=df["name"], y=df["F1t"], name="F1t", marker_color=CYAN))
        fig2.update_layout(**PLOTLY_LAYOUT, title="Resistencia Longitudinal F1t — Comparación", yaxis_title="F1t [MPa]")
        st.plotly_chart(fig2, width="stretch")
