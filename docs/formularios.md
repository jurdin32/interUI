# Formularios

Un formulario es un archivo más de la app: se declara en `forms.py` y la vista
solo lo coloca en la página. No hay que construir los campos a mano, ni escribir
la validación, ni acordarse de guardar: `ui.ModelForm` lo hace mirando el modelo.

```text
mi_app/
└── ventas/
    ├── models.py     ← las tablas
    ├── forms.py      ← los formularios
    ├── tables.py     ← cómo se ve y se usa la tabla
    ├── views.py      ← las páginas (una línea cada una)
    └── urls.py       ← qué vista responde a cada ruta
```

`startapp` ya crea los archivos conectados y funcionando: si ejecutas
`makemigrations`, `migrate` y abres `/ventas`, tienes un alta de registros con
su tabla. Esta página explica cómo cambiar esos campos y qué más se puede hacer.

---

## 1. El modelo primero

El formulario sale del modelo, así que empieza por ahí:

```python
# ventas/models.py
import interui as ui


class Cliente(ui.Model):
    nombre = ui.Str(max_length=120)
    email = ui.Str(max_length=120, unique=True)
    telefono = ui.Str(max_length=30, null=True)
    activo = ui.Bool(default=True)

    class Meta:
        table = "clientes"
```

| Campo | Se convierte en |
|---|---|
| `Str` | campo de texto (o de correo, si el nombre lleva `email`, `correo` o `mail`) |
| `Email` | campo de correo |
| `Choice` | desplegable con las opciones de `choices` |
| `LongText` | área de texto |
| `Int`, `Float` | campo numérico |
| `Date`, `DateTime` | selector de fecha / fecha y hora |
| `Bool` | interruptor |
| `Json` | área de texto |

Los campos automáticos (`Auto`) y las claves primarias no aparecen: los pone la
base de datos.

---

## 2. El formulario

```python
# ventas/forms.py
import interui as ui

from ventas.models import Cliente


class ClienteForm(ui.ModelForm):
    model = Cliente
    fields = ["nombre", "email", "telefono", "activo"]
    title = "Nuevo cliente"
```

Eso es todo. Un control por campo, con su etiqueta, la validación de
obligatorios hecha en Python y el botón **Guardar** conectado.

| Atributo | Para qué | Por defecto |
|---|---|---|
| `model` | el modelo del que salen los campos | obligatorio |
| `fields` | qué campos se muestran y en qué orden | todos los editables |
| `exclude` | qué campos dejar fuera | `()` |
| `labels` | el nombre visible de cada campo | el nombre del campo |
| `title` | título de la tarjeta | «Nuevo cliente» |
| `submit_label` | texto del botón | `"Guardar"` |
| `on_saved` | función que recibe el registro guardado | `None` |

### Iconos y textos de ayuda

```python
class ClienteForm(ui.ModelForm):
    model = Cliente
    icons = {"nombre": "user", "email": "mail", "ciudad": "building"}
    placeholders = {"email": "tu@correo.com", "telefono": "+34 600 000 000"}
```

Los dos se pueden omitir: sin `icons`, cada campo elige el suyo por su nombre
(`email`/`correo` → correo, `telefono` → teléfono, `nombre` → persona,
`direccion` → mapa, `cedula`/`documento` → almohadilla, `precio` → etiqueta…).
Un `Bool` no lleva icono y un `Choice` es un desplegable.

### Los nombres de los campos

`labels` cambia el texto que se ve: en el formulario **y** en la tabla de la
vista, porque los dos leen del formulario. Sin `labels`, el nombre del campo
(`fecha_nacimiento`) se muestra con espacios y mayúscula («Fecha nacimiento»).

```python
class ClienteForm(ui.ModelForm):
    model = Cliente
    fields = ["nombre", "email", "fecha_nacimiento"]
    labels = {
        "nombre": "Nombre completo",
        "email": "Correo electrónico",
        "fecha_nacimiento": "Fecha de nacimiento",
    }
```

Este archivo es el único sitio donde se decide **qué campos salen** y **cómo se
llaman**: `fields` manda sobre el orden y `labels` sobre los nombres.

Si el modelo tiene muchos campos y solo quieres cambiar un par, usa `exclude`:

```python
class ClienteForm(ui.ModelForm):
    model = Cliente
    exclude = ["telefono"]
```

### Sin declarar clase

