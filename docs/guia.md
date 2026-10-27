# Guía: de una ventana vacía a una aplicación completa

Tutorial progresivo. Cada paso es un archivo que puedes ejecutar tal cual; al
final tendrás una app real (agenda de contactos) con formularios, tabla,
búsqueda, validación, persistencia y diálogos nativos.

La versión terminada está en
[`examples/05_crud.py`](../examples/05_crud.py) y las pruebas la ejecutan en cada
commit.

---

## Índice

1. [Requisitos](#1-requisitos)
2. [La ventana más pequeña posible](#2-la-ventana-más-pequeña-posible)
3. [Añadir contenido y jerarquía](#3-añadir-contenido-y-jerarquía)
4. [La rejilla de 12 columnas](#4-la-rejilla-de-12-columnas)
5. [Botones y eventos](#5-botones-y-eventos)
6. [Estado reactivo](#6-estado-reactivo)
7. [Formularios con validación en Python](#7-formularios-con-validación-en-python)
8. [Mostrar datos: tabla y búsqueda](#8-mostrar-datos-tabla-y-búsqueda)
9. [Varias vistas y navegación](#9-varias-vistas-y-navegación)
10. [Diálogos, notificaciones y archivos](#10-diálogos-notificaciones-y-archivos)
11. [Tema claro y oscuro](#11-tema-claro-y-oscuro)
12. [Barra de menús y menú contextual](#12-barra-de-menús-y-menú-contextual)
13. [Iconos](#13-iconos)
14. [Persistencia de datos](#14-persistencia-de-datos)
15. [Estructura recomendada del proyecto](#15-estructura-recomendada-del-proyecto)
16. [Empaquetar y distribuir](#16-empaquetar-y-distribuir)
17. [Errores frecuentes](#17-errores-frecuentes)

---

## 1. Requisitos

```bash
pip install "interui[desktop]"
python -c "import interui; print(interui.__version__)"
```

Comprueba el entorno:

```bash
interui doctor
python -c "import interui; print(interui.__version__, interui.__file__)"
```

Debe decir que `pywebview` está instalado, que el CSS existe y que la versión es
**≥ 0.2.0**. Si `import interui` te da una versión antigua (o `window` «es un
símbolo de importación desconocido»), tienes otra copia instalada en el
intérprete que usa tu editor:

```bash
# trabajando sobre el repositorio
pip install -e ".[desktop,dev]"

# desde GitHub, versión concreta
pip install -U --force-reinstall "interui[desktop] @ git+https://github.com/jurdin32/interUI.git@v0.2.0"
```

En VS Code, selecciona el mismo intérprete con `Ctrl/Cmd + Shift + P` →
*Python: Select Interpreter*, y si acabas de instalar, recarga la ventana
(*Developer: Reload Window*): Pylance indexa cada intérprete por separado y
seguiría marcando `window` en rojo con el índice antiguo.

> Si el editor subraya `text`/`button` pero `python app.py` funciona, el problema
> es del analizador (intérprete o caché), no del código. Los alias del framework
> están declarados de forma estática en `interui/aliases.py` precisamente para
> que el editor los vea.

---

## 2. La ventana más pequeña posible

La forma más corta es `window(...)`, que crea la app, registra la página `/` y
envuelve el contenido en un contenedor:

```python
from interui import window

window("Mi primera ventana").run()
```

Y con un texto y un botón, que es lo que casi siempre necesitas:

```python
from interui import window, text, button

window(
    "Mi ventana",
    text("Hola mundo"),
    button("Pulsar", on_click=lambda: print("clic")),
).run()
```

Si prefieres el control explícito (útil cuando una ventana tiene varias vistas o
una estructura propia), la API larga es esta:

```python
from interui import App

app = App("Mi primera ventana")


@app.page("/")
def index():
    return None          # ← una vista vacía


app.run()
```

Ejecuta con `python archivo.py`. Se abre una ventana nativa vacía con el título
«Mi primera ventana». El servidor interno escucha solo en `127.0.0.1` y muere al
cerrar la ventana.

> `window(...)` devuelve la `App`, así que `.run()` se puede encadenar. Si el
> archivo puede importarse desde otro sitio (por ejemplo, en pruebas), deja
> `.run()` dentro de `if __name__ == "__main__":` para que importar no abra la
> ventana.

Sobre `App`:

```python
app = App(
    "Mi aplicación",
    width=1100, height=720,     # tamaño inicial
    theme="light",              # o "dark"
    frameless=False,            # True → sin marco del sistema
)
```

También puedes arrancar desde la CLI: `interui run archivo.py`.

---

## 3. Añadir contenido y jerarquía

En la API compacta los controles se llaman en minúsculas y se apilan solos:

```python
from interui import window, title, text, subtitle, card, row, button

window(
    "Mi app",
    title("Hola, escritorio", subtitle="Una ventana nativa"),
    text("Todo lo que ves son controles de interUI."),
    row(
        card(title="Uno")(text("Contenido")),
        card(title="Dos")(text("Contenido")),
    ),
).run()
```

Con la API larga, todo es un componente que se anida pasando hijos:

```python
from interui import App, Card, Container, Heading, Muted, Screen, Text

app = App("Mi primera ventana")


@app.page("/")
def index():
    return Screen(
        Container(size="prose", class_="py-10")(
            Heading("Hola, escritorio", level=1),
            Muted("Esto no es un navegador: es una ventana nativa."),
            Card(title="Primera tarjeta", description="Con cuerpo")(
                Text("El contenido vive dentro de la tarjeta."),
            ),
        )
    )


app.run()
```

Piezas básicas:

| Componente | Para qué |
|---|---|
| `Screen` | raíz de la ventana (alto completo, fondo del tema) |
| `Container` | centra y limita el ancho (`sm`, `md`, `lg`, `xl`, `full`, `prose`) |
| `Stack` | apila en vertical/horizontal con `gap` |
| `Card` | agrupa contenido con cabecera y pie |
| `Heading`, `Text`, `Muted`, `Paragraph` | texto |

Los hijos también se pueden añadir después: `card(ui.Text("más"))`.

---

## 4. La rejilla de 12 columnas

`Row` es una rejilla de 12; `Col` dice cuántas ocupa en cada breakpoint.

```python
from interui import App, Card, Col, Container, Row, Screen, Text

app = App("Rejilla")


@app.page("/")
def index():
    def tarjeta(titulo):
        return Card(title=titulo, class_="h-full")(Text("Contenido de ejemplo"))

    return Screen(
        Container(class_="py-8")(
            Row(
                Col(span=12, md=6, lg=4)(tarjeta("Uno")),
                Col(span=12, md=6, lg=4)(tarjeta("Dos")),
                Col(span=12, md=12, lg=4)(tarjeta("Tres")),
                gap=4,
            )
        )
    )


app.run()
```

- Móvil/ventana estrecha: `span=12` (100 %).
- Desde 768 px (`md`): 6 columnas (50 %).
- Desde 1024 px (`lg`): 4 columnas (33 %).

Más patrones en [la guía de la rejilla](rejilla.md).

---

## 5. Botones y eventos

Los handlers son funciones Python. El cliente solo envía el evento; la lógica se
ejecuta en tu proceso.

```python
from interui import App, Button, Container, Screen, Stack

app = App("Eventos")


@app.page("/")
def index():
    def saludar() -> None:
        app.notify("¡Hola desde Python!")

    def despedir(evento: object) -> None:
        print("evento recibido:", evento)

    return Screen(
        Container(class_="py-8")(
            Stack(
                Button("Saludar", icon="send", on_click=saludar),
                Button("Despedir", variant="outline", on_click=despedir),
                Button("Abrir documentación", variant="link",
                       on_click=lambda: app.native.open_external("https://tailwindcss.com")),
            )
        )
    )


app.run()
```

`app.notify(...)` muestra un *toast* en la ventana. Los handlers pueden recibir
`ui.UIEvent` (`value`, `checked`, `files`, `key`, `index`…) o no recibir nada.

Eventos disponibles en cualquier control: `on_click`, `on_dblclick`,
`on_change`, `on_input`, `on_submit`, `on_keydown`, `on_keyup`, `on_enter`,
`on_focus`, `on_blur`, `on_mouseenter`, `on_mouseleave`, `on_scroll`,
`on_sort`, `on_page`, `on_remove`, `on_add`, `on_toggle`.

---

## 6. Estado reactivo

Una señal es un valor que, al cambiar, repinta la ventana. Con la API compacta,
un contador completo son ocho líneas:

```python
from interui import window, text, button, state

count = state(0)

window(
    "Contador",
    text("Pulsaciones: ", count),          # el texto depende de la señal
    button("Pulsar", on_click=count.inc),  # el botón la incrementa
).run()
```

También puedes pasar una función para calcular el texto:

```python
window("Contador", text(lambda: f"doble = {count.get() * 2}"))
```

La API larga, con `app.state()` y handlers propios:

```python
from interui import App, Button, Card, Container, Screen, Text, Stack

app = App("Contador")


@app.page("/")
def index():
    contador = app.state("contador", 0)

    return Screen(
        Container(size="prose", class_="py-10")(
            Card(title="Contador")(
                Text(f"Valor actual: {contador.get()}", size="lg", weight="semibold"),
                Stack(
                    Button("−", variant="outline", on_click=lambda: contador.set(contador.get() - 1)),
                    Button("+", icon="plus", on_click=lambda: contador.update(lambda n: n + 1)),
                    Button("Reiniciar", variant="ghost", on_click=lambda: contador.set(0)),
                    direction="row",
                    gap=2,
                ),
            )
        )
    )


app.run()
```

Métodos de una señal: `get()`, `set(valor)`, `update(fn)`, `toggle()`,
`push(item)`, `clear()`.

> El cliente conserva el foco y el texto que estás escribiendo: el re-render no
> pisa los campos activos.

---

## 7. Formularios con validación en Python

La forma corta: pasa la señal como handler y el control guarda el valor.

```python
from interui import window, text, input, switch, button, state, toast

nombre = state("")
correo = state("")
activo = state(True)


def guardar() -> None:
    if "@" not in correo.get():
        toast("El correo no parece válido", "error")
        return
    toast(f"Guardado: {nombre.get()}", "success")


window(
    "Formulario",
    input(value=nombre, label="Nombre", on_input=nombre),
    input(value=correo, label="Correo", on_input=correo),
    switch("Activo", checked=activo, on_change=activo),
    text("Estado: ", lambda: "activo" if activo.get() else "inactivo"),
    button("Guardar", on_click=guardar),
).run()
```

La versión completa, con resumen de errores y validación por campo:

```python
from interui import (
    App, Button, Card, Container, Input, Screen, Stack, Switch, Text, ValidationSummary,
)

app = App("Formulario")
nombre = app.state("nombre", "")
correo = app.state("correo", "")
activo = app.state("activo", True)
errores = app.state("errores", [])
guardado = app.state("guardado", None)


@app.page("/")
def index():
    def guardar() -> None:
        problemas = []
        if len(nombre.get().strip()) < 2:
            problemas.append("El nombre debe tener al menos 2 caracteres.")
        if "@" not in correo.get():
            problemas.append("El correo no parece válido.")
        errores.set(problemas)
        if not problemas:
            guardado.set(f"{nombre.get()} <{correo.get()}>")
            app.notify("Guardado", "success")

    return Screen(
        Container(size="prose", class_="py-10")(
            Card(title="Datos de contacto")(
                ValidationSummary(errores.get()) if errores.get() else None,
                Input(nombre.get(), label="Nombre", required=True, icon="user",
                      on_input=lambda e: nombre.set(e.text)),
                Input(correo.get(), label="Correo", required=True, icon="mail",
                      error=errores.get()[1] if len(errores.get()) > 1 else None,
                      on_input=lambda e: correo.set(e.text)),
                Switch("Activo", checked=activo.get(),
                       on_change=lambda e: activo.set(bool(e.checked))),
                Button("Guardar", icon="check", on_click=guardar),
                Text(f"Guardado: {guardado.get()}" if guardado.get() else "", size="sm", tone="muted"),
            )
        )
    )


app.run()
```

Controles de entrada más usados: «`Input`», «`Textarea`», «`Select`»,
«`Checkbox`», «`Switch`», «`Slider`», «`DateInput`», «`FileInput`»…

Para formularios grandes existe `Form(..., on_submit=...)`: recibe el evento con
todos los campos en `evento.data["form"]`.

---

## 8. Mostrar datos: tabla y búsqueda

```python
from interui import App, Badge, Container, DataTable, Input, Screen, Stack, Text

app = App("Tabla")
filtro = app.state("filtro", "")

DATOS = [
    {"id": 1, "nombre": "Ana Ruiz", "correo": "ana@ejemplo.com", "activo": True},
    {"id": 2, "nombre": "Luis Paz", "correo": "luis@ejemplo.com", "activo": False},
]


@app.page("/")
def index():
    termino = filtro.get().lower()
    filas = [d for d in DATOS if termino in d["nombre"].lower() or termino in d["correo"].lower()]

    return Screen(
        Container(class_="py-8")(
            Stack(
                Input(filtro.get(), placeholder="Buscar…", icon="search", live=True,
                      on_input=lambda e: filtro.set(e.text)),
                DataTable(
                    columns=[
                        {"key": "nombre", "label": "Nombre", "sortable": True},
                        {"key": "correo", "label": "Correo"},
                        {
                            "key": "activo",
                            "label": "Estado",
                            "render": lambda fila: Badge(
                                "activo" if fila["activo"] else "inactivo",
                                variant="success" if fila["activo"] else "neutral",
                                size="sm",
                            ),
                        },
                    ],
                    rows=filas,
                    total=len(filas),
                    page=1,
                    page_size=max(1, len(filas)),
                ),
                Text(f"{len(filas)} resultados", size="sm", tone="muted"),
                gap=3,
            )
        )
    )


app.run()
```

- `render=` en una columna permite devolver un componente (badges, botones…).
- `searchable=True` añade búsqueda propia a la tabla; `sortable` en la columna.
- Para paginación real, usa `total`, `page` y `on_page`.
- Si la lista está vacía, muestra un `EmptyState`.

---

## 9. Varias vistas y navegación

```python
from interui import App, Button, Container, Heading, NavLink, Navbar, Screen, Text

app = App("Navegación")


@app.page("/")
def inicio():
    return Screen(
        Navbar(NavLink("Inicio", href="/", active=True), NavLink("Ajustes", href="/ajustes"),
               brand="Mi app"),
        Container(class_="py-8")(Heading("Inicio", level=1)),
    )


@app.page("/ajustes")
def ajustes():
    return Screen(
        Navbar(NavLink("Inicio", href="/"), NavLink("Ajustes", href="/ajustes", active=True),
               brand="Mi app"),
        Container(class_="py-8")(
            Heading("Ajustes", level=1),
            Button("Volver", variant="outline", on_click=lambda: app.navigate("/")),
        ),
    )


@app.page("/cliente/<int:cliente_id>")
def cliente(cliente_id: int):
    return Screen(Container(class_="py-8")(Heading(f"Cliente #{cliente_id}", level=1)))


app.run()
```

- Los enlaces internos (`href="/..."`) se interceptan: no recargan la ventana.
- `app.navigate("/ruta")` cambia de vista desde Python.
- Rutas con `<int:nombre>`, `<float:...>`, `<str:...>`, `<path:...>`.
- Para un panel lateral permanente, usa `Sidebar` + `NavLink`.

---

## 10. Diálogos, notificaciones y archivos

### Diálogos dentro de la app

```python
from interui import dialog, window, text, button, state, toast

nombre = state("")


def pedir_nombre() -> None:
    dialog.input(
        "Nombre del proyecto",
        title="Nuevo proyecto",
        placeholder="Mi proyecto",
        on_accept=lambda evento: toast(f"Creado: {evento.value}", "success"),
    )


def borrar() -> None:
    dialog.confirm(
        "Esta acción no se puede deshacer.",
        title="¿Eliminar el proyecto?",
        accept_label="Eliminar",
        on_accept=lambda: dialog.success("Proyecto eliminado"),
    )


window(
    "Diálogos",
    text("Panel"),
    button("Nuevo", icon="plus", on_click=pedir_nombre),
    button("Eliminar", variant="danger", on_click=borrar),
).run()
```

Tipos: `show`, `info`, `success`, `warning`, `error`, `critical`, `confirm`,
`input`, `form` y `custom`. Detalles en [la guía de diálogos](dialogos.md).

### Diálogos del sistema operativo

```python
from interui import App, Button, Card, Container, Modal, Screen, Stack, Text

app = App("Nativo")


@app.page("/")
def index():
    def abrir_archivo() -> None:
        resultado = app.native.read_text(file_types=("Texto (*.txt;*.md)",))
        if resultado:
            ruta, contenido = resultado
            app.notify("Abierto", f"{ruta} ({len(contenido)} caracteres)")

    def guardar_archivo() -> None:
        ruta = app.native.save_text("nota.txt", "Hola desde interUI")
        if ruta:
            app.native.notify("Guardado", ruta)

    def confirmar() -> None:
        app.eval_js("interui.openDialog('borrar')")

    return Screen(
        Container(class_="py-8")(
            Card(title="Sistema")(
                Stack(
                    Button("Abrir archivo…", icon="folder", on_click=abrir_archivo),
                    Button("Guardar como…", icon="download", variant="outline",
                           on_click=guardar_archivo),
                    Button("Copiar al portapapeles", variant="soft",
                           on_click=lambda: app.native.clipboard_write("texto")),
                    Button("Eliminar…", variant="danger", on_click=confirmar),
                    direction="row", wrap=True, gap=2,
                )
            )
        ),
        Modal(
            Stack(
                Text("Esta acción no se puede deshacer."),
                Stack(
                    Button("Cancelar", variant="outline",
                           on_click=lambda: app.eval_js("interui.closeDialog('borrar')")),
                    Button("Eliminar", variant="danger",
                           on_click=lambda: app.notify("Eliminado", "warning")),
                    direction="row", gap=2, justify="end",
                ),
                gap=4,
            ),
            dialog_id="borrar",
            title="¿Eliminar elemento?",
            size="sm",
        ),
    )


app.run()
```

Métodos nativos: `open_file`, `read_text`, `save_text`, `save_bytes`,
`pick_folder`, `notify`, `clipboard_write/read`, `set_title`, `minimize`,
`toggle_maximize`, `toggle_fullscreen`, `set_always_on_top`, `close`,
`open_external`.

`app.eval_js("...")` ejecuta JavaScript en la ventana si necesitas algo muy
puntual (`interui.toast("hola")`, `interui.openDialog("id")`).

---

## 11. Tema claro y oscuro

El tema es una propiedad de la app: cámbiala y todo se re-renderiza con las
variantes `dark:`.

```python
from interui import App, Button, Container, Screen, Text

app = App("Tema")


@app.page("/")
def index():
    return Screen(
        Container(class_="py-8")(
            Text(f"Tema actual: {app.theme}"),
            Button("Cambiar tema", icon="moon", on_click=app.toggle_theme),
        )
    )


app.run()
```

`app.set_theme("dark")` hace lo mismo desde cualquier handler y `app.quit()`
cierra la ventana (o detiene el servidor en modo navegador).

Desde el cliente también puedes alternar con `data={"iui-theme": "dark"}` en
cualquier elemento. El tema inicial se define en `App(theme="dark")`.

---

## 12. Barra de menús y menú contextual

Una app de escritorio se reconoce por sus menús. `AppShell` coloca el armazón y
`MenuBar` dibuja los menús de arriba:

```python
from interui import (
    App, AppShell, Container, ContextItem, ContextMenu, Heading, MenuBar, Sidebar,
    SidebarItem, StatusBar, Text, TitleBar, toast,
)

app = App("Mi app")


def nuevo() -> None:
    toast("Nuevo proyecto", level="success")


@app.page("/")
def index():
    contexto = ContextMenu(
        ContextItem("Abrir", icon="folder", on_click=lambda: toast("Abrir")),
        ContextItem("Eliminar", icon="trash", danger=True, on_click=lambda: toast("Eliminar", level="warning")),
    )
    return AppShell(
        Container(class_="py-6")(contexto(Heading("Panel", level=2))),
        title_bar=TitleBar("Mi app", icon="layers"),
        header=MenuBar(
            {
                "Archivo": [
                    ContextItem("Nuevo", icon="plus", shortcut="Ctrl+N", on_click=nuevo),
                    "-",
                    ContextItem("Salir", icon="power", danger=True, on_click=app.quit),
                ],
                "Ver": [ContextItem("Cambiar tema", icon="moon", on_click=app.toggle_theme)],
            },
            brand="Mi app",
        ),
        sidebar=Sidebar(SidebarItem("Panel", icon="grid", active=True)),
        status=StatusBar(Text("Listo")),
    )


app.run()
```

Sin escribir JavaScript ya funciona: abrir/cerrar el menú con clic, cambiar de
menú al pasar el ratón, cerrar con `Escape` o clic fuera, y el menú contextual
con el botón derecho (se coloca en el puntero y no se sale de la ventana).

También hay `MenuButton(...)` para un desplegable suelto, `CommandBar(...)` para
un buscador con acciones y `NotificationButton(3, items=[...])` para la campana
con contador. Todo el detalle está en [menús y armazón](menus.md).

---

## 13. Iconos

El set propio trae 202 iconos; no hace falta instalar nada ni tener conexión:

```python
from interui import ICON_NAMES, Icon, IconGrid

Icon("check", size=6, class_="text-emerald-600")
len(ICON_NAMES)                                   # 202
IconGrid(columns=10, searchable=True, on_pick=lambda nombre: print(nombre))
```

`IconGrid` es una galería buscable; con `on_pick` el nombre elegido llega a
Python. La lista completa está en el [catálogo de iconos](iconos.md).

---

## 14. Persistencia de datos

`app.data_dir` apunta a la carpeta de datos de la aplicación en cada sistema.
Guarda ahí tus archivos (JSON, SQLite, ajustes):

```python
import json
from pathlib import Path

from interui import App, Button, Container, Screen, Text

app = App("Persistencia")
STORE = Path(app.data_dir) / "ajustes.json"


def cargar() -> dict:
    try:
        return json.loads(STORE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"visitas": 0}


ajustes = app.state("ajustes", cargar())


@app.page("/")
def index():
    def guardar() -> None:
        datos = {"visitas": ajustes.get()["visitas"] + 1}
        ajustes.set(datos)
        STORE.write_text(json.dumps(datos), encoding="utf-8")

    return Screen(
        Container(class_="py-8")(
            Text(f"Veces abierto: {ajustes.get()['visitas']}"),
            Button("Guardar visita", icon="check", on_click=guardar),
        )
    )


@app.on_close
def _al_cerrar() -> None:
    STORE.write_text(json.dumps(ajustes.get()), encoding="utf-8")


app.run()
```

| Sistema | Carpeta |
|---|---|
| macOS | `~/Library/Application Support/<app>` |
| Windows | `%APPDATA%\<app>` |
| Linux | `~/.local/share/<app>` |

Puedes sobreescribirla con `App(data_dir=...)` o `INTERUI_DATA_DIR`.

---

## 15. Estructura recomendada del proyecto

```
mi_app/
├── app.py              # arranque: crea App, registra páginas, app.run()
├── ui/
│   ├── __init__.py
│   ├── components.py   # controles reutilizables propios
│   └── pages.py        # una función por vista
├── models.py           # datos y persistencia (sin dependencias de interui)
├── assets/             # iconos, imágenes, datos iniciales
└── README.md
```

Reglas prácticas:

- Las **vistas** solo describen la interfaz; la lógica va en funciones normales.
- Los **handlers** deben ser rápidos: para trabajo largo, lanza un hilo y
  actualiza el estado al terminar (`app.set_state`), lo que refresca la vista.
- Un archivo `models.py` sin importar `interui` se puede probar con pytest sin
  abrir ventanas.

---

## 16. Empaquetar y distribuir

```bash
pip install pyinstaller
interui build app.py --name MiApp          # macOS: dist/MiApp.app
interui build app.py --name MiApp --onefile
```

El comando incluye automáticamente los recursos de interUI (CSS, JS, shell) y los
binarios de `pywebview`. Antes de empaquetar:

```bash
interui doctor
```

Requisitos por plataforma en [la guía de escritorio](escritorio.md).

---

## 17. Errores frecuentes

| Síntoma | Causa | Solución |
|---|---|---|
| `RuntimeError: Registra al menos una página` | No has puesto `@app.page("/")` | Añade una vista. |
| La ventana abre sin estilos | Falta `interui/static/app.css` | `interui assets` (requiere Node). |
| `AttributeError: 'NoneType' has no attribute...` | Un handler devolvió `None` donde se esperaba algo, o usaste `e` sin parámetro | Revisa la firma: `def f()` o `def f(evento)`. |
| El texto no se actualiza al escribir | Usaste `value=` fijo sin `on_input` | Añade `on_input=lambda e: estado.set(e.text)`. |
| Un `Col` no responde a `md` | `Col` fuera de `Row` | Envuelve en `Row`. |
| `app.native` lanza `DesktopError` | La app corre en modo navegador | Abre con `app.run()` (ventana) o instala `interui[desktop]`. |
| La ventana no abre en Linux | Faltan GTK/WebKitGTK | `sudo apt install libgtk-3-0 libwebkit2gtk-4.1-0`. |
| Cambié estilos y no se ven | CSS sin recompilar | `interui assets` y reinicia. |

---

## Siguiente paso

- [Referencia de controles](controles.md) — firma y ejemplo de cada control.
- [Menús, barras y armazón](menus.md) — `AppShell`, barra de menús y menú contextual.
- [Catálogo de iconos](iconos.md) — los 202 iconos incluidos.
- [Guía de la rejilla](rejilla.md) — patrones responsive.
- [Guía de escritorio](escritorio.md) — ventana, puente nativo y empaquetado.
- [Instalación y publicación](publicar.md) — PyPI.
- [`examples/05_crud.py`](../examples/05_crud.py) — app completa de referencia.
- [`examples/06_app_moderna.py`](../examples/06_app_moderna.py) — armazón, menús, iconos y tema.
