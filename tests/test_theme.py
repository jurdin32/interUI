"""Los tokens de estilo (`colors.red_500`, `pad.py_6`) se compilan a clases de utilidad.

Comprueba dos cosas que se rompen en silencio si nadie las vigila:

* el token genera exactamente la clase (o el CSS en línea) esperado;
* esa clase existe de verdad en `interui/static/app.css`, porque se construye en
  tiempo de ejecución y el compilador solo la incluye por el safelist.
"""

from __future__ import annotations

import pathlib

import pytest

import interui as ui
from interui import border, colors, flex, font, gap, gradient, margin, pad, radius, shadow, width
from interui._palette import FAMILIES, PALETTE, SHADES
from interui.theme import Color, Css, CssColor, Token, resolve_style_props, utility

ROOT = pathlib.Path(__file__).resolve().parents[1]
CSS = (ROOT / "interui" / "static" / "app.css").read_text(encoding="utf-8")


def classes(component: ui.Component) -> str:
    return component.classes(ui.RenderContext(), "x")


def in_css(*names: str) -> None:
    for name in names:
        needle = "." + name.replace(":", r"\:").replace("/", r"\/").replace(".", r"\.")
        assert needle in CSS, f"{name} no está en app.css: recompila con `interui assets`"


# ---------------------------------------------------------------------------
# tokens
# ---------------------------------------------------------------------------
def test_color_tokens() -> None:
    assert colors.red_500 == "red-500"
    assert colors.red == "red-500"
    assert colors.slate_950 == "slate-950"
    assert colors.white == "white"
    assert colors.transparent == "transparent"
    assert isinstance(colors.red_500, Color)


def test_semantic_colors() -> None:
    assert colors.primary == "indigo-600"
    assert colors.danger == "rose-600"
    assert colors.surface == "white"


@pytest.mark.parametrize("family", FAMILIES)
def test_palette_has_css_value_for_every_shade(family: str) -> None:
    for shade in SHADES:
        token = getattr(colors, f"{family}_{shade}")
        assert token in PALETTE, f"falta el valor CSS de {family}-{shade}"


def test_unknown_color_fails_loudly() -> None:
    with pytest.raises(AttributeError):
        _ = colors.morado_500
    with pytest.raises(AttributeError):
        _ = colors.red_123


def test_spacing_tokens() -> None:
    assert pad.all_6 == "p-6"
    assert pad.p_6 == "p-6"
    assert pad.py_6 == "py-6"
    assert pad.px_4 == "px-4"
    assert pad.t_2 == "pt-2"
    assert margin.mt_2 == "mt-2"
    assert margin.x_auto == "mx-auto"
    assert margin.neg.mt_2 == "-mt-2"
    assert margin.neg.mx_4 == "-mx-4"
    assert gap.all_4 == "gap-4"
    assert gap.x_2 == "gap-x-2"


def test_spacing_accepts_exact_measures() -> None:
    assert pad.p(6) == "p-6"
    assert pad.py("13px") == "padding-block: 13px"
    assert pad.x("1.25rem") == "padding-inline: 1.25rem"
    assert isinstance(pad.py("13px"), Css)


def test_layout_tokens() -> None:
    assert radius.xl == "rounded-xl"
    assert radius.xxl == "rounded-2xl"
    assert radius._2xl == "rounded-2xl"
    assert radius.t_lg == "rounded-t-lg"
    assert shadow.md == "shadow-md"
    assert border.w_2 == "border-2"
    assert border.t_2 == "border-t-2"
    assert width.full == "w-full"
    assert width.n_64 == "w-64"
    assert width.half == "w-1/2"
    assert flex.center == "items-center justify-center"


def test_font_tokens_chain() -> None:
    assert font.lg == "text-lg"
    assert font.bold == "font-bold"
    assert font.lg.semibold == "text-lg font-semibold"
    assert font.center == "text-center"
    assert font.relaxed == "leading-relaxed"


def test_custom_colors() -> None:
    assert colors.hex("#22d3ee") == "#22d3ee"
    assert colors.hex("22d3ee") == "#22d3ee"
    assert colors.rgb(34, 211, 238) == "rgb(34 211 238)"
    assert colors.rgb(34, 211, 238, 0.5) == "rgb(34 211 238 / 0.5)"
    assert colors.hsl(190, 95, 54) == "hsl(190 95% 54%)"
    assert isinstance(colors.hex("#fff"), CssColor)
    with pytest.raises(ValueError):
        colors.hex("#zz")


def test_gradient_uses_real_css_values() -> None:
    grad = gradient.r(colors.indigo_500, colors.fuchsia_500)
    assert grad.css.startswith("linear-gradient(to right, oklch(")
    assert str(colors.hex("#000")) in gradient.br("#000", "#fff").css
    assert gradient.radial(colors.primary, colors.danger).css.startswith("radial-gradient(circle")


def test_utility_keeps_tokens_intact() -> None:
    assert utility("gap", 4) == "gap-4"
    assert utility("gap", gap.x_2) == "gap-x-2"
    assert utility("rounded", radius.xl) == "rounded-xl"
    assert utility("rounded", "2xl") == "rounded-2xl"


def test_namespaces_are_discoverable() -> None:
    assert "red_500" in dir(colors)
    assert "py_6" in dir(pad)
    assert "xl" in dir(radius)


def test_design_enums() -> None:
    from interui import size, tone, variant
    from interui.theme import Word

    assert variant.primary == "primary"
    assert variant.danger == "danger"
    assert tone.muted == "muted"
    assert size.lg == "lg"
    assert isinstance(variant.primary, Word)
    assert isinstance(variant.primary, str)
    with pytest.raises(AttributeError):
        _ = variant.no_existe
    with pytest.raises(AttributeError):
        _ = size.huge


