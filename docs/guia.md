# Tutorial: paso a paso, de la ventana vacía a la aplicación

Este es el recorrido completo, en orden. Cada paso es **un archivo que puedes
ejecutar tal cual** y que añade una sola cosa al anterior. Si haces los pasos en
orden, al final tienes una aplicación de escritorio con menús, formularios,
tabla y base de datos.

> **Cómo leerlo.** No hace falta saber HTML, CSS ni JavaScript: todo se escribe
> en Python. Copia el bloque en un archivo `mi_app.py`, ejecútalo con
> `python mi_app.py` y mira la ventana. Cuando entiendas el paso, pasa al
> siguiente.

> **Antes de empezar.** Instala interUI y comprueba el entorno:
>
> ```bash
> pip install "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"
> iui doctor
> ```
>
> Si `doctor` dice que falta `pywebview`, la ventana no se puede abrir:
> `pip install "interui[desktop]"` lo resuelve.
>
> **Si trabajas sobre el código del framework**, instálalo en modo enlace
> (`pip install -e .` dentro del repositorio). Con una copia normal, tus cambios
> no se ven y el síntoma es desconcertante: los archivos están bien pero la app
> se comporta como antes. Compruébalo siempre con
> `python -c "import interui; print(interui.__file__)"`: la ruta debe ser la de
> tu repositorio, no la de `site-packages`.

---

## Los 12 pasos