Para un formulario suelto, dentro de una vista o de un ejemplo:

```python
ui.ModelForm(Cliente)
```

Es el mismo formulario con los valores por defecto.

> El nombre empieza por mayúscula porque es un componente. `ui.Form` (y su
> alias `ui.form`) son otra cosa: la etiqueta HTML `<form>`.

---

## 3. La vista

La vista no sabe nada de campos, nombres ni validación. Estas diez líneas son
todo:

```python
# ventas/views.py
import interui as ui

from ventas.forms import ClienteForm


def lista() -> ui.Component:
    return ui.RecordPage(ClienteForm(), title="Clientes")
```

Eso pinta el título, el contador, el formulario y la tabla. Y si prefieres
colocarlo por partes (para añadir un resumen, una búsqueda, otra tarjeta…):

```python
def lista() -> ui.Component:
    form = ClienteForm(margin=ui.margin.t_6)
    return ui.Screen(
        ui.Container(pad=ui.pad.py_10)(
            ui.Heading("Clientes", level=1),
            ui.Muted(ui.RecordCounter(form)),      # «3 registros guardados»
            form,                                  # el formulario
            ui.RecordTable(form),                  # la tabla de lo guardado
        )
    )
```

| Pieza | Qué pinta |
|---|---|
| `ui.RecordPage(form, title=…)` | la página entera: título + contador + formulario + tabla |
| `ClienteForm(...)` | la tarjeta con los campos y el botón |
| `ui.RecordTable(form)` | la tabla con lo guardado, con las columnas y nombres del formulario |
| `ui.RecordCounter(form)` | el contador (`0 registros guardados`, `1 registro guardado`…) |

Sin `title`, el título es el plural del modelo (`Persona` → «Personas»). Las
columnas de la tabla se pueden acortar sin tocar el formulario:
`ui.RecordTable(form, columns=["nombre", "email"])`.

### Elegir qué se ve: formulario dentro, en modal o ninguno

| `form_mode` | La página muestra |
|---|---|
| `"inline"` (por defecto) | el formulario dentro de la página, y la tabla debajo |
| `"modal"` | solo el contador y la tabla, con un botón **Nuevo** que abre el formulario en un diálogo |
| `"none"` | solo el contador y la tabla (sin botón) |

```python
ui.RecordPage(PersonaForm(), title="Personas", form_mode="modal")
ui.RecordPage(PersonaForm(), title="Personas", form_mode="none")
ui.RecordPage(PersonaForm(), title="Personas", table=False)   # solo el formulario
```

El botón se cambia con `new_label="Nueva persona"` y `new_icon=ui.icons.plus`. El
diálogo se genera **solo** a partir del formulario: mismos campos, mismas
etiquetas, mismos iconos.

### Buscar, ordenar y paginar

`ui.RecordTable` (y `ui.RecordPage`) traen las tres cosas de serie y se
configuran desde la vista:

```python
ui.RecordPage(
    PersonaForm(),
    title="Personas",
    search=True,                 # buscador arriba de la tabla
    page_size=10,                # 10, 15 o 20 (selector en el pie)
    order_by="nombres",          # orden inicial («-creado» para descendente)
    sortable=["nombres", "email"],   # qué cabeceras se pueden pulsar
)
```

| Opción | Qué hace | Por defecto |
|---|---|---|
| `search` | muestra el buscador | `False` |
| `search_columns` | en qué campos busca (`["email"]`) | las columnas visibles |
| `search_placeholder` | texto del buscador | `"Buscar…"` |
| `page_size` | filas por página; `None` las muestra todas | `10` |
| `page_sizes` | tamaños del selector | `(10, 15, 20)` |
| `sort` | cabeceras que ordenan al pulsarlas | `True` |
| `sortable` | qué columnas ordenan | todas las visibles |
| `order_by` | orden inicial; `"-campo"` empieza de mayor a menor | sin orden |

La búsqueda es **global** (el texto en cualquiera de las columnas, sin distinguir
mayúsculas) y vuelve a la primera página. Al pulsar una cabecera se ordena
ascendente y, si la pulsas otra vez, descendente; la columna activa muestra la
flecha.

#### El pie de la tabla

Cuando hay `page_size`, debajo de la tabla aparece una sola línea con el
resumen a la izquierda y los controles a la derecha:

