# Implements: specs/04-estudio-parametrico.md
"""Componentes de visualización para el análisis paramétrico utilizando Plotly."""

from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from core.calculations import MATERIALS, parametric_sweep

@st.cache_data
def plot_e1_e2(vf_min: float, vf_max: float) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Módulo Longitudinal E1", "Módulo Transversal E2"))
    
    sweep_im7 = parametric_sweep(MATERIALS["IM7/8552 (CFRP)"], vf_min, vf_max)
    sweep_eg = parametric_sweep(MATERIALS["E-glass/Epoxi (GFRP)"], vf_min, vf_max)
    
    # Panel 1: E1 vs Vf
    fig.add_trace(go.Scatter(x=sweep_im7["vf"], y=sweep_im7["e1"], name="E1 IM7/8552 (ROM)", line=dict(color="#2C3E50", width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=sweep_eg["vf"], y=sweep_eg["e1"], name="E1 E-glass/Epoxi (ROM)", line=dict(color="#1A5276", width=2.5, dash="dash")), row=1, col=1)
    
    # Panel 2: E2 vs Vf
    fig.add_trace(go.Scatter(x=sweep_im7["vf"], y=sweep_im7["e2_rom"], name="E2 IM7/8552 (ROM)", line=dict(color="#34495E", width=1.5, dash="dot")), row=1, col=2)
    fig.add_trace(go.Scatter(x=sweep_im7["vf"], y=sweep_im7["e2"], name="E2 IM7/8552 (Halpin-Tsai)", line=dict(color="#2C3E50", width=2.5)), row=1, col=2)
    fig.add_trace(go.Scatter(x=sweep_eg["vf"], y=sweep_eg["e2_rom"], name="E2 E-glass/Epoxi (ROM)", line=dict(color="#2980B9", width=1.5, dash="dot")), row=1, col=2)
    fig.add_trace(go.Scatter(x=sweep_eg["vf"], y=sweep_eg["e2"], name="E2 E-glass/Epoxi (Halpin-Tsai)", line=dict(color="#1A5276", width=2.5, dash="dash")), row=1, col=2)
    
    # Líneas de referencia
    for col in (1, 2):
        fig.add_vline(x=0.60, line=dict(color="#2C3E50", width=1, dash="dash"), row=1, col=col)
        fig.add_vline(x=0.55, line=dict(color="#1A5276", width=1, dash="dash"), row=1, col=col)
        
    fig.update_xaxes(title_text="Vf [-]", gridcolor="rgba(0,0,0,0.1)")
    fig.update_yaxes(title_text="Módulo [GPa]", gridcolor="rgba(0,0,0,0.1)")
    
    fig.update_layout(
        title="Módulos Elásticos vs Fracción Volumétrica de Fibra (Vf)",
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        height=500
    )
    return fig

@st.cache_data
def plot_g12_nu12(vf_min: float, vf_max: float) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, subplot_titles=("Módulo de Corte G12", "Coeficiente de Poisson ν12"))
    
    sweep_im7 = parametric_sweep(MATERIALS["IM7/8552 (CFRP)"], vf_min, vf_max)
    sweep_eg = parametric_sweep(MATERIALS["E-glass/Epoxi (GFRP)"], vf_min, vf_max)
    
    # Panel 1: G12
    fig.add_trace(go.Scatter(x=sweep_im7["vf"], y=sweep_im7["g12"], name="G12 IM7/8552 (Halpin-Tsai)", line=dict(color="#2C3E50", width=2.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=sweep_eg["vf"], y=sweep_eg["g12"], name="G12 E-glass/Epoxi (Halpin-Tsai)", line=dict(color="#1A5276", width=2.5, dash="dash")), row=1, col=1)
    
    # Panel 2: nu12
    fig.add_trace(go.Scatter(x=sweep_im7["vf"], y=sweep_im7["nu12"], name="ν12 IM7/8552 (ROM)", line=dict(color="#2C3E50", width=2.5)), row=1, col=2)
    fig.add_trace(go.Scatter(x=sweep_eg["vf"], y=sweep_eg["nu12"], name="ν12 E-glass/Epoxi (ROM)", line=dict(color="#1A5276", width=2.5, dash="dash")), row=1, col=2)
    
    # Líneas de referencia
    for col in (1, 2):
        fig.add_vline(x=0.60, line=dict(color="#2C3E50", width=1, dash="dash"), row=1, col=col)
        fig.add_vline(x=0.55, line=dict(color="#1A5276", width=1, dash="dash"), row=1, col=col)
        
    fig.update_xaxes(title_text="Vf [-]", gridcolor="rgba(0,0,0,0.1)")
    fig.update_yaxes(row=1, col=1, title_text="G12 [GPa]", gridcolor="rgba(0,0,0,0.1)")
    fig.update_yaxes(row=1, col=2, title_text="ν12 [-]", gridcolor="rgba(0,0,0,0.1)")
    
    fig.update_layout(
        title="G12 y ν12 vs Fracción Volumétrica de Fibra (Vf)",
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        height=500
    )
    return fig

@st.cache_data
def plot_strength_im7(vf_min: float, vf_max: float) -> go.Figure:
    fig = go.Figure()
    
    sweep_im7 = parametric_sweep(MATERIALS["IM7/8552 (CFRP)"], vf_min, vf_max)
    
    fig.add_trace(go.Scatter(x=sweep_im7["vf"], y=sweep_im7["f1t"], name="F1t (ROM, Dominancia Fibra)", line=dict(color="#27AE60", width=2.5)))
    fig.add_trace(go.Scatter(x=sweep_im7["vf"], y=sweep_im7["f1c"], name="F1c Práctico (0.575 x F1t)", line=dict(color="#C0392B", width=2.5, dash="dash")))
    
    fig.add_vline(x=0.60, line=dict(color="#2C3E50", width=1.2, dash="dot"))
    
    fig.update_xaxes(title_text="Vf [-]", gridcolor="rgba(0,0,0,0.1)")
    fig.update_yaxes(title_text="Resistencia [MPa]", gridcolor="rgba(0,0,0,0.1)")
    
    fig.update_layout(
        title="Resistencias Longitudes F1t y F1c vs Vf (IM7/8552 CFRP)",
        plot_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        height=450
    )
    return fig

