# Especificación: Pestaña de Teoría del Curso (U1 + U2)

> **ID:** SPEC-09
> **Prioridad:** Must
> **Estado:** Propuesta
> **Fuente:** `U_2/Clase2_U2_updated.md`; `U_1/U1_Introduccion_DAMC.pptx`

## Objetivo

Ofrecer en la aplicación una pestaña "Teoría" donde el estudiante vea los aspectos
conceptuales y las fórmulas utilizadas en los cálculos, extraídos exclusivamente de
las unidades 1 y 2 del curso.

## Alcance

- Sexta pestaña "Teoría", ubicada junto a "Comparación".
- Contenido centralizado en `app/core/course_theory.py` (bloques con texto, viñetas,
  fórmulas LaTeX y notas), sin lógica de UI.
- Render nativo en `app/components/theory_tab.py` con `st.expander`, `st.markdown`,
  `st.latex` y `st.dataframe` (sin HTML).
- Tablas de apoyo: modelos usados en la aplicación y confiabilidad de las resistencias.

## Secciones

1. ¿Por qué predecir desde los constituyentes?
2. ¿Qué es un material compuesto? (U1)
3. Anisotropía y grados de libertad de diseño (U1)
4. La lámina UD y sus 9 propiedades
5. Fracciones volumétricas y VRE
6. Regla de Mezclas
7. Halpin-Tsai
8. Reciprocidad elástica (ν₂₁)
9. Resistencias de la lámina UD
10. Confiabilidad y limitaciones

## Reglas de dominio

- El contenido proviene solo de U1 y U2 (no se incluye U3 ni otras unidades).
- Las fórmulas se renderizan con `st.latex` (KaTeX incluido en Streamlit; no requiere red).
- Cada sección es colapsable (expander); la primera se muestra expandida.
- La interfaz no usa `unsafe_allow_html`.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-09-01 | Existen al menos 8 bloques teóricos con título | `test_theory_blocks` |
| AC-09-02 | El conjunto de fórmulas incluye Vf, E₁, G₁₂ y η | `test_theory_has_course_formulas` |
| AC-09-03 | El mapa de modelos cubre las 10 propiedades calculadas | `test_model_map` |
| AC-09-04 | La tabla de confiabilidad lista al menos 4 modelos con estrellas | `test_reliability_rows` |
| AC-09-05 | La pestaña "Teoría" se renderiza sin excepciones | `test_navigation_tabs` |
