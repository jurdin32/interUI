# Datos: configuración, modelos y migraciones

interUI trae lo mínimo para trabajar con datos sin montar medio Django:
un archivo `interui.json` que describe el proyecto, un asistente de consola que lo
crea, modelos declarativos al estilo de Django y migraciones que se generan solas.
Funciona con SQLite y con archivos JSON usando solo la biblioteca estándar; los
demás motores son un extra de `pip`.

---

## 1. El asistente: `interui init`

```bash
interui init tienda
```

```
Nombre de la aplicación [tienda]: Tienda
Motor de base de datos:
  1. SQLite (un archivo, sin servidor)
  2. PostgreSQL
  3. MySQL / MariaDB
  4. MongoDB
  5. Archivos JSON (sin servidor)
Elige un número [1]: 1
  name [data/app.db]:
```

Crea esto:

```text
tienda/
├── interui.json        ← el punto de partida de la app
├── app.py              ← ui.App.from_config()
├── models.py           ← tus modelos
├── migrations/         ← migraciones generadas
└── data/               ← la base de datos (SQLite)
```

Sin preguntas (CI, scripts):

```bash
interui init tienda --no-input --name Tienda --db postgres \
    --host localhost --port 5432 --user tienda --password "" --database tienda
```

| Opción | Para qué |
|---|---|
| `--db` | `sqlite`, `postgres`, `mysql`, `mongo` o `file`. |
| `--database` | Ruta del archivo (SQLite/archivos) o nombre de la base. |
| `--host`, `--port`, `--user`, `--password` | Conexión de servidor. |
| `--no-input` | No pregunta nada; usa los valores por defecto. |
| `--migrate` | Genera y aplica la migración inicial. |
| `--force` | Sobrescribe archivos existentes. |

---

## 2. `interui.json`

Es un JSON (no un `.env`) con secciones explícitas. Se lee con acceso por puntos:

```python
from interui import config

cfg = config.load()
cfg.app.name                  # "Tienda"
cfg.databases.default.engine  # "sqlite"
cfg.database().url            # "sqlite:///data/app.db"
```

```json
{
  "app": {
    "name": "Tienda",
    "version": "0.1.0",
    "theme": "light",
    "width": 1180,
    "height": 780,
    "entry": "app.py"
  },
  "databases": {
    "default": { "engine": "sqlite", "name": "data/app.db" },
    "reportes": {
      "engine": "postgres",
      "host": "localhost", "port": 5432,
      "user": "tienda", "password": "${PG_PASSWORD}", "name": "reportes"
    }
  },
  "migrations": { "directory": "migrations", "models": "models.py" }
}
```

- **Secretos fuera del JSON**: `${PG_PASSWORD}` (o `${PG_PASSWORD:valor}`) se
  sustituye desde el entorno, como en un `.env` pero dentro del JSON.
- **Varias bases**: cada alias (`default`, `reportes`, `archivos`…) tiene su
  motor y sus datos. Un modelo elige la suya con `Meta.database`.
- **Rutas relativas** al propio `interui.json`, no al directorio actual.
- `config.save()` reescribe el archivo; `interui.App.from_config()` construye la
  ventana con esos valores y deja la configuración en `app.config`.

### Motores

| `engine` | Necesita | Datos |
|---|---|---|
| `sqlite` | nada (biblioteca estándar) | `"name": "data/app.db"` |
| `file` | nada | `"name": "data"` → un `.json` por tabla |
| `postgres` | `pip install "interui[postgres]"` | host, port, user, password, name |
| `mysql` | `pip install "interui[mysql]"` | host, port, user, password, name |
| `mongo` | `pip install "interui[mongo]"` | host, port, name |

Si falta el driver, el error dice exactamente qué instalar.

---

## 3. Conexión directa

```python
from interui import config, db

cfg = config.load()
base = db.connect(cfg.database())

base.create_table("clientes", [
    db.Column("id", "int", primary_key=True, auto=True),
    db.Column("nombre", "varchar", null=False, max_length=80),
])
base.insert("clientes", {"nombre": "Ana"})
base.select("clientes", where=[("nombre", "=", "Ana")], order=["-id"], limit=10)
```

`db.configure(cfg)` registra los alias y `db.backend("default")` los reutiliza (lo
hacen el ORM y las migraciones). Para los motores con esquema existen
`create_table`, `add_column`, `remove_column`, `alter_column`, `drop_table`
y `tables()`; los motores de documentos las aceptan como no-op.

