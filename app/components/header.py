# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
"""Componente de cabecera para la aplicación."""

import streamlit as st

def render_header(fiber_name: str, matrix_name: str, Vf: float):
    st.markdown(f'''
    <div style="
      background: #0d1427;
      border-bottom: 1px solid #1e3a5f;
      padding: 12px 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    ">
      <div style="display:flex; align-items:center; gap:16px;">
        <span style="color:#22d3ee; font-size:13px; font-weight:600; letter-spacing:0.1em;">
          MICROMECÁNICA
        </span>
        <span style="background:#1a2235; border:1px solid #2a4080; border-radius:4px;
                     padding:2px 8px; font-size:10px; color:#6b8cba;">v1.0</span>
        <span style="color:#1e3a5f;">|</span>
        <span style="color:#4a6080; font-size:10px; letter-spacing:0.08em;">
          Halpin-Tsai · Rule of Mixtures · Tsai-Wu
        </span>
      </div>
      <div style="color:#6b8cba; font-size:10px; letter-spacing:0.06em;">
        PROPIEDADES CALCULADAS — Vf = {Vf*100:.0f}% · {fiber_name} / {matrix_name}
      </div>
    </div>
    ''', unsafe_allow_html=True)
