# local

App del proyecto **proyecto_tareas**, creada con `iui startapp`.

| Archivo | Para qué |
|---|---|
| `models.py` | modelos del ORM de esta app (los migra `python iui.py migrate`). |
| `views.py` | las páginas de la app. |
| `urls.py` | qué vista responde a cada ruta. |

Ya está declarada en `apps` de `interui.json`, así que sus rutas se registran
solas al abrir la ventana. Las migraciones son del proyecto (`migrations/`),
para que un solo `migrate` ponga al día todas las apps.
