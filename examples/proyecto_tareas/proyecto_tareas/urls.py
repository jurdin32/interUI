"""Rutas del proyecto.

Cada entrada es `(ruta, vista, título de la ventana)`. Para parámetros usa
`"/tarea/<int:id>"` y la vista recibirá la función `tarea(id=1)`.
"""

from typing import Any, Callable

from proyecto_tareas import views

URLPattern = tuple[str, Callable[..., Any], str]

urlpatterns: list[URLPattern] = [
    ("/", views.inicio, "Inicio"),
]


def register(app: Any) -> None:
    """Conecta `urlpatterns` con la aplicación.

    Las apps creadas con `python iui.py startapp` no se tocan aquí: están en
    `apps` de interui.json y sus rutas se registran solas.
    """
    for path, view, title in urlpatterns:
        app.page(path, title=title)(view)
