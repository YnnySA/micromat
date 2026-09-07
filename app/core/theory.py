# Implements: specs/02-espacio-teoria-analisis.md
"""Contenido teórico versionado para la vista de resultados."""

from __future__ import annotations

from dataclasses import dataclass


class TheoryUnavailableError(LookupError):
    """Indica que una sección teórica no está disponible."""


@dataclass(frozen=True)
class TheorySection:
    key: str
    title: str
    definition: str
    formulas: tuple[str, ...]
    details: tuple[str, ...]
    properties: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReliabilityNote:
    model: str
    properties: str
    reliability: str
    limitation: str


THEORY_SECTIONS: dict[str, TheorySection] = {
    "rom": TheorySection(
        "rom", "Teoría: Regla de Mezclas (ROM)",
        "La ROM supone isodeformación: fibra y matriz comparten la misma deformación en la dirección 1.",
        (r"E_1 = V_f E_{f1} + V_m E_m,\quad V_m = 1 - V_f", r"\nu_{12} = V_f \nu_f + V_m \nu_m"),
        ("En esta aplicación ROM se usa para E1 y nu12.", "Es más adecuada para la dirección longitudinal que para la transversal."),
        ("E1", "nu12"),
    ),
    "halpin_tsai": TheorySection(
        "halpin_tsai", "Teoría: Halpin-Tsai",
        "Halpin-Tsai representa la transferencia de carga transversal mediante los factores xi y eta.",
        (r"P = P_m\frac{1+\xi\eta V_f}{1-\eta V_f}", r"\eta = \frac{P_f/P_m - 1}{P_f/P_m + \xi}"),
        ("xi incorpora geometría, orientación y modo de carga.", "Se adopta xi=2 para E2 y xi=1 para G12.", "Para E2, Halpin-Tsai representa mejor la respuesta transversal que ROM."),
        ("E2 (xi=2)", "G12 (xi=1)"),
    ),
    "barbero": TheorySection(
        "barbero", "Teoría: Barbero",
        "Las estimaciones de Barbero para resistencia transversal y cortante incorporan un factor geométrico eta.",
        (r"\eta = \sqrt{\frac{4V_f}{\pi}} - V_f", r"F_{2t} = F_{mt}\left[1-\eta\left(1-\frac{E_m}{E_{f2}}\right)\right]", r"F_6 = \frac{F_{mt}}{\sqrt{3}}\left[1-\eta\left(1-\frac{G_m}{G_{f12}}\right)\right]"),
        ("Son estimaciones de prediseño y requieren validación experimental.", "eta resume un efecto geométrico simplificado de la distribución de fibras."),
        ("F2t", "F6"),
    ),
    "rosen": TheorySection(
        "rosen", "Teoría: Rosen",
        "Rosen se interpreta como una cota superior para la resistencia longitudinal a compresión por micro pandeo.",
        (r"F_{1c,\mathrm{Rosen}} \text{ es una cota superior}", r"F_{1c,\mathrm{práctico}} = 0.575F_{1t}"),
        ("Rosen no se usa como valor nominal en la validación.", "La estimación práctica también debe contrastarse con ensayos."),
        ("F1c",),
    ),
}


RELIABILITY_NOTES = (
    ReliabilityNote("ROM", "F1t", "★★★★★", "Alta confiabilidad para dominancia longitudinal de la fibra."),
    ReliabilityNote("ROM", "E1, nu12", "★★★★☆", "Supone isodeformación."),
    ReliabilityNote("Rosen", "F1c", "★★★☆☆", "Entrega una cota superior, no un valor nominal."),
    ReliabilityNote("Barbero", "F2t, F6", "★★☆☆☆", "Estimación simplificada sensible a la microestructura."),
    ReliabilityNote("Empírico", "F2c", "★☆☆☆☆", "F2c=4F2t requiere validación experimental."),
)


def get_theory_section(key: str) -> TheorySection:
    try:
        return THEORY_SECTIONS[key]
    except KeyError as exc:
        raise TheoryUnavailableError("Información teórica no disponible temporalmente") from exc


def interpretation_for_system(system_name: str) -> tuple[str, ...]:
    if "IM7/8552" in system_name:
        return (
            "E1 es mayor en CFRP porque la fibra IM7 tiene un módulo longitudinal muy superior al de la matriz 8552.",
            "E2 puede ser mayor en GFRP porque la fibra de vidrio se aproxima a un comportamiento isotrópico y conserva un módulo transversal alto.",
            "La diferencia entre ROM y Halpin-Tsai para E2 refleja que la transferencia transversal no sigue la hipótesis ideal de isodeformación.",
            "E1, E2, G12 y nu12 alimentan la matriz Q; al transformar los ejes se obtiene Qbar y, por inversión, S.",
        )
    if "E-glass/Epoxi" in system_name:
        return (
            "E1 es menor que en CFRP porque el módulo longitudinal de la fibra de vidrio es menor que el de IM7.",
            "E2 puede superar al de CFRP debido al módulo transversal elevado de la fibra de vidrio.",
            "Halpin-Tsai modera la estimación de E2 respecto de una interpolación ROM lineal.",
            "Las propiedades de la lámina se emplean para construir Q, Qbar y S en el análisis anisótropo de U3.",
        )
    return ("No existe una interpretación específica para el sistema seleccionado.",)


def theory_section_keys() -> tuple[str, ...]:
    return tuple(THEORY_SECTIONS)
