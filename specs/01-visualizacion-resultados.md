# Especificación: Visualización de Resultados

> **ID:** SPEC-01
> **Prioridad:** Must
> **Estado:** Propuesta
> **Fuente:** `tarea_01.ipynb` — Partes A1, A3, B

## Objetivo

El estudiante debe poder visualizar, para cada sistema de material compuesto (IM7/8552 y E-glass/Epoxi), las propiedades elásticas y de resistencia calculadas por los modelos micromecánicos, junto con su validación frente a valores experimentales de referencia.

## Alcance

- Selección de sistema de material (IM7/8552 o E-glass/Epoxi).
- Cálculo automático de propiedades elásticas (E1, E2, G12, ν12, ν21) mediante ROM y Halpin-Tsai.
- Cálculo automático de resistencias (F1t, F1c, F2t, F2c, F6) mediante modelos micromecánicos.
- Visualización tabular de resultados con unidades.
- Comparación con valores experimentales de referencia (Barbero 2011, Apéndice A) y error porcentual.

## Escenarios

### Scenario: Visualizar propiedades elásticas de un sistema

```gherkin
Given la aplicación está abierta en la vista "Resultados"
And el sistema seleccionado es "IM7/8552 (CFRP)"
And la fracción volumétrica de fibra es 0.60
When se cargan los resultados de propiedades elásticas
Then se muestra una tabla con E1, E2, G12, ν12 y ν21
And cada propiedad muestra su valor numérico y unidad (GPa o adimensional)
And E1 se calcula con ROM
And E2 y G12 se calculan con Halpin-Tsai
And ν21 se obtiene por reciprocidad elástica
```

### Scenario: Visualizar propiedades de resistencia de un sistema

```gherkin
Given la aplicación está abierta en la vista "Resultados"
And el sistema seleccionado es "IM7/8552 (CFRP)"
And la fracción volumétrica de fibra es 0.60
When se cargan los resultados de resistencia
Then se muestra una tabla con F1t, F1c, F2t, F2c, F6
And cada propiedad muestra su valor en MPa
And se indica el modelo utilizado para cada estimación
And se muestra un indicador de confiabilidad por modelo (★☆☆☆☆ a ★★★★★)
```

### Scenario: Validar resultados contra valores experimentales

```gherkin
Given la aplicación está en la vista "Resultados"
And el sistema seleccionado es "IM7/8552 (CFRP)"
When se activa la opción "Comparar con valores experimentales"
Then se muestra una tabla de validación con columnas: Propiedad, Predicho, Experimental, Error %
And el error se calcula como |predicho - experimental| / experimental × 100
And las propiedades con error > 20% se resaltan visualmente
And se muestra una nota sobre la confiabilidad de cada modelo
```

### Scenario: Cambiar entre sistemas de material

```gherkin
Given la aplicación muestra resultados del sistema "IM7/8552 (CFRP)"
When el usuario selecciona "E-glass/Epoxi (GFRP)" en el selector de sistema
Then los resultados se actualizan automáticamente
And se muestran las propiedades correspondientes al nuevo sistema
And la tabla de validación solo muestra propiedades con datos experimentales disponibles
```

### Scenario: Visualizar RVE del sistema seleccionado

```gherkin
Given la aplicación está en la vista "Resultados"
And el sistema seleccionado es "IM7/8552 (CFRP)"
When se despliega la sección "Visualización RVE"
Then se muestra una imagen del RVE generado por RSA
And se indica el número de fibras colocadas
And se indica la fracción volumétrica lograda vs. la objetivo
And se indica el número de intentos de colocación
```

### Scenario: Rechazar archivo de resultados inválido

```gherkin
Given la aplicación está abierta en la vista "Resultados"
When el usuario carga un archivo JSON de resultados con formato inválido
Then se muestra un mensaje de error identificable para el usuario
And no se reemplazan los resultados calculados actualmente
```

## Reglas de dominio

- **ROM** se aplica a E1 y ν12. Fórmula: E1 = Vf·Ef1 + (1−Vf)·Em.
- **Halpin-Tsai** se aplica a E2 (ξ=2) y G12 (ξ=1).
- **ν21** = ν12 · E2 / E1 (reciprocidad, no es constante independiente).
- **F1t** se calcula por ROM con dominancia de fibra.
- **F1c** práctico = 0.575 × F1t (Rosen es cota superior, no se usa como valor nominal).
- **F2t** y **F6** se calculan con el modelo de Barbero (factor geométrico η).
- **F2c** = 4.0 × F2t (estimación empírica).
- Los cálculos internos se realizan en MPa; las tablas convierten a GPa donde corresponde.

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-01-01 | El selector de sistema muestra ambas opciones y actualiza resultados | `test_ui_system_selector` |
| AC-01-02 | La tabla de propiedades elásticas muestra 5 filas con valor y unidad | `test_elastic_properties_table` |
| AC-01-03 | La tabla de resistencias muestra 5 filas con valor en MPa y modelo | `test_strength_properties_table` |
| AC-01-04 | La tabla de validación muestra error % correcto para al menos 4 propiedades | `test_validation_table` |
| AC-01-05 | El RVE se renderiza como imagen con Vf logrado vs objetivo | `test_rve_display` |
| AC-01-06 | Un archivo JSON inválido muestra un error y conserva los resultados actuales | `test_invalid_results_file` |