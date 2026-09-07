# Implements: specs/01-visualizacion-resultados.md
"""Visualización determinista del RVE RSA asociado al sistema seleccionado."""

from __future__ import annotations

import streamlit as st

from core.models import MaterialSystem


def _rve_svg(material: MaterialSystem) -> str:
    rve = material.rve
    radius = 2.0 if "IM7" in material.name else 5.0
    circles = []
    for index in range(int(rve["fibers"])):
        x = 5 + ((index * 17) % 90)
        y = 5 + ((index * 29 + 11) % 90)
        circles.append(
            f'<circle cx="{x}" cy="{y}" r="{radius}" fill="#2C3E50" '
            'stroke="#111827" stroke-width="0.25"/>'
        )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" '
        'role="img" aria-label="RVE generado por RSA">'
        '<rect width="100" height="100" fill="#F8FAFC" stroke="#111827"/>'
        + "".join(circles)
        + "</svg>"
    )


def render_rve(material: MaterialSystem) -> None:
    rve = material.rve
    st.image(_rve_svg(material), caption=f"RVE RSA — {material.name}", width="stretch")
    columns = st.columns(3)
    columns[0].metric("Fibras colocadas", int(rve["fibers"]))
    columns[1].metric("Vf logrado / objetivo", f'{rve["vf_achieved"]:.3f} / {rve["vf_target"]:.2f}')
    columns[2].metric("Intentos", int(rve["attempts"]))
