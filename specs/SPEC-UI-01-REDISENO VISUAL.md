SPEC-UI-01 - REDISENO VISUAL COMPLETO
Micromecanica de Materiales Compuestos
Referencia canonica: App.tsx (Figma Make export)
Esta spec reemplaza completamente cualquier interfaz existente.

===============================================================
1. OBJETIVO
===============================================================
Reescribir la interfaz actual de la app Streamlit para que sea
visualmente idéntica al prototipo de referencia en Figma Make.
Toda la lógica de cálculo existente debe preservarse. Solo cambia
la presentación: layout, tema, colores, tipografía, componentes
y organización de gráficos.

===============================================================
2. SISTEMA DE DISEÑO - TOKENS
===============================================================
Crear el archivo src/styles/theme.py con estas constantes.
No usar otros colores en ningun lugar de la app.

# Fondos
BG_APP        = "#0a0f1e"
BG_SIDEBAR    = "#0d1427"
BG_CARD       = "#111827"
BG_CHART      = "#0f1525"
BG_INPUT      = "#1a2235"
BG_TAB_ACTIVE = "#111827"

# Bordes
BORDER_DIM    = "#1e3a5f"
BORDER_ACCENT = "#2a4080"

# Texto
TEXT_PRIMARY  = "#e2e8f8"
TEXT_MUTED    = "#4a6080"
TEXT_LABEL    = "#6b8cba"

# Acentos (uno por propiedad, fijo en toda la app)
CYAN    = "#22d3ee"   # E1, F1t
GREEN   = "#4ade80"   # E2, F2t
ORANGE  = "#fb923c"   # G12, F12s
PURPLE  = "#a78bfa"   # nu12, F2c
RED     = "#f87171"   # F1c
GRAY    = "#94a3b8"   # nu21

FONT_MONO = "JetBrains Mono, monospace"
FONT_SIZE_LABEL = "11px"

