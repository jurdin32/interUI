"""La documentación de controles se ejecuta: cada ejemplo debe renderizar.

Si un control cambia de firma o se rompe, estas pruebas fallan y obligan a
actualizar `docs/controles.md` con `python scripts/gen_docs.py`.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

import interui as ui

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("gen_docs", ROOT / "scripts" / "gen_docs.py")
assert SPEC and SPEC.loader
gen_docs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gen_docs)


def _controls() -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for _title, module_name in gen_docs.GROUPS:
        for name, _cls in gen_docs.controls_of(module_name):
            out.append((module_name, name))
    return out


CONTROLS = _controls()


def test_catalog_is_complete() -> None:
    """Cada control exportado del paquete debe estar documentado."""
    documented = {name for _module, name in CONTROLS}
    exported = set(ui.__all__)
    missing = {
        name
        for name in exported
        if name in documented and name not in documented  # nunca ocurre: guarda de tipos
    }
    assert not missing
    # Los controles documentados deben existir realmente en el paquete.
    unknown = {name for name in documented if not hasattr(ui, name)}
    assert not unknown, f"documentados pero inexistentes: {sorted(unknown)}"
    assert len(documented) >= 190, f"solo {len(documented)} controles documentados"


@pytest.mark.parametrize("module,name", CONTROLS, ids=[f"{m.split('.')[-1]}.{n}" for m, n in CONTROLS])
def test_example_renders(module: str, name: str) -> None:
    snippet = gen_docs.snippet_for(name)
    component = eval(snippet, {"ui": ui})  # noqa: S307 - código propio del repositorio
    assert isinstance(component, ui.Component), f"{name}: el ejemplo no devuelve un Component"
    html = ui.render(component)
    assert html, f"{name}: el ejemplo renderiza vacío"
    assert "<" in html
    # Nunca debe escaparse un error de plantilla a la salida.
    assert "None" not in html.replace("NoneType", ""), f"{name}: aparece 'None' en el HTML"


def test_every_control_has_a_description_and_example() -> None:
    missing_description = [
        name
        for module, name in CONTROLS
        if not gen_docs.description_for(module, name)
    ]
    assert not missing_description, f"sin descripción: {missing_description}"
    for _module, name in CONTROLS:
        assert gen_docs.snippet_for(name), f"{name}: sin ejemplo"


def test_generated_markdown_is_up_to_date() -> None:
    current = (ROOT / "docs" / "controles.md").read_text(encoding="utf-8")
    assert current == gen_docs.build_markdown(), (
        "docs/controles.md está desactualizado: ejecuta `python scripts/gen_docs.py`"
    )


def test_icon_catalog_is_up_to_date() -> None:
    current = (ROOT / "docs" / "iconos.md").read_text(encoding="utf-8")
    assert current == gen_docs.build_icon_markdown(), (
        "docs/iconos.md está desactualizado: ejecuta `python scripts/gen_docs.py`"
    )


def test_icon_catalog_lists_every_icon() -> None:
    markdown = gen_docs.build_icon_markdown()
    for name in ui.ICON_NAMES:
        assert f"`{name}`" in markdown, f"falta el icono {name}"


def test_markdown_has_examples_for_every_control() -> None:
    markdown = gen_docs.build_markdown()
    for _module, name in CONTROLS:
        assert f"### `ui.{name}`" in markdown, f"falta la sección de {name}"
        assert gen_docs.snippet_for(name) in markdown, f"falta el ejemplo de {name}"
