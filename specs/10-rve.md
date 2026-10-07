# Especificación: Visualización Realista del RVE

> **ID:** SPEC-10
> **Prioridad:** Must
> **Estado:** Propuesta
> **Fuente:** `Tarea1_Micromecanica.docx` §A.2; `tarea_01.ipynb` (Parte A2); `Clase2_U2_updated.md` (VRE)

## Objetivo

Agregar una pestaña "RVE" (entre "Resistencias" y "Off-Axis") que muestre el
Elemento de Volumen Representativo de forma realista: las fibras cruzan los
bordes de la celda y reaparecen por el borde opuesto (condiciones periódicas),
respetando un Vf objetivo que nunca se supera.

## Alcance

- Pestaña "RVE" con controles de tamaño de celda, semilla editable y regeneración.
- Fibra y matriz tomadas de la selección del sidebar; el Vf objetivo es el slider.
- Diámetros de fibra `d_min`/`d_max` (µm) por fibra, almacenados en SQLite.
- Motor `core/rve.py`: celda periódica, mínima-imagen, sin Streamlit.
- Render vectorial nítido en `components/rve_view.py` (Plotly), sin HTML.

## Reglas de dominio

- `Vf = Σ π r_i² / L²`, contando el área de cada fibra una sola vez (periódica).
- No-superposición verificada con distancia mínima-imagen; tolerancia 0.01 µm.
- `Vf_logrado ≤ Vf_objetivo`, y lo más cercano posible al objetivo.
- Vf máximo práctico para el RVE: 0.65; si el slider lo supera, se informa.
- Colocación por compresión/relajación (alcanza ~0.60 donde RSA se estanca en ~0.547).
- Uniformización periódica posterior para reducir agrupamientos y zonas vacías sin
  permitir solapes.
- Diámetros dentro del rango `[d_min, d_max]` (se admite un escalado leve).
- Resultado determinista para una misma semilla.
- La semilla no representa una propiedad física: identifica una realización
  pseudoaleatoria reproducible. “Nueva realización” la incrementa para explorar
  otra distribución con los mismos parámetros.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-10-01 | No hay solapes considerando copias periódicas | `test_rve_no_overlap_and_target` |
| AC-10-02 | `Vf_logrado ≤ objetivo` y ≈ objetivo (IM7 0.60, E-glass 0.55) | `test_rve_no_overlap_and_target` |
| AC-10-03 | Los diámetros quedan en torno al rango solicitado | `test_rve_diameters_in_range` |
| AC-10-04 | Misma semilla produce el mismo RVE | `test_rve_deterministic` |
| AC-10-05 | El Vf objetivo no supera el máximo práctico | `test_vf_cap` |
| AC-10-06 | El dibujo incluye copias que cruzan los bordes | `test_polygons_cross_boundary` |
| AC-10-07 | La uniformización reduce agrupamientos manteniendo la periodicidad y el no-solape | `test_rve_uniform_distribution` |
