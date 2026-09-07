# Especificación: Interfaz Limpia y Accesible

> **ID:** SPEC-03
> **Prioridad:** Must
> **Estado:** Propuesta
> **Fuente:** Plan SDD §5.2; `QWEN.md` — convenciones de plotting

## Objetivo

La aplicación debe presentar una interfaz limpia, navegable y pedagógicamente efectiva, donde el estudiante pueda completar el flujo completo (selección → teoría → resultados → interpretación) sin fricción ni sobrecarga cognitiva.

## Alcance

- Navegación por pestañas o sidebar con flujo lineal guiado.
- Layout de dos columnas: teoría + resultados en la misma vista.
- Gráficos con título, ejes etiquetados, unidades, leyenda y grid.
- Mensajes de estado (vacío, cargando, error) claros y accionables.
- Tema visual consistente definido en `.streamlit/config.toml`.
- Paleta de colores limitada y accesible (no depender solo del color).

## Escenarios

Feature: Gestión de interfaz

  Scenario: Navegación principal por pestañas
    Given la aplicación está abierta
    Then se muestra una barra de navegación con las pestañas:
      | "Inicio" | "Resultados" | "Estudio Paramétrico" | "Diseño Inverso" |
    And la pestaña activa por defecto es "Inicio"
    And cada pestaña tiene un ícono o etiqueta descriptiva

  Scenario: Layout de dos columnas en resultados
    Given el usuario está en la pestaña "Resultados"
    Then la página se divide en dos columnas
    And la columna izquierda contiene los selectores y la teoría
    And la columna derecha contiene las tablas de resultados y gráficos
    And en pantallas estrechas, las columnas se apilan verticalmente

  Scenario: Estado vacío inicial
    Given la aplicación está en la pestaña "Resultados"
    And no se ha seleccionado ningún sistema ni ejecutado ningún cálculo
    Then se muestra un mensaje: "Seleccione un sistema de material para comenzar"
    And los contenedores de resultados muestran placeholders vacíos
    And no se muestran tablas con valores cero o por defecto

  Scenario: Gráficos con formato consistente
    Given la aplicación muestra un gráfico de E1 vs Vf
    Then el gráfico tiene título descriptivo
    And el eje X está etiquetado como "Vf [-]" 
    And el eje Y está etiquetado con la propiedad y unidad (ej. "E1 [GPa]")
    And se muestra la leyenda si hay más de una serie
    And se muestra grid con opacidad reducida
    And las líneas de referencia (Vf de referencia) se muestran con línea punteada

  Scenario: Mensaje de error accionable
    Given el usuario está en la pestaña "Estudio Paramétrico"
    When el usuario ingresa un Vf mínimo mayor que el Vf máximo
    Then se muestra un error: "Vf mínimo debe ser menor que Vf máximo"
    And el error aparece junto al control que debe corregirse
    And el botón de ejecución se deshabilita hasta que se corrija el error
    And no se muestra ningún resultado parcial o inválido

  Scenario: Error al cargar configuración de tema (Edge Case)
    Given la aplicación se inicia
    And el archivo `.streamlit/config.toml` está corrupto o mal formado
    When la aplicación carga el tema
    Then se muestra una notificación de error en pantalla
    And la aplicación revierte al tema por defecto para asegurar legibilidad
    And se registra el error en los logs

  Scenario: Indicador de carga durante cálculos
    Given el usuario cambia un parámetro que requiere recálculo
    When los cálculos están en progreso
    Then se muestra un spinner o indicador de progreso
    And los resultados anteriores permanecen visibles (no hay parpadeo)
    And al finalizar, los nuevos resultados reemplazan a los anteriores

## Reglas de presentación

- Usar `st.navigation` para la estructura de páginas.
- No usar `use_container_width` en código nuevo; preferir `width="stretch"`.
- No depender exclusivamente del color para comunicar estados (usar íconos, texto).
- Usar `st.session_state` solo para decisiones de usuario y resultados que deban persistir.
- Usar `@st.cache_data` para cargar datasets inmutables.
- Mantener paleta de colores limitada: máximo 4-5 colores para gráficos.
- Cada gráfico debe guardarse como PNG con nombre descriptivo (según convención QWEN.md).

## Criterios de aceptación

| ID | Criterio | Prueba |
|---|---|---|
| AC-03-01 | La navegación muestra 4 pestañas con nombres descriptivos | `test_navigation_tabs` |
| AC-03-02 | El layout de resultados usa dos columnas en pantalla >= 1200px | `test_two_column_layout` |
| AC-03-03 | El estado vacío muestra mensaje instructivo, no valores cero | `test_empty_state` |
| AC-03-04 | Los gráficos tienen título, ejes etiquetados, unidades y grid | `test_chart_formatting` |
| AC-03-05 | Errores de validación se muestran junto al control que los causa | `test_validation_error_placement` |
| AC-03-06 | El spinner se muestra durante recálculos prolongados | `test_loading_indicator` |
