# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md (Section 8)
# Implements: specs/08-interfaz-vintage-unificada.md
"""Gráficos Plotly nativos: tema claro, líneas delgadas y etiquetas Unicode.

Streamlit no carga MathJax, que es lo que Plotly necesita para renderizar LaTeX
delimitado por signos de dólar. Por eso las etiquetas usan notación Unicode
(E₁, ν₁₂, σ₁, …), que Plotly dibuja de forma nativa y sin dependencias de red.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core.calculations import elastic_from_props, offAxisStiffness, strength_from_props
from core import material_db

# Paleta reducida y clara (papel sepia, tinta, un acento y apoyos apagados)
PAPER = "#f4ecd8"
INK = "#3d3428"
GRID = "#d8ccae"
ACCENT = "#1f6f6b"
OCHRE = "#b07d2b"
OLIVE = "#5c6b3c"
RUST = "#a04b3a"
VIOLET = "#6b5b95"
FONT = "Consolas, 'Courier New', monospace"
LINE_WIDTH = 1.3

# Etiquetas libres de MathJax (se exportan para las pruebas de contrato).
LABELS = (
    "E₁", "E₂", "G₁₂", "ν₁₂",
    "F₁ₜ", "F₁c", "F₂ₜ", "F₂c", "F₆",
    "Vf", "θ", "σ₁", "σ₂", "Ex",
)

PLOTLY_LAYOUT = dict(
    paper_bgcolor=PAPER,
    plot_bgcolor=PAPER,
    font=dict(family=FONT, size=11, color=INK),
    xaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID),
    yaxis=dict(gridcolor=GRID, linecolor=GRID, zerolinecolor=GRID),
    legend=dict(bgcolor=PAPER, bordercolor=GRID, borderwidth=1),
    margin=dict(l=64, r=20, t=48, b=48),
    height=380,
)

VF_SWEEP: tuple[float, ...] = tuple(round(v, 2) for v in np.arange(0.05, 0.801, 0.01))


@st.cache_data(show_spinner=False)
def _elastic_sweep(fiber: dict, matrix: dict, vfs: tuple[float, ...]) -> dict[str, list[float]]:
    series = {"E1": [], "E2": [], "G12": [], "nu12": []}
    for vf in vfs:
        elastic = elastic_from_props(fiber, matrix, vf)
        for key in series:
            series[key].append(elastic[key])
    return series


@st.cache_data(show_spinner=False)
def _strength_sweep(fiber: dict, matrix: dict, vfs: tuple[float, ...]) -> dict[str, list[float]]:
    series = {"F1t": [], "F1c": [], "F2t": [], "F2c": [], "F6": []}
    for vf in vfs:
        strength = strength_from_props(fiber, matrix, vf)
        for key in series:
            series[key].append(strength[key])
    return series


def _reference_line(fig: go.Figure, vf_current: float) -> None:
    fig.add_vline(x=vf_current, line=dict(color=INK, width=1, dash="dash"))


# ---------------------------------------------------------------------------
# Pestaña: Módulos Elásticos
# ---------------------------------------------------------------------------

def render_elastic_chart(fiber: dict, matrix: dict, vf_current: float) -> None:
    sweep = _elastic_sweep(fiber, matrix, VF_SWEEP)
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["E1"], name="E₁", line=dict(color=ACCENT, width=LINE_WIDTH)))
        fig.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["E2"], name="E₂", line=dict(color=OCHRE, width=LINE_WIDTH)))
        fig.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["G12"], name="G₁₂", line=dict(color=OLIVE, width=LINE_WIDTH)))
        _reference_line(fig, vf_current)
        fig.update_layout(**PLOTLY_LAYOUT, title="Módulos vs fracción de volumen",
                          xaxis_title="Vf [-]", yaxis_title="E [GPa]")
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["nu12"], name="ν₁₂", line=dict(color=VIOLET, width=LINE_WIDTH)))
        _reference_line(fig2, vf_current)
        fig2.update_layout(**PLOTLY_LAYOUT, title="Coeficiente de Poisson ν₁₂ vs Vf",
                           xaxis_title="Vf [-]", yaxis_title="ν₁₂ [-]")
        st.plotly_chart(fig2, width="stretch")


# ---------------------------------------------------------------------------
# Pestaña: Resistencias
# ---------------------------------------------------------------------------

def render_strength_chart(fiber: dict, matrix: dict, vf_current: float) -> None:
    sweep = _strength_sweep(fiber, matrix, VF_SWEEP)
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["F1t"], name="F₁ₜ", line=dict(color=ACCENT, width=LINE_WIDTH)))
        fig.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["F1c"], name="F₁c", line=dict(color=RUST, width=LINE_WIDTH)))
        _reference_line(fig, vf_current)
        fig.update_layout(**PLOTLY_LAYOUT, title="Resistencias longitudinales vs Vf",
                          xaxis_title="Vf [-]", yaxis_title="F [MPa]")
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["F2t"], name="F₂ₜ", line=dict(color=OLIVE, width=LINE_WIDTH)))
        fig2.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["F2c"], name="F₂c", line=dict(color=OCHRE, width=LINE_WIDTH)))
        fig2.add_trace(go.Scatter(x=VF_SWEEP, y=sweep["F6"], name="F₆", line=dict(color=VIOLET, width=LINE_WIDTH)))
        _reference_line(fig2, vf_current)
        fig2.update_layout(**PLOTLY_LAYOUT, title="Resistencias transversales y cortante vs Vf",
                           xaxis_title="Vf [-]", yaxis_title="F [MPa]")
        st.plotly_chart(fig2, width="stretch")


# ---------------------------------------------------------------------------
# Pestaña: Off-Axis
# ---------------------------------------------------------------------------

def render_offaxis_chart(props: dict) -> None:
    thetas = tuple(range(0, 91, 2))
    ex_values = [offAxisStiffness(props["E1"], props["E2"], props["G12"], props["nu12"], t) for t in thetas]

    col1, col2 = st.columns([2, 1])
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=thetas, y=ex_values, name="Ex(θ)", line=dict(color=ACCENT, width=LINE_WIDTH)))
        marks = (0, 15, 30, 45, 60, 75, 90)
        fig.add_trace(go.Scatter(
            x=marks,
            y=[offAxisStiffness(props["E1"], props["E2"], props["G12"], props["nu12"], t) for t in marks],
            mode="markers",
            marker=dict(color=ACCENT, size=6),
            name="Puntos destacados",
        ))
        fig.update_layout(**PLOTLY_LAYOUT, title="Módulo off-axis Ex(θ)",
                          xaxis_title="θ (°)", yaxis_title="Ex [GPa]")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.caption("VALORES DESTACADOS")
        table = pd.DataFrame({
            "θ (°)": list(marks),
            "Ex (GPa)": [round(offAxisStiffness(props["E1"], props["E2"], props["G12"], props["nu12"], t), 2) for t in marks],
        })
        st.dataframe(table, hide_index=True)


# ---------------------------------------------------------------------------
# Pestaña: Envolvente Tsai-Wu
# ---------------------------------------------------------------------------

def render_envelope_chart(props: dict) -> None:
    f1t, f1c, f2t, f2c = props["F1t"], props["F1c"], props["F2t"], props["F2c"]
    f1 = 1 / f1t - 1 / f1c
    f2 = 1 / f2t - 1 / f2c
    f11 = 1 / (f1t * f1c)
    f22 = 1 / (f2t * f2c)
    f12 = -0.5 * np.sqrt(f11 * f22)

    points = []
    for phi in np.linspace(0, 2 * np.pi, 360):
        c, s = np.cos(phi), np.sin(phi)
        a = f11 * c**2 + f22 * s**2 + 2 * f12 * c * s
        b = f1 * c + f2 * s
        disc = b**2 + 4 * a
        if disc >= 0 and a != 0:
            r = (-b + np.sqrt(disc)) / (2 * a)
            if 0 < r < 10000:
                points.append((r * c, r * s))

    col1, col2 = st.columns([2, 1])

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[p[0] for p in points], y=[p[1] for p in points],
            fill="toself", fillcolor="rgba(31,111,107,0.10)",
            line=dict(color=ACCENT, width=LINE_WIDTH), name="Tsai-Wu",
        ))
        fig.add_vline(x=0, line=dict(color=GRID, width=1))
        fig.add_hline(y=0, line=dict(color=GRID, width=1))
        fig.update_layout(**PLOTLY_LAYOUT, title="Envolvente de fallo — criterio Tsai-Wu",
                          xaxis_title="σ₁ (MPa)", yaxis_title="σ₂ (MPa)")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.caption("CRITERIO TSAI-WU")
        st.markdown("F₁σ₁ + F₂σ₂ + F₁₁σ₁² + F₂₂σ₂² + 2F₁₂σ₁σ₂ = 1")
        st.caption("PARÁMETROS")
        params = pd.DataFrame({
            "Propiedad": ["F₁ₜ", "F₁c", "F₂ₜ", "F₂c"],
            "Valor (MPa)": [round(f1t, 1), round(f1c, 1), round(f2t, 1), round(f2c, 1)],
        })
        st.dataframe(params, hide_index=True)


# ---------------------------------------------------------------------------
# Pestaña: Comparación
# ---------------------------------------------------------------------------

def render_comparison_chart(matrix: dict, vf_current: float) -> None:
    rows = []
    for name in material_db.list_fibers():
        fiber = material_db.get_fiber(name)
        if not fiber:
            continue
        elastic = elastic_from_props(fiber, matrix, vf_current)
        strength = strength_from_props(fiber, matrix, vf_current)
        rows.append({
            "Fibra": name,
            "E1 (GPa)": round(elastic["E1"], 1),
            "E2 (GPa)": round(elastic["E2"], 1),
            "G12 (GPa)": round(elastic["G12"], 1),
            "F1t (MPa)": round(strength["F1t"], 1),
        })

    dataframe = pd.DataFrame(rows)
    if dataframe.empty:
        st.info("Agregue fibras a la base de datos para comparar.")
        return

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Bar(x=dataframe["Fibra"], y=dataframe["E1 (GPa)"], name="E₁", marker_color=ACCENT))
        fig.add_trace(go.Bar(x=dataframe["Fibra"], y=dataframe["E2 (GPa)"], name="E₂", marker_color=OCHRE))
        fig.add_trace(go.Bar(x=dataframe["Fibra"], y=dataframe["G12 (GPa)"], name="G₁₂", marker_color=OLIVE))
        fig.update_layout(**PLOTLY_LAYOUT, title="Módulos elásticos — comparación de fibras", barmode="group",
                          yaxis_title="E [GPa]")
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(x=dataframe["Fibra"], y=dataframe["F1t (MPa)"], name="F₁ₜ", marker_color=RUST))
        fig2.update_layout(**PLOTLY_LAYOUT, title="Resistencia longitudinal F₁ₜ", yaxis_title="F₁ₜ [MPa]")
        st.plotly_chart(fig2, width="stretch")
