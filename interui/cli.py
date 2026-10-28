"""CLI de interui: `interui init | run | new | db | build | doctor | assets`."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Sequence

__all__ = ["main"]

PACKAGE_DIR = Path(__file__).resolve().parent
STATIC_DIR = PACKAGE_DIR / "static"
TEMPLATE = '''"""{name} · aplicación de escritorio con interUI."""

from interui import button, state, text, title, toast, window

count = state(0)


def saludar() -> None:
    toast(f"¡Hola! Llevas {{count.get()}} pulsaciones", "success")


window(
    "{name}",
    title("{name}", subtitle="Edita app.py y guarda: la ventana se recompone sola."),
    text("Pulsaciones: ", count),
    button("Pulsar", icon="plus", on_click=count.inc),
    button("Saludar", variant="soft", icon="send", on_click=saludar),
).run()
'''


def _load_app(script: Path) -> Any:
    """Importa un archivo de Python y devuelve su objeto ``App``."""
    from .app import App

    script = script.expanduser().resolve()
    if not script.is_file():
        raise SystemExit(f"interui: no existe el archivo {script}")

    sys.path.insert(0, str(script.parent))
    spec = importlib.util.spec_from_file_location(script.stem, script)
    if spec is None or spec.loader is None:
        raise SystemExit(f"interui: no se pudo cargar {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    for value in vars(module).values():
        if isinstance(value, App):
            return value
    raise SystemExit(
        f"interui: {script.name} no define ninguna instancia de App "
        "(por ejemplo: app = interui.App('Mi app'))."
    )


def _npm() -> str | None:
    return shutil.which("npm")


def _frontend_dir() -> Path | None:
    candidates = [
        PACKAGE_DIR.parent / "frontend",
        Path.cwd() / "frontend",
    ]
    for candidate in candidates:
        if (candidate / "package.json").is_file():
            return candidate
    return None


# ---------------------------------------------------------------------------
# comandos
# ---------------------------------------------------------------------------
def cmd_run(args: argparse.Namespace) -> int:
    app = _load_app(Path(args.script))
    if args.title:
        app.title = args.title
    if args.width:
        app.width = args.width
    if args.height:
        app.height = args.height
    if args.theme:
        app.theme = args.theme
    app.verbose = args.verbose or app.verbose
    app.run(
        window=args.window,
        port=args.port,
        host=args.host,
        debug=args.debug,
    )
    return 0


def cmd_new(args: argparse.Namespace) -> int:
    target = Path(args.destination).expanduser().resolve()
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"interui: {target} no está vacío")
    target.mkdir(parents=True, exist_ok=True)
    (target / "app.py").write_text(TEMPLATE.format(name=args.name), encoding="utf-8")
    (target / "README.md").write_text(
        f"# {args.name}\n\n"
        "Aplicación de escritorio creada con **interui**.\n\n"
        "```bash\n"
        'pip install "interui[desktop]"\n'
        "python app.py\n"
        "```\n\n"
        "Empaquetado en un ejecutable autónomo:\n\n"
        "```bash\n"
        f"interui build app.py --name {args.name}\n"
        "```\n",
        encoding="utf-8",
    )
    (target / ".gitignore").write_text("__pycache__/\nbuild/\ndist/\n*.spec\n", encoding="utf-8")
    print(f"[interui] proyecto creado en {target}")
    print(f"[interui] siguiente paso: cd {target.name} && python app.py")
    return 0


MODELS_TEMPLATE = '''"""Modelos del proyecto.

