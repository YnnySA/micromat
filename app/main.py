# Implements: specs/SPEC-UI-01-REDISENO VISUAL.md
"""Punto de entrada único de la aplicación Streamlit."""

import streamlit as st

st.set_page_config(layout="wide", page_title="Micromecánica v1.0", page_icon="🔬")

# CSS Global
st.markdown('''
<style>
  @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600&display=swap');
  html, body, [class*="css"] {
    font-family: 'JetBrains Mono', monospace !important;
    background-color: #0a0f1e !important;
    color: #e2e8f8 !important;
  }
  section[data-testid="stSidebar"] {
    background-color: #0d1427 !important;
    border-right: 1px solid #1e3a5f !important;
    min-width: 300px !important;
    max-width: 320px !important;
  }
  .stSlider [data-baseweb="slider"] { accent-color: #22d3ee; }
  .stSelectbox > div > div { background-color: #1a2235 !important; border: 1px solid #1e3a5f !important; color: #22d3ee !important; }
  .stNumberInput input { background-color: #1a2235 !important; border: 1px solid #1e3a5f !important; color: #22d3ee !important; text-align: right !important; font-family: 'JetBrains Mono', monospace !important; }
  #MainMenu, footer { visibility: hidden; }
  header[data-testid="stHeader"] { visibility: visible; background: transparent !important; }
  div[data-testid="stAppDeployButton"], span[data-testid="stMainMenu"] { visibility: hidden !important; }
  [data-testid="stSidebarCollapseButton"],
  [data-testid="stSidebarCollapseButton"] [data-testid="stBaseButton-headerNoPadding"] {
    visibility: visible !important;
  }
  .stTabs [data-baseweb="tab-list"] { background-color: #111827; border-bottom: 1px solid #1e3a5f; gap: 0; }
  .stTabs [data-baseweb="tab"] { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.05em; color: #4a6080; background: transparent; padding: 10px 16px; border-bottom: 2px solid transparent; }
  .stTabs [aria-selected="true"] { color: #22d3ee !important; border-bottom: 2px solid #22d3ee !important; background: transparent !important; }
  .block-container { padding: 12px 24px 0 !important; max-width: 100% !important; }
</style>
''', unsafe_allow_html=True)

from pages.resultados import render_results_page


navigation = st.navigation(
    [st.Page(render_results_page, title="Micromecánica", icon="🔬")],
    position="hidden",
)
navigation.run()
