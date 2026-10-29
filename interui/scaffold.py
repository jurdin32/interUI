"""Estructura de un proyecto de escritorio: paquete, apps y migraciones.

`iui startproject tienda` crea::

    tienda/
    ├── main.py             ← punto de entrada: crea la app y abre la ventana
    ├── iui.py              ← comandos del proyecto
    ├── interui.json        ← configuración
    ├── requirements.txt
    ├── README.md
    ├── .gitignore
    ├── tienda/             ← el paquete del proyecto
    │   ├── __init__.py
    │   └── app.py          ← configuración: crea la App y el armazón
    ├── <app>/              ← apps del proyecto (`iui startapp`): modelos y vistas
    ├── migrations/         ← migraciones generadas
    └── data/               ← SQLite / archivos (se crea al migrar)

Todo es de escritorio: no hay servidor web ni pasos de despliegue.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from .config import CONFIG_NAME, DEFAULT_CONFIG, ENGINES

__all__ = ["create_app_module", "create_project", "model_name", "package_name"]


def package_name(raw: str) -> str:
    """``Mi Tienda`` / ``mi-tienda`` → ``mi_tienda`` (identificador válido)."""
    text = unicodedata.normalize("NFKD", str(raw)).encode("ascii", "ignore").decode()
    text = re.sub(r"[^0-9a-zA-Z]+", "_", text).strip("_").lower()
    if not text:
        text = "proyecto"
    if text[0].isdigit():
        text = f"app_{text}"
    return text


IUI_PY = '''#!/usr/bin/env python
"""Comandos de {name}.

    python iui.py run              abre la ventana de escritorio
    python iui.py startapp tareas  crea una app dentro del proyecto
    python iui.py makemigrations   genera la migración de los modelos
    python iui.py migrate          aplica las migraciones pendientes
    python iui.py status           estado de las migraciones
    python iui.py shell            consola con los modelos cargados
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from interui.cli import project_main

if __name__ == "__main__":
    raise SystemExit(project_main())
'''

INIT_PY = '''"""{name}: aplicación de escritorio con interUI."""

__version__ = "0.1.0"
'''

APP_PY = '''"""Configuración de la ventana.

Aquí se crea la `App` con lo que dice `interui.json`. El proyecto **no** tiene
modelos ni vistas: cada app (`python iui.py startapp <app>`) trae los suyos y
sus rutas se registran solas.
"""

from pathlib import Path

import interui as ui

#: `interui.json` vive un nivel por encima del paquete.
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = BASE_DIR / "interui.json"


def create_app() -> ui.App:
    """`App` del proyecto, con las rutas de todas sus apps.

    El armazón de la ventana (barra de título, menú, barra de estado) se pone
    aquí, una sola vez, con `app.layout = ui.AppShell(...)`. Las vistas solo
    devuelven su contenido.
    """
    return ui.App.from_config(CONFIG)


app = create_app()
'''

MAIN_PY = '''#!/usr/bin/env python
"""Punto de entrada de {name}.

Aquí se crea todo: la configuración, la base de datos (migraciones pendientes)
y la ventana nativa. Los comandos de mantenimiento viven en `iui.py`.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from interui import config as config_module
from interui import db as db_module
from interui import migrations as migrations_module

from {pkg}.app import create_app

CONFIG = BASE_DIR / "interui.json"


def prepare_database() -> None:
    """Aplica las migraciones pendientes antes de abrir la ventana."""
    settings = config_module.load(CONFIG)
    db_module.configure(settings)
    try:
        migrations_module.migrate(settings)
    except db_module.DatabaseError as exc:
        # La ventana debe abrirse igual: las vistas avisan de que falta migrar.
        print(f"[interui] no se pudieron aplicar las migraciones: {exc}")


def main() -> None:
    """Crea la aplicación y abre la ventana de escritorio."""
    prepare_database()
    create_app().run()


if __name__ == "__main__":
    main()
'''

README = """# {name}

Aplicación de escritorio creada con **interUI** (Python + Tailwind, sin navegador).

## Arrancar

```bash
pip install -r requirements.txt
python main.py
```

La ventana abre con «Hola mundo» centrado. En cuanto crees una app, su página
sustituye esa bienvenida.

`main.py` aplica las migraciones pendientes y abre la ventana nativa. Los
comandos que no abren ventana (`startapp`, `makemigrations`, `migrate`,
`status`, `shell`, `check`) están en `iui.py`.

## Estructura

| Archivo | Para qué |
|---|---|
| `main.py` | punto de entrada: crea la app y abre la ventana. |
| `iui.py` | comandos del proyecto (`startapp`, `makemigrations`, `migrate`, `status`, `shell`, `run`). |
| `interui.json` | configuración: nombre, ventana, base de datos, apps y migraciones. |
| `{pkg}/app.py` | crea la `App` (configuración; aquí se pone el armazón de la ventana). |
| `migrations/` | migraciones generadas. |
| `data/` | base SQLite o archivos (se crea al migrar). |

El proyecto no trae modelos ni vistas: van en las **apps**, una por dominio.

## Tu primera app

