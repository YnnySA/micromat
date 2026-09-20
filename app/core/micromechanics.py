# Implements: specs/08-interfaz-vintage-unificada.md
"""Envoltorios finos sobre las ecuaciones micromecánicas del curso.

Este módulo existe por compatibilidad con la interfaz principal: toda la
física vive en :mod:`core.calculations`, de modo que la vista de resultados y
las páginas de estudio paramétrico / diseño inverso no puedan divergir.
"""

from __future__ import annotations

from .calculations import elastic_from_props, offAxisStiffness, strength_from_props


def elastic_properties_from_sidebar(fiber: dict, matrix: dict, vf: float) -> dict[str, float]:
    """Propiedades elásticas con las entradas del sidebar (E1, E2, G12, nu12, E, nu, G)."""
    return elastic_from_props(fiber, matrix, vf)


def strength_properties_from_sidebar(fiber: dict, matrix: dict, vf: float) -> dict[str, float]:
    """Resistencias con los modelos del curso (F1t, F1c, F1c_rosen, F2t, F2c, F6)."""
    return strength_from_props(fiber, matrix, vf)


def off_axis_stiffness(e1: float, e2: float, g12: float, nu12: float, theta_deg: float) -> float:
    """Calcula Ex(theta) en GPa."""
    return offAxisStiffness(e1, e2, g12, nu12, theta_deg)
