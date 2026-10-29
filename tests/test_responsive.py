"""Comportamiento en ventanas estrechas: nada se sale ni queda aplastado."""

from __future__ import annotations

import pathlib

import interui as ui

ROOT = pathlib.Path(__file__).resolve().parents[1]
CSS = (ROOT / "interui" / "static" / "app.css").read_text(encoding="utf-8")


def render(component: ui.Component) -> str:
    return ui.render(component)


# --- AppShell: sidebar deslizante -------------------------------------------


def test_app_shell_con_sidebar_trae_panel_deslizante() -> None:
    html = render(ui.AppShell(ui.text("x"), sidebar=ui.Sidebar(ui.SidebarItem("Panel"))))
    assert "iui-shell " in html or 'class="iui-shell' in html
    assert 'data-iui-drawer="toggle"' in html, "falta el botón del menú"
    assert "iui-shell-backdrop" in html
    assert 'data-iui-drawer="close"' in html


def test_app_shell_sin_sidebar_no_muestra_el_boton() -> None:
    html = render(ui.AppShell(ui.text("x")))
    assert "iui-shell-drawer" not in html
    assert "iui-shell-backdrop" not in html


def test_el_contenido_principal_no_desborda_en_horizontal() -> None:
    html = render(ui.AppShell(ui.text("x"), sidebar=ui.Sidebar(ui.text("lateral"))))
    assert "overflow-x-hidden" in html
    assert "min-w-0" in html


def test_el_panel_respeta_el_lado_configurado() -> None:
    html = render(
        ui.AppShell(ui.text("x"), sidebar=ui.Sidebar(ui.text("lateral")), sidebar_position=ui.side.right)
    )
    assert 'data-side="right"' in html
    assert html.index("<main") < html.index("<aside"), "el sidebar derecho va después del contenido"


def test_el_css_trae_las_reglas_del_panel() -> None:
    assert ".iui-shell-row[data-collapsible=true]>aside" in CSS
    assert ".iui-shell[data-sidebar=open]" in CSS
    assert "@media(max-width:767px)" in CSS
    assert ".iui-shell-bar" in CSS


def test_el_sidebar_puede_quedarse_siempre_visible() -> None:
    """`collapsible=False`: el menú no se esconde tras el botón en ventanas estrechas."""
    html = render(
        ui.AppShell(
            ui.text("x"),
            sidebar=ui.Sidebar(ui.SidebarItem("Panel")),
            collapsible=False,
        )
    )
    assert 'data-collapsible="false"' in html
    assert 'data-iui-drawer="toggle"' not in html, "no debe haber botón de menú"
    assert ".iui-shell-row[data-collapsible=true]" in CSS, "las reglas del panel deben ser solo para el plegable"


def test_el_sidebar_colapsable_es_el_comportamiento_por_defecto() -> None:
    html = render(ui.AppShell(ui.text("x"), sidebar=ui.Sidebar(ui.SidebarItem("Panel"))))
    assert 'data-collapsible="true"' in html
    assert 'data-iui-drawer="toggle"' in html


# --- Controles que deben caber ------------------------------------------------


def test_dialogo_cabe_en_la_ventana_y_desplaza_su_cuerpo() -> None:
    html = render(ui.Dialog("¿Seguir?", title="Aviso"))
    assert "max-h-[calc(100dvh-2rem)]" in html
    assert "overflow-y-auto" in html


def test_imagen_sin_proporcion_no_se_sale() -> None:
    html = render(ui.Image("foto.png", alt="foto"))
    assert "max-w-full" in html and "h-auto" in html


def test_imagen_con_proporcion_ocupa_el_ancho() -> None:
    html = render(ui.Image("foto.png", alt="foto", ratio="video"))
    assert "h-full w-full" in html


def test_barra_de_estado_ajusta_sus_elementos() -> None:
    html = render(ui.StatusBar(ui.text("Listo"), ui.text("SQLite")))
    assert "flex-wrap" in html


def test_cajon_lateral_usa_ancho_relativo() -> None:
    html = render(ui.Drawer(ui.text("dentro"), title="Filtros"))
    assert "w-[min(" in html


def test_barra_de_menus_desplaza_en_horizontal() -> None:
    html = render(ui.MenuBar({"Archivo": [ui.ContextItem("Salir")]}))
    assert "overflow-x-auto" in html


def test_hay_respaldo_sin_dvh() -> None:
    """Motores antiguos usan 100vh / calc(100vh …); los nuevos, dvh."""
    assert ".iui-shell{height:100vh;height:100dvh}" in CSS.replace(" ", "") or (
        "height:100vh" in CSS and "height:100dvh" in CSS
    )
    assert "max-height:calc(100vh - 2rem)" in CSS
    assert "@supports (height:100dvh)" in CSS or "@supports(height:100dvh)" in CSS
