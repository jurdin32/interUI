"""Diálogos modales: avisos, confirmaciones, entradas y ventanas propias."""

from __future__ import annotations

import re

import pytest

import interui as ui
from interui import dialog
from interui.dialogs import Dialog
from interui.simple import state, text, window


class Client:
    def __init__(self) -> None:
        self.id = "cliente"
        self.alive = True
        self.sent: list[dict] = []

    def send_json(self, payload: dict) -> None:
        self.sent.append(payload)

    @property
    def html(self) -> str:
        return self.sent[-1]["html"]


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    application = window("Diálogos", text("contenido"))
    application.close_all_dialogs()
    yield application
    application.close_all_dialogs()


def bind(app: ui.App) -> tuple[Client, dict]:
    client = Client()
    app._client_pages[client.id] = "/"
    _title, _html, bindings = app.render_page("/")
    app._bindings[client.id] = bindings
    app._push_render(client)
    return client, bindings


def ids_with(bindings: dict, event: str) -> list[str]:
    return [uid for uid, handlers in bindings.items() if event in handlers]


def test_info_dialog_opens_and_closes(app) -> None:
    node = dialog.info("Proceso terminado", title="Listo")
    client, _bindings = bind(app)
    assert node in app.dialogs
    assert 'role="dialog"' in client.html
    assert "Proceso terminado" in client.html
    assert "Listo" in client.html
    node.close()
    assert app.dialogs == []
    _title, html, _b = app.render_page("/")
    assert 'role="dialog"' not in html


def test_show_has_single_close_button(app) -> None:
    dialog.show("Solo informativo")
    _title, html, _b = app.render_page("/")
    assert "Cerrar" in html
    assert "Aceptar" not in html


@pytest.mark.parametrize(
    ("method", "level", "icon_fragment"),
    [
        ("info", "info", "circle"),
        ("success", "success", "m8 12.5"),
        ("warning", "warning", "M12 3.5"),
        ("error", "error", "m9 9 6 6"),
        ("critical", "critical", "M12 3.5"),
    ],
)
def test_levels_render_with_their_icon(app, method, level, icon_fragment) -> None:
    node = getattr(dialog, method)(f"mensaje {level}", title=level)
    assert node.level == level
    _title, html, _b = app.render_page("/")
    assert "mensaje" in html
    assert icon_fragment in html


def test_alert_accepts_custom_level(app) -> None:
    node = dialog.alert("atención", level="warning")
    assert node.level == "warning"
    _title, html, _b = app.render_page("/")
    assert "atención" in html


def test_confirm_accept_runs_handler_and_closes(app) -> None:
    received: list[ui.UIEvent] = []
    dialog.confirm("¿Eliminar?", title="Borrar", on_accept=received.append)
    client, bindings = bind(app)

    submit_ids = [uid for uid in ids_with(bindings, "click") if uid.endswith("-ok")]
    assert submit_ids, "el botón de aceptar debe tener handler"
    app.handle_message(client, {"t": "event", "id": submit_ids[0], "e": "click"})

    assert received and received[0].event == "click"
    assert app.dialogs == []


def test_cancel_runs_handler_and_closes(app) -> None:
    cancelled: list[ui.UIEvent] = []
    dialog.confirm("¿Seguir?", on_cancel=cancelled.append)
    client, bindings = bind(app)
    cancel_ids = [uid for uid in ids_with(bindings, "click") if uid.endswith("-cancel")]
    app.handle_message(client, {"t": "event", "id": cancel_ids[0], "e": "click"})
    assert len(cancelled) == 1
    assert app.dialogs == []


def test_input_returns_single_value(app) -> None:
    received: list[ui.UIEvent] = []
    dialog.input("Nombre", title="Nuevo", on_accept=received.append)
    client, bindings = bind(app)

    submit_ids = [uid for uid in ids_with(bindings, "submit")]
    assert submit_ids, "el formulario debe declarar submit"
    app.handle_message(
        client,
        {
            "t": "event",
            "id": submit_ids[0],
            "e": "submit",
            "data": {"form": {"value": "Ana Ruiz"}},
        },
    )

    assert received[0].value == "Ana Ruiz"
    assert received[0].data["values"] == {"value": "Ana Ruiz"}
    assert app.dialogs == []


def test_input_with_signal(app) -> None:
    nombre = state("")
    dialog.input("Nombre", on_accept=nombre)
    client, bindings = bind(app)
    app.handle_message(
        client,
        {"t": "event", "id": ids_with(bindings, "submit")[0], "e": "submit",
         "data": {"form": {"value": "Luis"}}},
    )
    assert nombre.get() == "Luis"


