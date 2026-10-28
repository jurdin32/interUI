"""`iui startproject`: estructura completa, al estilo de Django y solo escritorio."""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

import pytest

import interui as ui
from interui import cli
from interui.config import Config
from interui.scaffold import create_project, package_name

ROOT = pathlib.Path(__file__).resolve().parents[1]

EXPECTED = {
    "iui.py",
    "interui.json",
    "requirements.txt",
    "README.md",
    ".gitignore",
    "migrations/.gitkeep",
    "data/.gitkeep",
}


@pytest.fixture
def proyecto(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    code = cli.main(["startproject", "tienda"])
    assert code == 0
    return tmp_path / "tienda"


def test_crea_la_estructura_completa(proyecto: pathlib.Path) -> None:
    archivos = {
        str(path.relative_to(proyecto))
        for path in proyecto.rglob("*")
        if path.is_file()
    }
    assert EXPECTED <= archivos
    for esperado in (
        "tienda/__init__.py",
        "tienda/app.py",
        "tienda/urls.py",
        "tienda/views.py",
        "tienda/layout.py",
        "tienda/models.py",
    ):
        assert esperado in archivos, f"falta {esperado}"


def test_los_archivos_generados_compilan(proyecto: pathlib.Path) -> None:
    for path in proyecto.rglob("*.py"):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_la_configuracion_apunta_al_paquete(proyecto: pathlib.Path) -> None:
    settings = Config.load(proyecto / "interui.json")
    assert settings.app.entry == "tienda.app"
    assert settings.migrations.models == "tienda/models.py"
    assert settings.database().engine == "sqlite"
    assert (proyecto / settings.migrations.models).is_file()


def test_el_proyecto_se_importa_y_renderiza(proyecto: pathlib.Path, monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(proyecto))
    from tienda.app import app  # type: ignore[import-not-found]

    assert app.routes == ["/", "/tareas"]
    for route in app.routes:
        title, html, _bindings = app.render_page(route)
        assert title
        assert html.startswith('<div id="iui-root"')
        assert "Traceback" not in html
        assert len(html) > 2000


def test_comandos_del_proyecto(proyecto: pathlib.Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(proyecto)
    assert cli.project_main(["check"]) == 0
    assert cli.project_main(["makemigrations"]) == 0
    assert (proyecto / "migrations" / "0001_initial.json").is_file()
    assert cli.project_main(["migrate"]) == 0
    assert (proyecto / "data" / "app.db").is_file()
    assert cli.project_main(["status"]) == 0
    salida = capsys.readouterr().out
    assert "0001_initial" in salida


def test_el_modelo_guarda_en_la_base(proyecto: pathlib.Path, monkeypatch) -> None:
    monkeypatch.chdir(proyecto)
    cli.project_main(["makemigrations"])
    cli.project_main(["migrate"])
    monkeypatch.syspath_prepend(str(proyecto))

    from tienda.models import Tarea  # type: ignore[import-not-found]

    Tarea.objects.create(titulo="Comprar pan")
    assert Tarea.objects.count() == 1
    assert Tarea.objects.first().titulo == "Comprar pan"


def test_no_sobrescribe_una_carpeta_con_contenido(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "ocupada").mkdir()
    (tmp_path / "ocupada" / "algo.txt").write_text("x", encoding="utf-8")
    with pytest.raises(SystemExit):
        cli.main(["startproject", "ocupada"])
    assert cli.main(["startproject", "ocupada", "--force"]) == 0


def test_el_nombre_se_convierte_en_un_paquete_valido() -> None:
    assert package_name("Mi Tienda") == "mi_tienda"
    assert package_name("mi-proyecto 2") == "mi_proyecto_2"
    assert package_name("2fast") == "app_2fast"
    assert package_name("ñandú") == "nandu"


def test_startproject_con_migrate_inicial(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert cli.main(["startproject", "blog", "--migrate"]) == 0
    assert (tmp_path / "blog" / "migrations" / "0001_initial.json").is_file()
    assert (tmp_path / "blog" / "data" / "app.db").is_file()


def test_el_iui_py_arranca_los_comandos(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert cli.main(["startproject", "agenda"]) == 0
    script = tmp_path / "agenda" / "iui.py"
    result = subprocess.run(
        [sys.executable, str(script), "check"],
        cwd=tmp_path / "agenda",
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "configuración correcta" in result.stdout


def test_el_proyecto_no_es_web(proyecto: pathlib.Path) -> None:
    """Solo escritorio: sin servidor web ni pasos de despliegue en lo generado."""
    for path in proyecto.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".md", ".txt", ".json"}:
            text = path.read_text(encoding="utf-8").lower()
            assert "window=\"browser\"" not in text
            assert "--window browser" not in text
            assert "startproject" not in text or path.name == "README.md"


def test_la_version_del_paquete_se_conserva(proyecto: pathlib.Path) -> None:
    init = (proyecto / "tienda" / "__init__.py").read_text(encoding="utf-8")
    assert '__version__ = "0.1.0"' in init


def test_requirements_instalan_desde_github(proyecto: pathlib.Path) -> None:
    text = (proyecto / "requirements.txt").read_text(encoding="utf-8")
    assert "interui" in text and "git+https://github.com/jurdin32/interUI" in text


def test_el_json_es_valido(proyecto: pathlib.Path) -> None:
    data = json.loads((proyecto / "interui.json").read_text(encoding="utf-8"))
    assert data["app"]["name"] == "tienda"
    assert data["databases"]["default"]["engine"] == "sqlite"
    assert data["migrations"]["directory"] == "migrations"


def test_create_project_devuelve_los_archivos(tmp_path) -> None:
    files = create_project(tmp_path / "otro", "Otro")
    assert len(files) >= 13
    assert all(path.is_file() for path in files)
    assert isinstance(ui, object)