def test_design_enums_work_in_controls() -> None:
    from interui import size, tone, variant

    html = ui.render(ui.Button("Guardar", variant=variant.danger, size=size.lg))
    assert "bg-rose-600" in html and "h-11" in html
    assert "text-slate-500" in ui.render(ui.Text("hola", tone=tone.muted))
    assert "bg-emerald-50" in ui.render(ui.Badge("ok", variant=variant.success))


# ---------------------------------------------------------------------------
# argumentos de estilo en los controles
# ---------------------------------------------------------------------------
def test_style_props_become_classes() -> None:
    html = ui.render(
        ui.Card(bg=colors.white, pad=pad.all_6, rounded=radius.xxl, shadow=shadow.md)
    )
    assert "bg-white" in html
    assert "p-6" in html
    assert "rounded-2xl" in html
    assert "shadow-md" in html
    assert "bg=" not in html and "pad=" not in html  # nunca llegan al HTML


def test_plain_values_work_too() -> None:
    component = ui.Card(pad=6, w=64, h="full", opacity=50, rounded="xl", shadow="md")
    rendered = classes(component)
    assert "p-6" in rendered
    assert "w-64" in rendered
    assert "h-full" in rendered
    assert "opacity-50" in rendered
    assert "rounded-xl" in rendered


def test_user_class_wins_over_tokens() -> None:
    assert classes(ui.Card(class_="p-2", pad=8)).endswith("p-2")
    assert "p-8" not in classes(ui.Card(class_="p-2", pad=8))


def test_variants() -> None:
    component = ui.Card(
        bg=colors.red_500,
        hover_bg=colors.red_600,
        dark_bg=colors.slate_900,
        md_pad=pad.p_8,
        md_hover_bg=colors.red_700,
    )
    rendered = classes(component)
    assert "bg-red-500" in rendered
    assert "hover:bg-red-600" in rendered
    assert "dark:bg-slate-900" in rendered
    assert "md:p-8" in rendered
    assert "md:hover:bg-red-700" in rendered


def test_hex_goes_to_inline_css() -> None:
    component = ui.Card(bg=colors.hex("#22d3ee"))
    assert "bg-[#22d3ee]" not in classes(component)
    assert component.style == {"background-color": "#22d3ee"}
    assert "style=\"background-color: #22d3ee\"" in ui.render(component)


def test_gradient_goes_to_inline_css() -> None:
    component = ui.Card(bg=gradient.r(colors.indigo_500, colors.fuchsia_500))
    assert "background-image" in ui.render(component)
    assert "linear-gradient" in ui.render(component)


def test_exact_measure_goes_to_inline_css() -> None:
    component = ui.Card(pad=pad.py("13px"))
    assert component.style == {"padding-block": "13px"}


def test_tokens_and_inline_style_coexist() -> None:
    component = ui.Card(bg=colors.hex("#fff"), style="outline: 1px solid red")
    assert "background-color" in str(component.style)
    assert "outline" in str(component.style)


def test_variants_reject_literal_values() -> None:
    with pytest.raises(TypeError):
        ui.Card(hover_bg=colors.hex("#fff"))


def test_gradient_only_for_background() -> None:
    with pytest.raises(TypeError):
        ui.Card(color=gradient.r(colors.red_500, colors.blue_500))


def test_clone_accepts_tokens() -> None:
    base = ui.Card(pad=4)
    assert "bg-red-500" in classes(base.clone(bg=colors.red_500))


def test_resolve_style_props_reports_both_outputs() -> None:
    props = {"bg": colors.red_500, "pad": pad.py("1rem"), "titulo": "x"}
    declared, inline = resolve_style_props(props)
    assert declared == ["bg-red-500"]
    assert inline == {"padding-block": "1rem"}
    assert props == {"titulo": "x"}


# ---------------------------------------------------------------------------
# el CSS compilado incluye lo que generan los tokens
# ---------------------------------------------------------------------------
def test_generated_classes_exist_in_the_stylesheet() -> None:
    in_css(
        "bg-red-500",
        "text-indigo-600",
        "border-slate-200",
        "ring-indigo-500",
        "hover:bg-red-600",
        "focus:ring-indigo-600",
        "active:bg-red-700",
        "dark:bg-slate-900",
        "md:p-8",
        "hover:p-4",
        "p-13",
        "-mt-2",
        "gap-x-2",
        "w-full",
        "h-64",
        "w-1/2",
        "rounded-2xl",
        "rounded-t-lg",
        "shadow-md",
        "border-2",
        "text-lg",
        "font-semibold",
        "leading-relaxed",
        "tracking-wider",
        "items-center",
        "opacity-75",
        "z-10",
    )


def test_tokens_never_leak_as_html_attributes() -> None:
    html = ui.render(ui.Card(bg=colors.red_500, pad=pad.p_4, font=font.lg.bold))
    for name in ("bg=", "pad=", "font="):
        assert name not in html


def test_out_of_range_steps_fall_back_to_calc() -> None:
    assert pad.py(999) == "padding-block: calc(var(--spacing) * 999)"
    assert margin.neg.mt(999) == "margin-top: calc(var(--spacing) * -999)"


def test_unknown_token_raises_instead_of_rendering_nothing() -> None:
    with pytest.raises(AttributeError):
        _ = pad.py_grande
    with pytest.raises(AttributeError):
        _ = gap.p_4
    with pytest.raises(AttributeError):
        _ = colors.morado


def test_token_type_is_a_string() -> None:
    assert isinstance(pad.py_6, Token)
    assert isinstance(pad.py_6, str)
    assert f"{pad.py_6}" == "py-6"
