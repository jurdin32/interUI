# Diálogos y ventanas modales

`interui` incluye un sistema completo de ventanas modales: avisos, información,
éxito, advertencia, error, crítico, confirmación, entrada de datos, formulario y
diálogos **totalmente personalizables**.

Todos comparten el mismo motor: se dibujan encima de la vista actual, atrapan el
foco, se cierran con `Escape` o con el fondo (configurable) y **no bloquean** el
canal de eventos: el resultado llega a un handler de Python.

---

## Índice

1. [Lo básico](#1-lo-básico)
2. [Tipos incluidos](#2-tipos-incluidos)
3. [Confirmar](#3-confirmar)
4. [Pedir un dato (input)](#4-pedir-un-dato-input)
5. [Formularios](#5-formularios)
6. [Diálogos a medida](#6-diálogos-a-medida)
7. [Botones propios](#7-botones-propios)
8. [Comportamiento y opciones](#8-comportamiento-y-opciones)
9. [Resultados en Python](#9-resultados-en-python)
10. [Recetas](#10-recetas)
11. [Diálogos del sistema operativo](#11-diálogos-del-sistema-operativo)

---

## 1. Lo básico

Se importa el objeto `dialog`:

```python
from interui import dialog, window, text, button

window(
    "Mi app",
    text("Panel principal"),
    button("Mostrar aviso", on_click=lambda: dialog.info("Proceso terminado")),
).run()
```

Se puede abrir desde cualquier handler y desde cualquier vista: la aplicación
guarda la pila de diálogos abiertos y los repinta encima de la página actual.

```python
dialog.show("Texto plano")                        # informativo, un botón
dialog.info("Guardado", title="Listo")
dialog.success("Todo correcto")
dialog.warning("Quedan 2 días")
dialog.error("No se pudo conectar")
dialog.critical("Se perdió la conexión con el servidor")
dialog.alert("Revisa la configuración", level="warning")
```

---

## 2. Tipos incluidos

| Función | Nivel / icono | Botones | Para qué |
|---|---|---|---|
| `dialog.show(msg)` | neutral | Cerrar | Mostrar información sin más. |
| `dialog.info(msg)` | azul · info | Cerrar | Aviso informativo. |
| `dialog.success(msg)` | verde · check | Cerrar | Confirmación de éxito. |
| `dialog.warning(msg)` | ámbar · alerta | Cerrar | Advertencia. |
| `dialog.error(msg)` | rojo · x | Cerrar | Error recuperable. |
| `dialog.critical(msg)` | rojo · alerta | Cerrar | Fallo grave; usa `dismissible=False`. |
| `dialog.alert(msg, level=…)` | el que pidas | Cerrar | Igual que los anteriores con nivel explícito. |
| `dialog.confirm(msg)` | índigo · pregunta | Cancelar / Aceptar | Confirmar una acción. |
| `dialog.input(label)` | índigo · pregunta | Cancelar / Aceptar | Pedir un dato. |
| `dialog.form(fields)` | índigo · pregunta | Cancelar / Aceptar | Varios campos. |
| `dialog.custom(*children)` | el que pidas | los que definas | Contenido propio. |

---

## 3. Confirmar

```python
from interui import dialog, toast, variant

def borrar() -> None:
    toast("Proyecto eliminado", "warning")

def preguntar() -> None:
    dialog.confirm(
        "Se eliminará el proyecto y sus archivos. Esta acción no se puede deshacer.",
        title="¿Eliminar proyecto?",
        accept_label="Eliminar",
        on_accept=borrar,
    )

button("Eliminar", variant=variant.danger, on_click=preguntar)
```

`on_cancel` se ejecuta al pulsar *Cancelar*, con `Escape` o al hacer clic fuera
(el fondo es descartable por defecto).

---

## 4. Pedir un dato (input)

```python
from interui import dialog, state, toast

nombre = state("")

def crear(evento) -> None:
    toast(f"Proyecto «{evento.value}» creado", "success")

def abrir() -> None:
    dialog.input(
        "Nombre del proyecto",
        title="Nuevo proyecto",
        placeholder="Mi proyecto",
        value=nombre.get(),
        on_accept=crear,
    )
```

El valor llega en `evento.value` (campo único) y en `evento.data["values"]`.

También puedes pasar una **señal** como handler: se guarda directamente el
texto introducido.

```python
nombre = state("")
dialog.input("Nombre", on_accept=nombre)     # nombre.set(texto)
```

Y si prefieres que el usuario escriba dentro de la página y no en un diálogo,
basta con `input(value=nombre, on_input=nombre)`.

---

## 5. Formularios

```python
def guardar(evento) -> None:
    datos = evento.data["values"]          # {"nombre": ..., "correo": ..., "notas": ...}
    toast(f"Guardado {datos['nombre']}", "success")

dialog.form(
    [
        {"name": "nombre", "label": "Nombre", "required": True},
        {"name": "correo", "label": "Correo", "type": "email"},
        {"name": "notas", "label": "Notas", "type": "textarea", "rows": 3},
    ],
    title="Nuevo contacto",
    accept_label="Guardar",
    on_accept=guardar,
)
```

- Cada campo es un diccionario con las mismas opciones que `ui.Input`
  (`label`, `placeholder`, `required`, `help_text`, `icon`…) o directamente un
  componente (`ui.Select(...)`, `ui.Switch(...)`).
- El diálogo usa un `<form>` real, así que `Enter` envía y la validación HTML
  básica funciona (`required`, `type="email"`).

---

## 6. Diálogos a medida

```python
from interui import dialog, card, text, progress, icon_badge, row, stat, tone

dialog.custom(
    row(
        icon_badge("cloud", tone=tone.primary),
        text("Copia de seguridad completada", weight="semibold"),
    ),
    progress(100, label="Archivos", show_value=True),
    stat("Tamaño total", "1,8 GB"),
    title="Resultado",
    width="lg",
    buttons=[("Cerrar", None, "outline")],
    on_close=lambda: print("cerrado"),
)
```

Puedes pasar cualquier árbol de componentes. El diálogo solo aporta el marco: fondo,
panel, cabecera y pie.

Para control total, instancia `ui.Dialog`:

```python
from interui import Dialog

manual = Dialog(
    text("Contenido totalmente libre"),
    title="Manual",
    level="warning",
    width="sm",
    dismissible=False,          # sin Escape ni clic fuera
    closable=False,             # sin aspa
    scrollable=True,            # cuerpo con scroll si es largo
)
app.show_dialog(manual)         # o ui.dialog: dialog.custom(...)
manual.close()
```

---

## 6 bis. Colores, esquinas y espaciados del modal

Todo el aspecto del panel se cambia con los mismos tokens que el resto del
framework, y **sin tocar la vista**: si el modal es de un formulario, se declara
en el `dialogs.py` de la app.

```python
# ventas/dialogs.py
class ClienteModal(ui.FormModal):
    form = ClienteForm
    width = "lg"
    options = dict(
        # superficie del panel
        bg=ui.colors.white,            # o colors.slate_900
        rounded="2xl",                 # "none" para esquinas rectas
        shadow="shadow-2xl",
        backdrop=ui.colors.slate_950,  # el velo oscuro de detrás
        # cabecera
        header_bg=ui.colors.slate_100,
        header_color=ui.colors.slate_900,
        header_border=ui.colors.slate_200,
        header_pad=ui.pad.px_5,
        title_font=ui.font.lg.bold,
        # pie
        footer_bg=ui.colors.slate_50,
        footer_pad=ui.pad.py_3,
        # espaciado
        body_pad=ui.pad.p_5,           # relleno del cuerpo
        gap=4,                         # separación entre los bloques del cuerpo
    )


ClienteModal.open()                    # alta
ClienteModal.open(instance=cliente)    # edición
```

Y en la vista solo aparece una vez:

```python
def inicio() -> ui.Component:
    # la tabla trae `new_modal = ClienteModal`; `form_mode="modal"` pone el botón
    return ui.RecordPage(ClienteTable, form_mode="modal")
```

| Opción | Qué cambia | Por defecto |
|---|---|---|
| `bg` | fondo del panel | blanco (o `slate-900` en oscuro) |
| `rounded` | esquinas: `"none"`, `"sm"`…`"3xl"` | `rounded-2xl` |
| `shadow` | sombra del panel | `shadow-2xl` |
| `backdrop` | velo de detrás | `bg-slate-950/50` |
| `header_bg` / `header_color` / `header_border` | franja del título | claro, sin fondo |
| `header_pad` / `body_pad` / `footer_pad` | rellenos (`ui.pad.p_5`, `"px-4 py-2"`) | `px-5 py-4` / `px-5 py-4` / `px-5 py-3` |
| `title_font` | tamaño y peso del título (`ui.font.lg.bold`) | `text-base font-semibold` |
| `footer_bg` | fondo del pie (zona de botones) | sin fondo |
| `gap` | separación entre los bloques del cuerpo (`4`, `ui.gap.all_6`) | `gap-3` |

Los diálogos hechos a mano (`ui.Dialog(...)`, `dialog.custom(...)`) aceptan
exactamente las mismas opciones.

---

## 7. Botones propios

`buttons=[(etiqueta, handler, variante), …]`:

```python
dialog.custom(
    text("¿Qué quieres hacer con el archivo?"),
    title="Archivo",
    buttons=[
        ("Cancelar", None, "outline"),
        ("Guardar copia", guardar_copia, "soft"),
        ("Sobrescribir", sobrescribir, "danger"),
    ],
)
```

Variantes disponibles: `primary`, `secondary`, `outline`, `ghost`, `soft`,
`danger`, `success`, `warning`, `link`. Si el handler es `None`, el botón solo
cierra el diálogo.

---

## 8. Comportamiento y opciones

| Opción | Por defecto | Efecto |
|---|---|---|
| `title` | `None` | Cabecera con `<h2>` (referenciado por `aria-labelledby`). |
| `message` | `None` | Texto principal bajo la cabecera. |
| `level` | según el tipo | `info`, `success`, `warning`, `error`, `critical`, `question`, `neutral`. |
| `icon` | según el nivel | Icono de la cabecera. |
| `width` | `"md"` | `xs`, `sm`, `md`, `lg`, `xl`, `full`. |
| `layer` | `"modal"` | `layer.modal`, `layer.panel` o `layer.blocking` (ver abajo). |
| `closable` | `True` | Muestra el aspa de cerrar. |
| `dismissible` | `True` | `Escape` y clic en el fondo cierran (ejecuta `on_close`). |
| `scrollable` | `False` | El cuerpo hace scroll en vez de desbordar. |
| `accept_label` / `cancel_label` / `close_label` | Aceptar / Cancelar / Cerrar | Texto de los botones. |
| `on_accept` | — | Se ejecuta al aceptar (recibe el `UIEvent`). |
| `on_cancel` | — | Se ejecuta al cancelar. |
| `on_close` | — | Se ejecuta al cerrar (aspa, fondo o `Escape`). |

Se renderizan con `role="dialog"`, `aria-modal="true"`, foco inicial en el primer
campo y animación de entrada (desactivada con `prefers-reduced-motion`).

### Niveles de modal

| `layer` | Comportamiento |
|---|---|
| `layer.modal` | Modal normal: se cierra con el aspa, `Escape` o el fondo. |
| `layer.panel` | Pensado para paneles laterales; no secuestra el primer plano. |
| `layer.blocking` | **Primer plano**: sin aspa, sin `Escape`, sin clic fuera. El único camino es aceptar. |
| `layer.alert` | Igual que `blocking`, con el tono de alerta. |

```python
ui.Dialog(
    ui.Text("Termina la importación antes de salir."),
    title="Hay un proceso en marcha",
    layer=ui.layer.blocking,
    on_accept=lambda _e: ui.toast("vale"),
)
```

Mientras haya uno abierto:

- `app.show_dialog(otro)` **no** lo abre: devuelve el bloqueante (`force=True` lo salta).
- `app.close_dialog()` sin argumentos no lo cierra; solo `dialogo.close()`.
- El fondo cubre toda la ventana (`z-index: 100`) y bloquea el puntero.

---

## 9. Resultados en Python

- **No bloquean**: el handler se ejecuta cuando el usuario responde. No hay
  `esperar_resultado()`; encadena la lógica en `on_accept`.
- **Varios diálogos**: se apilan; `dialog.close()` cierra el último y
  `app.close_all_dialogs()` todos.
- **Persistencia**: si cambias de vista con un diálogo abierto, sigue visible
  (vive en la aplicación, no en la página).

```python
handle = dialog.info("Hola")
handle.close()            # cerrar uno concreto
dialog.close()            # cerrar el último
app.close_all_dialogs()   # cerrar todos
```

---

## 10. Recetas

**Confirmación destructiva con doble seguridad**

```python
def borrar_todo() -> None:
    dialog.critical(
        "Se borrarán 42 registros de forma permanente.",
        title="Última confirmación",
        dismissible=False,
        accept_label="Sí, borrar todo",
        cancel_label="Cancelar",
        on_accept=lambda e: dialog.success("Registros eliminados"),
    )
```

**Renombrar un elemento**

```python
def renombrar(evento) -> None:
    seleccionado = evento.value
    dialog.input(
        "Nuevo nombre",
        title=f"Renombrar «{seleccionado}»",
        value=seleccionado,
        on_accept=lambda e: renombrar_a(seleccionado, e.value),
    )
```

**Diálogo con progreso (no descartable)**

```python
def empezar() -> None:
    dlg = dialog.custom(
        progress(0, label="Preparando…", indeterminate=True),
        title="Instalando",
        closable=False,
        dismissible=False,
        buttons=[],
    )
    lanzar_tarea(dlg)   # al terminar: dlg.close(); dialog.success("Instalado")
```

**Error con detalle técnico**

```python
dialog.custom(
    text("No se pudo abrir el archivo."),
    ui.code_block(trace, language="text", max_h="48"),
    title="Error",
    level="error",
    width="lg",
    buttons=[("Copiar detalle", lambda: app.native.clipboard_write(trace), "soft"),
             ("Cerrar", None, "outline")],
)
```

---

## 11. Diálogos del sistema operativo

Hay dos familias y conviene no confundirlas:

| | `dialog.*` (este documento) | `app.native.*` |
|---|---|---|
| Aspecto | HTML + Tailwind, dentro de tu app | Ventana del sistema operativo |
| Uso | Avisos, formularios, confirmaciones | Abrir/guardar archivos, notificaciones |
| Ejemplo | `dialog.input(...)` | `app.native.read_text()`, `app.native.notify()` |

Para mezclar ambos:

```python
def abrir_archivo() -> None:
    resultado = app.native.read_text(file_types=("Texto (*.txt)",))
    if resultado is None:
        return
    ruta, contenido = resultado
    if len(contenido) > 100_000:
        dialog.warning(f"El archivo es grande ({len(contenido):,} caracteres)")
```
