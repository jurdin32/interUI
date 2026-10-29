"""Todos los controles se pueden personalizar (colores, fondos, tipografía, iconos).

Recorre el catálogo completo de controles y comprueba que las utilidades de
estilo (`bg`, `pad`, `font`, `border`, `rounded`, `shadow`, `ring`, `class_`,
`style`, `aria`, `data`, variantes) llegan al HTML. Si un control nuevo se
«come» esas opciones, esta prueba falla y obliga a arreglarlo.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

import interui as ui
from interui.base import Component

#: Los mismos módulos que documenta `scripts/gen_docs.py`.
GROUPS = [
    "interui.grid",
    "interui.controls.typography",
    "interui.controls.buttons",
    "interui.controls.inputs",
    "interui.controls.data",
    "interui.controls.feedback",
    "interui.controls.layout",
    "interui.controls.shell",
    "interui.controls.navigation",
    "interui.controls.charts",
    "interui.controls.media",
    "interui.controls.advanced",
    "interui.controls.tags",
    "interui.icons",
]

#: Controles cuyo primer argumento es obligatorio.
ARGS: dict[str, tuple] = {
    "ChartCard": (ui.Sparkline([1, 2, 3]),),
    "CopyButton": ("texto",),
    "DescriptionItem": ("Término", "Definición"),
    "Figure": ("foto.png",),
    "Icon": ("user",),
    "PageHeader": ("Título",),
    "Splitter": (ui.text("a"), ui.text("b")),
    "Stat": ("Etiqueta", "42"),
    "TimelineItem": ("Título",),
    "TreeNode": ("Nodo",),
}

ESTILO = dict(
    bg=ui.colors.indigo_500,
    pad=ui.pad.p_6,
    font=ui.font.lg,
    class_="sonda",
)
ESPERADO = ("bg-indigo-500", "p-6", "text-lg", "sonda")


def _catalogo() -> list[tuple[str, type[Component]]]:
    out: list[tuple[str, type[Component]]] = []
    for module_name in GROUPS:
        module = importlib.import_module(module_name)
        for name in getattr(module, "__all__", []):
            obj = getattr(module, name, None)
            if inspect.isclass(obj) and issubclass(obj, Component):
                out.append((name, obj))
    return sorted(set(out), key=lambda item: item[0])


CATALOGO = _catalogo()


def test_el_catalogo_no_esta_vacio() -> None:
    assert len(CATALOGO) > 180, "¿se rompió el descubrimiento de controles?"


@pytest.mark.parametrize("nombre,cls", CATALOGO, ids=[name for name, _cls in CATALOGO])
def test_cada_control_acepta_estilos(nombre: str, cls: type[Component]) -> None:
    """`bg`, `pad`, `font` y `class_` funcionan en los 200+ controles."""
    html = ui.render(cls(*ARGS.get(nombre, ()), **ESTILO))
    faltan = [token for token in ESPERADO if token not in html]
    assert not faltan, f"{nombre} ignora {faltan}"


def test_utilidades_sueltas_llegan_al_html() -> None:
    casos = {
        "border": (ui.Card("x", border=ui.colors.red_500), "border-red-500"),
        "rounded": (ui.Card("x", rounded=ui.radius.xl), "rounded-xl"),
        "shadow": (ui.Card("x", shadow=ui.shadow.md), "shadow-md"),
        "ring": (ui.Card("x", ring=ui.colors.blue_500), "ring-blue-500"),
        "w": (ui.Card("x", w=ui.width.full), "w-full"),
        "h": (ui.Card("x", h=ui.height.screen), "h-screen"),
        "opacity": (ui.Card("x", opacity=ui.opacity._50), "opacity-50"),
        "hover": (ui.Card("x", hover_bg=ui.colors.slate_100), "hover:bg-slate-100"),
        "dark": (ui.Card("x", dark_bg=ui.colors.slate_900), "dark:bg-slate-900"),
        "color": (ui.Text("x", color=ui.colors.emerald_600), "text-emerald-600"),
    }
    for nombre, (control, clase) in casos.items():
        html = ui.render(control)
        assert clase in html, f"{nombre} no aplica {clase}"


def test_valores_literales_van_al_style() -> None:
    html = ui.render(ui.Card("x", bg=ui.colors.hex("#0f172a"), style="outline: 1px dashed red"))
    assert "#0f172a" in html
    assert "outline: 1px dashed red" in html


def test_atributos_aria_y_data() -> None:
    html = ui.render(ui.Card("x", aria={"label": "hola"}, data={"prueba": 1}))
    assert 'aria-label="hola"' in html
    assert 'data-prueba="1"' in html


def test_icono_en_cualquier_control_que_lo_admita() -> None:
    """Casi todos los controles aceptan `icon=`; se comprueba sobre una muestra."""
    controles = [
        ui.Button("Guardar", icon="save"),
        ui.Input("", icon="user"),
        ui.Select([("a", "A")], icon="list"),
        ui.Badge("Nuevo", icon="star"),
        ui.Alert("Aviso", icon="bell"),
        ui.Stat("Total", "42", icon="chart"),
        ui.TimelineItem("Paso", icon="check"),
        ui.CopyButton("texto", icon="copy"),
    ]
    for control in controles:
        assert "<svg" in ui.render(control), f"{type(control).__name__} no dibuja el icono"


def test_html_respeta_visible_y_envuelve_si_hay_estilos() -> None:
    assert ui.render(ui.Html("<b>hola</b>")) == "<b>hola</b>"
    assert ui.render(ui.Html("<b>hola</b>", visible=False)) == ""
    con_clases = ui.render(ui.Html("<b>hola</b>", class_="sonda", pad=ui.pad.p_2))
    assert con_clases.startswith("<div")
    assert "sonda" in con_clases
    assert "p-2" in con_clases
    assert "<b>hola</b>" in con_clases


def test_spinner_se_puede_colorear() -> None:
    html = ui.render(ui.Spinner(size=6, color=ui.colors.red_500, class_="sonda"))
    assert "h-6 w-6" in html
    assert "text-red-500" in html
    assert "sonda" in html
    assert ui.render(ui.Spinner(visible=False)) == ""


def test_icono_respeta_visible() -> None:
    assert ui.render(ui.Icon("user", visible=False)) == ""
    assert "<svg" in ui.render(ui.Icon("user", color=ui.colors.red_500))


def test_tabs_sin_pestanas_no_rompe() -> None:
    html = ui.render(ui.Tabs([]))
    assert "data-iui-tabbar" in html
