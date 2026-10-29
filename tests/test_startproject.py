"""`iui startproject`: estructura completa de un proyecto de escritorio."""

from __future__ import annotations

import io
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
    "main.py",
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
    for esperado in ("tienda/__init__.py", "tienda/app.py"):
        assert esperado in archivos, f"falta {esperado}"
    # El proyecto solo lleva configuración: modelos y vistas van en las apps.
    for sobrante in (
        "tienda/layout.py",
        "tienda/views.py",
        "tienda/models.py",
        "tienda/urls.py",
    ):
        assert sobrante not in archivos, f"el proyecto no debe traer {sobrante}"


def test_los_archivos_generados_compilan(proyecto: pathlib.Path) -> None:
    for path in proyecto.rglob("*.py"):
        compile(path.read_text(encoding="utf-8"), str(path), "exec")


def test_la_configuracion_apunta_al_paquete(proyecto: pathlib.Path) -> None:
    settings = Config.load(proyecto / "interui.json")
    assert settings.app.entry == "tienda.app"
    assert settings.database().engine == "sqlite"
    # Sin apps no hay modelos: el proyecto es solo configuración.
    assert settings.migrations.models == []
    assert settings.model_paths() == []


def test_el_proyecto_se_importa_y_renderiza(proyecto: pathlib.Path, monkeypatch) -> None:
    monkeypatch.syspath_prepend(str(proyecto))
    from tienda.app import app  # type: ignore[import-not-found]

    assert app.routes == ["/"], "el proyecto inicial trae una sola página"
    title, html, _bindings = app.render_page("/")
    assert title
    assert html.startswith('<div id="iui-root"')
    assert "Traceback" not in html
    assert "Hola mundo" in html
    assert "items-center" in html and "justify-center" in html, "la etiqueta va centrada"


