"""Verificaciones estructurales del paquete.

Evita clases o métodos duplicados (un parche mal aplicado puede dejar dos
definiciones de la misma clase y la segunda sombrea a la primera en silencio) y
comprueba que el catálogo público está completo.
"""

from __future__ import annotations

import ast
import pathlib

import pytest

PACKAGE = pathlib.Path(__file__).resolve().parents[1] / "interui"


def _modules() -> list[pathlib.Path]:
    return sorted(path for path in PACKAGE.rglob("*.py"))


@pytest.mark.parametrize("path", _modules(), ids=lambda p: p.name)
def test_no_duplicate_definitions(path: pathlib.Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    module_names: dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            module_names[node.name] = module_names.get(node.name, 0) + 1
    duplicated = {name: count for name, count in module_names.items() if count > 1}
    assert not duplicated, f"{path.name}: definiciones duplicadas en el módulo: {duplicated}"

    for node in tree.body:
        if not isinstance(node, ast.ClassDef):
            continue
        methods: dict[str, int] = {}
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods[item.name] = methods.get(item.name, 0) + 1
        duplicated = {name: count for name, count in methods.items() if count > 1}
        assert not duplicated, f"{path.name}:{node.lineno} {node.name}: métodos duplicados: {duplicated}"


@pytest.mark.parametrize("path", _modules(), ids=lambda p: p.name)
def test_every_module_has_docstring(path: pathlib.Path) -> None:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    has_doc = ast.get_docstring(tree) is not None
    if path.name == "__init__.py" and not has_doc:
        pytest.fail(f"{path.name}: falta el docstring del paquete")
    assert has_doc or path.name.startswith("__"), f"{path.name}: falta el docstring"


def test_public_catalog_is_exported():
    import interui

    expected = {
        "App", "Component", "Row", "Col", "Container", "Button", "Input", "Select",
        "Textarea", "Checkbox", "Switch", "Slider", "Table", "DataTable", "Card",
        "Modal", "Tabs", "Progress", "Alert", "Icon", "TitleBar", "StatusBar",
    }
    missing = expected - set(interui.__all__)
    assert not missing, f"faltan en __all__: {sorted(missing)}"
    unresolved = {name for name in interui.__all__ if not hasattr(interui, name)}
    assert not unresolved, f"exportados pero inexistentes: {sorted(unresolved)}"


def test_catalog_has_no_name_collisions():
    """Cada control exportado debe ser único (sin sombras accidentales)."""
    import interui
    from collections import Counter

    duplicated = [name for name, count in Counter(interui.__all__).items() if count > 1]
    assert not duplicated, f"nombres repetidos en __all__: {duplicated}"
