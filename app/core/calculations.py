# Implements: specs/01-visualizacion-resultados.md
# Implements: specs/08-interfaz-vintage-unificada.md
"""Cálculos micromecánicos exclusivos del contenido del curso (U2).

Todas las expresiones provienen de ``U_2/tarea_01.ipynb`` y de las láminas de
``Clase2_U2_updated.pptx``:

* ROM (isodeformación) para ``E1`` y ``nu12``.
* Halpin-Tsai (``xi=2`` para ``E2``, ``xi=1`` para ``G12``).
* Reciprocidad elástica ``nu21 = nu12 * E2 / E1``.
* ``F1t`` por ROM con dominancia de fibra.
* ``F1c`` de Rosen (cota superior) y estimación práctica ``0.575 * F1t``.
* ``F2t``/``F6`` de Barbero con factor geométrico ``eta``.
* ``F2c`` estimación empírica ``4.0 * F2t``.

Los módulos se manejan en GPa y las resistencias en MPa, igual que el notebook.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    DesignResult,
    ElasticProperties,
    MaterialSystem,
    StrengthProperties,
    StrengthProperty,
    ValidationRow,
)
from .materials_db import MATERIALS


class InvalidResultsFileError(ValueError):
    """Indica que un archivo JSON no cumple el contrato de resultados."""


# ---------------------------------------------------------------------------
# Ecuaciones base
# ---------------------------------------------------------------------------

def rom(property_fiber: float, property_matrix: float, vf: float) -> float:
    """Regla de mezclas (isodeformación)."""
    return vf * property_fiber + (1.0 - vf) * property_matrix


def halpin_tsai(property_fiber: float, property_matrix: float, vf: float, xi: float) -> float:
    """Modelo semiempírico de Halpin-Tsai."""
    eta = (property_fiber / property_matrix - 1.0) / (
        property_fiber / property_matrix + xi
    )
    return property_matrix * (1.0 + xi * eta * vf) / (1.0 - eta * vf)


def elastic_from_props(fiber: dict[str, float], matrix: dict[str, float], vf: float) -> dict[str, float]:
    """Propiedades elásticas de la lámina UD a partir de diccionarios normalizados.

    ``fiber`` usa las claves ``E1``, ``E2``, ``G12``, ``nu12`` (GPa).
    ``matrix`` usa ``E``, ``nu``, ``G`` (GPa).
    """
    e1 = rom(fiber["E1"], matrix["E"], vf)
    e2 = halpin_tsai(fiber["E2"], matrix["E"], vf, xi=2.0)
    g12 = halpin_tsai(fiber["G12"], matrix["G"], vf, xi=1.0)
    nu12 = rom(fiber["nu12"], matrix["nu"], vf)
    return {"E1": e1, "E2": e2, "G12": g12, "nu12": nu12, "nu21": nu12 * e2 / e1}


def strength_from_props(fiber: dict[str, float], matrix: dict[str, float], vf: float) -> dict[str, float]:
    """Resistencias de la lámina UD según los modelos del curso (MPa).

    ``fiber`` usa ``F1t`` (resistencia última a tracción, MPa), ``etu`` (deformación
    última, adimensional), ``E2`` y ``G12`` (GPa). ``matrix`` usa ``E``, ``G`` (GPa)
    y ``Ft`` (resistencia a tracción de la matriz, MPa).
    """
    vm = 1.0 - vf
    f1t = vf * fiber["F1t"] + vm * matrix["E"] * 1000.0 * fiber["etu"]
    f1c_rosen = matrix["G"] * 1000.0 / (1.0 - vf)
    f1c = 0.575 * f1t
    eta = math.sqrt(4.0 * vf / math.pi) - vf
    f2t = matrix["Ft"] * (1.0 - eta * (1.0 - matrix["E"] / fiber["E2"]))
    f6 = (matrix["Ft"] / math.sqrt(3.0)) * (
        1.0 - eta * (1.0 - matrix["G"] / fiber["G12"])
    )
    f2c = 4.0 * f2t
    return {
        "F1t": f1t,
        "F1c": f1c,
        "F1c_rosen": f1c_rosen,
        "F2t": f2t,
        "F2c": f2c,
        "F6": f6,
    }


# ---------------------------------------------------------------------------
# Adaptadores sobre MaterialSystem (compatibilidad con specs 01/04/05)
# ---------------------------------------------------------------------------

def _props_from_material(material: MaterialSystem) -> tuple[dict[str, float], dict[str, float]]:
    fiber = {
        "E1": material.fiber["ef1_gpa"],
        "E2": material.fiber["ef2_gpa"],
        "G12": material.fiber["gf12_gpa"],
        "nu12": material.fiber["nu"],
        "F1t": material.fiber["ftu_mpa"],
        "etu": material.fiber["etu"],
        "density": material.fiber["density"],
    }
    matrix = {
        "E": material.matrix["em_gpa"],
        "nu": material.matrix["nu"],
        "G": material.matrix["gm_gpa"],
        "Ft": material.matrix["ftu_mpa"],
        "density": material.matrix["density"],
    }
    return fiber, matrix


def elastic_properties(material: MaterialSystem, vf: float | None = None) -> ElasticProperties:
    vf_value = material.vf_reference if vf is None else vf
    fiber, matrix = _props_from_material(material)
    elastic = elastic_from_props(fiber, matrix, vf_value)
    return ElasticProperties(
        elastic["E1"], elastic["E2"], elastic["G12"], elastic["nu12"], elastic["nu21"]
    )


def strength_properties(material: MaterialSystem, vf: float | None = None) -> StrengthProperties:
    vf_value = material.vf_reference if vf is None else vf
    fiber, matrix = _props_from_material(material)
    strength = strength_from_props(fiber, matrix, vf_value)
    return StrengthProperties(
        f1t=StrengthProperty(strength["F1t"], "ROM con dominancia de fibra", "★★★★★"),
        f1c=StrengthProperty(strength["F1c"], "Estimación práctica 0.575 × F1t", "★★★☆☆"),
        f2t=StrengthProperty(strength["F2t"], "Barbero", "★★☆☆☆"),
        f2c=StrengthProperty(strength["F2c"], "Estimación empírica 4.0 × F2t", "★☆☆☆☆"),
        f6=StrengthProperty(strength["F6"], "Barbero", "★★☆☆☆"),
    )


def validation_rows(material: MaterialSystem) -> list[ValidationRow]:
    elastic = elastic_properties(material)
    strengths = strength_properties(material)
    predicted = {
        "E1": (elastic.e1_gpa, "GPa", "ROM"),
        "E2": (elastic.e2_gpa, "GPa", "Halpin-Tsai"),
        "G12": (elastic.g12_gpa, "GPa", "Halpin-Tsai"),
        "nu12": (elastic.nu12, "adimensional", "ROM"),
        "F1t": (strengths.f1t.value_mpa, "MPa", strengths.f1t.model),
        "F1c": (strengths.f1c.value_mpa, "MPa", strengths.f1c.model),
        "F2t": (strengths.f2t.value_mpa, "MPa", strengths.f2t.model),
        "F2c": (strengths.f2c.value_mpa, "MPa", strengths.f2c.model),
        "F6": (strengths.f6.value_mpa, "MPa", strengths.f6.model),
    }
    rows = []
    for name, experimental in material.experimental.items():
        value, unit, model = predicted[name]
        rows.append(
            ValidationRow(
                name,
                value,
                experimental,
                abs(value - experimental) / experimental * 100.0,
                unit,
                model,
            )
        )
    return rows


def load_results_file(path: str | Path) -> dict[str, Any]:
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidResultsFileError("El archivo de resultados no es un JSON válido.") from exc
    if not isinstance(payload, dict) or "system" not in payload:
        raise InvalidResultsFileError("El archivo debe contener el campo 'system'.")
    if payload["system"] not in MATERIALS:
        raise InvalidResultsFileError("El sistema indicado no está disponible.")
    return payload


def offAxisStiffness(e1: float, e2: float, g12: float, nu12: float, theta_deg: float) -> float:
    """Módulo elástico off-axis Ex(θ) en GPa."""
    import numpy as np

    theta = np.radians(theta_deg)
    c, s = np.cos(theta), np.sin(theta)
    inv_ex = c**4 / e1 + s**4 / e2 + (s * c) ** 2 * (1.0 / g12 - 2.0 * nu12 / e1)
    return 1.0 / inv_ex


def calcProps(fiber: dict, matrix: dict, vf: float) -> dict[str, float]:
    """Calcula propiedades elásticas desde formato sidebar (E1, E2, G12, nu12, E, nu, G)."""
    return elastic_from_props(fiber, matrix, vf)


def result_summary(material: MaterialSystem) -> dict[str, Any]:
    return {
        "system": material.name,
        "vf": material.vf_reference,
        "elastic": asdict(elastic_properties(material)),
        "strength": asdict(strength_properties(material)),
    }


# ---------------------------------------------------------------------------
# SPEC-04: estudio paramétrico
# ---------------------------------------------------------------------------

def parametric_sweep(material: MaterialSystem, vf_min: float, vf_max: float, steps: int = 200) -> dict[str, list[float]]:
    import numpy as np

    vfs = np.linspace(vf_min, vf_max, steps).tolist()

    keys = ("e1", "e2", "e2_rom", "g12", "nu12", "f1t", "f1c", "density", "specific_stiffness")
    series: dict[str, list[float]] = {key: [] for key in keys}

    for vf in vfs:
        elastic = elastic_properties(material, vf)
        series["e1"].append(elastic.e1_gpa)
        series["e2"].append(elastic.e2_gpa)
        series["e2_rom"].append(rom(material.fiber["ef2_gpa"], material.matrix["em_gpa"], vf))
        series["g12"].append(elastic.g12_gpa)
        series["nu12"].append(elastic.nu12)

        strengths = strength_properties(material, vf)
        series["f1t"].append(strengths.f1t.value_mpa)
        series["f1c"].append(strengths.f1c.value_mpa)

        density = vf * material.fiber["density"] + (1.0 - vf) * material.matrix["density"]
        series["density"].append(density)
        series["specific_stiffness"].append((elastic.e1_gpa * 1e6) / density)

    return {"vf": vfs, **series}


def optimal_vf(material: MaterialSystem, vf_min: float, vf_max: float, steps: int = 200) -> tuple[float, float]:
    sweep = parametric_sweep(material, vf_min, vf_max, steps)
    idx = max(range(len(sweep["specific_stiffness"])), key=lambda i: sweep["specific_stiffness"][i])
    return sweep["vf"][idx], sweep["specific_stiffness"][idx]


# ---------------------------------------------------------------------------
# SPEC-05: diseño inverso
# ---------------------------------------------------------------------------

def inverse_design_search(material: MaterialSystem, e1_req_mpa: float, f1t_req_mpa: float, vf_max: float) -> DesignResult:
    import numpy as np

    vfs = np.linspace(0.01, vf_max, 6500)

    for vf in vfs:
        elastic = elastic_properties(material, vf)
        strengths = strength_properties(material, vf)

        e1_mpa = elastic.e1_gpa * 1000.0

        if e1_mpa >= e1_req_mpa and strengths.f1t.value_mpa >= f1t_req_mpa:
            density = vf * material.fiber["density"] + (1.0 - vf) * material.matrix["density"]
            specific_stiffness = e1_mpa / density

            e1_margin = e1_mpa - e1_req_mpa
            f1t_margin = strengths.f1t.value_mpa - f1t_req_mpa
            active = "E1" if e1_margin < f1t_margin else "F1t"

            return DesignResult(
                factible=True,
                vf_min=float(vf),
                e1_at_vf=float(e1_mpa),
                f1t_at_vf=float(strengths.f1t.value_mpa),
                density=float(density),
                specific_stiffness=float(specific_stiffness),
                active_constraint=active,
            )

    return DesignResult(factible=False)
