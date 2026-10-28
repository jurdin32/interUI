"""Multiventana y niveles de cierre: ``close``, ``dispose`` y ``exit``."""

from __future__ import annotations

import types

import pytest

import interui as ui
from interui.desktop import DesktopError, Window


class FakeNative:
    """Sustituye a la ventana nativa en las pruebas sin abrir nada."""

    def __init__(self) -> None:
        self.window = object()
        self.closed = False
        self.title: str | None = None

    def close(self) -> None:
        self.closed = True
        self.window = None

    def set_title(self, title: str) -> None:
        self.title = title


class FakeClient:
    def __init__(self, window_id: str | None = None) -> None:
        self.id = window_id or "main"
        self.alive = True
        self.window_id = window_id
        self.sent: list[dict] = []

    def send_json(self, payload: dict) -> None:
        self.sent.append(payload)


def make_app(tmp_path) -> ui.App:
    app = ui.App("Ventanas", data_dir=tmp_path / "data")

    @app.page("/")
    def index():
        return ui.Text("principal")

    @app.page("/ajustes")
    def ajustes():
        return ui.Text("ajustes")

    return app


def add_window(app: ui.App, ident: str, route: str = "/") -> Window:
    window = Window(app, ident, f"Ventana {ident}", route)
    window.native = FakeNative()
    app._windows[ident] = window
    return window


# --- abrir ventanas -----------------------------------------------------------


def test_open_window_necesita_ventana_nativa(tmp_path):
    app = make_app(tmp_path)
    with pytest.raises(DesktopError):
        app.open_window("/ajustes")


def test_open_window_valida_la_ruta(tmp_path):
    app = make_app(tmp_path)
    with pytest.raises(ValueError):
        app.open_window("/no-existe")


def test_url_de_ventana_lleva_el_identificador(tmp_path):
    app = make_app(tmp_path)
    app.server = types.SimpleNamespace(url="http://127.0.0.1:9999/")
    assert app._url_for("/ajustes", "w1") == "http://127.0.0.1:9999/ajustes?w=w1"


# --- niveles de cierre ---------------------------------------------------------


def test_windows_lists_the_main_window_first(tmp_path):
    app = make_app(tmp_path)
    main = add_window(app, "main")
    extra = add_window(app, "w1", "/ajustes")
    assert app.windows == [main, extra]
    assert app.main_window is main


def test_close_cierra_solo_esa_ventana(tmp_path):
    app = make_app(tmp_path)
    main = add_window(app, "main")
    extra = add_window(app, "w1", "/ajustes")

    extra.close()

    assert extra.closed and not extra.is_open
    assert extra.native is None
    assert app.windows == [main]
    assert main.is_open
    assert app._stopped is False


def test_dispose_libera_la_ventana_indicada(tmp_path):
    app = make_app(tmp_path)
    add_window(app, "main")
    extra = add_window(app, "w1")

    app.dispose(extra)

    assert extra.closed
    assert app.windows and app.windows[0].ident == "main"


def test_app_close_cierra_la_ventana_del_evento(tmp_path):
    app = make_app(tmp_path)
    main = add_window(app, "main")
    extra = add_window(app, "w1", "/ajustes")

    # Un handler ejecutándose desde la segunda ventana.
    app._local.ws = FakeClient("w1")
    try:
        assert app.current_window is extra
        app.close()
    finally:
        app._local.ws = None

    assert extra.closed
    assert not main.closed
    assert app._stopped is False


def test_cerrar_la_ultima_ventana_termina_la_app(tmp_path):
    app = make_app(tmp_path)
    add_window(app, "main")
    app._local.ws = FakeClient(None)
    try:
        app.close()
    finally:
        app._local.ws = None
    assert app._stopped is True


def test_exit_cierra_todas_las_ventanas(tmp_path):
    app = make_app(tmp_path)
    main = add_window(app, "main")
    extra = add_window(app, "w1", "/ajustes")

    app.exit()

    assert extra.closed
    assert main.is_open is False or main.closed
    assert app._stopped is True


def test_current_window_cae_en_la_principal(tmp_path):
    app = make_app(tmp_path)
    main = add_window(app, "main")
    assert app.current_window is main
    app._local.ws = FakeClient("desconocida")
    try:
        assert app.current_window is main
    finally:
        app._local.ws = None


# --- navegación por ventana ----------------------------------------------------


def test_navigate_afecta_solo_a_su_ventana(tmp_path):
    app = make_app(tmp_path)
    add_window(app, "main")
    extra = add_window(app, "w1")

    cliente_w1 = FakeClient("w1")
    cliente_main = FakeClient(None)
    app.server = types.SimpleNamespace(clients={cliente_w1, cliente_main})

    extra.navigate("/ajustes")

    assert extra.route == "/ajustes"
    assert cliente_w1.sent == [{"t": "nav", "path": "/ajustes"}]
    assert cliente_main.sent == []


def test_clients_for_filtra_por_ventana(tmp_path):
    app = make_app(tmp_path)
    w1 = FakeClient("w1")
    principal = FakeClient(None)
    app.server = types.SimpleNamespace(clients={w1, principal})
    assert app.clients_for("w1") == [w1]
    assert app.clients_for("main") == [principal]


def test_set_title_de_la_ventana(tmp_path):
    app = make_app(tmp_path)
    window = add_window(app, "w1")
    window.set_title("Otro título")
    assert window.title == "Otro título"
    assert window.native.title == "Otro título"


def test_la_ruta_de_la_ventana_es_la_pagina_inicial(tmp_path):
    app = make_app(tmp_path)
    add_window(app, "w1", "/ajustes")
    cliente = FakeClient("w1")
    app.on_client_connect(cliente)
    assert app._client_pages[cliente.id] == "/ajustes"
