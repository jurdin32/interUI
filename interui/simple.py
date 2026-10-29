"""API compacta: menos código para lo cotidiano.

La API completa sigue disponible (`ui.Button`, `ui.Row`…), pero para el 90 % de
las pantallas basta con esto:

```python
from interui import window, text, button, state

count = state(0)

window(
    "Contador",
    text("Hola mundo"),
    text("Pulsaciones: ", count),          # se actualiza solo
    button("Pulsar", on_click=count.inc),  # sin lambdas ni eventos
).run()
```

Reglas de la API compacta:

* **una ventana implícita**: `window(...)` crea la app y registra la página `/`.
* **controles en minúsculas**: `button`, `input`, `card`, `table`… son alias de
  los controles (`Button`, `Input`, `Card`, `Table`), generados automáticamente.
* **texto reactivo**: puedes pasar una señal o una función como hijo y se
  evalúa en cada render.
* **señales como handlers**: `on_input=nombre`, `on_change=activo`,
  `on_click=contador.inc`.
* **rejilla automática**: `row(a, b, c)` reparte las 12 columnas sin escribir
  `Col`.
"""

from __future__ import annotations

import hashlib
import re
import sys
from typing import Any, Callable, Sequence

from .app import App
from .base import Component
from .grid import Col, Container, Row, Screen, Stack
from .state import Signal

__all__ = [
    "window", "view", "state", "row", "column", "title", "subtitle", "toast",
    "current_app", "snake_case", "SIMPLE_ALIASES", "alias_names", "RESERVED_ALIASES",
]

_DEFAULT_APP: App | None = None
_VIEW: Callable[[], Component] | None = None
_REGISTERED = False


# ---------------------------------------------------------------------------
# ventana implícita
# ---------------------------------------------------------------------------
def current_app(title: str = "interUI", **options: Any) -> App:
    """Devuelve (o crea) la aplicación por defecto de la API compacta.

    No se llama ``app`` para no tapar el submódulo ``interui.app``.
    """
    global _DEFAULT_APP
    if _DEFAULT_APP is None:
        _DEFAULT_APP = App(title, **options)
    else:
        _DEFAULT_APP.title = title
        for key in ("width", "height", "theme", "frameless", "resizable"):
            if key in options:
                setattr(_DEFAULT_APP, key, options[key])
    return _DEFAULT_APP


def window(
    title: str = "interUI",
    *children: Any,
    width: int = 960,
    height: int = 680,
    theme: str = "light",
    container: str = "xl",
    pad: str = "py-8",
    gap: int = 4,
    **options: Any,
) -> App:
    """Crea la ventana y su contenido en una sola llamada.

    Devuelve la ``App``, así que se encadena con ``.run()``.
    """
    global _VIEW, _REGISTERED
    application = current_app(
        title, width=width, height=height, theme=theme, **options
    )

    def build() -> Component:
        body = wrap(children, container=container, pad=pad, gap=gap)
        return body

    _VIEW = build
    if not _REGISTERED:
        @application.page("/")
        def _index() -> Component:
            assert _VIEW is not None
            return _VIEW()

        _REGISTERED = True
    return application


def recipient_app() -> App:
    """La app que ejecuta el handler actual, o la implícita fuera de uno."""
    from .app import active_app

    return active_app() or current_app()


