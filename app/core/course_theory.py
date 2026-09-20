# Implements: specs/09-teoria-curso.md
"""Contenido teórico del curso U1 + U2 para la pestaña "Teoría".

Fuentes exclusivas:
* ``U_1/U1_Introduccion_DAMC.pptx`` — motivación, constituyentes y enfoque.
* ``U_2/Clase2_U2_updated.md`` — fundamentos de micromecánica y modelos.

No incluye material de U3 ni de otras unidades.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TheoryBlock:
    key: str
    title: str
    paragraphs: tuple[str, ...] = ()
    bullets: tuple[str, ...] = ()
    formulas: tuple[tuple[str, str], ...] = ()
    notes: tuple[str, ...] = ()


COURSE_THEORY: tuple[TheoryBlock, ...] = (
    TheoryBlock(
        key="porque",
        title="1. ¿Por qué predecir desde los constituyentes?",
        paragraphs=(
            "El eje del curso (U1) es **predecir → diseñar → validar**: predecir las propiedades "
            "mecánicas de un laminado a partir de sus constituyentes, analizar tensiones y falla, "
            "diseñar la secuencia de apilado y validar contra datos experimentales.",
            "Medir todas las propiedades de una lámina UD nueva exige decenas de ensayos y probetas. "
            "La micromecánica (U2) reduce ese costo a conocer las propiedades de los constituyentes "
            "(E_f1, E_f2, G_f12, ν_f12, E_m, ν_m) y la fracción volumétrica Vf.",
        ),
        bullets=(
            "**Reducir ensayos:** estimar las 9 propiedades de la lámina desde constituyentes + Vf.",
            "**Explorar el espacio de diseño:** simular miles de combinaciones fibra/matriz/Vf antes de fabricar.",
            "**Entender qué falla primero:** identificar el constituyente o interfaz débil según el modo de carga.",
        ),
    ),
    TheoryBlock(
        key="definicion",
        title="2. ¿Qué es un material compuesto? (U1)",
        paragraphs=(
            "**Definición:** material formado por la unión de dos o más componentes, que produce "
            "propiedades o combinaciones de propiedades no alcanzables por ninguno de sus "
            "constituyentes de forma aislada.",
        ),
        bullets=(
            "**Separabilidad física:** dos o más fases distinguibles y separables mecánicamente; la interfase es un componente propio.",
            "**Inmiscibilidad química:** fases distintas e insolubles entre sí (las aleaciones metálicas no son MC).",
            "**Sinergia mecánica:** el conjunto supera la simple suma de los constituyentes.",
            "**Fibra:** soporta la carga; aporta rigidez, resistencia y direccionalidad.",
            "**Matriz:** une y protege las fibras, transfiere carga y define forma, temperatura y resistencia química.",
            "**Interfase:** controla la transferencia de carga y los modos de falla (despegue, pull-out, delaminación).",
        ),
        notes=(
            "El curso se enfoca en PMC termoestables (epoxi/fibra de carbono y epoxi/fibra de vidrio) "
            "por su prevalencia industrial y disponibilidad experimental.",
        ),
    ),
    TheoryBlock(
        key="anisotropia",
        title="3. Anisotropía y grados de libertad de diseño (U1)",
        paragraphs=(
            "A diferencia de un metal isótropo, una lámina UD es heterogénea y **anisótropa**: sus "
            "propiedades cambian con la dirección (E₁ ≫ E₂). La anisotropía no se corrige: se usa.",
        ),
        bullets=(
            "**Sistema fibra + matriz:** CF/epoxi (alta rigidez y bajo peso), GF/epoxi (menor costo, buena fatiga).",
            "**Fracción volumétrica Vf:** controla E₁, resistencia y densidad; típico 45–65 %.",
            "**Orientación θᵢ:** 0° máxima rigidez longitudinal, ±45° máxima resistencia a cortante, 90° rigidez transversal.",
            "**Secuencia de apilado [θ₁/…/θₙ]ₛ:** simétrico evita acoplamiento, balanceado evita A₁₆/A₂₆.",
        ),
    ),
    TheoryBlock(
        key="lamina",
        title="4. La lámina UD y sus 9 propiedades",
        paragraphs=(
            "La lámina unidireccional (UD) es el elemento básico del laminado. En estado plano "
            "(σ₃ ≈ 0) es ortótropa y queda caracterizada por **4 constantes elásticas** y "
            "**5 resistencias independientes**.",
        ),
        bullets=(
            "**E₁** — rigidez en la dirección de la fibra; domina la fibra.",
            "**E₂** — rigidez transversal; domina la matriz.",
            "**ν₁₂** — contracción transversal bajo tracción longitudinal (≈ 0.25–0.35).",
            "**G₁₂** — rigidez a la distorsión angular en el plano; domina la matriz.",
            "**F₁ₜ** — tracción longitudinal (fibra).",
            "**F₁c** — compresión longitudinal (fibra + matriz, microbuckling).",
            "**F₂ₜ** — tracción transversal (matriz/interfaz).",
            "**F₂c** — compresión transversal (matriz/interfaz, cortante a 45°).",
            "**F₆** — corte en plano (matriz/interfaz; ensayo Iosipescu o V-notch).",
        ),
    ),
    TheoryBlock(
        key="vf_rve",
        title="5. Fracciones volumétricas y VRE",
        paragraphs=(
            "La fracción volumétrica de fibra es la variable de diseño fundamental. El VRE "
            "(Volumen Representativo Elemental) es la celda más pequeña que conserva la "
            "información estadística del compuesto.",
        ),
        bullets=(
            "Diseño típico de Vf: 0.50 – 0.65; se busca Vv (vacíos) < 1 %.",
            "Vacíos > 2 % degradan fuertemente F₂ₜ y F₆.",
            "Empaquetamiento cuadrado: modelo simple, sobreestima E₂ y G₁₂.",
            "Empaquetamiento hexagonal: mejor geometría; Vf máximo teórico 0.907.",
            "Distribución real: aleatoria, como en las micrografías.",
        ),
        formulas=(
            ("Balance de fracciones volumétricas", r"V_f + V_m + V_v = 1"),
        ),
    ),
    TheoryBlock(
        key="rom",
        title="6. Regla de Mezclas (RdM)",
        paragraphs=(
            "La RdM combina las propiedades de fibra y matriz según el modo de carga: **isostrain** "
            "(deformación uniforme, carga longitudinal) o **isostress** (esfuerzo uniforme, carga "
            "transversal). Es exacta para E₁ y buena para ν₁₂; subestima E₂ y G₁₂.",
        ),
        formulas=(
            ("Isostrain — módulo longitudinal", r"E_1 = V_f\,E_{f1} + V_m\,E_m"),
            ("Isostrain — razón de Poisson", r"\nu_{12} = V_f\,\nu_f + V_m\,\nu_m"),
            ("Isostress — módulo transversal", r"\frac{1}{E_2} = \frac{V_f}{E_{f2}} + \frac{V_m}{E_m}"),
            ("Isostress — módulo de corte", r"\frac{1}{G_{12}} = \frac{V_f}{G_{f12}} + \frac{V_m}{G_m}"),
        ),
        notes=(
            "Limitación (U2): la RdM subestima E₂ un 20–30 % y G₁₂ un 30–40 %; "
            "no describe la geometría cilíndrica de la fibra ni la concentración de esfuerzos.",
        ),
    ),
    TheoryBlock(
        key="halpin",
        title="7. Halpin-Tsai (HT)",
        paragraphs=(
            "Modelo semiempírico que incorpora la geometría del refuerzo mediante el parámetro ξ. "
            "ξ → ∞ recupera la RdM paralelo (cota superior) y ξ → 0 la RdM serie (cota inferior).",
        ),
        formulas=(
            ("Ecuación general", r"\frac{P}{P_m} = \frac{1 + \xi\,\eta\,V_f}{1 - \eta\,V_f}"),
            ("Parámetro de refuerzo", r"\eta = \frac{P_f/P_m - 1}{P_f/P_m + \xi}"),
        ),
        bullets=(
            "**E₂:** ξ = 2 (inclusión cilíndrica/circular).",
            "**G₁₂:** ξ = 1 (elipsoide de relación de aspecto unitaria en corte).",
            "**ν₂₃:** ξ = 0 (recupera la RdM serie).",
        ),
    ),
    TheoryBlock(
        key="reciprocidad",
        title="8. Reciprocidad elástica (ν₂₁)",
        paragraphs=(
            "ν₂₁ no es una constante independiente: se obtiene por reciprocidad a partir de "
            "ν₁₂, E₂ y E₁.",
        ),
        formulas=(
            ("Reciprocidad", r"\nu_{21} = \nu_{12}\,\frac{E_2}{E_1}"),
        ),
    ),
    TheoryBlock(
        key="resistencias",
        title="9. Resistencias de la lámina UD",
        paragraphs=(
            "A diferencia de las propiedades elásticas, las resistencias son difíciles de predecir "
            "desde micromecánica: dependen de la interfaz, los defectos y el proceso.",
        ),
        formulas=(
            ("F₁ₜ — ROM con dominancia de fibra", r"F_{1t} \approx V_f\,F_f^{u} + V_m\,\sigma_m(\varepsilon_f^{u})"),
            ("F₁c — Rosen (cota superior)", r"F_{1c,\mathrm{Rosen}} = \frac{G_m}{1 - V_f}"),
            ("F₁c — regla práctica", r"F_{1c} \approx (0.50\ \text{a}\ 0.65)\,F_{1t}"),
            ("Barbero — factor geométrico", r"\eta = \sqrt{\frac{4V_f}{\pi}} - V_f"),
            ("F₂ₜ — Barbero", r"F_{2t} = F_{tu,m}\left[1 - \eta\left(1 - \frac{E_m}{E_{f2}}\right)\right]"),
            ("F₆ — Barbero", r"F_6 = \frac{F_{tu,m}}{\sqrt{3}}\left[1 - \eta\left(1 - \frac{G_m}{G_{f12}}\right)\right]"),
            ("F₂c — estimación empírica", r"F_{2c} \approx (3.5\ \text{a}\ 4.5)\,F_{2t}"),
            ("Regla del 10 % (solo orden de magnitud)", r"F_{2t} \approx F_6 \approx 0.10\,F_{1t}"),
        ),
        notes=(
            "La regla del 10 % sobreestima gravemente F₂t y F₆ en carbono/epoxi; nunca debe usarse "
            "para cálculo final. En esta aplicación se adopta F₁c = 0.575·F₁t y F₂c = 4·F₂t.",
        ),
    ),
    TheoryBlock(
        key="confiabilidad",
        title="10. Confiabilidad y limitaciones",
        paragraphs=(
            "Todos los modelos son aproximaciones. Un buen ingeniero conoce sus límites y valida "
            "con datos experimentales. La ventaja real de Mori-Tanaka está en el plano transversal "
            "2–3 (K₂₃, G₂₃, ν₂₃), no en E₁, E₂, G₁₂ o ν₁₂.",
        ),
        formulas=(
            ("Mori-Tanaka — compresibilidad planar", r"K_{23} = \frac{E_2}{2(1-\nu_{23})}"),
        ),
    ),
)


# Propiedades elásticas y de resistencia: modelo y fórmula usados en la app.
MODEL_MAP: tuple[tuple[str, str, str], ...] = (
    ("E₁", "Regla de Mezclas (isostrain)", r"E_1 = V_f\,E_{f1} + V_m\,E_m"),
    ("E₂", "Halpin-Tsai (ξ = 2)", r"E_2 = E_m\frac{1 + 2\eta V_f}{1 - \eta V_f}"),
    ("G₁₂", "Halpin-Tsai (ξ = 1)", r"G_{12} = G_m\frac{1 + \eta V_f}{1 - \eta V_f}"),
    ("ν₁₂", "Regla de Mezclas", r"\nu_{12} = V_f\,\nu_f + V_m\,\nu_m"),
    ("ν₂₁", "Reciprocidad elástica", r"\nu_{21} = \nu_{12}\,E_2/E_1"),
    ("F₁ₜ", "ROM con dominancia de fibra", r"F_{1t} = V_f F_f^{u} + V_m E_m \varepsilon_f^{u}"),
    ("F₁c", "Rosen + práctica 0.575·F₁ₜ", r"F_{1c} = 0.575\,F_{1t}"),
    ("F₂ₜ", "Barbero", r"F_{2t} = F_{tu,m}[1 - \eta(1 - E_m/E_{f2})]"),
    ("F₆", "Barbero", r"F_6 = (F_{tu,m}/\sqrt{3})[1 - \eta(1 - G_m/G_{f12})]"),
    ("F₂c", "Estimación empírica 4·F₂ₜ", r"F_{2c} = 4\,F_{2t}"),
)


# Confiabilidad de los modelos de resistencia (U2).
RELIABILITY: tuple[tuple[str, str, str, str], ...] = (
    ("F₁ₜ", "RdM (fibra dominante)", "★★★★☆", "Aceptable; sobreestima levemente por dispersión estadística."),
    ("F₁c", "Microbuckling (Rosen)", "★★☆☆☆", "Sobreestima hasta 100 %; Barbero corrige parcialmente."),
    ("F₂ₜ", "Ninguno confiable", "★☆☆☆☆", "Depende de la interfaz fibra-matriz y del proceso. Se mide."),
    ("F₂c", "Ninguno confiable", "★☆☆☆☆", "Dominada por la matriz y concentradores de esfuerzo. Se mide."),
    ("F₆", "Ninguno confiable", "★☆☆☆☆", "Matriz + interfaz; ensayo Iosipescu o V-notch."),
)


def theory_keys() -> tuple[str, ...]:
    return tuple(block.key for block in COURSE_THEORY)