```
Mostrando 1–10 de 25                     [10 ▾]  ‹  1 de 3  ›
```

- **`Mostrando 3–12 de 25`** cuenta solo las filas que cumplen la búsqueda;
  `25` es el total guardado. Con una búsqueda que deja pocas filas sigue
  apareciendo (`Mostrando 1–2 de 2`), para no perder el selector de tamaño.
- **`[10 ▾]`** cambia las filas por página (`page_sizes`) y vuelve a la primera.
- **`‹ 1 de 3 ›`** navega; los extremos se deshabilitan solos. El número de
  páginas se recalcula con lo filtrado.

Con `page_size=None` el pie desaparece y se ven todos los registros de una vez.

Los controles no se salen de la tarjeta: si la ventana es muy estrecha, el grupo
de la derecha baja a una segunda línea entero (no se parte por dentro).

Todo se resuelve en Python sobre los registros ya cargados: funciona igual con
SQLite, PostgreSQL o MySQL, sin tocar el motor.

### La tabla en su archivo: `tables.py`

Las opciones de la tabla **no van en la vista**. `startapp` crea un `tables.py`
con todo declarado como atributos de una clase, y la vista solo la coloca:

```python
# ventas/tables.py
import interui as ui

from ventas.forms import ClienteForm
from ventas.models import Cliente


def editar(registro: Cliente) -> None:
    ui.form_dialog(ClienteForm, instance=registro, title="Editar cliente")


def eliminar(registro: Cliente) -> None:
    registro.delete()
    ui.toast("Registro eliminado", "success")


class ClienteTable(ui.RecordTable):
    form = ClienteForm
    columns = ["nombre", "email", "activo"]

    search = True
    page_size = 10
    order_by = "nombre"

    striped = True
    header_bg = ui.colors.slate_100
    header_color = ui.colors.slate_700
    selected_bg = ui.colors.indigo_50
    cell_colors = {"email": ui.colors.slate_500}

    actions = False
    selectable = True
    on_row_dblclick = editar
    context_menu = [
        ui.RowAction("Editar", icon=ui.icons.edit, on_click=editar),
        ui.RowAction("Eliminar", icon=ui.icons.trash, danger=True,
                     confirm="¿Eliminar este cliente?", on_click=eliminar),
    ]
```

```python
# ventas/views.py
import interui as ui

from ventas.tables import ClienteTable


def inicio() -> ui.Component:
    return ui.RecordPage(ClienteTable)
```

La página toma de la tabla **el formulario y todas las opciones**, así que
`views.py` queda en una línea. Cualquier atributo se puede pisar al vuelo cuando
hace falta una variante: `ClienteTable(page_size=50)`.

### Colores, cebra y encabezado

Todo el aspecto se configura con los mismos tokens de estilo del resto del
framework (`ui.colors.*`), en `tables.py` o al crear la tabla:

```python
ui.RecordPage(
    PersonaForm(),
    table_options=dict(
        striped=True,                          # filas alternas (cebra)
        zebra=ui.colors.amber_50,              # color de la fila alterna
        header_bg=ui.colors.slate_100,         # fondo del encabezado
        header_color=ui.colors.slate_700,      # color del texto del encabezado
        hover_bg=ui.colors.indigo_50,          # al pasar el ratón
        cell_colors={"email": ui.colors.slate_500},   # por columna
        column_bg={"activo": ui.colors.slate_50},     # fondo por columna
        selected_bg=ui.colors.indigo_100,      # fila seleccionada
    ),
)
```

| Opción | Qué cambia | Por defecto |
|---|---|---|
| `striped` | pinta una fila sí y otra no | `False` |
| `zebra` | color de esas filas alternas | `slate-50/60` |
| `header_bg` | fondo de la fila de encabezados | `slate-50/80` |
| `header_color` | color del texto de los encabezados | `slate-500` |
| `hover_bg` | fondo al pasar el ratón por una fila | `slate-50` |
| `cell_colors` | color de texto por columna (`{"email": …}`) | el del texto normal |
| `column_bg` | fondo por columna | sin fondo |
| `selected_bg` | fondo de la fila seleccionada | `indigo-50` |

El modo oscuro sigue funcionando: si no fijas un color, cada pieza tiene su
variante `dark:`; si fijas uno, se usa el mismo en los dos temas.

**Doble clic en una celda selecciona su contenido entero**, como en una hoja de
cálculo (no hace falta configurar nada).

