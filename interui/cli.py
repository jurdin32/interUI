"""CLI de interui: `interui run | new | build | doctor | assets`."""

from __future__ import annotations

import argparse
import importlib.util
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
TEMPLATE = '''"""{name} · aplicación de escritorio con interui."""

from interui import App, Button, Card, Col, Container, Heading, Muted, Row, Screen

app = App("{name}")


@app.page("/")
def index():
    clicks = app.state("clicks", 0)
    return Screen(
        Container(size="prose", class_="py-16")(
            Heading("{name}", level=1),
            Muted("Edita app.py y guarda: la ventana se recompone sola."),
            Card(class_="mt-6")(
                Muted(f"Pulsaciones: {{clicks.get()}}"),
                Button(
                    "Pulsar",
                    icon="plus",
                    on_click=lambda: clicks.set(clicks.get() + 1),
                ),
            ),
        )
    )


if __name__ == "__main__":
    app.run()
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

    build = sub.add_parser("build", help="empaqueta un ejecutable autónomo")
    build.add_argument("script")
    build.add_argument("--name", help="nombre del ejecutable")
    build.add_argument("--output", default="build-out", help="carpeta de salida")
    build.add_argument("--onefile", action="store_true", help="un solo archivo (más lento de abrir)")
    build.add_argument("--console", action="store_true", help="mantiene la consola visible")
    build.add_argument("--icon", help="archivo .icns/.ico")
    build.set_defaults(func=cmd_build)

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
