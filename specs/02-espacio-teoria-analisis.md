# Especificación: Espacio de Teoría y Análisis

> **ID:** SPEC-02
> **Prioridad:** Must
> **Estado:** Propuesta
> **Fuente:** `tarea_01.ipynb` — Celdas Markdown teóricas; `Informe.md` — Marco teórico

## Objetivo

El estudiante debe tener acceso a explicaciones teóricas contextualizadas junto a los resultados, de modo que pueda relacionar cada valor calculado con el modelo micromecánico que lo produce y con el concepto físico subyacente.

## Alcance

- Panel de teoría colapsable/expandible junto a la vista de resultados.
- Definiciones de los modelos: ROM, Halpin-Tsai, reciprocidad elástica.
- Fórmulas renderizadas para cada propiedad calculada.
- Explicación de los factores de refuerzo (ξ) y del factor geométrico (η).
- Notas sobre confiabilidad y limitaciones de cada modelo.
- Conexión conceptual con la elasticidad anisótropa (U3): matriz Q, Qbar, S.

## Escenarios

Feature: Consultar teoría y resultados

  Scenario: Consultar teoría de un modelo específico
    Given la aplicación está en la vista "Resultados"
    And se muestran las propiedades elásticas del sistema IM7/8552
    When el usuario expande la sección "Teoría: Regla de Mezclas (ROM)"
    Then se muestra la definición del modelo ROM
    And se muestra la fórmula E1 = Vf·Ef1 + Vm·Em
    And se indica que ROM asume isodeformación entre fibra y matriz
    And se lista qué propiedades se calculan con este modelo (E1, ν12)

  Scenario: Consultar teoría de Halpin-Tsai
    Given la aplicación está en la vista "Resultados"
    When el usuario expande la sección "Teoría: Halpin-Tsai"
    Then se muestra la fórmula general P = Pm·(1 + ξ·η·Vf) / (1 − η·Vf)
    And se explica el significado del factor de refuerzo ξ
    And se indica ξ=2 para E2 y ξ=1 para G12
    And se compara con ROM para E2, mostrando cuándo cada modelo es aplicable

  Scenario: Ver interpretación de resultados
    Given la aplicación muestra los resultados de propiedades elásticas
    When el usuario despliega la sección "Interpretación"
    Then se muestra un texto que explica por qué E1 es mayor en CFRP que en GFRP
    And se explica por qué E2 puede ser mayor en GFRP (fibra isotrópica)
    And se menciona la diferencia entre ROM y Halpin-Tsai para E2
    And se conecta con la matriz Q de rigidez reducida (U3)

  Scenario: Ver notas de confiabilidad de modelos de resistencia
    Given la aplicación muestra los resultados de resistencia
    When el usuario expande la sección "Confiabilidad de modelos"
    Then se muestra una tabla con: Modelo, Propiedades, Confiabilidad, Limitación
    And ROM para F1t muestra confiabilidad alta (★★★★★)
    And Rosen para F1c muestra que es cota superior, no valor nominal
    And Barbero para F2t/F6 muestra confiabilidad baja (★★☆☆☆)
    And F2c empírico muestra que requiere validación experimental

  Scenario: Navegar entre teoría y resultados sin perder contexto
    Given la aplicación está en la vista "Resultados"
    And el usuario tiene expandida la sección "Teoría: Halpin-Tsai"
    When el usuario cambia el sistema de "IM7/8552" a "E-glass/Epoxi"
    Then la sección de teoría permanece expandida
    And los resultados se actualizan al nuevo sistema
    And las fórmulas mostradas en teoría son genéricas (no dependen del sistema)

  Scenario: Error al intentar cargar teoría inexistente
    Given la aplicación está en la vista "Resultados"
    When el usuario solicita una sección teórica que no ha sido cargada
    Then se muestra un mensaje: "Información teórica no disponible temporalmente"
    And se ofrece un botón "Reintentar carga"

## Reglas de dominio

- El contenido teórico debe estar versionado y centralizado (no hardcodeado en la UI).
- Las fórmulas deben renderizarse con notación matemática (LaTeX via st.latex o similar).
- Cada modelo debe vincularse explícitamente con las propiedades que calcula.
- La interpretación debe ser específica al sistema seleccionado, no genérica.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-02-01 | Existen secciones expandibles para ROM, Halpin-Tsai, Barbero y Rosen | `test_theory_sections_exist` |
| AC-02-02 | Cada sección de teoría contiene al menos una fórmula renderizada | `test_theory_contains_formulas` |
| AC-02-03 | La interpretación cambia según el sistema seleccionado | `test_interpretation_contextual` |
| AC-02-04 | La tabla de confiabilidad lista al menos 4 modelos con estrellas | `test_reliability_table` |
| AC-02-05 | La sección de teoría no se colapsa al cambiar de sistema | `test_theory_persistence` |
| AC-02-06 | Una sección teórica no disponible muestra el mensaje requerido y permite reintentar | `test_missing_theory_section` |
