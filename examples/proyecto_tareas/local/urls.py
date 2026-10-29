"""Rutas de la app local.

No hay que registrarlas a mano: «local» está en `apps` de interui.json y
`App.from_config()` conecta este `urlpatterns` al arrancar.
"""

from typing import Any, Callable

from local import views

URLPattern = tuple[str, Callable[..., Any], str]

urlpatterns: list[URLPattern] = [
    ("/local", views.inicio, "local"),
]


def register(app: Any) -> None:
    """Conecta las rutas de la app con la aplicación."""
    for path, view, title in urlpatterns:
        app.page(path, title=title)(view)
