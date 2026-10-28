"""Multiventana: cada ventana con su ruta, su canal y su cierre.

    python examples/10_multiventana.py

* ``app.open_window(route, title=…)`` abre otra ventana nativa.
* ``ventana.navigate("/…")`` mueve **solo** esa ventana.
* ``ventana.close()`` / ``app.close()`` cierran esa ventana sin apagar la app;
  ``app.exit()`` cierra todas.

Requiere `window="desktop"` (pywebview). En el navegador el botón avisa en vez de
fallar, así que el ejemplo se puede abrir igualmente.
"""

from interui import (
    App, Badge, Button, Card, Container, DesktopError, Heading, Muted, Row, Screen,
    Section, Stack, Text, colors, font, gap, icons, margin, pad, radius, variant,
    size,
)

app = App("Multiventana", width=980, height=720)


def abrir(route: str = "/ajustes", title: str = "Ajustes") -> None:
    try:
        ventana = app.open_window(route, title=title, width=720, height=520)
    except DesktopError as exc:
        app.notify(str(exc), "warning", title="Sin ventana nativa", icon=icons.info, duration=6000)
        return
    app.notify(
        f"Ventana «{ventana.ident}» abierta en {route}",
        "success",
        title="Multiventana",
        icon=icons.layout,
    )


def cerrar_actual() -> None:
    ventana = app.current_window
    if ventana is not None and ventana.ident != "main":
        ventana.close()
    else:
        app.notify("Esta es la ventana principal", "info", icon=icons.info)


def fila_ventana(ventana):
    return Row(gap=gap.all_2)(
        Badge(ventana.ident, variant=variant.primary),
        Text(ventana.title, font=font.sm),
        Text(ventana.route, font=font.xs, color=colors.slate_500),
        Button("Ir a /ajustes", size=size.sm, variant=variant.ghost,
               on_click=lambda: ventana.navigate("/ajustes")),
        Button("Cerrar", size=size.sm, variant=variant.soft, on_click=ventana.close),
    )


@app.page("/")
def index():
    return Screen(
        Container(pad=pad.py_10)(
            Heading("Multiventana", level=1),
            Muted("La principal siempre existe; las demás se abren desde ella."),
            Section(title="Abrir ventanas")(
                Row(gap=gap.all_3)(
                    Button("Ajustes", icon=icons.settings, on_click=lambda: abrir("/ajustes")),
                    Button(
                        "Informe",
                        icon=icons.chart,
                        variant=variant.secondary,
                        on_click=lambda: abrir("/informe", "Informe"),
                    ),
                    Button(
                        "Cerrar esta ventana",
                        icon=icons.close,
                        variant=variant.outline,
                        on_click=cerrar_actual,
                    ),
                )
            ),
            Section(title="Ventanas abiertas")(
                Card(pad=pad.all_5)(
                    Text(f"Total: {len(app.windows)}", font=font.sm.semibold),
                    Stack(gap=gap.all_2)(*[fila_ventana(item) for item in app.windows]),
                    Text(
                        "app.windows · app.main_window · app.current_window",
                        font=font.xs,
                        color=colors.slate_500,
                        margin=margin.t_3,
                    ),
                )
            ),
        )
    )


@app.page("/ajustes")
def ajustes():
    return Screen(
        Container(pad=pad.py_8)(
            Heading("Ajustes", level=2),
            Muted("Esta es otra ventana: su propia ruta y su propia conexión."),
            Row(gap=gap.all_3)(
                Button("Volver a la principal", icon=icons.home,
                       on_click=lambda: app.main_window.navigate("/")),
                Button("Cerrar esta", icon=icons.close, variant=variant.outline,
                       on_click=cerrar_actual),
                Button("Salir de todo", icon=icons.power, variant=variant.danger,
                       on_click=app.exit),
            ),
        )
    )


@app.page("/informe")
def informe():
    return Screen(
        Container(pad=pad.py_8)(
            Heading("Informe", level=2),
            Card(pad=pad.all_6, rounded=radius.xl)(
                Text("Ventana independiente", font=font.base.semibold),
                Muted("Cerrar esta ventana no afecta a la principal."),
                Button("Cerrar esta", icon=icons.close, variant=variant.outline,
                       margin=margin.t_4, on_click=cerrar_actual),
            ),
        )
    )


if __name__ == "__main__":
    app.run()
