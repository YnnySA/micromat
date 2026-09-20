# Implements: specs/10-rve.md
"""Pruebas del generador y la visualización del RVE."""

import math

import numpy as np

from core.rve import (
    TOL_SOLAPE,
    VF_MAX_PRACTICO,
    distancia_min_imagen,
    generar_rve,
    poligonos_periodicos,
)


def _max_solape(centros, radios, lado):
    mayor = -math.inf
    for i in range(len(radios)):
        for j in range(i + 1, len(radios)):
            distancia = distancia_min_imagen(
                centros[i, 0] - centros[j, 0],
                centros[i, 1] - centros[j, 1],
                lado,
            )
            mayor = max(mayor, radios[i] + radios[j] - distancia)
    return mayor


def test_rve_no_overlap_and_target():
    rve = generar_rve(0.60, 50.0, 5.0, 7.0, seed=5)
    assert rve.convergido
    assert rve.n_fibras > 0
    assert rve.vf_logrado <= 0.60 + 1e-9
    assert rve.vf_logrado >= 0.60 - 0.02
    assert _max_solape(rve.centros, rve.radios, rve.lado) <= TOL_SOLAPE + 1e-9

    gfrp = generar_rve(0.55, 50.0, 13.0, 17.0, seed=143)
    assert gfrp.convergido
    assert gfrp.vf_logrado <= 0.55 + 1e-9
    assert gfrp.vf_logrado >= 0.55 - 0.02


def test_rve_diameters_in_range():
    rve = generar_rve(0.55, 50.0, 13.0, 17.0, seed=143)
    assert rve.diametro_min >= 13.0 * 0.9
    assert rve.diametro_max <= 17.0 * 1.1

    cfrp = generar_rve(0.60, 50.0, 5.0, 7.0, seed=5)
    assert cfrp.diametro_min >= 5.0 * 0.9
    assert cfrp.diametro_max <= 7.0 * 1.1


def test_rve_deterministic():
    a = generar_rve(0.60, 50.0, 5.0, 7.0, seed=11)
    b = generar_rve(0.60, 50.0, 5.0, 7.0, seed=11)
    assert np.allclose(a.centros, b.centros)
    assert np.allclose(a.radios, b.radios)
    assert a.n_fibras == b.n_fibras


def test_vf_cap():
    rve = generar_rve(0.80, 50.0, 5.0, 7.0, seed=2)
    assert rve.vf_logrado <= VF_MAX_PRACTICO + 1e-9
    assert rve.vf_logrado <= 0.80


def test_polygons_cross_boundary():
    rve = generar_rve(0.60, 50.0, 5.0, 7.0, seed=5)
    xs, ys = poligonos_periodicos(rve.centros, rve.radios, rve.lado)
    assert len(xs) == len(ys)
    assert any(value is None for value in xs)
    reales = [value for value in xs if value is not None]
    assert min(reales) < 0.0 or max(reales) > rve.lado
