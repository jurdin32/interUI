"""Estilos con notación de punto: nada de clases a mano.

    python examples/07_estilos.py

Cada argumento dice qué se cambia (`bg`, `pad`, `rounded`, `font`…) y cada token
dice cuánto (`colors.red_500`, `pad.py_6`). Los prefijos `hover_`, `dark_`, `md_`
añaden variantes y `=` acepta valores exactos (`colors.hex`, `gradient`,
`pad.py("18px")`).
"""

from interui import (
    App, Badge, Button, Card, Col, Container, Heading, Muted, Row, Screen, Section,
    Text, colors, font, gap, gradient, icons, margin, pad, radius, shadow, size, tone,
    variant, width,
)

app = App("Estilos")


@app.page("/")
def index():
    return Screen(
        Container(pad=pad.py_10)(
            Heading("Estilos con notación de punto", level=1),
            Muted(
                "bg · color · pad · margin · gap · rounded · shadow · w · h · font · "
                "opacity, con tokens y valores exactos."
            ),
            Section(title="Colores")(
                Row(
                    Col(span=12, md=4)(
                        Card(
                            bg=colors.indigo_600,
                            rounded=radius.xxl,
                            shadow=shadow.lg,
                            pad=pad.all_5,
                        )(
                            Text("Paleta", font=font.sm.semibold, color=colors.white),
                            Text("colors.indigo_600", font=font.xs, color=colors.indigo_100),
                        )
                    ),
                    Col(span=12, md=4)(
                        Card(bg=colors.hex("#0f172a"), rounded=radius.xxl, pad=pad.all_5)(
                            Text("Hexadecimal", font=font.sm.semibold, color=colors.white),
                            Text('colors.hex("#0f172a")', font=font.xs, color=colors.slate_400),
                        )
                    ),
                    Col(span=12, md=4)(
                        Card(
                            bg=gradient.br(colors.fuchsia_500, colors.indigo_500),
                            rounded=radius.xxl,
                            pad=pad.all_5,
                        )(
                            Text("Degradado", font=font.sm.semibold, color=colors.white),
                            Text(
                                "gradient.br(fuchsia_500, indigo_500)",
                                font=font.xs,
                                color=colors.white,
                            ),
                        )
                    ),
                )
            ),
            Section(title="Variantes")(
                Row(
                    Col(span=12, md=6)(
                        Card(
                            bg=colors.white,
                            border=colors.slate_200,
                            rounded=radius.xl,
                            shadow=shadow.sm,
                            pad=pad.all_6,
                            hover_bg=colors.slate_50,
                            dark_bg=colors.slate_900,
                            dark_border=colors.slate_800,
                        )(
                            Text("Pasa el ratón", font=font.base.medium, tone=tone.default),
                            Muted("hover_bg=colors.slate_50 · dark_bg=colors.slate_900"),
                        )
                    ),
                    Col(span=12, md=6)(
                        Row(gap=gap.all_3)(
                            Button("Guardar", variant=variant.primary, icon=icons.check),
                            Button("Borrar", variant=variant.danger, icon=icons.trash),
                            Button(
                                "Grande",
                                variant=variant.soft,
                                size=size.lg,
                                icon=icons.car(),
                            ),
                        ),
                        Text(
                            "variant.danger · size.lg · icon=icons.car()",
                            font=font.xs,
                            color=colors.slate_500,
                            margin=margin.t_3,
                        ),
                    ),
                )
            ),
            Section(title="Medidas exactas")(
                Card(
                    w=width.full,
                    pad=pad.py("18px"),
                    margin=margin.t_2,
                    border=colors.slate_200,
                    rounded=radius.lg,
                )(
                    Text("pad=pad.py('18px') se emite como CSS en línea."),
                    Text(
                        "Sin recompilar CSS y sin escribir una sola clase.",
                        font=font.sm,
                        color=colors.slate_500,
                        margin=margin.t_2,
                    ),
                    Badge("22 tokens", bg=colors.indigo_50, color=colors.indigo_700),
                )
            ),
        )
    )


if __name__ == "__main__":
    app.run()
