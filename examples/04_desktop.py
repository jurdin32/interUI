"""Aplicación de escritorio con integración nativa del sistema operativo.

    python examples/04_desktop.py

Muestra:
  * ventana nativa (WebKit / WebView2 / WebKitGTK), sin navegador,
  * barra de título propia cuando la ventana no tiene marco,
  * diálogos nativos de abrir/guardar archivo y carpeta,
  * notificaciones, portapapeles y enlaces externos,
  * confirmación al cerrar la ventana.
"""

from __future__ import annotations

from interui import (
    Alert, App, Badge, Button, Card, Col, Container, Divider, Heading, Hint, Input,
    Muted, Row, Screen, Stack, StatusBar, Text, TitleBar,
)

app = App("interui · escritorio", width=940, height=680)


@app.page("/")
def index():
    name = app.state("name", "")
    status = app.state("status", "Listo")
    log = app.state("log", [])

    def add(message: str) -> None:
        log.set(([message] + list(log.get([])))[:8])

    def open_document() -> None:
        result = app.native.read_text(file_types=("Archivos de texto (*.txt;*.md)", "Todos (*.*)"))
        if result is None:
            status.set("Apertura cancelada")
            return
        path, content = result
        name.set(path)
        status.set(f"Abierto {path} ({len(content)} caracteres)")
        add(f"abierto: {path}")

    def save_document() -> None:
        path = app.native.save_text("nota.txt", f"Hola {name.get() or 'mundo'}\n")
        if path:
            status.set(f"Guardado en {path}")
            add(f"guardado: {path}")
            app.native.notify("Documento guardado", path)

    def pick_folder() -> None:
        folder = app.native.pick_folder()
        if folder:
            status.set(f"Carpeta: {folder}")
            add(f"carpeta: {folder}")

    def clipboard() -> None:
        app.native.clipboard_write(name.get() or "interui")
        status.set("Copiado al portapapeles")
        add("portapapeles actualizado")

    def toggle_top() -> None:
        app.native.set_always_on_top(True)
        add("ventana siempre visible")

    return Screen(
        TitleBar("interui · escritorio", icon="layers"),
        Container(size="lg", class_="flex-1 overflow-y-auto py-6")(
            Stack(
                Heading("Ventana de escritorio nativa", level=1),
                Muted(
                    "Esta ventana la pinta el sistema (WebKit/WebView2). El HTML y Tailwind "
                    "se generan en Python y se sirven desde un proceso local que muere al cerrar."
                ),
                Alert(
                    "El puente nativo ya está activo: prueba los botones para ver diálogos reales.",
                    level="info",
                    title="Sin navegador",
                ) if app.native.active else Alert(
                    "Estás viendo la app en el navegador: los diálogos nativos no están disponibles.",
                    level="warning",
                    title="Modo navegador",
                ),
                Divider("archivos"),
                Row(
                    Col(span=12, md=6)(
                        Card(title="Documento")(
                            Input(name.get(), label="Nombre o ruta", placeholder="sin documento",
                                  on_input=lambda e: name.set(e.text)),
                            Hint("Se rellena al abrir un archivo con el diálogo nativo."),
                        )
                    ),
                    Col(span=12, md=6)(
                        Card(title="Diálogos del sistema")(
                            Stack(
                                Button("Abrir…", icon="folder", on_click=open_document, full_width=True),
                                Button("Guardar…", icon="download", variant="outline",
                                       on_click=save_document, full_width=True),
                                Button("Elegir carpeta…", icon="folder", variant="ghost",
                                       on_click=pick_folder, full_width=True),
                                gap=2,
                            )
                        )
                    ),
                ),
                Divider("sistema"),
                Stack(
                    Button("Copiar al portapapeles", icon="copy", variant="soft", on_click=clipboard),
                    Button("Siempre visible", icon="pin", variant="outline", on_click=toggle_top),
                    Button(
                        "Documentación",
                        icon="external",
                        variant="ghost",
                        on_click=lambda: app.native.open_external("https://tailwindcss.com/docs"),
                    ),
                    Button("Cerrar ventana", icon="power", variant="danger",
                           on_click=app.native.close),
                    direction="row",
                    wrap=True,
                    gap=2,
                ),
                Divider("registro"),
                Card(title="Últimas acciones")(
                    *[Text(f"• {entry}", size="sm", tone="muted") for entry in log.get([])]
                    or [Muted("Todavía no hay acciones.")],
                ),
                gap=5,
            )
        ),
        StatusBar(
            Badge("escritorio" if app.native.active else "navegador",
                  variant="success" if app.native.active else "warning", size="sm"),
            Text(status.get(), size="sm"),
            Stack(
                Button("minimizar", variant="ghost", size="xs", on_click=app.native.minimize),
                Button("maximizar", variant="ghost", size="xs", on_click=app.native.toggle_maximize),
                direction="row",
                gap=1,
                class_="ml-auto",
            ),
        ),
        class_="flex flex-col h-screen",
    )


@app.on_close
def _closing() -> None:
    print("[ejemplo] guardando preferencias antes de cerrar…")


if __name__ == "__main__":
    app.run()
