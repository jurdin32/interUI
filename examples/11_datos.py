"""Datos: configuración, modelos y migraciones con una pantalla CRUD real.

    python examples/11_datos.py

En un proyecto normal esto empieza con el asistente:

    interui init tienda --db sqlite --migrate
    interui db makemigrations
    interui db migrate

Aquí se hace en el propio archivo (config en memoria + tabla si no existe) para
que el ejemplo funcione sin dependencias ni pasos previos. Si hay un
``interui.json`` junto a este archivo, se usa ese.
"""

from pathlib import Path

import interui as ui
from interui import (
    Alert, App, Badge, Button, Card, Config, Container, Heading, IconButton, Input,
    Muted, Row, Screen, Section, Table, Text, colors, db, dialog, font, gap, icons,
    margin, pad, radius, variant,
)

app = App("Clientes · datos", width=1080, height=740)

# ---------------------------------------------------------------------------
# 1. Configuración: interui.json si existe; si no, SQLite dentro de data_dir
# ---------------------------------------------------------------------------
CONFIG_FILE = Path(__file__).with_name("interui.json")
if CONFIG_FILE.is_file():
    settings = Config.load(CONFIG_FILE)
else:
    settings = Config(
        {
            "app": {"name": "Clientes"},
            "databases": {
                "default": {
                    "engine": "sqlite",
                    "name": str(Path(app.data_dir) / "clientes.db"),
                }
            },
        }
    )
db.configure(settings)

# ---------------------------------------------------------------------------
# 2. Modelo
# ---------------------------------------------------------------------------
class Cliente(ui.Model):
    nombre = ui.Str(max_length=80, unique=True)
    email = ui.Str(max_length=120, null=True)
    activo = ui.Bool(default=True)
    alta = ui.DateTime(auto_now_add=True)

    class Meta:
        table = "clientes"
        order = ["nombre"]


# ---------------------------------------------------------------------------
# 3. Esquema (equivalente a `interui db migrate`)
# ---------------------------------------------------------------------------
db.backend("default").create_table("clientes", Cliente.columns())

if Cliente.objects.count() == 0:
    for nombre, email in (
        ("Ana Torres", "ana@ejemplo.com"),
        ("Luis Pérez", "luis@ejemplo.com"),
        ("Eva Ruiz", None),
    ):
        Cliente.objects.create(nombre=nombre, email=email)

# ---------------------------------------------------------------------------
# 4. Acciones
# ---------------------------------------------------------------------------
query = app.state("query", "")


def nuevo() -> None:
    dialog.input(
        "Nombre del cliente",
        title="Nuevo cliente",
        placeholder="Ana Torres",
        on_accept=crear,
    )


def crear(evento) -> None:
    nombre = str(getattr(evento, "value", "") or "").strip()
    if not nombre:
        app.notify("El nombre es obligatorio", "warning", icon=icons.alert)
        return
    if Cliente.objects.filter(nombre=nombre).exists():
        app.notify("Ese cliente ya existe", "error", icon=icons.alert)
        return
    Cliente.objects.create(nombre=nombre)
    app.notify(f"«{nombre}» añadido", "success", title="Guardado", icon=icons.check)


def borrar(pk: int) -> None:
    Cliente.objects.filter(pk=pk).delete()
    app.notify("Cliente eliminado", "info", icon=icons.trash)


# ---------------------------------------------------------------------------
# 5. Pantalla
# ---------------------------------------------------------------------------
@app.page("/")
def index():
    clientes = Cliente.objects.filter(nombre__contains=query.get()).limit(50).all()
    filas = [
        [
            Text(cliente.nombre, font=font.sm.medium),
            Text(cliente.email or "—", font=font.sm, color=colors.slate_500),
            Badge("activo" if cliente.activo else "inactivo",
                  variant="success" if cliente.activo else "neutral"),
            Text(cliente.alta.strftime("%d/%m/%Y") if cliente.alta else "—",
                 font=font.xs, color=colors.slate_500),
            IconButton(
                "trash",
                label="Borrar",
                size="sm",
                variant="ghost",
                on_click=lambda pk=cliente.pk: borrar(pk),
            ),
        ]
        for cliente in clientes
    ]

    return Screen(
        Container(pad=pad.py_10)(
            Heading("Clientes", level=1),
            Muted(f"SQLite · {settings.database().url}"),
            Section(title="Buscar y añadir")(
                Row(gap=gap.all_3)(
                    Input(
                        placeholder="Buscar por nombre…",
                        icon=icons.search,
                        value=query,
                        on_input=query,
                    ),
                    Button("Nuevo cliente", icon=icons.plus, on_click=nuevo),
                ),
                Text(
                    f"{Cliente.objects.count()} clientes en la base de datos",
                    font=font.xs,
                    color=colors.slate_500,
                    margin=margin.t_2,
                ),
            ),
            Section(title="Tabla")(
                Card(pad=pad.all_2, rounded=radius.xl)(
                    Table(
                        headers=["Nombre", "Email", "Estado", "Alta", ""],
                        rows=filas,
                        empty="No hay clientes con ese filtro",
                        hover=True,
                    )
                )
            ),
            Section(title="Cómo se guarda")(
                Alert(
                    "Modelo → migración → tabla. `interui db makemigrations` compara "
                    "models.py con la última migración y `interui db migrate` aplica el SQL.",
                    variant="info",
                ),
            ),
        )
    )


if __name__ == "__main__":
    app.run()
