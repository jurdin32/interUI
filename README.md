# interUI

**Framework para crear aplicaciones de escritorio en Python con HTML, Tailwind CSS y JavaScript.**

No es un framework web: cada app se abre en una **ventana nativa** del sistema
operativo (WebKit en macOS, WebView2 en Windows, WebKitGTK en Linux) sin barra de
direcciones, sin navegador y sin conexión a internet. El HTML se genera en Python,
Tailwind lo compila Vite, y JavaScript solo transporta eventos.

```python
from interui import window, text, button, state

count = state(0)

window(
    "Mi primera app",
    text("Hola, escritorio"),
    text("Pulsaciones: ", count),          # se actualiza solo
    button("Pulsar", on_click=count.inc),  # sin lambdas ni eventos
).run()
```

Eso abre una **ventana nativa** con un texto y un botón. No hay HTML, ni CSS, ni
JavaScript que escribir.

Si prefieres el control total, la API larga sigue disponible:

```python
from interui import App, Button, Card, Container, Heading, Screen, icons, margin, pad

app = App("Mi primera app")


@app.page("/")
def index():
    clicks = app.state("clicks", 0)
    return Screen(
        Container(size="prose", pad=pad.py_16)(
            Heading("Hola, escritorio", level=1),
            Card(margin=margin.mt_6)(
                Button(
                    f"Pulsaciones: {clicks.get()}",
                    icon=icons.plus,
                    on_click=lambda: clicks.set(clicks.get() + 1),
                )
            ),
        )
    )


app.run()
```

---

## Actualizar interUI

> **¿Ya tienes interUI instalado?** Un solo comando: mira si hay algo nuevo,
> descarga e instala lo que corresponda según cómo lo instalaste.
>
> ```bash
> iui update --run     # o: interui update --run
> ```
>
> Solo ver el comando, sin ejecutarlo: `iui update`.
>
> Si prefieres hacerlo a mano desde GitHub:
>
> ```bash
> pip install -U --force-reinstall "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"
> ```
>
> 📖 **Guía de actualización:** [docs/actualizar.md](docs/actualizar.md) ·
> 🚀 **Última versión:** <https://github.com/jurdin32/interUI/releases>

La aplicación avisa sola: al arrancar consulta (en segundo plano, sin bloquear la
ventana) si hay una versión más nueva y, si la hay, muestra un aviso con el
comando para copiar, `app.update_available` pasa a `True` y el log registra
`[interui] Hay una versión nueva…`. Se desactiva con `App(..., check_updates=False)`
o `INTERUI_NO_UPDATE_CHECK=1`.

---

## Índice

