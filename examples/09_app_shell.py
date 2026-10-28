"""Armazón de app: sidebar a la izquierda o derecha, modales por niveles y cierre.

    python examples/09_app_shell.py

* ``sidebar_position`` acepta ``ui.side.left`` / ``ui.side.right`` y acepta
  señales, así que el usuario puede cambiarla desde la interfaz.
* ``ui.layer.blocking`` abre un modal de primer plano: sin aspa, sin Escape y sin
  clic fuera; el único camino es aceptar.
* ``app.close()`` cierra solo esta ventana, ``app.exit()`` cierra la aplicación.
"""

from interui import (
    App, AppShell, Button, Container, Dialog, Heading, MenuBar, Muted, Row, Screen,
    Section, Sidebar, SidebarItem, StatusBar, Text, TitleBar,
    colors, dialog, font, gap, icons, layer, pad, side, variant,
)

app = App("Armazón", width=1180, height=760)
lado = app.state("lado", "left")


def cambiar_lado() -> None:
    lado.set(side.right if lado.get() == "left" else side.left)


def modal_normal() -> None:
    dialog.confirm(
        "¿Quieres archivar el proyecto?",
        title="Archivar",
        on_accept=lambda _e: app.notify("Archivado", "success", icon=icons.check),
    )


def modal_bloqueante() -> None:
    app.show_dialog(
        Dialog(
            Text("Hay una importación en curso. Termínala antes de salir."),
            title="Proceso en marcha",
            layer=layer.blocking,
            on_accept=lambda _e: app.notify("Entendido", "info", icon=icons.info),
        )
    )


@app.page("/")
def index():
    return Screen(
        AppShell(
            Container(pad=pad.py_8)(
                Heading("Armazón de aplicación", level=1),
                Muted("El sidebar cambia de lado sin tocar el CSS: el borde se mueve solo."),
                Section(title="Sidebar")(
                    Row(gap=gap.all_3)(
                        Button(
                            f"Sidebar a la {'derecha' if lado.get() == 'left' else 'izquierda'}",
                            icon=icons.arrow_right if lado.get() == "left" else icons.arrow_left,
                            variant=variant.secondary,
                            on_click=cambiar_lado,
                        )
                    ),
                ),
                Section(title="Niveles de modal")(
                    Row(gap=gap.all_3)(
                        Button("Modal normal", icon=icons.info, on_click=modal_normal),
                        Button(
                            "Modal de primer plano",
                            icon=icons.lock,
                            variant=variant.danger,
                            on_click=modal_bloqueante,
                        ),
                    ),
                    Text(
                        "El bloqueante no se cierra con Escape ni con el fondo.",
                        font=font.xs,
                        color=colors.slate_500,
                    ),
                ),
                Section(title="Cierre")(
                    Row(gap=gap.all_3)(
                        Button("Cerrar esta ventana", icon=icons.close, on_click=app.close),
                        Button("Salir de la app", icon=icons.power, variant=variant.danger,
                               on_click=app.exit),
                    ),
                ),
            ),
            title_bar=TitleBar("Armazón", icon="layers"),
            header=MenuBar(
                {
                    "Archivo": [
                        {"label": "Cambiar sidebar", "icon": icons.columns, "on_click": cambiar_lado},
                        "-",
                        {"label": "Salir", "icon": icons.power, "on_click": app.exit},
                    ],
                    "Ver": [
                        {"label": "Modal bloqueante", "icon": icons.lock, "on_click": modal_bloqueante},
                    ],
                },
                brand="Armazón",
            ),
            sidebar=Sidebar(
                SidebarItem("Panel", icon=icons.grid, active=True),
                SidebarItem("Clientes", icon=icons.users),
                SidebarItem("Ajustes", icon=icons.settings, badge="3"),
                title="Navegación",
            ),
            sidebar_position=lado,
            status=StatusBar(Text(f"Sidebar: {lado.get()}")),
        )
    )


if __name__ == "__main__":
    app.run()
