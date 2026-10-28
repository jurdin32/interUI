"""Ventanas de cualquier tamaño: armazón por partes y panel deslizante.

    python examples/12_responsive.py

Arrastra el borde de la ventana (o usa `resizable=True`) y verás:

* por debajo de 768 px el sidebar se esconde y aparece el botón ☰;
* el contenido principal nunca desborda en horizontal;
* la tabla se desplaza dentro de su tarjeta, no estira la página;
* los espaciados cambian con `pad`, `md_pad` y `lg_pad`.
"""

import interui as ui

app = ui.App("Responsive · interUI", width=1180, height=760)

FILAS = [
    [f"Cliente {i}", f"cliente{i}@ejemplo.com", "activo", "2026-01-01"]
    for i in range(1, 16)
]


def abrir_dialogo() -> None:
    ui.dialog.info(
        "El diálogo se limita a la altura de la ventana y su cuerpo hace scroll.",
        title="Cabe en cualquier ventana",
        icon=ui.icons.info,
    )


@app.page("/")
def index():
    # Armazón por partes: cada zona es un atributo y el contenido va con `add`.
    shell = ui.AppShell()
    shell.title_bar = ui.TitleBar("Responsive · interUI", icon=ui.icons.layers)
    shell.header = ui.MenuBar(
        {
            "Archivo": [
                ui.ContextItem("Salir", icon=ui.icons.power, on_click=app.exit),
            ],
            "Ver": [
                ui.ContextItem("Abrir diálogo", icon=ui.icons.info, on_click=abrir_dialogo),
            ],
        },
        brand="interUI",
    )
    shell.sidebar = ui.Sidebar(
        ui.SidebarItem("Panel", icon=ui.icons.grid, active=True),
        ui.SidebarItem("Clientes", icon=ui.icons.users),
        ui.SidebarItem("Ajustes", icon=ui.icons.settings, badge="3"),
        title="Navegación",
    )
    shell.status = ui.StatusBar(ui.text("Listo"), ui.text("SQLite"))

    shell.add = ui.Container(
        pad=ui.pad.p_4,
        md_pad=ui.pad.p_8,
        lg_pad=ui.pad.p_10,
    )(
        ui.Row(gap=ui.gap.all_3)(
            ui.Col(span=12, md=8)(
                ui.Heading("Clientes", level=1, font=ui.font.xxl.bold, md_font=ui.font.xxxl.bold),
                ui.Muted("Cambia el tamaño de la ventana: todo se ajusta solo."),
            ),
            ui.Col(span=12, md=4)(
                ui.Button("Abrir diálogo", icon=ui.icons.info, on_click=abrir_dialogo),
            ),
        ),
        ui.Card(pad=ui.pad.all_2, margin=ui.margin.t_4)(
            ui.Table(
                headers=["Nombre", "Email", "Estado", "Alta"],
                rows=FILAS,
                hover=True,
            )
        ),
        ui.Muted(
            "La tabla se desplaza dentro de la tarjeta; el documento nunca crece a lo ancho.",
            margin=ui.margin.t_3,
        ),
    )
    return shell


if __name__ == "__main__":
    app.run()
