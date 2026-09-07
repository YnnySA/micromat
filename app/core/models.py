# Implements: specs/01-visualizacion-resultados.md
"""Modelos de dominio para la visualización de resultados micromecánicos."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class MaterialSystem:
    name: str
    fiber_name: str
    matrix_name: str
    vf_reference: float
    fiber: dict[str, float]
    matrix: dict[str, float]
    experimental: dict[str, float]
    rve: dict[str, Any]


@dataclass(frozen=True)
class ElasticProperties:
    e1_gpa: float
    e2_gpa: float
    g12_gpa: float
    nu12: float
    nu21: float


@dataclass(frozen=True)
class StrengthProperty:
    value_mpa: float
    model: str
    reliability: str


@dataclass(frozen=True)
class StrengthProperties:
    f1t: StrengthProperty
    f1c: StrengthProperty
    f2t: StrengthProperty
    f2c: StrengthProperty
    f6: StrengthProperty


@dataclass(frozen=True)
class ValidationRow:
    property_name: str
    predicted: float
    experimental: float
    error_percent: float
    unit: str
    model: str

    @property
    def exceeds_twenty_percent(self) -> bool:
        return self.error_percent > 20.0
