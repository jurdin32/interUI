"""Modelos y motores: SQLite y archivos JSON (sin drivers externos)."""

from __future__ import annotations

import datetime as dt
import json

import pytest

import interui as ui
from interui import db
from interui.config import CONFIG_NAME, Config


class Cliente(ui.Model):
    nombre = ui.Str(max_length=80, unique=True)
    email = ui.Str(max_length=120, null=True)
    edad = ui.Int(null=True)
    activo = ui.Bool(default=True)
    alta = ui.DateTime(null=True)
    extra = ui.Json(null=True)

    class Meta:
        table = "clientes"


class Nota(ui.Model):
    titulo = ui.Str(max_length=60)
    cuerpo = ui.LongText(null=True)

    class Meta:
        table = "notas"
        database = "archivos"


@pytest.fixture(autouse=True)
def limpiar():
    db.reset()
    yield
    db.reset()


@pytest.fixture
def proyecto(tmp_path):
    data = {
        "databases": {
            "default": {"engine": "sqlite", "name": "data/app.db"},
            "archivos": {"engine": "file", "name": "datos"},
        }
    }
    (tmp_path / CONFIG_NAME).write_text(json.dumps(data), encoding="utf-8")
    settings = Config.load(tmp_path / CONFIG_NAME)
    db.configure(settings)
    for model in (Cliente, Nota):
        backend = db.backend(model._database)
        backend.create_table(model._table, model.columns())
    return settings


# ---------------------------------------------------------------------------
# SQLite
# ---------------------------------------------------------------------------
def test_crear_y_leer(proyecto):
    ana = Cliente.objects.create(nombre="Ana", edad=34)
    assert ana.pk == 1
    assert ana.activo is True

    leida = Cliente.objects.get(nombre="Ana")
    assert leida.edad == 34
    assert leida.pk == ana.pk


def test_valores_por_defecto(proyecto):
    cliente = Cliente.objects.create(nombre="Luis")
    assert cliente.activo is True
    assert cliente.edad is None


def test_actualizar_y_borrar(proyecto):
    cliente = Cliente.objects.create(nombre="Ana", edad=30)
    cliente.edad = 31
    cliente.save()
    assert Cliente.objects.get(pk=cliente.pk).edad == 31

    cliente.delete()
    assert Cliente.objects.count() == 0


def test_filtros(proyecto):
    Cliente.objects.create(nombre="Ana", edad=20)
    Cliente.objects.create(nombre="Luis", edad=40)
    Cliente.objects.create(nombre="Ana María", edad=30)

    assert Cliente.objects.filter(edad__gte=30).count() == 2
    assert Cliente.objects.filter(edad__lt=30).count() == 1
    assert Cliente.objects.filter(nombre__contains="María").count() == 1
    assert Cliente.objects.filter(nombre__startswith="Ana").count() == 2
    assert Cliente.objects.filter(edad__in=[20, 40]).count() == 2
    assert Cliente.objects.filter(email__isnull=True).count() == 3


def test_orden_y_limites(proyecto):
    for nombre, edad in (("Ana", 20), ("Luis", 40), ("Eva", 30)):
        Cliente.objects.create(nombre=nombre, edad=edad)

    edades = [item.edad for item in Cliente.objects.order_by("-edad")]
    assert edades == [40, 30, 20]
    assert Cliente.objects.order_by("edad").first().nombre == "Ana"
    assert Cliente.objects.order_by("edad").last().nombre == "Luis"
    assert Cliente.objects.all().limit(2).count() == 2


def test_exclude(proyecto):
    Cliente.objects.create(nombre="Ana")
    Cliente.objects.create(nombre="Luis")
    restantes = Cliente.objects.exclude(nombre="Ana").all()
    assert [item.nombre for item in restantes] == ["Luis"]


def test_tipos_especiales(proyecto):
    ahora = dt.datetime(2026, 1, 2, 3, 4, 5)
    cliente = Cliente.objects.create(
        nombre="Ana", activo=False, alta=ahora, extra={"tags": ["a", "b"], "n": 3}
    )
    leida = Cliente.objects.get(pk=cliente.pk)
    assert leida.activo is False
    assert leida.alta == ahora
    assert leida.extra == {"tags": ["a", "b"], "n": 3}