```bash
python iui.py startapp tareas
python iui.py makemigrations
python iui.py migrate
python main.py
```

Crea `tareas/` con `models.py`, `forms.py`, `views.py` y `urls.py` **listos para
usar**: la página `/tareas` trae formulario de alta, validación y tabla con lo
guardado. Además la declara en `apps` de `interui.json`: sus rutas se registran
solas.

## Añadir un menú a la ventana

El armazón se escribe una vez en `{pkg}/app.py` y envuelve todas las páginas:

```python
def salir() -> None:
    ui.current_app().quit()


def create_app() -> ui.App:
    app = ui.App.from_config(CONFIG)
    app.layout = ui.AppShell(
        title_bar=ui.TitleBar("{name}", icon=ui.icons.layers),
        header=ui.MenuBar(
            {"Archivo": [ui.ContextItem("Salir", icon=ui.icons.power, on_click=salir)]},
            icons={"Archivo": ui.icons.folder},
        ),
        status=ui.StatusBar(ui.text("Listo")),
    )
    return app
```
"""

REQUIREMENTS = """# interUI todavía no está en PyPI: se instala desde GitHub.
interui[desktop] @ git+https://github.com/jurdin32/interUI
"""


def _render(template: str, name: str, pkg: str) -> str:
    """Sustituye los huecos sin pelear con las llaves del propio código."""
    return template.replace("{pkg}", pkg).replace("{name}", name)


def _config(
    name: str,
    pkg: str,
    engine: str,
    settings: dict[str, Any],
    *,
    title: str | None = None,
    theme: str = "light",
) -> dict[str, Any]:
    data = json.loads(json.dumps(DEFAULT_CONFIG))
    data["app"].update(
        {
            "name": name,
            "title": title or name,
            "version": "0.1.0",
            "theme": theme,
            "entry": f"{pkg}.app",
        }
    )
    data["databases"] = {"default": {"engine": engine, **settings}}
    data["migrations"] = {"directory": "migrations", "models": []}
    return data


def create_project(
    target: Path,
    name: str | None = None,
    *,
    engine: str = "sqlite",
    settings: dict[str, Any] | None = None,
    force: bool = False,
    title: str | None = None,
    theme: str = "light",
) -> list[Path]:
    """Crea la estructura completa en ``target`` y devuelve los archivos escritos.

    ``title`` es el nombre largo que se ve en la ventana y en los textos; si no
    se indica se usa ``name``.
    """
    target = Path(target).expanduser().resolve()
    if engine not in ENGINES:
        raise ValueError(f"motor desconocido {engine!r}; usa {', '.join(sorted(ENGINES))}")
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(f"{target} no está vacío (usa --force para continuar)")

    display = (title or name or target.name).strip() or target.name
    pkg = package_name(name or display)
    defaults = dict(ENGINES[engine]["defaults"])
    defaults.update(settings or {})

    files: dict[Path, str] = {
        target / "main.py": _render(MAIN_PY, display, pkg),
        target / "iui.py": _render(IUI_PY, display, pkg),
        target / "interui.json": json.dumps(
            _config(name or display, pkg, engine, defaults, title=display, theme=theme),
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        target / "requirements.txt": REQUIREMENTS,
        target / "README.md": _render(README, display, pkg),
        target / ".gitignore": "__pycache__/\n*.py[cod]\ndata/\nbuild/\ndist/\n*.spec\n.env\n",
        target / pkg / "__init__.py": _render(INIT_PY, display, pkg),
        target / pkg / "app.py": _render(APP_PY, display, pkg),
        target / "migrations" / ".gitkeep": "",
        target / "data" / ".gitkeep": "",
    }

    written: list[Path] = []
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


# ---------------------------------------------------------------------------
# startapp: una app dentro del proyecto
# ---------------------------------------------------------------------------
APP_INIT_PY = '''"""{app}: una app del proyecto {project}."""

__version__ = "0.1.0"
'''

APP_MODELS_PY = '''"""Modelos de {app}.

`python iui.py makemigrations` compara este archivo con la última migración y
`python iui.py migrate` aplica los cambios a la base de datos.
"""

import interui as ui


class {Model}(ui.Model):
    nombre = ui.Str(max_length=120)
    descripcion = ui.LongText(null=True)
    activo = ui.Bool(default=True)
    creado = ui.DateTime(auto_now_add=True)

    class Meta:
        table = "{table}"
        order = ["nombre"]
'''

APP_FORMS_PY = '''"""Formularios de la app {app}.

Aquí se declaran; la vista solo los usa (`from {app}.forms import {Model}Form`).
"""

import interui as ui

from {app}.models import {Model}


class {Model}Form(ui.ModelForm):
    """Alta de {Model}: cada campo del modelo se convierte en su control.

    Este archivo manda sobre el formulario **y** sobre la tabla de la vista:
    `fields` decide qué campos salen y en qué orden, y `labels` cómo se llaman.
    """

    model = {Model}
    # fields = ["nombre", "descripcion"]      # solo estos, en este orden
    # exclude = ["activo"]                    # todos menos estos
    # labels = {"nombre": "Nombre completo"}  # el nombre que se muestra
    title = "Nuevo registro"
'''

APP_VIEWS_PY = '''"""Vistas de {app}."""

import interui as ui

from {app}.forms import {Model}Form


def inicio() -> ui.Component:
    """Título, contador, formulario y tabla; el armazón lo pone `app.layout`."""
    return ui.RecordPage({Model}Form(), title="{App}")
'''

APP_URLS_PY = '''"""Rutas de la app {app}.

