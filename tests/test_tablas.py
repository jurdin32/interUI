"""Tablas configurables: colores, cebra, selección, doble clic y menú contextual."""

from __future__ import annotations

import pytest

import interui as ui
from interui import db
from interui.config import Config
from interui.context import RenderContext
from interui.events import UIEvent


class Persona(ui.Model):
    nombre = ui.Str(max_length=120)
    email = ui.Str(max_length=120, unique=True)
    activo = ui.Bool(default=True)

    class Meta:
        table = "tabla_personas"
        order = ["nombre"]


@pytest.fixture(autouse=True)
def limpiar():
    db.reset()
    yield
    db.reset()


def _app(tmp_path, total: int = 3) -> ui.App:
    db.configure(
        Config({"databases": {"default": {"engine": "sqlite", "name": str(tmp_path / "t.db")}}})
    )
    db.backend().create_table("tabla_personas", Persona.columns())
    for numero in range(1, total + 1):
        Persona.objects.create(nombre=f"Persona {numero}", email=f"p{numero}@x.com")
    return ui.App("Tablas", data_dir=tmp_path)


def _html(component: ui.Component, app: ui.App) -> str:
    app.page("/t")(lambda: ui.Screen(component))
    _title, html, _bindings = app.render_page("/t")
    return html


# --- aspecto ---------------------------------------------------------------
def test_colores_de_encabezado(tmp_path) -> None:
    html = _html(
        ui.Table(
            headers=["A", "B"],
            rows=[["1", "2"]],
            header_bg=ui.colors.slate_100,
            header_color=ui.colors.slate_700,
        ),
        _app(tmp_path),
    )
    assert "bg-slate-100" in html
    assert "text-slate-700" in html
    assert "dark:bg-slate-800/50" in html, "el modo oscuro sigue teniendo su fondo"


def test_cebra_y_colores_por_columna(tmp_path) -> None:
    html = _html(
        ui.Table(
            headers=["A", "B"],
            rows=[["1", "2"], ["3", "4"]],
            striped=True,
            zebra=ui.colors.amber_50,
            cell_colors={1: ui.colors.emerald_600},
            column_bg={0: ui.colors.slate_50},
        ),
        _app(tmp_path),
    )
    assert "bg-amber-50" in html
    assert "text-emerald-600" in html
    assert "bg-slate-50" in html


def test_fila_seleccionada(tmp_path) -> None:
    html = _html(
        ui.Table(
            headers=["A"],
            rows=[["1"], ["2"]],
            selected=1,
            selected_bg=ui.colors.indigo_50,
        ),
        _app(tmp_path),
    )
    filas = [parte for parte in html.split("<tr") if "bg-indigo-50" in parte]
    assert len(filas) == 1, "solo se resalta la fila pedida"
    assert "2" in filas[0]


def test_la_tabla_se_marca_para_el_doble_clic() -> None:
    """El runtime selecciona el contenido de la celda al hacer doble clic."""
    html = ui.render(ui.Table(headers=["A"], rows=[["1"]]))
    assert "data-iui-table" in html


# --- interacción por fila --------------------------------------------------
def _handlers(html: str, ctx: RenderContext) -> list[tuple[str, str, object]]:
    return [
        (uid, evento, handler)
        for uid, eventos in ctx.bindings.items()
        for evento, handler in eventos.items()
    ]


def test_clic_y_doble_clic_en_la_fila() -> None:
    vistos: list[tuple[str, object]] = []
    tabla = ui.Table(
        headers=["A"],
        rows=[["uno"], ["dos"]],
        on_row_click=lambda fila: vistos.append(("clic", fila[0])),
        on_row_dblclick=lambda indice, fila: vistos.append(("doble", indice)),
    )
    ctx = RenderContext()
    html = ui.render(tabla, ctx)
    assert 'data-iui-on="click,dblclick"' in html

    for uid, evento, handler in _handlers(html, ctx):
        if uid == "r":
            continue
        handler(UIEvent(id=uid, event=evento))  # type: ignore[operator]

    assert vistos == [("clic", "uno"), ("doble", 0), ("clic", "dos"), ("doble", 1)]


def test_menu_contextual_por_fila(tmp_path) -> None:
    html = _html(
        ui.Table(
            headers=["A"],
            rows=[["uno"], ["dos"]],
            context_menu=[
                ui.ContextItem("Editar", icon="edit"),
                ui.ContextItem("Eliminar", icon="trash", danger=True),
            ],
        ),
        _app(tmp_path),
    )
    assert html.count("data-iui-context-panel") == 2, "un panel por fila"
    assert html.count("data-iui-context=") == 2
    assert "cursor-context-menu" in html
    assert "Editar" in html and "Eliminar" in html


def test_el_menu_contextual_puede_depender_de_la_fila(tmp_path) -> None:
    html = _html(
        ui.Table(
            headers=["A"],
            rows=[["uno"], ["dos"]],
            context_menu=lambda indice, fila: [ui.ContextItem(f"Abrir {fila[0]}")],
        ),
        _app(tmp_path),
    )
    assert "Abrir uno" in html
    assert "Abrir dos" in html


# --- RecordTable / RecordPage ---------------------------------------------
def test_actions_false_esconde_los_botones(tmp_path) -> None:
    app = _app(tmp_path)
    con_botones = _html(
        ui.RecordTable(
            ui.ModelForm(Persona), actions=[ui.RowAction("Editar", icon="edit", on_click=lambda r: None)]
        ),
        app,
    )
    sin_botones = _html(ui.RecordTable(ui.ModelForm(Persona), actions=False), app)
    assert "Editar" in con_botones
    assert "Editar" not in sin_botones


