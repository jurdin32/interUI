import io
import json
import threading
import time
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
    app.handle_message(ws, {"t": "hello", "page": "/"})
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


def test_el_render_lo_pide_el_cliente_con_hello(tmp_path):
    """Al conectar solo se saluda: el render llega cuando el cliente dice qué página quiere."""
    app = make_app(tmp_path)
    ws = FakeSocket()
    app.on_client_connect(ws)
    assert [message["t"] for message in ws.sent] == ["ready"]

    app.handle_message(ws, {"t": "hello", "page": "/item/9"})
    assert ws.sent[-1]["t"] == "render"
    assert ws.sent[-1]["page"] == "/item/9"
    assert "item 9" in ws.sent[-1]["html"]


def test_refrescar_no_devuelve_a_inicio_antes_del_hello(tmp_path):
    """Un cliente recién conectado no recibe renders de una página que no pidió."""
    app = make_app(tmp_path)
    ws = FakeSocket()
    app.on_client_connect(ws)

    class Servidor:
        def clients_snapshot(self):
            return [ws]

    app.server = Servidor()
    app.refresh()
    assert [message["t"] for message in ws.sent] == ["ready"]

    app.handle_message(ws, {"t": "hello", "page": "/item/9"})
    app.refresh()
    assert ws.sent[-1]["t"] == "render"
    assert ws.sent[-1]["page"] == "/item/9"


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


def test_exit_is_an_alias_of_quit(tmp_path, monkeypatch):
    app = ui.App("Salida", data_dir=tmp_path / "data")
    calls: list[str] = []
    monkeypatch.setattr(app, "quit", lambda: calls.append("quit"))
    app.exit()
    app.close()
    assert calls == ["quit", "quit"]


def test_exit_stops_a_running_app(tmp_path):
    """``app.exit()`` cierra el bucle de ``run()`` y apaga el servidor."""
    import threading
    import time

    app = ui.App("Salida", data_dir=tmp_path / "data")

    @app.page("/")
    def index():
        return ui.Text("listo")

    worker = threading.Thread(target=app.run, kwargs={"window": "none"}, daemon=True)
    worker.start()
    try:
        for _ in range(200):
            if app.server is not None:
                break
            time.sleep(0.01)
        assert app.server is not None, "el servidor no arrancó"
        app.exit()
        worker.join(timeout=5)
        assert not worker.is_alive(), "run() siguió bloqueado tras app.exit()"
        assert app.server is None
    finally:
        app.quit()
        worker.join(timeout=5)


def test_desktop_mode_no_cae_al_navegador_sin_avisar(tmp_path, monkeypatch):
    """Sin pywebview, ``window="desktop"`` falla en claro en vez de abrir el navegador."""
    import interui.app as app_module

    monkeypatch.setattr(app_module, "desktop_available", lambda: False)
    opened: list[str] = []
    monkeypatch.setattr(app_module.webbrowser, "open", lambda url: opened.append(url))

    app = make_app(tmp_path)
    with pytest.raises(ui.DesktopError) as error:
        app.run(window="desktop")

    assert "pywebview" in str(error.value)
    assert opened == [], "no debe abrir el navegador por su cuenta"
    assert app.server is None, "no debe dejar el servidor encendido"


def test_window_auto_si_acepta_el_navegador_como_alternativa(tmp_path, monkeypatch):
    """``window="auto"`` sí es un opt-in explícito al navegador."""
    import threading
    import time

    import interui.app as app_module

    monkeypatch.setattr(app_module, "desktop_available", lambda: False)
    opened: list[str] = []
    monkeypatch.setattr(app_module.webbrowser, "open", lambda url: opened.append(url))

    app = make_app(tmp_path)
    worker = threading.Thread(target=app.run, kwargs={"window": "auto"}, daemon=True)
    worker.start()
    try:
        for _ in range(200):
            if app.server is not None and opened:
                break
            time.sleep(0.01)
        assert opened and opened[0].startswith("http://127.0.0.1:"), "no se abrió el navegador"
        app.exit()
        worker.join(timeout=5)
    finally:
        app.quit()
        worker.join(timeout=5)


