# Especificación: Diseño Inverso

> **ID:** SPEC-05
> **Prioridad:** Should
> **Estado:** Propuesta
> **Fuente:** `tarea_01.ipynb` — Parte D; `Informe.md` — Diseño Inverso

## Objetivo

El estudiante debe poder aplicar los modelos micromecánicos a un problema de diseño inverso: encontrar la fracción volumétrica mínima de fibra que satisface simultáneamente requisitos de rigidez y resistencia para un tubo de bicicleta, comparando ambos sistemas de material.

## Alcance

- Definición de requisitos de diseño: E1 ≥ 40 GPa, F1t ≥ 700 MPa, Vf ≤ 0.65.
- Barrido fino de Vf (6500 puntos) para identificar el Vf mínimo factible.
- Identificación de la restricción activa (rigidez o resistencia).
- Comparación de rigidez específica E1/ρ en el punto de diseño.
- Recomendación de material basada en los resultados.

## Escenarios

Feature: Diseño inverso de materiales compuestos

  Scenario: Definir requisitos de diseño
    Given el usuario está en la pestaña "Diseño Inverso"
    Then se muestran los requisitos de diseño por defecto:
      | E1 ≥ 40 GPa | F1t ≥ 700 MPa | Vf ≤ 0.65 |
    And cada requisito es editable mediante un campo numérico
    And se muestra una descripción del contexto: "Tubo de cuadro de bicicleta UD a 0°"

  Scenario: Ejecutar búsqueda de Vf mínimo
    Given los requisitos de diseño son E1 ≥ 40 GPa, F1t ≥ 700 MPa, Vf ≤ 0.65
    When el usuario ejecuta el diseño inverso
    Then se evalúan ambos sistemas (IM7/8552 y E-glass/Epoxi)
    And se muestra una tabla con:
      | Sistema | ¿Factible? | Vf_min | E1 en Vf_min | F1t en Vf_min | ρ | E1/ρ |
    And para IM7/8552, Vf_min ≈ 0.13
    And para E-glass/Epoxi, Vf_min ≈ 0.53

  Scenario: Identificar restricción activa
    Given se ha ejecutado el diseño inverso para IM7/8552
    When se muestran los resultados
    Then se indica cuál requisito determina el Vf mínimo
    And se muestra que E1 es la restricción activa (E1 ≈ 40 GPa en Vf_min)
    And se muestra que F1t tiene holgura (F1t > 700 MPa en Vf_min)

  Scenario: Comparar rigidez específica
    Given se han calculado los Vf mínimos para ambos sistemas
    When se muestran los resultados
    Then se compara E1/ρ de ambos sistemas en su Vf_min respectivo
    And se destaca el sistema con mayor rigidez específica
    And se muestra la densidad de cada sistema en el punto de diseño

  Scenario: Recomendación de material
    Given ambos sistemas son factibles
    When se muestran los resultados del diseño inverso
    Then se emite una recomendación fundamentada:
      | "IM7/8552 requiere menos fibra (Vf=0.13 vs 0.53) y ofrece mayor rigidez específica" |
    And se menciona que el tubo de IM7/8552 sería más liviano para la misma rigidez
    And se indica que esta es la opción preferida para un cuadro de bicicleta

  Scenario: Requisitos no factibles
    Given el usuario establece E1 ≥ 200 GPa (inalcanzable con estos materiales)
    When se ejecuta el diseño inverso
    Then se muestra "No factible" para ambos sistemas
    And se explica que ningún Vf ≤ 0.65 alcanza el requisito
    And se sugiere relajar el requisito o cambiar de material

  Scenario: Error al ingresar requisitos fuera de rango (Edge Case)
    Given el usuario está en la pestaña "Diseño Inverso"
    When el usuario ingresa un valor de Vf_max < 0 o > 1.0
    Then se muestra un mensaje: "El valor de Vf debe estar entre 0 y 1"
    And el botón "Ejecutar diseño" se deshabilita
    And no se realiza ningún cálculo

  Scenario: Modificar requisitos y recalcular
    Given el usuario está en la pestaña "Diseño Inverso"
    And los resultados actuales corresponden a E1 ≥ 40 GPa
    When el usuario cambia el requisito a E1 ≥ 50 GPa
    And ejecuta el diseño inverso
    Then los resultados se actualizan con los nuevos Vf_min
    And se recalculan E1/ρ y restricción activa

## Reglas de dominio

- Barrido fino: `np.linspace(0.01, Vf_max, 6500)`.
- Criterio de factibilidad: `(E1 >= E1_req) & (F1t >= F1t_req)`.
- Vf_min es el primer índice donde `cumple` es True (argmax).
- Si no existe solución, se reporta "No factible".
- La restricción activa es aquella cuyo valor en Vf_min está más cerca de su requisito.
- La densidad se calcula como ρ = Vf·ρf + (1−Vf)·ρm.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-05-01 | La tabla de resultados muestra 6 columnas para ambos sistemas | `test_design_table` |
| AC-05-02 | Vf_min para IM7 es ~0.13 y para E-glass es ~0.53 con tolerancia ±0.01 | `test_vf_min_values` |
| AC-05-03 | Se identifica E1 como restricción activa para IM7/8552 | `test_active_constraint` |
| AC-05-04 | Caso no factible muestra mensaje y sugiere acción | `test_infeasible_case` |
| AC-05-05 | Los requisitos son editables y el recálculo es inmediato | `test_editable_requirements` |
 