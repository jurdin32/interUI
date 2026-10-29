# Configuración: `interui.json`

`interui.json` es el único archivo de configuración de un proyecto. Lo leen la
CLI, la `App`, el ORM y las migraciones, así que no hay valores duplicados en
Python: cambiar de base de datos o el tamaño de la ventana es editar una línea.

```json
{
  "app": {
    "name": "mi_app",
    "title": "Mi Tienda — Gestión",
    "version": "0.1.0",
    "theme": "light",
    "width": 1180,
    "height": 780,
    "entry": "mi_app.app",
    "debug": false
  },
  "databases": {
    "default": { "engine": "sqlite", "name": "data/app.db" }
  },
  "apps": [],
  "migrations": {
    "directory": "migrations",
    "models": ["mi_app/models.py"]
  }
}
```

---

## 1. Dónde se busca

Los comandos buscan `interui.json` en la carpeta actual y, si no está, en las
carpetas superiores. Por eso `python iui.py migrate` funciona igual desde la raíz
del proyecto que desde `mi_app/`.

Puedes apuntar a otro archivo con `--config`:

```bash
iui db migrate --config /ruta/a/interui.json
```

Desde Python:

```python
import interui as ui

settings = ui.Config.load()            # busca hacia arriba
settings = ui.Config.load("ruta/interui.json")
settings.databases.default.engine      # "sqlite"
settings.database().url                # "sqlite:///data/app.db"
```

---

## 2. `app`

Identidad y ventana.

| Clave | Tipo | Por defecto | Qué hace |
|---|---|---|---|
| `name` | texto | `"Mi app"` | Nombre corto del proyecto. |
| `title` | texto | igual que `name` | Nombre largo que se ve en la barra de la ventana. |
| `version` | texto | `"0.1.0"` | Versión de tu app (útil para mostrarla o para actualizaciones). |
| `theme` | `"light"` \| `"dark"` | `"light"` | Tema inicial; se puede cambiar en caliente con `app.set_theme()`. |
| `width` | entero | `1180` | Ancho inicial de la ventana en píxeles. |
| `height` | entero | `780` | Alto inicial en píxeles. |
| `entry` | texto | `"app.py"` | Módulo o archivo que define la `App` del proyecto. |
| `debug` | booleano | `false` | Abre las herramientas de desarrollo del motor web. |

`entry` acepta las dos formas:

- `"mi_app.app"` → importa ese módulo y usa su variable `app` (o su función
  `create_app()`). Es lo que genera `startproject`.
- `"app.py"` → carga ese archivo y busca una instancia de `App`.

---

## 3. `databases`

Un objeto con una entrada por conexión. `default` es obligatoria y es la que usan
el ORM y las migraciones.

```json
"databases": {
  "default": { "engine": "sqlite", "name": "data/app.db" },
  "analitica": { "engine": "postgres", "name": "analitica" }
}
```

Para usar otra conexión en un modelo:

```python
class Visita(ui.Model):
    class Meta:
        table = "visitas"
        database = "analitica"
```

### Motores y sus claves

| `engine` | Claves | Valores por defecto | Extra |
|---|---|---|---|
| `sqlite` | `name` (ruta del archivo) | `data/app.db` | — |
| `file` | `name` (carpeta) | `data` | — |
| `postgres` | `host`, `port`, `user`, `password`, `name` | `localhost`, `5432`, `postgres`, —, `postgres` | `pip install "interui[postgres]"` |
| `mysql` | `host`, `port`, `user`, `password`, `name` | `localhost`, `3306`, `root`, —, `mysql` | `pip install "interui[mysql]"` |
| `mongo` | `host`, `port`, `name` | `localhost`, `27017`, `interui` | `pip install "interui[mongo]"` |

Las rutas relativas se resuelven **respecto a la carpeta de `interui.json`**, no
respecto al directorio desde el que lanzas el comando.

