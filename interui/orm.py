"""Modelos declarativos al estilo de Django, sobre cualquier motor.

.. code-block:: python

    import interui as ui

    class Cliente(ui.Model):
        nombre = ui.Str(max_length=80, unique=True)
        email = ui.Str(max_length=120, null=True)
        edad = ui.Int(null=True)
        activo = ui.Bool(default=True)
        creado = ui.DateTime(auto_now_add=True)

        class Meta:
            table = "clientes"

    Cliente.objects.create(nombre="Ana", edad=34)
    Cliente.objects.filter(edad__gte=18).order_by("-edad")
    ana = Cliente.objects.get(nombre="Ana")
    ana.edad = 35
    ana.save()
    ana.delete()

El motor (SQLite, PostgreSQL, MySQL, MongoDB o archivos) sale de
``interui.json``; aquí solo se declaran campos. Las migraciones comparan estos
modelos con la última migración y generan el SQL/operaciones necesarias.
"""

from __future__ import annotations

import datetime as _dt
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Iterator, Sequence

from . import db as _db
from .db import Column, DatabaseError

__all__ = [
    "Auto",
    "Blob",
    "Bool",
    "Date",
    "DateTime",
    "Field",
    "Float",
    "FK",
    "Int",
    "Json",
    "LongText",
    "Manager",
    "Model",
    "ModelMeta",
    "QuerySet",
    "Str",
    "Text",
    "declared_models",
]

_MISSING = object()


# ---------------------------------------------------------------------------
# campos
# ---------------------------------------------------------------------------
class Field:
    """Campo de un modelo. Se convierte en una columna al migrar."""

    type = "text"

    def __init__(
        self,
        *,
        null: bool = False,
        unique: bool = False,
        default: Any = _MISSING,
        primary_key: bool = False,
        auto: bool = False,
        max_length: int | None = None,
        column: str | None = None,
        auto_now_add: bool = False,
        auto_now: bool = False,
    ) -> None:
        self.name: str | None = None
        self.null = null
        self.unique = unique
        self.default = default
        self.primary_key = primary_key
        self.auto = auto
        self.max_length = max_length
        self.column = column
        self.auto_now_add = auto_now_add
        self.auto_now = auto_now

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = self.name or name

    # -- valores ---------------------------------------------------------
    def get_default(self) -> Any:
        if self.default is _MISSING:
            return None
        return self.default() if callable(self.default) else self.default

    def to_python(self, value: Any) -> Any:
        return value

    def to_db(self, value: Any) -> Any:
        return value

    # -- esquema ---------------------------------------------------------
    def to_column(self) -> Column:
        return Column(
            self.column or self.name or "",
            self.type,
            null=self.null and not self.primary_key,
            unique=self.unique,
            primary_key=self.primary_key,
            auto=self.auto,
            default=None if callable(self.default) or self.default is _MISSING else self.default,
            max_length=self.max_length,
        )

    def describe(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "null": self.null and not self.primary_key,
            "unique": self.unique,
            "primary_key": self.primary_key,
            "auto": self.auto,
            "max_length": self.max_length,
            "default": None if callable(self.default) or self.default is _MISSING else self.default,
        }

    def __repr__(self) -> str:  # pragma: no cover - ayuda al depurar
        return f"<{type(self).__name__} {self.name}>"


class Auto(Field):
    """Clave primaria autoincremental. Se añade sola si no declaras ninguna."""

    type = "int"

    def __init__(self, **kwargs: Any) -> None:
        kwargs.setdefault("primary_key", True)
        kwargs.setdefault("auto", True)
        kwargs.setdefault("null", False)
        super().__init__(**kwargs)


class Int(Field):
    type = "int"

    def to_python(self, value: Any) -> Any:
        return None if value is None else int(value)


class Str(Field):
    type = "varchar"

    def __init__(self, *, max_length: int = 255, **kwargs: Any) -> None:
        super().__init__(max_length=max_length, **kwargs)

    def to_python(self, value: Any) -> Any:
        return None if value is None else str(value)


class LongText(Field):
    """Texto largo (``TEXT``). Se llama ``LongText`` porque ``Text`` es el control."""

    type = "text"

    def to_python(self, value: Any) -> Any:
        return None if value is None else str(value)


#: Alias dentro de :mod:`interui.orm` (a nivel de paquete se exporta ``LongText``).
Text = LongText


class Bool(Field):
    type = "bool"

    def to_python(self, value: Any) -> Any:
        return None if value is None else bool(value)


class Float(Field):
    type = "real"

    def to_python(self, value: Any) -> Any:
        return None if value is None else float(value)


