"""API compacta: ventana + texto + botón con el mínimo código posible."""

from __future__ import annotations

import pytest

import interui as ui
from interui.simple import column, current_app, row, state, text, title, toast, view, window


class FakeClient:
    def __init__(self) -> None:
        self.id = "cliente"
        self.alive = True
        self.sent: list[dict] = []

    def send_json(self, payload: dict) -> None:
        self.sent.append(payload)

    @property
    def last_html(self) -> str:
        return self.sent[-1]["html"]


def _bind(app: ui.App) -> FakeClient:
    """Registra un cliente falso y su primer render (como hace el WebSocket)."""
    client = FakeClient()
    app.handle_message(client, {"t": "hello", "page": "/"})
    return client


def _handler_id(app: ui.App, client: FakeClient, event: str) -> str:
    bindings = app._bindings[client.id]
    return next(uid for uid, handlers in bindings.items() if event in handlers)


def test_minimal_window_renders(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    app = window("Hola", text("Hola mundo"), ui.button("Pulsar"))
    _title, html, _bindings = app.render_page("/")
    assert "Hola mundo" in html
    assert "Pulsar" in html
    assert html.startswith('<div id="iui-root"')


def test_counter_needs_no_lambdas(monkeypatch, tmp_path) -> None:
    """El caso del README: estado + texto reactivo + botón que incrementa."""
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    count = state(0)
    app = window("Contador", text("Pulsaciones: ", count), ui.button("Pulsar", on_click=count.inc))

    client = _bind(app)
    assert "Pulsaciones: 0" in client.last_html

    app.handle_message(client, {"t": "event", "id": _handler_id(app, client, "click"), "e": "click"})
    assert count.get() == 1
    assert "Pulsaciones: 1" in client.last_html


def test_signal_as_input_handler(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    nombre = state("")
    app = window("Form", ui.input(value=nombre, on_input=nombre, label="Nombre"))

    client = _bind(app)
    app.handle_message(
        client, {"t": "event", "id": _handler_id(app, client, "input"), "e": "input", "v": "Ana"}
    )
    assert nombre.get() == "Ana"
    assert "Ana" in client.last_html


def test_signal_as_switch_handler_uses_checked(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    activo = state(False)
    app = window("Switch", ui.switch("Activo", checked=activo, on_change=activo))

    client = _bind(app)
    app.handle_message(
        client,
        {"t": "event", "id": _handler_id(app, client, "change"), "e": "change", "v": "on", "checked": True},
    )
    assert activo.get() is True


def test_lambda_with_event_still_works(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    received: list[object] = []
    app = window("Evento", ui.button("x", on_click=lambda evento: received.append(evento)))

    client = _bind(app)
    app.handle_message(client, {"t": "event", "id": _handler_id(app, client, "click"), "e": "click"})
    assert received and received[0].event == "click"


def test_reactive_text_with_callable(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    valor = state(2)
    app = window("Reactivo", text(lambda: f"doble={valor.get() * 2}"))
    _title, html, _bindings = app.render_page("/")
    assert "doble=4" in html


def test_row_distributes_columns(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    html = ui.render(row(text("a"), text("b"), text("c")))
    assert "grid-cols-12" in html
    assert "lg:col-span-4" in html


def test_aliases_cover_the_catalog() -> None:
    assert ui.button is ui.Button
    assert ui.input is ui.Input
    assert ui.data_table is ui.DataTable
    assert ui.text is ui.Text
    assert ui.icon is ui.Icon
    assert "window" in ui.__all__
    assert len(ui.SIMPLE_ALIASES) >= 150


def test_lowercase_aliases_build_valid_components() -> None:
    node = ui.card(title="T")(ui.text("cuerpo"), ui.button("ok"))
    html = ui.render(node)
    assert "<h3" in html and "cuerpo" in html


def test_view_decorator_adds_routes(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    app = window("Multi", text("inicio"))

    @view("/ajustes")
    def ajustes():
        return text("panel de ajustes")

    assert "/ajustes" in app.routes
    _title, html, _bindings = app.render_page("/ajustes")
    assert "panel de ajustes" in html


def test_column_and_title_helpers(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    app = window("Helpers", title("Título", subtitle="Sub"), column(text("uno"), text("dos")))
    _title, html, _bindings = app.render_page("/")
    assert "Título" in html
    assert "Sub" in html
    assert "uno" in html and "dos" in html


def test_toast_uses_current_app(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    app = window("Toast", text("x"))
    sent: list[dict] = []
    app.server = type("S", (), {"broadcast": staticmethod(lambda payload: sent.append(payload) or 1)})()
    toast("guardado", "success")
    assert sent and sent[0]["message"] == "guardado"


def test_current_app_is_stable(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    app = window("Estable", text("x"))
    assert current_app() is app
    assert current_app("Otro título") is app
    assert app.title == "Otro título"


# --- señales dentro de los controles ---------------------------------------


def _checked(html: str) -> bool:
    import re

    return bool(re.search(r"<input[^>]* checked", html))


def test_switch_refleja_el_valor_de_la_senal(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    activo = state(False)
    app = window("Switch", ui.switch("Activo", checked=activo, on_change=activo))
    monkeypatch.setattr(app, "schedule_refresh", lambda: None)
    client = _bind(app)
    assert not _checked(client.last_html)

    activo.set(True)
    app._push_render(client)
    assert _checked(client.last_html)

    activo.set(False)
    app._push_render(client)
    assert not _checked(client.last_html)


def test_checkbox_refleja_el_valor_de_la_senal(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    activo = state(True)
    app = window("Check", ui.checkbox("Acepto", checked=activo))
    monkeypatch.setattr(app, "schedule_refresh", lambda: None)
    client = _bind(app)
    assert _checked(client.last_html)
    activo.set(False)
    app._push_render(client)
    assert not _checked(client.last_html)


def test_el_knob_del_switch_se_mueve(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    app = window("Switch", ui.switch("Activo", checked=True))
    _title, html, _b = app.render_page("/")
    # El desplazamiento tiene que ir en el track (hermano del input)…
    assert "peer-checked:[&>span]:translate-x-5" in html
    # …y no en el propio knob, donde el selector no aplicaría.
    assert html.count("peer-checked:[&>span]:translate-x-5") == 1


def test_input_escribe_el_valor_de_la_senal(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    nombre = state("Ana")
    app = window("Form", ui.input(value=nombre))
    monkeypatch.setattr(app, "schedule_refresh", lambda: None)
    client = _bind(app)
    assert 'value="Ana"' in client.last_html
    assert "Signal(" not in client.last_html

    nombre.set("Luis")
    app._push_render(client)
    assert 'value="Luis"' in client.last_html


def test_progress_y_compania_aceptan_senales(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    valor = state(40)
    app = window(
        "Progreso",
        ui.progress(valor),
        ui.progress_ring(valor),
        ui.meter(valor),
        ui.gauge(valor),
    )
    _title, html, _b = app.render_page("/")
    assert "Signal(" not in html
    assert "40" in html


# --- API imperativa: armar por partes con puntos -----------------------------


def test_add_admite_llamada_asignacion_y_suma() -> None:
    card = ui.Card()
    card.add(ui.text("uno"))
    card.add = ui.text("dos")
    card += ui.text("tres")
    card.add = [ui.text("cuatro"), ui.text("cinco")]

    assert len(card.children) == 5
    html = ui.render(card)
    for palabra in ("uno", "dos", "tres", "cuatro", "cinco"):
        assert palabra in html


def test_appshell_se_arma_por_partes() -> None:
    shell = ui.AppShell()
    shell.title_bar = ui.TitleBar("Mi app", icon=ui.icons.layers)
    shell.header = ui.MenuBar({"Archivo": [ui.ContextItem("Salir", icon=ui.icons.power)]})
    shell.sidebar = ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True))
    shell.status = ui.StatusBar(ui.text("Listo"))
    shell.add = ui.Container(pad=ui.pad.py_6)(ui.text("Contenido"))

    html = ui.render(shell)
    assert "Contenido" in html and "Panel" in html and "Listo" in html
    assert "iui-shell-drawer" in html, "el sidebar trae su botón en ventanas estrechas"


def test_menubar_admite_menus_por_corchetes() -> None:
    bar = ui.MenuBar(brand="App")
    bar["Archivo"] = [ui.ContextItem("Salir", icon=ui.icons.power)]
    bar["Archivo"] = [ui.ContextItem("Cerrar", icon=ui.icons.x)]

    assert [title for title, _items in bar.menus] == ["Archivo"]
    assert bar["Archivo"][0].label == "Cerrar"
    assert "Cerrar" in ui.render(bar)


def test_state_sin_nombre_es_estable_dentro_de_una_vista() -> None:
    """`state("")` en una vista conserva su señal entre repintados."""
    import interui as ui
    from interui.events import UIEvent, invoke

    app = ui.App("Vista")

    @app.page("/")
    def buscador() -> ui.Component:
        filtro = ui.state("")
        return ui.Screen(
            ui.Input(filtro.get(), label="Buscar", on_input=filtro),
            ui.Text(lambda: f"Buscando: {filtro.get()}"),
        )

    _title, html, bindings = app.render_page("/")
    assert "Buscando: " in html
    campo = next(
        (cid, handler)
        for cid, handlers in bindings.items()
        for event, handler in handlers.items()
        if event == "input"
    )
    invoke(campo[1], UIEvent(id=campo[0], event="input", value="hola"))

    claves = [name for name in app._signals if name.startswith("s_")]
    assert len(claves) == 1, claves
    _title, html, _bindings = app.render_page("/")
    assert "Buscando: hola" in html, "el texto escrito se perdió al repintar"


def test_dos_ventanas_en_el_mismo_proceso(monkeypatch) -> None:
    """`window()` registra la página `/` en cada app nueva, no solo en la primera."""
    import interui.simple as simple

    monkeypatch.setattr(simple, "_DEFAULT_APP", None)
    primera = simple.window("Una", simple.text("hola"))
    monkeypatch.setattr(simple, "_DEFAULT_APP", None)
    segunda = simple.window("Otra", simple.text("adiós"))

    assert primera is not segunda
    assert primera.has_page("/"), "la primera ventana perdió su página"
    assert segunda.has_page("/"), "la segunda ventana no registró la página"
