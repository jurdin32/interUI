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


def test_aliases_are_static_for_the_editor():
    """Los alias deben declararse de forma estática, no con globals().update().

    Si se inyectan en tiempo de ejecución, Pylance marca
    «"text" es un símbolo de importación desconocido» aunque el código funcione.
    """
    source = (PACKAGE / "__init__.py").read_text(encoding="utf-8")
    assert "globals().update" not in source, "los alias deben ser estáticos (interui/aliases.py)"
    assert "from .aliases import *" in source

    aliases_path = PACKAGE / "aliases.py"
    assert aliases_path.exists(), "falta interui/aliases.py"
    tree = ast.parse(aliases_path.read_text(encoding="utf-8"))

    assigned = {
        node.targets[0].id
        for node in tree.body
        if isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name)
    }
    declared: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Assign):  # __all__ = [...]
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id == "__all__":
                declared = {elt.value for elt in node.value.elts}  # type: ignore[attr-defined]
    assert declared, "interui/aliases.py debe declarar __all__"
    assert declared <= assigned, f"alias en __all__ sin asignación: {sorted(declared - assigned)}"


def test_every_alias_points_to_a_real_control():
    import interui
    from interui import aliases

    for alias in aliases.__all__:
        assert hasattr(interui, alias), f"interui.{alias} no existe"
        target = getattr(interui, alias)
        assert isinstance(target, type), f"interui.{alias} no es un control"
        assert interui.SIMPLE_ALIASES[alias] == target.__name__


def test_catalog_has_no_name_collisions():
    """Cada control exportado debe ser único (sin sombras accidentales)."""
    import interui
    from collections import Counter

    duplicated = [name for name, count in Counter(interui.__all__).items() if count > 1]
    assert not duplicated, f"nombres repetidos en __all__: {duplicated}"
