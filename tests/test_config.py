"""``interui.json``: el punto de partida del proyecto."""

from __future__ import annotations

import json

import pytest

import interui as ui
from interui.config import CONFIG_NAME, Config, ConfigError, find_config


def write(path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@pytest.fixture
def project(tmp_path):
    data = {
        "app": {"name": "Tienda", "theme": "dark"},
        "databases": {"default": {"engine": "sqlite", "name": "data/app.db"}},
    }
    write(tmp_path / CONFIG_NAME, data)
    return tmp_path


def test_acceso_por_puntos(project):
    config = Config.load(project / CONFIG_NAME)
    assert config.app.name == "Tienda"
    assert config.databases.default.engine == "sqlite"
    assert config.app.theme == "dark"


def test_valores_por_defecto_se_mezclan(project):
    config = Config.load(project / CONFIG_NAME)
    assert config.app.width == 1180          # del DEFAULT_CONFIG
    assert config.app.name == "Tienda"       # del archivo


def test_clave_inexistente_falla_claro(project):
    config = Config.load(project / CONFIG_NAME)
    with pytest.raises(AttributeError):
        _ = config.app.no_existe


def test_variables_de_entorno(monkeypatch, tmp_path):
    monkeypatch.setenv("PG_PASSWORD", "secreto")
    data = {
        "databases": {
            "default": {"engine": "sqlite", "name": "data/app.db"},
            "pg": {
                "engine": "postgres", "host": "${PG_HOST:localhost}", "port": 5432,
                "user": "app", "password": "${PG_PASSWORD}", "name": "tienda",
            },
        }
    }
    write(tmp_path / CONFIG_NAME, data)
    config = Config.load(tmp_path / CONFIG_NAME)
    assert config.databases.pg.password == "secreto"
    assert config.databases.pg.host == "localhost"
    assert config.databases.pg.url.startswith("postgresql://app:secreto@localhost:5432/tienda")


def test_guardar_y_recargar(project):
    config = Config.load(project / CONFIG_NAME)
    config.app.title = "Tienda · panel"
    config.save()
    again = Config.load(project / CONFIG_NAME)
    assert again.app.title == "Tienda · panel"


def test_motor_desconocido(tmp_path):
    write(
        tmp_path / CONFIG_NAME,
        {"databases": {"default": {"engine": "oracle", "name": "x"}}},
    )
    with pytest.raises(ConfigError) as info:
        Config.load(tmp_path / CONFIG_NAME)
    assert "oracle" in str(info.value)


def test_falta_default(tmp_path):
    write(tmp_path / CONFIG_NAME, {"databases": {"otra": {"engine": "file", "name": "d"}}})
    with pytest.raises(ConfigError):
        Config.load(tmp_path / CONFIG_NAME)


def test_busqueda_hacia_arriba(project):
    nested = project / "app" / "vistas"
    nested.mkdir(parents=True)
    assert find_config(nested) == project / CONFIG_NAME


def test_sin_archivo_es_error_claro(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with pytest.raises(ConfigError):
        Config.load()


def test_app_options_para_el_app(project):
    config = Config.load(project / CONFIG_NAME)
    options = config.app_options()
    assert options["title"] == "Tienda"
    assert options["theme"] == "dark"


def test_from_config(tmp_path):
    write(
        tmp_path / CONFIG_NAME,
        {
            "app": {"name": "Demo", "theme": "dark", "width": 900},
            "databases": {"default": {"engine": "file", "name": "datos"}},
        },
    )
    app = ui.App.from_config(tmp_path / CONFIG_NAME)
    assert app.title == "Demo"
    assert app.theme == "dark"
    assert app.width == 900
    assert app.config.app.name == "Demo"
    ui.db.reset()


def test_url_por_motor():
    from interui.config import DatabaseSettings

    sqlite = DatabaseSettings({"engine": "sqlite", "name": "data/a.db"})
    assert sqlite.url == "sqlite:///data/a.db"
    mongo = DatabaseSettings({"engine": "mongo", "host": "h", "port": 27017, "name": "db"})
    assert mongo.url == "mongodb://h:27017/db"
    archivos = DatabaseSettings({"engine": "file", "name": "datos"})
    assert archivos.url == "file://datos"
