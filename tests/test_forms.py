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


class Cliente(ui.Model):
    nombre = ui.Str(max_length=80)
    correo = ui.Email(max_length=120, unique=True)
    estado = ui.Choice(choices=["nuevo", "vip"], default="nuevo")
    pais = ui.Choice(choices=[("es", "España"), ("mx", "México")], null=True)

    class Meta:
        table = "form_clientes"


def test_email_y_choice_se_pintan_con_su_control(tmp_path) -> None:
    db.reset()
    db.configure(
        Config({"databases": {"default": {"engine": "sqlite", "name": str(tmp_path / "c.db")}}})
    )
    db.backend().create_table("form_clientes", Cliente.columns())
    application = ui.App("Clientes", data_dir=tmp_path)
    application.page("/")(lambda: ui.Screen(ui.ModelForm(Cliente)))

    _title, html, _bindings = application.render_page("/")
    assert 'type="email"' in html, "Email usa el campo de correo"
    assert "<select" in html, "Choice usa un desplegable"
    assert "España" in html and "México" in html, "las etiquetas de las opciones"
    assert 'value="vip"' in html


def test_choice_rechaza_valores_fuera_de_la_lista(tmp_path) -> None:
    db.reset()
    db.configure(
        Config({"databases": {"default": {"engine": "sqlite", "name": str(tmp_path / "c.db")}}})
    )
    db.backend().create_table("form_clientes", Cliente.columns())
    application = ui.App("Clientes", data_dir=tmp_path)
    application.page("/")(lambda: ui.Screen(ui.ModelForm(Cliente)))

    _title, _html, bindings = application.render_page("/")
    application._signals["form_form_clientes_nombre"].set("ACME")
    application._signals["form_form_clientes_correo"].set("a@b.c")
    application._signals["form_form_clientes_estado"].set("inventado")
    invoke(_boton(bindings), UIEvent(id="x", event="click"))

    assert "Estado: elige una de las opciones." in application._signals[
        "form_form_clientes_errores"
    ].get()
    assert Cliente.objects.count() == 0

    application._signals["form_form_clientes_estado"].set("vip")
    _title, _html, bindings = application.render_page("/")
    invoke(_boton(bindings), UIEvent(id="x", event="click"))
    assert Cliente.objects.count() == 1
    assert Cliente.objects.first().estado == "vip"
    db.reset()


def test_labels_cambia_el_nombre_visible(app) -> None:
    """`labels` decide cómo se llama el campo, en el formulario y en la tabla."""

    class ConEtiquetas(ui.ModelForm):
        model = Persona
        labels = {"nombre": "Nombre completo", "email": "Correo electrónico"}

    form = ConEtiquetas()
    assert form.label("nombre") == "Nombre completo"
    assert form.label("email") == "Correo electrónico"
    assert form.label("activo") == "Activo", "sin etiqueta, el nombre del campo"

    app.page("/etiquetas")(lambda: ui.Screen(form))
    _title, html, _bindings = app.render_page("/etiquetas")
    assert "Nombre completo" in html
    assert "Correo electrónico" in html


def test_recordtable_usa_las_columnas_del_formulario(app) -> None:
    """La tabla sale del formulario: sus campos, en su orden y con sus nombres."""
    def pagina():
        form = ui.ModelForm(Persona)
        return ui.Screen(ui.Muted(ui.RecordCounter(form)), ui.RecordTable(form))

    app.page("/registros")(pagina)
    _title, html, _bindings = app.render_page("/registros")
    assert "Nombre" in html
    assert "Todavía no hay registros" in html
    assert "0 registros guardados" in html

    Persona.objects.create(nombre="Ana", email="ana@x.com")
    _title, html, _bindings = app.render_page("/registros")
    assert "1 registro guardado" in html
    assert "Ana" in html
    assert "sí" in html, "el booleano se ve como etiqueta"


def test_recordtable_sin_base_de_datos_avisa(tmp_path) -> None:
    """Si la tabla no existe, la página abre con un aviso en vez de romperse."""
    db.reset()
    db.configure(
        Config({"databases": {"default": {"engine": "sqlite", "name": str(tmp_path / "v.db")}}})
    )
    application = ui.App("Sin BD", data_dir=tmp_path)
    application.page("/")(lambda: ui.Screen(ui.RecordTable(ui.ModelForm(Persona))))

    _title, html, _bindings = application.render_page("/")
    assert "Sin base de datos" in html
    assert "migrate" in html
    db.reset()


def test_recordpage_pinta_la_pagina_completa(app) -> None:
    """`RecordPage` es título + contador + formulario + tabla en una llamada."""
    app.page("/pagina")(lambda: ui.Screen(ui.RecordPage(ui.ModelForm(Persona), title="Personas")))
    _title, html, _bindings = app.render_page("/pagina")
    assert "Personas" in html
    assert "0 registros guardados" in html
    assert "Guardar" in html
    assert "Todavía no hay registros" in html

    # Sin `title`, el plural del modelo.
    app.page("/auto")(lambda: ui.Screen(ui.RecordPage(ui.ModelForm(Persona))))
    assert "Personas" in app.render_page("/auto")[1]
