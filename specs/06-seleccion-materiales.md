# Especificación: Selección Interactiva de Materiales

> **ID:** SPEC-06
> **Prioridad:** Must
> **Estado:** Propuesta
> **Fuente:** Prototipo Figma Make "Aplicación educativa de materiales"; retroalimentación de usuario post-MVP (sesión 2026-09-09)

## Objetivo

El estudiante debe poder seleccionar o definir libremente las propiedades de fibra y matriz desde un panel persistente, en lugar de trabajar con un único sistema de material fijo, para poder replicar los cálculos y análisis con cualquier combinación fibra-matriz de su interés.

## Alcance

- Panel lateral persistente con selección de fibra y matriz mediante listas desplegables predefinidas.
- Base de datos mínima de materiales de referencia: fibras (E-Glass, Carbon T300, Kevlar 49, Boron, IM7) y matrices (Epoxy 3501-6, Epoxi 8552).
- Autocompletado de propiedades (E, G, ν, resistencias, densidad) al seleccionar un material predefinido.
- Edición manual de cualquier propiedad autocompletada, sin restricción a los valores de catálogo.
- Recalculo inmediato de todos los resultados visibles al cambiar cualquier propiedad o material.
- No incluye: persistencia de materiales personalizados entre sesiones (queda fuera de alcance, ver SPEC-07 si se define).

## Escenarios

Feature: Selección y edición de materiales fibra-matriz

  Scenario: Seleccionar material predefinido
    Given el usuario está en el panel lateral "Propiedades de Fibra"
    When selecciona "E-Glass" desde la lista desplegable de fibra
    Then los campos E1, E2, G12, v12, F1t, F1c, F2t, F2c, F12s se
      autocompletan con los valores de referencia de E-Glass
    And todos los resultados calculados se actualizan sin recargar
      la página

  Scenario: Seleccionar matriz predefinida
    Given el usuario está en el panel lateral "Propiedades de Matriz"
    When selecciona "Epoxy 3501-6" desde la lista desplegable de matriz
    Then los campos Em, vm, Gm, Fmt, Fmc, Fms se autocompletan con
      los valores de referencia de Epoxy 3501-6
    And todos los resultados calculados se actualizan sin recargar
      la página

  Scenario: Sobreescribir una propiedad autocompletada
    Given el usuario tiene "Carbon T300" seleccionado como fibra
    And los campos están autocompletados con sus valores de referencia
    When el usuario edita manualmente el campo E1 a un valor distinto
    Then el sistema usa el valor editado en todos los cálculos
      subsecuentes
    And el material seleccionado permanece etiquetado como "Carbon T300
      (modificado)"

  Scenario: Ajustar fracción de volumen de fibra
    Given el usuario tiene un material fibra-matriz seleccionado
    When mueve el control deslizante de fracción de volumen (Vf)
    Then Vm se actualiza automáticamente como (1 − Vf)
    And todas las propiedades calculadas (E1, E2, G12, v12,
      resistencias) se recalculan en tiempo real

  Scenario: Comparar propiedades entre fibras
    Given el usuario está en la pestaña "Comparación"
    And una matriz está seleccionada (ej. "Epoxy 3501-6")
    When el sistema mantiene la matriz constante
    Then se muestra un gráfico de barras con E1, E2 y G12 para todas
      las fibras disponibles en la base de datos de materiales, en
      el Vf actualmente seleccionado

  Scenario: Navegar entre categorías de análisis sin perder contexto
    Given el usuario cambia el material o cualquier propiedad
    When navega entre las pestañas "Módulos Elásticos", "Resistencias",
      "Off-Axis Ex(θ)", "Envolvente de Fallo" y "Comparación"
    Then cada pestaña refleja los valores de entrada vigentes sin
      requerir reconfiguración

  Scenario: Ingresar propiedades de un material no catalogado
    Given el usuario selecciona la opción "Personalizado" en fibra
      o matriz
    When ingresa manualmente todas las propiedades requeridas
    Then el sistema valida que los valores estén dentro de rangos
      físicamente plausibles antes de habilitar el cálculo

  Scenario: Error al ingresar propiedades fuera de rango (Edge Case)
    Given el usuario está editando una propiedad de fibra o matriz
    When ingresa un valor negativo para un módulo elástico (E1, E2,
      G12) o un coeficiente de Poisson fuera del rango (0, 0.5)
    Then se muestra un mensaje de error específico junto al campo
      ("El módulo debe ser positivo", "ν debe estar entre 0 y 0.5")
    And los resultados no se recalculan hasta corregir el valor

## Reglas de dominio

- La base de datos de materiales reside en `app/core/materials_db.py`
  como estructura de datos pura, sin dependencias de Streamlit.
- Cada material de referencia incluye: nombre, tipo (fibra/matriz),
  propiedades elásticas, resistencias y densidad (ρ).
- Al seleccionar "Personalizado", el sistema no autocompleta ningún
  campo; todos los valores parten vacíos o en cero.
- La validación de rangos físicos se aplica independientemente del
  origen del valor (catálogo o edición manual): E > 0, G > 0,
  0 < ν < 0.5, resistencias ≥ 0.
- El estado "(modificado)" se activa si al menos un campo autocompletado
  difiere del valor de catálogo original para ese material.
- Vm se deriva siempre como (1 − Vf); no es editable de forma
  independiente.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-06-01 | Seleccionar una fibra o matriz predefinida autocompleta todos sus campos correspondientes | `test_material_autofill` |
| AC-06-02 | Editar manualmente un campo autocompletado marca el material como "(modificado)" y usa el valor editado en los cálculos | `test_material_override` |
| AC-06-03 | Cambiar Vf recalcula Vm y todas las propiedades dependientes sin recargar la página | `test_vf_recalculation` |
| AC-06-04 | La pestaña "Comparación" muestra E1, E2, G12 de todas las fibras disponibles con la matriz seleccionada constante | `test_comparison_chart` |
| AC-06-05 | Seleccionar "Personalizado" limpia los campos y exige validación de rango antes de habilitar el cálculo | `test_custom_material_validation` |
| AC-06-06 | Ingresar un valor fuera de rango físico (E ≤ 0, ν fuera de (0, 0.5)) muestra error específico y bloquea el recálculo | `test_invalid_property_range` |