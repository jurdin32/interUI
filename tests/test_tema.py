"""Tema global (`estilos.py`): colores y tamaños para todas las ventanas."""

from __future__ import annotations

import ast
import subprocess
import sys

import pytest

import interui as ui
from interui import db
from interui.config import Config
from interui.context import RenderContext
from interui.tema import (
    aplicar_tema,
    estilos_de,
    por_defecto,
    reiniciar_tema,
    tema_actual,
)


@pytest.fixture(autouse=True)
def sin_tema():
    reiniciar_tema()
    yield
    reiniciar_tema()


def _html(component: ui.Component) -> str:
    return component.render(RenderContext(), "t")


# --- el registro -----------------------------------------------------------
def test_aplicar_y_reiniciar() -> None:
    aplicar_tema({"Button": dict(pad=ui.pad.px_6)})
    assert tema_actual() == {"Button": {"pad": "px-6"}}
    reiniciar_tema()
    assert tema_actual() == {}


def test_se_suma_lo_que_se_aplica_despues() -> None:
    aplicar_tema({"Button": dict(pad=ui.pad.px_6)})
    aplicar_tema({"Button": dict(font=ui.font.sm), "Card": dict(radius="2xl")})
    assert tema_actual()["Button"] == {"pad": "px-6", "font": "text-sm"}
    assert tema_actual()["Card"] == {"radius": "2xl"}


def test_reiniciar_en_la_misma_llamada() -> None:
    aplicar_tema({"Card": dict(radius="2xl")})
    aplicar_tema({"Card": dict(radius="sm")}, reiniciar=True)
    assert tema_actual() == {"Card": {"radius": "sm"}}


def test_estilos_de_acepta_clase_instancia_y_nombre() -> None:
    aplicar_tema({"*": dict(rounded="2xl"), "Button": dict(pad=ui.pad.p_5)})
    esperado = {"rounded": "2xl", "pad": "p-5"}
    assert estilos_de(ui.Button) == esperado
    assert estilos_de(ui.Button("x")) == esperado
    assert estilos_de("Button") == {"rounded": "2xl", "pad": "p-5"}
    assert estilos_de(ui.Card) == {"rounded": "2xl"}


def test_por_defecto_no_pisa_lo_explicito() -> None:
    aplicar_tema({"Card": dict(radius="2xl")})
    assert por_defecto(ui.Card, "radius") == "2xl"
    assert por_defecto(ui.Card, "radius", "sm") == "sm"


# --- se aplica a los controles --------------------------------------------
def test_el_comodin_llega_a_todos_los_controles() -> None:
    aplicar_tema({"*": dict(rounded="2xl")})
    assert "rounded-2xl" in _html(ui.Button("Guardar"))
    assert "rounded-2xl" in _html(ui.Card("x"))


def test_solo_el_control_nombrado() -> None:
    aplicar_tema({"Button": dict(pad=ui.pad.p_6)})
    assert "p-6" in _html(ui.Button("Guardar"))
    assert "p-6" not in _html(ui.Card("x"))


def test_lo_explicito_gana_sobre_el_tema() -> None:
    aplicar_tema({"Button": dict(pad=ui.pad.p_6)})
    assert "p-2" in _html(ui.Button("Guardar", pad=ui.pad.p_2))
    assert "p-6" not in _html(ui.Button("Guardar", pad=ui.pad.p_2))


def test_la_clave_de_la_clase_base_vale_para_las_subclases() -> None:
    class MiBoton(ui.Button):
        pass

    aplicar_tema({"Button": dict(pad=ui.pad.p_6)})
    assert "p-6" in _html(MiBoton("Guardar"))


def test_la_variante_tambien_se_puede_fijar() -> None:
    aplicar_tema({"Button": dict(hover_bg=ui.colors.emerald_500)})
    assert "hover:bg-emerald-500" in _html(ui.Button("Guardar"))


def test_class_y_style_en_el_tema() -> None:
    aplicar_tema({"Card": dict(class_="ring-2", style={"min-height": "10rem"})})
    html = _html(ui.Card("x"))
    assert "ring-2" in html
    assert "min-height" in html


# --- opciones propias ------------------------------------------------------
def test_card_cabecera_y_esquinas() -> None:
    aplicar_tema({"Card": dict(header_bg=ui.colors.amber_100, radius="2xl")})
    html = _html(ui.Card("x", title="Hola"))
    assert "bg-amber-100" in html
    assert "rounded-2xl" in html
    assert "header-bg=" not in html, "la opción no debe acabar como atributo HTML"


def test_card_respeta_radius_de_fabrica() -> None:
    assert "rounded-xl" in _html(ui.Card("x"))
    assert "rounded-2xl" in _html(ui.Card("x", radius="lg"))
    assert "rounded-xl" in _html(ui.Card("x", radius=ui.radius.xl))


