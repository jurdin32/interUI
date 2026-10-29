"""El proyecto de ejemplo (`examples/proyecto_tareas`) debe arrancar de cero.

Se copia a una carpeta temporal para que la base de datos de prueba no acabe en
el repositorio y se comprueba el recorrido real: `main.prepare_database()` crea
las tablas y las vistas renderizan con datos.
"""

from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EJEMPLO = ROOT / "examples" / "proyecto_tareas"


def _copiar(tmp_path: pathlib.Path) -> pathlib.Path:
    destino = tmp_path / "proyecto_tareas"
    shutil.copytree(
        EJEMPLO,
        destino,
        ignore=shutil.ignore_patterns("data", "__pycache__", "*.pyc"),
    )
    return destino


def test_el_proyecto_de_ejemplo_arranca_desde_cero(tmp_path: pathlib.Path) -> None:
    proyecto = _copiar(tmp_path)
    code = """
import main

main.prepare_database()

from notas.models import Nota
from proyecto_tareas.app import app

assert Nota.objects.count() == 0
Nota.objects.create(titulo="Comprar café")
assert Nota.objects.count() == 1

for ruta in app.routes:
    titulo, html, _bindings = app.render_page(ruta)
    assert titulo and html.startswith('<div id="iui-root"')

_titulo, notas, _bindings = app.render_page("/notas")
assert "Comprar café" in notas
print("ok")
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=proyecto,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "ok" in result.stdout
    assert (proyecto / "data" / "app.db").is_file()


def test_el_ejemplo_tiene_la_estructura_de_proyecto(tmp_path: pathlib.Path) -> None:
    proyecto = _copiar(tmp_path)
    for esperado in (
        "main.py",
        "iui.py",
        "interui.json",
        "proyecto_tareas/app.py",
        "notas/models.py",
        "notas/urls.py",
        "migrations/0001_initial.json",
    ):
        assert (proyecto / esperado).is_file(), f"falta {esperado}"
