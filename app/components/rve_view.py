# Implements: specs/10-rve.md
"""Pestaña RVE: visualización realista del Elemento de Volumen Representativo.

Se usa una celda periódica: las fibras cruzan los bordes y reaparecen por el
opuesto, y el área de fibra se cuenta una sola vez por fibra
(``Vf = Σ π r_i² / L²``). El Vf objetivo nunca se supera.
"""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

from core.rve import VF_MAX_PRACTICO, generar_rve, poligonos_periodicos
from components.charts import ACCENT, FONT, GRID, INK, PAPER

FIBER_COLOR = "#2a5d6b"
FIBER_EDGE = "#12333f"
MATRIX_COLOR = "#efe4c8"


@st.cache_data(show_spinner=False)
def _rve_cached(vf_objetivo: float, lado: float, d_min: float, d_max: float, seed: int):
    return generar_rve(vf_objetivo, lado, d_min, d_max, seed)


def _metric(column, label: str, value: str) -> None:
    with column:
        with st.container(border=True):
            st.caption(label)
            st.markdown(f"**{value}**")


def _next_rve_seed() -> None:
    st.session_state["rve_seed"] = int(st.session_state.get("rve_seed", 0)) + 1


def render_rve_tab(fiber: dict, matrix: dict, vf_objetivo: float) -> None:
    st.markdown(
        "El **RVE** (*Representative Volume Element*) es la región más pequeña que "
        "conserva las proporciones de fibra y matriz del compuesto. Aquí se modela como "
        "una **celda periódica**: las fibras pueden cruzar los bordes y reaparecen por el "
        "borde opuesto, de modo que la fracción volumétrica de fibra en 2D es exacta, "
        "$V_f = \\sum A_f / A_{rve}$."
    )

    d_min = float(fiber.get("d_min") or 5.0)
    d_max = float(fiber.get("d_max") or 7.0)
    if d_max <= 0.0:
        d_min, d_max = 5.0, 7.0

    control, realization, context = st.columns([1, 1, 2])
    lado = control.number_input("Lado del RVE (µm)", min_value=10.0, max_value=200.0,
                                value=50.0, step=5.0, key="rve_side")
    seed = realization.number_input(
        "Semilla",
        min_value=0,
        max_value=2_147_483_647,
        value=0,
        step=1,
        help=(
            "Controla la realización pseudoaleatoria. La misma semilla reproduce "
            "el mismo RVE; cambiarla genera otra distribución con los mismos parámetros."
        ),
        key="rve_seed",
    )
    realization.button(
        "Nueva realización",
        width="stretch",
        on_click=_next_rve_seed,
    )
    seed = int(seed)
    context.caption(
        f"Vf objetivo = {vf_objetivo:.0%} · diámetro = {d_min:.1f}–{d_max:.1f} µm · "
        f"semilla = {seed}"
    )

    solicitado = float(vf_objetivo)
    resultado = _rve_cached(min(solicitado, VF_MAX_PRACTICO), lado, d_min, d_max, seed)

    if solicitado > VF_MAX_PRACTICO:
        st.info(
            f"El Vf solicitado ({solicitado:.2f}) supera el máximo práctico; "
            f"se usó Vf = {VF_MAX_PRACTICO:.2f}."
        )
    if resultado.vf_objetivo + 1e-9 < min(solicitado, VF_MAX_PRACTICO):
        st.warning(
            f"No se alcanzó Vf = {min(solicitado, VF_MAX_PRACTICO):.3f}; "
            f"se logró el máximo factible Vf = {resultado.vf_objetivo:.3f} (sin superarlo)."
        )

    fila = st.columns(5)
    _metric(fila[0], "Vf objetivo", f"{min(solicitado, VF_MAX_PRACTICO):.3f}")
    _metric(fila[1], "Vf logrado", f"{resultado.vf_logrado:.4f}")
    _metric(fila[2], "Nº de fibras", f"{resultado.n_fibras}")
    _metric(fila[3], "Σ Af (µm²)", f"{resultado.area_fibras:.1f}")
    _metric(fila[4], "A_rve (µm²)", f"{resultado.lado ** 2:.0f}")

    xs, ys = poligonos_periodicos(resultado.centros, resultado.radios, resultado.lado)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines", fill="toself",
        fillcolor=FIBER_COLOR, line=dict(color=FIBER_EDGE, width=0.6),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_shape(type="rect", x0=0, y0=0, x1=resultado.lado, y1=resultado.lado,
                  line=dict(color=INK, width=1.6))
    fig.update_layout(
        paper_bgcolor=PAPER,
        plot_bgcolor=MATRIX_COLOR,
        font=dict(family=FONT, size=11, color=INK),
        xaxis=dict(range=[0, resultado.lado], title="x [µm]", gridcolor=GRID,
                   zeroline=False, constrain="domain"),
        yaxis=dict(range=[0, resultado.lado], title="y [µm]", gridcolor=GRID,
                   zeroline=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=56, r=20, t=44, b=48),
        height=540,
        showlegend=False,
        title="RVE periódico (condiciones de borde periódicas)",
    )
    st.plotly_chart(fig, width="stretch")

    st.caption(
        "Diámetro mínimo logrado: "
        f"{resultado.diametro_min:.2f} µm · máximo: {resultado.diametro_max:.2f} µm · "
        f"iteraciones de relajación: {resultado.iteraciones}. "
        "La semilla fija reproduce exactamente la misma realización; "
        "«Nueva realización» cambia la semilla para explorar otra distribución "
        "aleatoria con la misma fracción volumétrica objetivo. "
        "Fuente: Barbero (2011), *Introduction to Composite Materials Design*; "
        "lámina de VRE (U2, Clase 2)."
    )
