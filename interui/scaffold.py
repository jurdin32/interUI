"""Estructura de proyecto al estilo de Django para apps de escritorio.

`iui startproject tienda` crea::

    tienda/
    ├── iui.py              ← comandos (como manage.py)
    ├── interui.json        ← configuración (como settings.py)
    ├── requirements.txt
    ├── README.md
    ├── .gitignore
    ├── tienda/             ← el paquete del proyecto
    │   ├── __init__.py
    │   ├── app.py          ← crea la App y registra las rutas
    │   ├── urls.py         ← qué vista responde a cada ruta
    │   ├── views.py        ← las páginas
    │   ├── layout.py       ← armazón compartido (menú, estado)
    │   └── models.py       ← modelos del ORM
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

from .config import DEFAULT_CONFIG, ENGINES

__all__ = ["create_project", "package_name"]


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

APP_PY = '''"""La ventana de la aplicación.

Equivale a `settings.py` de Django: aquí se crea la `App` con lo que dice
`interui.json` y se registran las rutas de `urls.py`.
"""

from pathlib import Path

import interui as ui

from {pkg} import urls

#: `interui.json` vive un nivel por encima del paquete (como BASE_DIR en Django).
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = BASE_DIR / "interui.json"


def create_app() -> ui.App:
    """`App` del proyecto, con todas las páginas ya registradas."""
    app = ui.App.from_config(CONFIG)
    urls.register(app)
    return app


app = create_app()
'''

URLS_PY = '''"""Rutas del proyecto, como `urls.py` de Django.

