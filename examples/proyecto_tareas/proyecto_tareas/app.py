"""La ventana de la aplicación.

Aquí se crea la `App` con lo que dice `interui.json` y se registran las rutas
de `urls.py`.
"""

from pathlib import Path

import interui as ui

from proyecto_tareas import urls

#: `interui.json` vive un nivel por encima del paquete.
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = BASE_DIR / "interui.json"


def create_app() -> ui.App:
    """`App` del proyecto, con todas las páginas ya registradas."""
    app = ui.App.from_config(CONFIG)
    urls.register(app)
    return app


app = create_app()
