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
    app._client_pages[client.id] = "/"
    _title, _html, bindings = app.render_page("/")
    app._bindings[client.id] = bindings
    app._push_render(client)
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