def test_comandos_del_proyecto(proyecto: pathlib.Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(proyecto)
    assert cli.project_main(["check"]) == 0
    assert cli.project_main(["makemigrations"]) == 0
    assert "no hay cambios" in capsys.readouterr().out
    assert cli.project_main(["migrate"]) == 0
    assert (proyecto / "data" / "app.db").is_file()
    assert cli.project_main(["status"]) == 0


def test_un_modelo_nuevo_se_migra_y_guarda(proyecto: pathlib.Path, monkeypatch) -> None:
    """El proyecto nace vacío: los modelos entran con una app."""
    monkeypatch.chdir(proyecto)
    assert cli.main(["startapp", "tareas"]) == 0
    (proyecto / "tareas" / "models.py").write_text(
        "import interui as ui\n"
        "\n"
        "class Tarea(ui.Model):\n"
        "    titulo = ui.Str(max_length=120)\n"
        "\n"
        "    class Meta:\n"
        "        table = \"tareas\"\n",
        encoding="utf-8",
    )
    assert cli.project_main(["makemigrations"]) == 0
    assert (proyecto / "migrations" / "0001_initial.json").is_file()
    assert cli.project_main(["migrate"]) == 0
    monkeypatch.syspath_prepend(str(proyecto))
    _fresh_modules("tienda", "tareas")

    from tareas.models import Tarea  # type: ignore[import-not-found]

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


def test_startproject_con_migrate_crea_la_base(tmp_path, monkeypatch) -> None:
    """Sin modelos no hay migración que generar, pero la base queda lista."""
    monkeypatch.chdir(tmp_path)
    assert cli.main(["startproject", "blog", "--migrate"]) == 0
    assert (tmp_path / "blog" / "data" / "app.db").is_file()
    assert not list((tmp_path / "blog" / "migrations").glob("0*.json"))


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
    assert len(files) >= 10
    assert all(path.is_file() for path in files)
    assert isinstance(ui, object)


# ---------------------------------------------------------------------------
# startapp: apps dentro del proyecto
# ---------------------------------------------------------------------------
def test_startapp_crea_la_app_y_la_registra(proyecto: pathlib.Path, monkeypatch) -> None:
    monkeypatch.chdir(proyecto)
    assert cli.main(["startapp", "Tareas"]) == 0

    for esperado in ("__init__.py", "models.py", "forms.py", "views.py", "urls.py", "README.md"):
        assert (proyecto / "tareas" / esperado).is_file(), f"falta tareas/{esperado}"

    data = json.loads((proyecto / "interui.json").read_text(encoding="utf-8"))
    assert data["apps"] == ["tareas"]
    assert "tareas/models.py" in data["migrations"]["models"]

    settings = Config.load(proyecto / "interui.json")
    assert settings.installed_apps() == ["tareas"]
    assert (proyecto / "tareas" / "models.py") in settings.model_paths()


def _fresh_modules(*names: str) -> None:
    """Olvida imports previos: cada prueba crea su propio ``interui.json``."""
    for name in list(sys.modules):
        root = name.split(".")[0]
        if root in names:
            del sys.modules[name]


def test_startapp_registra_las_rutas_sin_tocar_urls(proyecto: pathlib.Path, monkeypatch) -> None:
    monkeypatch.chdir(proyecto)
    assert cli.main(["startapp", "clientes"]) == 0
    monkeypatch.syspath_prepend(str(proyecto))
    _fresh_modules("tienda", "clientes")

    from tienda.app import create_app

    app = create_app()
    assert app.has_page("/clientes"), app.routes
    title, html, _bindings = app.render_page("/clientes")
    assert title == "clientes"
    assert "clientes" in html


def test_la_app_generada_guarda_desde_su_formulario(proyecto: pathlib.Path, monkeypatch) -> None:
    """``startapp`` deja el formulario listo: se rellenan señales y se guarda."""
    monkeypatch.chdir(proyecto)
    assert cli.main(["startapp", "clientes"]) == 0
    assert cli.main(["db", "makemigrations"]) == 0
    assert cli.main(["db", "migrate"]) == 0
    monkeypatch.syspath_prepend(str(proyecto))
    _fresh_modules("tienda", "clientes")

    from tienda.app import create_app

    app = create_app()
    title, html, bindings = app.render_page("/clientes")
    assert "ClienteForm" in (proyecto / "clientes" / "forms.py").read_text(encoding="utf-8")
    assert title == "clientes"

    from interui.events import UIEvent, invoke

    def señales():
        return {
            name: signal
            for name, signal in app._signals.items()
            if name.startswith("form_clientes_")
        }

    for name, signal in señales().items():
        if name.endswith("_nombre"):
            signal.set("ACME")

    handler = next(
        handler
        for handlers in bindings.values()
        for event, handler in handlers.items()
        if event == "click"
    )
    invoke(handler, UIEvent(id="x", event="click"))

    from clientes.models import Cliente

    assert Cliente.objects.count() == 1
    assert Cliente.objects.first().nombre == "ACME"
    assert "ACME" in app.render_page("/clientes")[1]


def test_startapp_no_duplica_apps_ni_rutas(proyecto: pathlib.Path, monkeypatch) -> None:
    monkeypatch.chdir(proyecto)
    assert cli.main(["startapp", "clientes"]) == 0
    assert cli.main(["startapp", "clientes"]) == 1, "no debe sobrescribir sin --force"

    data = json.loads((proyecto / "interui.json").read_text(encoding="utf-8"))
    assert data["apps"] == ["clientes"]
    assert data["migrations"]["models"].count("clientes/models.py") == 1


def test_startapp_fuera_de_un_proyecto_falla(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    assert cli.main(["startapp", "suelta"]) == 1
    assert "interui.json" in capsys.readouterr().err


def test_los_modelos_de_la_app_entran_en_las_migraciones(proyecto: pathlib.Path, monkeypatch) -> None:
    monkeypatch.chdir(proyecto)
    assert cli.main(["startapp", "clientes"]) == 0
    (proyecto / "clientes" / "models.py").write_text(
        "import interui as ui\n"
        "\n"
        "class Cliente(ui.Model):\n"
        "    nombre = ui.Str(max_length=80)\n"
        "\n"
        "    class Meta:\n"
        "        table = \"clientes\"\n",
        encoding="utf-8",
    )
    assert cli.main(["db", "makemigrations"]) == 0
    assert cli.main(["db", "migrate"]) == 0

    settings = Config.load(proyecto / "interui.json")
    migrations = list((proyecto / "migrations").glob("0*.json"))
    assert migrations, "no se generó ninguna migración"
    payload = json.loads(migrations[-1].read_text(encoding="utf-8"))
    tables = {operation["table"] for operation in payload["operations"]}
    assert "clientes" in tables
    assert settings.database().engine == "sqlite"


def test_python_iui_py_startapp(proyecto: pathlib.Path) -> None:
    result = subprocess.run(
        [sys.executable, "iui.py", "startapp", "notas"],
        cwd=proyecto,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert (proyecto / "notas" / "urls.py").is_file()


def test_main_es_el_punto_de_entrada_y_deja_la_base_lista(proyecto: pathlib.Path) -> None:
    """`main.py` crea todo: migra lo pendiente y abre la ventana."""
    text = (proyecto / "main.py").read_text(encoding="utf-8")
    assert "def main()" in text
    assert "create_app().run()" in text
    assert "prepare_database()" in text

    assert subprocess.run(
        [sys.executable, "iui.py", "makemigrations"],
        cwd=proyecto,
        capture_output=True,
        text=True,
        timeout=60,
    ).returncode == 0

    code = (
        "import main; main.prepare_database();"
        "import interui as ui; print(sorted(ui.db.backend().tables()))"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=proyecto,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr
    assert "'interui_migrations'" in result.stdout, result.stdout
    assert "'tareas'" not in result.stdout, "el proyecto nace sin tablas de ejemplo"


# ---------------------------------------------------------------------------
# asistente de `startproject`
# ---------------------------------------------------------------------------
class _TTY(io.StringIO):
    """stdin de mentira: dice que es una terminal para que salga el asistente."""

    def isatty(self) -> bool:  # noqa: D102 - lo exige la CLI
        return True


def _respuestas(monkeypatch, values: list[str]) -> list[str]:
    pendientes = iter(values)
    hechas: list[str] = []

    def fake_input(prompt: str = "") -> str:
        value = next(pendientes)
        hechas.append(f"{prompt}{value}")
        return value

    monkeypatch.setattr("builtins.input", fake_input)
    monkeypatch.setattr(cli.sys, "stdin", _TTY())
    return hechas


def test_startproject_sin_nombre_abre_el_asistente(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    preguntas = _respuestas(
        monkeypatch,
        [
            "Mi Tienda",              # nombre (carpeta y paquete)
            "Mi Tienda — Gestión",    # nombre largo
            ".",                      # carpeta
            "1",                      # sqlite
            "data/tienda.db",         # ruta del archivo
            "dark",                   # tema
            "s",                      # migrar
        ],
    )
    assert cli.main(["startproject"]) == 0

    proyecto = tmp_path / "mi_tienda"
    assert proyecto.is_dir()
    data = json.loads((proyecto / "interui.json").read_text(encoding="utf-8"))
    assert data["app"]["name"] == "mi_tienda"
    assert data["app"]["title"] == "Mi Tienda — Gestión"
    assert data["app"]["theme"] == "dark"
    assert data["databases"]["default"]["name"] == "data/tienda.db"
    assert (proyecto / "data" / "tienda.db").is_file(), "no creó la base de datos"
    assert not list((proyecto / "migrations").glob("0*.json"))
    assert any("Nombre largo" in pregunta for pregunta in preguntas)


def test_startproject_con_nombre_solo_pregunta_lo_que_falta(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    preguntas = _respuestas(
        monkeypatch,
        [
            "Agenda",           # nombre largo (acepta el valor propuesto)
            ".",                # carpeta
            "1",                # sqlite
            "data/agenda.db",   # ruta
            "light",            # tema
            "n",                # sin migración
        ],
    )
    assert cli.main(["startproject", "agenda"]) == 0
    assert not any("Nombre del proyecto" in pregunta for pregunta in preguntas)
    assert (tmp_path / "agenda" / "main.py").is_file()
    assert not list((tmp_path / "agenda" / "migrations").glob("0*.json"))


def test_startproject_respeta_los_parametros_de_la_linea(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _respuestas(monkeypatch, ["", ".", "light", "n"])  # solo título, carpeta, tema, migrar
    code = cli.main(["startproject", "agenda", "--db", "sqlite", "--database", "data/x.db"])
    assert code == 0
    data = json.loads((tmp_path / "agenda" / "interui.json").read_text(encoding="utf-8"))
    assert data["databases"]["default"]["name"] == "data/x.db"


def test_startproject_sin_nombre_y_sin_terminal_avisa(tmp_path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.sys, "stdin", io.StringIO("no soy una terminal"))
    assert cli.main(["startproject"]) == 1
    assert "falta el nombre del proyecto" in capsys.readouterr().err


def test_startproject_no_input_no_pregunta(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cli.sys, "stdin", _TTY())
    assert cli.main(["startproject", "notas", "--no-input"]) == 0
    data = json.loads((tmp_path / "notas" / "interui.json").read_text(encoding="utf-8"))
    assert data["app"]["theme"] == "light"
    assert data["databases"]["default"]["engine"] == "sqlite"


def test_init_tambien_pregunta_el_nombre_largo(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    _respuestas(
        monkeypatch,
        [
            "Agenda",               # nombre corto
            "Agenda de Contactos",  # nombre largo
            "1",                    # sqlite
            "data/agenda.db",       # ruta
            "light",                # tema
            "n",                    # sin migración
        ],
    )
    assert cli.main(["init", "."]) == 0
    data = json.loads((tmp_path / "interui.json").read_text(encoding="utf-8"))
    assert data["app"]["name"] == "Agenda"
    assert data["app"]["title"] == "Agenda de Contactos"
    assert data["databases"]["default"]["name"] == "data/agenda.db"


def test_el_proyecto_sin_apps_muestra_la_bienvenida(proyecto: pathlib.Path, monkeypatch) -> None:
    """Sin vistas propias, el framework pone la página `/` con una pista."""
    monkeypatch.syspath_prepend(str(proyecto))
    _fresh_modules("tienda")

    from tienda.app import create_app

    app = create_app()
    assert app.has_page("/")
    title, html, _bindings = app.render_page("/")
    assert "Hola mundo" in html
    assert "startapp" in html, "la bienvenida dice cómo empezar"

    # Cuando hay apps, la pista lista sus páginas.
    monkeypatch.chdir(proyecto)
    assert cli.main(["startapp", "clientes"]) == 0
    _fresh_modules("tienda", "clientes")
    from tienda.app import create_app as crear

    html = crear().render_page("/")[1]
    assert "/clientes" in html
