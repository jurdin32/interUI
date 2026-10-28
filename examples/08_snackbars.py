"""Snackbars: texto, icono **o** imagen, acción y duración.

    python examples/08_snackbars.py

* ``ui.Snackbar`` es el control: vive en el árbol, admite handlers de Python y
  cualquier icono, imagen o acción.
* ``ui.toast`` / ``app.notify`` son el aviso transitorio: se pinta encima de la
  ventana y desaparece solo.
"""

from interui import (
    App, Badge, Button, Card, Col, Container, Heading, Muted, Row, Screen, Section,
    Snackbar, Stack, Text, colors, font, gap, icons, margin, pad, radius, variant,
)

app = App("Snackbars")

# Imagen sin red: un SVG en línea (también valdría https://…)
AVATAR = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'>"
    "<rect width='40' height='40' rx='8' fill='%230ea5e9'/>"
    "<circle cx='20' cy='15' r='7' fill='white'/>"
    "<path d='M6 40c0-8 6-13 14-13s14 5 14 13' fill='white'/></svg>"
)


def deshacer() -> None:
    app.notify("Nada que deshacer, era una demo", "info", icon=icons.info)


def transitorio() -> None:
    app.notify(
        "Proyecto archivado",
        "success",
        title="Hecho",
        icon=icons.check,
        duration=4000,
        action={"label": "Deshacer", "js": "console.log('deshacer')"},
    )


def con_imagen() -> None:
    app.notify("Ana te ha mencionado", "info", title="Nueva mención", image=AVATAR, duration=0)


def error() -> None:
    app.notify("No se pudo guardar el archivo", "error", icon=icons.alert, duration=6000)


@app.page("/")
def index():
    return Screen(
        Container(pad=pad.py_10)(
            Heading("Snackbars", level=1),
            Muted("Tres formas: control en el árbol, aviso transitorio y variantes."),
            Section(title="Control Snackbar")(
                Stack(gap=gap.all_4)(
                    Snackbar(
                        "Proyecto archivado",
                        title="Hecho",
                        icon=icons.check,
                        variant=variant.success,
                        action=("Deshacer", deshacer),
                        position="static",
                    ),
                    Snackbar(
                        "Ana te ha mencionado",
                        title="Nueva mención",
                        image=AVATAR,
                        variant="neutral",
                        action=("Ver", deshacer),
                        position="static",
                    ),
                    Snackbar(
                        "Conexión perdida, reintentando…",
                        icon=icons.alert,
                        variant=variant.danger,
                        dismissible=True,
                        position="static",
                    ),
                    Snackbar(
                        "Guardado a las 10:32",
                        icon=icons.check_circle,
                        variant=variant.info,
                        duration=8000,
                        position="static",
                    ),
                )
            ),
            Section(title="Avisos transitorios (esquina inferior derecha)")(
                Row(gap=gap.all_3)(
                    Col(span=12, md=3)(
                        Button("Éxito", icon=icons.check, variant=variant.success,
                               on_click=transitorio)
                    ),
                    Col(span=12, md=3)(Button("Con imagen", icon=icons.user, on_click=con_imagen)),
                    Col(span=12, md=3)(
                        Button("Error", icon=icons.alert, variant=variant.danger, on_click=error)
                    ),
                    Col(span=12, md=3)(Button("toast()", icon=icons.bell, on_click=deshacer)),
                )
            ),
            Section(title="Posiciones")(
                Card(pad=pad.all_5)(
                    Text("position=…", font=font.sm.semibold),
                    Row(gap=gap.all_2)(
                        *[
                            Badge(name, variant="neutral", margin=margin.t_2)
                            for name in ("bottom_right", "bottom_left", "bottom_center",
                                         "top_right", "top_left", "top_center")
                        ]
                    ),
                    Text(
                        "El control usa `fixed` salvo position='static'.",
                        font=font.xs,
                        color=colors.slate_500,
                        margin=margin.t_3,
                    ),
                )
            ),
        )
    )


if __name__ == "__main__":
    app.run()