Inyectar con st.markdown() al inicio de main.py:

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
  #MainMenu, footer, header { visibility: hidden; }
  .stTabs [data-baseweb="tab-list"] { background-color: #111827; border-bottom: 1px solid #1e3a5f; gap: 0; }
  .stTabs [data-baseweb="tab"] { font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 0.05em; color: #4a6080; background: transparent; padding: 10px 16px; border-bottom: 2px solid transparent; }
  .stTabs [aria-selected="true"] { color: #22d3ee !important; border-bottom: 2px solid #22d3ee !important; background: transparent !important; }
  .block-container { padding: 0 !important; max-width: 100% !important; }
</style>
''', unsafe_allow_html=True)

===============================================================
3. ESTRUCTURA DE ARCHIVOS
===============================================================
app/
  main.py                  <- REESCRIBIR completamente
  core/
    materials_db.py        <- PRESERVAR, extender con nuevas matrices
    micromechanics.py      <- PRESERVAR sin cambios
  styles/
    theme.py                <- CREAR (tokens del punto 2)
  components/
    header.py               <- CREAR
    sidebar_inputs.py       <- CREAR (reemplaza material_selector.py)
    result_cards.py         <- CREAR
    charts.py                <- CREAR (todos los graficos Plotly)

===============================================================
4. LAYOUT PRINCIPAL (main.py)
===============================================================
Usar st.set_page_config(layout="wide", page_title="Micromecánica v1.0", page_icon="🔬")

El layout tiene 3 zonas verticales en este orden:

  HEADER (franja completa ancho 100%)
  ---------------------------------------------------------
  SIDEBAR INPUTS (25%)  |  RESULTS STRIP + TABS + CHART AREA (75%)

Implementar con: col_left, col_right = st.columns([1, 3])

===============================================================
5. COMPONENTE: HEADER (components/header.py)
===============================================================
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

===============================================================
6. COMPONENTE: SIDEBAR INPUTS (components/sidebar_inputs.py)
===============================================================

6.1 Base de datos de materiales - COMPLETA
(valores tomados literalmente del App.tsx)

FIBER_PRESETS = {
    "Carbon T300": {"E1":230, "E2":15,  "G12":15,  "nu12":0.20, "F1t":3500, "F1c":2500, "F2t":56,   "F2c":150,  "F12s":70},
    "E-Glass":     {"E1":73,  "E2":73,  "G12":30,  "nu12":0.22, "F1t":2400, "F1c":1200, "F2t":2400, "F2c":1200, "F12s":500},
    "Kevlar 49":   {"E1":125, "E2":8,   "G12":2.9, "nu12":0.35, "F1t":2800, "F1c":480,  "F2t":30,   "F2c":138,  "F12s":43},
    "Boron":       {"E1":400, "E2":400, "G12":167, "nu12":0.20, "F1t":3500, "F1c":3000, "F2t":3500, "F2c":3000, "F12s":1200},
}

MATRIX_PRESETS = {
    "Epoxy 3501-6":  {"E":4.2,  "nu":0.35, "G":1.56, "Ft":69,  "Fc":250, "Fs":50},
    "Polyester":     {"E":3.5,  "nu":0.38, "G":1.27, "Ft":55,  "Fc":140, "Fs":40},
    "Aluminum 6061": {"E":69,   "nu":0.33, "G":26,   "Ft":310, "Fc":310, "Fs":200},
    "Titanium":      {"E":110,  "nu":0.34, "G":41,   "Ft":900, "Fc":900, "Fs":550},
}

6.2 Controles del sidebar

def render_sidebar() -> tuple[dict, dict, float]:
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
            fiber["E1"]   = st.number_input("E1 (GPa)",  value=float(fiber["E1"]),  step=1.0, key="f_E1")
            fiber["E2"]   = st.number_input("E2 (GPa)",  value=float(fiber["E2"]),  step=0.5, key="f_E2")
            fiber["G12"]  = st.number_input("G12 (GPa)", value=float(fiber["G12"]), step=0.5, key="f_G12")
            fiber["nu12"] = st.number_input("nu12",       value=float(fiber["nu12"]),step=0.01,key="f_nu12")
            fiber["F1t"]  = st.number_input("F1t (MPa)", value=float(fiber["F1t"]), step=10.0,key="f_F1t")
            fiber["F1c"]  = st.number_input("F1c (MPa)", value=float(fiber["F1c"]), step=10.0,key="f_F1c")
            fiber["F2t"]  = st.number_input("F2t (MPa)", value=float(fiber["F2t"]), step=1.0, key="f_F2t")
            fiber["F2c"]  = st.number_input("F2c (MPa)", value=float(fiber["F2c"]), step=1.0, key="f_F2c")
            fiber["F12s"] = st.number_input("F12s (MPa)",value=float(fiber["F12s"]),step=1.0, key="f_F12s")

        st.markdown("---")

        st.markdown('<p style="color:#4a6080;font-size:10px;letter-spacing:0.1em;">PROPIEDADES DE MATRIZ</p>', unsafe_allow_html=True)
        matrix_preset = st.selectbox("Matriz", list(MATRIX_PRESETS.keys()), label_visibility="collapsed")
        matrix = dict(MATRIX_PRESETS[matrix_preset])

        with st.expander("Editar propiedades de matriz", expanded=False):
            matrix["E"]  = st.number_input("Em (GPa)", value=float(matrix["E"]),  step=0.1, key="m_E")
            matrix["nu"] = st.number_input("num",       value=float(matrix["nu"]), step=0.01,key="m_nu")
            matrix["G"]  = st.number_input("Gm (GPa)", value=float(matrix["G"]),  step=0.1, key="m_G")
            matrix["Ft"] = st.number_input("Fmt (MPa)",value=float(matrix["Ft"]), step=1.0, key="m_Ft")
            matrix["Fc"] = st.number_input("Fmc (MPa)",value=float(matrix["Fc"]), step=1.0, key="m_Fc")
            matrix["Fs"] = st.number_input("Fms (MPa)",value=float(matrix["Fs"]), step=1.0, key="m_Fs")

    return fiber, matrix, Vf

===============================================================
7. COMPONENTE: RESULT CARDS (components/result_cards.py)
===============================================================
Dos filas de 5 tarjetas cada una. Usar st.columns(5) por fila.

def render_result_cards(props: dict):
    cols = st.columns(5)
    cards_elastic = [
        ("E1",   props["E1"],   "GPa", CYAN),
        ("E2",   props["E2"],   "GPa", GREEN),
        ("G12",  props["G12"],  "GPa", ORANGE),
        ("nu12", props["nu12"], "",    PURPLE),
        ("nu21", props["nu21"], "",    GRAY),
    ]
    for col, (label, value, unit, color) in zip(cols, cards_elastic):
        with col:
            decimals = 4 if label in ("nu12","nu21") else 2
            st.markdown(f'''
            <div style="background:#111827; border:1px solid #1e3a5f; border-top:2px solid {color};
                        border-radius:6px; padding:12px 10px; text-align:center; margin-bottom:8px;">
              <div style="color:#4a6080;font-size:9px;letter-spacing:0.1em;margin-bottom:4px;">{label}</div>
              <div style="color:{color};font-size:18px;font-weight:600;font-family:'JetBrains Mono',monospace;">
                {value:.{decimals}f}
              </div>
              <div style="color:#4a6080;font-size:9px;">{unit}</div>
            </div>
            ''', unsafe_allow_html=True)

    cols2 = st.columns(5)
    cards_strength = [
        ("F1t",  props["F1t"],  "MPa", CYAN),
        ("F1c",  props["F1c"],  "MPa", RED),
        ("F2t",  props["F2t"],  "MPa", GREEN),
        ("F2c",  props["F2c"],  "MPa", ORANGE),
        ("F12s", props["F12s"], "MPa", PURPLE),
    ]
    for col, (label, value, unit, color) in zip(cols2, cards_strength):
        with col:
            st.markdown(f'''
            <div style="background:#111827; border:1px solid #1e3a5f; border-top:2px solid {color};
                        border-radius:6px; padding:12px 10px; text-align:center; margin-bottom:8px;">
              <div style="color:#4a6080;font-size:9px;letter-spacing:0.1em;margin-bottom:4px;">{label}</div>
              <div style="color:{color};font-size:18px;font-weight:600;font-family:'JetBrains Mono',monospace;">
                {value:.1f}
              </div>
              <div style="color:#4a6080;font-size:9px;">{unit}</div>
            </div>
            ''', unsafe_allow_html=True)

===============================================================
8. COMPONENTE: GRAFICOS PLOTLY (components/charts.py)
===============================================================

8.0 Config base de todos los graficos

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#0f1525",
    plot_bgcolor="#0f1525",
    font=dict(family="JetBrains Mono, monospace", size=11, color="#e2e8f8"),
    xaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    yaxis=dict(gridcolor="#1e3a5f", linecolor="#1e3a5f", zerolinecolor="#1e3a5f"),
    legend=dict(bgcolor="#0f1525", bordercolor="#1e3a5f", borderwidth=1),
    margin=dict(l=50, r=20, t=40, b=40),
    height=380,
)

8.1 Tab "Módulos Elásticos"
- Grafico 1: LineChart eje X = Vf (5%-80%), lineas E1 (CYAN), E2 (GREEN), G12 (ORANGE).
  Eje Y en GPa. Titulo: "Módulos vs Fracción de Volumen".
  Linea vertical punteada (color #4a6080) en el Vf actual.
- Grafico 2: LineChart mismos ejes, solo nu12 (PURPLE).
  Titulo: "Coeficiente de Poisson nu12 vs Vf".
- Usar st.columns(2) para poner los dos lado a lado.
- Sweep: vf_range = np.arange(0.05, 0.81, 0.01), calcular calcProps() para cada valor.

8.2 Tab "Resistencias"
- Grafico 1: LineChart F1t (CYAN), F1c (RED). Eje Y en MPa.
  Titulo: "Resistencias Longitudinales vs Vf".
- Grafico 2: LineChart F2t (GREEN), F2c (ORANGE), F12s (PURPLE).
  Titulo: "Resistencias Transversales vs Vf".
- Linea vertical punteada en Vf actual en ambos.
- Layout: st.columns(2).

8.3 Tab "Off-Axis Ex(theta)"
- Grafico: LineChart eje X = theta (0-90 grados, paso 2), eje Y = Ex (GPa) en CYAN.
  Titulo: "Módulo Longitudinal Off-Axis Ex(θ)".
  Marcadores en theta = 0,15,30,45,60,75,90.
- Tabla de valores a la derecha del grafico en st.columns([2,1]):
  tabla HTML con fondo #111827, cabecera en #4a6080, valores en CYAN.
  Columnas: theta, Ex (GPa). Filas para theta = 0,15,30,45,60,75,90.

8.4 Tab "Envolvente Fallo"
- Grafico: ScatterChart (linea cerrada) eje X = sigma1 (MPa), eje Y = sigma2 (MPa).
  Color CYAN con relleno semitransparente rgba(34,211,238,0.08).
  Lineas de referencia verticales y horizontales en 0 (color #4a6080).
  Titulo: "Envolvente de Fallo — Criterio Tsai-Wu".
- Panel de parametros a la derecha en st.columns([2,1]):
  Label "CRITERIO TSAI-WU" en #4a6080
  Ecuacion: F1*sigma1 + F2*sigma2 + F11*sigma1^2 + F22*sigma2^2 + 2*F12*sigma1*sigma2 = 1
  en #e2e8f8 con fuente mono
  Label "PARAMETROS" en #4a6080
  Tabla: F1t, F1c, F2t, F2c con sus valores calculados en MPa, coloreados CYAN.

Calculo del barrido (identico al App.tsx):
  F1  = 1/F1t - 1/F1c
  F2  = 1/F2t - 1/F2c
  F11 = 1/(F1t*F1c)
  F22 = 1/(F2t*F2c)
  F12 = -0.5 * sqrt(F11*F22)
  # barrido 360 puntos
  for phi in linspace(0, 2*pi, 361):
      c, s = cos(phi), sin(phi)
      a = F11*c**2 + F22*s**2 + 2*F12*c*s
      b = F1*c + F2*s
      disc = b**2 + 4*a
      if disc >= 0 and a != 0:
          r = (-b + sqrt(disc)) / (2*a)
          if 0 < r < 10000:
              points.append((r*c, r*s))

8.5 Tab "Comparación"
- Grafico 1: BarChart agrupado X = [Carbon T300, E-Glass, Kevlar 49, Boron],
  barras E1 (CYAN), E2 (GREEN), G12 (ORANGE). Eje Y en GPa.
  Titulo: "Módulos Elásticos — Comparación de Fibras (Vf actual)".
  Calcular con matrix actual y Vf actual.
- Grafico 2: BarChart X = mismas fibras, barra F1t (CYAN). Eje Y en MPa.
  Titulo: "Resistencia Longitudinal F1t — Comparación".
- Layout: st.columns(2).

===============================================================
9. MICROMECANICA - FORMULAS
===============================================================
(verificar que micromechanics.py las tenga exactas)

# Regla de mezclas
E1   = fiber["E1"]*Vf + matrix["E"]*Vm
nu12 = fiber["nu12"]*Vf + matrix["nu"]*Vm
nu21 = nu12 * E2/E1

# Halpin-Tsai E2 (xi=2)
eta_E2 = (fiber["E2"]/matrix["E"] - 1) / (fiber["E2"]/matrix["E"] + 2)
E2     = matrix["E"] * (1 + 2*eta_E2*Vf) / (1 - eta_E2*Vf)

# Halpin-Tsai G12 (xi=1)
eta_G12 = (fiber["G12"]/matrix["G"] - 1) / (fiber["G12"]/matrix["G"] + 1)
G12     = matrix["G"] * (1 + eta_G12*Vf) / (1 - eta_G12*Vf)

# Resistencias (Rule of Mixtures + correccion empirica)
F1t = fiber["F1t"]*Vf + matrix["Ft"]*Vm
F1c = fiber["F1c"]*Vf + matrix["Fc"]*Vm
F2t = matrix["Ft"] * (1 - Vf**(1/3) * (1 - matrix["E"]/E2))
F2c = matrix["Fc"] * (1 - Vf**(1/3) * (1 - matrix["E"]/E2))
F12s = matrix["Fs"] * (1 - (Vf**(1/3) - Vf) * (1 - matrix["G"]/G12))

# Off-axis Ex(theta)
inv = cos**4/E1 + sin**4/E2 + (sin*cos)**2 * (1/G12 - 2*nu12/E1)
Ex  = 1/inv

===============================================================
10. CRITERIOS DE ACEPTACION
===============================================================
[ ] AC-01 - Fondo #0a0f1e visible en toda la app sin fondo blanco de Streamlit
[ ] AC-02 - Sidebar con fondo #0d1427, ancho ~300px, fuente monoespaciada
[ ] AC-03 - Header con badge v1.0 y contexto dinamico Vf = XX% · Fibra / Matriz
[ ] AC-04 - Slider Vf muestra valor actualizado con Vf = XX% · Vm = 0.XX bajo el slider
[ ] AC-05 - 10 tarjetas de resultado visibles (5 modulos + 5 resistencias) con color-top de acento correcto por propiedad
[ ] AC-06 - Tab "Módulos Elásticos": 2 graficos Plotly con fondo #0f1525, linea vertical en Vf actual
[ ] AC-07 - Tab "Resistencias": 2 graficos Plotly con las 5 curvas en sus colores correctos
[ ] AC-08 - Tab "Off-Axis": grafico + tabla HTML con 7 filas (0 a 90 grados)
[ ] AC-09 - Tab "Envolvente": scatter cerrado + panel con ecuacion Tsai-Wu y parametros
[ ] AC-10 - Tab "Comparación": 2 bar charts para las 4 fibras con matrix/Vf actuales
[ ] AC-11 - Al cambiar preset de fibra, todos los graficos y tarjetas se actualizan sin recargar la pagina
[ ] AC-12 - No existe ningun elemento de la interfaz anterior (colores por defecto de Streamlit, texto blanco sobre fondo blanco, tablas pandas sin estilo)

===============================================================
11. DEPENDENCIAS
===============================================================
Verificar en requirements.txt o pyproject.toml:
streamlit>=1.35
plotly>=5.20
numpy>=1.26

No se requieren librerias adicionales.