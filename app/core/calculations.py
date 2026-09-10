# Implements: specs/01-visualizacion-resultados.md
"""Cálculos micromecánicos y carga segura de resultados."""

from __future__ import annotations

import json
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


def offAxisStiffness(e1: float, e2: float, g12: float, nu12: float, theta_deg: float) -> float:
    """Módulo elástico off-axis Ex(θ) en GPa."""
    import numpy as np
    theta = np.radians(theta_deg)
    c, s = np.cos(theta), np.sin(theta)
    inv_ex = c**4 / e1 + s**4 / e2 + (s * c)**2 * (1.0 / g12 - 2.0 * nu12 / e1)
    return 1.0 / inv_ex


def calcProps(fiber: dict, matrix: dict, vf: float) -> dict[str, float]:
    """Calcula propiedades elásticas desde formato sidebar_inputs (E1, E2, G12, nu12, E, nu, G)."""
    e1 = rom(fiber["E1"], matrix["E"], vf)
    e2 = halpin_tsai(fiber["E2"], matrix["E"], vf, xi=2.0)
    g12 = halpin_tsai(fiber["G12"], matrix["G"], vf, xi=1.0)
    nu12 = rom(fiber["nu12"], matrix["nu"], vf)
    return {"E1": e1, "E2": e2, "G12": g12, "nu12": nu12}


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


# Implements: specs/05-diseno-inverso.md

def inverse_design_search(material: MaterialSystem, e1_req_mpa: float, f1t_req_mpa: float, vf_max: float) -> DesignResult:
    import numpy as np
    
    # Rango dinámico 0.01 a vf_max
    vfs = np.linspace(0.01, vf_max, 6500)
    
    for vf in vfs:
        elastic = elastic_properties(material, vf)
        strengths = strength_properties(material, vf)
        
        # Convertir E1 a MPa para comparar con req
        e1_mpa = elastic.e1_gpa * 1000.0
        
        if e1_mpa >= e1_req_mpa and strengths.f1t.value_mpa >= f1t_req_mpa:
            density = vf * material.fiber["density"] + (1.0 - vf) * material.matrix["density"]
            specific_stiffness = (e1_mpa) / density
            
            # Identificar restricción activa
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
                active_constraint=active
            )
            
    return DesignResult(factible=False)
