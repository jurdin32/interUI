# Menús, barras y armazón de aplicación (shell)

Todo lo necesario para que una ventana se vea como una app de escritorio de
verdad: barra de menús, desplegables, menú contextual, barra de comandos, barra
de estado, campana de notificaciones, galería de iconos y el armazón que lo
coloca todo en su sitio.

```python
import interui as ui
```

---

## 1. `AppShell`: el esqueleto de la ventana

`AppShell` reparte las zonas típicas y deja el scroll **solo** en el contenido:

```text
┌──────────────────────────────────────────────┐
│ title_bar      (arrastrable en ventana nativa)│
├──────────────────────────────────────────────┤
│ header         (barra de menús / comandos)    │
├────────────┬─────────────────────────────────┤
│ sidebar    │ main  (aquí va el scroll)        │
├────────────┴─────────────────────────────────┤
│ footer (opcional)                             │
│ status                                        │
└──────────────────────────────────────────────┘
```

```python
@app.page("/")
def index():
    return ui.AppShell(
        ui.Container(pad=ui.pad.py_6)(ui.text("Contenido")),
        title_bar=ui.TitleBar("Mi app", icon=ui.icons.layers),
        header=ui.MenuBar({"Archivo": [ui.ContextItem("Salir", icon=ui.icons.power)]}, brand="Mi app"),
        sidebar=ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True)),
        footer=None,
        status=ui.StatusBar(ui.text("Listo")),
    )
```

| Parámetro | Para qué |
|---|---|
| `*content` | Contenido principal (va dentro de `<main>` con scroll). |
| `title_bar` | `ui.TitleBar(...)`; en ventana nativa permite arrastrar y cerrar. |
| `header` | `ui.MenuBar(...)`, `ui.CommandBar(...)` o cualquier componente. |
| `sidebar` | `ui.Sidebar(...)`; si se omite, el contenido ocupa todo el ancho. |
| `footer` | Franja opcional sobre la barra de estado. |
| `status` | `ui.StatusBar(...)` fija al pie. |
| `sidebar_position` | `ui.side.left` (por defecto) o `ui.side.right`; también `start`/`end`. |
| `sidebar_width` | Clase de ancho del hueco cuando `sidebar` no es un `ui.Sidebar`. |
| `menu_label` | Texto que acompaña al botón del menú en ventanas estrechas. |
| `collapsible` | `True` (por defecto): en ventanas estrechas el sidebar pasa a panel deslizante. `False`: el menú **siempre** queda a la vista, aunque la ventana se encoja. |

En una app de escritorio, lo normal es que la navegación no desaparezca: si
quieres el menú siempre visible, `collapsible=False`.

```python
ui.AppShell(
    ui.Container(pad=ui.pad.py_6)(ui.text("Contenido")),
    sidebar=ui.Sidebar(ui.SidebarItem("Inicio", icon=ui.icons.home, active=True)),
    collapsible=False,          # nunca se esconde tras el botón ☰
)
```

### Los desplegables siempre quedan encima

Los paneles de `MenuBar`, `MenuButton` y `ContextMenu` se dibujan en `position:
fixed` con `z-index` alto y el runtime los coloca bajo su disparador. Así no los
recorta ningún contenedor con `overflow` (la barra de menús con scroll
horizontal, una tarjeta, el propio `<main>`), y se abren hacia arriba si no caben
abajo.

### Armarlo por partes

El constructor con todas las zonas está bien para ejemplos, pero cuando la app
crece se lee mejor ir asignando cada parte. Todas las zonas son atributos, y el
contenido se añade con `add`:

```python
shell = ui.AppShell()
shell.title_bar = ui.TitleBar("Mi app", icon=ui.icons.layers)
shell.header = ui.MenuBar({"Archivo": [ui.ContextItem("Salir", icon=ui.icons.power)]})
shell.sidebar = ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True))
shell.status = ui.StatusBar(ui.text("Listo"))
shell.add = ui.Container(pad=ui.pad.py_6)(ui.text("Contenido"))
```

| Forma | Ejemplo |
|---|---|
| llamada | `shell.add(ui.text("Contenido"))` |
| asignación | `shell.add = ui.text("Contenido")` |
| suma | `shell += ui.text("Contenido")` |
| lista | `shell.add = [ui.text("Uno"), ui.text("Dos")]` |

