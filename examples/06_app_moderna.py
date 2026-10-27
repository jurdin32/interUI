"""Aplicación «moderna» de referencia: armazón, menús, paleta e iconos.

    python examples/06_app_moderna.py

Reúne todas las piezas de escritorio que ofrece interUI:

* ``AppShell`` con barra de título, barra de menús, barra lateral, contenido con
  scroll y barra de estado.
* ``MenuBar`` con desplegables (Archivo, Ver, Ayuda) que ejecutan handlers de
  Python, con atajos y separadores.
* ``CommandBar`` con búsqueda en vivo y acciones.
* ``ContextMenu``: clic derecho sobre la tabla abre un menú contextual.
* ``NotificationButton`` con contador en la barra de menús.
* ``IconGrid``: galería de los 200+ iconos incluidos, buscable y seleccionable.
* Diálogos (info, entrada de texto), toasts y tema claro/oscuro.
"""

from __future__ import annotations

from interui import (
    App, Badge, Button, Card, CommandBar, Container, ContextItem, ContextMenu, DataTable,
    Divider, Heading, IconGrid, ListItem, MenuBar, NotificationButton, Stack,
    StatusBar, Text, TitleBar, AppShell, Sidebar, SidebarItem, dialog, toast,
)

app = App("interUI · app moderna", width=1180, height=780)

# ---------------------------------------------------------------------------
# Estado reactivo
# ---------------------------------------------------------------------------
seccion = app.state("seccion", "Panel")
filtro = app.state("filtro", "")
notificaciones = app.state("notificaciones", 3)

FILAS = [
    {"nombre": "Ana Torres", "rol": "Diseño", "estado": "Activa"},
    {"nombre": "Luis Prado", "rol": "Backend", "estado": "Activa"},
    {"nombre": "Marta Ruiz", "rol": "Producto", "estado": "Invitada"},
    {"nombre": "Iván Sosa", "rol": "QA", "estado": "Activa"},
]


# ---------------------------------------------------------------------------
# Acciones de los menús
# ---------------------------------------------------------------------------
def nuevo() -> None:
    dialog.input(
        "Nombre del proyecto",
        title="Nuevo proyecto",
        placeholder="Mi proyecto",
        on_accept=lambda valor: toast(f"Proyecto «{valor}» creado", level="success"),
    )


def alternar_tema() -> None:
    toast(f"Tema {app.toggle_theme()}", level="info")


def acerca_de() -> None:
    dialog.info(
        "interUI genera ventanas nativas con HTML, Tailwind y Python.",
        title="Acerca de interUI",
        level="success",
    )


def eliminar_fila(nombre: str) -> None:
    dialog.confirm(
        f"¿Eliminar a {nombre}?",
        title="Eliminar",
        level="critical",
        on_accept=lambda: toast(f"{nombre} eliminado", level="warning"),
    )


def abrir_fila(nombre: str) -> None:
    dialog.show(f"Ficha de {nombre}", title=nombre, icon="user")


# ---------------------------------------------------------------------------
# Vistas
# ---------------------------------------------------------------------------
def vista_panel() -> object:
    return Container(class_="py-6")(
        Heading("Panel", level=2),
        Text("Todo lo que necesitas para construir apps de escritorio.", tone="muted"),
        Divider(),
        DataTable(
            headers=["Nombre", "Rol", "Estado"],
            rows=[[f["nombre"], f["rol"], Badge(f["estado"], variant="success")] for f in FILAS],
            striped=True,
            hover=True,
        ),
    )


def vista_iconos() -> object:
    return Container(class_="py-6")(
        Heading("Iconos", level=2),
        Text("Haz clic en un icono para copiar su nombre al portapapeles.", tone="muted"),
        Divider(),
        Card(
            IconGrid(
                columns=10,
                searchable=True,
                on_pick=lambda nombre: toast(f"Icono: {nombre}"),
            )
        ),
    )


VISTAS = {"Panel": vista_panel, "Iconos": vista_iconos}


def contenido() -> object:
    vista = VISTAS.get(seccion.get(), vista_panel)
    return ContextMenu(
        ContextItem("Abrir", icon="folder", on_click=lambda: abrir_fila("Ana Torres")),
        ContextItem("Editar", icon="edit"),
        "-",
        ContextItem("Eliminar", icon="trash", danger=True, on_click=lambda: eliminar_fila("Ana Torres")),
        hint="Clic derecho para opciones",
    )(vista())


def navegacion() -> object:
    return Sidebar(
        *[
            SidebarItem(
                nombre,
                icon="layout-dashboard" if nombre == "Panel" else "smile",
                active=seccion.get() == nombre,
                on_click=lambda nombre=nombre: seccion.set(nombre),
            )
            for nombre in VISTAS
        ],
        title="Navegación",
    )


def barra_de_menus() -> object:
    return MenuBar(
        {
            "Archivo": [
                ContextItem("Nuevo proyecto…", icon="plus", shortcut="Ctrl+N", on_click=nuevo),
                ContextItem("Abrir carpeta…", icon="folder", shortcut="Ctrl+O"),
                "-",
                ContextItem("Salir", icon="power", danger=True, on_click=app.quit),
            ],
            "Ver": [
                ContextItem("Cambiar tema", icon="moon", shortcut="Ctrl+T", on_click=alternar_tema),
                ContextItem("Iconos", icon="smile", on_click=lambda: seccion.set("Iconos")),
            ],
            "Ayuda": [
                ContextItem("Acerca de interUI", icon="info", on_click=acerca_de),
            ],
        },
        brand="interUI",
        actions=Stack(
            CommandBar(
                Button("Nuevo", icon="plus", variant="primary", on_click=nuevo),
                search=filtro.get(),
                search_placeholder="Buscar…",
                on_search=lambda: None,
                class_="border-0 bg-transparent px-0 py-0",
            ),
            NotificationButton(
                notificaciones.get(),
                items=[
                    ListItem("Nueva tarea asignada", icon="check"),
                    ListItem("Comentario en tu informe", icon="mail"),
                ],
            ),
            direction="row",
            gap=2,
            align="center",
        ),
    )


@app.page("/")
def index() -> object:
    return AppShell(
        contenido(),
        title_bar=TitleBar("interUI · app moderna", icon="layers"),
        header=barra_de_menus(),
        sidebar=navegacion(),
        status=StatusBar(
            Text(seccion.get(), weight="semibold"),
            Text("·"),
            Text("Todo guardado", tone="muted"),
            # Si al arrancar se detectó una versión nueva, se muestra en la barra.
            (
                Badge(f"interUI {app.update.latest} disponible", variant="warning")
                if app.update_available
                else None
            ),
        ),
    )


if __name__ == "__main__":
    app.run()
