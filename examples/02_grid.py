"""La rejilla de 12 columnas: cambia el tamaño de la ventana y observa.

    python examples/02_grid.py
"""

from interui import (
    App, Badge, Card, Col, Container, Heading, Muted, Row, Screen, Section, Text,
)

app = App("Rejilla")


@app.page("/")
def index():
    def box(span: int, **extra: object) -> Card:
        return Card(
            title=f"span={span}",
            description="móvil · tablet · escritorio",
            class_="h-full",
        )(Badge(f"{span}/12", variant="primary"), Text(str(extra), size="sm", tone="muted"))

    return Screen(
        Container(class_="py-10")(
            Heading("Sistema de rejilla", level=1),
            Muted("12 columnas responsive con breakpoints sm · md · lg · xl · 2xl."),
            Section(title="Columnas iguales")(
                Row(
                    Col(span=12, md=6, lg=3)(box(3)),
                    Col(span=12, md=6, lg=3)(box(3)),
                    Col(span=12, md=6, lg=3)(box(3)),
                    Col(span=12, md=6, lg=3)(box(3)),
                )
            ),
            Section(title="Mezcla de anchos")(
                Row(
                    Col(span=12, lg=8)(box(8, md=12)),
                    Col(span=12, lg=4)(box(4, md=12)),
                ),
                Row(
                    Col(span=12, md=4)(box(4)),
                    Col(span=12, md=8)(box(8)),
                ),
            ),
            Section(title="Separación configurable")(
                Row(
                    Col(span=12, sm=6)(box(6)),
                    Col(span=12, sm=6)(box(6)),
                    gap=8,
                )
            ),
        )
    )


if __name__ == "__main__":
    app.run()
