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


def test_load_rellena_y_actualiza_el_registro(app) -> None:
    """`form.load(registro)` edita ese registro en vez de crear otro."""
    persona = Persona.objects.create(nombre="Ana", email="ana@x.com")
    form = ui.ModelForm(Persona)
    app.page("/editar")(lambda: ui.Screen(form))

    app.render_page("/editar")
    form.load(persona)
    _title, html, _bindings = app.render_page("/editar")
    assert 'value="Ana"' in html, "el campo viene relleno"

    _señal(app, "nombre").set("Ana María")
    _title, _html, bindings = app.render_page("/editar")
    invoke(_boton(bindings), UIEvent(id="x", event="click"))

    assert Persona.objects.count() == 1, "no debe crear un registro nuevo"
    assert Persona.objects.first().nombre == "Ana María"
    assert Persona.objects.first().email == "ana@x.com"


def test_al_editar_no_choca_con_su_propio_unique(app) -> None:
    """El registro que se edita no cuenta como duplicado de sí mismo."""
    persona = Persona.objects.create(nombre="Ana", email="ana@x.com")
    form = ui.ModelForm(Persona)
    app.page("/editar")(lambda: ui.Screen(form))
    app.render_page("/editar")
    form.load(persona)

    _title, _html, bindings = app.render_page("/editar")
    invoke(_boton(bindings), UIEvent(id="x", event="click"))

    assert _señal(app, "errores").get() == []
    assert Persona.objects.count() == 1


def test_rowaction_ejecuta_con_el_registro_de_su_fila(app) -> None:
    """Cada icono de la tabla llama al handler con su registro."""
    vistos: list[str] = []

    def borrar(registro) -> None:
        vistos.append(registro.nombre)
        registro.delete()

    app.page("/acciones")(
        lambda: ui.Screen(
            ui.RecordTable(
                ui.ModelForm(Persona),
                columns=["nombre"],
                sort=False,
                actions=[
                    ui.RowAction("Eliminar", icon=ui.icons.trash, danger=True, on_click=borrar),
                ],
            )
        )
    )
    Persona.objects.create(nombre="Ana", email="ana@x.com")
    Persona.objects.create(nombre="Luis", email="luis@x.com")

    _title, html, bindings = app.render_page("/acciones")
    assert "Eliminar" in html
    assert html.count('aria-label="Eliminar"') == 2, "un botón por fila"

    for uid, handlers in list(bindings.items()):
        if "click" in handlers:
            invoke(handlers["click"], UIEvent(id=uid, event="click"))
            break

    assert len(vistos) == 1
    assert Persona.objects.count() == 1


def test_rowaction_con_confirm_pide_permiso(app) -> None:
    """Con `confirm` primero pregunta y solo borra al aceptar."""
    app.page("/confirmar")(
        lambda: ui.Screen(
            ui.RecordTable(
                ui.ModelForm(Persona),
                columns=["nombre"],
                sort=False,
                actions=[
                    ui.RowAction(
                        "Eliminar",
                        confirm="¿Seguro?",
                        on_click=lambda registro: registro.delete(),
                    )
                ],
            )
        )
    )
    Persona.objects.create(nombre="Ana", email="ana@x.com")
    _title, _html, bindings = app.render_page("/confirmar")

    class _WS:
        id = "w1"

        def send_json(self, payload) -> None:
            pass

    app._client_pages["w1"] = "/confirmar"
    app._bindings["w1"] = bindings
    uid = next(u for u, handlers in bindings.items() if "click" in handlers)
    app._dispatch(_WS(), {"id": uid, "e": "click"})

    assert Persona.objects.count() == 1, "no borra sin confirmar"
    assert app.dialogs, "abre un diálogo de confirmación"


def test_form_dialog_abre_el_formulario_en_un_modal(app) -> None:
    """`form_dialog` abre el formulario en un diálogo con el registro cargado."""

    class _WS:
        id = "w1"

        def send_json(self, payload) -> None:
            pass

    def editar(registro) -> None:
        ui.form_dialog(ui.ModelForm(Persona), instance=registro, title="Editar")

    app.page("/modal")(lambda: ui.Screen(ui.Button("Editar", on_click=lambda: editar(
        Persona.objects.first()
    ))))
    Persona.objects.create(nombre="Ana", email="ana@x.com")
    _title, _html, bindings = app.render_page("/modal")

    app._client_pages["w1"] = "/modal"
    app._bindings["w1"] = bindings
    uid = next(u for u, handlers in bindings.items() if "click" in handlers)
    app._dispatch(_WS(), {"id": uid, "e": "click"})

    assert len(app.dialogs) == 1
    html = app.render_page("/modal")[1]
    assert "Editar" in html
    assert 'value="Ana"' in html