def view(
    path: str = "/",
    *,
    title: str | None = None,
    container: str = "xl",
    pad: str = "py-8",
    gap: int = 4,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Registra una vista adicional: ``@view("/ajustes")``."""
    application = current_app()

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def registered() -> Component:
            return wrap([func()], container=container, pad=pad, gap=gap)

        application.page(path, title=title)(registered)
        return func

    return decorator


def wrap(
    children: Sequence[Any],
    *,
    container: str = "xl",
    pad: str = "py-8",
    gap: int = 4,
) -> Component:
    """Envuelve contenido suelto en Screen + Container + Stack."""
    items = list(children)
    if len(items) == 1 and isinstance(items[0], Component) and items[0].tag in ("div", "main"):
        if items[0].__class__.__name__ == "Screen":
            return items[0]
    return Screen(
        Container(size=container, class_=pad)(Stack(*items, gap=gap)),
    )


# ---------------------------------------------------------------------------
# estado implícito
# ---------------------------------------------------------------------------
def _key_for_caller(frame: Any) -> str:
    """Nombre estable para ``state()`` sin ``name``: el sitio donde se escribió.

    Se calcula con el archivo, la función, la línea y la instrucción, así que
    dos llamadas distintas nunca chocan y la misma llamada conserva su señal
    entre repintados (que es lo que espera una vista).
    """
    code = frame.f_code
    raw = f"{code.co_filename}|{code.co_qualname}|{frame.f_lineno}|{frame.f_lasti}"
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    return f"s_{code.co_name}_{digest}"


def state(initial: Any = None, *, name: str | None = None) -> Signal:
    """Crea (o recupera) una señal de la ventana activa: ``count = state(0)``.

    Si la señal ya existe se devuelve la misma: el valor inicial solo se aplica
    la primera vez, así llamarla dentro de una vista no borra lo que escribió el
    usuario en el repintado siguiente. Sin ``name`` la señal se identifica por
    el lugar del código donde se llama, de modo que ``state("")`` dentro de una
    vista siempre devuelve la misma señal.
    """
    application = recipient_app()
    key = name or _key_for_caller(sys._getframe(1))
    nueva = key not in application._signals
    signal = application.state(key, initial)
    if nueva and initial is not None:
        signal.set(initial)
    return signal


# ---------------------------------------------------------------------------
# atajos de composición
# ---------------------------------------------------------------------------
def row(*children: Any, gap: int = 4, span: int | None = None, **props: Any) -> Row:
    """Fila con columnas automáticas: ``row(a, b, c)`` → tres columnas iguales."""
    total = len(children) or 1
    per_row = min(total, 4)
    width = span or max(1, 12 // per_row)
    columns = [Col(child, span=12, md=width, lg=width) for child in children]
    return Row(*columns, gap=gap, **props)


def column(*children: Any, gap: int = 4, **props: Any) -> Stack:
    """Columna (alias de ``Stack`` vertical)."""
    return Stack(*children, gap=gap, **props)


def title(text: Any, subtitle: Any = None, **props: Any) -> Component:
    """Título principal de la pantalla."""
    from .controls.typography import Title

    return Title(text, subtitle=subtitle, **props)


def subtitle(text: Any, **props: Any) -> Component:
    """Texto secundario bajo un título."""
    from .controls.typography import Muted

    return Muted(text, **props)


def toast(message: str, level: str = "info", **options: Any) -> None:
    """Snackbar flotante (equivale a ``app.notify``).

    Si se llama dentro de un handler, el aviso sale en **esa** ventana, aunque la
    app se haya creado con `ui.App(...)`. Acepta ``title``, ``icon``, ``image``,
    ``duration`` y ``action``::

        toast("Guardado", "success", icon=icons.check, title="Hecho")
    """
    recipient_app().notify(message, level, **options)


# ---------------------------------------------------------------------------
# alias en minúsculas para todos los controles
# ---------------------------------------------------------------------------
_CAMEL = re.compile(r"(?<!^)(?=[A-Z])")
RESERVED_ALIASES = frozenset({
    "row", "title", "state", "window", "view", "app", "toast", "column",
    "subtitle", "current_app",
})
_RESERVED = RESERVED_ALIASES


def snake_case(name: str) -> str:
    """``DataTable`` → ``data_table``."""
    return _CAMEL.sub("_", name).lower()


def alias_names(names: Sequence[str]) -> dict[str, str]:
    """Mapa ``alias -> Control`` para los nombres dados."""
    out: dict[str, str] = {}
    for name in names:
        alias = snake_case(name)
        if alias in _RESERVED or alias == name:
            continue
        out[alias] = name
    return out


def install(namespace: dict[str, Any]) -> dict[str, str]:
    """Inyecta los alias en el espacio de nombres del paquete."""
    aliases = alias_names([name for name in namespace.get("__all__", []) if name[:1].isupper()])
    for alias, control in aliases.items():
        target = namespace.get(control)
        if isinstance(target, type):
            namespace[alias] = target
    return aliases


# ---------------------------------------------------------------------------
# alias disponibles también al importar desde `interui.simple`
# ---------------------------------------------------------------------------
from .aliases import *  # noqa: E402,F401,F403  (alias estáticos)
from .aliases import __all__ as _alias_all  # noqa: E402

__all__ = [*__all__, *_alias_all]

SIMPLE_ALIASES: dict[str, str] = {alias: snake_case(alias) for alias in _alias_all}