def test_form_collects_all_fields(app) -> None:
    received: list[ui.UIEvent] = []
    dialog.form(
        [
            {"name": "nombre", "label": "Nombre"},
            {"name": "correo", "label": "Correo"},
            {"name": "notas", "label": "Notas", "type": "textarea"},
        ],
        title="Alta",
        on_accept=received.append,
    )
    client, bindings = bind(app)
    _title, html, _b = app.render_page("/")
    assert html.count("<form") == 1
    assert "Correo" in html and "<textarea" in html

    app.handle_message(
        client,
        {"t": "event", "id": ids_with(bindings, "submit")[0], "e": "submit",
         "data": {"form": {"nombre": "Ana", "correo": "ana@e.com", "notas": "hola"}}},
    )
    assert received[0].data["values"]["correo"] == "ana@e.com"
    assert received[0].value is None


def test_backdrop_click_closes_with_on_close(app) -> None:
    closed: list[ui.UIEvent] = []
    dialog.info("hola", on_close=closed.append)
    client, bindings = bind(app)
    backdrop_ids = [uid for uid in ids_with(bindings, "click") if uid.endswith("-backdrop")]
    assert backdrop_ids
    app.handle_message(client, {"t": "event", "id": backdrop_ids[0], "e": "click"})
    assert len(closed) == 1
    assert app.dialogs == []


def test_escape_declared_only_when_dismissible(app) -> None:
    app.close_all_dialogs()
    dismissible = dialog.info("a")
    _title, _html, bindings = app.render_page("/")
    assert sum(1 for handlers in bindings.values() if "escape" in handlers) == 1

    app.close_all_dialogs()
    dialog.info("b", dismissible=False)
    _title, _html, bindings = app.render_page("/")
    assert sum(1 for handlers in bindings.values() if "escape" in handlers) == 0
    dismissible.close()


def test_custom_dialog_buttons(app) -> None:
    fired: list[str] = []
    node = dialog.custom(
        ui.text("contenido propio"),
        title="A medida",
        buttons=[("Cancelar", lambda: fired.append("cancel"), "outline"),
                 ("Guardar", lambda: fired.append("save"), "primary")],
    )
    client, bindings = bind(app)
    assert "contenido propio" in client.html
    buttons = [uid for uid in ids_with(bindings, "click") if re.search(r"-b\d+$", uid)]
    assert len(buttons) == 2
    app.handle_message(client, {"t": "event", "id": buttons[1], "e": "click"})
    assert fired == ["save"]
    node.close()


def test_custom_width_and_scroll(app) -> None:
    dialog.custom(ui.text("x"), width="lg", scrollable=True)
    _title, html, _b = app.render_page("/")
    assert "max-w-lg" in html
    assert "overflow-y-auto" in html


def test_dialog_without_title_hides_header(app) -> None:
    dialog.info("solo mensaje")
    _title, html, _b = app.render_page("/")
    assert "dlg-title-" not in html


def test_close_all(app) -> None:
    dialog.info("uno")
    dialog.info("dos")
    assert len(app.dialogs) == 2
    app.close_all_dialogs()
    assert app.dialogs == []


def test_dialog_survives_rerender_and_route_change(app) -> None:
    dialog.info("persistente")
    _title, html, _b = app.render_page("/")
    assert "persistente" in html
    _title, html, _b = app.render_page("/")
    assert "persistente" in html


def test_direct_construction(app) -> None:
    node = Dialog("texto", title="Manual", level="warning", width="sm")
    app.show_dialog(node)
    _title, html, _b = app.render_page("/")
    assert "Manual" in html and "max-w-sm" in html
    node.close()


def test_api_close_without_argument_closes_last(app) -> None:
    dialog.info("primero")
    dialog.info("segundo")
    dialog.close()
    assert len(app.dialogs) == 1
    assert dialog.close is not None


# --- niveles de modal ---------------------------------------------------------


def test_dialogo_de_primer_plano_no_se_puede_cerrar(app) -> None:
    accepted: list[object] = []
    node = Dialog(
        ui.Text("Debes aceptar"),
        title="Bloqueante",
        layer=ui.layer.blocking,
        on_accept=accepted.append,
    )
    _title, html, _bindings = app.render_page("/")
    app.show_dialog(node)
    _title, html, _bindings = app.render_page("/")

    assert 'data-layer="blocking"' in html
    assert node.is_blocking is True
    assert node.dismissible is False and node.closable is False
    assert "Cancelar" not in html          # sin salida lateral
    assert "Aceptar" in html

    # ni Escape ni la X están enlazados
    assert "escape" not in node.handlers
    assert not any(uid.endswith("-x") for uid in _bindings)


