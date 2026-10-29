"""Vistas de la app notas: lista, alta y borrado contra SQLite."""

import interui as ui

from notas.models import Nota
from proyecto_tareas import layout


def _hay_tabla() -> bool:
    """¿Ya se aplicaron las migraciones? Evita un error en el primer arranque."""
    try:
        Nota.objects.exists()
    except ui.db.DatabaseError:
        return False
    return True


def _avisos() -> ui.Component | None:
    if _hay_tabla():
        return None
    return ui.Alert(
        "Falta la base de datos. Ejecuta `python iui.py migrate` y vuelve a abrir la ventana.",
        title="Sin base de datos",
        level=ui.tone.warning,
        margin=ui.margin.t_6,
    )


def inicio() -> ui.Component:
    filas = [
        [
            ui.Text(nota.titulo),
            ui.Badge("hecha" if nota.hecha else "pendiente"),
            ui.IconButton(
                ui.icons.trash,
                label="Borrar",
                variant=ui.variant.ghost,
                on_click=lambda pk=nota.pk: _borrar(pk),
            ),
        ]
        for nota in (Nota.objects.all() if _hay_tabla() else [])
    ]
    return layout.frame(
        ui.Heading("Notas", level=1),
        ui.Muted("App «notas»: los datos viven en SQLite, dentro de data/."),
        _avisos(),
        ui.Button(
            "Nueva nota",
            icon=ui.icons.plus,
            on_click=_nueva,
            margin=ui.margin.t_4,
        ),
        ui.Card(pad=ui.pad.all_2, margin=ui.margin.t_4)(
            ui.Table(
                headers=["Título", "Estado", ""],
                rows=filas,
                empty="Todavía no hay notas",
                hover=True,
            )
        ),
        title="Notas · proyecto_tareas",
        active="/notas",
    )


def _nueva() -> None:
    ui.dialog.input("Título de la nota", title="Nueva nota", on_accept=_crear)


def _crear(evento) -> None:
    titulo = str(getattr(evento, "value", "") or "").strip()
    if not titulo:
        ui.toast("Escribe un título", "warning", icon=ui.icons.alert)
        return
    Nota.objects.create(titulo=titulo)
    ui.toast(f"«{titulo}» añadida", "success", title="Guardado", icon=ui.icons.check)


def _borrar(pk: int) -> None:
    Nota.objects.filter(pk=pk).delete()
    ui.toast("Nota eliminada", "info", icon=ui.icons.trash)
