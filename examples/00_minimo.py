"""El ejemplo mínimo: una ventana, un texto y un botón.

    python examples/00_minimo.py

Ocho líneas, API compacta: sin clases propias, sin decoradores y sin lambdas.
"""

from interui import button, state, text, window, icons

count = state(0)

app = window(
    "interUI · mínimo",
    text("Hola, escritorio"),
    text("Pulsaciones: ", count),
    button("Pulsar", icon=icons.plus, on_click=count.inc),
)

if __name__ == "__main__":
    app.run()