def test_recordpage_sin_formulario_en_la_pagina(app) -> None:
    """`form_mode="none"` deja solo el contador y la tabla."""
    app.page("/solo")(
        lambda: ui.Screen(ui.RecordPage(ui.ModelForm(Persona), title="Personas", form_mode="none"))
    )
    _title, html, _bindings = app.render_page("/solo")
    assert "Personas" in html
    assert "Todavía no hay registros" in html
    assert "Guardar" not in html, "no debe haber formulario dentro de la página"


def test_recordpage_con_el_formulario_en_un_modal(app) -> None:
    """`form_mode="modal"` pone un botón Nuevo y abre el formulario en un diálogo."""

    class _WS:
        id = "w1"

        def send_json(self, payload) -> None:
            pass

    app.page("/modal2")(
        lambda: ui.Screen(ui.RecordPage(ui.ModelForm(Persona), title="Personas", form_mode="modal"))
    )
    _title, html, bindings = app.render_page("/modal2")
    assert "Nuevo" in html
    assert "Guardar" not in html, "el formulario no va en la página"

    app._client_pages["w1"] = "/modal2"
    app._bindings["w1"] = bindings
    uid = next(u for u, handlers in bindings.items() if "click" in handlers)
    app._dispatch(_WS(), {"id": uid, "e": "click"})

    assert len(app.dialogs) == 1
    html = app.render_page("/modal2")[1]
    assert "Guardar" in html, "el modal sí trae el formulario"


def test_form_mode_invalido_falla(app) -> None:
    with pytest.raises(ValueError, match="form_mode"):
        ui.RecordPage(ui.ModelForm(Persona), form_mode="ventana")


def test_iconos_y_placeholders_configurables(app) -> None:
    """`icons` y `placeholders` del formulario llegan a los campos."""

    class ConIconos(ui.ModelForm):
        model = Persona
        icons = {"nombre": "user", "email": "mail"}
        placeholders = {"email": "tu@correo.com"}

    form = ConIconos()
    assert form.icon("nombre") == "user"
    assert form.icon("activo") is None, "un booleano no lleva icono"
    app.page("/iconos")(lambda: ui.Screen(form))

    _title, html, _bindings = app.render_page("/iconos")
    assert 'placeholder="tu@correo.com"' in html
    assert html.count("<svg") >= 2, "los iconos se dibujan"


def test_iconos_por_defecto_segun_el_nombre(app) -> None:
    """Sin `icons`, el nombre del campo elige un icono razonable."""
    form = ui.ModelForm(Persona)
    assert form.icon("nombre") == "user"
    assert form.icon("email") == "mail"


def test_fresh_copia_la_configuracion_del_formulario(app) -> None:
    """`fresh()` da otro formulario igual (lo usa el botón Nuevo del modal)."""

    class ConEtiquetas(ui.ModelForm):
        model = Persona
        labels = {"nombre": "Nombre completo"}
        placeholders = {"email": "tu@correo.com"}

    copia = ConEtiquetas().fresh()
    assert isinstance(copia, ConEtiquetas)
    assert copia.form_labels == {"nombre": "Nombre completo"}
    assert copia.form_placeholders == {"email": "tu@correo.com"}
    assert copia is not None


def _tabla_app(tmp_path, total: int = 25):
    """App con una tabla de `total` personas y su página de registro."""
    db.reset()
    db.configure(
        Config({"databases": {"default": {"engine": "sqlite", "name": str(tmp_path / "t.db")}}})
    )
    db.backend().create_table("form_personas", Persona.columns())
    for numero in range(1, total + 1):
        Persona.objects.create(
            nombre=f"Persona {numero:02d}",
            email=f"p{numero}@x.com",
            activo=numero % 2 == 0,
        )
    return ui.App("Tabla", data_dir=tmp_path)


