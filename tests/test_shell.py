"""Pruebas del armazón de aplicación: menús, contexto, barras y notificaciones."""

from __future__ import annotations

import re

import pytest

import interui as ui


def render(node) -> str:
    return ui.render(node)


# --- MenuItem / ContextItem ---------------------------------------------------


def test_menu_item_tiene_rol_icono_y_atajo() -> None:
    html = render(ui.MenuItem("Guardar", icon="save", shortcut="Ctrl+S"))
    assert 'role="menuitem"' in html
    assert "Guardar" in html
    assert "Ctrl+S" in html
    assert "<svg" in html
    assert 'data-iui-menu-item="true"' in html


def test_menu_item_peligro_y_deshabilitado() -> None:
    html = render(ui.ContextItem("Eliminar", danger=True, disabled=True))
    assert "text-rose-600" in html
    assert "disabled" in html


def test_context_item_es_un_menu_item() -> None:
    assert issubclass(ui.ContextItem, ui.MenuItem)


def test_menu_item_con_href_es_un_enlace() -> None:
    html = render(ui.MenuItem("Documentación", href="https://tailwindcss.com"))
    assert "<a" in html
    assert 'href="https://tailwindcss.com"' in html


# --- MenuBar ------------------------------------------------------------------


def test_barra_de_menus_genera_trigger_y_panel_por_menu() -> None:
    html = render(
        ui.MenuBar(
            {
                "Archivo": [ui.ContextItem("Nuevo", icon="plus")],
                "Ver": [ui.ContextItem("Tema", icon="moon")],
            },
            brand="Mi app",
        )
    )
    assert 'role="menubar"' in html
    assert "Mi app" in html
    assert html.count("data-iui-menu-panel") == 2
    assert html.count('aria-expanded="false"') == 2
    triggers = re.findall(r'data-iui-menu="([^"]+)"', html)
    panels = re.findall(r'id="([^"]+)" data-iui-menu-panel', html)
    assert triggers == panels, "cada disparador debe apuntar a su panel"


def test_barra_de_menus_acepta_tuplas_dicts_y_separadores() -> None:
    html = render(
        ui.MenuBar(
            {
                "Archivo": [
                    ("Nuevo", "plus", None, "Ctrl+N"),
                    "-",
                    {"label": "Salir", "icon": "power", "danger": True},
                ]
            }
        )
    )
    assert 'role="separator"' in html
    assert "Nuevo" in html and "Ctrl+N" in html
    assert "text-rose-600" in html


def test_barra_de_menus_con_acciones_a_la_derecha() -> None:
    html = render(
        ui.MenuBar(
            {"Archivo": []},
            brand="X",
            actions=ui.Button("Nuevo", icon="plus"),
        )
    )
    assert "flex-1" in html
    assert ">Nuevo<" in html


# --- MenuButton ---------------------------------------------------------------


def test_menu_button_despliega_su_panel() -> None:
    html = render(
        ui.MenuButton(
            "Acciones",
            icon="settings",
            items=[ui.ContextItem("Editar", icon="edit"), ("Eliminar", "trash", None)],
        )
    )
    assert "Acciones" in html
    assert "data-iui-menu-panel" in html
    assert html.count('role="menuitem"') == 2


def test_menu_button_alineado_a_la_derecha() -> None:
    html = render(ui.MenuButton("Más", items=["Uno"], align="right"))
    assert "right-0" in html


# --- ContextMenu --------------------------------------------------------------


def test_menu_contextual_envuelve_el_contenido() -> None:
    html = render(
        ui.ContextMenu(
            ui.ContextItem("Abrir", icon="folder"),
            "-",
            ui.ContextItem("Borrar", icon="trash", danger=True),
            title="Opciones",
        )(ui.Text("Clic derecho"))
    )
    assert "data-iui-context=" in html
    assert "data-iui-context-panel" in html
    assert "position" not in html or "fixed" in html
    assert "Clic derecho" in html
    assert 'role="separator"' in html


def test_menu_contextual_ancho_minimo_y_pista() -> None:
    html = render(ui.ContextMenu("Uno", min_width="16rem", hint="Clic derecho"))
    assert "min-width:16rem" in html
    assert "Clic derecho" in html


def test_menu_contextual_sin_elementos() -> None:
    html = render(ui.ContextMenu()(ui.Text("zona")))
    assert "data-iui-context-panel" in html


# --- AppShell -----------------------------------------------------------------


def test_app_shell_coloca_todas_las_zonas() -> None:
    html = render(
        ui.AppShell(
            ui.Text("contenido"),
            title_bar=ui.TitleBar("Mi app", icon="layers"),
            header=ui.MenuBar({"Archivo": []}, brand="Mi app"),
            sidebar=ui.Sidebar(ui.SidebarItem("Panel", icon="grid", active=True)),
            status=ui.StatusBar(ui.Text("Listo")),
            footer=ui.Text("pie"),
        )
    )
    assert "h-screen" in html
    assert "contenido" in html and "Listo" in html and "pie" in html
    assert html.count("<main") == 1
    assert "overflow-y-auto" in html


def test_app_shell_sin_barra_lateral_no_envuelve_en_fila() -> None:
    html = render(ui.AppShell(ui.Text("solo")))
    assert html.count("<main") == 1
    assert "<main" in html


def test_app_shell_clases_personalizadas() -> None:
    html = render(ui.AppShell(ui.Text("x"), class_="bg-white"))
    assert "bg-white" in html and "h-screen" in html
    assert "bg-slate-50" not in html, "class_ debe ganar al valor por defecto"


# --- CommandBar ---------------------------------------------------------------