Lo mismo sirve para cualquier control (`card.add = …`, `form.add = …`) y para
los menús: `bar["Archivo"] = [ui.ContextItem("Salir", icon=ui.icons.power)]`.

### Ventanas estrechas

En menos de 768 px el sidebar deja de ocupar sitio: se esconde y aparece un
botón (☰) en una barra superior que lo desliza sobre el contenido, con fondo
oscuro para cerrarlo al tocar fuera. Al elegir un elemento del menú lateral se
cierra solo. No hay nada que configurar y el contenido nunca queda aplastado.

### Posición de la barra lateral

```python
ui.AppShell(
    ui.Container(pad=ui.pad.py_6)(ui.text("Contenido")),
    sidebar=ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid)),
    sidebar_position=ui.side.right,
)
```

El borde del sidebar se mueve solo al lado correcto. `side.start` y `side.end`
respetan la dirección de escritura (`dir="rtl"`). Se aceptan también `"right"`,
`"derecha"`, `"end"` y `"r"`, así que la preferencia puede venir de un ajuste
guardado y cambiar entre renders:

```python
preferencia = ui.state("izquierda")

ui.AppShell(..., sidebar_position=preferencia)
ui.Button("Cambiar lado", on_click=lambda: preferencia.set(...))
```

---

## 2. `MenuBar`: menús arriba de la ventana

```python
ui.MenuBar(
    {
        "Archivo": [
            ui.ContextItem("Nuevo proyecto…", icon=ui.icons.plus, shortcut="Ctrl+N", on_click=nuevo),
            ui.ContextItem("Abrir carpeta…", icon=ui.icons.folder, shortcut="Ctrl+O"),
            "-",                                      # separador
            ui.ContextItem("Salir", icon=ui.icons.power, danger=True, on_click=app.quit),
        ],
        "Ver": [ui.ContextItem("Cambiar tema", icon=ui.icons.moon, on_click=alternar_tema)],
        "Ayuda": [ui.ContextItem("Acerca de", icon=ui.icons.info, on_click=acerca_de)],
    },
    brand="Mi app",              # nombre + logo a la izquierda
    icons={"Archivo": ui.icons.folder},  # icono en el título del menú
    actions=ui.NotificationButton(3),   # zona derecha opcional
)
```

### Icono en el título de un menú

Hay dos formas, y las dos se pueden combinar:

```python
# 1. Un mapa título → icono (lo más corto si hay varios menús)
ui.MenuBar(
    {"Registros": [ui.ContextItem("Personas", icon=ui.icons.user)]},
    icons={"Registros": ui.icons.users},
)

# 2. Como tercer elemento de la entrada de la lista
ui.MenuBar([
    ("Registros", [ui.ContextItem("Personas", icon=ui.icons.user)], ui.icons.users),
])
```

Para el **nombre de la aplicación** a la izquierda de la barra hay dos
parámetros propios: `brand="Registros"` y `logo=ui.icons.users` (el logo va
dentro de un cuadro índigo). Con `brand=None` esa zona no se dibuja.

Qué hace el cliente por ti (sin escribir JavaScript):

- abrir/cerrar el desplegable al hacer clic en el título,
- cambiar de menú al pasar el ratón cuando ya hay uno abierto,
- cerrar con `Escape`, con clic fuera o al elegir una opción,
- `aria-expanded` sincronizado para accesibilidad.

| Parámetro | Para qué |
|---|---|
| `menus` | dict `{título: [ítems]}` o lista de tuplas `(título, ítems[, icono])`. |
| `brand` | nombre de la app a la izquierda. |
| `logo` | icono del cuadro que acompaña al `brand` (`"layers"` por defecto). |
| `icons` | icono de cada pestaña: `{"Registros": ui.icons.users}`. |
| `actions` | componente a la derecha (notificaciones, avatar…). |
| `sticky` | la barra se queda arriba al hacer scroll (`True` por defecto). |

Los ítems pueden escribirse de tres formas equivalentes:

```python
ui.ContextItem("Abrir", icon=ui.icons.folder, on_click=abrir)      # componente
("Abrir", "folder", abrir, "Ctrl+O", False)                 # tupla: label, icono, handler, atajo, peligro
{"label": "Abrir", "icon": "folder", "on_click": abrir}     # dict
"-"                                                          # separador
```

