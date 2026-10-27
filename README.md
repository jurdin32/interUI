# interUI

**Framework para crear aplicaciones de escritorio en Python con HTML, Tailwind CSS y JavaScript.**

No es un framework web: cada app se abre en una **ventana nativa** del sistema
operativo (WebKit en macOS, WebView2 en Windows, WebKitGTK en Linux) sin barra de
direcciones, sin navegador y sin conexión a internet. El HTML se genera en Python,
Tailwind lo compila Vite, y JavaScript solo transporta eventos.

```python
from interui import App, Button, Card, Container, Heading, Screen

app = App("Mi primera app")


@app.page("/")
def index():
    clicks = app.state("clicks", 0)
    return Screen(
        Container(size="prose", class_="py-16")(
            Heading("Hola, escritorio", level=1),
            Card(class_="mt-6")(
                Button(
                    f"Pulsaciones: {clicks.get()}",
                    icon="plus",
                    on_click=lambda: clicks.set(clicks.get() + 1),
                )
            ),
        )
    )


if __name__ == "__main__":
    app.run()          # ← abre una ventana nativa
```

---

## Índice

- [Estado del proyecto](#estado-del-proyecto)
- [Multiplataforma](#multiplataforma)
- [Instalación](#instalación)
- [Guía paso a paso](#guía-paso-a-paso)
- [Inicio rápido](#inicio-rápido)
- [Cómo funciona una app](#cómo-funciona-una-app)
- [Rejilla de 12 columnas](#rejilla-de-12-columnas)
- [Controles](#controles)
- [Eventos](#eventos)
- [Estado reactivo](#estado-reactivo)
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
| Catálogo de controles | ✅ ~230 exportaciones (`docs/controles.md`) |
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
| Instalación de la ventana | `pip install "interui[desktop]"` | igual | igual |
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

### Instalar como paquete

```bash
pip install "interui[desktop]"      # desde PyPI (incluye ventana nativa)
```

El wheel ya trae el CSS de Tailwind compilado y el runtime JS: **no necesitas
Node.js ni internet** para usar el framework.

Otras formas de instalación:

```bash
pip install interui                              # solo el núcleo, sin ventana nativa
pipx install "interui[desktop]"                  # solo el comando `interui`, aislado
uv add "interui[desktop]"                        # o: poetry add "interui[desktop]"
pip install "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"
```

### Instalar para desarrollar el framework

```bash
git clone https://github.com/jurdin32/interUI.git
cd interUI
python -m venv venv
./venv/bin/pip install -e ".[desktop,dev]"

# Estilos: solo al cambiar la paleta o añadir clases nuevas
cd frontend && npm install && npm run build
```

Comprobación del entorno:

```bash
interui doctor
```

👉 Guía completa de instalación y **publicación en PyPI**:
[`docs/publicar.md`](docs/publicar.md).

---

## Guía paso a paso

El recorrido completo, desde una ventana vacía hasta una app con formularios,
tabla, búsqueda, validación, persistencia y diálogos nativos está en
**[docs/guia.md](docs/guia.md)**:

| Paso | Qué aprendes |
|---|---|
| 1–2 | Instalar y abrir la ventana más pequeña posible |
| 3–4 | Jerarquía de componentes y rejilla de 12 columnas |
| 5–6 | Botones, eventos y estado reactivo |
| 7 | Formularios con validación hecha en Python |
| 8 | Tablas, búsqueda, filtrado y estados vacíos |
| 9 | Varias vistas y navegación |
| 10 | Diálogos nativos, notificaciones, portapapeles y archivos |
| 11–12 | Tema claro/oscuro y persistencia en `app.data_dir` |
| 13–15 | Estructura de proyecto, empaquetado y errores frecuentes |

Cada bloque de código de la guía se compila y se ejecuta en las pruebas
([`tests/test_guide.py`](tests/test_guide.py)), así que no puede quedarse
obsoleto.

---

## Inicio rápido

```bash
interui new mi_app          # crea mi_app/app.py + README + .gitignore
cd mi_app
python app.py               # abre la ventana nativa
```

Contenido de `app.py`:

```python
from interui import App, Button, Card, Container, Heading, Screen

app = App("mi_app")


@app.page("/")
def index():
    return Screen(Container(size="prose", class_="py-10")(Heading("mi_app", level=1)))


if __name__ == "__main__":
    app.run()
```

Ejemplos completos en [`examples/`](examples):

| Archivo | Qué muestra |
|---|---|
| [`01_hello.py`](examples/01_hello.py) | Contador con estado reactivo. |
| [`02_grid.py`](examples/02_grid.py) | Rejilla de 12 columnas y breakpoints. |
| [`03_catalog.py`](examples/03_catalog.py) | Catálogo visual de todos los controles. |
| [`04_desktop.py`](examples/04_desktop.py) | Integración nativa: diálogos, notificaciones, barra de título. |
| [`05_crud.py`](examples/05_crud.py) | **App completa**: alta/edición, búsqueda, validación, persistencia y exportación. |

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

Ejemplos de uso:

```python
ui.Card(title="Equipo", description="3 personas", icon="users")(
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
ui.Button("Guardar", class_="w-full bg-emerald-600 hover:bg-emerald-500")
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
    ui.TitleBar("Mi app", icon="layers"),   # botones nativos + zona arrastrable
    ui.Container(...)(...),
    ui.StatusBar(ui.Text("Listo")),
    class_="flex flex-col h-screen",
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

```bash
interui run app.py              # ventana nativa (por defecto)
interui run app.py --window browser  # navegador (depuración)
interui run app.py --debug      # herramientas de desarrollo en la ventana
interui new mi_app              # proyecto nuevo
interui doctor                  # comprueba el entorno
interui assets                  # recompila Tailwind (Vite)
interui dev                     # Tailwind en modo watch
interui build app.py --name MiApp
```

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

El paquete está preparado para publicarse tal cual (nombre `interui` libre,
`twine check` correcto, CSS incluido en el wheel):

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
`owner=jurdin32`, `repo=interUI`, `workflow=publish.yml`, `environment=pypi`.

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
| La ventana no aparece / no abre | `interui doctor`: falta `pywebview` → `pip install "interui[desktop]"`. |
| Se ve sin estilos | Falta `interui/static/app.css` → `interui assets`. |
| `ImportError: No module named webview` | Instala el extra `desktop`. |
| Linux: error de GTK/WebKit | Instala `libgtk-3-0` y `libwebkit2gtk-4.1-0`. |
| Windows: ventana en blanco | Instala/actualiza WebView2 Runtime. |
| Un clic no responde | El handler lanzó una excepción: se muestra como *toast*; revisa la consola o `--debug`. |
| El ejecutable no arranca en Windows | Es una app `--windowed` sin `stdout`; los mensajes van a `<data_dir>/interui.log`. |
| Los estilos nuevos no aparecen | Recompila (`interui assets`) y reinicia la app. |

---

## Documentación adicional

- [Guía paso a paso](docs/guia.md) — de la ventana vacía a la app completa.
- [Referencia de controles](docs/controles.md) — un ejemplo ejecutable y la firma de cada control.
- [Guía de la rejilla](docs/rejilla.md) — patrones responsive.
- [Guía de escritorio](docs/escritorio.md) — ventana nativa, puente y empaquetado.
- [Instalación y publicación en PyPI](docs/publicar.md) — cómo instalarlo y cómo publicarlo.

---

## Licencia

MIT. Ver [`LICENSE`](LICENSE).
