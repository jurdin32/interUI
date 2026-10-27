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

__version__ = "0.1.0"

from .app import App
from .base import Component, Fragment, bind_many, render, render_children
from .desktop import DesktopError, Native, desktop_info
from .context import RenderContext
from .events import Attachment, UIEvent
from .grid import (
    AspectRatio, Center, Col, Container, Divider, Grid, Row, Screen, ScrollArea,
    Spacer, Stack,
)
from .html import Markup, escape, raw
from .icons import ICON_NAMES, ICONS, Icon
from .state import Signal
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
    "Signal", "Icon", "ICONS", "ICON_NAMES", "Markup", "raw", "escape", "tw", "cl",
    "render", "render_children", "bind_many", "BUTTON_SIZES", "BUTTON_VARIANTS",
    "window", "view", "state", "row", "column", "title", "subtitle", "toast",
    "current_app", "snake_case", "alias_names",
    "Container", "Row", "Col", "Stack", "Spacer", "Divider", "Center",
    "AspectRatio", "ScrollArea", "Grid", "Screen",
    *_controls_all,
]


# Alias en minúsculas para todos los controles: ui.button, ui.input, ui.card…
# (SIMPLE_ALIASES se calcula una sola vez aquí, sobre el catálogo completo.)
SIMPLE_ALIASES: dict[str, str] = alias_names([name for name in __all__ if name[:1].isupper()])
globals().update({alias: globals()[control] for alias, control in SIMPLE_ALIASES.items()})
__all__ = [*__all__, *SIMPLE_ALIASES]


def run(app: "App", **kwargs: object) -> None:
    """Atajo: ``interui.run(app)``."""
    app.run(**kwargs)  # type: ignore[arg-type]
