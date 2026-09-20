# Implements: specs/07-base-materiales.md
"""Base de datos ligera de fibras y matrices sobre SQLite (stdlib).

La base reside en ``proyecto01/data/materials.db`` y se crea y siembra de forma
automática en el primer uso. Contiene únicamente las propiedades que consumen
los modelos micromecánicos del curso y la generación del RVE:

* Fibras: ``E1, E2, G12, nu12, F1t, etu, density, d_min, d_max``.
* Matrices: ``E, nu, G, Ft, density``.

``d_min`` y ``d_max`` son el diámetro de fibra en µm (rango usado por el RVE).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "materials.db"

FIBER_FIELDS: tuple[str, ...] = ("E1", "E2", "G12", "nu12", "F1t", "etu", "density", "d_min", "d_max")
MATRIX_FIELDS: tuple[str, ...] = ("E", "nu", "G", "Ft", "density")


# Valores de referencia tomados del notebook (sistemas del curso), de la
# lámina 13 de Clase2_U2 y de la directriz de la Tarea 1 (diámetros en µm).
_SEED_FIBERS: dict[str, dict[str, float]] = {
    "IM7": {"E1": 276.0, "E2": 19.0, "G12": 27.0, "nu12": 0.20, "F1t": 5180.0, "etu": 0.0187, "density": 1780.0, "d_min": 5.0, "d_max": 7.0},
    "E-glass": {"E1": 72.0, "E2": 72.0, "G12": 29.5, "nu12": 0.22, "F1t": 2400.0, "etu": 0.034, "density": 2540.0, "d_min": 13.0, "d_max": 17.0},
    "Carbon T300": {"E1": 230.0, "E2": 15.0, "G12": 9.0, "nu12": 0.20, "F1t": 3500.0, "etu": 0.0152, "density": 1760.0, "d_min": 6.0, "d_max": 8.0},
    "Carbon M40J": {"E1": 380.0, "E2": 6.5, "G12": 3.0, "nu12": 0.20, "F1t": 4400.0, "etu": 0.0116, "density": 1770.0, "d_min": 4.0, "d_max": 6.0},
    "Kevlar-49": {"E1": 125.0, "E2": 8.0, "G12": 2.0, "nu12": 0.35, "F1t": 2800.0, "etu": 0.0224, "density": 1440.0, "d_min": 11.0, "d_max": 13.0},
}

_SEED_MATRICES: dict[str, dict[str, float]] = {
    "Epoxi 8552": {"E": 4.67, "nu": 0.36, "G": 1.72, "Ft": 121.0, "density": 1300.0},
    "Epoxi GFRP": {"E": 3.50, "nu": 0.38, "G": 1.28, "Ft": 80.0, "density": 1200.0},
    "Epoxy 3501-6": {"E": 4.20, "nu": 0.35, "G": 1.56, "Ft": 69.0, "density": 1200.0},
    "Poliéster": {"E": 3.40, "nu": 0.38, "G": 1.27, "Ft": 55.0, "density": 1200.0},
    "PEEK": {"E": 3.80, "nu": 0.38, "G": 1.40, "Ft": 100.0, "density": 1300.0},
}

_DEFAULT_BY_FIELD: dict[str, float] = {"d_min": 7.0, "d_max": 10.0}

_initialized = False


def _connect(db_path: Path | str | None = None) -> sqlite3.Connection:
    path = Path(db_path) if db_path is not None else DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(path))
    connection.row_factory = sqlite3.Row
    return connection


def _migrate_fiber_columns(connection: sqlite3.Connection) -> None:
    """Agrega ``d_min``/``d_max`` a bases creadas antes de esta versión."""
    columns = {row["name"] for row in connection.execute("PRAGMA table_info(fibers)")}
    if "d_min" not in columns:
        connection.execute("ALTER TABLE fibers ADD COLUMN d_min REAL DEFAULT 7.0")
    if "d_max" not in columns:
        connection.execute("ALTER TABLE fibers ADD COLUMN d_max REAL DEFAULT 10.0")
    for name, props in _SEED_FIBERS.items():
        connection.execute(
            "UPDATE fibers SET d_min = ?, d_max = ? "
            "WHERE name = ? AND (d_min IS NULL OR d_min = 7.0) AND (d_max IS NULL OR d_max = 10.0)",
            (props["d_min"], props["d_max"], name),
        )


def init_db(db_path: Path | str | None = None) -> None:
    """Crea las tablas, migra columnas y siembra los materiales si están vacías."""
    with _connect(db_path) as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS fibers ("
            "name TEXT PRIMARY KEY, E1 REAL, E2 REAL, G12 REAL, nu12 REAL, "
            "F1t REAL, etu REAL, density REAL, d_min REAL, d_max REAL)"
        )
        connection.execute(
            "CREATE TABLE IF NOT EXISTS matrices ("
            "name TEXT PRIMARY KEY, E REAL, nu REAL, G REAL, Ft REAL, density REAL)"
        )
        _migrate_fiber_columns(connection)
        for table, seed in (("fibers", _SEED_FIBERS), ("matrices", _SEED_MATRICES)):
            count = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if count:
                continue
            for name, props in seed.items():
                fields = FIBER_FIELDS if table == "fibers" else MATRIX_FIELDS
                columns = ", ".join(("name", *fields))
                placeholders = ", ".join("?" for _ in range(len(fields) + 1))
                values = [name, *(props[field] for field in fields)]
                connection.execute(
                    f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", values
                )


def reset_db(db_path: Path | str | None = None) -> None:
    """Vacía las tablas y vuelve a sembrar los materiales de referencia."""
    _ensure(db_path)
    with _connect(db_path) as connection:
        connection.execute("DELETE FROM fibers")
        connection.execute("DELETE FROM matrices")
    init_db(db_path)


def _ensure(db_path: Path | str | None = None) -> None:
    global _initialized
    if db_path is not None or not _initialized:
        init_db(db_path)
        if db_path is None:
            _initialized = True


def _list(table: str, db_path: Path | str | None = None) -> list[str]:
    _ensure(db_path)
    with _connect(db_path) as connection:
        rows = connection.execute(f"SELECT name FROM {table} ORDER BY name").fetchall()
    return [row["name"] for row in rows]


def _get(table: str, fields: Iterable[str], name: str, db_path: Path | str | None = None) -> dict[str, float] | None:
    _ensure(db_path)
    with _connect(db_path) as connection:
        row = connection.execute(
            f"SELECT * FROM {table} WHERE name = ?", (name,)
        ).fetchone()
    if row is None:
        return None
    return {field: row[field] for field in fields}


def _upsert(table: str, fields: Iterable[str], name: str, props: dict[str, float], db_path: Path | str | None = None) -> None:
    _ensure(db_path)
    fields = tuple(fields)
    columns = ", ".join(("name", *fields))
    placeholders = ", ".join("?" for _ in range(len(fields) + 1))
    assignments = ", ".join(f"{field}=excluded.{field}" for field in fields)
    values = [name, *(float(props.get(field, _DEFAULT_BY_FIELD.get(field, 0.0))) for field in fields)]
    with _connect(db_path) as connection:
        connection.execute(
            f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) "
            f"ON CONFLICT(name) DO UPDATE SET {assignments}",
            values,
        )


def _delete(table: str, name: str, db_path: Path | str | None = None) -> None:
    _ensure(db_path)
    with _connect(db_path) as connection:
        connection.execute(f"DELETE FROM {table} WHERE name = ?", (name,))


# --- API pública de fibras -------------------------------------------------

def list_fibers(db_path: Path | str | None = None) -> list[str]:
    return _list("fibers", db_path)


def get_fiber(name: str, db_path: Path | str | None = None) -> dict[str, float] | None:
    return _get("fibers", FIBER_FIELDS, name, db_path)


def save_fiber(name: str, props: dict[str, float], db_path: Path | str | None = None) -> None:
    _upsert("fibers", FIBER_FIELDS, name, props, db_path)


def delete_fiber(name: str, db_path: Path | str | None = None) -> None:
    _delete("fibers", name, db_path)


# --- API pública de matrices -----------------------------------------------

def list_matrices(db_path: Path | str | None = None) -> list[str]:
    return _list("matrices", db_path)


def get_matrix(name: str, db_path: Path | str | None = None) -> dict[str, float] | None:
    return _get("matrices", MATRIX_FIELDS, name, db_path)


def save_matrix(name: str, props: dict[str, float], db_path: Path | str | None = None) -> None:
    _upsert("matrices", MATRIX_FIELDS, name, props, db_path)


def delete_matrix(name: str, db_path: Path | str | None = None) -> None:
    _delete("matrices", name, db_path)
