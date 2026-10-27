"""Aplicación completa de referencia: agenda de contactos.

    python examples/05_crud.py

Incluye, en un solo archivo:

* ventana nativa con barra de título y de estado,
* estado reactivo y persistencia en JSON dentro de ``app.data_dir``,
* búsqueda en vivo, tabla con acciones por fila,
* alta/edición en un modal con validación hecha en Python,
* confirmación de borrado, notificaciones y exportación con diálogo nativo,
* tema claro/oscuro conmutables.

Sirve como plantilla: copia este archivo, renómbralo y adapta el modelo.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from interui import (
    Alert, App, Badge, Button, Card, Col, Container, DataTable, Divider, EmptyState,
    Hint, IconButton, Input, Modal, Row, Screen, Stack, Stat, StatGrid, StatusBar,
    Switch, Text, TitleBar, Toolbar, ValidationSummary,
)

app = App("Agenda interUI", width=1080, height=720)

# ---------------------------------------------------------------------------
# Modelo y persistencia
# ---------------------------------------------------------------------------
STORE = Path(app.data_dir) / "contactos.json"


def load_contacts() -> list[dict[str, Any]]:
    try:
        data = json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return data if isinstance(data, list) else []


def save_contacts() -> None:
    STORE.write_text(
        json.dumps(app.get_state("contacts", []), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


contacts = app.state("contacts", load_contacts())
query = app.state("query", "")
editing = app.state("editing", None)          # id en edición o None
form_name = app.state("form_name", "")
form_email = app.state("form_email", "")
form_company = app.state("form_company", "")
form_active = app.state("form_active", True)
errors = app.state("errors", [])
to_delete = app.state("to_delete", None)


def visible_contacts() -> list[dict[str, Any]]:
    term = query.get().strip().lower()
    items = list(contacts.get([]))
    if not term:
        return items
    return [
        item
        for item in items
        if term in item["name"].lower()
        or term in item["email"].lower()
        or term in item.get("company", "").lower()
    ]


# ---------------------------------------------------------------------------
# Acciones
# ---------------------------------------------------------------------------
def open_new() -> None:
    editing.set(None)
    form_name.set("")
    form_email.set("")
    form_company.set("")
    form_active.set(True)
    errors.set([])
    app.eval_js("interui.openDialog('form-modal')")


def open_edit(event: Any) -> None:
    contact_id = int(event.value)
    item = next((c for c in contacts.get([]) if c["id"] == contact_id), None)
    if item is None:
        return
    editing.set(contact_id)
    form_name.set(item["name"])
    form_email.set(item["email"])
    form_company.set(item.get("company", ""))
    form_active.set(bool(item.get("active", True)))
    errors.set([])
    app.eval_js("interui.openDialog('form-modal')")


def close_form() -> None:
    app.eval_js("interui.closeDialog('form-modal')")


def save_contact() -> None:
    problems = []
    if len(form_name.get().strip()) < 2:
        problems.append("El nombre debe tener al menos 2 caracteres.")
    if "@" not in form_email.get() or "." not in form_email.get().split("@")[-1]:
        problems.append("El correo no parece válido.")
    duplicated = any(
        c["email"].lower() == form_email.get().strip().lower() and c["id"] != editing.get()
        for c in contacts.get([])
    )
    if duplicated:
        problems.append("Ya existe un contacto con ese correo.")

    errors.set(problems)
    if problems:
        return

    items = list(contacts.get([]))
    if editing.get() is None:
        new_id = max((c["id"] for c in items), default=0) + 1
        items.append(
            {
                "id": new_id,
                "name": form_name.get().strip(),
                "email": form_email.get().strip(),
                "company": form_company.get().strip(),
                "active": bool(form_active.get()),
            }
        )
        app.notify(f"{form_name.get()} añadido", "success")
    else:
        for item in items:
            if item["id"] == editing.get():
                item.update(
                    name=form_name.get().strip(),
                    email=form_email.get().strip(),
                    company=form_company.get().strip(),
                    active=bool(form_active.get()),
                )
        app.notify("Contacto actualizado", "success")

    contacts.set(items)
    save_contacts()
    close_form()


def ask_delete(event: Any) -> None:
    to_delete.set(int(event.value))
    app.eval_js("interui.openDialog('delete-modal')")


def confirm_delete() -> None:
    target = to_delete.get()
    contacts.set([c for c in contacts.get([]) if c["id"] != target])
    save_contacts()
    to_delete.set(None)
    app.eval_js("interui.closeDialog('delete-modal')")
    app.notify("Contacto eliminado", "warning")


def export_csv() -> None:
    rows = ["nombre,correo,empresa,activo"]
    for item in contacts.get([]):
        rows.append(
            f"{item['name']},{item['email']},{item.get('company', '')},{item.get('active', True)}"
        )
    path = app.native.save_text("contactos.csv", "\n".join(rows))
    if path:
        app.notify("Exportado", path)


def toggle_theme() -> None:
    app.theme = "dark" if app.theme == "light" else "light"


# ---------------------------------------------------------------------------
# Vista
# ---------------------------------------------------------------------------
@app.page("/")
def index():
    items = visible_contacts()
    total = len(contacts.get([]))
    active = sum(1 for c in contacts.get([]) if c.get("active"))

    table = (
        DataTable(
            columns=[
                {"key": "name", "label": "Nombre", "sortable": True},
                {"key": "email", "label": "Correo", "sortable": True},
                {"key": "company", "label": "Empresa"},
                {
                    "key": "active",
                    "label": "Estado",
                    "render": lambda row: Badge(
                        "activo" if row.get("active") else "inactivo",
                        variant="success" if row.get("active") else "neutral",
                        size="sm",
                    ),
                },
                {
                    "key": "actions",
                    "label": "",
                    "align": "right",
                    "render": lambda row: Stack(
                        IconButton("edit", label="Editar", size="sm",
                                   data={"iui-emit": "edit", "iui-value": row["id"], "iui-cast": "int"}),
                        IconButton("trash", label="Eliminar", size="sm",
                                   variant="ghost",
                                   data={"iui-emit": "delete", "iui-value": row["id"], "iui-cast": "int"}),
                        direction="row",
                        gap=1,
                        justify="end",
                    ),
                },
            ],
            rows=[{**item, "id": item["id"]} for item in items],
            total=len(items),
            page=1,
            page_size=max(1, len(items)),
            selectable=False,
        )
        if items
        else EmptyState(
            Button("Nuevo contacto", icon="plus", on_click=open_new),
            title="Sin contactos",
            description="Añade el primero con el botón «Nuevo contacto».",
            icon="users",
        )
    )

    return Screen(
        TitleBar("Agenda interUI", icon="users"),
        Container(size="xl", class_="flex-1 overflow-y-auto py-6")(
            Stack(
                StatGrid(
                    Stat("Contactos", str(total), icon="users"),
                    Stat("Activos", str(active), icon="check-circle"),
                    Stat("Empresas", str(len({c.get('company') for c in contacts.get([]) if c.get('company')})),
                         icon="box"),
                    columns=3,
                ),
                Toolbar(
                    Input(query.get(), placeholder="Buscar por nombre, correo o empresa…",
                          icon="search", live=True, on_input=lambda e: query.set(e.text),
                          class_="max-w-md flex-1"),
                    Button("Nuevo contacto", icon="plus", on_click=open_new),
                    Button("Exportar CSV", icon="download", variant="outline", on_click=export_csv),
                    Button("Tema", icon="moon", variant="ghost", on_click=toggle_theme),
                ),
                Text(
                    f"{len(items)} de {total} contactos"
                    + (f" · filtro «{query.get()}»" if query.get() else ""),
                    size="sm",
                    tone="muted",
                ),
                Card(class_="p-0")(table),
                Divider(),
                Hint(
                    "Los datos se guardan en "
                    f"{STORE}. La tabla, la búsqueda y el formulario son controles de interUI."
                ),
                gap=4,
            )
        ),
        StatusBar(
            Badge("local", variant="success", size="sm"),
            Text(f"{total} contactos · guardado automático", size="sm"),
        ),
        Modal(
            Stack(
                ValidationSummary(errors.get()) if errors.get() else None,
                Input(form_name.get(), label="Nombre", required=True, icon="user",
                      on_input=lambda e: form_name.set(e.text)),
                Input(form_email.get(), label="Correo", required=True, icon="mail",
                      on_input=lambda e: form_email.set(e.text)),
                Input(form_company.get(), label="Empresa", icon="box",
                      on_input=lambda e: form_company.set(e.text)),
                Switch("Activo", checked=form_active.get(),
                       on_change=lambda e: form_active.set(bool(e.checked))),
                Stack(
                    Button("Cancelar", variant="outline", on_click=close_form),
                    Button("Guardar", icon="check", on_click=save_contact),
                    direction="row",
                    gap=2,
                    justify="end",
                ),
                gap=4,
            ),
            dialog_id="form-modal",
            title="Contacto",
            description="Los datos se validan en Python antes de guardarse.",
        ),
        Modal(
            Stack(
                Text("Esta acción no se puede deshacer."),
                Stack(
                    Button("Cancelar", variant="outline",
                           on_click=lambda: app.eval_js("interui.closeDialog('delete-modal')")),
                    Button("Eliminar", variant="danger", icon="trash", on_click=confirm_delete),
                    direction="row",
                    gap=2,
                    justify="end",
                ),
                gap=4,
            ),
            dialog_id="delete-modal",
            title="¿Eliminar contacto?",
            size="sm",
        ),
        class_="flex flex-col h-screen",
    )


@app.on_close
def _persist() -> None:
    save_contacts()


if __name__ == "__main__":
    app.run()
