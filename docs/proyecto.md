# Anatomía de un proyecto

Un proyecto de interUI es una carpeta con una estructura fija. Conocerla te
ahorra buscar dónde va cada cosa: **`main.py` abre la app**, **`iui.py` ejecuta
comandos**, **`interui.json` guarda la configuración** y el paquete del proyecto
(`mi_app/`) solo tiene configuración: **los modelos y las páginas viven en las
apps**.

```text
mi_app/
├── main.py                 ← punto de entrada: crea todo y abre la ventana
├── iui.py                  ← comandos del proyecto
├── interui.json            ← configuración
├── requirements.txt
├── README.md
├── .gitignore
├── mi_app/                 ← el paquete del proyecto (solo configuración)
│   ├── __init__.py
│   └── app.py              ← construye la App y el armazón de la ventana
├── ventas/                 ← una app del proyecto (`iui.py startapp ventas`)
│   ├── models.py           ← sus tablas
│   ├── forms.py            ← sus formularios
│   ├── tables.py           ← su tabla (columnas, colores, clic, menú)
│   ├── views.py            ← sus páginas (una línea cada una)
│   ├── urls.py
│   └── README.md
├── migrations/             ← migraciones (se versionan en git)
└── data/                   ← base de datos y archivos (no se versiona)
```

---

## 1. `main.py`: el punto de entrada

Es lo que se ejecuta para abrir la app. Siempre hace lo mismo, en este orden:

```python
def prepare_database() -> None:
    """Aplica las migraciones pendientes antes de abrir la ventana."""
    settings = config_module.load(CONFIG)
    db_module.configure(settings)
    migrations_module.migrate(settings)


def main() -> None:
    prepare_database()
    create_app().run()
```

1. **Lee `interui.json`** y configura la base de datos.
2. **Aplica las migraciones pendientes**: si la base está vacía, la crea; si tu
   equipo añadió un modelo, la actualiza. La app siempre arranca con el esquema
   al día.
3. **Construye la `App`** (`create_app()`) y **abre la ventana**.

Los pasos 1 y 2 no son obligatorios (podrías llamar a `create_app().run()` y
nada más), pero dejarlos aquí evita el error clásico: «la app abre pero la tabla
no existe». Si la base de datos falla, `prepare_database()` avisa por consola y
la ventana se abre igual; las vistas muestran un aviso en lugar de romperse.

> **Por qué hay dos archivos y no uno.** `main.py` abre la app; `iui.py` ejecuta
> tareas de mantenimiento (`startapp`, `makemigrations`, `migrate`…). Separarlos
> permite que un comando de consola nunca tenga que abrir una ventana y que
> `python main.py` sea siempre el gesto de «arranca la app».

---

## 2. `iui.py`: los comandos del proyecto

Es un archivo de veinte líneas que delega en `interui.cli.project_main()`:

```python
from interui.cli import project_main

if __name__ == "__main__":
    raise SystemExit(project_main())
```

Al ejecutarse busca `interui.json` desde la carpeta actual hacia arriba, así que
funciona igual desde la raíz del proyecto que desde una subcarpeta.

```bash
python iui.py                   # abre la ventana (igual que `run`)
python iui.py run
python iui.py startapp ventas
python iui.py makemigrations
python iui.py migrate
python iui.py status
python iui.py shell
python iui.py check
```

Referencia completa en [comandos.md](comandos.md).

---

## 3. `interui.json`: la configuración

Todo lo configurable vive aquí: nombre de la app, tamaño y tema de la ventana,
base de datos, apps instaladas y dónde están las migraciones. Se puede editar a
mano y admite variables de entorno con `${VARIABLE:valor_por_defecto}`.

```json
{
  "app": {
    "name": "mi_app",
    "title": "Mi Tienda — Gestión",
    "theme": "light",
    "width": 1180,
    "height": 780,
    "entry": "mi_app.app"
  },
  "databases": {
    "default": { "engine": "sqlite", "name": "data/app.db" }
  },
  "apps": [],
  "migrations": {
    "directory": "migrations",
    "models": []
  }
}
```

