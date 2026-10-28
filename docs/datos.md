# Datos: `interui.json`, modelos, ORM y migraciones

Todo lo que hay en esta guía viene en el paquete (`interui.config`,
`interui.db`, `interui.orm` y `interui.migrations`): no necesitas Django,
SQLAlchemy ni ningún servidor para empezar. SQLite y los archivos JSON usan solo
la biblioteca estándar; PostgreSQL, MySQL/MariaDB y MongoDB son un extra de `pip`.

| Quiero… | Sección |
|---|---|
| crear el proyecto con el asistente | [1](#1-proyecto-nuevo-en-tres-comandos) |
| escribir `interui.json` a mano | [2](#2-interuijson-paso-a-paso) |
| declarar mis modelos | [3](#3-modelos-paso-a-paso) |
| consultar datos | [4](#4-consultas-orm) |
| crear y aplicar migraciones | [5](#5-migraciones) |
| ver los comandos | [6](#6-referencia-de-la-cli) |
| usarlo dentro de la interfaz | [7](#7-la-orm-dentro-de-la-interfaz) |
| resolver un error concreto | [8](#8-errores-frecuentes) |

| Motor | `engine` | Necesita |
|---|---|---|
| SQLite (un archivo) | `sqlite` | nada |
| Archivos JSON (un archivo por tabla) | `file` | nada |
| PostgreSQL | `postgres` | `pip install "interui[postgres]"` |
| MySQL / MariaDB | `mysql` | `pip install "interui[mysql]"` |
| MongoDB | `mongo` | `pip install "interui[mongo]"` |

---

## 1. Proyecto nuevo en tres comandos

```bash
pip install "interui[desktop]"
interui init tienda --db sqlite --name Tienda --migrate
cd tienda && python app.py
```

`interui init` pregunta lo mínimo y deja el proyecto listo:

```text
Nombre de la aplicación [tienda]: Tienda
Motor de base de datos:
  1. SQLite (un archivo, sin servidor)
  2. PostgreSQL
  3. MySQL / MariaDB
  4. MongoDB
  5. Archivos JSON (sin servidor)
Elige un número [1]: 1
  name [data/app.db]:
[interui] proyecto creado en /ruta/tienda
[interui] configuración: /ruta/tienda/interui.json
[interui] migración creada: migrations/0001_initial.json
[interui] aplicada 0001_initial
```

Lo que crea:

```text
tienda/
├── interui.json          ← punto de partida: app, bases de datos y migraciones
├── app.py                ← ui.App.from_config() + una ruta de ejemplo
├── models.py             ← tus modelos (aquí se declaran las tablas)
├── migrations/           ← migraciones generadas (0001_initial.json…)
├── data/                 ← SQLite o archivos JSON (se crea al migrar)
├── .gitignore
└── README.md
```

Sin preguntas, para CI o scripts:

```bash
interui init tienda --no-input --name Tienda --db postgres \
    --host localhost --port 5432 --user tienda --password "" \
    --database tienda --migrate
```

| Opción | Para qué |
|---|---|
| `--db` | `sqlite`, `postgres`, `mysql`, `mongo` o `file`. |
| `--database` | Ruta del archivo (SQLite/archivos) o nombre de la base. |
| `--host`, `--port`, `--user`, `--password` | Conexión de servidor. |
| `--name`, `--title`, `--theme` | Nombre del proyecto, título de la ventana y tema. |
| `--no-input` | No pregunta nada; usa los valores por defecto. |
| `--migrate` | Genera y aplica la migración inicial. |
| `--force` | Escribe aunque la carpeta no esté vacía. |

`app.py` recién generado (así se usa la configuración):

```python
import interui as ui

app = ui.App.from_config()


@app.page("/")
def index():
    return ui.Screen(
        ui.Container(pad=ui.pad.py_10)(
            ui.Heading("Tienda", level=1),
            ui.Muted("Configuración leída de interui.json"),
            ui.Button("Salir", icon=ui.icons.power, on_click=app.exit),
        )
    )
```

El archivo termina con el arranque de siempre: `if __name__ == "__main__":
app.run()`.

Y `models.py`:

```python
import interui as ui


class Ejemplo(ui.Model):
    nombre = ui.Str(max_length=80)
    notas = ui.LongText(null=True)
    activo = ui.Bool(default=True)
    creado = ui.DateTime(auto_now_add=True)

    class Meta:
        table = "ejemplo"
```

---

## 2. `interui.json` paso a paso

Es el **punto de partida de la app**: un JSON (no un `.env`) que describe la
ventana, las bases de datos y dónde viven las migraciones. Sin asistente también
funciona: crea el archivo con un editor y ya está.

### 2.1 Lo mínimo que funciona

```json
{
  "databases": {
    "default": { "engine": "sqlite", "name": "data/app.db" }
  }
}
```

Con eso `ui.App.from_config()` arranca, `ui.Model` guarda en SQLite y las
migraciones se generan en `migrations/`. Todo lo que no escribas toma el valor
por defecto.

### 2.2 El archivo completo

```json
{
  "app": {
    "name": "Tienda",
    "title": "Tienda · escritorio",
    "version": "0.1.0",
    "theme": "light",
    "width": 1180,
    "height": 780,
    "entry": "app.py",
    "debug": false
  },
  "databases": {
    "default": { "engine": "sqlite", "name": "data/app.db" },
    "reportes": {
      "engine": "postgres",
      "host": "localhost",
      "port": 5432,
      "user": "tienda",
      "password": "${PG_PASSWORD}",
      "name": "reportes"
    }
  },
  "migrations": {
    "directory": "migrations",
    "models": "models.py"
  }
}
```

`app.*`:

| Clave | Por defecto | Efecto |
|---|---|---|
| `name` | `"Mi app"` | Nombre lógico (título por defecto y carpeta de datos). |
| `title` | igual que `name` | Título de la ventana. |
| `version` | `"0.1.0"` | Aparece en el aviso de versión nueva. |
| `theme` | `"light"` | `light` o `dark`. |
| `width`, `height` | `1180`, `780` | Tamaño inicial de la ventana. |
| `entry` | `"app.py"` | Archivo que se ejecuta con `interui run`. |
| `debug` | `false` | Abre las herramientas de desarrollo. |

`databases.<alias>.*`: siempre `engine`; según el motor:

| Motor | Claves |
|---|---|
| `sqlite` | `name` (ruta del `.db`) |
| `file` | `name` (carpeta con un `.json` por tabla) |
| `postgres` | `host`, `port` (5432), `user`, `password`, `name` |
| `mysql` | `host`, `port` (3306), `user`, `password`, `name` |
| `mongo` | `host`, `port` (27017), `name` |

`migrations.*`: `directory` (por defecto `migrations`) y `models` (por defecto
`models.py`).

Las claves que no conozcas no se tocan: se guardan tal cual y se leen con
`cfg.mi_clave`.

### 2.3 Secretos fuera del JSON

`${VARIABLE}` se sustituye desde el entorno, como en un `.env` pero dentro del
JSON. Si la variable no existe puedes dar un valor:

```json
"password": "${PG_PASSWORD:dev}"
```

```bash
export PG_PASSWORD="secreto-de-verdad"
```

### 2.4 Rutas relativas

`name`, `directory` y `models` se resuelven **respecto a `interui.json`**, no al
directorio desde el que lanzas la app. Así funciona igual con
`python app.py`, `interui run app.py` o el ejecutable empaquetado.

### 2.5 Varias bases a la vez

Cada alias (`default`, `reportes`, `archivos`…) es una conexión con su motor. Un
modelo elige la suya con `Meta.database`:

```json
{
  "databases": {
    "default": { "engine": "sqlite", "name": "data/app.db" },
    "archivos": { "engine": "file", "name": "data/adjuntos" }
  }
}
```

```python
import interui as ui


class Adjunto(ui.Model):
    ruta = ui.Str(max_length=200)

    class Meta:
        table = "adjuntos"
        database = "archivos"
```

### 2.6 Leer y guardar desde Python

```python
from interui import Config

cfg = Config.load()                 # busca interui.json hacia arriba
cfg = Config.load("ruta/interui.json")
cfg = Config.default()              # uno nuevo con valores por defecto

cfg.app.name                        # "Tienda"
cfg.database().url                  # "sqlite:///data/app.db"
cfg.database("reportes").engine     # "postgres"
cfg.databases_map()                 # {"default": ..., "reportes": ...}
cfg.resolve("data/app.db")          # ruta absoluta junto al JSON
cfg.validate()                      # revisa motores y claves obligatorias
cfg.save()                          # reescribe el archivo
cfg.to_dict()                       # dict normal, sin envoltorios
```

Se lee con puntos (`cfg.app.width`) y también como diccionario
(`cfg["app"]["width"]`); `cfg.path` es el archivo del que se cargó.

### 2.7 Usarlo en la ventana

```python
import interui as ui

app = ui.App.from_config()      # interui.json del directorio del script
app.config                      # la Config completa
```

`from_config()` hace tres cosas: crea la `App` con `app.name`, `width`, `height`
y `theme`, deja la configuración en `app.config` y registra las bases de datos,
así que `Model` y las migraciones funcionan sin llamar a nada más. Puedes pisar
valores sueltos:

```python
app = ui.App.from_config(width=1440, theme="dark")
```

Si prefieres construir la `Config` a mano (tests, demos, ejecutable):

```python
from pathlib import Path

import interui as ui

app = ui.App("Clientes · datos")
settings = ui.Config({
    "app": {"name": "Clientes"},
    "databases": {"default": {"engine": "sqlite", "name": str(Path(app.data_dir) / "clientes.db")}},
})
ui.db.configure(settings)
```

---

## 3. Modelos paso a paso

Un modelo es una clase que hereda de `ui.Model`; cada atributo de campo es una
columna. Se declaran en `models.py` (o en cualquier archivo), nunca se escriben
`CREATE TABLE` a mano.

### 3.1 El archivo `models.py`

```python
import interui as ui


class Cliente(ui.Model):
    nombre = ui.Str(max_length=80, unique=True)
    email = ui.Str(max_length=120, null=True)
    edad = ui.Int(null=True)
    activo = ui.Bool(default=True)
    alta = ui.DateTime(auto_now_add=True)
    extra = ui.Json(null=True)
    notas = ui.LongText(null=True)

    class Meta:
        table = "clientes"
        database = "default"
        order = ["nombre"]
```

### 3.2 Campos

| Campo | Columna | Notas |
|---|---|---|
| `ui.Auto()` | `INTEGER` autoincremental | clave primaria; se añade como `id` si no declaras una |
| `ui.Int()` | entero | |
| `ui.Str(max_length=…)` | `VARCHAR(n)` | 255 por defecto |
| `ui.LongText()` | `TEXT` | se llama así porque `Text` es el control de interfaz |
| `ui.Bool()` | booleano | |
| `ui.Float()` | real | |
| `ui.Date()` | fecha | `datetime.date` en Python |
| `ui.DateTime()` | fecha y hora | `datetime.datetime` |
| `ui.Json()` | JSON | se serializa y deserializa solo |
| `ui.Blob()` | binario | `bytes` |
| `ui.FK("clientes")` | entero | referencia simple, **sin** FK del motor |

### 3.3 Opciones de cualquier campo

| Opción | Efecto |
|---|---|
| `null=True` | admite `NULL` (si no, el valor es obligatorio al guardar). |
| `unique=True` | índice único; el motor rechaza duplicados. |
| `default=…` | valor inicial (`default=True`, `default=0`); si es una función, se llama. |
| `max_length=…` | longitud de `VARCHAR`. |
| `column="…"` | nombre real de la columna, si no quieres el del atributo. |
| `auto_now_add=True` | al crear, guarda la fecha actual. |
| `auto_now=True` | en cada `save()`, actualiza la fecha. |
| `primary_key=True` | marca la clave primaria. |
| `auto=True` | deja que el motor asigne el número. |

### 3.4 `Meta`

| Opción | Por defecto | Efecto |
|---|---|---|
| `table` | el nombre de la clase en minúsculas + `s` (`Cliente` → `clientes`) | tabla real |
| `database` | `"default"` | alias de `interui.json` |
| `order` | `[]` | orden por defecto de las consultas (`["-alta"]` = descendente) |

### 3.5 Clave primaria

Si no declaras ninguna, se añade `id = ui.Auto()`. `Cliente.pk` siempre apunta a
la clave primaria, se llame como se llame la columna:

```python
cliente = Cliente.objects.get(pk=1)
cliente.pk          # 1
```

### 3.6 Crear, guardar, refrescar y borrar

```python
ana = Cliente(nombre="Ana", edad=34)   # sin tocar la base todavía
ana.save()                             # INSERT (o UPDATE si ya tiene pk)
ana.edad = 35                          # cambio en memoria
ana.save()                             # UPDATE
ana.refresh()                          # relee la fila
ana.delete()                           # DELETE

ana.to_dict()                          # {"id": 1, "nombre": "Ana", ...}
```

`Cliente(nombre=…)` valida los nombres de campo: un atributo que no existe lanza
`TypeError`, así no se pierden datos por una errata.

### 3.7 Relaciones

`ui.FK` guarda el `pk` de otra tabla. No hay integridad referencial automática ni
`JOIN`: se resuelve con una segunda consulta, que es explícito y suficiente para
estas apps.

```python
class Autor(ui.Model):
    nombre = ui.Str(max_length=80)

    class Meta:
        table = "autores"


class Libro(ui.Model):
    titulo = ui.Str(max_length=120)
    autor = ui.FK("autores")
    publicado = ui.Date(null=True)

    class Meta:
        table = "libros"


libro = Libro(titulo="Rayuela", autor=1)
autor = Autor.objects.get(pk=libro.autor)
```

### 3.8 Cargar un `models.py` suelto

Las migraciones ya lo hacen por ti (`migrations.models` del JSON). Si lo
necesitas a mano:

```python
from interui.orm import declared_models

modelos = declared_models("models.py")      # [Cliente, Libro, ...]
```

---

## 4. Consultas (ORM)

`Modelo.objects` es el punto de entrada. Las consultas son perezosas: se ejecutan
al iterar, contar o pedir un objeto.

| Método | Devuelve | Ejemplo |
|---|---|---|
| `objects.all()` | lista | `Cliente.objects.all()` |
| `objects.filter(**f)` | consulta | `Cliente.objects.filter(edad__gte=18)` |
| `objects.exclude(**f)` | consulta | `Cliente.objects.exclude(activo=False)` |
| `objects.get(**f)` | un objeto | `Cliente.objects.get(pk=1)` |
| `objects.order_by(*f)` | consulta | `Cliente.objects.order_by("-edad")` |
| `objects.first()` / `.last()` | objeto o `None` | |
| `objects.count()` / `.exists()` | número / booleano | |
| `objects.create(**f)` | objeto guardado | `Cliente.objects.create(nombre="Ana")` |
| `objects.bulk_create(lista)` | lista guardada | |

Sobre una consulta: `.filter()`, `.exclude()`, `.order_by()`, `.limit(n)`,
`.offset(n)`, `.all()`, `.first()`, `.last()`, `.count()`, `.exists()`,
`.values()` (filas como diccionarios), `.update(**f)`, `.delete()`.

Operadores (con `campo__operador`):

| Operador | Significado |
|---|---|
| `exact` (o nada) | igual |
| `ne` | distinto |
| `gt`, `gte`, `lt`, `lte` | comparaciones |
| `in` | dentro de una lista |
| `contains` | contiene el texto |
| `startswith`, `endswith` | empieza / termina por |
| `isnull` | es `NULL` (`True`) o no (`False`) |

```python
Cliente.objects.create(nombre="Ana", edad=34)

Cliente.objects.all()
Cliente.objects.filter(edad__gte=18).order_by("-edad")
Cliente.objects.filter(nombre__contains="an", email__isnull=True)
Cliente.objects.filter(edad__in=[18, 21, 30])
Cliente.objects.exclude(activo=False)
Cliente.objects.get(nombre="Ana")            # DoesNotExist / MultipleObjectsReturned
Cliente.objects.count(), Cliente.objects.exists()
Cliente.objects.all().limit(10).offset(20)

ana = Cliente.objects.get(nombre="Ana")
ana.edad = 35
ana.save()
```

Errores tipados, para `try/except`:

```python
from interui.orm import DoesNotExist, MultipleObjectsReturned

try:
    cliente = Cliente.objects.get(nombre="Ana")
except DoesNotExist:
    cliente = None
```

`Model.DoesNotExist` hace lo mismo que `DoesNotExist`, si prefieres no importar.

---

## 5. Migraciones

El flujo es el de Django: declaras modelos, generas la migración, la aplicas.
Entre una y otra, `interui` compara el esquema guardado en la última migración con
el que describen tus modelos.

```bash
interui db makemigrations      # compara models.py con la última migración
interui db migrate             # aplica las pendientes
interui db status              # ✔ aplicada · pendiente
```

```text
[interui] migración creada: migrations/0002_auto.json
[interui] aplicada 0002_auto
```

Qué detecta:

| Cambio en `models.py` | Operación |
|---|---|
| modelo nuevo | `CreateModel` |
| campo nuevo | `AddField` |
| campo borrado | `RemoveField` (pide `--force`) |
| modelo borrado | `DeleteModel` (pide `--force`) |
| tipo, longitud, `null`, `unique` o `default` cambiados | `AlterField` |

Los cambios que **borran datos** no se generan solos: `makemigrations` se niega y
dice cuáles son. Si es lo que quieres, repite con `--force`.

```bash
interui db makemigrations --force
```

Cada migración es un JSON legible, versionable en Git, con las operaciones y el
**estado completo** del esquema (así no hace falta encadenar todas para saber
cómo está la base):

```json
{
  "name": "0002_auto",
  "operations": [
    { "op": "AddField", "table": "clientes", "database": "default",
      "column": { "name": "email", "type": "varchar", "max_length": 120, "null": true } },
    { "op": "AlterField", "table": "clientes", "database": "default",
      "column": { "name": "nombre", "type": "varchar", "max_length": 120 },
      "previous": { "name": "nombre", "type": "varchar", "max_length": 80 } }
  ],
  "state": { "tables": { "...": {} } }
}
```

Detalles que conviene saber:

- Las migraciones aplicadas se registran en la tabla `interui_migrations` de cada
  base; `interui db status` la lee.
- `AlterField` en SQLite reconstruye la tabla copiando los datos; en PostgreSQL y
  MySQL usa `ALTER COLUMN` / `MODIFY`.
- Los motores `file` y `mongo` no tienen esquema: las migraciones se generan y se
  marcan como aplicadas, pero no cambian columnas.
- Cambiar de motor = editar `interui.json` y volver a generar el esquema
  (`interui db makemigrations --force`). Los datos no se copian solos.

---

## 6. Referencia de la CLI

| Comando | Qué hace |
|---|---|
| `interui init [carpeta]` | asistente: `interui.json`, `app.py`, `models.py` y `migrations/`. |
| `interui db makemigrations [nombre]` | crea la migración con los cambios. |
| `interui db migrate` | aplica todas las pendientes. |
| `interui db status` | lista las migraciones y su estado. |
| `interui run app.py` | abre la app (`--window desktop\|browser\|none`). |
| `interui new carpeta` | proyecto mínimo, sin base de datos. |
| `interui build app.py` | ejecutable autónomo. |
| `interui doctor` | revisa el entorno. |

Opciones de `db`:

| Opción | Comando | Efecto |
|---|---|---|
| `--force` | `makemigrations` | permite `RemoveField` / `DeleteModel`. |
| `--config ruta` | los tres | usa otro `interui.json`. |

Salida: `0` si todo fue bien, `1` si la configuración o el motor fallan (el
mensaje va a `stderr`, así que se puede usar en un script).

Los mismos pasos, desde Python:

```python
from interui import Config, db, migrations

cfg = Config.load()
db.configure(cfg)

ruta = migrations.makemigrations(cfg)      # Path o None si no hay cambios
aplicadas = migrations.migrate(cfg)        # ["0001_initial", ...]
estado = migrations.status(cfg)            # [{"name", "applied", "operations"}]
```

---

## 7. La ORM dentro de la interfaz

Un CRUD completo: la tabla se lee en cada render, así que al guardar o borrar
basta con `app.refresh()` para ver los cambios.

```python
from pathlib import Path

import interui as ui

app = ui.App("Clientes · datos")

settings = ui.Config({
    "app": {"name": "Clientes"},
    "databases": {
        "default": {"engine": "sqlite", "name": str(Path(app.data_dir) / "clientes.db")}
    },
})
ui.db.configure(settings)


class Cliente(ui.Model):
    nombre = ui.Str(max_length=80, unique=True)
    activo = ui.Bool(default=True)

    class Meta:
        table = "clientes"
        order = ["nombre"]


ui.db.backend("default").create_table("clientes", Cliente.columns())
if not Cliente.objects.exists():
    Cliente.objects.create(nombre="Ana Torres")
    Cliente.objects.create(nombre="Luis Pérez")

filtro = app.state("filtro", "")


def crear(evento):
    nombre = str(getattr(evento, "value", "") or "").strip()
    if not nombre:
        app.notify("El nombre es obligatorio", "warning", icon=ui.icons.alert)
        return
    if Cliente.objects.filter(nombre=nombre).exists():
        app.notify("Ese cliente ya existe", "error", icon=ui.icons.alert)
        return
    Cliente.objects.create(nombre=nombre)
    app.notify(f"«{nombre}» añadido", "success", title="Guardado", icon=ui.icons.check)
    app.refresh()


def borrar(pk):
    Cliente.objects.filter(pk=pk).delete()
    app.refresh()


@app.page("/")
def index():
    clientes = Cliente.objects.filter(nombre__contains=filtro.get()).all()
    filas = [
        [
            ui.Text(cliente.nombre),
            ui.Badge("activo" if cliente.activo else "inactivo"),
            ui.IconButton(ui.icons.trash, label="Borrar", on_click=lambda pk=cliente.pk: borrar(pk)),
        ]
        for cliente in clientes
    ]
    return ui.Screen(
        ui.Container(pad=ui.pad.py_8)(
            ui.Heading("Clientes", level=1),
            ui.Row(gap=ui.gap.all_3)(
                ui.Input(placeholder="Buscar…", icon=ui.icons.search, value=filtro, on_input=filtro),
                ui.Button(
                    "Nuevo cliente",
                    icon=ui.icons.plus,
                    on_click=lambda: ui.dialog.input(
                        "Nombre", title="Nuevo cliente", on_accept=crear
                    ),
                ),
            ),
            ui.Card(pad=ui.pad.all_2)(
                ui.Table(
                    headers=["Nombre", "Estado", ""],
                    rows=filas,
                    empty="Sin clientes todavía",
                )
            ),
            ui.Muted(f"{Cliente.objects.count()} clientes en la base de datos"),
        )
    )


if __name__ == "__main__":
    app.run()
```

Piezas que intervienen:

- `ui.Config({...})` — configuración en memoria, sin archivo (útil en demos y tests).
- `ui.db.configure(settings)` — registra la base para que `Model` la encuentre.
- `Cliente.columns()` — las columnas que el modelo describe, para crear la tabla
  sin migraciones.
- `app.refresh()` — vuelve a renderizar la página actual leyendo la base otra vez.

En un proyecto real no hace falta `create_table` ni `Config` a mano: usas
`ui.App.from_config()`, `interui db makemigrations` y `interui db migrate`.

Otro ejemplo completo, con buscador y avisos:
[`examples/11_datos.py`](../examples/11_datos.py).

---

## 8. Errores frecuentes

| Mensaje | Causa | Solución |
|---|---|---|
| `no such table: clientes` | la migración no se aplicó (o falta `create_table`) | `interui db makemigrations && interui db migrate` |
| `No existe el archivo de modelos: …` | `migrations.models` apunta a otro sitio | escribe la ruta correcta en `interui.json` |
| `interui: no encuentro interui.json` | estás en otra carpeta | ejecuta desde el proyecto o `--config ruta` |
| `Falta el driver de PostgreSQL (psycopg)` | el extra no está instalado | `pip install "interui[postgres]"` |
| `Estos cambios borran datos y no se aplican solos` | `RemoveField`/`DeleteModel` | revisa el modelo o repite con `--force` |
| `DoesNotExist` | `.get()` sin resultados | usa `.filter().first()` o captura la excepción |
| `MultipleObjectsReturned` | `.get()` con más de una fila | filtra por `pk` o usa `.first()` |
| `filtro no soportado: campo__xyz` | operador mal escrito | revisa la tabla de operadores |
| `Cliente no tiene …` | `Cliente(campo_inexistente=…)` | corrige el nombre o declara el campo |
| `mongo` guarda pero `status` no cambia columnas | los motores de documentos no tienen esquema | es normal: usa `Json` para lo variable |

---

## 9. Recetas

**Datos iniciales.** Un módulo que se ejecuta una vez:

```python
import interui as ui

from models import Cliente

if not Cliente.objects.exists():
    Cliente.objects.bulk_create([
        Cliente(nombre="Ana Torres"),
        Cliente(nombre="Luis Pérez"),
    ])
```

**Probar sin servidor.** `sqlite` y `file` no necesitan nada instalado, así que
sirven para tests y para el ejecutable empaquetado:

```python
from interui import Config, db

base = Config({"databases": {"default": {"engine": "sqlite", "name": ":memory:"}}})
db.configure(base)
```

**Empezar de cero.** Borra `data/` y `migrations/`, y vuelve a migrar:

```bash
rm -rf data migrations && interui db makemigrations && interui db migrate
```

**Cambiar de SQLite a PostgreSQL.** Instala el extra, edita `interui.json` y
genera el esquema en la base nueva:

```bash
pip install "interui[postgres]"
interui db makemigrations --force
interui db migrate
```

---

## 10. Límites (a propósito)

- No hay `JOIN` ni relaciones automáticas: `FK` guarda el `pk` y resuelves con otra
  consulta.
- No hay transacciones que abarquen varios modelos ni bloqueos optimistas.
- No hay `select_related`, `prefetch_related` ni índices compuestos.
- SQLite no permite cambiar un tipo con `ALTER TABLE`: `AlterField` reconstruye la
  tabla (los datos se copian, pero con tablas enormes tarda).
- Las migraciones describen columnas, no datos: para rellenar usa un script.

Si necesitas algo de eso, el ORM sigue siendo la puerta de entrada y siempre
puedes bajar a `ui.db.backend("default")` para SQL directo.
