# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
# Implements: specs/06-seleccion-materiales.md
# Implements: specs/07-base-materiales.md
# Implements: specs/08-interfaz-vintage-unificada.md
"""Sidebar de entradas (100% Streamlit nativo) respaldado por la base SQLite."""

from __future__ import annotations

import streamlit as st

from core import material_db

DEFAULT_FIBER = "IM7"
DEFAULT_MATRIX = "Epoxi 8552"


# ---------------------------------------------------------------------------
# Lectura / selección de materiales
# ---------------------------------------------------------------------------

def _select(options: list[str], default: str, label: str, key: str) -> str:
    current = st.session_state.get(key)
    if current is not None and current in options:
        index = options.index(current)
    elif default in options:
        index = options.index(default)
    else:
        index = 0
    return st.selectbox(label, options, index=index, key=key, label_visibility="collapsed")


def _apply_pending_selection() -> None:
    """Aplica una selección pendiente antes de instanciar los widgets."""
    for kind, widget_key in (("fiber", "fiber_select"), ("matrix", "matrix_select")):
        pending = st.session_state.pop(f"_select_{kind}", None)
        if pending is not None:
            st.session_state[widget_key] = pending
    pending_vf = st.session_state.pop("_select_vf", None)
    if pending_vf is not None:
        st.session_state["vf_slider"] = pending_vf


def _set_preset(fiber_name: str, matrix_name: str, vf_val: float, seed_val: int | None = None) -> None:
    st.session_state["_select_fiber"] = fiber_name
    st.session_state["_select_matrix"] = matrix_name
    st.session_state["_select_vf"] = vf_val
    if seed_val is not None:
        st.session_state["rve_seed"] = seed_val


# ---------------------------------------------------------------------------
# Formularios de propiedades
# ---------------------------------------------------------------------------

def _fiber_fields(prefix: str, defaults: dict) -> dict[str, float]:
    return {
        "E1": st.number_input("E₁ (GPa)", value=float(defaults.get("E1", 0.0)), min_value=0.0, step=1.0, key=f"{prefix}_E1"),
        "E2": st.number_input("E₂ (GPa)", value=float(defaults.get("E2", 0.0)), min_value=0.0, step=0.5, key=f"{prefix}_E2"),
        "G12": st.number_input("G₁₂ (GPa)", value=float(defaults.get("G12", 0.0)), min_value=0.0, step=0.5, key=f"{prefix}_G12"),
        "nu12": st.number_input("ν₁₂", value=float(defaults.get("nu12", 0.0)), min_value=0.0, max_value=0.4999, step=0.01, format="%.3f", key=f"{prefix}_nu12"),
        "F1t": st.number_input("F₁ₜ (MPa)", value=float(defaults.get("F1t", 0.0)), min_value=0.0, step=10.0, key=f"{prefix}_F1t"),
        "etu": st.number_input("εₜᵤ", value=float(defaults.get("etu", 0.0)), min_value=0.0, max_value=1.0, step=0.0005, format="%.4f", key=f"{prefix}_etu"),
        "density": st.number_input("ρ (kg/m³)", value=float(defaults.get("density", 0.0)), min_value=0.0, step=10.0, key=f"{prefix}_density"),
        "d_min": st.number_input("d mín (µm)", value=float(defaults.get("d_min", 0.0)), min_value=0.0, step=0.5, key=f"{prefix}_d_min"),
        "d_max": st.number_input("d máx (µm)", value=float(defaults.get("d_max", 0.0)), min_value=0.0, step=0.5, key=f"{prefix}_d_max"),
    }


def _matrix_fields(prefix: str, defaults: dict) -> dict[str, float]:
    return {
        "E": st.number_input("Em (GPa)", value=float(defaults.get("E", 0.0)), min_value=0.0, step=0.1, key=f"{prefix}_E"),
        "nu": st.number_input("νm", value=float(defaults.get("nu", 0.0)), min_value=0.0, max_value=0.4999, step=0.01, format="%.3f", key=f"{prefix}_nu"),
        "G": st.number_input("Gm (GPa)", value=float(defaults.get("G", 0.0)), min_value=0.0, step=0.1, key=f"{prefix}_G"),
        "Ft": st.number_input("Fₘₜ (MPa)", value=float(defaults.get("Ft", 0.0)), min_value=0.0, step=1.0, key=f"{prefix}_Ft"),
        "density": st.number_input("ρ (kg/m³)", value=float(defaults.get("density", 0.0)), min_value=0.0, step=10.0, key=f"{prefix}_density"),
    }


# ---------------------------------------------------------------------------
# Gestión de la base de datos
# ---------------------------------------------------------------------------

