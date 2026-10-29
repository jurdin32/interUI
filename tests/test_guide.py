"""La guía se ejecuta: cada ejemplo completo de `docs/*.md` debe arrancar y renderizar.

Los bloques ```python de la documentación se compilan siempre y, si son
aplicaciones completas (`app.run()`), se ejecutan sustituyendo `app.run()` por
una no-op para poder renderizar sus vistas sin abrir ventanas.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

import interui as ui

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = [
    ROOT / "docs" / "guia.md",
    ROOT / "docs" / "menus.md",
    ROOT / "docs" / "actualizar.md",
    ROOT / "docs" / "estilos.md",
    ROOT / "docs" / "datos.md",
    ROOT / "docs" / "formularios.md",
    ROOT / "README.md",
]
BLOCK = re.compile(r"```python\n(.*?)```", re.S)


def _blocks(path: pathlib.Path) -> list[str]:
    return [block for block in BLOCK.findall(path.read_text(encoding="utf-8"))]


PY_BLOCKS = [(path, block) for path in DOCS for block in _blocks(path)]


def _ids(block: str) -> str:
    first = block.strip().splitlines()[0][:60]
    return first


@pytest.mark.parametrize("path,block", PY_BLOCKS, ids=[_ids(b) for _p, b in PY_BLOCKS])
def test_documentation_snippets_compile(path: pathlib.Path, block: str) -> None:
    compile(block, str(path), "exec")


RUNNABLE = [(path, block) for path, block in PY_BLOCKS if "app.run()" in block]


def test_guide_has_runnable_apps() -> None:
    assert len(RUNNABLE) >= 8, (
        f"solo {len(RUNNABLE)} ejemplos ejecutables en la documentación; "
        "la guía debe cubrir el recorrido completo"
    )


@pytest.mark.parametrize("path,block", RUNNABLE, ids=[_ids(b) for _p, b in RUNNABLE])
def test_guide_apps_render(path: pathlib.Path, block: str, monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path))
    source = block.replace("app.run()", "pass")
    namespace: dict[str, object] = {"__name__": "guia"}
    exec(compile(source, str(path), "exec"), namespace)  # noqa: S102 - código del repo

    apps = [value for value in namespace.values() if isinstance(value, ui.App)]
    assert apps, f"{path.name}: el ejemplo no crea una App"
    for app in apps:
        assert app.routes
        for route in app.routes:
            if "<" in route:
                continue
            title, html, bindings = app.render_page(route)
            assert title
            assert html.startswith('<div id="iui-root"')
            # El primer ejemplo de la guía es una ventana vacía a propósito.
            assert len(html) >= 40, f"{path.name} {route}: render vacío"
            assert "Traceback" not in html
            assert "None</" not in html


GUIDE = ROOT / "docs" / "guia.md"


def test_guide_covers_the_full_journey() -> None:
    """La guía debe ir de la ventana vacía a la app completa."""
    text = GUIDE.read_text(encoding="utf-8")
    milestones = [
        "La ventana más pequeña posible",
        "Añadir contenido y jerarquía",
        "La rejilla de 12 columnas",
        "Botones y eventos",
        "Estado reactivo",
        "Formularios con validación",
        "tabla y búsqueda",
        "Varias vistas",
        "Diálogos, notificaciones y archivos",
        "Tema claro y oscuro",
        "Persistencia de datos",
        "Empaquetar y distribuir",
    ]
    for milestone in milestones:
        assert milestone in text, f"falta la sección: {milestone}"


def test_guide_links_exist() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#]+)\)", text):
        if target.startswith("http"):
            continue
        assert (GUIDE.parent / target).exists(), f"enlace roto en la guía: {target}"


def test_readme_links_exist() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)#]+)\)", text):
        if target.startswith("http"):
            continue
        assert (ROOT / target).exists(), f"enlace roto en el README: {target}"


def test_control_reference_links_back_to_guide() -> None:
    text = (ROOT / "docs" / "controles.md").read_text(encoding="utf-8")
    assert "guia.md" in text or "scripts/gen_docs.py" in text


def _unused() -> None:  # pragma: no cover - evita advertencias de importaciones
    importlib.util.find_spec("interui")
