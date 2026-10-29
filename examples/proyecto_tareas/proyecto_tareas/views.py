"""Vistas del proyecto: la portada."""

import interui as ui

from notas.models import Nota
from proyecto_tareas import layout


def _cuentas() -> tuple[int, int]:
    """Total y hechas; sin base de datos todavía, la portada abre igual."""
    try:
        return Nota.objects.count(), Nota.objects.filter(hecha=True).count()
    except ui.db.DatabaseError:
        return 0, 0


def inicio() -> ui.Component:
    total, hechas = _cuentas()
    return layout.frame(
        ui.Heading("Hola desde proyecto_tareas", level=1),
        ui.Muted("Aplicación de escritorio: se abre en su propia ventana, sin navegador."),
        ui.Row(gap=ui.gap.all_3, margin=ui.margin.t_6)(
            ui.Col(span=12, md=6)(
                ui.Stat("Notas", total, icon=ui.icons.check),
            ),
            ui.Col(span=12, md=6)(
                ui.Stat("Hechas", hechas, icon=ui.icons.check),
            ),
        ),
        ui.Alert(
            "La app «notas» está en `apps` de interui.json: sus rutas se registran solas.",
            level=ui.tone.info,
            margin=ui.margin.t_6,
        ),
        active="/",
    )
