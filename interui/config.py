"""Configuración del proyecto: ``interui.json``, el punto de partida de la app.

Es un archivo JSON (no un ``.env``) con secciones claras y acceso por puntos:

.. code-block:: python

    from interui import config

    config.app.name                 # "Mi tienda"
    config.databases.default.engine # "sqlite"
    config.database().url           # "sqlite:///data/app.db"

Los valores pueden referenciar variables de entorno con ``${VAR}`` (o
``${VAR:valor_por_defecto}``), así que los secretos no viven en el JSON.

El archivo lo genera el asistente de consola (``interui init``) y lo lee el resto
del framework: ``App.from_config()``, ``interui.db``, ``interui.orm`` y
``interui.migrations``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Iterable

__all__ = [
    "CONFIG_NAME",
    "Config",
    "ConfigError",
    "ENGINES",
    "Section",
    "find_config",
    "load",
]

CONFIG_NAME = "interui.json"

_ENV = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::([^}]*))?\}")


class ConfigError(RuntimeError):
    """El ``interui.json`` no existe, no es válido o le falta algo."""


# ---------------------------------------------------------------------------
# motores disponibles (los usa el asistente de consola y la validación)
# ---------------------------------------------------------------------------
ENGINES: dict[str, dict[str, Any]] = {
    "sqlite": {
        "label": "SQLite (un archivo, sin servidor)",
        "driver": None,
        "fields": ["name"],
        "defaults": {"name": "data/app.db"},
        "extra": None,
    },
    "postgres": {
        "label": "PostgreSQL",
        "driver": "psycopg",
        "fields": ["host", "port", "user", "password", "name"],
        "defaults": {"host": "localhost", "port": 5432, "user": "postgres", "name": "postgres"},
        "extra": "postgres",
        "install": 'pip install "interui[postgres]"',
    },
    "mysql": {
        "label": "MySQL / MariaDB",
        "driver": "pymysql",
        "fields": ["host", "port", "user", "password", "name"],
        "defaults": {"host": "localhost", "port": 3306, "user": "root", "name": "mysql"},
        "extra": "mysql",
        "install": 'pip install "interui[mysql]"',
    },
    "mongo": {
        "label": "MongoDB",
        "driver": "pymongo",
        "fields": ["host", "port", "name"],
        "defaults": {"host": "localhost", "port": 27017, "name": "interui"},
        "extra": "mongo",
        "install": 'pip install "interui[mongo]"',
    },
    "file": {
        "label": "Archivos JSON (sin servidor)",
        "driver": None,
        "fields": ["name"],
        "defaults": {"name": "data"},
        "extra": None,
    },
}

DEFAULT_CONFIG: dict[str, Any] = {
    "app": {
        "name": "Mi app",
        "version": "0.1.0",
        "theme": "light",
        "width": 1180,
        "height": 780,
        "entry": "app.py",
        "debug": False,
    },
    "databases": {
        "default": {"engine": "sqlite", "name": "data/app.db"},
    },
    "migrations": {
        "directory": "migrations",
        "models": "models.py",
    },
}


# ---------------------------------------------------------------------------
# diccionario con acceso por puntos
# ---------------------------------------------------------------------------
def _wrap(value: Any) -> Any:
    """Convierte diccionarios anidados en ``Section`` **una sola vez**."""
    if isinstance(value, dict) and not isinstance(value, Section):
        return Section(value)
    if isinstance(value, list):
        return [_wrap(item) for item in value]
    return value


def _plain(value: Any) -> Any:
    if isinstance(value, Section):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_plain(item) for item in value]
    return value


class Section(dict):
    """``dict`` con acceso por puntos: ``config.app.name``.

    Los diccionarios anidados se convierten una sola vez, así que
    ``config.app.name = "Otra"`` modifica la configuración de verdad.
    """

    def __init__(self, data: dict[str, Any] | None = None, **kwargs: Any) -> None:
        super().__init__()
        for key, value in {**(data or {}), **kwargs}.items():
            dict.__setitem__(self, key, _wrap(value))

    def __getattr__(self, name: str) -> Any:
        if name.startswith("__"):
            raise AttributeError(name)
        try:
            return self[name]
        except KeyError:
            raise AttributeError(
                f"«{name}» no existe en la configuración; claves: {', '.join(map(str, self))}"
            ) from None

    def __setattr__(self, name: str, value: Any) -> None:
        attribute = getattr(type(self), name, None)
        if name.startswith("_") or isinstance(attribute, property):
            object.__setattr__(self, name, value)
        else:
            dict.__setitem__(self, name, _wrap(value))

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name) from None

    def to_dict(self) -> dict[str, Any]:
        return _plain(self)


# ---------------------------------------------------------------------------
# interpolación de variables de entorno
# ---------------------------------------------------------------------------
def _expand(value: Any) -> Any:
    if isinstance(value, str):

        def replace(match: re.Match[str]) -> str:
            variable, fallback = match.group(1), match.group(2)
            return os.environ.get(variable, fallback if fallback is not None else match.group(0))

        return _ENV.sub(replace, value)
    if isinstance(value, dict):
        return {key: _expand(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand(item) for item in value]
    return value


def _merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    out = dict(base)
    for key, value in override.items():
        # ``databases`` se reemplaza entero: si defines las tuyas, las tuyas mandan.
        if key == "databases":
            out[key] = value
        elif isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = value
    return out


# ---------------------------------------------------------------------------
# búsqueda del archivo
# ---------------------------------------------------------------------------
def find_config(start: str | Path | None = None) -> Path | None:
    """Busca ``interui.json`` desde ``start`` hacia arriba."""
    current = Path(start or Path.cwd()).resolve()
    if current.is_file():
        current = current.parent
    for folder in (current, *current.parents):
        candidate = folder / CONFIG_NAME
        if candidate.is_file():
            return candidate
    return None


class DatabaseSettings(Section):
    """Una base de datos declarada en ``databases``."""

    def __init__(
        self,
        data: dict[str, Any] | None = None,
        alias: str = "default",
        root: Path | None = None,
    ) -> None:
        super().__init__(data)
        self._alias = alias
        self._root = root

    @property
    def alias(self) -> str:
        return self._alias

    def _get_root(self) -> Path | None:
        return self._root

    def _set_root(self, value: Path | None) -> None:
        object.__setattr__(self, "_root", value)

    root = property(_get_root, _set_root)

    @property
    def engine(self) -> str:
        return str(self.get("engine", "sqlite"))

    @property
    def name(self) -> str:
        return str(self.get("name", ""))

    @property
    def url(self) -> str:
        """URL legible (estilo SQLAlchemy) para mostrar en logs y docs."""
        engine = self.engine
        if engine == "sqlite":
            return f"sqlite:///{self.name}"
        if engine == "file":
            return f"file://{self.name}"
        if engine == "mongo":
            return f"mongodb://{self.get('host', 'localhost')}:{self.get('port', 27017)}/{self.name}"
        driver = "postgresql" if engine == "postgres" else engine
        user = self.get("user", "")
        password = self.get("password", "")
        auth = f"{user}:{password}@" if password else (f"{user}@" if user else "")
        return f"{driver}://{auth}{self.get('host', 'localhost')}:{self.get('port')}/{self.name}"

    def describe(self) -> str:
        return f"{self.alias}: {self.engine} · {self.url}"


class Config(Section):
    """La configuración completa del proyecto."""

    path: Path | None = None

    # -- carga y guardado ------------------------------------------------
    @classmethod
    def load(cls, path: str | Path | None = None, *, required: bool = True) -> "Config":
        if path is None:
            found = find_config()
            if found is None:
                if required:
                    raise ConfigError(
                        f"No se encontró {CONFIG_NAME}. Créalo con «interui init»."
                    )
                return cls(DEFAULT_CONFIG)
            path = found
        target = Path(path)
        if target.is_dir():
            target = target / CONFIG_NAME
        if not target.is_file():
            if required:
                raise ConfigError(f"No existe {target}")
            config = cls(DEFAULT_CONFIG, path=target)
            return config
        try:
            raw = json.loads(target.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ConfigError(f"{target}: JSON inválido en la línea {exc.lineno}: {exc.msg}") from exc
        if not isinstance(raw, dict):
            raise ConfigError(f"{target}: la raíz debe ser un objeto JSON")
        config = cls(_expand(_merge(DEFAULT_CONFIG, raw)), path=target)
        config.validate()
        return config

    @classmethod
    def default(cls) -> "Config":
        """Configuración por defecto sin tocar el disco."""
        return cls(DEFAULT_CONFIG)

    def __init__(self, data: dict[str, Any], path: Path | None = None) -> None:
        super().__init__(data)
        self._file = Path(path) if path is not None else None
        databases = self.get("databases") or {}
        if isinstance(databases, dict):
            wrapped = Section(
                {
                    alias: DatabaseSettings(settings, alias, self.root)
                    for alias, settings in databases.items()
                }
            )
            dict.__setitem__(self, "databases", wrapped)

    def _get_path(self) -> Path | None:
        return self._file

    def _set_path(self, value: Path | None) -> None:
        object.__setattr__(self, "_file", Path(value) if value is not None else None)

    path = property(_get_path, _set_path)

    def save(self, path: str | Path | None = None) -> Path:
        target = Path(path) if path is not None else self.path
        if target is None:
            raise ConfigError("La configuración no tiene ruta; pasa una a save()")
        if target.is_dir():
            target = target / CONFIG_NAME
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
        )
        self.path = target
        return target

    # -- validación ------------------------------------------------------
    def validate(self) -> "Config":
        databases = self.get("databases")
        if not isinstance(databases, dict) or not databases:
            raise ConfigError("Falta la sección «databases» (al menos «default»).")
        for alias, settings in databases.items():
            engine = str(settings.get("engine", "")).lower()
            if engine not in ENGINES:
                raise ConfigError(
                    f"databases.{alias}.engine={engine!r} no es válido; "
                    f"usa {', '.join(sorted(ENGINES))}"
                )
            missing = [
                field
                for field in ENGINES[engine]["fields"]
                if field not in settings and field not in ("port", "password", "user", "host")
            ]
            if missing:
                raise ConfigError(f"databases.{alias}: faltan {', '.join(missing)}")
        if "default" not in databases:
            raise ConfigError("Falta «databases.default».")
        return self

    # -- acceso ----------------------------------------------------------
    @property
    def root(self) -> Path:
        """Carpeta del proyecto (donde está el JSON)."""
        return self.path.parent if self.path is not None else Path.cwd()

    def resolve(self, relative: str | Path) -> Path:
        """Convierte una ruta relativa del JSON en absoluta."""
        target = Path(relative)
        return target if target.is_absolute() else (self.root / target)

    def database(self, alias: str = "default") -> DatabaseSettings:
        databases = self.get("databases") or {}
        if alias not in databases:
            raise ConfigError(f"No hay una base de datos «{alias}» en {CONFIG_NAME}")
        settings = databases[alias]
        if not isinstance(settings, DatabaseSettings):
            settings = DatabaseSettings(settings, alias, self.root)
        settings.root = self.root
        return settings

    def databases_map(self) -> dict[str, DatabaseSettings]:
        return {alias: self.database(alias) for alias in (self.get("databases") or {})}

    def app_options(self) -> dict[str, Any]:
        """Argumentos para construir ``App`` desde la configuración."""
        app = self.get("app") or {}
        options: dict[str, Any] = {}
        title = app.get("title") or app.get("name")
        if title:
            options["title"] = title
        for key in ("theme", "width", "height", "dev"):
            if key in app:
                options[key] = app[key]
        return options

    def model_classes(self) -> Iterable[type]:
        """Importa ``migrations.models`` y devuelve las clases ``Model``."""
        from .orm import Model, declared_models

        relative = (self.get("migrations") or {}).get("models", "models.py")
        target = self.resolve(relative)
        if not target.is_file():
            raise ConfigError(f"No existe el archivo de modelos {target}")
        return declared_models(target, Model)


def load(path: str | Path | None = None, *, required: bool = True) -> Config:
    """Atajo de :meth:`Config.load`."""
    return Config.load(path, required=required)