def test_get_inexistente(proyecto):
    with pytest.raises(Cliente.DoesNotExist):
        Cliente.objects.get(nombre="Nadie")


def test_campo_desconocido(proyecto):
    with pytest.raises(TypeError):
        Cliente(nombre="Ana", inexistente=1)


def test_estado_del_modelo(proyecto):
    estado = Cliente.state()
    assert estado["table"] == "clientes"
    assert estado["fields"]["nombre"]["max_length"] == 80
    assert estado["fields"]["id"]["primary_key"] is True


def test_columnas_generadas(proyecto):
    nombres = {column.name for column in Cliente.columns()}
    assert nombres >= {"id", "nombre", "email", "edad", "activo", "alta", "extra"}


# ---------------------------------------------------------------------------
# archivos JSON
# ---------------------------------------------------------------------------
def test_motor_de_archivos(proyecto):
    nota = Nota.objects.create(titulo="Primera", cuerpo="Hola")
    assert nota.pk == 1
    assert Nota.objects.count() == 1
    leida = Nota.objects.get(titulo="Primera")
    assert leida.cuerpo == "Hola"

    nota.titulo = "Cambiada"
    nota.save()
    assert Nota.objects.get(pk=nota.pk).titulo == "Cambiada"

    nota.delete()
    assert Nota.objects.count() == 0


def test_motor_de_archivos_filtra_en_python(proyecto):
    Nota.objects.create(titulo="a", cuerpo="uno")
    Nota.objects.create(titulo="b", cuerpo="dos")
    assert Nota.objects.filter(titulo__contains="b").count() == 1
    assert [item.titulo for item in Nota.objects.order_by("-titulo")] == ["b", "a"]


def test_motor_sin_driver_dice_que_instalar():
    import importlib.util

    if importlib.util.find_spec("psycopg") or importlib.util.find_spec("psycopg2"):
        pytest.skip("psycopg está instalado")
    from interui.config import DatabaseSettings
    from interui.db import DatabaseError

    settings = DatabaseSettings(
        {"engine": "postgres", "host": "localhost", "port": 5432, "user": "u", "name": "n"}
    )
    with pytest.raises(DatabaseError) as info:
        db.connect(settings)
    assert "interui[postgres]" in str(info.value)


def test_motor_desconocido():
    from interui.config import DatabaseSettings
    from interui.db import DatabaseError

    with pytest.raises(DatabaseError):
        db.connect(DatabaseSettings({"engine": "oracle", "name": "x"}))


def test_sqlite_en_memoria_no_toca_el_disco(tmp_path, monkeypatch):
    """`name: ":memory:"` crea una base efímera, sin archivo ni carpeta."""
    monkeypatch.chdir(tmp_path)
    settings = Config({"databases": {"default": {"engine": "sqlite", "name": ":memory:"}}})
    db.configure(settings)
    backend = db.backend("default")
    backend.create_table("clientes", Cliente.columns())
    Cliente.objects.create(nombre="Ana")

    assert Cliente.objects.count() == 1
    assert list(tmp_path.iterdir()) == []


def test_campos_email_y_choice():
    """`Email` es texto con control de correo; `Choice` es texto con opciones."""
    import interui as ui

    class Contacto(ui.Model):
        correo = ui.Email(max_length=120, unique=True)
        estado = ui.Choice(choices=["nuevo", "vip"], default="nuevo")
        pais = ui.Choice(choices=[("es", "España")])

        class Meta:
            table = "orm_contactos"

    correo = Contacto._fields["correo"]
    assert correo.type == "varchar"
    assert correo.max_length == 120 and correo.unique

    estado = Contacto._fields["estado"]
    assert estado.type == "varchar", "la columna es texto, como Str"
    assert estado.get_default() == "nuevo"
    assert estado.choices == [("nuevo", "nuevo"), ("vip", "vip")]
    assert estado.option_values == ["nuevo", "vip"]

    assert Contacto._fields["pais"].choices == [("es", "España")]
    assert "choices" not in estado.describe(), "las opciones no cambian la tabla"

    with pytest.raises(ValueError):
        ui.Choice(choices=[])
