# Implements: specs/06-seleccion-materiales.md
"""Base de datos pura de materiales de referencia."""

from __future__ import annotations

from core.models import MaterialSystem

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
