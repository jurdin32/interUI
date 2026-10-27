"""Las pruebas ejecutan los ejemplos reales: si un ejemplo se rompe, falla la CI.

Cada archivo de `examples/` se importa en un directorio de datos temporal y se
renderizan todas sus vistas.
"""

from __future__ import annotations

import importlib.util
import pathlib

import pytest

import interui as ui

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXAMPLES = sorted((ROOT / "examples").glob("*.py"))


def _load(path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path):
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path / path.stem))
    spec = importlib.util.spec_from_file_location(f"example_{path.stem}", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _apps(module) -> list[ui.App]:
    found = [value for value in vars(module).values() if isinstance(value, ui.App)]
    if found:
        return found
    # La API compacta (`window(...)`) no necesita asignar la app a una variable.
    from interui.simple import current_app

    app = current_app()
    return [app] if app.routes else []


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_has_an_app(path, monkeypatch, tmp_path):
    module = _load(path, monkeypatch, tmp_path)
    apps = _apps(module)
    assert apps, f"{path.name} no define ninguna instancia de App"
    for app in apps:
        assert app.routes, f"{path.name}: la app no registra páginas"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_routes_render(path, monkeypatch, tmp_path):
    module = _load(path, monkeypatch, tmp_path)
    for app in _apps(module):
        for route in app.routes:
            if "<" in route:  # rutas con parámetros necesitan datos concretos
                continue
            title, html, bindings = app.render_page(route)
            assert title
            assert html.startswith('<div id="iui-root"')
            assert len(html) > 200, f"{path.name} {route}: render sospechosamente pequeño"
            assert "Traceback" not in html
            assert "None</" not in html
            assert isinstance(bindings, dict)


def test_crud_example_behaviour(monkeypatch, tmp_path):
    """El ejemplo de referencia debe crear, buscar y borrar de verdad."""
    module = _load(ROOT / "examples" / "05_crud.py", monkeypatch, tmp_path)
    app = module.app

    _title, html, _bindings = app.render_page("/")
    assert "Sin contactos" in html

    module.form_name.set("Ana Ruiz")
    module.form_email.set("ana@ejemplo.com")
    module.form_company.set("Acme")
    module.save_contact()

    _title, html, _bindings = app.render_page("/")
    assert "Ana Ruiz" in html
    assert "Ana Ruiz" in [c["name"] for c in module.contacts.get([])]

    # Validación en Python
    module.form_name.set("A")
    module.form_email.set("sin-arroba")
    module.save_contact()
    assert len(module.errors.get()) == 2

    # Búsqueda
    module.form_name.set("Beto")
    module.form_email.set("beto@ejemplo.com")
    module.save_contact()
    module.query.set("ana")
    assert [c["name"] for c in module.visible_contacts()] == ["Ana Ruiz"]
    _title, html, _bindings = app.render_page("/")
    assert "1 de 2 contactos" in html

    # Borrado (se elimina Beto, que quedó como último)
    beto = next(c for c in module.contacts.get([]) if c["name"] == "Beto")
    module.to_delete.set(beto["id"])
    module.confirm_delete()
    assert [c["name"] for c in module.contacts.get([])] == ["Ana Ruiz"]

    # Persistencia
    stored = (pathlib.Path(app.data_dir) / "contactos.json").read_text(encoding="utf-8")
    assert "Ana Ruiz" in stored
