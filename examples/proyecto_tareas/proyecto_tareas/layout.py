"""Armazón compartido: barra de título, menú lateral y barra de estado."""

from typing import Any

import interui as ui

MENU = (
    ("Inicio", ui.icons.home, "/"),
    ("Notas", ui.icons.check, "/notas"),
)


def sidebar(active: str = "/") -> ui.Sidebar:
    """Menú lateral; cada entrada navega sin recargar la ventana."""
    barra = ui.Sidebar(title="Navegación")
    for label, icon, path in MENU:
        barra.add = ui.SidebarItem(
            label,
            icon=icon,
            active=path == active,
            data={"iui-link": path},
            class_="cursor-pointer",
        )
    return barra


def frame(*content: Any, title: str = "proyecto_tareas", active: str = "/") -> ui.AppShell:
    """Envuelve el contenido de una vista en el armazón de la app."""
    shell = ui.AppShell()
    shell.title_bar = ui.TitleBar(title, icon=ui.icons.layers)
    shell.header = ui.MenuBar({"Archivo": [_salir()]}, brand=title)
    shell.sidebar = sidebar(active)
    shell.status = ui.StatusBar(ui.text("Listo"))
    shell.add = ui.Container(pad=ui.pad.p_4, md_pad=ui.pad.p_8)(*content)
    return shell


def _salir() -> ui.ContextItem:
    """Cierra la ventana; `app.exit()` cerraría también el proceso."""

    def cerrar() -> None:
        from proyecto_tareas.app import app

        app.close()

    return ui.ContextItem("Salir", icon=ui.icons.power, on_click=cerrar)