---

## 4. Modelos

```python
import interui as ui

class Cliente(ui.Model):
    nombre = ui.Str(max_length=80, unique=True)
    email  = ui.Str(max_length=120, null=True)
    edad   = ui.Int(null=True)
    activo = ui.Bool(default=True)
    alta   = ui.DateTime(auto_now_add=True)
    extra  = ui.Json(null=True)
    notas  = ui.LongText(null=True)

    class Meta:
        table = "clientes"
        database = "default"
        order = ["nombre"]
```

| Campo | Columna | Notas |
|---|---|---|
| `ui.Auto()` | entero autoincremental | se añade como `id` si no declaras clave |
| `ui.Int()` | entero | |
| `ui.Str(max_length=…)` | `VARCHAR(n)` | `null`, `unique`, `default` |
| `ui.LongText()` | `TEXT` | se llama así porque `Text` es el control |
| `ui.Bool()` | booleano | |
| `ui.Float()` | real | |
| `ui.Date()` / `ui.DateTime()` | fecha / fecha y hora | `auto_now_add`, `auto_now` |
| `ui.Json()` | JSON | se serializa solo |
| `ui.Blob()` | binario | |
| `ui.FK("tabla")` | entero | referencia simple, sin FK del motor |

### Consultas

```python
Cliente.objects.create(nombre="Ana", edad=34)

Cliente.objects.all()
Cliente.objects.filter(edad__gte=18).order_by("-edad")
Cliente.objects.filter(nombre__contains="an", email__isnull=True)
Cliente.objects.exclude(activo=False)
Cliente.objects.get(pk=1)              # DoesNotExist / MultipleObjectsReturned
Cliente.objects.count(), Cliente.objects.exists()
Cliente.objects.all().limit(10).offset(20)
Cliente.objects.first(), Cliente.objects.last()

ana = Cliente.objects.get(nombre="Ana")
ana.edad = 35
ana.save()
ana.refresh()
ana.delete()
```

Operadores: `exact`, `ne`, `gt`, `gte`, `lt`, `lte`, `in`, `contains`,
`startswith`, `endswith`, `isnull`. `pk` siempre apunta a la clave primaria.

---

## 5. Migraciones

```bash
interui db makemigrations      # compara models.py con la última migración
interui db migrate             # aplica las pendientes
interui db status              # ✔ aplicada · pendiente
```

```
[interui] migración creada: migrations/0001_initial.json
[interui] aplicada 0001_initial
```

Cada migración es un JSON legible con las operaciones y el **estado completo**
del esquema:

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

- Operaciones: `CreateModel`, `AddField`, `RemoveField`, `AlterField` y
  `DeleteModel`.
- Los cambios que **borran datos** (`RemoveField`, `DeleteModel`) no se generan
  solos: `makemigrations` se niega y explica cuáles son. Si es lo que quieres,
  repite con `--force`.
- `AlterField` en SQLite reconstruye la tabla copiando los datos; en PostgreSQL y
  MySQL usa `ALTER COLUMN`/`MODIFY`.
- El registro de migraciones aplicadas vive en la tabla `interui_migrations` de
  cada base.
- Los motores `file` y `mongo` no tienen esquema: las migraciones se generan y se
  marcan como aplicadas, pero no cambian columnas.

### Flujo típico

```bash
interui init tienda --name Tienda --db sqlite --migrate
# editas models.py
interui db makemigrations
interui db migrate
```

---

## 6. Recetas

**Cambiar de motor.** Edita `interui.json`, ajusta `engine` y sus datos, y crea
una migración inicial nueva (el esquema se genera otra vez):

```bash
interui db makemigrations --force   # si el modelo no cambió, no generará nada
```

**Dos bases en el mismo proyecto.**

```json
"databases": {
  "default":  { "engine": "sqlite", "name": "data/app.db" },
  "analitica": { "engine": "postgres", "host": "localhost", "name": "analitica",
                 "user": "app", "password": "${PG_PASSWORD}" }
}
```

```python
class Evento(ui.Model):
    nombre = ui.Str(max_length=60)

    class Meta:
        table = "eventos"
        database = "analitica"
```

**Probar sin servidor.** `sqlite` y `file` no necesitan nada instalado, así que
sirven para tests y para el ejecutable empaquetado.