| Clave | Qué controla |
|---|---|
| `app.name` | Nombre corto del proyecto (el del paquete). |
| `app.title` | Nombre largo que se ve en la ventana. |
| `app.width` / `app.height` | Tamaño inicial de la ventana. |
| `app.theme` | `light` u `dark`. |
| `app.entry` | Módulo que define la app (`paquete.app`). |
| `databases` | Conexiones disponibles; `default` es la que usa el ORM. |
| `apps` | Apps del proyecto: sus rutas se registran solas. |
| `migrations` | Carpeta de migraciones y archivos de modelos. |

Referencia completa, con todos los motores y ejemplos:
[configuracion.md](configuracion.md).

---

## 4. El paquete del proyecto

El paquete (`mi_app/`) es **solo configuración**: dos archivos.

| Archivo | Pregunta que responde |
|---|---|
| `__init__.py` | ¿Cómo se llama el paquete? |
| `app.py` | ¿Cómo se construye la `App` y cuál es el armazón de la ventana? |

No hay `models.py`, `views.py` ni `urls.py`: los modelos, los formularios y las
páginas van en las **apps**, una por dominio (`ventas`, `personas`, `tareas`…).
Así una app se puede copiar de un proyecto a otro sin arrastrar el resto.

Mientras no haya ninguna app que registre la página `/`, la ventana muestra
«Hola mundo» centrado con una pista de cómo crear la primera. Esa bienvenida la
pone el framework, no un archivo del proyecto.

### `app.py`

```python
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = BASE_DIR / "interui.json"


def create_app() -> ui.App:
    """`App` del proyecto, con las rutas de todas sus apps."""
    return ui.App.from_config(CONFIG)


app = create_app()
```

`App.from_config()` lee `interui.json`, configura la base de datos y **registra
las rutas de cada app** de la lista `apps`. El módulo deja además una instancia
`app` lista para usar (`from mi_app.app import app`), que es lo que espera la
CLI.

**Si quieres un menú**, el armazón se pone aquí, una sola vez:

```python
def create_app() -> ui.App:
    app = ui.App.from_config(CONFIG)
    app.layout = ui.AppShell(
        title_bar=ui.TitleBar("Mi app", icon=ui.icons.layers),
        header=ui.MenuBar(
            {
                "Archivo": [ui.ContextItem("Salir", icon=ui.icons.power, on_click=salir)],
                "Ventas": [ui.ContextItem("Clientes", icon=ui.icons.users, href="/clientes")],
            },
            icons={"Archivo": ui.icons.folder},
        ),
        status=ui.StatusBar(ui.text("Listo")),
    )
    return app
```

