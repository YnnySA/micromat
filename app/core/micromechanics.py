"""Ecuaciones micromecánicas usadas por la interfaz principal."""

from __future__ import annotations

import numpy as np

from .calculations import halpin_tsai, rom


def elastic_properties_from_sidebar(fiber: dict, matrix: dict, vf: float) -> dict[str, float]:
    """Calcula las propiedades elásticas con las entradas del sidebar."""
    e1 = rom(fiber["E1"], matrix["E"], vf)
    e2 = halpin_tsai(fiber["E2"], matrix["E"], vf, xi=2.0)
    g12 = halpin_tsai(fiber["G12"], matrix["G"], vf, xi=1.0)
    nu12 = rom(fiber["nu12"], matrix["nu"], vf)
    return {"E1": e1, "E2": e2, "G12": g12, "nu12": nu12, "nu21": nu12 * e2 / e1}


def strength_properties_from_sidebar(fiber: dict, matrix: dict, vf: float) -> dict[str, float]:
    """Calcula las resistencias con los modelos definidos en SPEC-UI-01."""
    e2 = halpin_tsai(fiber["E2"], matrix["E"], vf, xi=2.0)
    g12 = halpin_tsai(fiber["G12"], matrix["G"], vf, xi=1.0)
    vm = 1.0 - vf
    f1t = fiber["F1t"] * vf + matrix["Ft"] * vm
    f1c = fiber["F1c"] * vf + matrix["Fc"] * vm
    eta = vf ** (1.0 / 3.0)
    f2t = matrix["Ft"] * (1.0 - eta * (1.0 - matrix["E"] / e2))
    f2c = matrix["Fc"] * (1.0 - eta * (1.0 - matrix["E"] / e2))
    f12s = matrix["Fs"] * (1.0 - (eta - vf) * (1.0 - matrix["G"] / g12))
    return {"F1t": f1t, "F1c": f1c, "F2t": f2t, "F2c": f2c, "F12s": f12s}


def off_axis_stiffness(e1: float, e2: float, g12: float, nu12: float, theta_deg: float) -> float:
    """Calcula Ex(theta) en GPa."""
    theta = np.radians(theta_deg)
    c, s = np.cos(theta), np.sin(theta)
    inverse_ex = c**4 / e1 + s**4 / e2 + (s * c) ** 2 * (1.0 / g12 - 2.0 * nu12 / e1)
    return float(1.0 / inverse_ex)
