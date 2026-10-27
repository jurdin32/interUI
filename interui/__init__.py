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

__all__ = [
    "App", "Component", "Fragment", "RenderContext", "UIEvent", "Attachment",
    "Native", "DesktopError", "desktop_info",
    "Signal", "Icon", "ICONS", "ICON_NAMES", "Markup", "raw", "escape", "tw", "cl",
    "render", "render_children", "bind_many", "BUTTON_SIZES", "BUTTON_VARIANTS",
    "Container", "Row", "Col", "Stack", "Spacer", "Divider", "Center",
    "AspectRatio", "ScrollArea", "Grid", "Screen",
    *_controls_all,
]


def run(app: "App", **kwargs: object) -> None:
    """Atajo: ``interui.run(app)``."""
    app.run(**kwargs)  # type: ignore[arg-type]
