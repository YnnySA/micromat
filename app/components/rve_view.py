# Implements: specs/10-rve.md
"""Pestaña RVE: visualización realista del Elemento de Volumen Representativo.

Se usa una celda periódica: las fibras cruzan los bordes y reaparecen por el
opuesto, y el área de fibra se cuenta una sola vez por fibra
(Vf = suma(Af) / A_rve). El Vf objetivo nunca se supera.
"""

from __future__ import annotations

import math

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from core import material_db
from core.rve import VF_MAX_PRACTICO, RveResult, generar_rve, poligonos_periodicos
from components.charts import GRID, INK, PAPER, FONT

FIBER_COLOR = "#2a5d6b"
FIBER_EDGE = "#12333f"
MATRIX_COLOR = "#efe4c8"

# Criterio práctico de representatividad: lado del RVE >= 10 diámetros medios.
LD_MIN = 10.0
# Límites de empaquetamiento 2D de referencia (discos iguales).
VF_RSA = 0.547
VF_CUADRADO = math.pi / 4.0
VF_HEXAGONAL = math.pi / (2.0 * math.sqrt(3.0))

REFERENCE_CASES = {
    "Carbono IM7/8552": {"fiber": "IM7", "vf": 0.60, "seed": 5, "d": (5.0, 7.0)},
    "Vidrio E-glass/Epoxi": {"fiber": "E-glass", "vf": 0.55, "seed": 143, "d": (13.0, 17.0)},
}


@st.cache_data(show_spinner=False)
def _rve_cached(vf_objetivo: float, lado: float, d_min: float, d_max: float, seed: int):
    return generar_rve(vf_objetivo, lado, d_min, d_max, seed)


def _stats(res: RveResult) -> dict[str, float]:
    """Métricas geométricas usadas en la exposición."""
    c, r, lado = res.centros, res.radios, res.lado
    cortadas = int(np.sum(
        (c[:, 0] < r) | (c[:, 0] > lado - r) | (c[:, 1] < r) | (c[:, 1] > lado - r)
    ))
    if len(r) > 1:
        d = c[:, None, :] - c[None, :, :]
        d -= lado * np.round(d / lado)
        dist = np.hypot(d[..., 0], d[..., 1])
        np.fill_diagonal(dist, np.inf)
        gap = float(np.min(dist - (r[:, None] + r[None, :])))
    else:
        gap = float("nan")
    d_medio = float(2.0 * np.mean(r))
    return {
        "cortadas": cortadas,
        "completas": res.n_fibras - cortadas,
        "d_medio": d_medio,
        "gap": max(gap, 0.0),
        "ld": lado / d_medio,
    }


def _figure(res: RveResult, title: str, height: int = 540) -> go.Figure:
    xs, ys = poligonos_periodicos(res.centros, res.radios, res.lado)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=xs, y=ys, mode="lines", fill="toself",
        fillcolor=FIBER_COLOR, line=dict(color=FIBER_EDGE, width=0.6),
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=res.centros[:, 0], y=res.centros[:, 1], mode="markers",
        marker=dict(size=3, color=MATRIX_COLOR),
        hovertext=[f"Fibra {i + 1} · d = {2 * rr:.2f} µm" for i, rr in enumerate(res.radios)],
        hoverinfo="text", showlegend=False,
    ))
    fig.add_shape(type="rect", x0=0, y0=0, x1=res.lado, y1=res.lado,
                  line=dict(color=INK, width=1.6))
    fig.update_layout(
        paper_bgcolor=PAPER, plot_bgcolor=MATRIX_COLOR,
        font=dict(family=FONT, size=11, color=INK),
        xaxis=dict(range=[0, res.lado], title="x [µm]", gridcolor=GRID,
                   zeroline=False, constrain="domain"),
        yaxis=dict(range=[0, res.lado], title="y [µm]", gridcolor=GRID,
                   zeroline=False, scaleanchor="x", scaleratio=1),
        margin=dict(l=56, r=20, t=44, b=48), height=height,
        showlegend=False, title=title,
    )
    return fig


def _metric(column, label: str, value: str, help_text: str | None = None) -> None:
    with column:
        with st.container(border=True):
            st.caption(label, help=help_text)
            st.markdown(f"**{value}**")


def _next_rve_seed() -> None:
    st.session_state["rve_seed"] = int(st.session_state.get("rve_seed", 0)) + 1


def _render_comparison(lado: float) -> None:
    """Carbono vs vidrio en la misma ventana y a la misma escala."""
    cols = st.columns(2)
    for col, (name, case) in zip(cols, REFERENCE_CASES.items()):
        fiber = material_db.get_fiber(case["fiber"]) or {}
        d_min = float(fiber.get("d_min") or case["d"][0])
        d_max = float(fiber.get("d_max") or case["d"][1])
        res = _rve_cached(case["vf"], lado, d_min, d_max, case["seed"])
        s = _stats(res)
        with col:
            st.plotly_chart(_figure(res, f"{name} · Vf = {res.vf_logrado:.2f}", 430),
                            width="stretch", key=f"cmp_{case['fiber']}")
            st.markdown(
                f"**{res.n_fibras} fibras** · d = {d_min:.0f}–{d_max:.0f} µm · "
                f"L/d = {s['ld']:.1f}"
            )
    st.caption(
        "Misma fracción de volumen aproximada, distinta escala: con fibras más gruesas "
        "caben muchas menos en la misma ventana, y la muestra pierde representatividad."
    )