Cada entrada es `(ruta, vista, título de la ventana)`. Para parámetros usa
`"/tarea/<int:id>"` y la vista recibirá la función `tarea(id=1)`.
"""

from typing import Any, Callable

from {pkg} import views

URLPattern = tuple[str, Callable[..., Any], str]

urlpatterns: list[URLPattern] = [
    ("/", views.inicio, "Inicio"),
    ("/tareas", views.tareas, "Tareas"),
]


def register(app: Any) -> None:
    """Conecta `urlpatterns` con la aplicación."""
    for path, view, title in urlpatterns:
        app.page(path, title=title)(view)
'''

LAYOUT_PY = '''"""Armazón compartido: barra de título, menú lateral y barra de estado."""

from typing import Any

import interui as ui

MENU = (
    ("Inicio", ui.icons.home, "/"),
    ("Tareas", ui.icons.check, "/tareas"),
)


def sidebar() -> ui.Sidebar:
    """Menú lateral; cada entrada navega sin recargar la ventana."""
    barra = ui.Sidebar(title="Navegación")
    for label, icon, path in MENU:
        barra.add = ui.SidebarItem(
            label,
            icon=icon,
            active=path == "/tareas",
            data={"iui-link": path},
            class_="cursor-pointer",
        )
    return barra


def frame(*content: Any, title: str = "{name}") -> ui.AppShell:
    """Envuelve el contenido de una vista en el armazón de la app."""
    shell = ui.AppShell()
    shell.title_bar = ui.TitleBar(title, icon=ui.icons.layers)
    shell.header = ui.MenuBar({"Archivo": [_salir()]}, brand=title)
    shell.sidebar = sidebar()
    shell.status = ui.StatusBar(ui.text("Listo"))
    shell.add = ui.Container(pad=ui.pad.p_4, md_pad=ui.pad.p_8)(*content)
    return shell


def _salir() -> ui.ContextItem:
    """Cierra la ventana; `app.exit()` cerraría también el proceso."""

    def cerrar() -> None:
        from {pkg}.app import app

        app.close()

    return ui.ContextItem("Salir", icon=ui.icons.power, on_click=cerrar)
'''

VIEWS_PY = '''"""Vistas: cada función devuelve la página que se pinta en la ventana."""

import interui as ui

from {pkg} import layout
from {pkg}.models import Tarea

SIN_BASE = (
    "Falta la base de datos. Ejecuta `python iui.py migrate` y vuelve a abrir la ventana."
)


def _hay_tabla() -> bool:
    """¿Ya se aplicaron las migraciones? Evita un error en el primer arranque."""
    try:
        Tarea.objects.exists()
    except ui.db.DatabaseError:
        return False
    return True


def _avisos() -> ui.Component | None:
    if _hay_tabla():
        return None
    return ui.Alert(SIN_BASE, title="Sin base de datos", level=ui.tone.warning,
                    margin=ui.margin.t_6)


def inicio() -> ui.Component:
    total = Tarea.objects.count() if _hay_tabla() else 0
    pendientes = Tarea.objects.filter(hecha=False).count() if _hay_tabla() else 0
    hechas = Tarea.objects.filter(hecha=True).count() if _hay_tabla() else 0
    return layout.frame(
        ui.Heading("Hola desde {name}", level=1),
        ui.Muted("Aplicación de escritorio: se abre en su propia ventana, sin navegador."),
        _avisos(),
        ui.Row(gap=ui.gap.all_3, margin=ui.margin.t_6)(
            ui.Col(span=12, md=4)(
                ui.Stat("Tareas", total, icon=ui.icons.check),
            ),
            ui.Col(span=12, md=4)(
                ui.Stat("Pendientes", pendientes, icon=ui.icons.clock),
            ),
            ui.Col(span=12, md=4)(
                ui.Stat("Hechas", hechas, icon=ui.icons.check),
            ),
        ),
        ui.Alert(
            "Edita views.py y guarda: la ventana se vuelve a pintar sola.",
            level=ui.tone.info,
            margin=ui.margin.t_6,
        ),
    )


def tareas() -> ui.Component:
    filas = [
        [
            ui.Text(tarea.titulo),
            ui.Badge("hecha" if tarea.hecha else "pendiente"),
            ui.IconButton(
                ui.icons.trash,
                label="Borrar",
                variant=ui.variant.ghost,
                on_click=lambda pk=tarea.pk: _borrar(pk),
            ),
        ]
        for tarea in (Tarea.objects.all() if _hay_tabla() else [])
    ]
    return layout.frame(
        ui.Heading("Tareas", level=1),
        _avisos(),
        ui.Button("Nueva tarea", icon=ui.icons.plus, on_click=_nueva, margin=ui.margin.t_4),
        ui.Card(pad=ui.pad.all_2, margin=ui.margin.t_4)(
            ui.Table(
                headers=["Título", "Estado", ""],
                rows=filas,
                empty="Todavía no hay tareas",
                hover=True,
            )
        ),
        title="Tareas · {name}",
    )


def _nueva() -> None:
    ui.dialog.input("Título de la tarea", title="Nueva tarea", on_accept=_crear)


def _crear(evento) -> None:
    titulo = str(getattr(evento, "value", "") or "").strip()
    if not titulo:
        ui.toast("Escribe un título", "warning", icon=ui.icons.alert)
        return
    Tarea.objects.create(titulo=titulo)
    ui.toast(f"«{titulo}» añadida", "success", title="Guardado", icon=ui.icons.check)
    _app().navigate("/tareas")


def _borrar(pk: int) -> None:
    Tarea.objects.filter(pk=pk).delete()
    ui.toast("Tarea eliminada", "info", icon=ui.icons.trash)
    _app().navigate("/tareas")


def _app():
    """La `App` del proyecto, importada al vuelo para evitar ciclos."""
    from {pkg}.app import app

    return app
'''

MODELS_PY = '''"""Modelos del ORM.

`python iui.py makemigrations` compara este archivo con la última migración y
`python iui.py migrate` aplica los cambios a la base.
"""

import interui as ui


class Tarea(ui.Model):
    titulo = ui.Str(max_length=120)
    hecha = ui.Bool(default=False)
    creada = ui.DateTime(auto_now_add=True)

    class Meta:
        table = "tareas"
        order = ["-creada"]
'''

README = """# {name}