def test_command_bar_tiene_buscador_y_acciones() -> None:
    html = render(
        ui.CommandBar(
            ui.Button("Nuevo", icon="plus", variant="primary"),
            search_placeholder="Buscar tareas…",
            on_search=lambda: None,
        )
    )
    assert 'placeholder="Buscar tareas…"' in html
    assert ">Nuevo<" in html
    assert "backdrop-blur" in html


# --- NotificationButton -------------------------------------------------------


def test_notification_button_muestra_contador_y_panel() -> None:
    html = render(
        ui.NotificationButton(3, items=[ui.ContextItem("Nueva tarea", icon="check")])
    )
    assert ">3<" in html
    assert "data-iui-toggle" in html
    assert "Nueva tarea" in html


def test_notification_button_vacio() -> None:
    html = render(ui.NotificationButton())
    assert "Sin notificaciones" in html


def test_notification_button_abre_el_mismo_panel_que_el_disparador() -> None:
    html = render(ui.NotificationButton(1))
    toggle = re.search(r'data-iui-toggle="([^"]+)"', html)
    panel = re.search(r'id="([^"]+)" class="absolute right-0', html)
    assert toggle and panel and toggle.group(1) == panel.group(1)


# --- IconGrid -----------------------------------------------------------------


def test_icon_grid_muestra_todos_los_iconos() -> None:
    html = render(ui.IconGrid(columns=6))
    assert html.count("<svg") == len(ui.ICON_NAMES)
    assert "repeat(6" in html


def test_icon_grid_buscable_y_con_seleccion() -> None:
    picks: list[str] = []
    html = render(ui.IconGrid(names=["check", "x"], searchable=True, on_pick=picks.append))
    assert "data-iui-command" in html
    assert html.count('data-iui-emit="change"') == 2
    assert html.count('data-iui-item') == 2


def test_icon_grid_sin_seleccion_no_emite_eventos() -> None:
    html = render(ui.IconGrid(names=["check"]))
    assert "data-iui-emit" not in html


# --- integración con el servidor ----------------------------------------------


class _FakeSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.id = "fake"
        self.alive = True

    def send_json(self, payload: dict) -> None:
        self.sent.append(payload)

    def close(self) -> None:
        self.alive = False


def test_item_de_menu_ejecuta_su_handler_en_el_servidor(tmp_path) -> None:
    acciones: list[str] = []
    app = ui.App("Menús", data_dir=tmp_path / "data")

    @app.page("/")
    def index():
        return ui.Screen(
            ui.MenuBar(
                {
                    "Archivo": [
                        ui.ContextItem("Nuevo", id="nuevo", on_click=lambda: acciones.append("nuevo")),
                    ]
                }
            )
        )

    ws = _FakeSocket()
    app._client_pages[ws.id] = "/"
    _t, _b, bindings = app.render_page("/")
    app._bindings[ws.id] = bindings
    assert "click" in bindings["nuevo"]

    app.handle_message(ws, {"t": "event", "id": "nuevo", "e": "click"})
    assert acciones == ["nuevo"]


def test_menu_contextual_ejecuta_su_handler(tmp_path) -> None:
    acciones: list[str] = []
    app = ui.App("Contexto", data_dir=tmp_path / "data")

    @app.page("/")
    def index():
        return ui.Screen(
            ui.ContextMenu(
                ui.ContextItem("Abrir", id="abrir", on_click=lambda: acciones.append("abrir")),
            )(ui.Text("zona"))
        )

    ws = _FakeSocket()
    app._client_pages[ws.id] = "/"
    _t, _b, bindings = app.render_page("/")
    app._bindings[ws.id] = bindings
    app.handle_message(ws, {"t": "event", "id": "abrir", "e": "click"})
    assert acciones == ["abrir"]


def test_icon_grid_entrega_el_nombre_elegido(tmp_path) -> None:
    elegidos: list[str] = []
    app = ui.App("Iconos", data_dir=tmp_path / "data")

    @app.page("/")
    def index():
        return ui.Screen(
            ui.IconGrid(names=["check", "x"], id="galeria", on_pick=elegidos.append)
        )

    ws = _FakeSocket()
    app._client_pages[ws.id] = "/"
    _t, _b, bindings = app.render_page("/")
    app._bindings[ws.id] = bindings
    app.handle_message(ws, {"t": "event", "id": "galeria-i1", "e": "change", "v": "x"})
    assert elegidos == ["x"]


# --- AppShell: posición del sidebar -------------------------------------------


def test_sidebar_a_la_izquierda_por_defecto() -> None:
    html = render(ui.AppShell(ui.Text("x"), sidebar=ui.Sidebar(ui.SidebarItem("Panel"))))
    assert 'data-side="left"' in html
    assert html.index("<aside") < html.index("<main")


def test_sidebar_a_la_derecha() -> None:
    html = render(
        ui.AppShell(
            ui.Text("x"),
            sidebar=ui.Sidebar(ui.SidebarItem("Panel")),
            sidebar_position=ui.side.right,
        )
    )
    assert 'data-side="right"' in html
    assert html.index("<main") < html.index("<aside")


def test_posicion_del_sidebar_acepta_texto_y_espanol() -> None:
    for value in ("right", "derecha", "end", "r"):
        html = render(
            ui.AppShell(ui.Text("x"), sidebar=ui.Sidebar(), sidebar_position=value)
        )
        assert 'data-side="right"' in html, value


def test_posicion_del_sidebar_invalida() -> None:
    with pytest.raises(ValueError):
        ui.AppShell(ui.Text("x"), sidebar_position="arriba")


def test_app_shell_sin_sidebar_no_emite_fila() -> None:
    html = render(ui.AppShell(ui.Text("x")))
    assert "iui-shell-row" not in html
