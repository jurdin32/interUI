"""Vistas de local: cada función devuelve la página que se pinta en la ventana."""

import interui as ui


def inicio() -> ui.Component:
    return ui.Screen(
        ui.Container(pad=ui.pad.py_10)(
            ui.Heading("local", level=1),
            ui.Muted("Página de la app «local», servida dentro de la ventana nativa."),
            ui.Alert(
                "Declara tus modelos en models.py y ejecuta `python iui.py makemigrations`.",
                level=ui.tone.info,
                margin=ui.margin.t_6,
            ),
        )
    )