def test_los_refrescos_seguidos_se_agrupan(tmp_path, monkeypatch):
    """Diez cambios rápidos no deben abrir diez renders en paralelo."""
    import threading
    import time

    app = make_app(tmp_path)
    renders: list[int] = []
    done = threading.Event()

    def fake_refresh() -> None:
        renders.append(1)
        time.sleep(0.05)

    monkeypatch.setattr(app, "refresh", fake_refresh)
    for _ in range(10):
        app.schedule_refresh()
    for _ in range(100):
        if not app._refresh_pending:
            break
        time.sleep(0.01)
    time.sleep(0.15)
    done.set()

    assert 1 <= len(renders) <= 3, f"se renderizó {len(renders)} veces para 10 cambios"
    assert not app._in_handler


def test_in_handler_es_por_hilo(tmp_path):
    """El estado de «estoy ejecutando un handler» no se comparte entre ventanas."""
    import threading

    app = make_app(tmp_path)
    app._begin_handler()
    try:
        seen: list[bool] = []
        worker = threading.Thread(target=lambda: seen.append(app._in_handler))
        worker.start()
        worker.join(timeout=5)
        assert app._in_handler is True
        assert seen == [False], "otro hilo no está ejecutando ningún handler"
    finally:
        app._end_handler()
    assert app._in_handler is False


def test_layout_envuelve_todas_las_paginas() -> None:
    """`app.layout` pone el armazón una vez y las vistas solo dan contenido."""
    app = ui.App("Con armazón")
    app.page("/")(lambda: ui.Heading("Inicio"))
    app.page("/otra")(lambda: ui.Heading("Otra"))

    sin_layout = app.render_page("/")[1]
    assert "iui-shell" not in sin_layout

    app.layout = ui.AppShell(
        title_bar=ui.TitleBar("Mi app", icon=ui.icons.users),
        header=ui.MenuBar({"Archivo": [ui.ContextItem("Salir")]}),
        status=ui.StatusBar(ui.text("Listo")),
    )
    for ruta, texto in (("/", "Inicio"), ("/otra", "Otra")):
        html = app.render_page(ruta)[1]
        assert "iui-shell" in html, f"{ruta}: falta el armazón"
        assert texto in html
        assert "Listo" in html and "Archivo" in html

    # La vista puede devolver None: el armazón se pinta igual.
    app.page("/vacia")(lambda: None)
    html = app.render_page("/vacia")[1]
    assert "iui-shell" in html


def test_current_app_devuelve_la_app_del_handler() -> None:
    """En un proyecto, `ui.current_app()` es la app que ejecuta el handler.

    Es lo que hace que un menú con `ui.current_app().quit()` cierre la ventana
    en vez de crear una app nueva y apagarla a ella.
    """

    class _WS:
        id = "w1"

        def __init__(self) -> None:
            self.enviados: list[dict[str, object]] = []

        def send_json(self, payload: dict[str, object]) -> None:
            self.enviados.append(payload)

    app = ui.App("Proyecto")
    visto: list[object] = []

    def salir() -> None:
        visto.append(ui.current_app())
        ui.current_app().quit()

    app.page("/")(lambda: ui.Screen(ui.Button("Salir", on_click=salir)))
    _title, _html, bindings = app.render_page("/")
    uid = next(iter(bindings))
    app._client_pages["w1"] = "/"
    app._bindings["w1"] = bindings

    ws = _WS()
    app._dispatch(ws, {"id": uid, "e": "click"})

    assert visto == [app], "current_app() debe ser la app en curso, no una nueva"
    assert app._stopped, "Salir tiene que detener la aplicación"


def test_quit_cierra_la_ventana_nativa_sin_bloquear() -> None:
    """`quit()` destruye la ventana en otro hilo: el handler no se queda colgado."""

    class _Desktop:
        def __init__(self) -> None:
            self.cerrada = threading.Event()

        def close(self) -> None:
            time.sleep(0.3)  # como el destroy real: bloquea hasta cerrar
            self.cerrada.set()

    app = ui.App("Escritorio")
    app._desktop = _Desktop()
    inicio = time.monotonic()
    app.quit()
    tardanza = time.monotonic() - inicio

    assert tardanza < 0.2, "quit() no debe esperar al destroy"
    assert app._stopped
    assert app._desktop.cerrada.wait(timeout=2), "la ventana no se cerró"