```json
"databases": { "default": { "engine": "sqlite", "name": "data/tienda.db" } }
```

### Secretos con variables de entorno

Cualquier valor puede leer una variable de entorno, con valor por defecto
opcional:

```json
"databases": {
  "default": {
    "engine": "postgres",
    "host": "${DB_HOST:localhost}",
    "port": 5432,
    "user": "${DB_USER:postgres}",
    "password": "${DB_PASSWORD}",
    "name": "${DB_NAME:tienda}"
  }
}
```

Así el `interui.json` se puede versionar sin contraseñas. Si la variable no
existe y no hay valor por defecto, el valor queda vacío y la conexión fallará al
usarse (no al arrancar).

---

## 4. `apps`

Lista de apps del proyecto. Cada nombre es un **módulo importable** con un
`urls.py` dentro:

```json
"apps": ["ventas", "inventario"]
```

Al arrancar, `App.from_config()` importa `ventas.urls` e `inventario.urls` y
registra sus rutas. `python iui.py startapp ventas` añade la entrada por ti.

Si tu app necesita más control, puede exponer `register(app)` en su `urls.py`:

```python
def register(app) -> None:
    for path, view, title in urlpatterns:
        app.page(path, title=title)(view)
```

Si no define `register`, se usan sus `urlpatterns` tal cual.

---

## 5. `migrations`

| Clave | Tipo | Por defecto | Qué hace |
|---|---|---|---|
| `directory` | texto | `"migrations"` | Carpeta donde se guardan las migraciones (se versiona en git). |
| `models` | texto o lista | `["models.py"]` | Archivos de modelos que hay que vigilar. |

`models` acepta un solo archivo o una lista; `startapp` añade el de cada app:

```json
"models": ["mi_app/models.py", "ventas/models.py"]
```

`makemigrations` importa todos esos archivos, compara las tablas declaradas con
la última migración y escribe solo las diferencias. El orden de la lista no
importa salvo que dos archivos declaren la misma tabla (gana el último).

---

## 6. Variables de entorno del framework

Además de las que uses tú dentro del JSON, interUI entiende:

| Variable | Efecto |
|---|---|
| `INTERUI_DATA_DIR` | Carpeta de datos de la app (registro, caché del motor web). Útil en tests y apps portables. |
| `INTERUI_DEV` | Activa el modo desarrollo (equivale a `App(dev=True)`). |
| `INTERUI_NO_UPDATE_CHECK=1` | Desactiva la consulta de versión nueva al arrancar. |

Las rutas de datos por defecto son:

| Sistema | Carpeta |
|---|---|
| macOS | `~/Library/Application Support/<slug>` |
| Windows | `%APPDATA%\<slug>` |
| Linux | `$XDG_DATA_HOME/<slug>` o `~/.local/share/<slug>` |

El `<slug>` sale del título de la app (`Mi Tienda` → `mi-tienda`).

---

## 7. Validación

`iui.py check` valida el archivo sin abrir la ventana:

```bash
python iui.py check
```

Comprueba que:

- `databases` existe y tiene `default`;
- cada `engine` es conocido;
- no faltan claves obligatorias del motor (se permiten omitir `host`, `port`,
  `user` y `password`, que toman su valor por defecto);
- el archivo de modelos existe.

Los mismos errores aparecen, con el nombre del archivo y la línea, si el JSON
está mal formado:

```text
[interui] /ruta/interui.json: JSON inválido en la línea 12: Expecting ',' delimiter
```

---

## 8. Editar la configuración desde Python

```python
import interui as ui

settings = ui.Config.load()
settings.app.title = "Otro nombre"
settings.databases.default.engine = "sqlite"
settings.save()                    # reescribe interui.json
```

`settings.to_dict()` devuelve un diccionario normal si necesitas serializarlo.
Ten en cuenta que `save()` escribe también los valores por defecto que no estaban
en el archivo; si prefieres un JSON mínimo, edítalo a mano.