class Date(Field):
    type = "date"

    def to_python(self, value: Any) -> Any:
        if isinstance(value, _dt.datetime):
            return value.date()
        if isinstance(value, _dt.date) or value is None:
            return value
        return _dt.date.fromisoformat(str(value)[:10])

    def to_db(self, value: Any) -> Any:
        return value.isoformat() if isinstance(value, _dt.date) else value


class DateTime(Field):
    type = "datetime"

    def to_python(self, value: Any) -> Any:
        if isinstance(value, _dt.datetime) or value is None:
            return value
        text = str(value).replace("T", " ")
        try:
            return _dt.datetime.fromisoformat(text)
        except ValueError:
            return value

    def to_db(self, value: Any) -> Any:
        return value.isoformat(sep=" ") if isinstance(value, _dt.datetime) else value


class Json(Field):
    type = "json"

    def to_python(self, value: Any) -> Any:
        if isinstance(value, (str, bytes)):
            try:
                return json.loads(value)
            except (TypeError, ValueError):
                return value
        return value

    def to_db(self, value: Any) -> Any:
        return json.dumps(value, ensure_ascii=False)


class Blob(Field):
    type = "blob"


class FK(Int):
    """Referencia a otra tabla (``FK("clientes")``), sin integridad automática."""

    def __init__(self, target: str | type | None = None, **kwargs: Any) -> None:
        self.target = target if isinstance(target, str) else getattr(target, "__name__", None)
        super().__init__(**kwargs)

    def describe(self) -> dict[str, Any]:
        data = super().describe()
        data["target"] = self.target
        return data


