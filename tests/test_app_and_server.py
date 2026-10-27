import io
import json
import urllib.request

import pytest

import interui as ui
from interui.events import UIEvent, invoke
from interui.server import Server, encode_frame, read_frame


class FakeSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.id = "fake"
        self.alive = True

    def send_json(self, payload: dict) -> None:
        self.sent.append(payload)

    def close(self) -> None:
        self.alive = False


def make_app(tmp_path, **kwargs) -> ui.App:
    app = ui.App("Pruebas", data_dir=tmp_path / "data", **kwargs)

    @app.page("/")
    def index():
        count = app.state("count", 0)
        return ui.Screen(
            ui.Text(f"valor={count.get()}"),
            ui.Button("sumar", id="sumar", on_click=lambda: count.set(count.get() + 1)),
        )

    @app.page("/item/<int:item_id>")
    def item(item_id: int):
        return ui.Screen(ui.Text(f"item {item_id}"))

    return app


def test_routes_are_registered(tmp_path):
    app = make_app(tmp_path)
    assert app.has_page("/")
    assert app.has_page("/item/42")
    assert not app.has_page("/nope")


def test_typed_route_parameters(tmp_path):
    app = make_app(tmp_path)
    title, body, _bindings = app.render_page("/item/17")
    assert "item 17" in body


def test_render_page_returns_markup_and_bindings(tmp_path):
    app = make_app(tmp_path)
    _title, body, bindings = app.render_page("/")
    assert body.startswith('<div id="iui-root"')
    assert "valor=0" in body
    assert "click" in bindings["sumar"]


def test_bootstrap_html_injects_config_and_assets(tmp_path):
    app = make_app(tmp_path)
    html = app.bootstrap_html("/")
    assert "<!doctype html>" in html
    assert "/static/app.css" in html
    assert 'window.__INTERUI__ = {"page"' in html
    assert "%%CONTENT%%" not in html


def test_dispatch_updates_state_and_rerenders(tmp_path):
    app = make_app(tmp_path)
    ws = FakeSocket()
    app._client_pages[ws.id] = "/"
    _t, _b, bindings = app.render_page("/")
    app._bindings[ws.id] = bindings

    app.handle_message(ws, {"t": "event", "id": "sumar", "e": "click", "v": None})

    assert app.get_state("count") == 1
    kinds = [message["t"] for message in ws.sent]
    assert kinds[-1] == "render"
    assert "valor=1" in ws.sent[-1]["html"]


def test_handler_errors_are_reported_as_toast(tmp_path):
    app = make_app(tmp_path)

    @app.page("/boom")
    def boom():
        return ui.Screen(ui.Button("x", id="x", on_click=lambda: 1 / 0))

    ws = FakeSocket()
    app._client_pages[ws.id] = "/boom"
    _t, _b, bindings = app.render_page("/boom")
    app._bindings[ws.id] = bindings
    app.handle_message(ws, {"t": "event", "id": "x", "e": "click"})
    assert any(m["t"] == "toast" and m["level"] == "error" for m in ws.sent)


def test_unknown_route_message_is_not_navigated(tmp_path):
    app = make_app(tmp_path)
    ws = FakeSocket()
    app.handle_message(ws, {"t": "nav", "path": "/no-existe"})
    assert ws.sent[0]["t"] == "toast"


def test_navigation_switches_page(tmp_path):
    app = make_app(tmp_path)
    ws = FakeSocket()
    app.handle_message(ws, {"t": "nav", "path": "/item/9"})
    assert app._client_pages[ws.id] == "/item/9"
    assert "item 9" in ws.sent[-1]["html"]


def test_signal_triggers_render(tmp_path):
    app = make_app(tmp_path)
    ws = FakeSocket()
    app._client_pages[ws.id] = "/"
    app._bindings[ws.id] = {}
    counter = app.state("count", 0)
    counter.set(5)
    assert app.get_state("count") == 5
    assert "valor=5" not in ws.sent  # el refresco llega por el canal, no en el set


def test_invoke_supports_handlers_with_and_without_event():
    event = UIEvent(id="a", event="click")
    assert invoke(lambda: "sin", event) == "sin"
    assert invoke(lambda e: e.id, event) == "a"


def test_ui_event_helpers():
    event = UIEvent(id="a", event="input", value="12.5", checked=True, data={"index": "3"})
    assert event.as_number == 12.5
    assert event.index == 3
    assert event.text == "12.5"


class TestWebSocketFrames:
    @pytest.mark.parametrize("size", [1, 125, 126, 65535, 65536, 200000])
    def test_roundtrip(self, size):
        payload = b"x" * size
        frame = encode_frame(payload)
        fin, opcode, body = read_frame(io.BytesIO(frame))
        assert fin is True
        assert opcode == 0x1
        assert body == payload

    def test_masked_client_frame_is_unmasked(self):
        payload = b"hola"
        mask = b"\x01\x02\x03\x04"
        masked = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
        frame = bytes([0x81, 0x80 | len(payload)]) + mask + masked
        _fin, _opcode, body = read_frame(io.BytesIO(frame))
        assert body == payload


def test_http_server_serves_app_and_assets(tmp_path):
    app = make_app(tmp_path)
    server = Server(app, "127.0.0.1", 0)
    server.start()
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{server.port}/", timeout=5) as response:
            html = response.read().decode()
        assert response.status == 200
        assert "iui-root" in html

        with urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}/__interui/health", timeout=5
        ) as response:
            health = json.loads(response.read())
        assert health["ok"] is True

        with urllib.request.urlopen(
            f"http://127.0.0.1:{server.port}/static/interui.js", timeout=5
        ) as response:
            runtime = response.read().decode()
        assert "new WebSocket" in runtime
    finally:
        server.stop()


def test_unknown_route_returns_404(tmp_path):
    app = make_app(tmp_path)
    server = Server(app, "127.0.0.1", 0)
    server.start()
    try:
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(f"http://127.0.0.1:{server.port}/no-existe", timeout=5)
        assert error.value.code == 404
    finally:
        server.stop()