### Interacción por fila: clic, doble clic y clic derecho

Los botones por fila son opcionales. Con `actions=False` desaparecen y la tabla
se maneja con el ratón:

```python
ui.RecordPage(
    PersonaForm(),
    actions=False,                 # sin botones por fila
    table_options=dict(
        selectable=True,                    # el clic marca la fila
        on_row_dblclick=editar,             # doble clic → modal de edición
        context_menu=[                      # clic derecho → menú en el cursor
            ui.RowAction("Editar", icon=ui.icons.edit, on_click=editar),
            ui.RowAction("Eliminar", icon=ui.icons.trash, danger=True,
                         confirm="¿Eliminar esta persona?", on_click=eliminar),
        ],
    ),
)
```

| Opción | Qué hace |
|---|---|
| `actions` | los iconos al final de la fila; `False` los esconde |
| `selectable` | el clic selecciona la fila y la deja resaltada con `selected_bg` |
| `on_row_click` | handler del clic; recibe **el registro** |
| `on_row_dblclick` | handler del doble clic; recibe **el registro** |
| `context_menu` | acciones del clic derecho (`RowAction`) o una función `registro → [acciones]` |
| `row_context` | variante avanzada: menú construido por ti para cada fila |

`on_row_click`, `on_row_dblclick` y `context_menu` se combinan: por ejemplo, el
clic selecciona y el doble clic abre el modal, sin botones de por medio. El menú
contextual hereda `danger=True` (en rojo) y `confirm="…"` de `RowAction`, igual
que los botones.

### Acciones en cada fila: editar y eliminar

`actions=` añade iconos al final de cada fila. El handler recibe **el registro**
de esa fila:

```python
def editar(registro: Persona) -> None:
    ui.form_dialog(PersonaForm, instance=registro, title="Editar persona")


def eliminar(registro: Persona) -> None:
    registro.delete()
    ui.toast("Registro eliminado", "success")


def inicio() -> ui.Component:
    return ui.RecordPage(
        PersonaForm(),
        title="Personas",
        columns=["cedula", "nombres", "email", "activo"],   # menos columnas, más sitio
        actions=[
            ui.RowAction("Editar", icon=ui.icons.edit, on_click=editar),
            ui.RowAction(
                "Eliminar",
                icon=ui.icons.trash,
                danger=True,
                confirm="¿Eliminar esta persona?",
                on_click=eliminar,
            ),
        ],
    )
```

| Opción de `RowAction` | Para qué |
|---|---|
| `on_click` | la función que recibe el registro de la fila |
| `icon` | el icono del botón (`ui.icons.*`) |
| `label` | texto del tooltip y de accesibilidad |
| `danger=True` | lo pinta en rojo |
| `confirm="…"` | pregunta antes de ejecutar |

### Editar en un modal con el formulario

`ui.form_dialog(PersonaForm, instance=registro)` abre el formulario dentro de un
diálogo, ya relleno, y lo cierra al guardar. Como el formulario lleva el
registro cargado, **actualiza** en vez de crear, y su propia fila no cuenta como
duplicado en los campos `unique`.

```python
ui.form_dialog(PersonaForm, instance=registro, title="Editar persona")
ui.form_dialog(PersonaForm, title="Nueva persona")     # alta, sin registro
```

Opciones: `title`, `width` (`"sm"`, `"md"`, `"lg"`, `"xl"`), `cancel_label` y
`on_saved` (se ejecuta después de guardar y antes de cerrar).

`RecordTable` y `RecordCounter` reciben **el formulario**, no el modelo: así no
hay que repetir la lista de campos y, si añades una columna en `forms.py`,
aparece en la tabla sin tocar la vista. Si la tabla de la base de datos todavía
no existe (falta `migrate`), `RecordTable` muestra un aviso en su lugar en vez de
romper la página.

> ¿Quieres otra tabla (un resumen, una búsqueda)? Escribe tu `ui.Table` con las
> filas que necesites; `RecordTable` es solo el caso más común hecho.

```python
# ventas/urls.py
from ventas import views

urlpatterns = [
    ("/clientes", views.lista, "Clientes"),
]


def register(app) -> None:
    for path, view, title in urlpatterns:
        app.page(path, title=title)(view)
```

