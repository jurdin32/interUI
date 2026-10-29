"""Migraciones: se generan solas y se aplican por orden."""

from __future__ import annotations

import json

import pytest

import interui as ui
from interui import db, migrations
from interui.config import CONFIG_NAME, Config, ConfigError

MODELS_V1 = '''
import interui as ui


class Cliente(ui.Model):
    nombre = ui.Str(max_length=80)
    edad = ui.Int(null=True)

    class Meta:
        table = "clientes"
'''

MODELS_V2 = '''
import interui as ui


class Cliente(ui.Model):
    nombre = ui.Str(max_length=120)
    edad = ui.Int(null=True)
    email = ui.Str(max_length=120, null=True)

    class Meta:
        table = "clientes"
'''


@pytest.fixture(autouse=True)
def limpiar():
    db.reset()
    yield
    db.reset()


@pytest.fixture
def proyecto(tmp_path):
    (tmp_path / CONFIG_NAME).write_text(
        json.dumps({"databases": {"default": {"engine": "sqlite", "name": "data/app.db"}}}),
        encoding="utf-8",
    )
    (tmp_path / "models.py").write_text(MODELS_V1, encoding="utf-8")
    config = Config.load(tmp_path / CONFIG_NAME)
    db.configure(config)
    return config


def escribe_modelos(config: Config, text: str) -> None:
    config.resolve("models.py").write_text(text, encoding="utf-8")


def test_primera_migracion(proyecto):
    path = migrations.makemigrations(proyecto)
    assert path is not None and path.name == "0001_initial.json"

    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["operations"][0]["op"] == "CreateModel"
    assert data["operations"][0]["table"] == "clientes"
    assert {"nombre", "edad", "id"} <= {item["name"] for item in data["operations"][0]["columns"]}

    aplicadas = migrations.migrate(proyecto)
    assert aplicadas == ["0001_initial"]
    tablas = db.backend("default").tables()
    assert "clientes" in tablas


def test_sin_cambios_no_genera_nada(proyecto):
    migrations.makemigrations(proyecto)
    migrations.migrate(proyecto)
    assert migrations.makemigrations(proyecto) is None


def test_campo_nuevo_y_alterado(proyecto):
    migrations.makemigrations(proyecto)
    migrations.migrate(proyecto)

    escribe_modelos(proyecto, MODELS_V2)
    path = migrations.makemigrations(proyecto)
    assert path is not None and path.name == "0002_auto.json"

    data = json.loads(path.read_text(encoding="utf-8"))
    kinds = [operation["op"] for operation in data["operations"]]
    assert "AddField" in kinds and "AlterField" in kinds

    migrations.migrate(proyecto)
    columnas = {column.name for column in db.backend("default").table_columns("clientes")}
    assert {"email", "nombre"} <= columnas


def test_los_datos_sobreviven_a_un_alter(proyecto):
    migrations.makemigrations(proyecto)
    migrations.migrate(proyecto)

    class Cliente(ui.Model):
        nombre = ui.Str(max_length=80)
        edad = ui.Int(null=True)

        class Meta:
            table = "clientes"

    Cliente.objects.create(nombre="Ana", edad=30)

    escribe_modelos(proyecto, MODELS_V2)
    migrations.makemigrations(proyecto)
    migrations.migrate(proyecto)

    fila = db.backend("default").select("clientes")[0]
    assert fila["nombre"] == "Ana"
    assert fila["edad"] == 30


def test_estado_de_migraciones(proyecto):
    migrations.makemigrations(proyecto)
    pendientes = migrations.status(proyecto)
    assert [item["applied"] for item in pendientes] == [False]

    migrations.migrate(proyecto)
    aplicadas = migrations.status(proyecto)
    assert [item["applied"] for item in aplicadas] == [True]
    assert aplicadas[0]["operations"] == ["crear tabla clientes"]


def test_borrar_un_modelo_pide_confirmacion(proyecto):
    migrations.makemigrations(proyecto)
    migrations.migrate(proyecto)

    escribe_modelos(proyecto, "import interui as ui\n")
    with pytest.raises(ConfigError) as info:
        migrations.makemigrations(proyecto)
    assert "borrar" in str(info.value)

    path = migrations.makemigrations(proyecto, allow_destructive=True)
    assert path is not None
    migrations.migrate(proyecto)
    assert "clientes" not in db.backend("default").tables()


def test_motor_de_archivos_no_necesita_esquema(tmp_path):
    (tmp_path / CONFIG_NAME).write_text(
        json.dumps(
            {
                "migrations": {"models": "models.py", "directory": "migrations"},
                "databases": {"default": {"engine": "file", "name": "datos"}},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "models.py").write_text(MODELS_V1, encoding="utf-8")
    config = Config.load(tmp_path / CONFIG_NAME)
    db.configure(config)

    migrations.makemigrations(config)
    assert migrations.migrate(config) == ["0001_initial"]
    assert "clientes" in db.backend("default").collection_names()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def test_cli_init_crea_el_proyecto(tmp_path, monkeypatch, capsys):
    from interui.cli import main

    target = tmp_path / "tienda"
    code = main(
        [
            "init", str(target), "--no-input", "--name", "Tienda", "--db", "sqlite",
            "--database", "data/tienda.db", "--migrate",
        ]
    )
    assert code == 0
    assert (target / CONFIG_NAME).is_file()
    assert (target / "app.py").is_file()
    assert (target / "models.py").is_file()
    assert (target / "migrations" / "0001_initial.json").is_file()
    assert (target / "data" / "tienda.db").is_file()

    config = Config.load(target / CONFIG_NAME)
    assert config.app.name == "Tienda"
    assert config.databases.default.engine == "sqlite"


def test_cli_db_status(tmp_path, monkeypatch, capsys):
    from interui.cli import main

    target = tmp_path / "tienda"
    assert main(["init", str(target), "--no-input", "--name", "Tienda"]) == 0
    monkeypatch.chdir(target)
    db.reset()
    assert main(["db", "makemigrations"]) == 0
    assert main(["db", "migrate"]) == 0
    assert main(["db", "status"]) == 0
    salida = capsys.readouterr().out
    assert "0001_initial" in salida
    assert "✔" in salida