def _manage_section(fiber: dict, matrix: dict) -> None:
    kind = st.radio("Tipo", ["Fibra", "Matriz"], horizontal=True, key="gestion_kind", label_visibility="collapsed")

    is_fiber = kind == "Fibra"
    table = "fiber" if is_fiber else "matrix"
    names = material_db.list_fibers() if is_fiber else material_db.list_matrices()
    current = fiber if is_fiber else matrix

    with st.form(f"form_new_{table}", clear_on_submit=True):
        name = st.text_input("Nuevo nombre")
        values = _fiber_fields(f"new_{table}", current) if is_fiber else _matrix_fields(f"new_{table}", current)
        submitted = st.form_submit_button("Guardar material", width="stretch")

    if submitted:
        clean = name.strip()
        if not clean:
            st.error("Ingrese un nombre.")
        else:
            if is_fiber:
                material_db.save_fiber(clean, values)
            else:
                material_db.save_matrix(clean, values)
            st.session_state[f"_select_{table}"] = clean
            st.rerun()

    if names:
        to_delete = st.selectbox("Eliminar", names, key=f"delete_{table}")
        if st.button("Eliminar material", key=f"button_delete_{table}", width="stretch"):
            if is_fiber:
                material_db.delete_fiber(to_delete)
            else:
                material_db.delete_matrix(to_delete)
            st.rerun()

    if st.button("Restaurar materiales de referencia", key="reset_db", width="stretch"):
        material_db.reset_db()
        st.rerun()


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------

def render_sidebar() -> tuple[dict, dict, float, str, str]:
    _apply_pending_selection()

    with st.sidebar:
        st.caption("CASOS DE REFERENCIA DEL CURSO")
        col_c1, col_c2 = st.columns(2)
        if col_c1.button("Carbono (IM7)", width="stretch", help="IM7/8552 CFRP: Vf = 0.60"):
            _set_preset("IM7", "Epoxi 8552", 0.60, 5)
            st.rerun()
        if col_c2.button("Vidrio (E-glass)", width="stretch", help="E-glass/Epoxi GFRP: Vf = 0.55"):
            _set_preset("E-glass", "Epoxi GFRP", 0.55, 143)
            st.rerun()

        st.divider()

        st.caption("FRACCIÓN DE VOLUMEN (Vf)")
        st.session_state.setdefault("vf_slider", 0.60)
        vf = st.slider("Vf", min_value=0.01, max_value=0.80, step=0.01,
                       format="%.2f", label_visibility="collapsed", key="vf_slider")
        st.caption(f"Vf = {vf:.0%} · Vm = {1 - vf:.2f}")

        st.divider()

        st.caption("CONSTITUYENTES")
        fibers = material_db.list_fibers()
        if fibers:
            fiber_name = _select(fibers, DEFAULT_FIBER, "Fibra", "fiber_select")
            fiber = material_db.get_fiber(fiber_name) or {}
        else:
            fiber_name = DEFAULT_FIBER
            fiber = {"E1": 276.0, "E2": 19.0, "G12": 27.0, "nu12": 0.20, "F1t": 5180.0, "etu": 0.0187, "density": 1780.0, "d_min": 5.0, "d_max": 7.0}
            st.warning("No hay fibras en la base de datos.")

        matrices = material_db.list_matrices()
        if matrices:
            matrix_name = _select(matrices, DEFAULT_MATRIX, "Matriz", "matrix_select")
            matrix = material_db.get_matrix(matrix_name) or {}
        else:
            matrix_name = DEFAULT_MATRIX
            matrix = {"E": 4.67, "nu": 0.36, "G": 1.72, "Ft": 121.0, "density": 1300.0}
            st.warning("No hay matrices en la base de datos.")

        st.divider()

        st.caption("MICROESTRUCTURA RVE (DIÁMETROS)")
        cd1, cd2 = st.columns(2)
        d_min_val = cd1.number_input(
            "d mín (µm)",
            value=float(fiber.get("d_min", 5.0)),
            min_value=0.1,
            max_value=100.0,
            step=0.5,
            key=f"dmin_{fiber_name}",
        )
        d_max_val = cd2.number_input(
            "d máx (µm)",
            value=float(fiber.get("d_max", 7.0)),
            min_value=0.1,
            max_value=100.0,
            step=0.5,
            key=f"dmax_{fiber_name}",
        )
        fiber["d_min"] = d_min_val
        fiber["d_max"] = d_max_val

        st.divider()

        with st.expander("⚙️ Parámetros avanzados y base de datos", expanded=False):
            st.caption("EDITAR PROPIEDADES DE FIBRA")
            fiber = _fiber_fields(f"fiber_{fiber_name}", fiber)
            fiber["d_min"], fiber["d_max"] = d_min_val, d_max_val
            if st.button("Guardar fibra", key="save_fiber", width="stretch"):
                if fiber_name in fibers:
                    material_db.save_fiber(fiber_name, fiber)
                    st.toast(f"Fibra «{fiber_name}» guardada.")

            st.divider()
            st.caption("EDITAR PROPIEDADES DE MATRIZ")
            matrix = _matrix_fields(f"matrix_{matrix_name}", matrix)
            if st.button("Guardar matriz", key="save_matrix", width="stretch"):
                if matrix_name in matrices:
                    material_db.save_matrix(matrix_name, matrix)
                    st.toast(f"Matriz «{matrix_name}» guardada.")

            st.divider()
            st.caption("GESTIONAR MATERIALES")
            _manage_section(fiber, matrix)

    return fiber, matrix, vf, fiber_name, matrix_name