`on_click` se ejecuta **en Python**; el manejador no recibe argumentos salvo que
los declare.

---

## 3. `MenuButton`: desplegable en cualquier sitio

```python
ui.MenuButton(
    "Acciones",
    icon=ui.icons.settings,
    items=[
        ui.ContextItem("Editar", icon=ui.icons.edit, on_click=editar),
        ui.ContextItem("Eliminar", icon=ui.icons.trash, danger=True, on_click=borrar),
    ],
    align="right",      # el panel se abre alineado a la derecha
)
```

---

## 4. `ContextMenu`: botón derecho

Envuelve el contenido sobre el que se quiere actuar:

```python
CONTEXTO = ui.ContextMenu(
    ui.ContextItem("Abrir", icon=ui.icons.folder, on_click=abrir),
    ui.ContextItem("Renombrar", icon=ui.icons.edit, on_click=renombrar),
    "-",
    ui.ContextItem("Eliminar", icon=ui.icons.trash, danger=True, on_click=eliminar),
    hint="Clic derecho para más opciones",   # ayuda bajo el contenido (opcional)
)

pagina = CONTEXTO(ui.Table(headers=["Nombre"], rows=[["Ana"], ["Luis"]]))
```

El menú se posiciona con las coordenadas del puntero, se mantiene dentro de la
ventana y se cierra al hacer clic fuera, con `Escape` o al elegir una acción.

---

## 5. `MenuItem` y `ContextItem`

Son el mismo tipo de entrada; `ContextItem` es un alias semántico de
`MenuItem`, y ambos se pueden usar en cualquier menú.

| Parámetro | Efecto |
|---|---|
| `label` | Texto visible. |
| `icon` | Nombre de icono del set incluido. |
| `shortcut` | Atajo que se muestra a la derecha (informativo). |
| `danger` | Estilo destructivo (rojo). |
| `disabled` | Deshabilitado (no ejecuta el handler). |
| `href` | Convierte la entrada en enlace. |
| `on_click` | Handler de Python. |

---

## 6. `CommandBar`: buscador + acciones

```python
ui.CommandBar(
    ui.Button("Nuevo", icon=ui.icons.plus, variant=ui.variant.primary, on_click=nuevo),
    search=filtro.get(),
    search_placeholder="Buscar…",
    on_search=lambda: None,       # se llama al escribir (evento input)
)
```

---

## 7. `NotificationButton`: campana con contador

```python
ui.NotificationButton(
    notificaciones.get(),
    items=[
        ui.ListItem("Nueva tarea asignada", icon=ui.icons.check),
        ui.ListItem("Comentario en tu informe", icon=ui.icons.mail),
    ],
)
```

Al pulsarla se abre/cierra el panel (comportamiento incluido en el cliente).

---

## 8. Iconos

El paquete trae **202 iconos** propios (trazo 24×24), sin dependencias ni red:

```python
ui.Icon(ui.icons.check, size=6, color=ui.colors.emerald_600)
len(ui.ICON_NAMES)                      # 202
ui.IconGrid(columns=10, searchable=True, on_pick=lambda nombre: toast(nombre))
```

`IconGrid` es una galería buscable: al escribir filtra por nombre y, si pasas
`on_pick`, el nombre elegido llega a Python.

La lista completa está en [el catálogo de iconos](iconos.md).

---

## 9. Tema y cierre desde Python

```python
app.toggle_theme()      # devuelve el tema activo ("light"/"dark")
app.set_theme("dark")   # también acepta "oscuro"/"claro"
app.close()             # cierra SOLO la ventana que ejecuta la acción
app.dispose(ventana)    # cierra y libera esa ventana; la app sigue viva
app.exit()              # todas las ventanas y el servidor
```

Perfecto para las entradas `Ver → Cambiar tema` y `Archivo → Salir` del menú
(`on_click=app.exit`, sin paréntesis).

---

## 10. Ejemplo completo

[`examples/06_app_moderna.py`](../examples/06_app_moderna.py) reúne armazón,
barra de menús con atajos, menú contextual, búsqueda en vivo, campana de
notificaciones, galería de iconos, cambio de tema y cierre:

```bash
python examples/06_app_moderna.py
```