Con `app.layout`, **todas** las páginas se pintan dentro del armazón y cada
vista devuelve solo su contenido. Los `href` de los menús navegan entre páginas
sin recargar. Se explica en [menús](menus.md#el-armazón-de-toda-la-aplicación-applayout).

### Dónde va cada cosa

| Quiero… | Va en |
|---|---|
| una tabla | `<app>/models.py` |
| un formulario | `<app>/forms.py` |
| cómo se ve la tabla (columnas, colores, clic, menú) | `<app>/tables.py` |
| una página | `<app>/views.py` |
| una ruta nueva | `<app>/urls.py` |
| el menú y la barra de título | `mi_app/app.py` (`app.layout`) |
| la base de datos y la ventana | `interui.json` |

Una vista es una función sin argumentos (o con los parámetros de la ruta) que
devuelve un componente. Las vistas se ejecutan **en cada render**; por eso
conviene que sean rápidas y que no guarden estado en variables globales: el
estado va en `ui.state()` (señales) o en la base de datos.

La vista más corta que existe:

```python
# ventas/views.py
def inicio() -> ui.Component:
    return ui.RecordPage(VentaForm(), title="Ventas")
```

Y el armazón (barra de título, menú, barra de estado) se pone una sola vez en
`mi_app/app.py` con `app.layout`:

```python
app.layout = ui.AppShell(
    title_bar=ui.TitleBar("Mi app", icon=ui.icons.layers),
    header=ui.MenuBar({"Ventas": [ui.ContextItem("Clientes", href="/clientes")]}),
    status=ui.StatusBar(ui.text("Listo")),
)
```

Con eso, **todas** las páginas se pintan dentro del armazón: el menú no
desaparece al navegar y ninguna vista lo repite. Está explicado en
[menús y armazón](menus.md) y en el [tutorial](guia.md#paso-3-poner-un-menú).

---

## 5. Las apps: módulos que se enchufan solas

Una app es una carpeta con `models.py` (tablas), `forms.py` (formularios),
`tables.py` (cómo se ve y se usa la tabla), `views.py` (páginas) y `urls.py`
(rutas). Cada cosa vive en su archivo y la vista solo une las piezas. Se crea con
un comando y **no hay que registrarla a mano**:

```bash
python iui.py startapp ventas
```

Ese comando:

1. crea `ventas/` con los cinco archivos y un `README.md`, todos listos para
   usar: la página `/ventas` ya trae formulario de alta y tabla de lo guardado;
2. añade `"ventas"` a la lista `apps` de `interui.json`;
3. añade `ventas/models.py` a `migrations.models`.

Al arrancar, `App.from_config()` importa `ventas/urls.py` y registra sus rutas.
Si prefieres controlar el orden, cada app puede exponer su propio
`register(app)`; si no, se usan sus `urlpatterns`.

**Cuándo crear una app y cuándo no.** Una app agrupa un dominio con sus modelos
y sus páginas (por ejemplo, «ventas» o «inventario»). Si tu proyecto tiene una
sola pantalla, no hace falta: escribe las vistas en el paquete del proyecto y ya.

### `forms.py`

Cada app trae su archivo de formularios, separado de las vistas: se declaran
allí y la vista solo los coloca en la página. Se explica entero en
[formularios](formularios.md).

```python
# ventas/forms.py
class VentaForm(ui.ModelForm):
    model = Venta
    fields = ["nombre", "descripcion", "activo"]      # qué campos y en qué orden
    labels = {"descripcion": "Detalle"}               # cómo se llaman
```

```python
# ventas/views.py: el formulario y la tabla, sin repetir los campos
def inicio() -> ui.Component:
    form = VentaForm()
    return ui.Screen(
        ui.Container(pad=ui.pad.py_10)(
            ui.Heading("Ventas", level=1),
            ui.Muted(ui.RecordCounter(form)),
            form,
            ui.RecordTable(form),
        )
    )
```

---

## 6. Migraciones y datos

Las migraciones son **del proyecto**, no de cada app: una sola carpeta
`migrations/` con archivos JSON legibles. Así un único `migrate` pone al día
todos los modelos, vengan de la app que vengan.

```bash
python iui.py makemigrations   # compara los models.py con la última migración
python iui.py migrate          # aplica las pendientes
python iui.py status           # qué falta por aplicar
```

Los archivos de `migrations/` **se versionan en git**: son el historial del
esquema. `data/` no: contiene la base de datos y los archivos que genere la app.

Puedes cambiar de motor (SQLite, PostgreSQL, MySQL, MongoDB o archivos) editando
`databases` en `interui.json`; el código de tus vistas no cambia. Detalles en
[datos.md](datos.md).

---

## 7. Cómo encaja todo al arrancar

```text
python main.py
   │
   ├─ lee interui.json ................ configuración
   ├─ aplica migraciones .............. base de datos al día
   ├─ create_app()
   │     ├─ App.from_config() ......... tema, tamaño, datos
   │     │     └─ apps → rutas ........ ventas/urls.py, …
   │     └─ urls.register(app) ........ rutas del proyecto
   └─ app.run()
         ├─ servidor local en 127.0.0.1 (puerto efímero)
         ├─ ventana nativa (WebKit / WebView2 / WebKitGTK)
         └─ el cliente conecta → se renderiza la primera vista
```

Cada clic viaja como un mensaje por un canal local, Python ejecuta el handler y
devuelve el HTML nuevo, que sustituye al anterior sin recargar la ventana. El
servidor escucha solo en `127.0.0.1`, en un puerto aleatorio, y muere al cerrar
la ventana: no queda nada expuesto.

---

## Siguiente paso

- [Tutorial](guia.md): construye una app completa, paso a paso.
- [Controles](controles.md): qué puedes poner en una vista.
- [Datos](datos.md): modelos, consultas y migraciones con detalle.
