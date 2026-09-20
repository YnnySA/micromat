# Especificación: Interfaz Nativa, Vintage y Cálculos Unificados

> **ID:** SPEC-08
> **Prioridad:** Must
> **Estado:** Propuesta
> **Fuente:** Retroalimentación de usuario (2026-09-20); `U_2/tarea_01.ipynb`; `U_2/Clase2_U2_updated.pptx`

## Objetivo

Unificar todos los cálculos con el contenido exclusivo del curso (U2), eliminar la
inyección de CSS/HTML de la interfaz para usar componentes nativos de Streamlit
(rápida), y adoptar un tema claro tipo papel sepia con tipografía monoespaciada,
sin alterar la estructura de pestañas, menús y distribución existentes.

## Alcance

- Cálculos exclusivos del notebook: ROM (`E1`, `nu12`), Halpin-Tsai (`E2` ξ=2, `G12` ξ=1),
  reciprocidad (`nu21`), `F1t` ROM, `F1c` Rosen + práctica `0.575·F1t`, Barbero (`F2t`, `F6`),
  `F2c = 4·F2t`.
- Interfaz puro Python: sin `unsafe_allow_html`, sin bloques `<style>`, sin `@import`.
- Tema vía `.streamlit/config.toml` (light, `font = "monospace"`, papel sepia, un acento).
- Etiquetas con letras griegas (Unicode). Los ejes Plotly usan notación Unicode
  (E₁, ν₁₂, σ₁, …) porque Plotly requiere MathJax, que Streamlit no carga; `$...$`
  se muestra literal. El LaTeX de la pestaña Teoría usa `st.latex` (KaTeX, offline).
- Tarjetas de resultados en `st.container(border=True)` + `st.caption` + `st.markdown`,
  con valor a tamaño base para que no se truncen (se descarta `st.metric`).
- Líneas de gráficos delgadas (≈1.3–1.5 px) y pocos colores.
- Se conserva: sidebar (Vf, Fibra, edición, Matriz, edición), franja de cabecera,
  10 tarjetas (5+5) y las 5 pestañas con sus gráficos.

## Reglas de dominio

- Una sola capa física: `core/calculations.py`; `core/micromechanics.py` son envoltorios.
- Las cifras del notebook son la referencia (p. ej. IM7: `Gf12=27`, `Em=4.67`).
- Los valores se calculan en MPa donde corresponde y se muestran en GPa cuando aplica.
- No se añaden dependencias nuevas.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-08-01 | Las fórmulas del curso se reproducen desde `calculations` | `test_spec01_calculations` |
| AC-08-02 | El código de `app/` no usa `unsafe_allow_html` ni bloques `<style>` | `test_no_html_injection` |
| AC-08-03 | `micromechanics` y `calculations` entregan los mismos resultados | `test_layers_agree` |
| AC-08-04 | Existe `.streamlit/config.toml` con tema claro y fuente monoespaciada | `test_theme_config` |
| AC-08-05 | El layout de 10 tarjetas y 6 pestañas se mantiene | `test_two_column_layout` |
| AC-08-06 | Las etiquetas de los gráficos no usan `$...$` (MathJax) | `test_charts_labels_unicode` |