def test_un_bloqueante_no_deja_abrir_otros(app) -> None:
    blocking = Dialog(ui.Text("Acepta"), title="Primero", layer=ui.layer.blocking)
    app.show_dialog(blocking)
    otro = dialog.info("No debería abrirse")
    result = app.show_dialog(otro)

    assert result is blocking
    assert otro not in app.dialogs
    assert app.blocking_dialog is blocking


def test_un_bloqueante_no_se_cierra_sin_aceptarlo(app) -> None:
    blocking = Dialog(ui.Text("Acepta"), title="Primero", layer=ui.layer.blocking)
    app.show_dialog(blocking)
    app.close_dialog()
    assert blocking in app.dialogs
    blocking.close()                       # cerrarlo explícitamente sí puede
    assert app.dialogs == []


def test_force_abre_encima_de_un_bloqueante(app) -> None:
    blocking = Dialog(ui.Text("Acepta"), title="Primero", layer=ui.layer.blocking)
    app.show_dialog(blocking)
    extra = dialog.info("Encima")
    assert app.show_dialog(extra, force=True) is extra
    assert extra in app.dialogs


def test_modal_normal_sigue_siendo_cerrable(app) -> None:
    node = dialog.info("Hola")          # dialog.info ya lo abre
    assert node.is_blocking is False
    app.close_dialog()
    assert app.dialogs == []


# --- snackbars ----------------------------------------------------------------


def test_snackbar_con_texto_icono_y_accion() -> None:
    node = ui.Snackbar(
        "Proyecto archivado",
        title="Hecho",
        icon=ui.icons.check,
        action=("Deshacer", lambda event: None),
        variant=ui.variant.success,
    )
    html = ui.render(node)
    assert "Proyecto archivado" in html
    assert "Hecho" in html
    assert "<svg" in html
    assert "Deshacer" in html
    assert "bg-emerald-600" in html
    assert 'data-iui-dismiss="true"' in html
    assert "fixed bottom-4 right-4" in html


def test_snackbar_con_imagen() -> None:
    html = ui.render(ui.Snackbar("Con foto", image="https://ejemplo/x.png"))
    assert '<img src="https://ejemplo/x.png"' in html
    assert "object-cover" in html


def test_snackbar_sin_icono() -> None:
    assert "<svg" not in ui.render(ui.Snackbar("Solo texto"))


def test_snackbar_posiciones() -> None:
    html = ui.render(ui.Snackbar("Arriba", position="top_center"))
    assert "top-4 left-1/2 -translate-x-1/2" in html
    with pytest.raises(ValueError):
        ui.Snackbar("x", position="en_medio")


def test_snackbar_con_temporizador() -> None:
    html = ui.render(ui.Snackbar("Se va", duration=1500))
    assert 'data-iui-duration="1500"' in html
    assert 'data-iui-snackbar="true"' in html


def test_snackbar_con_marcado_svg_propio() -> None:
    html = ui.render(ui.Snackbar("x", icon='<svg class="mio"></svg>'))
    assert 'class="mio"' in html


def test_notify_manda_icono_e_imagen(monkeypatch) -> None:
    app = window("Snackbars", text("contenido"))

    class FakeServer:
        def __init__(self) -> None:
            self.sent: list[dict] = []

        def broadcast(self, payload: dict) -> None:
            self.sent.append(payload)

    app.server = FakeServer()
    app.notify(
        "Guardado", "success", title="Hecho", icon=ui.icons.check,
        duration=2000, action={"label": "Deshacer", "js": "1"},
    )
    payload = app.server.sent[0]
    assert payload["t"] == "toast"
    assert payload["title"] == "Hecho"
    assert payload["duration"] == 2000
    assert payload["icon"].startswith("<svg")
    assert payload["action"] == {"label": "Deshacer", "js": "1"}

    app.notify("Con imagen", image="https://ejemplo/y.png")
    assert app.server.sent[1]["image"] == "https://ejemplo/y.png"


def test_toast_compacto_acepta_opciones() -> None:
    from interui import toast as toast_fn

    app = window("Snackbars", text("contenido"))

    class FakeServer:
        def __init__(self) -> None:
            self.sent: list[dict] = []

        def broadcast(self, payload: dict) -> None:
            self.sent.append(payload)

    app.server = FakeServer()
    toast_fn("Listo", "success", title="Hecho", icon=ui.icons.check)
    assert app.server.sent[0]["title"] == "Hecho"
    assert app.server.sent[0]["icon"].startswith("<svg")