def _tabla(page: ui.Component, app) -> ui.Component:
    app.page("/tabla")(lambda: ui.Screen(page))
    return app


def test_tabla_pagina_de_10_en_10(tmp_path) -> None:
    app = _tabla_app(tmp_path)
    page = ui.RecordPage(ui.ModelForm(Persona), title="Personas", search=True, page_size=10)
    _tabla(page, app)

    _title, html, _bindings = app.render_page("/tabla")
    assert "Mostrando 1–10 de 25" in html
    assert "1 de 3" in html
    assert html.count("Persona ") == 10, "solo diez filas"

    app._signals["tabla_form_personas_pagina"].set(2)
    _title, html, _bindings = app.render_page("/tabla")
    assert "Mostrando 21–25 de 25" in html
    assert "3 de 3" in html
    db.reset()


def test_tabla_pagina_configurable(tmp_path) -> None:
    app = _tabla_app(tmp_path)
    _tabla(ui.RecordPage(ui.ModelForm(Persona), search=True, page_size=15), app)

    app.render_page("/tabla")
    app._signals["tabla_form_personas_tamano"].set(15)
    _title, html, _bindings = app.render_page("/tabla")
    assert "Mostrando 1–15 de 25" in html
    db.reset()


def test_tabla_busca_en_las_columnas(tmp_path) -> None:
    app = _tabla_app(tmp_path)
    _tabla(ui.RecordPage(ui.ModelForm(Persona), search=True), app)
    app.render_page("/tabla")

    app._signals["tabla_form_personas_busqueda"].set("Persona 07")
    _title, html, _bindings = app.render_page("/tabla")
    assert "Persona 07" in html
    assert "Persona 08" not in html
    assert "Mostrando 1–1 de 1" in html, "con una sola coincidencia también hay pie"
    db.reset()


def test_tabla_muestra_el_pie_aunque_quepan_todas_las_filas(tmp_path) -> None:
    """El pie y el selector de filas no deben desaparecer al filtrar."""
    app = _tabla_app(tmp_path, total=6)
    _tabla(ui.RecordPage(ui.ModelForm(Persona), search=True, page_size=10), app)

    _title, html, _bindings = app.render_page("/tabla")
    assert "Mostrando 1–6 de 6" in html
    assert "1 de 1" in html
    assert "Filas por página" in html
    db.reset()


def test_tabla_busca_solo_en_las_columnas_indicadas(tmp_path) -> None:
    app = _tabla_app(tmp_path)
    _tabla(
        ui.RecordPage(
            ui.ModelForm(Persona), search=True, search_columns=["email"], columns=["nombre"]
        ),
        app,
    )
    app.render_page("/tabla")

    app._signals["tabla_form_personas_busqueda"].set("p7@x.com")
    _title, html, _bindings = app.render_page("/tabla")
    assert "Persona 07" in html and "Persona 08" not in html
    db.reset()


def test_tabla_ordena_por_columna(tmp_path) -> None:
    app = _tabla_app(tmp_path)
    _tabla(ui.RecordPage(ui.ModelForm(Persona), search=True), app)

    _title, html, _bindings = app.render_page("/tabla")
    assert 'aria-label="Ordenar por Nombre"' in html

    app._signals["tabla_form_personas_orden"].set("nombre")
    app._signals["tabla_form_personas_sentido"].set("desc")
    _title, html, _bindings = app.render_page("/tabla")
    primera = html.split("Persona ")[1][:2]
    assert primera == "25", f"orden descendente, llegó {primera}"

    app._signals["tabla_form_personas_sentido"].set("asc")
    _title, html, _bindings = app.render_page("/tabla")
    assert html.split("Persona ")[1][:2] == "01"
    db.reset()


def test_tabla_sin_ordenacion_ni_busqueda(tmp_path) -> None:
    app = _tabla_app(tmp_path)
    _tabla(
        ui.RecordPage(
            ui.ModelForm(Persona), search=False, sort=False, page_size=None
        ),
        app,
    )
    _title, html, _bindings = app.render_page("/tabla")
    assert "Ordenar por" not in html
    assert "Buscar…" not in html
    assert "Mostrando" not in html, "sin paginación no hay pie"
    assert "Persona 25" in html, "todas las filas de una vez"
    db.reset()
