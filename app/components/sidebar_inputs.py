# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
"""Componente de sidebar para entradas de usuario."""

import streamlit as st

FIBER_PRESETS = {
    "Carbon T300": {"E1": 230, "E2": 15, "G12": 15, "nu12": 0.20, "F1t": 3500, "F1c": 2500, "F2t": 56, "F2c": 150, "F12s": 70},
    "E-Glass": {"E1": 73, "E2": 73, "G12": 30, "nu12": 0.22, "F1t": 2400, "F1c": 1200, "F2t": 2400, "F2c": 1200, "F12s": 500},
    "Kevlar 49": {"E1": 125, "E2": 8, "G12": 2.9, "nu12": 0.35, "F1t": 2800, "F1c": 480, "F2t": 30, "F2c": 138, "F12s": 43},
    "Boron": {"E1": 400, "E2": 400, "G12": 167, "nu12": 0.20, "F1t": 3500, "F1c": 3000, "F2t": 3500, "F2c": 3000, "F12s": 1200},
}

MATRIX_PRESETS = {
    "Epoxy 3501-6": {"E": 4.2, "nu": 0.35, "G": 1.56, "Ft": 69, "Fc": 250, "Fs": 50},
    "Polyester": {"E": 3.5, "nu": 0.38, "G": 1.27, "Ft": 55, "Fc": 140, "Fs": 40},
    "Aluminum 6061": {"E": 69, "nu": 0.33, "G": 26, "Ft": 310, "Fc": 310, "Fs": 200},
    "Titanium": {"E": 110, "nu": 0.34, "G": 41, "Ft": 900, "Fc": 900, "Fs": 550},
}

def render_sidebar() -> tuple[dict, dict, float, str, str]:
    with st.sidebar:
        st.markdown('<p style="color:#4a6080;font-size:10px;letter-spacing:0.1em;">FRACCIÓN DE VOLUMEN</p>', unsafe_allow_html=True)
        Vf = st.slider("Vf", min_value=0.01, max_value=0.80, value=0.60, step=0.01,
                       format="%.2f", label_visibility="collapsed")
        st.markdown(f'<p style="color:#22d3ee;font-size:11px;text-align:center;">Vf = {Vf:.0%} · Vm = {1-Vf:.2f}</p>',
                    unsafe_allow_html=True)

        st.markdown("---")

        st.markdown('<p style="color:#4a6080;font-size:10px;letter-spacing:0.1em;">PROPIEDADES DE FIBRA</p>', unsafe_allow_html=True)
        fiber_preset = st.selectbox("Fibra", list(FIBER_PRESETS.keys()), label_visibility="collapsed")
        fiber = dict(FIBER_PRESETS[fiber_preset])

        with st.expander("Editar propiedades de fibra", expanded=False):
            fiber["E1"] = st.number_input("E1 (GPa)", value=float(fiber["E1"]), step=1.0, key=f"f_E1_{fiber_preset}")
            fiber["E2"] = st.number_input("E2 (GPa)", value=float(fiber["E2"]), step=0.5, key=f"f_E2_{fiber_preset}")
            fiber["G12"] = st.number_input("G12 (GPa)", value=float(fiber["G12"]), step=0.5, key=f"f_G12_{fiber_preset}")
            fiber["nu12"] = st.number_input("nu12", value=float(fiber["nu12"]), step=0.01, key=f"f_nu12_{fiber_preset}")
            fiber["F1t"] = st.number_input("F1t (MPa)", value=float(fiber["F1t"]), step=10.0, key=f"f_F1t_{fiber_preset}")
            fiber["F1c"] = st.number_input("F1c (MPa)", value=float(fiber["F1c"]), step=10.0, key=f"f_F1c_{fiber_preset}")
            fiber["F2t"] = st.number_input("F2t (MPa)", value=float(fiber["F2t"]), step=1.0, key=f"f_F2t_{fiber_preset}")
            fiber["F2c"] = st.number_input("F2c (MPa)", value=float(fiber["F2c"]), step=1.0, key=f"f_F2c_{fiber_preset}")
            fiber["F12s"] = st.number_input("F12s (MPa)", value=float(fiber["F12s"]), step=1.0, key=f"f_F12s_{fiber_preset}")

        st.markdown("---")

        st.markdown('<p style="color:#4a6080;font-size:10px;letter-spacing:0.1em;">PROPIEDADES DE MATRIZ</p>', unsafe_allow_html=True)
        matrix_preset = st.selectbox("Matriz", list(MATRIX_PRESETS.keys()), label_visibility="collapsed")
        matrix = dict(MATRIX_PRESETS[matrix_preset])

        with st.expander("Editar propiedades de matriz", expanded=False):
            matrix["E"] = st.number_input("Em (GPa)", value=float(matrix["E"]), step=0.1, key=f"m_E_{matrix_preset}")
            matrix["nu"] = st.number_input("num", value=float(matrix["nu"]), step=0.01, key=f"m_nu_{matrix_preset}")
            matrix["G"] = st.number_input("Gm (GPa)", value=float(matrix["G"]), step=0.1, key=f"m_G_{matrix_preset}")
            matrix["Ft"] = st.number_input("Fmt (MPa)", value=float(matrix["Ft"]), step=1.0, key=f"m_Ft_{matrix_preset}")
            matrix["Fc"] = st.number_input("Fmc (MPa)", value=float(matrix["Fc"]), step=1.0, key=f"m_Fc_{matrix_preset}")
            matrix["Fs"] = st.number_input("Fms (MPa)", value=float(matrix["Fs"]), step=1.0, key=f"m_Fs_{matrix_preset}")

    return fiber, matrix, Vf, fiber_preset, matrix_preset