def render_rve_tab(fiber: dict, matrix: dict, vf_objetivo: float) -> None:
    st.markdown(
        "El **RVE** (Elemento de Volumen Representativo) es la ventana más pequeña de la "
        "sección transversal que conserva la proporción fibra/matriz del compuesto. Se modela "
        "como **celda periódica**: una fibra que sale por un borde reaparece por el opuesto, "
        "así Vf = suma(Af) / A_rve es exacta."
    )

    d_min = float(fiber.get("d_min") or 5.0)
    d_max = float(fiber.get("d_max") or 7.0)
    if d_max <= 0.0:
        d_min, d_max = 5.0, 7.0
    d_medio = 0.5 * (d_min + d_max)

    vista = st.radio(
        "Vista",
        ["RVE del material seleccionado", "Comparar carbono vs vidrio"],
        horizontal=True, label_visibility="collapsed", key="rve_vista",
    )

    c_side, c_seed, c_info = st.columns([1, 1, 2])
    lado_rec = float(math.ceil(LD_MIN * d_medio / 10.0) * 10.0)
    modo = c_side.radio(
        "Ventana",
        ["50 µm (pauta)", f"Representativa ({lado_rec:.0f} µm)"],
        key="rve_modo",
        help=f"Representativa: lado ≥ {LD_MIN:.0f} diámetros medios de fibra.",
    )
    lado = 50.0 if modo.startswith("50") else lado_rec

    if vista.startswith("Comparar"):
        _render_comparison(lado)
        return

    st.session_state.setdefault("rve_seed", 5)
    seed = c_seed.number_input(
        "Semilla", min_value=0, max_value=2_147_483_647, step=1, key="rve_seed",
        help="Fija la realización aleatoria: misma semilla, mismo RVE.",
    )
    c_seed.button("Nueva realización", width="stretch", on_click=_next_rve_seed)
    seed = int(seed)

    solicitado = float(vf_objetivo)
    objetivo = min(solicitado, VF_MAX_PRACTICO)
    res = _rve_cached(objetivo, lado, d_min, d_max, seed)
    s = _stats(res)

    n_teorico = objetivo * lado**2 / (math.pi * d_medio**2 / 4.0)
    c_info.markdown(
        f"**¿Cuántas fibras caben?**  \n"
        f"n ≈ Vf · L² / (π · d² / 4) = {objetivo:.2f} · {lado:.0f}² / "
        f"(π · {d_medio:.1f}² / 4) ≈ **{n_teorico:.0f} fibras**  \n"
        f"Generadas: **{res.n_fibras}** (la diferencia viene de la dispersión de diámetros)."
    )

    if solicitado > VF_MAX_PRACTICO:
        st.info(f"Vf = {solicitado:.2f} supera el máximo práctico; se usó {VF_MAX_PRACTICO:.2f}.")
    if res.vf_objetivo + 1e-9 < objetivo:
        st.warning(f"No se alcanzó Vf = {objetivo:.3f}; máximo factible {res.vf_objetivo:.3f}.")

    fila = st.columns(6)
    _metric(fila[0], "Nº de fibras", f"{res.n_fibras}",
            "Cada fibra se cuenta una sola vez, aunque cruce el borde.")
    _metric(fila[1], "Completas / cortadas", f"{s['completas']} / {s['cortadas']}",
            "Cortadas: cruzan el borde y reaparecen por el lado opuesto.")
    _metric(fila[2], "Vf logrado", f"{res.vf_logrado:.3f}")
    _metric(fila[3], "Diámetro medio", f"{s['d_medio']:.2f} µm")
    _metric(fila[4], "Separación mínima", f"{s['gap']:.2f} µm",
            "Menor distancia superficie a superficie entre dos fibras (sin solapes).")
    _metric(fila[5], "L / d", f"{s['ld']:.1f}",
            f"Criterio práctico de representatividad: L/d ≥ {LD_MIN:.0f}.")

    if s["ld"] < LD_MIN:
        st.warning(
            f"Con L = {lado:.0f} µm y d ≈ {d_medio:.0f} µm la ventana contiene solo "
            f"{res.n_fibras} fibras (L/d = {s['ld']:.1f}). Es poco representativa: una fibra "
            f"más o menos cambia mucho el Vf local. Use la ventana representativa."
        )

    st.plotly_chart(
        _figure(res, f"RVE periódico · {lado:.0f} × {lado:.0f} µm · {res.n_fibras} fibras"),
        width="stretch",
    )

    with st.expander("Límites de empaquetamiento y detalles del algoritmo", expanded=False):
        st.markdown(
            f"- Aleatorio secuencial (RSA): se atasca cerca de Vf ≈ {VF_RSA:.3f}.\n"
            f"- Arreglo cuadrado ideal: Vf máx = π/4 ≈ {VF_CUADRADO:.3f}.\n"
            f"- Arreglo hexagonal ideal: Vf máx = π/(2√3) ≈ {VF_HEXAGONAL:.3f}.\n"
            f"- Aquí se usa compresión con relajación periódica, que supera el límite RSA "
            f"y llega a Vf ≈ 0.60 sin solapes (tolerancia 0.01 µm). Tope práctico: "
            f"{VF_MAX_PRACTICO:.2f}."
        )
        st.caption(
            f"Diámetros logrados: {res.diametro_min:.2f}–{res.diametro_max:.2f} µm · "
            f"iteraciones de relajación: {res.iteraciones} · semilla {seed}. "
            "Fuente: Barbero (2011); lámina de VRE (U2, Clase 2)."
        )