def test_tabla_colores_desde_el_tema() -> None:
    aplicar_tema(
        {
            "Table": dict(
                header_bg=ui.colors.amber_100,
                header_color=ui.colors.amber_900,
                zebra=ui.colors.slate_50,
                striped=True,
            )
        }
    )
    html = _html(ui.Table(headers=["A"], rows=[["1"], ["2"]]))
    assert "bg-amber-100" in html
    assert "text-amber-900" in html


def test_dialogo_desde_el_tema() -> None:
    aplicar_tema({"Dialog": dict(header_bg=ui.colors.slate_100, body_pad=ui.pad.p_8)})
    html = _html(ui.Dialog(title="Aviso", message="Hola"))
    assert "bg-slate-100" in html
    assert "p-8" in html


def test_formulario_de_modelo_desde_el_tema() -> None:
    class Persona(ui.Model):
        nombre = ui.Str(max_length=60)

        class Meta:
            table = "tema_personas"

    class PersonaForm(ui.ModelForm):
        model = Persona

    aplicar_tema({"ModelForm": dict(header_bg=ui.colors.slate_100)})
    html = _html(PersonaForm())
    assert "bg-slate-100" in html


def test_modal_declarado_desde_el_tema() -> None:
    class Persona(ui.Model):
        nombre = ui.Str(max_length=60)

        class Meta:
            table = "tema_modal_personas"

    class PersonaForm(ui.ModelForm):
        model = Persona

    class PersonaModal(ui.FormModal):
        form = PersonaForm

    aplicar_tema({"FormModal": dict(width="2xl")})
    assert estilos_de(PersonaModal)["width"] == "2xl"


# --- tablas de registro ----------------------------------------------------
class Persona(ui.Model):
    nombre = ui.Str(max_length=120)
    email = ui.Str(max_length=120, unique=True)

    class Meta:
        table = "tema_personas"
        order = ["nombre"]


class PersonaForm(ui.ModelForm):
    model = Persona


@pytest.fixture
def app(tmp_path):
    db.reset()
    db.configure(
        Config({"databases": {"default": {"engine": "sqlite", "name": str(tmp_path / "t.db")}}})
    )
    db.backend().create_table("tema_personas", Persona.columns())
    for numero in range(1, 4):
        Persona.objects.create(nombre=f"Persona {numero}", email=f"p{numero}@x.com")
    yield ui.App("Tema", data_dir=tmp_path)
    db.reset()


def _pagina(app: ui.App, componente: ui.Component) -> str:
    app.page("/t")(lambda: ui.Screen(componente))
    _title, html, _bindings = app.render_page("/t")
    return html


def test_tabla_de_registro_toma_el_tema(app) -> None:
    class PersonaTable(ui.RecordTable):
        form = PersonaForm

    aplicar_tema({"RecordTable": dict(header_bg=ui.colors.amber_100, striped=True)})
    html = _pagina(app, PersonaTable())
    assert "bg-amber-100" in html, "el tema manda sobre el valor de fábrica"


def test_lo_declarado_en_la_clase_gana_sobre_el_tema(app) -> None:
    class PersonaTable(ui.RecordTable):
        form = PersonaForm
        header_bg = ui.colors.slate_200

    aplicar_tema({"RecordTable": dict(header_bg=ui.colors.amber_100)})
    html = _pagina(app, PersonaTable())
    assert "bg-slate-200" in html
    assert "bg-amber-100" not in html


def test_franja_de_la_pagina_desde_el_tema(app) -> None:
    class PersonaTable(ui.RecordTable):
        form = PersonaForm

    aplicar_tema({"RecordPage": dict(title_bg=ui.colors.emerald_600)})
    html = _pagina(app, ui.RecordPage(PersonaTable))
    assert "bg-emerald-600" in html


# --- archivos generados ----------------------------------------------------
def _iui(desde, *args: str) -> None:
    resultado = subprocess.run(
        [sys.executable, "-m", "interui", *args],
        cwd=desde,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr


def test_startproject_genera_estilos(tmp_path) -> None:
    _iui(tmp_path, "startproject", "demo")
    archivo = tmp_path / "demo" / "demo" / "estilos.py"
    assert archivo.is_file()
    codigo = archivo.read_text(encoding="utf-8")
    ast.parse(codigo)
    assert "TEMA" in codigo
    for nombre in ('"Card"', '"RecordTable"', '"Dialog"', '"FormModal"'):
        assert nombre in codigo, f"el catálogo debe incluir {nombre}"
    assert "aplicar_tema" in codigo
    app_py = (tmp_path / "demo" / "demo" / "app.py").read_text(encoding="utf-8")
    assert "estilos" in app_py


def test_startapp_genera_estilos(tmp_path) -> None:
    _iui(tmp_path, "startproject", "demo")
    _iui(tmp_path / "demo", "startapp", "libros")
    archivo = tmp_path / "demo" / "libros" / "estilos.py"
    assert archivo.is_file()
    codigo = archivo.read_text(encoding="utf-8")
    ast.parse(codigo)
    assert "TEMA" in codigo
    urls = (tmp_path / "demo" / "libros" / "urls.py").read_text(encoding="utf-8")
    assert "estilos" in urls
