# Implements: specs/01-visualizacion-resultados.md
"""Componentes tabulares para la vista de resultados."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.models import ElasticProperties, StrengthProperties, ValidationRow


def elastic_dataframe(properties: ElasticProperties) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"Propiedad": "E1", "Valor": properties.e1_gpa, "Unidad": "GPa", "Modelo": "ROM"},
            {"Propiedad": "E2", "Valor": properties.e2_gpa, "Unidad": "GPa", "Modelo": "Halpin-Tsai"},
            {"Propiedad": "G12", "Valor": properties.g12_gpa, "Unidad": "GPa", "Modelo": "Halpin-Tsai"},
            {"Propiedad": "nu12", "Valor": properties.nu12, "Unidad": "Adimensional", "Modelo": "ROM"},
            {"Propiedad": "nu21", "Valor": properties.nu21, "Unidad": "Adimensional", "Modelo": "Reciprocidad"},
        ]
    )


def strength_dataframe(properties: StrengthProperties) -> pd.DataFrame:
    rows = []
    for name, property_value in (
        ("F1t", properties.f1t),
        ("F1c", properties.f1c),
        ("F2t", properties.f2t),
        ("F2c", properties.f2c),
        ("F6", properties.f6),
    ):
        rows.append(
            {
                "Propiedad": name,
                "Valor": property_value.value_mpa,
                "Unidad": "MPa",
                "Modelo": property_value.model,
                "Confiabilidad": property_value.reliability,
            }
        )
    return pd.DataFrame(rows)


def validation_dataframe(rows: list[ValidationRow]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Propiedad": row.property_name,
                "Calculado": row.predicted,
                "Experimental": row.experimental,
                "Error %": row.error_percent,
                "Unidad": row.unit,
                "Modelo": row.model,
            }
            for row in rows
        ]
    )


def _highlight_validation(row: pd.Series) -> list[str]:
    color = "background-color: #ffd6d6; color: #7f1d1d" if row["_highlight"] else ""
    return [color] * len(row)


def render_elastic_table(properties: ElasticProperties) -> None:
    st.dataframe(
        elastic_dataframe(properties),
        hide_index=True,
        column_config={
            "Valor": st.column_config.NumberColumn("Valor", format="%.4f"),
        },
    )


def render_strength_table(properties: StrengthProperties) -> None:
    st.dataframe(
        strength_dataframe(properties),
        hide_index=True,
        column_config={
            "Valor": st.column_config.NumberColumn("Valor", format="%.1f"),
        },
    )


def render_validation_table(rows: list[ValidationRow]) -> None:
    dataframe = validation_dataframe(rows)
    st.dataframe(
        dataframe,
        hide_index=True,
        column_config={
            "Calculado": st.column_config.NumberColumn("Calculado", format="%.3f"),
            "Experimental": st.column_config.NumberColumn("Experimental", format="%.3f"),
            "Error %": st.column_config.NumberColumn("Error %", format="%.2f%%"),
        },
    )


def render_validation_editor(
    rows: list[ValidationRow],
    key: str,
) -> pd.DataFrame:
    """Permite editar referencias experimentales con navegación por celdas."""
    dataframe = validation_dataframe(rows)
    edited = st.data_editor(
        dataframe,
        hide_index=True,
        width="stretch",
        key=key,
        disabled=["Propiedad", "Calculado", "Error %", "Unidad", "Modelo"],
        column_config={
            "Calculado": st.column_config.NumberColumn("Calculado", format="%.3f"),
            "Experimental": st.column_config.NumberColumn(
                "Experimental",
                format="%.3f",
                help="Valor de referencia experimental editable.",
            ),
            "Error %": st.column_config.NumberColumn("Error %", format="%.2f%%"),
        },
    )
    return edited