# ---------------------------------------------------------------------------
# metaclase
# ---------------------------------------------------------------------------
class ModelMeta(type):
    def __new__(mcls, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> "ModelMeta":
        cls = super().__new__(mcls, name, bases, namespace)
        fields: dict[str, Field] = {}
        for base in reversed(bases):
            fields.update({key: field for key, field in getattr(base, "_fields", {}).items()})
        for key, value in list(namespace.items()):
            if isinstance(value, Field):
                value.name = value.name or key
                fields[key] = value
        if not any(field.primary_key for field in fields.values()):
            auto = Auto()
            auto.name = "id"
            fields = {"id": auto, **fields}
            setattr(cls, "id", auto)
        for key, field in fields.items():
            if getattr(cls, key, None) is not field:
                setattr(cls, key, field)
        cls._fields = fields
        meta = namespace.get("Meta")
        cls._table = getattr(meta, "table", None) or f"{name.lower()}s"
        cls._database = getattr(meta, "database", None) or "default"
        cls._order = getattr(meta, "order", None) or []
        return cls

    @property
    def table(cls) -> str:
        return cls._table

    def __repr__(cls) -> str:  # pragma: no cover - ayuda al depurar
        return f"<Model {cls.__name__}>"


# ---------------------------------------------------------------------------
# consultas
# ---------------------------------------------------------------------------
_OPERATORS = {
    "exact": "=",
    "eq": "=",
    "ne": "!=",
    "gt": ">",
    "gte": ">=",
    "lt": "<",
    "lte": "<=",
    "in": "in",
}


def _parse_filters(
    kwargs: dict[str, Any], model: "type[Model] | None" = None
) -> list[tuple[str, str, Any]]:
    where: list[tuple[str, str, Any]] = []
    for key, value in kwargs.items():
        name, _, suffix = key.partition("__")
        if model is not None:
            name = model._column_for(name)
        if not suffix:
            where.append((name, "=", value))
            continue
        if suffix in _OPERATORS:
            where.append((name, _OPERATORS[suffix], value))
        elif suffix == "contains":
            where.append((name, "like", f"%{value}%"))
        elif suffix == "startswith":
            where.append((name, "like", f"{value}%"))
        elif suffix == "endswith":
            where.append((name, "like", f"%{value}"))
        elif suffix == "isnull":
            where.append((name, "is null" if value else "is not null", None))
        else:
            raise DatabaseError(f"filtro no soportado: {key}")
    return where


class QuerySet:
    """Consulta diferida; se ejecuta al iterar, contar o pedir un objeto."""

    def __init__(
        self,
        model: type["Model"],
        where: Sequence[tuple[str, str, Any]] | None = None,
        order: Sequence[str] | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> None:
        self.model = model
        self._where = list(where or [])
        self._order = list(order or model._order)
        self._limit = limit
        self._offset = offset

    # -- construcción ----------------------------------------------------
    def filter(self, **kwargs: Any) -> "QuerySet":
        return QuerySet(
            self.model,
            [*self._where, *_parse_filters(kwargs, self.model)],
            self._order,
            self._limit,
            self._offset,
        )

    def order_by(self, *fields: str) -> "QuerySet":
        return QuerySet(self.model, self._where, list(fields), self._limit, self._offset)

    def limit(self, value: int) -> "QuerySet":
        return QuerySet(self.model, self._where, self._order, value, self._offset)

    def offset(self, value: int) -> "QuerySet":
        return QuerySet(self.model, self._where, self._order, self._limit, value)

    # -- ejecución -------------------------------------------------------
    @property
    def _backend(self) -> _db.Backend:
        return _db.backend(self.model._database)

    def __iter__(self) -> Iterator["Model"]:
        for row in self._rows():
            yield self.model._from_row(row)

    def __len__(self) -> int:
        return self.count()

    def __repr__(self) -> str:  # pragma: no cover - ayuda al depurar
        return f"<QuerySet {self.model.__name__} {self._where or ''}>"

    def _rows(self) -> list[dict[str, Any]]:
        return self._backend.select(
            self.model._table,
            where=self._where,
            order=self._order,
            limit=self._limit,
            offset=self._offset,
        )

    def all(self) -> list["Model"]:
        return list(self)

    def first(self) -> "Model | None":
        rows = QuerySet(self.model, self._where, self._order, 1, self._offset)._rows()
        return self.model._from_row(rows[0]) if rows else None

    def last(self) -> "Model | None":
        """Último de la consulta (invierte el orden actual)."""
        if not self._order:
            pk = self.model._pk_field()
            order = [f"-{pk.column or pk.name}"]
        else:
            order = [term[1:] if term.startswith("-") else f"-{term}" for term in self._order]
        rows = QuerySet(self.model, self._where, order, 1, 0)._rows()
        return self.model._from_row(rows[0]) if rows else None

    def get(self, **kwargs: Any) -> "Model":
        rows = (self.filter(**kwargs) if kwargs else self).limit(2)._rows()
        if not rows:
            raise self.model.DoesNotExist(
                f"No existe {self.model.__name__} con {kwargs or self._where}"
            )
        if len(rows) > 1:
            raise self.model.MultipleObjectsReturned(
                f"Hay más de un {self.model.__name__} con {kwargs or self._where}"
            )
        return self.model._from_row(rows[0])

    def count(self) -> int:
        if self._limit is not None or self._offset:
            return len(self._rows())
        return self._backend.count(self.model._table, self._where)

    def exists(self) -> bool:
        return bool(self._rows())

    def delete(self) -> int:
        total = 0
        for item in self:
            item.delete()
            total += 1
        return total

    def values(self) -> list[dict[str, Any]]:
        return self._rows()

    def create(self, **kwargs: Any) -> "Model":
        return self.model.objects.create(**kwargs)

    def update(self, **kwargs: Any) -> int:
        total = 0
        for item in self:
            for key, value in kwargs.items():
                setattr(item, key, value)
            item.save()
            total += 1
        return total


class Manager:
    """``Model.objects``: puerta de entrada a las consultas."""

    def __init__(self, model: type["Model"] | None = None) -> None:
        self.model = model

    def __get__(self, instance: Any, owner: type["Model"] | None = None) -> "Manager":
        return Manager(owner) if owner is not None else self

    def all(self) -> QuerySet:
        assert self.model is not None
        return QuerySet(self.model)

    def filter(self, **kwargs: Any) -> QuerySet:
        return self.all().filter(**kwargs)

    def exclude(self, **kwargs: Any) -> "_Exclude":
        rows = self.all()
        banned = {item.pk for item in rows.filter(**kwargs)}
        return _Exclude(self.model, rows, banned)

    def get(self, **kwargs: Any) -> "Model":
        return self.all().get(**kwargs)

    def order_by(self, *fields: str) -> QuerySet:
        return self.all().order_by(*fields)

    def first(self) -> "Model | None":
        return self.all().first()

    def count(self) -> int:
        return self.all().count()

    def exists(self) -> bool:
        return self.all().exists()

    def create(self, **kwargs: Any) -> "Model":
        item = self.model(**kwargs)
        item.save()
        return item

    def bulk_create(self, items: Iterable["Model"]) -> list["Model"]:
        out = []
        for item in items:
            item.save()
            out.append(item)
        return out


class _Exclude:
    """``exclude()`` resuelto en Python (el resto de filtros va al motor)."""

    def __init__(self, model: type["Model"], source: QuerySet, banned: set[Any]) -> None:
        self.model = model
        self._source = source
        self._banned = banned

    def __iter__(self) -> Iterator["Model"]:
        for item in self._source:
            if item.pk not in self._banned:
                yield item

    def all(self) -> list["Model"]:
        return list(self)

    def count(self) -> int:
        return sum(1 for _ in self)

    def __len__(self) -> int:
        return self.count()


# ---------------------------------------------------------------------------
# modelo
# ---------------------------------------------------------------------------
class DoesNotExist(Exception):
    pass


class MultipleObjectsReturned(Exception):
    pass


class Model(metaclass=ModelMeta):
    """Base de todos los modelos."""

    DoesNotExist = DoesNotExist
    MultipleObjectsReturned = MultipleObjectsReturned

    objects = Manager()

    def __init__(self, **kwargs: Any) -> None:
        names = set(self._fields)
        unknown = set(kwargs) - names
        if unknown:
            raise TypeError(f"{type(self).__name__} no tiene {', '.join(sorted(unknown))}")
        for name, field in self._fields.items():
            if name in kwargs:
                setattr(self, name, field.to_python(kwargs[name]))
            elif field.auto:
                setattr(self, name, None)
            else:
                setattr(self, name, field.get_default())

    # -- utilidades ------------------------------------------------------
    @classmethod
    def _pk_field(cls) -> Field:
        for field in cls._fields.values():
            if field.primary_key:
                return field
        return next(iter(cls._fields.values()))

    def _get_pk(self) -> Any:
        return getattr(self, self._pk_field().name or "id", None)

    def _set_pk(self, value: Any) -> None:
        setattr(self, self._pk_field().name or "id", value)

    pk = property(_get_pk, _set_pk)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Model) or type(other) is not type(self):
            return NotImplemented
        return self.pk is not None and self.pk == other.pk

    def __hash__(self) -> int:
        return hash((type(self).__name__, self.pk))

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {self.pk}>"

    def __str__(self) -> str:
        return f"{type(self).__name__} {self.pk}"

    def to_dict(self) -> dict[str, Any]:
        return {name: getattr(self, name, None) for name in self._fields}

    @classmethod
    def _from_row(cls, row: dict[str, Any]) -> "Model":
        item = cls.__new__(cls)
        for name, field in cls._fields.items():
            setattr(item, name, field.to_python(row.get(field.column or name)))
        return item

    @classmethod
    def _column_for(cls, name: str) -> str:
        """``pk`` y los nombres de campo se traducen al nombre real de columna."""
        if name == "pk":
            field = cls._pk_field()
            return field.column or field.name or "id"
        field = cls._fields.get(name)
        if field is None:
            raise DatabaseError(
                f"{cls.__name__} no tiene el campo «{name}»; "
                f"disponibles: {', '.join(cls._fields)}"
            )
        return field.column or field.name or name

    @classmethod
    def columns(cls) -> list[Column]:
        return [field.to_column() for field in cls._fields.values()]

    @classmethod
    def state(cls) -> dict[str, Any]:
        """Esquema declarado, tal como lo guardan las migraciones."""
        return {
            "table": cls._table,
            "database": cls._database,
            "fields": {name: field.describe() for name, field in cls._fields.items()},
        }

    # -- persistencia ----------------------------------------------------
    def save(self) -> "Model":
        now = _dt.datetime.now().replace(microsecond=0)
        for name, field in self._fields.items():
            if field.auto_now or (field.auto_now_add and self.pk is None):
                setattr(self, name, now)
        alias = type(self)._database
        backend = _db.backend(alias)
        data = {
            name: field.to_db(getattr(self, name, None))
            for name, field in self._fields.items()
            if not (field.auto and getattr(self, name, None) is None)
        }
        if self.pk is None:
            new_pk = backend.insert(type(self)._table, data)
            if self.pk is None and new_pk is not None:
                self.pk = new_pk
        else:
            backend.update(type(self)._table, self.pk, data)
        return self

    def delete(self) -> None:
        if self.pk is None:
            return
        _db.backend(type(self)._database).delete(type(self)._table, self.pk)
        self.pk = None

    def refresh(self) -> "Model":
        fresh = type(self).objects.get(pk=self.pk)
        for name in self._fields:
            setattr(self, name, getattr(fresh, name))
        return self


# ---------------------------------------------------------------------------
# carga de models.py
# ---------------------------------------------------------------------------
def declared_models(path: str | Path, base: type[Model] = Model) -> list[type[Model]]:
    """Importa un ``models.py`` y devuelve sus modelos en orden de declaración."""
    target = Path(path)
    if not target.is_file():
        raise DatabaseError(f"No existe el archivo de modelos: {target}")
    name = f"interui_models_{abs(hash(str(target.resolve())))}"
    spec = importlib.util.spec_from_file_location(name, target)
    if spec is None or spec.loader is None:
        raise DatabaseError(f"No se pudo cargar {target}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    models: list[type[Model]] = []
    for value in vars(module).values():
        if (
            isinstance(value, type)
            and issubclass(value, base)
            and value is not base
            and value.__module__ == name
        ):
            models.append(value)
    return models


def model_state(models: Sequence[type[Model]]) -> dict[str, Any]:
    """Estado de esquema de todos los modelos (lo que leen las migraciones)."""
    state: dict[str, Any] = {}
    for model in models:
        info = model.state()
        state[info["table"]] = {
            "database": info["database"],
            "fields": info["fields"],
        }
    return state
