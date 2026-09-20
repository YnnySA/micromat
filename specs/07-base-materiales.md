# Especificación: Base de Datos Ligera de Materiales

> **ID:** SPEC-07
> **Prioridad:** Must
> **Estado:** Propuesta
> **Fuente:** Retroalimentación de usuario (2026-09-20); `U_2/Clase2_U2_updated.pptx` — lámina 13

## Objetivo

Reemplazar los catálogos de fibras/matrices codificados en el código por una
base de datos SQLite ligera (stdlib) que permita insertar, editar, eliminar y
seleccionar materiales de forma persistente, partiendo sin fibras preestablecidas
en la interfaz.

## Alcance

- Base SQLite en `proyecto01/data/materials.db`, creada y sembrada automáticamente.
- Tablas `fibers` y `matrices` con las propiedades que consumen los modelos del curso.
- API pura (sin Streamlit): `list_*`, `get_*`, `save_*`, `delete_*`.
- Semilla con los materiales del curso (notebook) y de referencia (lámina 13).
- Interfaz de gestión dentro del sidebar: agregar, guardar cambios y eliminar.

## Reglas de dominio

- Campos de fibra: `E1, E2, G12, nu12, F1t, etu, density` (GPa, GPa, GPa, —, MPa, —, kg/m³).
- Campos de matriz: `E, nu, G, Ft, density` (GPa, —, GPa, MPa, kg/m³).
- La lista de semilla es editable y eliminar un material no afecta a los demás.
- Los sistemas del curso (`IM7` + `Epoxy 8552`, `E-glass` + `Epoxi`) reproducen
  los valores del notebook.
- Sin dependencias nuevas: se usa `sqlite3` de la biblioteca estándar.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-07-01 | La base se crea y siembra si no existe, y `list_fibers` devuelve las de referencia | `test_material_db_seed` |
| AC-07-02 | Guardar una fibra nueva y recuperarla devuelve los mismos valores | `test_material_db_crud` |
| AC-07-03 | Actualizar una fibra existente reemplaza sus propiedades | `test_material_db_crud` |
| AC-07-04 | Eliminar una fibra la quita de la lista | `test_material_db_crud` |
| AC-07-05 | `get_fiber` de un nombre inexistente devuelve `None` | `test_material_db_crud` |
