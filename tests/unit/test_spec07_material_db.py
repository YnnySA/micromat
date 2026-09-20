# Implements: specs/07-base-materiales.md
"""Pruebas de la base de datos ligera de materiales (SQLite)."""

from core import material_db


def test_material_db_seed(tmp_path):
    db = tmp_path / "materials.db"
    material_db.init_db(db)

    assert "IM7" in material_db.list_fibers(db)
    assert "E-glass" in material_db.list_fibers(db)
    assert "Epoxi 8552" in material_db.list_matrices(db)

    fiber = material_db.get_fiber("IM7", db)
    assert fiber["E1"] == 276.0
    assert fiber["etu"] == 0.0187
    assert fiber["density"] == 1780.0

    matrix = material_db.get_matrix("Epoxi 8552", db)
    assert matrix["E"] == 4.67
    assert matrix["G"] == 1.72


def test_material_db_crud(tmp_path):
    db = tmp_path / "materials.db"
    material_db.init_db(db)

    props = {"E1": 1.0, "E2": 2.0, "G12": 3.0, "nu12": 0.1, "F1t": 4.0, "etu": 0.5, "density": 6.0, "d_min": 5.0, "d_max": 7.0}
    material_db.save_fiber("Prueba", props, db)
    assert material_db.get_fiber("Prueba", db)["E1"] == 1.0

    props["E1"] = 9.0
    material_db.save_fiber("Prueba", props, db)
    assert material_db.get_fiber("Prueba", db)["E1"] == 9.0

    material_db.delete_fiber("Prueba", db)
    assert "Prueba" not in material_db.list_fibers(db)
    assert material_db.get_fiber("Prueba", db) is None


def test_material_db_reset(tmp_path):
    db = tmp_path / "materials.db"
    material_db.init_db(db)
    material_db.save_fiber("Extra", {"E1": 1, "E2": 1, "G12": 1, "nu12": 0.1, "F1t": 1, "etu": 0.1, "density": 1, "d_min": 5, "d_max": 7}, db)
    material_db.reset_db(db)
    assert "Extra" not in material_db.list_fibers(db)
    assert "IM7" in material_db.list_fibers(db)
