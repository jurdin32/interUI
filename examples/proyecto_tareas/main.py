#!/usr/bin/env python
"""Punto de entrada de proyecto_tareas.

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

from proyecto_tareas.app import create_app

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
