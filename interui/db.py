"""Conexiones a bases de datos declaradas en ``interui.json``.

Un solo API para cinco motores:

============  ==========================================================
``sqlite``    archivo local con ``sqlite3`` (biblioteca estándar)
``file``      una carpeta de archivos JSON (sin servidor ni drivers)
``postgres``  PostgreSQL (``pip install "interui[postgres]"``)
``mysql``     MySQL / MariaDB (``pip install "interui[mysql]"``)
``mongo``     MongoDB (``pip install "interui[mongo]"``)
============  ==========================================================

.. code-block:: python

    from interui import config, db

    cfg = config.load()
    base = db.connect(cfg.database())
    base.create_table("clientes", [db.Column("id", "int", primary_key=True, auto=True),
                                   db.Column("nombre", "varchar", max_length=80)])
    base.insert("clientes", {"nombre": "Ana"})
    base.select("clientes", where=[("nombre", "=", "Ana")])

El ORM (:mod:`interui.orm`) y las migraciones (:mod:`interui.migrations`) usan
esta misma capa, así que el motor es un detalle de configuración.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sqlite3
import threading
from pathlib import Path
from typing import Any, Iterable, Sequence

from .config import DatabaseSettings, ENGINES, Section

__all__ = [
    "Backend",
    "Column",
    "DatabaseError",
    "FileBackend",
    "MongoBackend",
    "MySQLBackend",
    "PostgresBackend",
    "SQLiteBackend",
    "backend",
    "configure",
    "connect",
    "reset",
]

_IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

# tipos lógicos -> SQL por motor
_TYPES = {
    "sqlite": {
        "int": "INTEGER", "bigint": "INTEGER", "text": "TEXT", "varchar": "VARCHAR({n})",
        "bool": "INTEGER", "real": "REAL", "datetime": "TEXT", "date": "TEXT",
        "json": "TEXT", "blob": "BLOB",
    },
    "postgres": {
        "int": "INTEGER", "bigint": "BIGINT", "text": "TEXT", "varchar": "VARCHAR({n})",
        "bool": "BOOLEAN", "real": "DOUBLE PRECISION", "datetime": "TIMESTAMP", "date": "DATE",
        "json": "JSONB", "blob": "BYTEA",
    },
    "mysql": {
        "int": "INT", "bigint": "BIGINT", "text": "TEXT", "varchar": "VARCHAR({n})",
        "bool": "TINYINT(1)", "real": "DOUBLE", "datetime": "DATETIME", "date": "DATE",
        "json": "JSON", "blob": "BLOB",
    },
}

_AUTO = {
    "sqlite": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "postgres": "SERIAL PRIMARY KEY",
    "mysql": "INTEGER PRIMARY KEY AUTO_INCREMENT",
}


class DatabaseError(RuntimeError):
    """No se pudo conectar o la operación no es válida."""


def _check_ident(name: str) -> str:
    if not _IDENT.match(str(name)):
        raise DatabaseError(f"nombre no válido: {name!r} (usa letras, números y _)")
    return str(name)


class Column:
    """Columna de una tabla, con el tipo lógico del ORM."""

    __slots__ = ("name", "type", "null", "unique", "primary_key", "auto", "default", "max_length")

    def __init__(
        self,
        name: str,
        type: str = "text",
        *,
        null: bool = True,
        unique: bool = False,
        primary_key: bool = False,
        auto: bool = False,
        default: Any = None,
        max_length: int | None = None,
    ) -> None:
        self.name = _check_ident(name)
        self.type = type
        self.null = null
        self.unique = unique
        self.primary_key = primary_key
        self.auto = auto
        self.default = default
        self.max_length = max_length

    # -- serialización ---------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "type": self.type,
            "null": self.null,
            "unique": self.unique,
            "primary_key": self.primary_key,
            "auto": self.auto,
            "default": self.default,
            "max_length": self.max_length,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Column":
        return cls(
            data["name"],
            data.get("type", "text"),
            null=bool(data.get("null", True)),
            unique=bool(data.get("unique", False)),
            primary_key=bool(data.get("primary_key", False)),
            auto=bool(data.get("auto", False)),
            default=data.get("default"),
            max_length=data.get("max_length"),
        )

    def same_as(self, other: "Column") -> bool:
        return (
            self.type == other.type
            and self.null == other.null
            and self.unique == other.unique
            and self.max_length == other.max_length
        )

    def __repr__(self) -> str:  # pragma: no cover - ayuda al depurar
        return f"<Column {self.name} {self.type}>"


# ---------------------------------------------------------------------------
# conversión de valores
# ---------------------------------------------------------------------------
def _to_storage(column: Column, value: Any) -> Any:
    if value is None:
        return None
    if column.type == "bool":
        return int(bool(value))
    if column.type == "json":
        return json.dumps(value, ensure_ascii=False)
    if column.type in ("datetime", "date") and not isinstance(value, str):
        return value.isoformat(sep=" ") if hasattr(value, "isoformat") else str(value)
    if column.type == "blob" and isinstance(value, (bytes, bytearray)):
        return sqlite3.Binary(bytes(value))
    return value


def _from_storage(column_type: str, value: Any) -> Any:
    if value is None:
        return None
    if column_type == "bool":
        return bool(value)
    if column_type == "json" and isinstance(value, (str, bytes)):
        try:
            return json.loads(value)
        except (TypeError, ValueError):
            return value
    if column_type == "blob" and isinstance(value, memoryview):
        return bytes(value)
    return value


def _where_sql(
    where: Sequence[tuple[str, str, Any]] | None,
    placeholder: str,
    quote,
) -> tuple[str, list[Any]]:
    if not where:
        return "", []
    parts: list[str] = []
    params: list[Any] = []
    for column, op, value in where:
        name = quote(_check_ident(column))
        operator = op.lower().strip()
        if operator in ("is null", "is not null"):
            parts.append(f"{name} {operator.upper()}")
        elif operator == "in":
            values = list(value or [])
            if not values:
                parts.append("1 = 0")
            else:
                marks = ", ".join(placeholder for _ in values)
                parts.append(f"{name} IN ({marks})")
                params.extend(values)
        elif operator in ("=", "!=", "<>", ">", ">=", "<", "<="):
            parts.append(f"{name} {operator} {placeholder}")
            params.append(value)
        elif operator in ("like", "not like"):
            parts.append(f"{name} {operator.upper()} {placeholder}")
            params.append(value)
        else:
            raise DatabaseError(f"operador no soportado: {op!r}")
    return " WHERE " + " AND ".join(parts), params


# ---------------------------------------------------------------------------
# base
# ---------------------------------------------------------------------------
class Backend:
    """Interfaz común de todos los motores."""

    engine = "base"
    dialect = "sql"

    def __init__(self, settings: DatabaseSettings | Section) -> None:
        self.settings = settings
        self.alias = getattr(settings, "alias", "default")
        self._lock = threading.RLock()

    # -- ciclo de vida ---------------------------------------------------
    def open(self) -> None:  # pragma: no cover - lo implementa cada motor
        raise NotImplementedError

    def close(self) -> None:
        pass

    def __enter__(self) -> "Backend":
        self.open()
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    # -- esquema ---------------------------------------------------------
    def tables(self) -> dict[str, list[Column]]:
        raise NotImplementedError

    def create_table(self, table: str, columns: Iterable[Column]) -> None:
        raise NotImplementedError

    def drop_table(self, table: str) -> None:
        raise NotImplementedError

    def add_column(self, table: str, column: Column) -> None:
        raise NotImplementedError

    def remove_column(self, table: str, column: Column) -> None:
        raise NotImplementedError

    def alter_column(self, table: str, column: Column, previous: Column) -> None:
        raise NotImplementedError

    # -- datos -----------------------------------------------------------
    def insert(self, table: str, row: dict[str, Any]) -> Any:
        raise NotImplementedError

    def update(self, table: str, pk: Any, row: dict[str, Any]) -> None:
        raise NotImplementedError

    def delete(self, table: str, pk: Any) -> None:
        raise NotImplementedError

    def select(
        self,
        table: str,
        *,
        where: Sequence[tuple[str, str, Any]] | None = None,
        order: Sequence[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    def count(self, table: str, where: Sequence[tuple[str, str, Any]] | None = None) -> int:
        return len(self.select(table, where=where))

    def table_columns(self, table: str) -> list[Column]:
        return self.tables().get(table, [])


# ---------------------------------------------------------------------------
# SQL
# ---------------------------------------------------------------------------
class SQLBackend(Backend):
    """Base común de SQLite, PostgreSQL y MySQL."""

    placeholder = "?"
    quote_char = '"'

    def __init__(self, settings: DatabaseSettings | Section) -> None:
        super().__init__(settings)
        self._conn: Any = None

    def quote(self, name: str) -> str:
        return f"{self.quote_char}{name}{self.quote_char}"

    def open(self) -> None:  # pragma: no cover - cada motor conecta
        raise NotImplementedError

    def _ensure(self) -> Any:
        if self._conn is None:
            self.open()
        return self._conn

    def execute(self, sql: str, params: Sequence[Any] = ()) -> Any:
        with self._lock:
            conn = self._ensure()
            cursor = conn.cursor()
            try:
                cursor.execute(sql, list(params))
                return cursor
            except Exception as exc:  # noqa: BLE001 - se traduce a DatabaseError
                raise DatabaseError(f"{type(exc).__name__}: {exc}\nSQL: {sql}") from exc

    def commit(self) -> None:
        if self._conn is not None:
            self._conn.commit()

    def sql_type(self, column: Column) -> str:
        table = _TYPES[self.engine]
        if column.primary_key and column.auto:
            return _AUTO[self.engine]
        template = table.get(column.type, "TEXT")
        if "{n}" in template:
            return template.format(n=column.max_length or 255)
        return template

    def column_sql(self, column: Column) -> str:
        if column.primary_key and column.auto:
            return f"{self.quote(column.name)} {self.sql_type(column)}"
        parts = [self.quote(column.name), self.sql_type(column)]
        if not column.null:
            parts.append("NOT NULL")
        if column.unique:
            parts.append("UNIQUE")
        if column.default is not None:
            parts.append(f"DEFAULT {self.literal(column.default)}")
        return " ".join(parts)

    def literal(self, value: Any) -> str:
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)):
            return str(value)
        if value is None:
            return "NULL"
        return "'" + str(value).replace("'", "''") + "'"

    def create_table(self, table: str, columns: Iterable[Column]) -> None:
        name = _check_ident(table)
        body = ", ".join(self.column_sql(column) for column in columns)
        self.execute(f"CREATE TABLE IF NOT EXISTS {self.quote(name)} ({body})")
        self.commit()

    def drop_table(self, table: str) -> None:
        self.execute(f"DROP TABLE IF EXISTS {self.quote(_check_ident(table))}")
        self.commit()

    def add_column(self, table: str, column: Column) -> None:
        self.execute(
            f"ALTER TABLE {self.quote(_check_ident(table))} ADD COLUMN {self.column_sql(column)}"
        )
        self.commit()

    def remove_column(self, table: str, column: Column) -> None:
        self.execute(
            f"ALTER TABLE {self.quote(_check_ident(table))} DROP COLUMN {self.quote(column.name)}"
        )
        self.commit()

    def alter_column(self, table: str, column: Column, previous: Column) -> None:
        """Reconstruye la tabla (SQLite) o usa ALTER COLUMN en el resto."""
        raise DatabaseError(f"{self.engine} no soporta cambiar columnas automáticamente")

    # -- datos -----------------------------------------------------------
    def insert(self, table: str, row: dict[str, Any]) -> Any:
        columns = self.table_columns(table)
        by_name = {column.name: column for column in columns}
        keys = [key for key in row if key in by_name]
        values = [_to_storage(by_name[key], row[key]) for key in keys]
        marks = ", ".join(self.placeholder for _ in keys)
        names = ", ".join(self.quote(key) for key in keys)
        sql = f"INSERT INTO {self.quote(_check_ident(table))} ({names}) VALUES ({marks})"
        cursor = self.execute(sql, values)
        self.commit()
        pk_name = next((column.name for column in columns if column.primary_key), None)
        if pk_name and pk_name in row:
            return row[pk_name]
        last_id = getattr(cursor, "lastrowid", None)
        return last_id

    def update(self, table: str, pk: Any, row: dict[str, Any]) -> None:
        columns = self.table_columns(table)
        by_name = {column.name: column for column in columns}
        pk_name = next((column.name for column in columns if column.primary_key), "id")
        keys = [key for key in row if key in by_name and key != pk_name]
        if not keys:
            return
        assignments = ", ".join(f"{self.quote(key)} = {self.placeholder}" for key in keys)
        values = [_to_storage(by_name[key], row[key]) for key in keys]
        sql = (
            f"UPDATE {self.quote(_check_ident(table))} SET {assignments} "
            f"WHERE {self.quote(pk_name)} = {self.placeholder}"
        )
        self.execute(sql, [*values, pk])
        self.commit()

    def delete(self, table: str, pk: Any) -> None:
        columns = self.table_columns(table)
        pk_name = next((column.name for column in columns if column.primary_key), "id")
        sql = (
            f"DELETE FROM {self.quote(_check_ident(table))} "
            f"WHERE {self.quote(pk_name)} = {self.placeholder}"
        )
        self.execute(sql, [pk])
        self.commit()

    def select(
        self,
        table: str,
        *,
        where: Sequence[tuple[str, str, Any]] | None = None,
        order: Sequence[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        columns = self.table_columns(table)
        types = {column.name: column.type for column in columns}
        clause, params = _where_sql(where, self.placeholder, self.quote)
        sql = f"SELECT * FROM {self.quote(_check_ident(table))}{clause}"
        if order:
            terms = []
            for term in order:
                descending = term.startswith("-")
                name = _check_ident(term[1:] if descending else term)
                terms.append(f"{self.quote(name)}{' DESC' if descending else ''}")
            sql += " ORDER BY " + ", ".join(terms)
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        if offset:
            sql += f" OFFSET {int(offset)}"
        cursor = self.execute(sql, params)
        rows = cursor.fetchall()
        names = [item[0] for item in cursor.description] if cursor.description else []
        out: list[dict[str, Any]] = []
        for row in rows:
            if isinstance(row, dict):  # mysql con DictCursor
                record = dict(row)
            else:
                record = dict(zip(names, row))
            out.append({key: _from_storage(types.get(key, "text"), value) for key, value in record.items()})
        return out

    def count(self, table: str, where: Sequence[tuple[str, str, Any]] | None = None) -> int:
        clause, params = _where_sql(where, self.placeholder, self.quote)
        cursor = self.execute(f"SELECT COUNT(*) FROM {self.quote(_check_ident(table))}{clause}", params)
        row = cursor.fetchone()
        return int(row[0]) if row else 0

    # -- introspección ---------------------------------------------------
    def _logical_type(self, sql_type: str) -> str:
        text = (sql_type or "").lower()
        if "int" in text:
            return "int"
        if "bool" in text or "tinyint(1)" in text:
            return "bool"
        if "char" in text or "varchar" in text:
            return "varchar"
        if "text" in text or "clob" in text:
            return "text"
        if "real" in text or "double" in text or "float" in text or "numeric" in text or "decimal" in text:
            return "real"
        if "timestamp" in text or "datetime" in text:
            return "datetime"
        if "date" in text:
            return "date"
        if "json" in text:
            return "json"
        if "blob" in text or "bytea" in text:
            return "blob"
        return "text"


class SQLiteBackend(SQLBackend):
    engine = "sqlite"
    placeholder = "?"
    quote_char = '"'

    def open(self) -> None:
        path = str(self.settings.get("name", "data/app.db"))
        # Bases efímeras (tests, demos): no tocan el disco ni resuelven rutas.
        if path.startswith(":memory:") or path.startswith("file::memory:"):
            self._conn = sqlite3.connect(path, check_same_thread=False, timeout=10)
            self._conn.execute("PRAGMA foreign_keys = ON")
            self.path = Path(path)
            return
        target = Path(path)
        if not target.is_absolute():
            base = getattr(self.settings, "root", None)
            target = (Path(base) / target) if base else target
        target.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(target), check_same_thread=False, timeout=10)
        self._conn.execute("PRAGMA foreign_keys = ON")
        self.path = target

    def tables(self) -> dict[str, list[Column]]:
        cursor = self.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        )
        names = [row[0] for row in cursor.fetchall()]
        out: dict[str, list[Column]] = {}
        for name in names:
            info = self.execute(f"PRAGMA table_info({self.quote(name)})").fetchall()
            columns = []
            for _cid, column_name, column_type, notnull, default, primary_key in info:
                columns.append(
                    Column(
                        column_name,
                        self._logical_type(column_type),
                        null=not notnull,
                        primary_key=bool(primary_key),
                        auto=bool(primary_key) and "int" in (column_type or "").lower(),
                        default=default,
                    )
                )
            out[name] = columns
        return out

    def alter_column(self, table: str, column: Column, previous: Column) -> None:
        """SQLite no tiene ``ALTER COLUMN``: se reconstruye la tabla."""
        name = _check_ident(table)
        current = self.table_columns(name)
        previous_names = {item.name for item in current}
        replaced = [column if item.name == column.name else item for item in current]
        temp = f"{name}__new"
        self.drop_table(temp)
        self.create_table(temp, replaced)
        # Se copian todas las columnas que ya existían (la alterada incluida).
        keep = [item.name for item in replaced if item.name in previous_names]
        renamed = ", ".join(f"{self.quote(item)}" for item in keep)
        if keep:
            self.execute(
                f"INSERT INTO {self.quote(temp)} ({renamed}) "
                f"SELECT {renamed} FROM {self.quote(name)}"
            )
        self.drop_table(name)
        self.execute(f"ALTER TABLE {self.quote(temp)} RENAME TO {self.quote(name)}")
        self.commit()


class PostgresBackend(SQLBackend):
    engine = "postgres"
    placeholder = "%s"
    quote_char = '"'

    def open(self) -> None:
        try:
            import psycopg  # type: ignore
        except ModuleNotFoundError:
            try:
                import psycopg2 as psycopg  # type: ignore
            except ModuleNotFoundError as exc:
                raise DatabaseError(
                    'Falta el driver de PostgreSQL. Instálalo con: pip install "interui[postgres]"'
                ) from exc
        self._conn = psycopg.connect(
            host=self.settings.get("host", "localhost"),
            port=int(self.settings.get("port", 5432)),
            user=self.settings.get("user"),
            password=self.settings.get("password"),
            dbname=self.settings.get("name"),
        )

    def tables(self) -> dict[str, list[Column]]:
        cursor = self.execute(
            "SELECT table_name, column_name, data_type, is_nullable, column_default "
            "FROM information_schema.columns WHERE table_schema = 'public' ORDER BY ordinal_position"
        )
        out: dict[str, list[Column]] = {}
        for table, column, data_type, nullable, default in cursor.fetchall():
            out.setdefault(table, []).append(
                Column(column, self._logical_type(data_type), null=nullable == "YES", default=default)
            )
        return out

    def alter_column(self, table: str, column: Column, previous: Column) -> None:
        name = _check_ident(table)
        self.execute(
            f"ALTER TABLE {self.quote(name)} ALTER COLUMN {self.quote(column.name)} "
            f"TYPE {self.sql_type(column)}"
        )
        if column.null != previous.null:
            action = "DROP NOT NULL" if column.null else "SET NOT NULL"
            self.execute(
                f"ALTER TABLE {self.quote(name)} ALTER COLUMN {self.quote(column.name)} {action}"
            )
        self.commit()


class MySQLBackend(SQLBackend):
    engine = "mysql"
    placeholder = "%s"
    quote_char = "`"

    def open(self) -> None:
        try:
            import pymysql  # type: ignore
        except ModuleNotFoundError as exc:
            raise DatabaseError(
                'Falta el driver de MySQL. Instálalo con: pip install "interui[mysql]"'
            ) from exc
        self._conn = pymysql.connect(
            host=self.settings.get("host", "localhost"),
            port=int(self.settings.get("port", 3306)),
            user=self.settings.get("user"),
            password=self.settings.get("password", ""),
            database=self.settings.get("name"),
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True,
        )

    def tables(self) -> dict[str, list[Column]]:
        cursor = self.execute(
            "SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT "
            "FROM information_schema.columns WHERE table_schema = DATABASE() "
            "ORDER BY ORDINAL_POSITION"
        )
        out: dict[str, list[Column]] = {}
        for table, column, data_type, nullable, default in cursor.fetchall():
            out.setdefault(table, []).append(
                Column(column, self._logical_type(data_type), null=nullable == "YES", default=default)
            )
        return out

    def alter_column(self, table: str, column: Column, previous: Column) -> None:
        self.execute(
            f"ALTER TABLE {self.quote(_check_ident(table))} "
            f"MODIFY {self.column_sql(column)}"
        )
        self.commit()


# ---------------------------------------------------------------------------
# documentos (Mongo) y archivos JSON
# ---------------------------------------------------------------------------
class DocumentBackend(Backend):
    """Motores sin esquema: los tipos se validan en el ORM."""

    dialect = "document"

    def tables(self) -> dict[str, list[Column]]:
        return {name: [] for name in self.collection_names()}

    def create_table(self, table: str, columns: Iterable[Column]) -> None:
        self.create_collection(_check_ident(table), list(columns))

    def add_column(self, table: str, column: Column) -> None:
        """Sin esquema: no hay nada que migrar."""

    def remove_column(self, table: str, column: Column) -> None:
        self.unset_field(_check_ident(table), column.name)

    def alter_column(self, table: str, column: Column, previous: Column) -> None:
        """Sin esquema: nada que cambiar."""

    def collection_names(self) -> list[str]:  # pragma: no cover - cada motor
        raise NotImplementedError

    def create_collection(self, name: str, columns: list[Column]) -> None:  # pragma: no cover
        raise NotImplementedError

    def unset_field(self, table: str, field: str) -> None:
        for row in self.select(table):
            if field in row:
                pk = row.get(self.pk_name(table))
                self.update(table, pk, {field: None})

    def pk_name(self, table: str) -> str:
        return "id"


class MongoBackend(DocumentBackend):
    engine = "mongo"

    def open(self) -> None:
        try:
            import pymongo  # type: ignore
        except ModuleNotFoundError as exc:
            raise DatabaseError(
                'Falta el driver de MongoDB. Instálalo con: pip install "interui[mongo]"'
            ) from exc
        host = self.settings.get("host", "localhost")
        port = int(self.settings.get("port", 27017))
        self._client = pymongo.MongoClient(host, port, serverSelectionTimeoutMS=4000)
        self._db = self._client[self.settings.get("name", "interui")]

    def _ensure(self):
        if getattr(self, "_db", None) is None:
            self.open()
        return self._db

    def collection_names(self) -> list[str]:
        return list(self._ensure().list_collection_names())

    def create_collection(self, name: str, columns: list[Column]) -> None:
        database = self._ensure()
        if name not in database.list_collection_names():
            database.create_collection(name)
        unique = [column.name for column in columns if column.unique]
        if unique:
            database[name].create_index([(field, 1) for field in unique], unique=True)

    def insert(self, table: str, row: dict[str, Any]) -> Any:
        payload = {key: _to_storage(Column(key, "json" if isinstance(value, (dict, list)) else "text"), value)
                   for key, value in row.items()}
        result = self._ensure()[table].insert_one(payload)
        return row.get("id") or str(result.inserted_id)

    def update(self, table: str, pk: Any, row: dict[str, Any]) -> None:
        self._ensure()[table].update_one({"id": pk}, {"$set": row})

    def delete(self, table: str, pk: Any) -> None:
        self._ensure()[table].delete_one({"id": pk})

    def select(
        self,
        table: str,
        *,
        where: Sequence[tuple[str, str, Any]] | None = None,
        order: Sequence[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        for column, op, value in where or ():
            if op == "=":
                query[column] = value
            elif op == "in":
                query[column] = {"$in": list(value or [])}
            elif op in (">", ">=", "<", "<=", "!="):
                key = {"!=": "$ne"}.get(op, {"$" + op})
                query.setdefault(column, {}).update(key if isinstance(key, dict) else {op: value})
        cursor = self._ensure()[table].find(query, {"_id": 0})
        if order:
            cursor = cursor.sort([(term.lstrip("-"), -1 if term.startswith("-") else 1) for term in order])
        if offset:
            cursor = cursor.skip(int(offset))
        if limit is not None:
            cursor = cursor.limit(int(limit))
        return [dict(item) for item in cursor]


class FileBackend(DocumentBackend):
    """Una carpeta con un ``.json`` por tabla. Cero dependencias."""

    engine = "file"

    def __init__(self, settings: DatabaseSettings | Section) -> None:
        super().__init__(settings)
        base = getattr(settings, "root", None)
        folder = Path(self.settings.get("name", "data"))
        self.folder = folder if folder.is_absolute() or base is None else Path(base) / folder
        self.folder.mkdir(parents=True, exist_ok=True)

    def _path(self, table: str) -> Path:
        return self.folder / f"{_check_ident(table)}.json"

    def _read(self, table: str) -> list[dict[str, Any]]:
        path = self._path(table)
        if not path.is_file():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
        return data if isinstance(data, list) else []

    def _write(self, table: str, rows: list[dict[str, Any]]) -> None:
        self._path(table).write_text(
            json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def collection_names(self) -> list[str]:
        return sorted(path.stem for path in self.folder.glob("*.json"))

    def create_collection(self, name: str, columns: list[Column]) -> None:
        if not self._path(name).exists():
            self._write(name, [])

    def drop_table(self, table: str) -> None:
        self._path(table).unlink(missing_ok=True)

    def insert(self, table: str, row: dict[str, Any]) -> Any:
        rows = self._read(table)
        payload = dict(row)
        if payload.get("id") is None:
            payload["id"] = max((int(item.get("id") or 0) for item in rows), default=0) + 1
        ids = [item for item in rows if item.get("id") != payload["id"]]
        ids.append(payload)
        self._write(table, ids)
        return payload["id"]

    def update(self, table: str, pk: Any, row: dict[str, Any]) -> None:
        rows = self._read(table)
        for item in rows:
            if item.get("id") == pk:
                item.update({key: value for key, value in row.items() if key != "id"})
        self._write(table, rows)

    def delete(self, table: str, pk: Any) -> None:
        self._write(table, [item for item in self._read(table) if item.get("id") != pk])

    def select(
        self,
        table: str,
        *,
        where: Sequence[tuple[str, str, Any]] | None = None,
        order: Sequence[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[dict[str, Any]]:
        rows = self._read(table)
        for column, op, value in where or ():
            rows = [item for item in rows if _matches(item.get(column), op, value)]
        if order:
            for term in reversed(order):
                descending = term.startswith("-")
                key = term[1:] if descending else term
                rows.sort(key=lambda item: (item.get(key) is None, item.get(key)), reverse=descending)
        if offset:
            rows = rows[int(offset):]
        if limit is not None:
            rows = rows[: int(limit)]
        return rows

    def count(self, table: str, where: Sequence[tuple[str, str, Any]] | None = None) -> int:
        return len(self.select(table, where=where))


def _matches(value: Any, op: str, expected: Any) -> bool:
    if op == "=":
        return value == expected
    if op == "!=":
        return value != expected
    if op == "in":
        return value in (expected or [])
    if value is None:
        return False
    try:
        if op == ">":
            return value > expected
        if op == ">=":
            return value >= expected
        if op == "<":
            return value < expected
        if op == "<=":
            return value <= expected
    except TypeError:
        return False
    if op == "like":
        return str(expected).strip("%") in str(value)
    if op == "not like":
        return str(expected).strip("%") not in str(value)
    return False


_BACKENDS: dict[str, Backend] = {}


def connect(settings: DatabaseSettings | Section | str | None = None) -> Backend:
    """Crea el backend del motor indicado (sin registrarlo)."""
    if settings is None:
        from . import config as config_module

        settings = config_module.load().database()
    if isinstance(settings, str):
        from . import config as config_module

        settings = config_module.load().database(settings)
    engine = str(settings.get("engine", "sqlite")).lower()
    classes = {
        "sqlite": SQLiteBackend,
        "postgres": PostgresBackend,
        "mysql": MySQLBackend,
        "mongo": MongoBackend,
        "file": FileBackend,
    }
    if engine not in classes:
        raise DatabaseError(
            f"motor desconocido: {engine!r}; disponibles: {', '.join(sorted(classes))}"
        )
    info = ENGINES.get(engine, {})
    driver = info.get("driver")
    if driver and importlib.util.find_spec(driver) is None:
        raise DatabaseError(
            f"El motor «{engine}» necesita el driver «{driver}». "
            f"Instálalo con: {info.get('install')}"
        )
    backend = classes[engine](settings)
    return backend


def configure(config: Any, *, aliases: Iterable[str] | None = None) -> dict[str, Backend]:
    """Registra las bases de datos de una configuración y devuelve el mapa."""
    reset()
    for alias, settings in config.databases_map().items():
        if aliases is not None and alias not in aliases:
            continue
        settings.root = config.root  # type: ignore[attr-defined]
        _BACKENDS[alias] = connect(settings)
    return dict(_BACKENDS)


def backend(alias: str = "default") -> Backend:
    """Backend registrado con :func:`configure` (se conecta al primer uso)."""
    if alias not in _BACKENDS:
        from . import config as config_module

        found = config_module.find_config()
        if found is None:
            raise DatabaseError(
                "No hay base de datos configurada: crea interui.json con «interui init» "
                "o llama a interui.db.configure(config)."
            )
        configure(config_module.load(found))
        if alias not in _BACKENDS:
            raise DatabaseError(f"No hay una base de datos «{alias}» en interui.json")
    return _BACKENDS[alias]


def reset() -> None:
    """Cierra y olvida los backends registrados (útil en tests)."""
    for item in _BACKENDS.values():
        try:
            item.close()
        except Exception:  # noqa: BLE001 - cerrar nunca debe romper
            pass
    _BACKENDS.clear()
