"""interui · interfaces gráficas de Python con HTML, Tailwind y JS.

.. code-block:: python

    from interui import App, Card, Col, Label, Button, Row

    app = App("Contador")

    @app.page("/")
    def index():
        count = app.state("count", 0)
        return Card(title="Contador")(
            Label(f"Valor: {count.get()}"),
            Button("Incrementar", on_click=lambda: count.set(count.get() + 1)),
        )

    app.run()
"""

from __future__ import annotations

import sys

__version__ = "0.4.0"

from .app import App
from .base import Component, Fragment, bind_many, render, render_children
from .desktop import DesktopError, Native, desktop_info
from .dialogs import Dialog, DialogAPI, DialogHost
from .dialogs import dialog
from .context import RenderContext
from .events import Attachment, UIEvent
from .grid import (
    AspectRatio, Center, Col, Container, Divider, Grid, Row, Screen, ScrollArea,
    Spacer, Stack,
)
from .html import Markup, escape, raw
from .icons import ICON_NAMES, ICONS, Icon, IconGrid
from .state import Signal
from . import updates
from .style import cl, tw
from .ui import BUTTON_SIZES, BUTTON_VARIANTS
from .controls import *  # noqa: F401,F403  (catálogo de controles)
from .controls import __all__ as _controls_all
from .simple import (  # API compacta (minúsculas, ventana implícita)
    alias_names, column, current_app, row, snake_case, state, subtitle, title, toast,
    view, window,
)

__all__ = [
    "App", "Component", "Fragment", "RenderContext", "UIEvent", "Attachment",
    "Native", "DesktopError", "desktop_info",
    "Dialog", "DialogAPI", "DialogHost", "dialog",
    "Signal", "Icon", "IconGrid", "ICONS", "ICON_NAMES", "Markup", "raw", "escape", "tw", "cl",
    "render", "render_children", "bind_many", "BUTTON_SIZES", "BUTTON_VARIANTS",
    "window", "view", "state", "row", "column", "title", "subtitle", "toast",
    "current_app", "snake_case", "alias_names", "updates",
    "Container", "Row", "Col", "Stack", "Spacer", "Divider", "Center",
    "AspectRatio", "ScrollArea", "Grid", "Screen",
    *_controls_all,
]


# Alias en minúsculas para todos los controles: ui.button, ui.input, ui.card…
# Se importan de un módulo real y estático (interui/aliases.py) para que Pylance
# y mypy resuelvan `from interui import text` sin falsos errores.
from .aliases import *  # noqa: F401,F403,E402  (alias estáticos)
from .aliases import __all__ as _alias_all  # noqa: E402

SIMPLE_ALIASES: dict[str, str] = {
    alias: getattr(sys.modules[__name__], alias).__name__ for alias in _alias_all
}
__all__ = [*__all__, *_alias_all]


def run(app: "App", **kwargs: object) -> None:
    """Atajo: ``interui.run(app)``."""
    app.run(**kwargs)  # type: ignore[arg-type]
