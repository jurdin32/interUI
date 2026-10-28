"""Ejemplo mínimo: un contador con estado reactivo.

    python examples/01_hello.py
"""

from interui import App, Button, Card, Col, Container, Heading, Muted, Row, Screen, Text, size, variant, margin, pad, icons

app = App("Hola interui")


@app.page("/")
def index():
    count = app.state("count", 0)

    def increment() -> None:
        count.set(count.get() + 1)

    def reset() -> None:
        count.set(0)

    return Screen(
        Container(size="prose", pad=pad.py_16)(
            Heading("Hola, interui", level=1),
            Muted("Una interfaz nativa construida con HTML, Tailwind y Python."),
            Card(title="Contador", description="El estado vive en Python", margin=margin.mt_6)(
                Text(f"Valor actual: {count.get()}", size=size.lg, weight="semibold"),
                Row(
                    Col(span=6)(Button("Incrementar", on_click=increment, icon=icons.plus, full_width=True)),
                    Col(span=6)(
                        Button("Reiniciar", variant=variant.outline, on_click=reset, icon=icons.refresh, full_width=True)
                    ),
                ),
            ),
        )
    )


if __name__ == "__main__":
    app.run()
