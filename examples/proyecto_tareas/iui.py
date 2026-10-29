#!/usr/bin/env python
"""Comandos de proyecto_tareas.

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