| Paso | Qué consigues |
|---|---|
| [1](#paso-1-la-ventana-más-pequeña-posible) | Una ventana vacía |
| [2](#paso-2-añadir-contenido-y-jerarquía) | Texto y tarjetas dentro |
| [3](#paso-3-poner-un-menú) | Un menú de verdad, con Archivo y Ayuda |
| [4](#paso-4-botones-y-eventos) | Que un botón ejecute tu código |
| [5](#paso-5-estado-reactivo) | Que la ventana se actualice sola |
| [6](#paso-6-la-rejilla-de-12-columnas) | Ordenar todo en columnas |
| [7](#paso-7-varias-vistas-y-navegación) | Varias páginas en la misma ventana |
| [8](#paso-8-formularios-con-validación) | Un formulario que valida |
| [9](#paso-9-mostrar-datos-tabla-y-búsqueda) | Una tabla con búsqueda |
| [10](#paso-10-persistencia-de-datos) | Guardar entre sesiones |
| [11](#paso-11-formulario-desde-un-modelo) | El formulario, hecho solo desde el modelo |
| [12](#paso-12-de-archivo-suelto-a-proyecto) | El proyecto completo, con apps |

Al final: [tema claro y oscuro](#extras-tema-claro-y-oscuro),
[diálogos y avisos](#extras-diálogos-y-avisos),
[empaquetar](#extras-empaquetar-y-distribuir) y
[errores frecuentes](#errores-frecuentes).

---

## Paso 1 · La ventana más pequeña posible

**Objetivo:** abrir una ventana nativa, vacía.

Archivo `mi_app.py`:

```python
from interui import window

window("Mi primera ventana").run()
```

Ejecuta:

```bash
python mi_app.py
```

**Ves:** una ventana del sistema operativo, de 960×680, con el título
«Mi primera ventana» y nada dentro. Al cerrarla, el programa termina.

**Qué acaba de pasar.** `window(...)` hace tres cosas a la vez:

1. crea la aplicación (`App`),
2. registra una página en la ruta `/`,
3. envuelve lo que le pases en un contenedor centrado.

`.run()` abre la ventana. El contenido que le pases después del título son los
hijos de esa página, así que el paso 2 es tan simple como añadirlos.

<details>
<summary>La misma ventana con la API larga (cuando la app crece)</summary>

```python
from interui import App

app = App("Mi primera ventana")


@app.page("/")
def index():
    return None          # ← una vista sin contenido


app.run()
```

`App` es la ventana y `@app.page("/")` dice qué función pinta la página `/`.
Es lo que usarás a partir del paso 7; `window(...)` es un atajo de esto.

</details>

---

## Paso 2 · Añadir contenido y jerarquía

**Objetivo:** poner cosas dentro de la ventana.

```python
from interui import window, title, text, card

window(
    "Mi app",
    title("Hola, escritorio"),
    text("Todo esto es Python: no hay HTML ni JavaScript."),
    card(
        text("Nombre: Ana"),
        text("Ciudad: Madrid"),
        title="Ficha",
    ),
).run()
```

**Ves:** un título grande, un párrafo y una tarjeta con dos líneas.

**Tres ideas que sirven para todo el resto del tutorial:**

| Idea | Ejemplo |
|---|---|
| Cada control es una función | `text("...")`, `card(...)`, `button("...")` |
| Los hijos se pasan dentro | `window("título", hijo1, hijo2)` |
| Los nombres en minúscula son atajos | `text` es `Text`, `card` es `Card` |

> Los controles se apilan en vertical y se separan solos. No hay que colocar
> nada a mano: si quieres columnas, está el paso 6.

👉 Todos los controles, con un ejemplo de cada uno: [controles.md](controles.md).

---

## Paso 3 · Poner un menú

**Objetivo:** una ventana principal **vacía**, con la barra de menús arriba
(Archivo, Ayuda…) y los botones de la ventana.

Un menú no es un control suelto: vive en el **armazón** de la aplicación
(`AppShell`), que es el que reparte la ventana en zonas.

```python
from interui import (
    App, AppShell, ContextItem, MenuBar, TitleBar, dialog, icons,
)

app = App("registro")


@app.page("/")
def inicio():
    shell = AppShell(
        title_bar=TitleBar("registro", icon=icons.layers),   # barra de arriba
        header=MenuBar(                                      # el menú
            {
                "Archivo": [
                    ContextItem("Salir", icon=icons.power, on_click=salir),
                ],
                "Ayuda": [
                    ContextItem("Acerca de", icon=icons.info, on_click=acerca),
                ],
            }
        ),
    )
    return shell


def salir() -> None:
    app.quit()


def acerca() -> None:
    dialog.info("registro 0.1.0", title="Acerca de")


app.run()
```

**Ves:** la ventana con su barra de título, la fila **Archivo · Ayuda** y el
resto vacío. Al abrir **Archivo → Salir** se cierra; **Ayuda → Acerca de** abre
un aviso encima.

**Cómo se lee:**

| Pieza | Qué es |
|---|---|
| `AppShell(...)` | el esqueleto: barra de título, menú, contenido, barra de estado |
| `TitleBar("registro")` | la barra de arriba con el nombre y minimizar/maximizar/cerrar |
| `MenuBar({...})` | las pestañas del menú; cada clave es un título |
| `ContextItem("Salir", on_click=salir)` | una entrada del menú que llama a tu función |

No hay contenido porque no le pasaste ningún hijo a `AppShell`: por eso la
ventana está vacía. Cuando quieras llenarla, se la pasas igual que a
`window(...)`:

```python
AppShell(
    text("Aquí va el contenido"),          # ← esto llena la zona central
    title_bar=TitleBar("registro"),
    header=MenuBar({"Archivo": [ContextItem("Salir", on_click=salir)]}),
)
```

> **Cada cosa en su zona.** Lo que se pasa *dentro* de `AppShell` es el contenido
> central; `title_bar`, `header`, `sidebar` y `status` son zonas fijas alrededor.
> Con `AppShell(collapsible=False)` la barra lateral queda siempre visible.

👉 Menús contextuales, barra de comandos y notificaciones: [menus.md](menus.md).

---

## Paso 4 · Botones y eventos

**Objetivo:** que al pulsar un botón pase algo.

```python
from interui import window, button, text, toast, title

window(
    "Botones",
    title("Pulsa el botón"),
    text("El mensaje aparece abajo, en la ventana."),
    button("Saludar", icon="hand", on_click=lambda: toast("¡Hola!", "success")),
).run()
```

**Ves:** un botón; al pulsarlo sale un aviso pequeño abajo.

**Qué es un handler.** `on_click=` recibe una función de Python. Puede ser una
función con nombre (más cómoda de leer y de probar):

```python
def saludar() -> None:
    toast("¡Hola!", "success")


button("Saludar", on_click=saludar)
```

| Nombre | Cuándo se ejecuta |
|---|---|
| `on_click` | al pulsar |
| `on_input` | al escribir en un campo |
| `on_change` | al cambiar un valor (interruptor, desplegable) |
| `on_submit` | al enviar un formulario |

---

## Paso 5 · Estado reactivo

**Objetivo:** que la ventana se actualice sola cuando cambia un dato.

```python
from interui import window, button, state, text, title

contador = state(0)          # una señal: 0 al empezar

window(
    "Contador",
    title("Contador"),
    text("Pulsaciones: ", contador),           # se repinta solo
    button("Sumar una", on_click=contador.inc),
    button("Reiniciar", variant="secondary", on_click=lambda: contador.set(0)),
).run()
```

**Ves:** un número que sube al pulsar y vuelve a cero con **Reiniciar**.

**Las señales** (`state`) son la memoria de la ventana. Tres formas de usarlas:

| Quiero… | Escribo |
|---|---|
| leer el valor | `contador.get()` |
| cambiarlo | `contador.set(5)` o `contador.inc()` |
| que se actualice el texto | pasar la señal como hijo: `text("Pulsaciones: ", contador)` |

También se pueden conectar a un campo de texto: escribir guarda el valor.

```python
from interui import window, input, state, text

nombre = state("")

window(
    "Saludo",
    input(value=nombre, label="Tu nombre", on_input=nombre),
    text("Hola, ", nombre),
).run()
```

---

## Paso 6 · La rejilla de 12 columnas

**Objetivo:** poner cosas una al lado de otra.

```python
from interui import window, card, col, row, text, title

window(
    "Rejilla",
    title("Tres tarjetas"),
    row(
        card(text("1.240 €"), title="Ventas"),
        card(text("38"), title="Clientes"),
        card(text("5"), title="Pendientes"),
    ),
).run()
```

**Ves:** tres tarjetas iguales, una al lado de otra.

| Pieza | Para qué |
|---|---|
| `row(...)` | reparte lo que le pases en columnas iguales |
| `col(..., span=6)` | ocupa la mitad del ancho (6 de 12) |
| `stack(...)` | apila en vertical con separación |

```python
row(
    col(text("Ancho completo"), span=12),
    col(text("Mitad"), span=6),
    col(text("Mitad"), span=6),
)
```

En ventanas estrechas, la rejilla pasa a una sola columna sin que hagas nada.

👉 Columnas por tamaño de ventana y patrones: [rejilla.md](rejilla.md).

---

## Paso 7 · Varias vistas y navegación

**Objetivo:** dos páginas en la misma ventana.

```python
from interui import App, Button, Container, Heading, Screen, Text, pad

app = App("Varias vistas")


@app.page("/", title="Inicio")
def inicio():
    return Screen(
        Container(pad=pad.py_10)(
            Heading("Inicio", level=1),
            Text("Esta es la primera página."),
            Button("Ir a ajustes", on_click=lambda: app.navigate("/ajustes")),
        )
    )


@app.page("/ajustes", title="Ajustes")
def ajustes():
    return Screen(
        Container(pad=pad.py_10)(
            Heading("Ajustes", level=1),
            Text("Y esta es la segunda."),
            Button("Volver", variant="secondary", on_click=lambda: app.navigate("/")),
        )
    )


app.run()
```

**Ves:** cambia el contenido de la ventana al pulsar los botones, sin abrir otra
ventana. El título de la ventana también cambia.

| Pieza | Qué hace |
|---|---|
| `@app.page("/ruta")` | registra la función que pinta esa página |
| `title="..."` | el título de la ventana en esa página |
| `app.navigate("/ruta")` | salta a otra página (desde tu código Python) |

> Las rutas pueden llevar datos: `@app.page("/cliente/<int:id>")` y entonces tu
> función recibe `id` como parámetro.

---

## Paso 8 · Formularios con validación

**Objetivo:** recoger datos, comprobarlos en Python y avisar de los errores.

```python
from interui import (
    App, Button, Card, Container, Input, Screen, Stack, ValidationSummary,
    pad, state, toast,
)

app = App("Formulario")
nombre = app.state("nombre", "")
correo = app.state("correo", "")
errores = app.state("errores", [])


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
            toast("Guardado", "success")

    return Screen(
        Container(pad=pad.py_10)(
            Card(title="Datos de contacto")(
                ValidationSummary(errores.get()),
                Stack(gap=4)(
                    Input(nombre.get(), label="Nombre", required=True, on_input=nombre),
                    Input(correo.get(), label="Correo", required=True, on_input=correo),
                ),
                Button("Guardar", icon="check", on_click=guardar),
            ),
        )
    )


app.run()
```

**Ves:** dos campos y un botón. Si dejas el nombre vacío y pulsas **Guardar**,
aparece un recuadro rojo con la lista de problemas; si todo está bien, sale el
aviso «Guardado».

**El patrón se repite siempre:**

1. una señal por campo (`state`),
2. el campo la escribe con `on_input=`,
3. al guardar, se validan los valores en Python,
4. los errores van a otra señal que se pinta con `ValidationSummary`.

> Esto es un formulario **escrito a mano**. Cuando los datos ya son un modelo de
> la base de datos, no hace falta: el paso 11 lo genera solo.

---

## Paso 9 · Mostrar datos: tabla y búsqueda

**Objetivo:** una lista y un filtro que la reduce mientras escribes.

```python
from interui import (
    App, Card, Container, Input, Screen, Table, Text, pad, state,
)

app = App("Tabla")
filtro = state("")

CLIENTES = [
    ["Ana", "Madrid", "ana@correo.com"],
    ["Luis", "Sevilla", "luis@correo.com"],
    ["Marta", "Madrid", "marta@correo.com"],
]


@app.page("/")
def index():
    texto = filtro.get().strip().lower()
    filas = [
        fila for fila in CLIENTES
        if not texto or texto in " ".join(fila).lower()
    ]
    return Screen(
        Container(pad=pad.py_10)(
            Input(filtro.get(), label="Buscar", icon="search", on_input=filtro),
            Text(f"{len(filas)} de {len(CLIENTES)}"),
            Card(pad=pad.all_2)(
                Table(
                    headers=["Nombre", "Ciudad", "Correo"],
                    rows=filas,
                    empty="Nada coincide con la búsqueda",
                )
            ),
        )
    )


app.run()
```

**Ves:** escribes en **Buscar** y la tabla se reduce al momento.

---

## Paso 10 · Persistencia de datos

**Objetivo:** que lo guardado siga ahí al cerrar y abrir la app.

`app.data_dir` es la carpeta de datos de tu aplicación en cada sistema (macOS,
Windows y Linux). Guarda ahí tus archivos:

```python
import json
from pathlib import Path

from interui import App, Button, Container, Screen, Text, pad

app = App("Persistencia")
AJUSTES = Path(app.data_dir) / "ajustes.json"


def cargar() -> dict:
    try:
        return json.loads(AJUSTES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"visitas": 0}


datos = app.state("datos", cargar())


@app.page("/")
def index():
    def sumar() -> None:
        nuevos = {"visitas": datos.get()["visitas"] + 1}
        datos.set(nuevos)
        AJUSTES.write_text(json.dumps(nuevos), encoding="utf-8")

    return Screen(
        Container(pad=pad.py_10)(
            Text(f"Veces guardado: {datos.get()['visitas']}"),
            Button("Guardar una visita", icon="check", on_click=sumar),
        )
    )


app.run()
```

**Ves:** el número sigue donde lo dejaste al cerrar y volver a abrir.

| Sistema | Dónde queda |
|---|---|
| macOS | `~/Library/Application Support/<app>` |
| Windows | `%APPDATA%\<app>` |
| Linux | `~/.local/share/<app>` |

> Para tablas de verdad (varias filas, consultas, migraciones) no uses JSON: el
> paso 11 conecta la app a SQLite con modelos.

---

## Paso 11 · Formulario desde un modelo

**Objetivo:** que el formulario, la validación y el guardado salgan del modelo.

Este paso ya es un **proyecto** (la base de datos y las migraciones necesitan
carpeta propia). Créalo con el comando:

```bash
iui startproject agenda --no-input
cd agenda
python iui.py startapp contactos
python iui.py makemigrations
python iui.py migrate
python main.py
```

**Lo que ya tienes, sin escribir nada:** la página `/contactos` con un formulario
de alta, su validación y una tabla con lo guardado.

Ahora mira los dos archivos que lo hacen posible:

`contactos/models.py` — los campos:

```python
class Contacto(ui.Model):
    nombre = ui.Str(max_length=120)
    email = ui.Email(max_length=120, unique=True)
    pais = ui.Choice(choices=["es", "mx"], default="es")
    activo = ui.Bool(default=True)

    class Meta:
        table = "contactos_contacto"
```

`contactos/forms.py` — el formulario, en su propio archivo:

```python
class ContactoForm(ui.ModelForm):
    model = Contacto
    title = "Nuevo contacto"
```

`contactos/views.py` — la vista solo lo coloca:

```python
def inicio() -> ui.Component:
    return ui.Screen(ui.Container(pad=ui.pad.py_10)(
        ui.Heading("Contactos", level=1),
        ContactoForm(margin=ui.margin.t_6),
    ))
```

**Cada tipo de campo elige su control solo:** `Str` → texto, `Email` → correo,
`Choice` → desplegable, `Bool` → interruptor, `Date` → fecha, `LongText` → área
de texto. Cambia el modelo, vuelve a migrar y el formulario se adapta.

👉 Todo sobre formularios: [formularios.md](formularios.md).

---

## Paso 12 · De archivo suelto a proyecto

**Objetivo:** entender qué hay dentro de la carpeta que crea `startproject`.

```bash
iui startproject mi_app      # sin nombre: pregunta base de datos, tema, etc.
```

| Archivo | Para qué |
|---|---|
| `main.py` | el punto de entrada: migra lo pendiente y abre la ventana |
| `iui.py` | los comandos del proyecto (`startapp`, `makemigrations`, `migrate`…) |
| `interui.json` | la configuración: nombre, ventana, base de datos, apps |
| `mi_app/app.py` | configuración: crea la `App` y el armazón de la ventana |
| `<app>/` | apps del proyecto: modelos, formularios, páginas y rutas |
| `migrations/` | el historial de la base de datos (se versiona en git) |
| `data/` | la base de datos y los archivos (no se versiona) |

El paquete del proyecto **solo tiene configuración**: no hay `models.py` ni
`views.py` en `mi_app/`. Mientras no exista ninguna app, la ventana muestra
«Hola mundo»; la primera app que registre una página la sustituye.

El ciclo de trabajo, siempre el mismo:

```bash
python iui.py startapp ventas     # añadir una app
python iui.py makemigrations      # detectar cambios en los modelos
python iui.py migrate             # aplicarlos a la base de datos
python main.py                    # abrir la ventana
```

👉 Archivo por archivo: [proyecto.md](proyecto.md). Todos los comandos:
[comandos.md](comandos.md).

---

## Extras: tema claro y oscuro

```python
from interui import App, Button, Container, Screen, Text, pad

app = App("Tema")


@app.page("/")
def index():
    return Screen(
        Container(pad=pad.py_10)(
            Text("Pulsa para cambiar de tema"),
            Button("Modo oscuro", on_click=lambda: app.set_theme("dark")),
            Button("Modo claro", variant="secondary", on_click=lambda: app.set_theme("light")),
        )
    )


app.run()
```

También puedes arrancar ya en oscuro: `App("Tema", theme="dark")`, o dejarlo
fijo en `interui.json` (`"theme": "dark"`).

---

## Extras: diálogos y avisos

```python
from interui import App, Button, Container, Screen, Text, dialog, pad, toast

app = App("Diálogos")


@app.page("/")
def index():
    def preguntar() -> None:
        dialog.confirm(
            "¿Seguro que quieres continuar?",
            on_accept=lambda: toast("Confirmado", "success"),
        )

    return Screen(
        Container(pad=pad.py_10)(
            Text("Tres formas de avisar:"),
            Button("Aviso", on_click=lambda: toast("Listo", "info")),
            Button("Info", variant="secondary", on_click=lambda: dialog.info("Todo correcto")),
            Button("Preguntar", variant="secondary", on_click=preguntar),
        )
    )


app.run()
```

| Quiero… | Uso |
|---|---|
| un aviso que se va solo | `toast("Guardado", "success")` |
| un cartel con **Aceptar** | `dialog.info("…")` |
| preguntar sí/no | `dialog.confirm("…", on_accept=…)` |
| pedir un dato | `dialog.input("Nombre")` |

👉 Diálogos con formulario y varios niveles: [dialogos.md](dialogos.md).

---

## Extras: empaquetar y distribuir

```bash
pip install pyinstaller
iui build                    # dentro del proyecto
```

Queda un `.app` en macOS, un `.exe` en Windows y un binario en Linux, con la
ventana nativa y sin necesidad de Python instalado.

👉 Detalles y firma de código: [escritorio.md](escritorio.md#6-empaquetado).

---

## Errores frecuentes

| Síntoma | Causa y solución |
|---|---|
| `DesktopError: falta pywebview` | `pip install "interui[desktop]"`. Sin él no hay ventana nativa |
| La ventana se abre en blanco | la vista devolvió `None`; devuelve un control (aunque sea `Text("")`) |
| `LookupError: Ruta no registrada` | falta `@app.page("/")` o la ruta no coincide |
| `AttributeError: module 'interui' has no attribute 'Xxx'` | ese control no existe con ese nombre: busca en [controles.md](controles.md) |
| El texto no se actualiza | pasaste `contador.get()` en vez de `contador` como hijo |
| `TypeError: state() takes ...` | la firma es `state(valor, name="clave")`, no `state("clave", valor)` |
| La tabla dice «Todavía no hay registros» | falta `python iui.py migrate` |
| Un formulario no guarda y no dice nada | míralo en la consola: los errores de tus handlers salen ahí |

Si algo se queda colgado, ejecuta con más información:

```bash
python mi_app.py --debug      # o: iui run mi_app.py --debug
```

---

## Dónde seguir

| Quiero… | Documento |
|---|---|
| ver todos los controles | [controles.md](controles.md) |
| formularios y modelos | [formularios.md](formularios.md) |
| base de datos y consultas | [datos.md](datos.md) |
| menús, barras y armazón | [menus.md](menus.md) |
| la ventana, multiventana y empaquetado | [escritorio.md](escritorio.md) |
| todos los comandos | [comandos.md](comandos.md) |
| el índice completo | [indice.md](indice.md) |