def test_clic_selecciona_la_fila(tmp_path) -> None:
    app = _app(tmp_path)
    tabla = ui.RecordTable(ui.ModelForm(Persona), selectable=True, selected_bg=ui.colors.indigo_50)
    app.page("/sel")(lambda: ui.Screen(tabla))
    _title, html, bindings = app.render_page("/sel")
    assert "bg-indigo-50" not in html, "al principio no hay nada seleccionado"

    registro = list(Persona.objects.all())[1]
    handler = next(
        fn
        for uid, eventos in bindings.items()
        for evento, fn in eventos.items()
        if evento == "click" and "fila" in uid
    )
    handler(UIEvent(id="fila", event="click", value=None))

    _title, html, _bindings = app.render_page("/sel")
    assert html.count("bg-indigo-50") == 1
    assert registro.nombre in html


def test_doble_clic_recibe_el_registro(tmp_path) -> None:
    app = _app(tmp_path)
    elegidos: list[Persona] = []
    tabla = ui.RecordTable(ui.ModelForm(Persona), on_row_dblclick=elegidos.append)
    app.page("/dbl")(lambda: ui.Screen(tabla))
    _title, _html_, bindings = app.render_page("/dbl")

    handler = next(
        fn
        for uid, eventos in bindings.items()
        for evento, fn in eventos.items()
        if evento == "dblclick" and "fila" in uid
    )
    handler(UIEvent(id="fila", event="dblclick", value=None))

    assert len(elegidos) == 1
    assert isinstance(elegidos[0], Persona)


def test_menu_contextual_con_acciones_de_fila(tmp_path) -> None:
    app = _app(tmp_path)
    borrados: list[Persona] = []
    tabla = ui.RecordTable(
        ui.ModelForm(Persona),
        actions=False,
        context_menu=[
            ui.RowAction("Editar", icon="edit", on_click=lambda r: None),
            ui.RowAction("Eliminar", icon="trash", danger=True, on_click=borrados.append),
        ],
    )
    html = _html(tabla, app)
    assert html.count("data-iui-context-panel") == 3, "un panel por registro"
    assert "Eliminar" in html


def test_record_page_acepta_opciones_de_tabla(tmp_path) -> None:
    app = _app(tmp_path)
    html = _html(
        ui.RecordPage(
            ui.ModelForm(Persona),
            title="Personas",
            actions=False,
            table_options=dict(
                striped=True,
                header_bg=ui.colors.slate_100,
                selectable=True,
                on_row_dblclick=lambda registro: None,
            ),
        ),
        app,
    )
    assert "bg-slate-100" in html
    assert "dark:bg-slate-800/30" in html, "cebra"
    assert "data-iui-on" in html


def test_solo_hay_un_formulario_en_modal_abierto(tmp_path) -> None:
    """Dos dobles clics seguidos no dejan dos modales iguales apilados."""

    class Cliente:
        def __init__(self) -> None:
            self.id = "cliente"
            self.alive = True
            self.sent: list[dict] = []

        def send_json(self, payload: dict) -> None:
            self.sent.append(payload)

    app = _app(tmp_path)
    tabla = ui.RecordTable(
        ui.ModelForm(Persona),
        on_row_dblclick=lambda registro: ui.form_dialog(
            ui.ModelForm(Persona), instance=registro, title="Editar"
        ),
    )
    app.page("/dbl")(lambda: ui.Screen(tabla))
    _t, _h, bindings = app.render_page("/dbl")
    filas = [uid for uid, eventos in bindings.items() if "dblclick" in eventos and "fila" in uid]

    cliente = Cliente()
    app.handle_message(cliente, {"t": "hello", "page": "/dbl"})
    for fila in filas[:2]:
        app.handle_message(cliente, {"t": "event", "id": fila, "e": "dblclick", "v": None})

    assert len(app.dialogs) == 1, "el segundo modal sustituye al primero"
    app.close_all_dialogs()


# --- tabla declarada como clase (tables.py) -------------------------------
def test_tabla_declarada_en_una_clase(tmp_path) -> None:
    """Todo se declara como atributos de clase; la vista no repite nada."""
    vistas: list[Persona] = []

    class PersonaTable(ui.RecordTable):
        form = ui.ModelForm(Persona)
        columns = ["nombre", "email"]
        striped = True
        header_bg = ui.colors.slate_100
        actions = False
        selectable = True
        on_row_dblclick = vistas.append

    app = _app(tmp_path)
    html = _html(ui.RecordPage(PersonaTable), app)

    assert "Persona 1" in html
    assert "bg-slate-100" in html, "el encabezado usa el color declarado"
    assert "dark:bg-slate-800/30" in html, "cebra"
    assert html.count("p1@x.com") == 1, "solo las columnas declaradas"
    assert "Editar" not in html, "actions=False esconde los botones"


def test_la_pagina_toma_el_formulario_de_la_tabla(tmp_path) -> None:
    class PersonaTable(ui.RecordTable):
        form = ui.ModelForm(Persona)
        page_size = 1

    app = _app(tmp_path)
    html = _html(ui.RecordPage(PersonaTable), app)
    assert "Mostrando 1–1 de 3" in html
    assert "registros guardados" in html, "el contador sale del formulario de la tabla"


def test_los_atributos_de_la_clase_se_pueden_pisar(tmp_path) -> None:
    class PersonaTable(ui.RecordTable):
        form = ui.ModelForm(Persona)
        page_size = 10

    app = _app(tmp_path)
    html = _html(ui.RecordPage(PersonaTable(page_size=1)), app)
    assert "Mostrando 1–1 de 3" in html
