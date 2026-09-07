# Especificación: Estudio Paramétrico

> **ID:** SPEC-04
> **Prioridad:** Should
> **Estado:** Propuesta
> **Fuente:** `tarea_01.ipynb` — Parte C; `Informe.md` — Análisis Paramétrico

## Objetivo

El estudiante debe tener acceso a explicaciones teóricas contextualizadas junto a los resultados, de modo que pueda relacionar cada valor calculado con el modelo micromecánico que lo produce y con el concepto físico subyacente.

## Alcance

- Gráfico E1, E2 vs Vf (ROM para E1, ROM + Halpin-Tsai para E2).
- Gráfico G12, ν12 vs Vf (Halpin-Tsai para G12, ROM para ν12).
- Gráfico F1t, F1c vs Vf (solo IM7/8552).
- Cálculo de rigidez específica E1/ρ y Vf óptimo.
- Líneas de referencia en Vf de referencia de cada sistema.
- Interpretación textual de cada gráfico.

## Escenarios

Feature: Estudio paramétrico de propiedades

  Scenario: Generar gráfico E1 y E2 vs Vf
    Given el usuario está en la pestaña "Estudio Paramétrico"
    And el rango de Vf es [0.30, 0.65]
    When se ejecuta el análisis paramétrico
    Then se muestra un gráfico de dos paneles:
      | Panel 1: E1 vs Vf para IM7/8552 y E-glass/Epoxi (ROM) |
      | Panel 2: E2 vs Vf para ambos sistemas (ROM y Halpin-Tsai) |
    And el panel de E2 muestra ambas curvas (ROM y Halpin-Tsai) para comparación
    And se muestran líneas verticales punteadas en Vf=0.60 (IM7) y Vf=0.55 (E-glass)
    And los ejes están etiquetados con unidades

  Scenario: Generar gráfico G12 y ν12 vs Vf
    Given el usuario está en la pestaña "Estudio Paramétrico"
    When se ejecuta el análisis paramétrico
    Then se muestra un gráfico de dos paneles:
      | Panel 1: G12 vs Vf (Halpin-Tsai) para ambos sistemas |
      | Panel 2: ν12 vs Vf (ROM) para ambos sistemas |
    And se observa que G12 crece de forma no lineal
    And se observa que ν12 decrece linealmente con Vf

  Scenario: Generar gráfico F1t y F1c vs Vf para IM7
    Given el usuario está en la pestaña "Estudio Paramétrico"
    And el sistema seleccionado es "IM7/8552 (CFRP)"
    When se ejecuta el análisis paramétrico de resistencias
    Then se muestra un gráfico de F1t y F1c vs Vf
    And F1c es siempre menor que F1t (factor 0.575)
    And se muestra la línea de referencia en Vf=0.60

  Scenario: Calcular y mostrar Vf óptimo para rigidez específica
    Given el usuario está en la pestaña "Estudio Paramétrico"
    When se ejecuta el análisis de rigidez específica
    Then se calcula E1/ρ para cada Vf en el rango
    And se muestra el Vf que maximiza E1/ρ para cada sistema
    And se muestra una tabla con: Sistema, Vf_opt, E1/ρ_max
    And se indica que Vf_opt puede estar en el límite superior del rango (0.65)

  Scenario: Interpretación contextual de cada gráfico
    Given se ha generado un gráfico paramétrico
    When el usuario despliega la interpretación
    Then se muestra texto que explica la tendencia observada
    And se menciona el modelo aplicable y por qué
    And se comparan los dos sistemas cuando aplica
    And se relaciona con la física del material compuesto

  Scenario: Personalizar rango de Vf y validar límites
    Given el usuario está en la pestaña "Estudio Paramétrico"
    When el usuario modifica el Vf mínimo a 0.20 y el Vf máximo a 0.70
    Then se validan los límites (Vf_min < Vf_max, ambos en [0, 1])
    And los gráficos se actualizan con el nuevo rango
    And si Vf_max > 0.65 se muestra una advertencia: "Vf > 0.65 puede no ser físicamente alcanzable"

  Scenario: Error al ejecutar análisis con rango inválido
    Given el usuario está en la pestaña "Estudio Paramétrico"
    When el usuario ingresa un rango de Vf donde Vf_min > Vf_max
    Then se deshabilita el botón "Ejecutar análisis"
    And se muestra una alerta visual: "Error: El rango de Vf es inválido (Vf_min > Vf_max)"

## Reglas de dominio

- El barrido usa 200 puntos equidistantes en el rango de Vf.
- La densidad del compuesto se calcula como ρ = Vf·ρf + (1−Vf)·ρm.
- ρf_IM7 = 1780 kg/m³, ρm_IM7 = 1300 kg/m³.
- ρf_Eglass = 2540 kg/m³, ρm_Eglass = 1200 kg/m³.
- Vf_opt se determina como argmax(E1/ρ) en el rango barrido.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-04-01 | El gráfico E1/E2 vs Vf tiene 2 paneles con 4 curvas en total | `test_parametric_e1_e2_chart` |
| AC-04-02 | El gráfico G12/ν12 vs Vf tiene 2 paneles con 2 curvas cada uno | `test_parametric_g12_nu12_chart` |
| AC-04-03 | El gráfico F1t/F1c vs Vf se genera solo para IM7/8552 | `test_parametric_strength_chart` |
| AC-04-04 | Se calcula Vf_opt para ambos sistemas y se muestra en tabla | `test_optimal_vf` |
| AC-04-05 | Los sliders de Vf validan límites y muestran advertencia si Vf > 0.65 | `test_vf_range_validation` |
