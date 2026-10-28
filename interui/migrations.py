"""Migraciones al estilo de Django: se generan solas y se aplican por orden.

.. code-block:: bash

    interui db makemigrations    # compara models.py con la última migración
    interui db migrate           # aplica las pendientes
    interui db status            # qué falta por aplicar

Cada migración es un JSON legible dentro de ``migrations/`` con dos partes: las
operaciones a ejecutar y el **estado completo** del esquema después de
aplicarlas. Guardar el estado (y no solo el delta) permite comparar siempre
contra la verdad declarada y evita migraciones imposibles de reconstruir.

Operaciones soportadas: ``CreateModel``, ``AddField``, ``RemoveField``,
``AlterField`` y ``DeleteModel``.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any, Sequence

from . import db as _db
from .config import Config, ConfigError
from .db import Column

__all__ = [
    "MIGRATIONS_TABLE",
    "Migration",
    "apply",
    "load_migrations",
    "makemigrations",
    "migrate",
    "pending",
    "state_of",
    "status",
]

MIGRATIONS_TABLE = "interui_migrations"


# ---------------------------------------------------------------------------
# operaciones
# ---------------------------------------------------------------------------
class Operation:
    """Una operación de esquema."""

    kind = "Operation"

    def __init__(self, kind: str, table: str, database: str = "default", **extra: Any) -> None:
        self.kind = kind
        self.table = table
        self.database = database
        self.extra = extra

    def to_dict(self) -> dict[str, Any]:
        return {"op": self.kind, "table": self.table, "database": self.database, **self.extra}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Operation":
        kind = data.get("op")
        table = data.get("table", "")
        database = data.get("database", "default")
        if kind == "CreateModel":
            return Operation("CreateModel", table, database, columns=data.get("columns", []))
        if kind == "AddField":
            return Operation("AddField", table, database, column=data.get("column", {}))
        if kind == "RemoveField":
            return Operation("RemoveField", table, database, column=data.get("column", {}))
        if kind == "AlterField":
            return Operation(
                "AlterField", table, database,
                column=data.get("column", {}), previous=data.get("previous", {}),
            )
        if kind == "DeleteModel":
            return Operation("DeleteModel", table, database)
        raise ConfigError(f"Operación de migración desconocida: {kind!r}")

    def __repr__(self) -> str:  # pragma: no cover - ayuda al depurar
        return f"<{self.kind} {self.table}>"

    # -- ejecución -------------------------------------------------------
    def run(self) -> None:
        backend = _db.backend(self.database)
        if self.kind == "CreateModel":
            columns = [Column.from_dict(item) for item in self.extra.get("columns", [])]
            backend.create_table(self.table, columns)
        elif self.kind == "DeleteModel":
            backend.drop_table(self.table)
        elif self.kind == "AddField":
            backend.add_column(self.table, Column.from_dict(self.extra["column"]))
        elif self.kind == "RemoveField":
            backend.remove_column(self.table, Column.from_dict(self.extra["column"]))
        elif self.kind == "AlterField":
            backend.alter_column(
                self.table,
                Column.from_dict(self.extra["column"]),
                Column.from_dict(self.extra["previous"]),
            )
        else:  # pragma: no cover - defensivo
            raise ConfigError(f"Operación desconocida: {self.kind}")

    def describe(self) -> str:
        name = self.table
        if self.kind == "CreateModel":
            return f"crear tabla {name}"
        if self.kind == "DeleteModel":
            return f"borrar tabla {name}"
        column = self.extra.get("column", {}).get("name", "?")
        if self.kind == "AddField":
            return f"añadir {name}.{column}"
        if self.kind == "RemoveField":
            return f"quitar {name}.{column}"
        return f"cambiar {name}.{column}"


# ---------------------------------------------------------------------------
# migración
# ---------------------------------------------------------------------------
class Migration:
    """Un archivo ``NNNN_nombre.json``."""

    def __init__(
        self,
        name: str,
        operations: Sequence[Operation],
        state: dict[str, Any],
        path: Path | None = None,
    ) -> None:
        self.name = name
        self.operations = list(operations)
        self.state = state
        self.path = path

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "created": _dt.datetime.now().replace(microsecond=0).isoformat(),
            "operations": [operation.to_dict() for operation in self.operations],
            "state": self.state,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any], path: Path | None = None) -> "Migration":
        name = data.get("name") or (path.stem if path is not None else "?")
        return cls(
            name,
            [Operation.from_dict(item) for item in data.get("operations", [])],
            data.get("state", {"tables": {}}),
            path,
        )

    @classmethod
    def load(cls, path: Path) -> "Migration":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"{path}: JSON inválido ({exc.msg})") from exc
        data.setdefault("name", path.stem)
        return cls.from_dict(data, path)

    def save(self, folder: Path) -> Path:
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / f"{self.name}.json"
        path.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self.path = path
        return path

    def __repr__(self) -> str:  # pragma: no cover - ayuda al depurar
        return f"<Migration {self.name} ({len(self.operations)} operaciones)>"


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------
def _folder(config: Config) -> Path:
    relative = (config.get("migrations") or {}).get("directory", "migrations")
    folder = config.resolve(relative)
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def load_migrations(config: Config) -> list[Migration]:
    """Todas las migraciones, ordenadas por nombre."""
    folder = _folder(config)
    return [Migration.load(path) for path in sorted(folder.glob("[0-9]*.json"))]


def state_of(config: Config) -> dict[str, Any]:
    """Estado de esquema declarado por ``models.py``."""
    from .orm import model_state

    return {"tables": model_state(config.model_classes())}


def _columns(fields: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for name, info in fields.items():
        item = {"name": name, **{key: value for key, value in info.items() if key != "target"}}
        out.append(item)
    return out


def _diff(
    previous: dict[str, Any],
    current: dict[str, Any],
) -> tuple[list[Operation], list[Operation]]:
    """Devuelve ``(operaciones, borrados)``."""
    old_tables = previous.get("tables", {})
    new_tables = current.get("tables", {})
    operations: list[Operation] = []
    destructive: list[Operation] = []

    for table, info in new_tables.items():
        database = info.get("database", "default")
        if table not in old_tables:
            operations.append(
                Operation("CreateModel", table, database, columns=_columns(info.get("fields", {})))
            )
            continue
        old_fields = old_tables[table].get("fields", {})
        new_fields = info.get("fields", {})
        for name, field in new_fields.items():
            column = {"name": name, **field}
            if name not in old_fields:
                operations.append(Operation("AddField", table, database, column=column))
            elif old_fields[name] != field:
                previous_column = {"name": name, **old_fields[name]}
                operations.append(
                    Operation(
                        "AlterField", table, database,
                        column=column, previous=previous_column,
                    )
                )
        for name, field in old_fields.items():
            if name not in new_fields:
                destructive.append(
                    Operation("RemoveField", table, database, column={"name": name, **field})
                )

    for table in old_tables:
        if table not in new_tables:
            destructive.append(Operation("DeleteModel", table, old_tables[table].get("database", "default")))
    return operations, destructive


def _next_name(config: Config, label: str | None) -> str:
    existing = load_migrations(config)
    number = len(existing) + 1
    slug = (label or ("initial" if number == 1 else "auto")).strip().lower().replace(" ", "_")
    return f"{number:04d}_{slug}"


def makemigrations(
    config: Config,
    name: str | None = None,
    *,
    allow_destructive: bool = False,
) -> Path | None:
    """Crea la migración que pone el esquema al día. ``None`` si no hay cambios."""
    migrations = load_migrations(config)
    previous = migrations[-1].state if migrations else {"tables": {}}
    current = state_of(config)
    operations, destructive = _diff(previous, current)
    if destructive and not allow_destructive:
        detail = "\n  ".join(operation.describe() for operation in destructive)
        raise ConfigError(
            "Estos cambios borran datos y no se aplican solos:\n  "
            f"{detail}\nPásalos a mano o repite con --force si es lo que quieres."
        )
    operations = operations + destructive
    if not operations:
        return None
    migration = Migration(_next_name(config, name), operations, current)
    return migration.save(_folder(config))


# ---------------------------------------------------------------------------
# aplicación
# ---------------------------------------------------------------------------
def _ensure_registry(backend: _db.Backend) -> None:
    backend.create_table(
        MIGRATIONS_TABLE,
        [
            Column("name", "varchar", null=False, primary_key=True, max_length=120),
            Column("applied", "varchar", null=True, max_length=40),
        ],
    )


def _applied_names(backend: _db.Backend) -> set[str]:
    try:
        rows = backend.select(MIGRATIONS_TABLE)
    except Exception:  # noqa: BLE001 - la tabla aún no existe
        return set()
    return {str(row.get("name")) for row in rows}


def apply(config: Config, migration: Migration) -> None:
    """Ejecuta una migración y la marca como aplicada."""
    for operation in migration.operations:
        operation.run()
    backends = {operation.database for operation in migration.operations} or {"default"}
    stamp = _dt.datetime.now().replace(microsecond=0).isoformat()
    for alias in backends:
        backend = _db.backend(alias)
        _ensure_registry(backend)
        backend.insert(MIGRATIONS_TABLE, {"name": migration.name, "applied": stamp})


def pending(config: Config) -> list[Migration]:
    """Migraciones sin aplicar (según la base de datos ``default``)."""
    migrations = load_migrations(config)
    backend = _db.backend("default")
    _ensure_registry(backend)
    applied = _applied_names(backend)
    return [migration for migration in migrations if migration.name not in applied]


def migrate(config: Config) -> list[str]:
    """Aplica todas las pendientes y devuelve sus nombres."""
    done: list[str] = []
    for migration in pending(config):
        apply(config, migration)
        done.append(migration.name)
    return done


def status(config: Config) -> list[dict[str, Any]]:
    """Lista ``[{"name", "applied", "operations"}]`` para ``interui db status``."""
    migrations = load_migrations(config)
    backend = _db.backend("default")
    _ensure_registry(backend)
    applied = _applied_names(backend)
    return [
        {
            "name": migration.name,
            "applied": migration.name in applied,
            "operations": [operation.describe() for operation in migration.operations],
        }
        for migration in migrations
    ]
