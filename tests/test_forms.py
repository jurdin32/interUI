"""Formularios a partir de un modelo (`ui.ModelForm`)."""

from __future__ import annotations

import pytest

import interui as ui
import interui.simple as simple
from interui import db
from interui.config import Config
from interui.events import UIEvent, invoke


class Persona(ui.Model):
    nombre = ui.Str(max_length=120)
    email = ui.Str(max_length=120, unique=True)
    fecha = ui.Date(null=True)
    activo = ui.Bool(default=True)
    creado = ui.DateTime(auto_now_add=True)

    class Meta:
        table = "form_personas"
        order = ["nombre"]


@pytest.fixture(autouse=True)
def limpiar():
    db.reset()
    yield
    db.reset()


@pytest.fixture
def app(tmp_path):
    db.configure(
        Config(
            {
                "databases": {
                    "default": {"engine": "sqlite", "name": str(tmp_path / "app.db")}
                }
            }
        )
    )
    db.backend().create_table("form_personas", Persona.columns())
    application = ui.App("Formularios", data_dir=tmp_path)

    @application.page("/")
    def index():
        return ui.Screen(ui.ModelForm(Persona))

    return application


def _boton(bindings):
    return next(
        handler
        for handlers in bindings.values()
        for event, handler in handlers.items()
        if event == "click"
    )


def _señal(app, campo: str):
    return app._signals[f"form_form_personas_{campo}"]


def test_genera_un_control_por_campo_editable(app) -> None:
    _title, html, _bindings = app.render_page("/")
    assert html.count("<input") == 4, "nombre, email, fecha y activo"
    assert 'type="date"' in html
    assert 'type="email"' in html
    assert "checkbox" in html
    assert "creado" not in html, "auto_now_add no se pide en el formulario"
    assert "Nuevo persona" in html


def test_guarda_y_limpia_el_formulario(app) -> None:
    _title, _html, bindings = app.render_page("/")
    _señal(app, "nombre").set("Ana Torres")
    _señal(app, "email").set("ana@ejemplo.com")
    _señal(app, "fecha").set("1990-05-14")

    invoke(_boton(bindings), UIEvent(id="x", event="click"))

    assert Persona.objects.count() == 1
    guardada = Persona.objects.first()
    assert guardada.nombre == "Ana Torres"
    assert guardada.email == "ana@ejemplo.com"
    assert _señal(app, "nombre").get() == "", "el formulario se limpia al guardar"
    assert _señal(app, "errores").get() == []


def test_valida_los_obligatorios(app) -> None:
    _title, _html, bindings = app.render_page("/")
    invoke(_boton(bindings), UIEvent(id="x", event="click"))

    errores = _señal(app, "errores").get()
    assert "Nombre es obligatorio." in errores
    assert "Email es obligatorio." in errores
    assert Persona.objects.count() == 0
    _title, html, _bindings = app.render_page("/")
    assert "Revisa los siguientes campos" in html


def test_no_permite_repetir_un_campo_unique(app) -> None:
    Persona.objects.create(nombre="Ana", email="ana@ejemplo.com")
    _title, _html, bindings = app.render_page("/")
    _señal(app, "nombre").set("Otra")
    _señal(app, "email").set("ana@ejemplo.com")

    invoke(_boton(bindings), UIEvent(id="x", event="click"))

    assert Persona.objects.count() == 1
    assert _señal(app, "errores").get() == ["Ya existe un registro con ese email."]


def test_declarado_como_clase_usa_sus_campos(app) -> None:
    class SoloNombre(ui.ModelForm):
        model = Persona
        fields = ["nombre"]
        title = "Solo el nombre"
        submit_label = "Crear"

    @app.page("/solo")
    def solo():
        return ui.Screen(ui.Container(pad=ui.pad.py_10)(SoloNombre()))

    _title, html, _bindings = app.render_page("/solo")
    assert html.count("<input") == 1
    assert "Solo el nombre" in html
    assert "Crear" in html


def test_excluye_los_campos_indicados(app) -> None:
    @app.page("/corto")
    def corto():
        return ui.Screen(ui.ModelForm(Persona, exclude=("email", "activo")))

    _title, html, _bindings = app.render_page("/corto")
    assert 'type="email"' not in html
    assert "checkbox" not in html


def test_ui_state_funciona_dentro_de_una_vista(tmp_path) -> None:
    """La vista pinta con su propia app, no con la ventana implícita."""
    application = ui.App("Proyecto", data_dir=tmp_path)

    @application.page("/")
    def index():
        valor = ui.state("", name="desde_la_vista")
        return ui.Screen(ui.Text(f"valor={valor.get()}"))

    application.render_page("/")

    assert "desde_la_vista" in application._signals
    assert "desde_la_vista" not in simple.current_app()._signals


def test_el_valor_inicial_no_pisa_lo_escrito(tmp_path) -> None:
    application = ui.App("Proyecto", data_dir=tmp_path)

    @application.page("/")
    def index():
        campo = ui.state("", name="nombre_vivo")
        return ui.Screen(ui.Text(f"valor={campo.get()}"))

    application.render_page("/")
    application._signals["nombre_vivo"].set("Ana")
    application.render_page("/")
    assert application._signals["nombre_vivo"].get() == "Ana"


def test_escribir_retira_los_errores(app) -> None:
    """Al corregir un campo, el resumen de errores desaparece."""
    _title, _html, bindings = app.render_page("/")
    invoke(_boton(bindings), UIEvent(id="x", event="click"))
    assert _señal(app, "errores").get()

    campo = next(
        (cid, handler)
        for cid, handlers in bindings.items()
        for event, handler in handlers.items()
        if event == "input"
    )
    invoke(campo[1], UIEvent(id=campo[0], event="input", value="Ana"))

    assert _señal(app, "errores").get() == []
    assert _señal(app, "nombre").get() == "Ana"
    _title, html, _bindings = app.render_page("/")
    assert "Revisa los siguientes campos" not in html
