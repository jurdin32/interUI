"""La guía se ejecuta: cada ejemplo completo de `docs/*.md` debe arrancar y renderizar.

Los bloques ```python de la documentación se compilan siempre y, si son
aplicaciones completas (`app.run()` o `window(...).run()`), se ejecutan
sustituyendo el `.run()` por una no-op para poder renderizar sus vistas sin
abrir ventanas.
"""

from __future__ import annotations

import importlib.util
import pathlib
import re

import pytest

import interui as ui
import interui.simple as simple

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


COMPACT = [
    (path, block)
    for path, block in PY_BLOCKS
    if ").run()" in block and "app.run()" not in block
]


def test_guide_has_compact_windows() -> None:
    assert len(COMPACT) >= 5, (
        f"solo {len(COMPACT)} ejemplos con `window(...)`; el tutorial empieza por ahí"
    )


@pytest.mark.parametrize("path,block", COMPACT, ids=[_ids(b) for _p, b in COMPACT])
def test_compact_windows_render(path: pathlib.Path, block: str, monkeypatch) -> None:
    """`window(...).run()`: se ejecuta sin abrir ventana y su página se pinta."""
    monkeypatch.setattr(simple, "_DEFAULT_APP", None)
    source = block.replace(").run()", ")")
    exec(compile(source, str(path), "exec"), {"__name__": "guia"})  # noqa: S102

    application = simple._DEFAULT_APP
    assert application is not None, f"{path.name}: el ejemplo no crea la ventana"
    title, html, _bindings = application.render_page("/")
    assert title
    assert html.startswith('<div id="iui-root"')
    assert len(html) >= 40, f"{path.name}: render vacío"
    assert "Traceback" not in html and "None</" not in html


GUIDE = ROOT / "docs" / "guia.md"


def test_guide_covers_the_full_journey() -> None:
    """La guía debe ir de la ventana vacía a la app completa."""
    text = GUIDE.read_text(encoding="utf-8")
    milestones = [
        "Paso 1 · La ventana más pequeña posible",
        "Paso 2 · Añadir contenido y jerarquía",
        "Paso 3 · Poner un menú",
        "Paso 4 · Botones y eventos",
        "Paso 5 · Estado reactivo",
        "Paso 6 · La rejilla de 12 columnas",
        "Paso 7 · Varias vistas y navegación",
        "Paso 8 · Formularios con validación",
        "Paso 9 · Mostrar datos: tabla y búsqueda",
        "Paso 10 · Persistencia de datos",
        "Paso 11 · Formulario desde un modelo",
        "Paso 12 · De archivo suelto a proyecto",
        "tema claro y oscuro",
        "diálogos y avisos",
        "empaquetar y distribuir",
        "Errores frecuentes",
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
    """El README se publica en PyPI: los enlaces van absolutos al repositorio."""
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    base = "https://github.com/jurdin32/interUI/"
    for target in re.findall(r"\]\(([^)#]+)\)", text):
        if target.startswith(base):
            # .../blob/main/docs/x.md -> docs/x.md (y que exista de verdad)
            local = target[len(base):].split("/", 2)[2]
            assert (ROOT / local).exists(), f"enlace roto en el README: {target}"
            continue
        if target.startswith("http"):
            continue
        assert (ROOT / target).exists(), f"enlace roto en el README: {target}"


def test_control_reference_links_back_to_guide() -> None:
    text = (ROOT / "docs" / "controles.md").read_text(encoding="utf-8")
    assert "guia.md" in text or "scripts/gen_docs.py" in text


def _unused() -> None:  # pragma: no cover - evita advertencias de importaciones
    importlib.util.find_spec("interui")
