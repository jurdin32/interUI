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
        ui.Container(class_="py-6")(ui.text("Contenido")),
        title_bar=ui.TitleBar("Mi app", icon="layers"),
        header=ui.MenuBar({"Archivo": [ui.ContextItem("Salir", icon="power")]}, brand="Mi app"),
        sidebar=ui.Sidebar(ui.SidebarItem("Panel", icon="grid", active=True)),
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
| `sidebar_width` | Clase de ancho de la barra lateral (`"w-64"` por defecto). |

---

## 2. `MenuBar`: menús arriba de la ventana

```python
ui.MenuBar(
    {
        "Archivo": [
            ui.ContextItem("Nuevo proyecto…", icon="plus", shortcut="Ctrl+N", on_click=nuevo),
            ui.ContextItem("Abrir carpeta…", icon="folder", shortcut="Ctrl+O"),
            "-",                                      # separador
            ui.ContextItem("Salir", icon="power", danger=True, on_click=app.quit),
        ],
        "Ver": [ui.ContextItem("Cambiar tema", icon="moon", on_click=alternar_tema)],
        "Ayuda": [ui.ContextItem("Acerca de", icon="info", on_click=acerca_de)],
    },
    brand="Mi app",              # nombre + logo a la izquierda
    actions=ui.NotificationButton(3),   # zona derecha opcional
)
```

Qué hace el cliente por ti (sin escribir JavaScript):

- abrir/cerrar el desplegable al hacer clic en el título,
- cambiar de menú al pasar el ratón cuando ya hay uno abierto,
- cerrar con `Escape`, con clic fuera o al elegir una opción,
- `aria-expanded` sincronizado para accesibilidad.

Los ítems pueden escribirse de tres formas equivalentes:

```python
ui.ContextItem("Abrir", icon="folder", on_click=abrir)      # componente
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
    icon="settings",
    items=[
        ui.ContextItem("Editar", icon="edit", on_click=editar),
        ui.ContextItem("Eliminar", icon="trash", danger=True, on_click=borrar),
    ],
    align="right",      # el panel se abre alineado a la derecha
)
```

---

## 4. `ContextMenu`: botón derecho

Envuelve el contenido sobre el que se quiere actuar:

```python
CONTEXTO = ui.ContextMenu(
    ui.ContextItem("Abrir", icon="folder", on_click=abrir),
    ui.ContextItem("Renombrar", icon="edit", on_click=renombrar),
    "-",
    ui.ContextItem("Eliminar", icon="trash", danger=True, on_click=eliminar),
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
    ui.Button("Nuevo", icon="plus", variant="primary", on_click=nuevo),
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
        ui.ListItem("Nueva tarea asignada", icon="check"),
        ui.ListItem("Comentario en tu informe", icon="mail"),
    ],
)
```

Al pulsarla se abre/cierra el panel (comportamiento incluido en el cliente).

---

## 8. Iconos

El paquete trae **202 iconos** propios (trazo 24×24), sin dependencias ni red:

```python
ui.Icon("check", size=6, class_="text-emerald-600")
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
app.quit()              # cierra la ventana nativa (o detiene el servidor)
```

Perfecto para las entradas `Ver → Cambiar tema` y `Archivo → Salir` del menú.

---

## 10. Ejemplo completo

[`examples/06_app_moderna.py`](../examples/06_app_moderna.py) reúne armazón,
barra de menús con atajos, menú contextual, búsqueda en vivo, campana de
notificaciones, galería de iconos, cambio de tema y cierre:

```bash
python examples/06_app_moderna.py
```