Al pulsar **Guardar** pasan tres cosas: se validan los campos, se crea el
registro con `Cliente.objects.create(...)` y la página se repinta sola para
mostrarlo en la tabla. Si algo falta, los errores salen en la tarjeta y no se
guarda nada; en cuanto corriges un campo, el aviso desaparece.

---

## 4. Dónde viven los valores

Los valores de los campos son **señales** de la app en la que se está pintando
el formulario. Por eso el usuario puede escribir sin que el texto desaparezca
cuando la página se repinta, y por eso el formulario puede vivir en su propio
archivo sin recibir nada de la vista.

Cada formulario usa una clave por campo:

```text
form_clientes_nombre
form_clientes_email
form_clientes_errores
```

Si necesitas dos formularios del mismo modelo en la misma página, dale un
`prefix` distinto a cada uno para que no compartan claves:

```python
ClienteForm(prefix="principal")
ClienteForm(prefix="rapido")
```

---

## 5. Guardar y hacer algo más

`on_saved` recibe el registro recién creado. Sirve para avisar, navegar o
rellenar otra parte de la pantalla:

```python
class ClienteForm(ui.ModelForm):
    model = Cliente

    def on_saved(self, cliente) -> None:
        ui.toast(f"{cliente.nombre} añadido", "success")
        ui.current_app().navigate("/clientes")
```

También puedes pasarlo sin declarar clase:

```python
ClienteForm = ui.ModelForm(Cliente, on_saved=lambda cliente: ui.toast(cliente.nombre, "success"))
```

---

## 6. Validar más de lo que dice el modelo

`ModelForm` ya comprueba lo obligatorio y los campos `unique`. Para reglas
propias, sobrescribe `guardar()` o valida antes con `ui.state`. Lo más simple es
añadir la comprobación al modelo con un método y llamarlo desde la vista:

```python
class ClienteForm(ui.ModelForm):
    model = Cliente

    def on_saved(self, cliente) -> None:
        if not cliente.email.endswith("@empresa.com"):
            ui.toast("Correo externo: revísalo", "warning")
```

Si necesitas un formulario que **no** salga de un modelo (una búsqueda, unos
ajustes), no uses `ModelForm`: compón los controles y guarda los valores en
señales con `ui.state`.

---

## 7. `ui.state()` en las vistas

Dentro de una vista puedes crear señales con `ui.state` igual que en un ejemplo
de un solo archivo:

```python
def buscador() -> ui.Component:
    filtro = ui.state("")

    return ui.Screen(
        ui.Input(filtro.get(), label="Buscar", on_input=filtro),
        ui.Text(lambda: f"Buscando: {filtro.get()}", size=ui.size.sm, tone=ui.tone.muted),
    )
```

La señal pertenece a la app del proyecto (no a una app implícita), así que se
mantiene entre repintados y navegaciones. El valor inicial solo se aplica la
primera vez: si vuelves a llamar a `ui.state("")` sobre una señal ya creada, no
la reinicia.

| Forma | Cuándo |
|---|---|
| `ui.state(valor)` | señal suelta dentro de una vista |
| `ui.state(valor, name="clave")` | cuando quieres un nombre fijo y legible |
| `app.state("clave", valor)` | en `main.py` o en un archivo de un solo uso |

---

## 8. Errores frecuentes

| Síntoma | Causa |
|---|---|
| `AttributeError: module 'interui' has no attribute 'Xxx'` | el campo no existe: los disponibles son `Int`, `Str`, `Email`, `Choice`, `LongText`, `Bool`, `Float`, `Date`, `DateTime`, `Json`, `Blob` y `FK` |
| `TypeError: ModelForm necesita un modelo` | falta `model = ...` en la clase |
| Un campo del modelo no sale en el formulario | está en `exclude`, o lo genera la base de datos (`Auto`, `auto_now_add`, `auto_now`) |
| La tabla dice «Todavía no hay registros» tras guardar | falta `python iui.py migrate`: la tabla no existe |
| Dos formularios se pisan el texto | comparten `prefix`; dale uno distinto a cada uno |
| `ui.state("x", "")` falla | la firma es `ui.state(valor, name="x")` |

---

## Siguiente paso

- [Datos](datos.md): consultas, filtros y migraciones.
- [Controles](controles.md): todos los campos disponibles y sus opciones.
- [Anatomía de un proyecto](proyecto.md): dónde va cada archivo.
