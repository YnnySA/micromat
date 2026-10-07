# Implements: specs/10-rve.md
"""Generación realista del RVE (Elemento de Volumen Representativo).

El RVE se trata como una **celda periódica** (condiciones de borde periódicas):
las fibras pueden cruzar los bordes y reaparecen por el opuesto. El área de
fibra se cuenta una sola vez por fibra, de modo que

    Vf = Σ π r_i² / L²

es exacta y no requiere recortar áreas. La no-superposición se verifica con la
distancia mínima-imagen (la menor distancia entre copias periódicas).

La colocación usa una **relajación por compresión** (estilo Lubachevsky-
Stillinger): se parte de una caja holgada y se contrae hasta ``L`` empujando los
pares solapados, lo que permite alcanzar densidades (~0.60) donde RSA se
estanca (~0.547). El Vf objetivo nunca se supera: si no es alcanzable, se
reduce en pasos de 0.005 hasta converger.

``TOL_SOLAPE`` es la tolerancia de solape (µm). Se adopta 0.01 µm (10 nm), muy
por debajo de la resolución de una micrografía.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

TOL_SOLAPE = 1e-2
VF_MAX_PRACTICO = 0.65


@dataclass(frozen=True)
class RveResult:
    centros: np.ndarray
    radios: np.ndarray
    lado: float
    vf_objetivo: float
    vf_logrado: float
    n_fibras: int
    iteraciones: int
    convergido: bool

    @property
    def area_fibras(self) -> float:
        return float(np.sum(np.pi * self.radios**2))

    @property
    def diametro_min(self) -> float:
        return float(2.0 * np.min(self.radios))

    @property
    def diametro_max(self) -> float:
        return float(2.0 * np.max(self.radios))


def distancia_min_imagen(dx: float, dy: float, lado: float) -> float:
    """Distancia euclídea considerando las copias periódicas de la celda."""
    dx = dx - lado * round(dx / lado)
    dy = dy - lado * round(dy / lado)
    return math.hypot(dx, dy)


def _max_solape(centros: np.ndarray, radios: np.ndarray, lado: float) -> float:
    diff = centros[:, None, :] - centros[None, :, :]
    dx = diff[:, :, 0]
    dy = diff[:, :, 1]
    dx = dx - lado * np.round(dx / lado)
    dy = dy - lado * np.round(dy / lado)
    dist = np.hypot(dx, dy)
    np.fill_diagonal(dist, np.inf)
    solape = (radios[:, None] + radios[None, :]) - dist
    return float(np.max(solape)) if solape.size else -math.inf


def _relajar(
    centros: np.ndarray,
    radios: np.ndarray,
    lado: float,
    max_iter: int = 200,
    tol: float = TOL_SOLAPE,
    factor: float = 0.5,
    rng: np.random.Generator | None = None,
    separacion_extra: float = 0.0,
) -> tuple[np.ndarray, int]:
    """Separa pares cercanos usando la distancia mínima-imagen periódica.

    ``separacion_extra`` activa una repulsión suave entre fibras que no se
    solapan, reduciendo agrupamientos y zonas vacías en la representación.
    """
    suma = radios[:, None] + radios[None, :]
    escala_cap = 0.5 * float(np.min(radios)) if radios.size else 0.1
    distancia_objetivo = suma + float(max(0.0, separacion_extra))
    for iteration in range(max_iter):
        diff = centros[:, None, :] - centros[None, :, :]
        dx = diff[:, :, 0].copy()
        dy = diff[:, :, 1].copy()
        dx = dx - lado * np.round(dx / lado)
        dy = dy - lado * np.round(dy / lado)
        dist = np.hypot(dx, dy)
        np.fill_diagonal(dist, np.inf)
        solape = np.where(np.isfinite(distancia_objetivo - dist), distancia_objetivo - dist, 0.0)
        mask = solape > tol
        if not mask.any():
            return centros, iteration

        dist_safe = np.where(dist > 1e-9, dist, 1.0)
        solape_pos = np.where(mask, solape, 0.0)
        fx = (dx / dist_safe) * solape_pos
        fy = (dy / dist_safe) * solape_pos
        disp = np.stack([fx.sum(axis=1), fy.sum(axis=1)], axis=1) * factor

        mag = np.hypot(disp[:, 0], disp[:, 1])
        excede = mag > escala_cap
        if excede.any():
            factor_escala = np.where(excede, escala_cap / np.maximum(mag, 1e-12), 1.0)
            disp[:, 0] *= factor_escala
            disp[:, 1] *= factor_escala

        centros = (centros + disp) % lado
        if rng is not None and iteration % 25 == 24:
            centros = (centros + rng.normal(0.0, 0.002 * float(np.mean(radios)), centros.shape)) % lado
    return centros, max_iter


def _intentar(vf: float, lado: float, d_min: float, d_max: float,
              rng: np.random.Generator, pasos: int = 80) -> RveResult:
    area_objetivo = vf * lado**2
    d_medio = 0.5 * (d_min + d_max)
    area_medio = math.pi * (d_medio / 2.0) ** 2
    n = max(1, int(round(area_objetivo / area_medio)))

    diametros = rng.uniform(d_min, d_max, size=n)
    radios = diametros / 2.0
    suma = math.pi * float(np.sum(radios**2))
    if suma <= 0.0:
        radios = np.full(n, math.sqrt(area_objetivo / (math.pi * n)))
    else:
        radios = radios * math.sqrt(area_objetivo / suma)

    area_total = math.pi * float(np.sum(radios**2))
    lado0 = math.sqrt(area_total / 0.30)  # arranque holgado (Vf ≈ 0.30)
    centros = rng.random((n, 2)) * lado0

    iteraciones = 0
    for k in range(1, pasos + 1):
        lado_k = lado0 + (lado - lado0) * k / pasos
        centros = centros % lado_k
        centros, its = _relajar(centros, radios, lado_k, max_iter=120, rng=rng)
        iteraciones += its

    centros = centros % lado
    centros, its = _relajar(
        centros,
        radios,
        lado,
        max_iter=260,
        factor=0.22,
        rng=rng,
        separacion_extra=0.18 * float(np.mean(radios)),
    )
    iteraciones += its
    if _max_solape(centros, radios, lado) > TOL_SOLAPE:
        centros, its = _relajar(centros, radios, lado, max_iter=800, rng=rng)
        iteraciones += its

    solape = _max_solape(centros, radios, lado)
    return RveResult(
        centros=centros,
        radios=radios,
        lado=lado,
        vf_objetivo=vf,
        vf_logrado=area_total / lado**2,
        n_fibras=int(n),
        iteraciones=iteraciones,
        convergido=solape <= TOL_SOLAPE,
    )


def generar_rve(vf_objetivo: float, lado: float = 50.0, d_min: float = 5.0,
                d_max: float = 7.0, seed: int = 0,
                intentos_por_objetivo: int = 3) -> RveResult:
    """Genera un RVE periódico sin solapes con ``Vf_logrado <= Vf_objetivo``.

    El objetivo se limita al máximo práctico (0.65). Si no se alcanza, se reduce
    en pasos de 0.005 hasta obtener una colocación válida.
    """
    vf_objetivo = float(min(max(vf_objetivo, 0.02), VF_MAX_PRACTICO))
    d_min, d_max = float(min(d_min, d_max)), float(max(d_min, d_max))
    if d_min <= 0.0:
        d_min, d_max = 0.1, max(d_max, 0.2)

    rng = np.random.default_rng(seed)
    objetivo = vf_objetivo
    ultimo: RveResult | None = None
    while objetivo >= 0.05:
        for _ in range(intentos_por_objetivo):
            resultado = _intentar(objetivo, lado, d_min, d_max, rng)
            if resultado.convergido:
                return resultado
            ultimo = resultado
        objetivo -= 0.005
    return ultimo  # type: ignore[return-value]


def poligonos_periodicos(centros: np.ndarray, radios: np.ndarray, lado: float,
                         n_lados: int = 48) -> tuple[list[float | None], list[float | None]]:
    """Polígonos de cada fibra y sus 8 copias periódicas, separados por ``None``."""
    angulo = np.linspace(0.0, 2.0 * math.pi, n_lados + 1)
    coseno, seno = np.cos(angulo), np.sin(angulo)
    xs: list[float | None] = []
    ys: list[float | None] = []
    for (cx, cy), r in zip(centros, radios):
        for ox in (-lado, 0.0, lado):
            x0 = cx + ox
            if x0 + r < 0.0 or x0 - r > lado:
                continue
            for oy in (-lado, 0.0, lado):
                y0 = cy + oy
                if y0 + r < 0.0 or y0 - r > lado:
                    continue
                xs.extend((x0 + r * coseno).tolist())
                ys.extend((y0 + r * seno).tolist())
                xs.append(None)
                ys.append(None)
    return xs, ys