No hay que registrarlas a mano: «{app}» está en `apps` de interui.json y
`App.from_config()` conecta este `urlpatterns` al arrancar.
"""

from typing import Any, Callable

from {app} import views

URLPattern = tuple[str, Callable[..., Any], str]

urlpatterns: list[URLPattern] = [
    ("/{app}", views.inicio, "{app}"),
]


def register(app: Any) -> None:
    """Conecta las rutas de la app con la aplicación."""
    for path, view, title in urlpatterns:
        app.page(path, title=title)(view)
'''

APP_README = """# {app}

App del proyecto **{project}**, creada con `iui startapp` y **lista para usar**.

| Archivo | Para qué |
|---|---|
| `models.py` | modelo `{Model}` (tabla `{table}`); lo migra `python iui.py migrate`. |
| `forms.py` | formulario `{Model}Form`, generado a partir del modelo. |
| `views.py` | la página: el formulario y la tabla de lo guardado. |
| `urls.py` | la ruta `/{app}`. |

## Probarlo

```bash
python iui.py makemigrations
python iui.py migrate
python main.py          # abre la ventana; la app está en /{app}
```

Ya está declarada en `apps` de `interui.json`, así que sus rutas se registran
solas. Las migraciones son del proyecto (`migrations/`), para que un solo
`migrate` ponga al día todas las apps.

## Cambiarla

- Campos del modelo: `models.py` y vuelve a migrar; el formulario y la tabla se
  adaptan solos.
- Campos del formulario: `fields` o `exclude` en `forms.py` (sin nada, salen
  todos los del modelo).
- Qué se ve: `views.py`.
"""


def _write_files(files: dict[Path, str], force: bool) -> list[Path]:
    written: list[Path] = []
    for path, content in files.items():
        if path.exists() and not force:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written


def register_app(config_path: Path, package: str) -> Path:
    """Añade la app a ``apps`` y sus modelos a ``migrations.models``."""
    data = json.loads(Path(config_path).read_text(encoding="utf-8"))
    apps = data.setdefault("apps", [])
    if not isinstance(apps, list):
        raise ValueError("«apps» en interui.json debe ser una lista")
    if package not in apps:
        apps.append(package)

    migrations = data.setdefault("migrations", {})
    models = migrations.get("models", "models.py")
    models = [models] if isinstance(models, str) else list(models)
    relative = f"{package}/models.py"
    if relative not in models:
        models.append(relative)
    migrations["models"] = models

    Path(config_path).write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return Path(config_path)


def model_name(name: str) -> str:
    """``personas`` → ``Persona``: nombre de clase del modelo de una app nueva."""
    base = package_name(name)
    if len(base) > 3 and base.endswith("s") and base[-2] in "aeiou":
        base = base[:-1]
    return "".join(part[:1].upper() + part[1:] for part in base.split("_"))


def create_app_module(root: Path, name: str, *, force: bool = False) -> list[Path]:
    """Crea una app dentro del proyecto.

    Devuelve los archivos escritos. Falla si ``root`` no tiene ``interui.json``:
    primero va el proyecto (``iui startproject``) y después sus apps.
    """
    root = Path(root).expanduser().resolve()
    config_path = root / CONFIG_NAME
    if not config_path.is_file():
        raise FileNotFoundError(
            f"No existe {config_path}. `startapp` crea apps dentro de un proyecto: "
            "usa antes `iui startproject <nombre>`."
        )

    package = package_name(name)
    folder = root / package
    if folder.exists() and any(folder.iterdir()) and not force:
        raise FileExistsError(f"{folder} no está vacío (usa --force para continuar)")

    data = json.loads(config_path.read_text(encoding="utf-8"))
    project = str((data.get("app") or {}).get("name") or root.name)
    model = model_name(package)
    values = {
        "app": package,
        "App": package.replace("_", " ").capitalize(),
        "project": project,
        "Model": model,
        "model_lower": model.lower(),
        "table": f"{package}_{model.lower()}s",
    }

    files: dict[Path, str] = {
        folder / "__init__.py": _fill(APP_INIT_PY, **values),
        folder / "models.py": _fill(APP_MODELS_PY, **values),
        folder / "forms.py": _fill(APP_FORMS_PY, **values),
        folder / "views.py": _fill(APP_VIEWS_PY, **values),
        folder / "urls.py": _fill(APP_URLS_PY, **values),
        folder / "README.md": _fill(APP_README, **values),
    }
    written = _write_files(files, force)
    register_app(config_path, package)
    return written


def _fill(template: str, **values: str) -> str:
    """Sustituye ``{clave}`` en las plantillas de ``startapp``."""
    out = template
    for key, value in values.items():
        out = out.replace("{" + key + "}", value)
    return out