Aplicación de escritorio creada con **interUI** (Python + Tailwind, sin navegador).

## Arrancar

```bash
pip install -r requirements.txt
python iui.py makemigrations
python iui.py migrate
python iui.py run
```

## Estructura

| Archivo | Para qué |
|---|---|
| `iui.py` | comandos del proyecto (`run`, `makemigrations`, `migrate`, `status`, `shell`). |
| `interui.json` | configuración: nombre, tamaño de la ventana, base de datos, migraciones. |
| `{pkg}/app.py` | crea la `App` y registra las rutas. |
| `{pkg}/urls.py` | qué vista responde a cada ruta. |
| `{pkg}/views.py` | las páginas, en Python con componentes. |
| `{pkg}/layout.py` | armazón compartido: menú lateral, título y estado. |
| `{pkg}/models.py` | modelos del ORM (se convierten en tablas con las migraciones). |
| `migrations/` | migraciones generadas. |
| `data/` | base SQLite o archivos (se crea al migrar). |

## Añadir una página

1. Escribe la vista en `{pkg}/views.py`.
2. Añádela a `urlpatterns` en `{pkg}/urls.py`.

```python
("\\"/ajustes\\"", views.ajustes, "Ajustes"),
```
"""

REQUIREMENTS = """# interUI todavía no está en PyPI: se instala desde GitHub.
interui[desktop] @ git+https://github.com/jurdin32/interUI
"""


def _render(template: str, name: str, pkg: str) -> str:
    """Sustituye los huecos sin pelear con las llaves del propio código."""
    return template.replace("{pkg}", pkg).replace("{name}", name)


def _config(name: str, pkg: str, engine: str, settings: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(json.dumps(DEFAULT_CONFIG))
    data["app"].update(
        {
            "name": name,
            "title": name,
            "version": "0.1.0",
            "theme": "light",
            "entry": f"{pkg}.app",
        }
    )
    data["databases"] = {"default": {"engine": engine, **settings}}
    data["migrations"] = {"directory": "migrations", "models": f"{pkg}/models.py"}
    return data


def create_project(
    target: Path,
    name: str | None = None,
    *,
    engine: str = "sqlite",
    settings: dict[str, Any] | None = None,
    force: bool = False,
) -> list[Path]:
    """Crea la estructura completa en ``target`` y devuelve los archivos escritos."""
    target = Path(target).expanduser().resolve()
    if engine not in ENGINES:
        raise ValueError(f"motor desconocido {engine!r}; usa {', '.join(sorted(ENGINES))}")
    if target.exists() and any(target.iterdir()) and not force:
        raise FileExistsError(f"{target} no está vacío (usa --force para continuar)")

    title = name or target.name
    pkg = package_name(title)
    defaults = dict(ENGINES[engine]["defaults"])
    defaults.update(settings or {})

    files: dict[Path, str] = {
        target / "iui.py": _render(IUI_PY, title, pkg),
        target / "interui.json": json.dumps(
            _config(title, pkg, engine, defaults), ensure_ascii=False, indent=2
        )
        + "\n",
        target / "requirements.txt": REQUIREMENTS,
        target / "README.md": _render(README, title, pkg),
        target / ".gitignore": "__pycache__/\n*.py[cod]\ndata/\nbuild/\ndist/\n*.spec\n.env\n",
        target / pkg / "__init__.py": _render(INIT_PY, title, pkg),
        target / pkg / "app.py": _render(APP_PY, title, pkg),
        target / pkg / "urls.py": _render(URLS_PY, title, pkg),
        target / pkg / "views.py": _render(VIEWS_PY, title, pkg),
        target / pkg / "layout.py": _render(LAYOUT_PY, title, pkg),
        target / pkg / "models.py": MODELS_PY,
        target / "migrations" / ".gitkeep": "",
        target / "data" / ".gitkeep": "",
    }

    written: list[Path] = []
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        written.append(path)
    return written