- [Documentación completa](docs/indice.md) — tutorial, temas, referencia y cómo se hace
- [Estado del proyecto](#estado-del-proyecto)
- [Multiplataforma](#multiplataforma)
- [Actualizar interUI](#actualizar-interui)
- [Instalación](#instalación)
- [Por qué el editor marca errores](#por-qué-el-editor-marca-errores-y-el-programa-funciona)
- [Tutorial paso a paso](#tutorial-paso-a-paso)
- [Inicio rápido](#inicio-rápido)
- [Cómo funciona una app](#cómo-funciona-una-app)
- [Rejilla de 12 columnas](#rejilla-de-12-columnas)
- [API compacta (recomendada)](#api-compacta-recomendada)
- [Estilos con notación de punto](#estilos-con-notación-de-punto)
- [Datos: configuración, modelos y migraciones](#datos-configuración-modelos-y-migraciones)
- [Controles](#controles)
- [Eventos](#eventos)
- [Estado reactivo](#estado-reactivo)
- [Diálogos y ventanas modales](#diálogos-y-ventanas-modales)
- [Armazón de app, menús y barras](#armazón-de-app-menús-y-barras)
- [Iconos](#iconos)
- [Integración con el escritorio](#integración-con-el-escritorio)
- [CLI](#cli)
- [Empaquetado en ejecutable](#empaquetado-en-ejecutable)
- [Publicar en PyPI](#publicar-en-pypi)
- [Estilos con Tailwind y Vite](#estilos-con-tailwind-y-vite)
- [Arquitectura](#arquitectura)
- [Pruebas](#pruebas)
- [Solución de problemas](#solución-de-problemas)
- [Documentación adicional](#documentación-adicional)

---

## Estado del proyecto

| Área | Estado |
|---|---|
| Motor de componentes y render HTML | ✅ estable |
| Rejilla responsive de 12 columnas | ✅ estable |
| Estilos por tokens (`bg=colors.red_500`, `pad=pad.py_6`) | ✅ estable |
| `interui.json` + modelos y migraciones (SQLite, archivos, PG, MySQL, Mongo) | ✅ estable |
| Catálogo de controles | ✅ ~230 exportaciones (`docs/controles.md`) |
| Shell, menús, barras e iconos propios | ✅ 204 iconos (`docs/iconos.md`) |
| Canal en vivo (WebSocket propio, sin dependencias) | ✅ estable |
| Ventana nativa + puente al sistema operativo | ✅ estable |
| CLI (`run`, `new`, `build`, `doctor`, `assets`) | ✅ estable |
| Tematización Tailwind vía Vite | ✅ estable |
| Distribución multiplataforma | ✅ macOS · Windows · Linux |

---

## Multiplataforma

El mismo código Python funciona sin cambios en los tres sistemas. Lo único que
cambia es el motor de render que aporta el sistema operativo:

| | macOS | Windows | Linux |
|---|---|---|---|
| Motor de ventana | WebKit (Cocoa) | WebView2 (Chromium) | WebKitGTK |
| Requisito del sistema | ninguno (WebKit incluido) | WebView2 Runtime (incluido en Windows 10/11 actualizados) | `libgtk-3-0` + `libwebkit2gtk-4.1-0` |
| Instalación de la ventana | `pip install "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"` | igual | igual |
| Ejecutable | `.app` (PyInstaller) | `.exe` | binario ELF |
| Selector de archivos | *sheet* nativo | diálogo Win32 | diálogo GTK |
| Notificaciones | Centro de notificaciones | cuadro nativo (`MessageBoxW`) | `notify-send` / `zenity` |
| Portapapeles | `pbcopy`/`pbpaste` | API Win32 por `ctypes` | `wl-copy` / `xclip` / `xsel` |
| Datos de la app | `~/Library/Application Support/<app>` | `%APPDATA%\<app>` | `$XDG_DATA_HOME/<app>` |

Detalles por plataforma:

```bash
# Linux: dependencias del motor de ventana (Debian/Ubuntu)
sudo apt install libgtk-3-0 libwebkit2gtk-4.1-0
# Fedora
sudo dnf install gtk3 webkit2gtk4.1
```

Notas de compatibilidad garantizadas por el framework:

- **Python 3.10 a 3.14** (los tests y el linter se ejecutan con `--target-version py310`).
- **Sin dependencias obligatorias**: el núcleo usa solo la biblioteca estándar
  (`socket`, `http.server`, `hashlib`, `threading`). `pywebview` es un extra.
- **Sin CDN ni recursos remotos**: CSS, JS, iconos y fuentes del sistema se sirven
  desde el propio paquete, así que la app funciona sin internet.
- **Rutas con `pathlib`** y directorios de datos por plataforma (`INTERUI_DATA_DIR`
  permite sobreescribirlos, útil en tests y en apps portables).
- **Sin consola**: en ejecutables de Windows (`--windowed`) `stdout` no existe;
  los mensajes van a `<data_dir>/interui.log` automáticamente.
- **Alta densidad de píxeles, zoom y temas claro/oscuro** gestionados por el motor
  del sistema y Tailwind.

---

## Instalación

### Instalar desde GitHub (la vía disponible hoy)

El paquete **todavía no está publicado en PyPI**, así que se instala directamente
del repositorio:

```bash
pip install "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"
```

- `[desktop]` añade `pywebview` (ventana nativa real). Sin el extra, el núcleo
  funciona en el navegador.
- **Fijar una versión**: añade `@v0.5.0` al final de la URL.
- **Actualizar**: repite el comando con `pip install -U`.
- Necesita `git` instalado y conexión la primera vez (pip compila el paquete con
  `hatchling`).

Variantes:

```bash
pip install "git+https://github.com/jurdin32/interUI.git"                        # núcleo
pip install "interui[desktop] @ git+https://github.com/jurdin32/interUI.git@v0.5.0"
pipx install "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"
uv add "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"
pip install -U --force-reinstall "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"
```

En `requirements.txt` (o `pyproject.toml`, `uv.lock`…):

```text
interui[desktop] @ git+https://github.com/jurdin32/interUI.git@v0.5.0
```

### El día que esté en PyPI

Cuando el primer release esté publicado, lo anterior se resume en:

```bash
pip install "interui[desktop]"      # desde PyPI (incluye ventana nativa)
```

El wheel trae el CSS de Tailwind compilado y el runtime JS: **no necesitas
Node.js ni internet** para usar el framework.

### Instalar para desarrollar el framework

```bash
git clone https://github.com/jurdin32/interUI.git
cd interUI
python -m venv venv
./venv/bin/pip install -e ".[desktop,dev]"

# Estilos: solo al cambiar la paleta o añadir clases nuevas
cd frontend && npm install && npm run build
```

Comprobación del entorno e **del intérprete correcto**:

```bash
interui doctor
python -c "import interui; print(interui.__version__, interui.__file__)"
```

Ese segundo comando es el que delata el 90 % de los «no funciona»: si la versión
es antigua o la ruta no es la de tu código, tu editor está usando otro entorno.
En VS Code: `Ctrl/Cmd + Shift + P` → *Python: Select Interpreter* → elige el
`venv` del proyecto.

👉 Guía completa de instalación y **publicación en PyPI**:
[`docs/publicar.md`](docs/publicar.md).

👉 Para **mantenerlo actualizado** (comandos por tipo de instalación, aviso en la
app y problemas frecuentes): [`docs/actualizar.md`](docs/actualizar.md).

---

## Tutorial paso a paso

El recorrido completo está en **[docs/guia.md](docs/guia.md)**: doce pasos en
orden, cada uno un archivo que se ejecuta tal cual, desde una ventana vacía
hasta la app con base de datos.

| Paso | Qué consigues |
|---|---|
| 1 | Una ventana vacía |
| 2 | Texto y tarjetas dentro |
| 3 | Un menú (Archivo, Ayuda) en la ventana |
| 4 | Que un botón ejecute tu código |
| 5 | Que la ventana se actualice sola (estado) |
| 6 | Ordenar todo en columnas |
| 7 | Varias páginas en la misma ventana |
| 8 | Un formulario que valida |
| 9 | Una tabla con búsqueda |
| 10 | Guardar entre sesiones |
| 11 | Un formulario hecho solo desde el modelo |
| 12 | El proyecto completo, con apps |

Cada bloque de código del tutorial se compila y se ejecuta en las pruebas
([`tests/test_guide.py`](tests/test_guide.py)), así que no puede quedarse
obsoleto.

---

## Inicio rápido

```bash
iui startproject mi_app     # sin nombre abre un asistente de configuración
cd mi_app
pip install -r requirements.txt
python main.py              # crea todo y abre la ventana nativa
```

El asistente pregunta el **nombre largo** de la ventana, el motor de base de
datos, la ruta del archivo, el tema y si aplicar ya la migración inicial. Todo se
puede pasar por parámetro si prefieres no responder preguntas.

Para añadir una app dentro del proyecto:

```bash
python iui.py startapp tareas
python iui.py makemigrations
python iui.py migrate
python main.py
```

Lo que crea (todo de escritorio, sin servidor web): **lo mínimo**, una ventana
con una etiqueta centrada que dice «Hola mundo».

```
mi_app/
├── main.py             # punto de entrada: crea todo y abre la ventana
├── iui.py              # comandos del proyecto
├── interui.json        # configuración
├── requirements.txt
├── README.md
├── .gitignore
├── mi_app/             # el paquete del proyecto (solo configuración)
│   ├── __init__.py
│   └── app.py          # crea la App y el armazón de la ventana
├── migrations/         # migraciones generadas
└── data/               # SQLite o archivos
```

Cuando necesites más, `python iui.py startapp tareas` añade una app con sus
modelos, sus formularios, sus vistas y sus rutas; la página `/tareas` ya
funciona (alta de registros y tabla con lo guardado).

`main.py` y `iui.py` se reparten el trabajo: `main.py` es el punto de entrada
(aplica las migraciones pendientes, crea la `App` y abre la ventana) e `iui.py`
es la consola de comandos.

Cada pieza tiene una responsabilidad y no se solapan:

| Pieza | Para qué |
|---|---|
| `main.py` | abre la app: aplica migraciones, construye la `App` y muestra la ventana |
| `iui.py` | comandos que nunca abren ventana: `startapp`, `makemigrations`, `migrate`, `status`, `shell`, `check` |
| `interui.json` | configuración: identidad, ventana, base de datos, apps y migraciones |
| `<app>/views.py` | qué se pinta en cada página |
| `<app>/urls.py` | qué vista responde a cada ruta |
| `<app>/forms.py` | formularios: un control por campo del modelo |
| `<app>/models.py` | modelos del ORM; `makemigrations` los convierte en tablas |
| `migrations/` | historial del esquema, en JSON legible y versionado |
| `data/` | base de datos y archivos de la app (fuera de git) |
| `<app>/` | apps del proyecto: modelos, formularios, vistas y rutas que se registran solas |

`iui` y `interui` son el mismo comando (`iui startproject`, `iui run`, `iui db
migrate`…). Si solo quieres un archivo suelto: `interui new mi_app`.

Contenido de `mi_app/app.py` (todo el paquete del proyecto):

```python
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG = BASE_DIR / "interui.json"


def create_app() -> ui.App:
    """`App` del proyecto, con las rutas de todas sus apps."""
    return ui.App.from_config(CONFIG)


app = create_app()
```

Ejemplos completos en [`examples/`](examples):

| Archivo | Qué muestra |
|---|---|
| [`00_minimo.py`](examples/00_minimo.py) | Ventana + texto + botón en 8 líneas (API compacta). |
| [`01_hello.py`](examples/01_hello.py) | Contador con la API explícita. |
| [`02_grid.py`](examples/02_grid.py) | Rejilla de 12 columnas y breakpoints. |
| [`03_catalog.py`](examples/03_catalog.py) | Catálogo visual de todos los controles. |
| [`04_desktop.py`](examples/04_desktop.py) | Integración nativa: diálogos, notificaciones, barra de título. |
| [`05_crud.py`](examples/05_crud.py) | **App completa**: alta/edición, búsqueda, validación, persistencia y exportación. |
| [`06_app_moderna.py`](examples/06_app_moderna.py) | Armazón de app, menús, iconos y diálogos. |
| [`07_estilos.py`](examples/07_estilos.py) | Estilos con tokens: colores, variantes, hex y degradados. |
| [`08_snackbars.py`](examples/08_snackbars.py) | Snackbars con icono, imagen, acción y duración. |
| [`09_app_shell.py`](examples/09_app_shell.py) | Sidebar a izquierda/derecha, modales por niveles y cierre. |
| [`10_multiventana.py`](examples/10_multiventana.py) | Varias ventanas, rutas independientes y cierre por ventana. |
| [`11_datos.py`](examples/11_datos.py) | Modelos, SQLite y una pantalla CRUD completa. |
| [`12_responsive.py`](examples/12_responsive.py) | Armazón por partes y todo adaptándose al tamaño de la ventana. |

Y un **proyecto completo de ejemplo**: [`examples/proyecto_tareas/`](examples/proyecto_tareas)
— creado con `iui startproject` + `iui startapp notas`, con `main.py`, `iui.py` y
SQLite (`python main.py` dentro de esa carpeta).

---

## Cómo funciona una app

```
┌──────────────────────── ventana nativa (WebKit / WebView2 / WebKitGTK) ────────────────────────┐
│  HTML + Tailwind renderizado                          JS runtime (interui.js)                  │
│  ┌──────────────────────────┐   eventos (click, input, submit…) por WebSocket   ┌────────────┐  │
│  │  <div id="iui-root">     │ ─────────────────────────────────────────────────▶ │  Python    │  │
│  │   controles de interui   │ ◀───────────────────────────────────────────────── │ handlers   │  │
│  └──────────────────────────┘        HTML nuevo (reconciliación por nodo)        └────────────┘  │
└────────────────────────────────────────────────────────────────────────────────────────────────┘
                     ▲                                                    │
                     │ puente nativo (pywebview.api)                      │ estado + señales
                     └────────────────────────────────────────────────────┘
         diálogos, notificaciones, portapapeles, controles de ventana
```

1. `@app.page("/")` registra una vista que devuelve un árbol de componentes.
2. Al abrir la ventana, Python renderiza ese árbol a HTML con clases Tailwind.
3. Cada control con handler recibe un `id` estable y se registra en el servidor.
4. Un clic viaja por WebSocket, se ejecuta el handler **en Python** y la vista se
   vuelve a renderizar; el cliente aplica solo los cambios (sin recargar).
5. El estado de los controles enfocados no se pisa mientras se escribe.

Rutas con parámetros tipados:

```python
@app.page("/cliente/<int:cliente_id>")
def cliente(cliente_id: int):
    return Screen(Heading(f"Cliente #{cliente_id}"))
```

Navegación entre vistas (sin recargar la ventana):

```python
ui.Button("Ir a ajustes", on_click=lambda: app.navigate("/ajustes"))
ui.Link("Ajustes", href="/ajustes")        # también intercepta enlaces internos
```

---

## Rejilla de 12 columnas

La rejilla es responsive: cada columna declara cuánto ocupa en móvil, tablet y
escritorio.

```python
ui.Row(
    ui.Col(span=12, md=6, lg=4)(ui.Card(title="A")(ui.Text("…"))),
    ui.Col(span=12, md=6, lg=4)(ui.Card(title="B")(ui.Text("…"))),
    ui.Col(span=12, md=12, lg=4)(ui.Card(title="C")(ui.Text("…"))),
    gap=6,                # separación
    align="stretch",      # items-stretch
)
```

| Breakpoint | Ancho mínimo | Ejemplo |
|---|---|---|
| (base) | 0 | `span=12` → 100 % |
| `sm` | 640 px | `sm=6` → 50 % |
| `md` | 768 px | `md=4` → 33 % |
| `lg` | 1024 px | `lg=3` → 25 % |
| `xl` | 1280 px | `xl=2` → 16 % |
| `2xl` | 1536 px | `xxl=1` |

También existen `offset` (desplazamiento), `order`, `Row(dense=True)` y la rejilla
nativa de Tailwind con `ui.Grid(cols=1, md=2, lg=4)`.

👉 Guía completa con patrones de dashboard, formularios y tarjetas:
[`docs/rejilla.md`](docs/rejilla.md).

---

## API compacta (recomendada)

Para el día a día hay una capa fina sobre los controles, pensada para escribir
poco y leer fácil.

### Una ventana y su contenido en una llamada

```python
from interui import window, text, button, state, toast

count = state(0)                     # señal (estado reactivo)

window(
    "Contador",
    text("Hola mundo"),
    text("Pulsaciones: ", count),    # texto reactivo: se repinta solo
    button("Pulsar", on_click=count.inc),
).run()
```

- `window(título, *contenido)` crea la app, registra la página `/` y la envuelve
  en `Screen + Container + Stack` (puedes ajustar `width`, `height`, `theme`,
  `container`, `pad` y `gap`).
- Los hijos se apilan en vertical con separación uniforme.

### Controles en minúsculas

Todos los controles tienen alias `snake_case`; el nombre indica qué son:

```python
from interui import text, title, card, input, table, progress, icon, row, icons

title("Panel", subtitle="Resumen del día")
card(title="Ventas")(progress(72, label="Objetivo"), icon("chart", size=6))
input(label="Buscar", icon=icons.search, placeholder="Escribe…")
table(headers=["A", "B"], rows=[["1", "2"]])
```

`ui.button is ui.Button`, `ui.input is ui.Input`, `ui.data_table is ui.DataTable`,
etc. Son exactamente los mismos controles: puedes mezclar ambas formas.

### Eventos sin ceremonia

Un handler puede ser cualquiera de estas cosas:

```python
def guardar():                 # 1. función sin parámetros
    toast("guardado", "success")

def al_pulsar(evento):          # 2. función con el evento
    print(evento.value)

nombre = state("")              # 3. una señal: guarda el valor del evento
activo = state(False)

button("Guardar", on_click=guardar)
button("Ver evento", on_click=al_pulsar)
input(value=nombre, on_input=nombre)          # escribir → nombre.set(texto)
switch("Activo", checked=activo, on_change=activo)   # checked → activo.set(bool)
button("+1", on_click=count.inc)              # métodos de señal: inc/dec/toggle
```

### Texto y valores reactivos

Cualquier hijo puede ser una señal o una función; se evalúa en cada render:

```python
count = state(0)
nombre = state("Ana")

text("Pulsaciones: ", count)
text("Saludo: ", lambda: f"Hola {nombre.get()}")
```

### Fila con columnas automáticas

`row(a, b, c)` reparte las 12 columnas sin escribir `Col`:

```python
from interui import row, card, text

row(
    card(title="Uno")(text("…")),
    card(title="Dos")(text("…")),
    card(title="Tres")(text("…")),
)
```

### Varias vistas

```python
from interui import window, view, text, button

window("Mi app", text("Inicio"))

@view("/ajustes")
def ajustes():
    return text("Ajustes")

# navega con ui.button("Ajustes", href="/ajustes") o app.navigate("/ajustes")
```

Resumen de la capa compacta:

| Elemento | Para qué |
|---|---|
| `window(title, *children)` | crea la ventana, la página `/` y el contenedor |
| `view(path)` | registra una vista adicional |
| `state(valor)` | señal ligada a la ventana (`get`, `set`, `update`, `inc`, `dec`, `toggle`) |
| `text`, `button`, `card`… | alias en minúsculas de todos los controles |
| `row(*children)` | rejilla de 12 con columnas iguales automáticas |
| `column(*children)` | apilado vertical |
| `title`, `subtitle` | título principal y texto secundario |
| `toast(msg, level, **opciones)` | snackbar flotante (`title`, `icon`, `image`, `duration`, `action`) |

---

## Estilos con notación de punto

Los controles aceptan el estilo por argumentos: el nombre dice **qué** se cambia
y el token dice **cuánto**. Ni una clase a mano.

```python
from interui import Card, Text, colors, font, pad, radius, shadow

Card(
    bg=colors.white,
    border=colors.slate_200,
    pad=pad.all_6,
    rounded=radius.xxl,
    shadow=shadow.md,
    hover_bg=colors.slate_50,
    dark_bg=colors.slate_900,
    md_pad=pad.p_8,
)(
    Text("Hola", font=font.lg.semibold, color=colors.slate_700),
)
```

Esto genera `bg-white border border-slate-200 p-6 rounded-2xl shadow-md
hover:bg-slate-50 dark:bg-slate-900 md:p-8` y `text-lg font-semibold
text-slate-700`: exactamente lo que escribirías en Tailwind, pero sin escribirlo.

- **Espacios de nombres**: `colors`, `pad`, `margin`, `gap`, `radius`, `shadow`,
  `border`, `font`, `width`, `height`, `opacity` y `flex`.
- **Variantes con prefijo**: `hover_bg`, `focus_ring`, `active_bg`, `dark_bg`,
  `md_pad`, `md_hover_bg`… (el punto de ruptura va primero).
- **Valores exactos** cuando Tailwind no llega: `colors.hex("#0f172a")`,
  `colors.rgb(34, 211, 238)`, `gradient.br(colors.fuchsia_500,
  colors.indigo_500)` o `pad.py("18px")`. Se emiten como CSS en línea, así que
  funcionan sin recompilar nada.
- **Nada desaparece**: `class_` y `style` siguen disponibles y siempre ganan.
- **También con puntos**: los iconos (`icons.car`, `icons.edit`) y los
  enumerados de los controles (`variant.danger`, `tone.muted`, `size.lg`).

👉 Referencia completa, tabla de argumentos y catálogo de tokens:
[`docs/estilos.md`](docs/estilos.md).

---

## Datos: configuración, modelos y migraciones

El asistente deja el proyecto listo: `interui.json` (el punto de partida),
`app.py`, `models.py` y `migrations/`.

```bash
interui init tienda --db sqlite --migrate
interui db makemigrations      # compara models.py con la última migración
interui db migrate             # aplica lo pendiente
interui db status              # ✔ aplicada · pendiente
```

```python
import interui as ui

class Cliente(ui.Model):
    nombre = ui.Str(max_length=80, unique=True)
    edad = ui.Int(null=True)
    activo = ui.Bool(default=True)
    alta = ui.DateTime(auto_now_add=True)

    class Meta:
        table = "clientes"

Cliente.objects.create(nombre="Ana", edad=34)
mayores = Cliente.objects.filter(edad__gte=18).order_by("-edad")
ana = Cliente.objects.get(nombre="Ana")
ana.edad = 35
ana.save()
```

```json
{
  "databases": {
    "default": { "engine": "sqlite", "name": "data/app.db" },
    "reportes": {
      "engine": "postgres", "host": "localhost", "port": 5432,
      "user": "tienda", "password": "${PG_PASSWORD}", "name": "reportes"
    }
  }
}
```

- **Motores**: `sqlite` y `file` funcionan sin instalar nada; `postgres`, `mysql`
  y `mongo` van con extras (`pip install "interui[postgres]"` y compañía).
- **Secretos fuera del JSON**: `${VARIABLE}` se lee del entorno, como un `.env`.
- **Varias bases** por alias; cada modelo elige la suya con `Meta.database`.
- **Migraciones**: se generan comparando los modelos con el esquema actual y solo
  escriben las diferencias; los cambios que borran datos exigen `--force`.

👉 Guía completa: [`docs/datos.md`](docs/datos.md) — el `interui.json` clave por
clave (también escrito a mano), los modelos campo por campo, el ORM, las
migraciones paso a paso, un CRUD completo dentro de la interfaz y los errores
frecuentes con su solución.

---

## Controles

Todo se importa desde el paquete:

```python
import interui as ui
```

Categorías (referencia completa con firmas en [`docs/controles.md`](docs/controles.md)):

| Categoría | Ejemplos |
|---|---|
| Rejilla y estructura | `Row`, `Col`, `Container`, `Stack`, `Grid`, `Divider`, `Screen` |
| Tipografía | `Heading`, `Text`, `Lead`, `Muted`, `Badge`, `CodeBlock`, `Kbd` |
| Botones | `Button`, `IconButton`, `ButtonGroup`, `CopyButton`, `Fab` |
| Formularios | `Input`, `Textarea`, `Select`, `Combobox`, `Checkbox`, `Switch`, `Slider`, `DateInput`, `Dropzone`, `OtpInput`, `Rating`, `TagInput`, `SegmentedControl`, `Form` |
| Datos | `Table`, `DataTable`, `ListGroup`, `Tree`, `Timeline`, `Stat`, `JsonView`, `LogView`, `EmptyState` |
| Retroalimentación | `Alert`, `Progress`, `ProgressRing`, `Meter`, `Skeleton`, `StatusDot`, `ConfirmDialog` |
| Contenedores | `Card`, `Panel`, `Section`, `Modal`, `Drawer`, `Sheet`, `Collapse`, `Accordion`, `Splitter`, `Dropdown`, `TitleBar`, `StatusBar` |
| Navegación | `Tabs`, `Breadcrumb`, `Pagination`, `Steps`, `Navbar`, `Sidebar`, `CommandPalette` |
| Gráficos | `LineChart`, `AreaChart`, `BarChart`, `PieChart`, `DonutChart`, `Sparkline`, `Gauge` |
| Medios | `Image`, `Avatar`, `AvatarGroup`, `Carousel`, `Gallery`, `Video`, `Audio` |
| Avanzados | `CodeEditor`, `RichTextEditor`, `Markdown`, `Terminal`, `Iframe`, `Canvas`, `Icon` |
| Shell y menús | `AppShell`, `MenuBar`, `MenuButton`, `ContextMenu`, `ContextItem`, `CommandBar`, `NotificationButton`, `IconGrid` |

Ejemplos de uso:

```python
ui.Card(title="Equipo", description="3 personas", icon=ui.icons.users)(
    ui.DataTable(
        columns=[
            {"key": "name", "label": "Nombre", "sortable": True},
            {"key": "role", "label": "Rol", "align": "right"},
        ],
        rows=[{"id": 1, "name": "Ana", "role": "Admin"}],
        searchable=True, selectable=True, total=1, page=1,
        on_sort=lambda e: app.notify(f"ordenar por {e.value}"),
    )
)

ui.Tabs(
    [("resumen", "Resumen", ui.Text("…")), ("detalle", "Detalle", ui.Text("…"))],
    active="resumen",
    on_change=lambda e: app.set_state("tab", e.value),
)

ui.Modal(ui.Text("Contenido"), dialog_id="alta", title="Nueva ficha").trigger("Abrir")
```

Cualquier control acepta `class_` para ajustar Tailwind; `tw()` resuelve los
conflictos (gana la última clase), sin peleas de especificidad:

```python
ui.Button("Guardar", w=ui.width.full, bg=ui.colors.emerald_600, hover_bg=ui.colors.emerald_500)
```

---

## Eventos

Los handlers son funciones Python normales. Pueden recibir un `UIEvent` o nada:

```python
import interui as ui


def guardar() -> None:                       # sin parámetros
    app.notify("guardado")


def on_nombre(evento: ui.UIEvent) -> None:   # con evento
    print(evento.value, evento.name, evento.files, evento.mods)
```

Handlers disponibles: `on_click`, `on_dblclick`, `on_change`, `on_input`,
`on_submit`, `on_keydown`, `on_keyup`, `on_enter`, `on_focus`, `on_blur`,
`on_mouseenter`, `on_mouseleave`, `on_dragstart`, `on_dragover`, `on_drop`,
`on_sort`, `on_page`, `on_search`, `on_remove`, `on_add`, `on_toggle`.

`UIEvent` incluye: `id`, `event`, `value`, `checked`, `key`, `mods`,
`data` (`index`, `name`, valores del formulario), `files` (subidas) y
propiedades cómodas `text`, `as_number`, `index`, `name`.

Archivos: cualquier `FileInput` o `Dropzone` sube el binario al proceso local y
entrega `Attachment` con `read()`, `read_text()` y `path`:

```python
def on_file(evento: ui.UIEvent) -> None:
    for archivo in evento.files:
        print(archivo.name, archivo.size, archivo.read_text()[:120])
```

---

## Estado reactivo

```python
contador = app.state("contador", 0)      # Signal

contador.get()          # leer
contador.set(5)         # escribir  → re-render automático
contador.update(len)    # transformar
contador.toggle()       # bool
contador.push("item")   # listas
```

Cualquier cambio de estado vuelve a renderizar todas las vistas conectadas; el
cliente aplica los cambios de forma incremental.

---

## Diálogos y ventanas modales

Un sistema completo de ventanas modales, sin escribir HTML ni JavaScript:

```python
from interui import dialog, toast

dialog.show("Texto plano")
dialog.info("Guardado", title="Listo")
dialog.success("Todo correcto")
dialog.warning("Quedan 2 días de prueba")
dialog.error("No se pudo conectar")
dialog.critical("Se perdió la conexión")          # fallo grave

dialog.confirm("¿Eliminar el proyecto?", title="Atención", on_accept=borrar)
dialog.input("Nombre", title="Nuevo", on_accept=nombre)      # nombre es una señal
dialog.form([{"name": "correo", "label": "Correo", "type": "email"}],
            title="Alta", on_accept=guardar)

dialog.custom(                                    # 100 % personalizable
    ui.text("Copia completada"),
    ui.progress(100, label="Archivos"),
    title="Resultado",
    buttons=[("Cerrar", None, "outline")],
)
```

| Función | Para qué |
|---|---|
| `dialog.show/info/success/warning/error/critical` | Avisos con su nivel e icono. |
| `dialog.alert(msg, level=…)` | Aviso con nivel explícito. |
| `dialog.confirm(msg, on_accept=…)` | Confirmar una acción. |
| `dialog.input(label, on_accept=…)` | Pedir un dato (llega en `evento.value`). |
| `dialog.form(fields, on_accept=…)` | Varios campos (`evento.data["values"]`). |
| `dialog.custom(*children, buttons=…)` | Ventana a medida con tu propio contenido. |
| `dialog.close()` / `app.close_all_dialogs()` | Cerrar. |

Son HTML + Tailwind dentro de tu ventana (no diálogos del sistema), con
`role="dialog"`, foco, `Escape`, cierre por fondo y animación. No bloquean: la
respuesta llega a tu handler.

👉 Guía completa, opciones y recetas: [`docs/dialogos.md`](docs/dialogos.md).

---

## Armazón de app, menús y barras

Una ventana de escritorio «de verdad» se monta con `AppShell`, que coloca cada
zona en su sitio (barra de título, menús, lateral, contenido con scroll, estado):

```python
import interui as ui

app = ui.App("Mi app", width=1180, height=780)


def nuevo() -> None:
    ui.dialog.input("Nombre", title="Nuevo", on_accept=lambda v: ui.toast(f"Creado {v}"))


@app.page("/")
def index():
    return ui.AppShell(
        ui.Container(pad=ui.pad.py_6)(ui.heading("Panel", level=2)),
        title_bar=ui.TitleBar("Mi app", icon=ui.icons.layers),
        header=ui.MenuBar(
            {
                "Archivo": [
                    ui.ContextItem("Nuevo…", icon=ui.icons.plus, shortcut="Ctrl+N", on_click=nuevo),
                    "-",
                    ui.ContextItem("Salir", icon=ui.icons.power, danger=True, on_click=app.quit),
                ],
                "Ver": [ui.ContextItem("Cambiar tema", icon=ui.icons.moon, on_click=app.toggle_theme)],
            },
            brand="Mi app",
        ),
        sidebar=ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True)),
        status=ui.StatusBar(ui.text("Listo")),
    )


app.run()
```

Los menús funcionan sin escribir JavaScript: clic abre el desplegable, el ratón
cambia de menú cuando hay uno abierto, `Escape` o el clic fuera lo cierran y
`aria-expanded` se mantiene sincronizado.

Menú contextual (botón derecho) sobre cualquier contenido:

```python
CONTEXTO = ui.ContextMenu(
    ui.ContextItem("Abrir", icon=ui.icons.folder, on_click=abrir),
    ui.ContextItem("Renombrar", icon=ui.icons.edit, on_click=renombrar),
    "-",
    ui.ContextItem("Eliminar", icon=ui.icons.trash, danger=True, on_click=eliminar),
)

pagina = CONTEXTO(ui.table(headers=["Nombre"], rows=[["Ana"], ["Luis"]]))
```

Extras listos para usar: `ui.MenuButton(...)` (despliegue suelto),
`ui.CommandBar(...)` (buscador + acciones), `ui.NotificationButton(3, items=[...])`
(campana con contador) y `app.toggle_theme()` desde Python.

### Armarlo por partes

Cuando la ventana crece, en vez de un constructor con diez argumentos puedes
asignar cada zona, y añadir contenido con `add` (llamada, asignación o `+=`):

```python
shell = ui.AppShell()
shell.title_bar = ui.TitleBar("Mi app", icon=ui.icons.layers)
shell.header = ui.MenuBar({"Archivo": [ui.ContextItem("Salir", icon=ui.icons.power)]})
shell.sidebar = ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True))
shell.status = ui.StatusBar(ui.text("Listo"))
shell.add = ui.Container(pad=ui.pad.py_6)(ui.text("Contenido"))
```

Vale para todos los controles: `card.add = ui.text("Hola")`, `card += ui.text("…")`,
`bar["Archivo"] = [ui.ContextItem("Salir", icon=ui.icons.power)]`.

### Ventanas estrechas

El armazón se adapta solo: por debajo de 768 px el sidebar se esconde y aparece
un botón (☰) que lo desliza sobre el contenido, con fondo para cerrarlo al tocar
fuera. Además, el contenido principal nunca desborda en horizontal, las tablas y
el código se desplazan dentro de su caja, los diálogos se limitan a la altura de
la ventana con el cuerpo con scroll y las imágenes se ajustan al ancho. Para
espaciados que cambian con el tamaño, usa los prefijos de punto: `pad=pad.p_4,
md_pad=pad.p_8, lg_pad=pad.p_10`.

### Posición del sidebar

```python
ui.AppShell(..., sidebar=ui.Sidebar(...), sidebar_position=ui.side.right)
```

`side.left` (por defecto), `side.right`, `side.start` y `side.end` (respetan la
dirección de escritura). También acepta `"derecha"` / `"right"`; el borde del
sidebar se cambia de lado solo. Como el árbol se reconstruye en cada render, la
posición puede venir de una preferencia del usuario.

### Niveles de cierre

| Llamada | Qué cierra |
|---|---|
| `app.close()` | **solo** la ventana que ejecuta el handler |
| `app.dispose(ventana)` | cierra y libera esa ventana; la app sigue viva |
| `app.exit()` / `app.quit()` | todas las ventanas y el servidor |

### Multiventana

```python
@app.page("/ajustes")
def ajustes():
    return ui.Text("Ajustes")

def abrir_ajustes() -> None:
    app.open_window("/ajustes", title="Ajustes", width=720, height=520)

ui.Button("Abrir ajustes", icon=ui.icons.settings, on_click=abrir_ajustes)
```

Cada ventana tiene su propio canal WebSocket, su ruta y su ciclo de vida:
`app.windows`, `app.main_window`, `ventana.close()`, `ventana.navigate("/otra")`.
Requiere `window="desktop"` y el extra `interui[desktop]`.

Detalle completo en [menús y armazón](docs/menus.md) y en el ejemplo
[`examples/06_app_moderna.py`](examples/06_app_moderna.py).

---

## Iconos

El framework incluye su propio set de **204 iconos** vectoriales (trazo 24×24),
sin dependencias externas ni acceso a red, así que también funciona dentro del
ejecutable empaquetado:

```python
from interui import icons

icons.car                       # el nombre, para icon=…
ui.Icon(icons.car, size=6)      # el control
icons.car(size=6, stroke=2)     # atajo: el control con opciones
Card(icons.edit, "Editar")      # como hijo se dibuja el icono
icons.chevron_down              # los guiones se escriben con _
icons.close                     # alias cómodos: close→x, delete→trash, exit→power
```

En cualquier control que acepte `icon=`:

```python
Button("Guardar", icon=icons.check)
Input(icon=icons.search, placeholder="Buscar…")
ContextItem("Salir", icon=icons.power, on_click=app.exit)
```

`len(ui.ICON_NAMES)` → 204 iconos, y
`ui.IconGrid(searchable=True)` dibuja la galería completa. La lista está en el
[catálogo de iconos](docs/iconos.md).

---

## Integración con el escritorio

```python
def abrir() -> None:
    resultado = app.native.read_text(file_types=("Texto (*.txt;*.md)",))
    if resultado:
        ruta, contenido = resultado

def guardar() -> None:
    ruta = app.native.save_text("nota.txt", "contenido")
    app.native.notify("Guardado", ruta or "cancelado")

ui.Button("Abrir", on_click=abrir)
ui.Button("Carpeta", on_click=lambda: app.native.pick_folder())
ui.Button("Copiar", on_click=lambda: app.native.clipboard_write("texto"))
ui.Button("Siempre visible", on_click=lambda: app.native.set_always_on_top(True))
ui.Button("Cerrar", on_click=app.native.close)
```

| Método | Descripción |
|---|---|
| `app.native.open_file(...)` | Diálogo de apertura; devuelve metadatos de los archivos. |
| `app.native.read_text(...)` | `(ruta, contenido)` o `None`. |
| `app.native.save_text(name, texto)` | Diálogo de guardado; devuelve la ruta. |
| `app.native.save_bytes(name, datos)` | Guarda binario. |
| `app.native.pick_folder()` | Selector de carpeta. |
| `app.native.notify(title, msg)` | Notificación del sistema. |
| `app.native.clipboard_write/read()` | Portapapeles. |
| `app.native.set_title/minimize/toggle_maximize/toggle_fullscreen/close` | Control de ventana. |
| `app.native.open_external(url)` | Abre el navegador del sistema. |
| `app.native.set_always_on_top(bool)` | Ventana siempre visible. |
| `app.on_close(fn)` / `@app.on_close` | Hook al cerrar la ventana. |

Ventana sin marco con barra propia:

```python
app = App("Mi app", frameless=True)
ui.Screen(
    ui.TitleBar("Mi app", icon=ui.icons.layers),   # botones nativos + zona arrastrable
    ui.Container(...)(...),
    ui.StatusBar(ui.Text("Listo")),
    h=ui.height.screen, class_="flex flex-col",
)
```

Desde JavaScript también existe el puente:

```js
await window.interui.native.openFile()
await window.interui.native.save("datos.csv", texto)
await window.interui.native.notify("Hola", "desde JS")
window.interui.desktop      // true dentro de la ventana nativa
```

👉 Detalles y empaquetado: [`docs/escritorio.md`](docs/escritorio.md).

---

## CLI

`iui` y `interui` son el mismo comando. Todo es de escritorio: no hay servidor
que desplegar.

```bash
iui startproject mi_app         # proyecto completo (sin nombre: asistente)
iui startapp tareas             # una app dentro del proyecto (desde su carpeta)
iui run app.py                  # ventana nativa (por defecto)
iui run app.py --debug          # herramientas de desarrollo en la ventana
iui new mi_app                  # un solo archivo, sin base de datos
iui init mi_app                 # asistente: interui.json + base de datos
iui db makemigrations           # migraciones (también `iui db migrate|status`)
iui doctor                      # comprueba el entorno
iui assets                      # recompila Tailwind (Vite)
iui dev                         # Tailwind en modo watch
iui build app.py --name MiApp
```

Dentro de un proyecto creado con `startproject`, los comandos viven en `iui.py`,
la consola del proyecto:

```bash
python iui.py run
python iui.py startapp tareas   # crea tareas/ y la registra en interui.json
python iui.py makemigrations
python iui.py migrate
python iui.py status
python iui.py shell             # consola con tus modelos cargados
python iui.py check             # revisa interui.json y la base de datos
```

`iui startapp` crea `models.py`, `forms.py`, `views.py`, `urls.py` y
`README.md`, añade la app a `apps` de `interui.json` y su `models.py` a la lista
de migraciones: sus rutas se registran solas, un solo `migrate` pone al día
todas las apps y el formulario de alta ya viene hecho.

`python -m interui ...` funciona igual si no quieres el script en el PATH.

---

## Empaquetado en ejecutable

```bash
pip install pyinstaller
interui build app.py --name MiApp            # carpeta dist/MiApp
interui build app.py --name MiApp --onefile  # un único archivo
```

El comando añade automáticamente `interui/static` (CSS y runtime JS) y los
binarios de `pywebview`, que es lo que suele faltar en los empaquetados caseros.

| Plataforma | Resultado | Notas |
|---|---|---|
| macOS | `dist/MiApp.app` | Firma/notarización para distribuir fuera de tu Mac. |
| Windows | `dist/MiApp/MiApp.exe` | Requiere WebView2 Runtime en el equipo destino. |
| Linux | `dist/MiApp/MiApp` | Enlaza dinámicamente a GTK/WebKitGTK. |

Consejos:

- Usa `--onefile` solo si necesitas un archivo único: arranca más lento.
- `--icon app.icns` (macOS) / `--icon app.ico` (Windows).
- Comprueba con `interui doctor` que `app.css` existe **antes** de empaquetar.
- Empaqueta en el mismo sistema operativo donde vas a distribuir.

---

## Publicar en PyPI

**Estado:** el paquete no está en PyPI todavía (por eso la instalación es desde
GitHub); está preparado para publicarse tal cual (nombre `interui` libre, CSS y
JS incluidos en el wheel de `hatchling`).

```bash
pip install build twine
python -m build                 # dist/interui-<version>-py3-none-any.whl + .tar.gz
python -m twine check dist/*
python -m twine upload --repository testpypi dist/*   # ensayo
python -m twine upload dist/*                          # definitivo
```

La versión vive en un solo sitio: `__version__` en
[`interui/__init__.py`](interui/__init__.py) (la lee `hatchling`).

Publicación automática: [`.github/workflows/publish.yml`](.github/workflows/publish.yml)
usa *Trusted Publishing* (OIDC, sin tokens en el repo) al crear un release.
Solo hay que registrar el proyecto en
[PyPI → Publishing](https://pypi.org/manage/account/publishing/) con
`owner=jurdin32`, `repo=interUI`, `workflow=publish.yml`, `environment=pypi` y
crear la etiqueta:

```bash
git tag -a v0.5.0 -m "interui 0.5.0"
git push origin main
git push origin v0.5.0
```

👉 Paso a paso, errores habituales y checklist de versión:
[`docs/publicar.md`](docs/publicar.md).

---

## Estilos con Tailwind y Vite

El CSS se genera con la configuración oficial de Tailwind v4 sobre Vite
([guía de instalación](https://tailwindcss.com/docs/installation/using-vite)) en
[`frontend/`](frontend):

```
frontend/
├── index.html            # taller visual para ajustar el tema
├── package.json
├── vite.config.js        # compila a interui/static/app.css
└── src/styles.css        # tokens de marca + base + safelist
```

- `src/styles.css` escanea `interui/**/*.py` y el runtime JS (`@source`), así que
  cualquier clase que uses en Python entra en el CSS.
- La **safelist** (`@source inline(...)`) cubre clases construidas dinámicamente
  (`col-span-{1..12}`, `gap-{0..12}`, `h-{2..16}`…).
- Los tokens de marca están en `@theme`: cámbialos y recompila para reestilizar
  todos los controles.

```bash
cd frontend
npm run dev      # taller de estilos con recarga en caliente
npm run build    # genera ../interui/static/app.css
npm run watch    # recompila al guardar
```

---

## Arquitectura

```
interui/
├── app.py         # App: rutas, estado, render, ciclo de vida
├── base.py        # Component: árbol declarativo → HTML
├── grid.py        # rejilla de 12 columnas
├── controls/      # catálogo de controles (11 módulos)
├── style.py       # tw(): resolución de conflictos Tailwind
├── html.py        # escapado y serialización segura
├── events.py      # UIEvent, Attachment, invocación de handlers
├── state.py       # Signal
├── server.py      # HTTP estático + WebSocket RFC 6455 (stdlib)
├── desktop.py     # ventana nativa + puente al sistema operativo
├── log.py         # registro seguro sin consola
├── cli.py         # interui run|new|build|doctor|assets|dev
└── static/        # shell.html, interui.js, app.css, favicon
```

Decisiones de diseño:

- **Cero dependencias en el núcleo**: el WebSocket está implementado en
  `server.py` (handshake + framing), no hace falta `fastapi`/`uvicorn`.
- **Un solo proceso**: el servidor escucha en `127.0.0.1` con puerto efímero y
  muere con la ventana; no expone nada fuera de la máquina.
- **Seguridad por defecto**: todo el texto se escapa (`html.escape`); solo
  `ui.raw()`/`ui.Html()` permiten HTML deliberado.
- **Reconciliación por nodo**: se parchea el DOM existente en vez de reemplazarlo,
  así se conservan foco, selección y scroll.

---

## Pruebas

```bash
./venv/bin/python -m pytest -q
```

Cubren render y escapado, resolución de clases Tailwind, rejilla, eventos,
protocolo WebSocket, servidor HTTP, capa de escritorio, ramas por sistema
operativo, registro sin consola y verificaciones estructurales (clases o métodos
duplicados, catálogo exportado).

```
155 passed
```

---

## Solución de problemas

| Síntoma | Causa y solución |
|---|---|
| La ventana no aparece / no abre | `interui doctor`: falta `pywebview` → `pip install "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"`. Desde 0.5 la app no abre el navegador por su cuenta: si quieres depurar así, `app.run(window="browser")` o `--window browser`. |
| Se ve sin estilos | Falta `interui/static/app.css` → `interui assets`. |
| `ImportError: No module named webview` | Instala el extra `desktop`. |
| Linux: error de GTK/WebKit | Instala `libgtk-3-0` y `libwebkit2gtk-4.1-0`. |
| Windows: ventana en blanco | Instala/actualiza WebView2 Runtime. |
| Un clic no responde | El handler lanzó una excepción: se muestra como *toast*; revisa la consola o `--debug`. |
| El ejecutable no arranca en Windows | Es una app `--windowed` sin `stdout`; los mensajes van a `<data_dir>/interui.log`. |
| Los estilos nuevos no aparecen | Recompila (`interui assets`) y reinicia la app. |
| El editor subraya `window`/`text` en rojo **pero el programa funciona** | Pylance analiza con *otro* intérprete o con caché vieja. Ver [por qué el editor marca errores](#por-qué-el-editor-marca-errores-y-el-programa-funciona). |
| `"window" es un símbolo de importación desconocido` o `state` «no se puede llamar al módulo» | Hay una versión antigua de `interui` instalada en el intérprete que usa tu editor. Comprueba con `python -c "import interui; print(interui.__version__, interui.__file__)"` (debe ser ≥ 0.5.0 y apuntar a tu código) y reinstala: `pip install -U --force-reinstall "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"` o, si trabajas sobre el repo, `pip install -e ".[desktop,dev]"`. |

---

## Por qué el editor marca errores y el programa funciona

Son dos analizadores distintos:

| | Ejecutar (`python app.py`) | Editor (Pylance / mypy) |
|---|---|---|
| Qué usa | el intérprete y `site-packages` reales | el intérprete **seleccionado en el editor** y su propio índice |
| Cuándo se actualiza | al instalar | al recargar la ventana / reiniciar el servidor de lenguaje |
| Qué ve | todo lo que existe en tiempo de ejecución | solo lo que puede resolverse **estáticamente** |

Las tres causas habituales, en orden de frecuencia:

1. **Intérprete distinto.** VS Code usa otro Python (o otro `venv`) que el de tu
   terminal. Comprueba:
   ```bash
   python -c "import interui; print(interui.__version__, interui.__file__)"
   ```
   Elige el mismo en `Ctrl/Cmd + Shift + P` → *Python: Select Interpreter*.

2. **Caché del analizador.** Instalaste la versión nueva, pero Pylance mantiene el
   índice anterior: `Ctrl/Cmd + Shift + P` → *Developer: Reload Window*
   (o *Python: Restart Language Server*).

3. **Símbolos generados en tiempo de ejecución.** Los analizadores no ven nada
   creado con `globals()[...] = ...`. Por eso los alias (`text`, `button`…) se
   declaran **estáticamente** en [`interui/aliases.py`](interui/aliases.py), y una
   prueba ([`tests/test_structure.py`](tests/test_structure.py)) impide volver a
   inyectarlos dinámicamente.

Comprobación rápida de que el paquete se analiza bien: abre un archivo con

```python
from interui import button, state, text, window

count = state(0)
window("App", text("Hola"), button("Pulsar", on_click=count.inc)).run()
```

y pasa el ratón por `button`; debe mostrar `(type) button = Button`. Si aparece
«símbolo desconocido», es el punto 1 o 2, no el código.

---

## Documentación adicional

El mapa completo está en **[docs/indice.md](docs/indice.md)**.

**Primeros pasos**

- [Tutorial paso a paso](docs/guia.md) — de la ventana vacía a la app completa, en 12 pasos.
- [Anatomía de un proyecto](docs/proyecto.md) — qué es `main.py`, qué es `iui.py`,
  dónde van los modelos y cómo encajan las apps.
- [Configuración](docs/configuracion.md) — cada clave de `interui.json`.

**Temas**

- [Escritorio](docs/escritorio.md) — ciclo de vida, multiventana, diálogos del
  sistema, datos persistentes y empaquetado.
- [Menús y barras](docs/menus.md) — `AppShell`, barra de menús, menú contextual,
  barra de comandos y notificaciones.
- [Diálogos](docs/dialogos.md) — avisos, confirmaciones, formularios y ventanas propias.
- [Rejilla de 12 columnas](docs/rejilla.md) — columnas, breakpoints y patrones.
- [Estilos](docs/estilos.md) — tokens, variantes, hex y degradados.
- [Formularios](docs/formularios.md) — `forms.py` en la app, `ui.ModelForm`,
  validación y `ui.state()` en las vistas.
- [Datos](docs/datos.md) — modelos, ORM, migraciones, motores y recetas.
- [Iconos](docs/iconos.md) — los 204 iconos incluidos.

**Referencia**

- [Comandos](docs/comandos.md) — `iui`, `interui`, `iui.py` y `python -m interui`.
- [Controles](docs/controles.md) — firma y ejemplo ejecutable de cada componente.

**Cómo se hace**

- [Actualizar interUI](docs/actualizar.md) — versión, comandos y aviso en la app.
- [Empaquetar y publicar](docs/publicar.md) — wheel, TestPyPI, PyPI y ejecutables.
- [Guía de escritorio](docs/escritorio.md) — ventana nativa, puente y empaquetado.
- [Instalación y publicación](docs/publicar.md) — instalar desde GitHub y publicar en PyPI.
- [Historial de cambios](CHANGELOG.md) — qué trae cada versión (actual: 0.5.0).

---

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
