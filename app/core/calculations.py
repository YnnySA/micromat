# Implements: specs/01-visualizacion-resultados.md
"""Cálculos micromecánicos y carga segura de resultados."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .models import (
    ElasticProperties,
    MaterialSystem,
    StrengthProperties,
    StrengthProperty,
    ValidationRow,
)


class InvalidResultsFileError(ValueError):
    """Indica que un archivo JSON no cumple el contrato de resultados."""


MATERIALS: dict[str, MaterialSystem] = {
    "IM7/8552 (CFRP)": MaterialSystem(
        name="IM7/8552 (CFRP)",
        fiber_name="IM7",
        matrix_name="8552",
        vf_reference=0.60,
        fiber={
            "ef1_gpa": 276.0, "ef2_gpa": 19.0, "gf12_gpa": 27.0,
            "nu": 0.20, "density": 1780.0, "ftu_mpa": 5180.0,
            "etu": 0.0187,
        },
        matrix={
            "em_gpa": 4.67, "gm_gpa": 1.72, "nu": 0.36,
            "density": 1300.0, "ftu_mpa": 121.0,
        },
        experimental={
            "E1": 164.0, "E2": 8.98, "G12": 5.29, "nu12": 0.30,
            "F1t": 2326.0, "F1c": 1200.0, "F2t": 62.3,
            "F2c": 254.0, "F6": 92.0,
        },
        rve={"fibers": 51, "vf_achieved": 0.532, "vf_target": 0.60, "attempts": 100000},
    ),
    "E-glass/Epoxi (GFRP)": MaterialSystem(
        name="E-glass/Epoxi (GFRP)",
        fiber_name="E-glass",
        matrix_name="Epoxi",
        vf_reference=0.55,
        fiber={
            "ef1_gpa": 72.0, "ef2_gpa": 72.0, "gf12_gpa": 29.5,
            "nu": 0.22, "density": 2540.0, "ftu_mpa": 2400.0,
            "etu": 0.034,
        },
        matrix={
            "em_gpa": 3.50, "gm_gpa": 1.28, "nu": 0.38,
            "density": 1200.0, "ftu_mpa": 80.0,
        },
        experimental={"E1": 41.0, "E2": 10.5, "G12": 4.2, "nu12": 0.28},
        rve={"fibers": 8, "vf_achieved": 0.492, "vf_target": 0.55, "attempts": 100000},
    ),
}


def rom(property_fiber: float, property_matrix: float, vf: float) -> float:
    return vf * property_fiber + (1.0 - vf) * property_matrix


def halpin_tsai(property_fiber: float, property_matrix: float, vf: float, xi: float) -> float:
    eta = (property_fiber / property_matrix - 1.0) / (
        property_fiber / property_matrix + xi
    )
    return property_matrix * (1.0 + xi * eta * vf) / (1.0 - eta * vf)


def elastic_properties(material: MaterialSystem, vf: float | None = None) -> ElasticProperties:
    vf_value = material.vf_reference if vf is None else vf
    fiber, matrix = material.fiber, material.matrix
    e1 = rom(fiber["ef1_gpa"], matrix["em_gpa"], vf_value)
    e2 = halpin_tsai(fiber["ef2_gpa"], matrix["em_gpa"], vf_value, xi=2.0)
    g12 = halpin_tsai(fiber["gf12_gpa"], matrix["gm_gpa"], vf_value, xi=1.0)
    nu12 = rom(fiber["nu"], matrix["nu"], vf_value)
    return ElasticProperties(e1, e2, g12, nu12, nu12 * e2 / e1)


def strength_properties(material: MaterialSystem, vf: float | None = None) -> StrengthProperties:
    vf_value = material.vf_reference if vf is None else vf
    fiber, matrix = material.fiber, material.matrix
    f1t = vf_value * fiber["ftu_mpa"] + (1.0 - vf_value) * matrix["em_gpa"] * 1000.0 * fiber["etu"]
    f1c = 0.575 * f1t
    eta = (4.0 * vf_value / 3.141592653589793) ** 0.5 - vf_value
    f2t = matrix["ftu_mpa"] * (1.0 - eta * (1.0 - matrix["em_gpa"] / fiber["ef2_gpa"]))
    f6 = matrix["ftu_mpa"] / (3.0**0.5) * (
        1.0 - eta * (1.0 - matrix["gm_gpa"] / fiber["gf12_gpa"])
    )
    f2c = 4.0 * f2t
    return StrengthProperties(
        f1t=StrengthProperty(f1t, "ROM con dominancia de fibra", "★★★★★"),
        f1c=StrengthProperty(f1c, "Estimación práctica 0.575 × F1t", "★★★☆☆"),
        f2t=StrengthProperty(f2t, "Barbero", "★★☆☆☆"),
        f2c=StrengthProperty(f2c, "Estimación empírica 4.0 × F2t", "★☆☆☆☆"),
        f6=StrengthProperty(f6, "Barbero", "★★☆☆☆"),
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
        rows.append(ValidationRow(name, value, experimental, abs(value - experimental) / experimental * 100.0, unit, model))
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


def result_summary(material: MaterialSystem) -> dict[str, Any]:
    return {
        "system": material.name,
        "vf": material.vf_reference,
        "elastic": asdict(elastic_properties(material)),
        "strength": asdict(strength_properties(material)),
    }


# Implements: specs/04-estudio-parametrico.md

def parametric_sweep(material: MaterialSystem, vf_min: float, vf_max: float, steps: int = 200) -> dict[str, list[float]]:
    import numpy as np
    vfs = np.linspace(vf_min, vf_max, steps).tolist()
    
    e1_list = []
    e2_list = []
    e2_rom_list = []
    g12_list = []
    nu12_list = []
    f1t_list = []
    f1c_list = []
    density_list = []
    specific_stiffness_list = []
    
    for vf in vfs:
        elastic = elastic_properties(material, vf)
        e1_list.append(elastic.e1_gpa)
        e2_list.append(elastic.e2_gpa)
        
        e2_rom = rom(material.fiber["ef2_gpa"], material.matrix["em_gpa"], vf)
        e2_rom_list.append(e2_rom)
        
        g12_list.append(elastic.g12_gpa)
        nu12_list.append(elastic.nu12)
        
        strengths = strength_properties(material, vf)
        f1t_list.append(strengths.f1t.value_mpa)
        f1c_list.append(strengths.f1c.value_mpa)
        
        density = vf * material.fiber["density"] + (1.0 - vf) * material.matrix["density"]
        density_list.append(density)
        
        specific_stiffness = (elastic.e1_gpa * 1e6) / density
        specific_stiffness_list.append(specific_stiffness)
        
    return {
        "vf": vfs,
        "e1": e1_list,
        "e2": e2_list,
        "e2_rom": e2_rom_list,
        "g12": g12_list,
        "nu12": nu12_list,
        "f1t": f1t_list,
        "f1c": f1c_list,
        "density": density_list,
        "specific_stiffness": specific_stiffness_list,
    }


def optimal_vf(material: MaterialSystem, vf_min: float, vf_max: float, steps: int = 200) -> tuple[float, float]:
    sweep = parametric_sweep(material, vf_min, vf_max, steps)
    idx = max(range(len(sweep["specific_stiffness"])), key=lambda i: sweep["specific_stiffness"][i])
    return sweep["vf"][idx], sweep["specific_stiffness"][idx]