`interui db makemigrations` compara este archivo con la última migración y
genera los cambios; `interui db migrate` los aplica.
"""

import interui as ui


class Ejemplo(ui.Model):
    nombre = ui.Str(max_length=80)
    notas = ui.LongText(null=True)
    activo = ui.Bool(default=True)
    creado = ui.DateTime(auto_now_add=True)

    class Meta:
        table = "ejemplo"
'''

APP_TEMPLATE = '''"""{name} · aplicación de escritorio con interUI."""

import interui as ui

app = ui.App.from_config()


@app.page("/")
def index():
    return ui.Screen(
        ui.Container(pad=ui.pad.py_10)(
            ui.Heading("{name}", level=1),
            ui.Muted("Configuración leída de interui.json"),
            ui.Button("Salir", icon=ui.icons.power, on_click=app.exit),
        )
    )


if __name__ == "__main__":
    app.run()
'''


def _ask(question: str, default: Any = None, *, input_fn: Any = input) -> str:
    suffix = f" [{default}]" if default not in (None, "") else ""
    try:
        answer = str(input_fn(f"{question}{suffix}: ")).strip()
    except (EOFError, KeyboardInterrupt):
        answer = ""
    return answer or (str(default) if default is not None else "")


def _choose_engine(engines: dict[str, Any], input_fn: Any = input) -> str:
    names = list(engines)
    print("\nMotor de base de datos:")
    for index, name in enumerate(names, start=1):
        print(f"  {index}. {engines[name]['label']}")
    answer = _ask("Elige un número", "1", input_fn=input_fn)
    if answer.isdigit() and 1 <= int(answer) <= len(names):
        return names[int(answer) - 1]
    return answer if answer in engines else "sqlite"


def cmd_init(args: argparse.Namespace) -> int:
    """Asistente: crea interui.json, app.py, models.py y migrations/."""
    from .config import CONFIG_NAME, DEFAULT_CONFIG, ENGINES, Config

    target = Path(args.destination or ".").expanduser().resolve()
    if target.exists() and any(target.iterdir()) and not args.force:
        raise SystemExit(f"interui: {target} no está vacío (usa --force para continuar)")
    target.mkdir(parents=True, exist_ok=True)
    ask = (lambda question, default=None: str(default if default is not None else "")) \
        if args.no_input else _ask

    name = args.name or ask("Nombre de la aplicación", target.name or "Mi app")
    engine = args.db or ("sqlite" if args.no_input else _choose_engine(ENGINES))
    if engine not in ENGINES:
        raise SystemExit(f"interui: motor desconocido {engine!r}; usa {', '.join(ENGINES)}")

    settings: dict[str, Any] = {"engine": engine}
    defaults = ENGINES[engine]["defaults"]
    flag_values = {
        "name": args.database, "host": args.host, "port": args.port,
        "user": args.user, "password": args.password,
    }
    for field_name in ENGINES[engine]["fields"]:
        value = flag_values.get(field_name)
        if value is None:
            value = ask(f"  {field_name}", defaults.get(field_name, ""))
        if field_name == "port" and isinstance(value, str) and value.isdigit():
            value = int(value)
        settings[field_name] = value

    data = json.loads(json.dumps(DEFAULT_CONFIG))
    data["app"].update(
        {
            "name": name,
            "title": args.title or name,
            "theme": args.theme or "light",
            "entry": "app.py",
        }
    )
    data["databases"] = {"default": settings}
    config = Config(data, path=target / "interui.json")
    config.save()

    (target / "app.py").write_text(APP_TEMPLATE.format(name=name), encoding="utf-8")
    models = target / "models.py"
    if not models.exists() or args.force:
        models.write_text(MODELS_TEMPLATE, encoding="utf-8")
    (target / "migrations").mkdir(exist_ok=True)
    (target / "migrations" / ".gitkeep").write_text("", encoding="utf-8")
    (target / ".gitignore").write_text(
        "__pycache__/\nbuild/\ndist/\n*.spec\ndata/\n.env\n", encoding="utf-8"
    )
    (target / "README.md").write_text(
        f"# {name}\n\n"
        "Proyecto interUI con configuración en `interui.json`.\n\n"
        "```bash\n"
        'pip install "interui[desktop]"\n'
        "interui db makemigrations\n"
        "interui db migrate\n"
        "python app.py\n"
        "```\n\n"
        f"Base de datos: `{settings['engine']}`.\n",
        encoding="utf-8",
    )

    print(f"[interui] proyecto creado en {target}")
    print(f"[interui] configuración: {target / 'interui.json'}")
    if args.migrate:
        location = str(target / CONFIG_NAME)
        code = cmd_db(
            argparse.Namespace(action="makemigrations", name=None, force=True, config=location)
        )
        if code:
            return code
        return cmd_db(
            argparse.Namespace(action="migrate", name=None, force=False, config=location)
        )
    print("[interui] siguiente paso: interui db makemigrations && interui db migrate")
    return 0


def cmd_db(args: argparse.Namespace) -> int:
    """Migraciones: ``makemigrations``, ``migrate`` y ``status``."""
    from . import config as config_module
    from . import db as db_module
    from . import migrations as migrations_module
    from .config import ConfigError

    try:
        cfg = config_module.load(getattr(args, "config", None))
        db_module.configure(cfg)
        if args.action == "makemigrations":
            path = migrations_module.makemigrations(
                cfg, getattr(args, "name", None), allow_destructive=getattr(args, "force", False)
            )
            if path is None:
                print("[interui] no hay cambios en los modelos")
            else:
                print(f"[interui] migración creada: {path}")
        elif args.action == "migrate":
            applied = migrations_module.migrate(cfg)
            if applied:
                for name in applied:
                    print(f"[interui] aplicada {name}")
            else:
                print("[interui] nada pendiente")
        else:
            rows = migrations_module.status(cfg)
            if not rows:
                print("[interui] no hay migraciones todavía")
            for row in rows:
                mark = "✔" if row["applied"] else "·"
                print(f" {mark} {row['name']}")
                for detail in row["operations"]:
                    print(f"     - {detail}")
    except (ConfigError, db_module.DatabaseError) as exc:
        print(f"[interui] {exc}", file=sys.stderr)
        return 1
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    from . import updates

    info = updates.check(force=True, timeout=getattr(args, "timeout", 5.0))
    origin, command = updates.install_info()
    print(f"interui {updates.current_version()} (instalado desde {origin})")
    if info is None:
        print("No se pudo consultar la última versión (¿sin conexión?).")
        print(f"Actualiza manualmente con:\n  {command}")
        return 1
    if info.available:
        print(f"Hay una versión nueva: {info.latest}")
        print(f"Actualiza con:\n  {info.command}")
    else:
        print(f"Estás al día (última publicada: {info.latest}).")
        print(f"Para forzar la actualización:\n  {info.command}")
    if getattr(args, "run", False):
        print("[interui] ejecutando la actualización…")
        return updates.run_upgrade(info.command if info.available else command)
    return 0


def cmd_doctor(_args: argparse.Namespace) -> int:
    from .desktop import desktop_info

    info = desktop_info()
    npm = _npm()
    node = shutil.which("node")
    css = STATIC_DIR / "app.css"
    js = STATIC_DIR / "interui.js"

    rows = [
        ("Python", info["python"], True),
        ("Sistema", info["platform"], True),
        ("pywebview (ventana nativa)", "instalado" if info["pywebview"] else "no instalado", info["pywebview"]),
        ("Backend de ventana", str(info["backend"] or "—"), bool(info["backend"])),
        ("CSS compilado", f"{css.stat().st_size // 1024} kB" if css.exists() else "falta (npm run build)", css.exists()),
        ("Runtime JS", f"{js.stat().st_size // 1024} kB" if js.exists() else "falta", js.exists()),
        ("Node.js", node or "no instalado (solo necesario para recompilar Tailwind)", True),
        ("npm", npm or "no instalado", True),
        ("PyInstaller", shutil.which("pyinstaller") or "no instalado (necesario para `interui build`)", True),
    ]
    width = max(len(label) for label, _value, _ok in rows)
    print("interui doctor\n" + "=" * (width + 42))
    for label, value, ok in rows:
        mark = "✔" if ok else "✖"
        print(f" {mark} {label.ljust(width)}  {value}")
    print("=" * (width + 42))
    print("La app funciona sin Node ni PyInstaller; solo se usan para recompilar estilos y empaquetar.")
    return 0


def cmd_assets(_args: argparse.Namespace) -> int:
    frontend = _frontend_dir()
    if frontend is None:
        raise SystemExit("interui: no se encontró el directorio frontend/ con package.json")
    if shutil.which("npm") is None:
        raise SystemExit("interui: npm no está instalado; instala Node.js para recompilar Tailwind")
    if not (frontend / "node_modules").is_dir():
        print("[interui] instalando dependencias de frontend…")
        subprocess.run(["npm", "install"], cwd=frontend, check=True)
    print("[interui] compilando Tailwind con Vite…")
    subprocess.run(["npm", "run", "build"], cwd=frontend, check=True)
    css = STATIC_DIR / "app.css"
    print(f"[interui] app.css -> {css} ({css.stat().st_size // 1024} kB)")
    return 0


def cmd_dev(_args: argparse.Namespace) -> int:
    frontend = _frontend_dir()
    if frontend is None:
        raise SystemExit("interui: no se encontró el directorio frontend/ con package.json")
    if not (frontend / "node_modules").is_dir():
        subprocess.run(["npm", "install"], cwd=frontend, check=True)
    return subprocess.run(["npm", "run", "watch"], cwd=frontend).returncode


def cmd_build(args: argparse.Namespace) -> int:
    script = Path(args.script).expanduser().resolve()
    if not script.is_file():
        raise SystemExit(f"interui: no existe {script}")
    if not (STATIC_DIR / "app.css").exists():
        raise SystemExit("interui: falta interui/static/app.css; ejecuta `interui assets` antes de empaquetar")

    executable = shutil.which("pyinstaller")
    if executable is None:
        raise SystemExit(
            "interui: PyInstaller no está instalado.\n"
            "  pip install pyinstaller\n"
            "  interui build " + script.name
        )

    name = args.name or script.stem
    out = Path(args.output).expanduser().resolve()
    sep = ";" if platform.system() == "Windows" else ":"
    data = f"{STATIC_DIR}{sep}interui/static"
    icon = f"--icon={Path(args.icon).expanduser()}" if args.icon else ""

    command = [
        executable,
        "--noconfirm",
        "--clean",
        "--windowed" if not args.console else "--console",
        "--name",
        name,
        "--distpath",
        str(out / "dist"),
        "--workpath",
        str(out / "build"),
        "--specpath",
        str(out),
        "--add-data",
        data,
        "--collect-all",
        "webview",
        "--hidden-import",
        "interui",
    ]
    if args.onefile:
        command.append("--onefile")
    if icon:
        command.append(icon)
    command.append(str(script))

    print("[interui] empaquetando:", " ".join(command))
    result = subprocess.run(command)
    if result.returncode == 0:
        print(f"\n[interui] listo: {out / 'dist' / name}")
    return result.returncode


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="interui",
        description="Aplicaciones de escritorio en Python con HTML, Tailwind y JS.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="abre una app de escritorio")
    run.add_argument("script", help="archivo Python que define `app`")
    run.add_argument("--window", default="desktop", choices=["desktop", "browser", "none"])
    run.add_argument("--port", type=int, default=0, help="puerto local (0 = aleatorio)")
    run.add_argument("--host", default="127.0.0.1")
    run.add_argument("--debug", action="store_true", help="abre las herramientas de desarrollo")
    run.add_argument("--verbose", action="store_true")
    run.add_argument("--title")
    run.add_argument("--width", type=int)
    run.add_argument("--height", type=int)
    run.add_argument("--theme", choices=["light", "dark"])
    run.set_defaults(func=cmd_run)

    new = sub.add_parser("new", help="crea un proyecto nuevo")
    new.add_argument("destination", help="carpeta del proyecto")
    new.add_argument("--name", help="nombre de la aplicación")
    new.set_defaults(func=cmd_new)

    init = sub.add_parser("init", help="asistente: proyecto + interui.json + base de datos")
    init.add_argument("destination", nargs="?", default=".", help="carpeta del proyecto")
    init.add_argument("--name", help="nombre de la aplicación")
    init.add_argument("--title", help="título de la ventana")
    init.add_argument("--db", help="motor: sqlite, postgres, mysql, mongo o file")
    init.add_argument("--database", help="nombre de la base de datos o ruta del archivo")
    init.add_argument("--host")
    init.add_argument("--port", type=int)
    init.add_argument("--user")
    init.add_argument("--password")
    init.add_argument("--theme", choices=["light", "dark"])
    init.add_argument("--no-input", action="store_true", help="sin preguntas (usa los valores por defecto)")
    init.add_argument("--migrate", action="store_true", help="crea y aplica la migración inicial")
    init.add_argument("--force", action="store_true", help="sobrescribe archivos existentes")
    init.set_defaults(func=cmd_init)

    database = sub.add_parser("db", help="migraciones de la base de datos")
    db_sub = database.add_subparsers(dest="action", required=True)
    make = db_sub.add_parser("makemigrations", help="genera la migración de los cambios")
    make.add_argument("name", nargs="?", help="nombre de la migración")
    make.add_argument("--force", action="store_true", help="permite cambios que borran datos")
    make.add_argument("--config", help="ruta de interui.json")
    make.set_defaults(func=cmd_db)
    run_db = db_sub.add_parser("migrate", help="aplica las migraciones pendientes")
    run_db.add_argument("--config", help="ruta de interui.json")
    run_db.set_defaults(func=cmd_db, name=None, force=False)
    show = db_sub.add_parser("status", help="muestra el estado de las migraciones")
    show.add_argument("--config", help="ruta de interui.json")
    show.set_defaults(func=cmd_db, name=None, force=False)

    build = sub.add_parser("build", help="empaqueta un ejecutable autónomo")
    build.add_argument("script")
    build.add_argument("--name", help="nombre del ejecutable")
    build.add_argument("--output", default="build-out", help="carpeta de salida")
    build.add_argument("--onefile", action="store_true", help="un solo archivo (más lento de abrir)")
    build.add_argument("--console", action="store_true", help="mantiene la consola visible")
    build.add_argument("--icon", help="archivo .icns/.ico")
    build.set_defaults(func=cmd_build)

    update = sub.add_parser("update", help="comprueba si hay versión nueva y muestra el comando")
    update.add_argument("--run", action="store_true", help="ejecuta la actualización")
    update.add_argument("--timeout", type=float, default=5.0)
    update.set_defaults(func=cmd_update)

    sub.add_parser("doctor", help="comprueba el entorno").set_defaults(func=cmd_doctor)
    sub.add_parser("assets", help="recompila Tailwind (Vite)").set_defaults(func=cmd_assets)
    sub.add_parser("dev", help="Tailwind en modo watch").set_defaults(func=cmd_dev)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    if getattr(args, "command", None) == "new" and not getattr(args, "name", None):
        args.name = Path(args.destination).name
    try:
        return int(args.func(args) or 0)
    except KeyboardInterrupt:
        return 130


_ = os
