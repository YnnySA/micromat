# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
# Implements: specs/08-interfaz-vintage-unificada.md
"""Tarjetas de resultados nativas (Streamlit puro, sin HTML ni CSS).

Se usa `st.container(border=True)` con `st.caption` + `st.markdown` en lugar de
`st.metric`, cuyo valor (~2 rem) se truncaba en 5 columnas.
"""

import streamlit as st


def render_result_cards(props: dict) -> None:
    """Dos filas de 5 tarjetas: módulos elásticos y resistencias."""
    elastic = [
        ("E₁", props["E1"], "GPa", 2),
        ("E₂", props["E2"], "GPa", 2),
        ("G₁₂", props["G12"], "GPa", 2),
        ("ν₁₂", props["nu12"], "", 4),
        ("ν₂₁", props["nu21"], "", 4),
    ]
    for column, (label, value, unit, decimals) in zip(st.columns(5), elastic):
        _card(column, label, value, unit, decimals)

    strength = [
        ("F₁ₜ", props["F1t"], "MPa", 1),
        ("F₁c", props["F1c"], "MPa", 1),
        ("F₂ₜ", props["F2t"], "MPa", 1),
        ("F₂c", props["F2c"], "MPa", 1),
        ("F₆", props["F6"], "MPa", 1),
    ]
    for column, (label, value, unit, decimals) in zip(st.columns(5), strength):
        _card(column, label, value, unit, decimals)


def _card(column, label: str, value: float, unit: str, decimals: int) -> None:
    heading = f"{label} ({unit})" if unit else label
    with column:
        with st.container(border=True):
            st.caption(heading)
            st.markdown(f"**{value:.{decimals}f}**")
