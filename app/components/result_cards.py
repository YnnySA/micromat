# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
# Implements: specs/08-interfaz-vintage-unificada.md
"""Tarjetas de resultados nativas (Streamlit puro, sin HTML ni CSS).

Se usa `st.container(border=True)` con `st.caption` + `st.markdown` en lugar de
`st.metric`, cuyo valor (~2 rem) se truncaba en 5 columnas.
"""

import streamlit as st


def render_result_cards(props: dict) -> None:
    """Dos filas de 5 tarjetas con el modelo usado en cada propiedad."""
    st.caption("PROPIEDADES ELÁSTICAS — modelo de cálculo")
    elastic = [
        ("E₁", props["E1"], "GPa", 2, "ROM"),
        ("E₂", props["E2"], "GPa", 2, "Halpin-Tsai (ξ=2)"),
        ("G₁₂", props["G12"], "GPa", 2, "Halpin-Tsai (ξ=1)"),
        ("ν₁₂", props["nu12"], "", 4, "ROM"),
        ("ν₂₁", props["nu21"], "", 4, "Reciprocidad"),
    ]
    for column, (label, value, unit, decimals, model) in zip(st.columns(5), elastic):
        _card(column, label, value, unit, decimals, model)

    st.caption("RESISTENCIAS — modelo de cálculo")
    strength = [
        ("F₁ₜ", props["F1t"], "MPa", 1, "ROM · dominancia de fibra"),
        ("F₁c", props["F1c"], "MPa", 1, "Estimación práctica · 0.575 × F₁ₜ"),
        ("F₂ₜ", props["F2t"], "MPa", 1, "Barbero"),
        ("F₂c", props["F2c"], "MPa", 1, "Estimación empírica · 4.0 × F₂ₜ"),
        ("F₆", props["F6"], "MPa", 1, "Barbero"),
    ]
    for column, (label, value, unit, decimals, model) in zip(st.columns(5), strength):
        _card(column, label, value, unit, decimals, model)


def _card(
    column,
    label: str,
    value: float,
    unit: str,
    decimals: int,
    model: str,
) -> None:
    heading = f"{label} ({unit})" if unit else label
    with column:
        with st.container(border=True):
            st.caption(heading)
            st.caption(model)
            st.markdown(f"**{value:.{decimals}f}**")
