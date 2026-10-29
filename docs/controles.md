# Referencia de controles de interUI

Un ejemplo **ejecutable** por cada control, más su firma. Todos se importan del
paquete:

```python
import interui as ui
```

> Este archivo se genera desde el código con `python scripts/gen_docs.py`.
> `tests/test_docs.py` evalúa y renderiza cada ejemplo: si un control cambia y la
> documentación no, las pruebas fallan.

## Convenciones comunes

El estilo se escribe con **notación de punto**, nunca con clases a mano:

```python
ui.Card(title="Hola", bg=ui.colors.white, rounded=ui.radius.xxl, shadow=ui.shadow.md)(
    ui.Text("mundo", color=ui.colors.slate_700, font=ui.font.lg.semibold)
)
```

| Propiedad | Tipo | Efecto |
|---|---|---|
| `bg`, `color`, `border_color` | token | `ui.colors.red_500`, `ui.colors.hex("#0f172a")`, `ui.gradient.br(a, b)`. |
| `pad`, `margin`, `gap` | token | `ui.pad.py_6`, `ui.margin.mt_4`, `ui.gap.g_2`. |
| `rounded`, `shadow`, `font` | token | `ui.radius.lg`, `ui.shadow.md`, `ui.font.sm.medium`. |
| `variant`, `tone`, `size`, `layer`, `side` | token | `ui.variant.primary`, `ui.tone.danger`, `ui.size.lg`. |
| `icon` | token | `ui.icons.check` (los 204 iconos, ver [iconos](iconos.md)). |
| `class_` | `str` | Escape: clases Tailwind extra; sustituyen a las del control cuando chocan. |
| `id` | `str` | Identificador estable (por defecto se genera por posición). |
| `key` | `Any` | Sufijo estable del `id` dentro de listas. |
| `visible` / `when` | `bool` / `callable` | No renderiza el control. |
| `hidden` | `bool` | Renderiza oculto (`hidden`). |
| `style` | `str` / `dict` | Estilos en línea. |
| `data` | `dict` | Atributos `data-*` (comportamientos del cliente). |
| `aria` | `dict` | Atributos `aria-*`. |
| `on_*` | `callable` | Handler en Python. Puede ser una función sin argumentos, una función que recibe el evento o **una señal** (`on_input=nombre`). |

Además:

* **Todos los controles tienen alias en minúsculas**: `ui.button` es `ui.Button`,
  `ui.data_table` es `ui.DataTable`… Se muestran bajo cada título.
* **Los hijos pueden ser señales o funciones**: `text("Total: ", total)` y
  `text(lambda: f"{total.get() * 2}")` se recalculan en cada render.
* Para una ventana con texto y botón en pocas líneas: `ui.window(...)`, `ui.state(...)`,
  `ui.row(...)` (ver [la guía](guia.md)).

Los hijos se pasan como posicionales y se pueden añadir después con `(...)`:

```python
card = ui.Card(title="Hola")
card(ui.Text("mundo"))
```


## Ventana y estructura

### `ui.AspectRatio`

Alias en minúsculas: `ui.aspect_ratio`

Mantiene una proporción fija.

```text
ui.AspectRatio(*children, ratio="video")
```

```python
ui.AspectRatio(ui.Center(ui.Text("16:9")), ratio="video")
```

### `ui.Center`

Alias en minúsculas: `ui.center`

Centra el contenido en ambos ejes.

```text
ui.Center(*children)
```

```python
ui.Center(ui.Text("centrado"), class_="h-40")
```

### `ui.Col`

Alias en minúsculas: `ui.col`

Columna responsive (`span`, `sm`, `md`, `lg`, `xl`, `xxl`).

```text
ui.Col(*children, span=12, sm=None, md=None, lg=None, xl=None, xxl=None, offset=None, order=None)
```

```python
ui.Row(ui.Col(span=12, md=6, lg=4)(ui.Text("12 → 6 → 4 columnas")))
```

### `ui.Container`

Alias en minúsculas: `ui.container`

Centra el contenido y limita el ancho máximo.

```text
ui.Container(*children, size=size.xl, padded=True)
```

```python
ui.Container(size="prose")(ui.Text("ancho limitado y centrado"))
```

### `ui.Divider`

Alias en minúsculas: `ui.divider`

Separador con etiqueta opcional.

```text
ui.Divider(label=None, orientation="horizontal")
```

```python
ui.Divider("o")
```

### `ui.Grid`

Alias en minúsculas: `ui.grid`

Rejilla nativa de Tailwind (columnas por breakpoint).

```text
ui.Grid(*children, cols=1, sm=None, md=None, lg=None, xl=None, gap=4)
```

```python
ui.Grid(ui.Text("a"), ui.Text("b"), cols=1, md=2, gap=4)
```

### `ui.Row`

Fila de la rejilla de 12 columnas.

```text
ui.Row(*children, gap=4, gap_y=None, align="stretch", justify="start", cols=12, dense=False)
```

```python
ui.Row(ui.Col(span=6)(ui.Text("izquierda")), ui.Col(span=6)(ui.Text("derecha")))
```

### `ui.Screen`

Alias en minúsculas: `ui.screen`

Raíz de la ventana: ocupa todo el alto y define el fondo del tema.

```text
ui.Screen(*children)
```

```python
ui.Screen(ui.Text("contenido de la ventana"), class_="p-6")
```

### `ui.ScrollArea`

Alias en minúsculas: `ui.scroll_area`

Área con scroll y altura máxima.

```text
ui.ScrollArea(*children, max_h="80", axis="y")
```

```python
ui.ScrollArea(ui.Text("mucho contenido"), max_h="48")
```

### `ui.Spacer`

Alias en minúsculas: `ui.spacer`

Empuja el contenido en un flexbox.

```python
ui.Stack(ui.Text("izq"), ui.Spacer(), ui.Text("der"), direction="row")
```

### `ui.Stack`

Alias en minúsculas: `ui.stack`

Apila hijos en vertical u horizontal con separación uniforme.

```text
ui.Stack(*children, direction="col", gap=4, align="stretch", justify="start", wrap=False)
```

```python
ui.Stack(ui.Text("uno"), ui.Text("dos"), direction="row", gap=3)
```


## Tipografía y texto

### `ui.Announcement`

Alias en minúsculas: `ui.announcement`

Franja de anuncio a todo el ancho.

```text
ui.Announcement(*children, variant=variant.primary)
```

```python
ui.Announcement("Nueva versión disponible")
```

### `ui.Badge`

Alias en minúsculas: `ui.badge`

Etiqueta compacta con variantes de color.

```text
ui.Badge(label="", variant=variant.neutral, size=size.md, dot=False, icon=None, pill=True)
```

```python
ui.Badge("nuevo", variant=ui.variant.success, dot=True)
```

### `ui.Blockquote`

Alias en minúsculas: `ui.blockquote`

Cita con autor opcional.

```text
ui.Blockquote(*children, cite=None)
```

```python
ui.Blockquote("La simplicidad es la máxima sofisticación.", cite="Leonardo")
```

### `ui.Chip`

Alias en minúsculas: `ui.chip`

Etiqueta con botón de borrado.

```text
ui.Chip(label="", on_remove=None, variant=variant.neutral)
```

```python
ui.Chip("python", variant=ui.variant.primary)
```

### `ui.Code`

Alias en minúsculas: `ui.code`

Código en línea.

```text
ui.Code(*children)
```

```python
ui.Code("pip install interui")
```

### `ui.CodeBlock`

Alias en minúsculas: `ui.code_block`

Bloque de código con botón de copiar.

```text
ui.CodeBlock(code="", language=None, filename=None, max_h="none")
```

```python
ui.CodeBlock("print('hola')", language="python", filename="demo.py")
```

### `ui.Em`

Alias en minúsculas: `ui.em`

Texto en cursiva semántica.

```text
ui.Em(*children)
```

```python
ui.Em("énfasis")
```

### `ui.Heading`

Alias en minúsculas: `ui.heading`

Encabezado `h1`–`h6`.

```text
ui.Heading(*children, level=2, tone=tone.default)
```

```python
ui.Heading("Sección", level=2)
```

### `ui.Kbd`

Alias en minúsculas: `ui.kbd`

Tecla de teclado.

```text
ui.Kbd(*children)
```

```python
ui.Stack(ui.Kbd("Ctrl"), ui.Kbd("K"), direction="row", gap=1)
```

### `ui.Label`

Alias en minúsculas: `ui.label`

Etiqueta de campo.

```text
ui.Label(*children, required=False, for_=None)
```

```python
ui.Label("Correo electrónico", for_="campo", required=True)
```

### `ui.Lead`

Alias en minúsculas: `ui.lead`

Entradilla destacada.

```text
ui.Lead(*children)
```

```python
ui.Lead("Entradilla que resume el contenido.")
```

### `ui.Link`

Alias en minúsculas: `ui.link`

Enlace interno o externo.

```text
ui.Link(*children, href="#", external=False)
```

```python
ui.Link("Documentación", href="https://tailwindcss.com")
```

### `ui.Mark`

Alias en minúsculas: `ui.mark`

Texto resaltado.

```text
ui.Mark(*children)
```

```python
ui.Mark("resaltado")
```

### `ui.Muted`

Alias en minúsculas: `ui.muted`

Texto secundario atenuado.

```text
ui.Muted(*children)
```

```python
ui.Muted("Texto secundario")
```

### `ui.Paragraph`

Alias en minúsculas: `ui.paragraph`

Párrafo con interlineado relajado.

```text
ui.Paragraph(*children, tone=tone.default, size=size.base)
```

```python
ui.Paragraph("Un párrafo con interlineado relajado para leer cómodo.")
```

### `ui.Small`

Alias en minúsculas: `ui.small`

Nota de tamaño reducido.

```text
ui.Small(*children)
```

```python
ui.Small("nota al pie")
```

### `ui.Strong`

Alias en minúsculas: `ui.strong`

Texto en negrita semántica.

```text
ui.Strong(*children)
```

```python
ui.Strong("importante")
```

### `ui.Text`

Alias en minúsculas: `ui.text`

Texto con tamaño, tono y peso.

```text
ui.Text(*children, size=size.base, tone=tone.default, weight=None, leading=None, truncate=False)
```

```python
ui.Text("Texto normal", size=ui.size.lg, tone=ui.tone.muted, weight="medium")
```

### `ui.Title`

Título principal con subtítulo.

```text
ui.Title(*children, subtitle=None)
```

```python
ui.Title("Mi aplicación", subtitle="Subtítulo descriptivo")
```


## Botones y acciones

### `ui.Button`

Alias en minúsculas: `ui.button`

Botón con variantes, tamaños, iconos y estado de carga.

```text
ui.Button(*children, label=None, variant=variant.primary, size=size.md, icon=None, icon_right=None, loading=False, disabled=False, submit=False, full_width=False, href=None, pill=False)
```

```python
ui.Button("Guardar", icon=ui.icons.check, variant=ui.variant.primary, on_click=lambda: None)
```

### `ui.ButtonGroup`

Alias en minúsculas: `ui.button_group`

Botones pegados horizontal o verticalmente.

```text
ui.ButtonGroup(*children, vertical=False)
```

```python
ui.ButtonGroup(ui.Button("Día", variant=ui.variant.outline), ui.Button("Semana", variant=ui.variant.outline))
```

### `ui.CopyButton`

Alias en minúsculas: `ui.copy_button`

Copia un texto al portapapeles sin ir al servidor.

```text
ui.CopyButton(text, label="Copiar", icon=icons.copy)
```

```python
ui.CopyButton("texto que se copia")
```

### `ui.Fab`

Alias en minúsculas: `ui.fab`

Botón flotante de acción.

```text
ui.Fab(icon=icons.plus, label=None)
```

```python
ui.Fab("plus", label="Nuevo")
```

### `ui.IconButton`

Alias en minúsculas: `ui.icon_button`

Botón cuadrado solo con icono.

```text
ui.IconButton(icon=icons.more_h, label=None, variant=variant.ghost, size=size.md, loading=False, disabled=False, href=None)
```

```python
ui.IconButton("settings", label="Ajustes", variant=ui.variant.outline)
```

### `ui.LinkButton`

Alias en minúsculas: `ui.link_button`

Botón con apariencia de botón que navega a `href`.

```text
ui.LinkButton(*children, label=None, variant=variant.primary, size=size.md, icon=None, icon_right=None, loading=False, disabled=False, submit=False, full_width=False, href=None, pill=False)
```

```python
ui.Button("Ir a ajustes", href="/ajustes", variant=ui.variant.outline)
```

### `ui.Spinner`

Alias en minúsculas: `ui.spinner`

Indicador de carga animado.

```text
ui.Spinner(size=4)
```

```python
ui.Spinner(size=5)
```


## Formularios

### `ui.Checkbox`

Alias en minúsculas: `ui.checkbox`

Casilla con etiqueta.

```text
ui.Checkbox(label=None, checked=False, value="on", name=None, disabled=False, help_text=None, indeterminate=False)
```

```python
ui.Checkbox("Acepto los términos", checked=True)
```

### `ui.CheckboxGroup`

Alias en minúsculas: `ui.checkbox_group`

Grupo de casillas.

```text
ui.CheckboxGroup(items=None, values=None, name=None, label=None, help_text=None, columns=1, on_change=None)
```

```python
ui.CheckboxGroup(["Correo", "Push", "SMS"], values=["Push"], label="Canales")
```

### `ui.ColorInput`

Alias en minúsculas: `ui.color_input`

Selector de color.

```text
ui.ColorInput(value="#4f46e5", label=None, name=None, on_change=None)
```

```python
ui.ColorInput("#4f46e5", label="Color de marca")
```

### `ui.Combobox`

Alias en minúsculas: `ui.combobox`

Texto con sugerencias (`datalist`).

```text
ui.Combobox(value="", items=None, label=None, help_text=None, error=None, placeholder=None, name=None, on_change=None)
```

```python
ui.Combobox("", items=["Madrid", "Barcelona"], label="Ciudad")
```

### `ui.Datalist`

Alias en minúsculas: `ui.datalist`

Lista de sugerencias suelta.

```text
ui.Datalist(items=None)
```

```python
ui.Datalist(["uno", "dos"])
```

### `ui.DateInput`

Alias en minúsculas: `ui.date_input`

Selector de fecha.

```text
ui.DateInput(value="")
```

```python
ui.DateInput("2026-01-31", label="Fecha")
```

### `ui.DateRangeInput`

Alias en minúsculas: `ui.date_range_input`

Rango de fechas.

```text
ui.DateRangeInput(start="", end="", label=None, start_label="Desde", end_label="Hasta", on_change=None)
```

```python
ui.DateRangeInput("2026-01-01", "2026-01-31", label="Periodo")
```

### `ui.DateTimeInput`

Alias en minúsculas: `ui.date_time_input`

Fecha y hora.

```text
ui.DateTimeInput(value="")
```

```python
ui.DateTimeInput("2026-01-31T09:30", label="Fecha y hora")
```

### `ui.Dropzone`

Alias en minúsculas: `ui.dropzone`

Zona de arrastrar y soltar archivos.

```text
ui.Dropzone(*children, label="Arrastra archivos aquí", hint="o haz clic para seleccionarlos", accept=None, multiple=True)
```

```python
ui.Dropzone(label="Suelta archivos aquí", accept=".csv")
```

### `ui.EmailInput`

Alias en minúsculas: `ui.email_input`

Campo de correo.

```text
ui.EmailInput(*children)
```

```python
ui.EmailInput("", label="Correo", help_text="No lo compartiremos")
```

### `ui.Fieldset`

Alias en minúsculas: `ui.fieldset`

Grupo de campos con leyenda.

```text
ui.Fieldset(*children, legend=None)
```

```python
ui.Fieldset(ui.Input("", label="Calle"), legend="Dirección")
```

### `ui.FileInput`

Alias en minúsculas: `ui.file_input`

Selector de archivos (se suben al proceso local).

```text
ui.FileInput(accept=None, multiple=False, label=None, help_text=None, name=None)
```

```python
ui.FileInput(label="Adjuntar", accept=".pdf,.txt", multiple=True)
```

### `ui.Form`

Alias en minúsculas: `ui.form`

Formulario que envía todos los campos a Python.

```text
ui.Form(*children, on_submit=None, layout="stack", gap=4)
```

```python
ui.Form(ui.Input("", label="Nombre"), ui.Button("Enviar", submit=True), on_submit=lambda e: None)
```

### `ui.FormField`

Alias en minúsculas: `ui.form_field`

Envuelve un control con etiqueta, ayuda y error.

```text
ui.FormField(*children, label=None, help_text=None, error=None, required=False, for_=None, horizontal=False)
```

```python
ui.FormField(ui.Input(""), label="Nombre", help_text="Como en tu DNI", required=True)
```

### `ui.HiddenInput`

Alias en minúsculas: `ui.hidden_input`

Campo oculto.

```text
ui.HiddenInput(value="", name=None)
```

```python
ui.HiddenInput("abc123", name="token")
```

### `ui.Input`

Alias en minúsculas: `ui.input`

Campo de texto con etiqueta, ayuda, error e iconos.

```text
ui.Input(value="", name=None, placeholder=None, size=size.md, icon=None, trailing=None, label=None, help_text=None, error=None, required=False, disabled=False, readonly=False, invalid=None, live=False, debounce=220, horizontal=False, autofocus=False, autocomplete=None, width=None)
```

```python
ui.Input("", label="Nombre", placeholder="Ana Ruiz", icon=ui.icons.user, required=True)
```

### `ui.MonthInput`

Alias en minúsculas: `ui.month_input`

Selector de mes.

```text
ui.MonthInput(value="")
```

```python
ui.MonthInput("2026-01", label="Mes")
```

### `ui.MultiSelect`

Alias en minúsculas: `ui.multi_select`

Selección múltiple.

```text
ui.MultiSelect(options=None, values=None)
```

```python
ui.MultiSelect([("a", "A"), ("b", "B"), ("c", "C")], values=["a"], label="Opciones")
```

### `ui.NumberInput`

Alias en minúsculas: `ui.number_input`

Campo numérico con `min`, `max`, `step`.

```text
ui.NumberInput(value="", min=None, max=None, step=None)
```

```python
ui.NumberInput(3, label="Cantidad", min=0, max=99)
```

### `ui.OtpInput`

Alias en minúsculas: `ui.otp_input`

Código de un solo uso.

```text
ui.OtpInput(length=6, value="", label=None, on_change=None, size=size.md)
```

```python
ui.OtpInput(6, label="Código de verificación")
```

### `ui.PasswordInput`

Alias en minúsculas: `ui.password_input`

Contraseña con botón para mostrarla.

```text
ui.PasswordInput(*children)
```

```python
ui.PasswordInput("", label="Contraseña")
```

### `ui.Radio`

Alias en minúsculas: `ui.radio`

Opción de radio individual.

```text
ui.Radio(label=None, checked=False, value="on", name="radio", disabled=False, help_text=None)
```

```python
ui.Radio("Tarjeta", value="card", name="pago", checked=True)
```

### `ui.RadioGroup`

Alias en minúsculas: `ui.radio_group`

Grupo de radios, en lista o tarjetas.

```text
ui.RadioGroup(items=None, value="", name="radio", label=None, help_text=None, cards=False, columns=1, on_change=None)
```

```python
ui.RadioGroup(["Tarjeta", "Bizum"], value="Bizum", label="Pago")
```

### `ui.RangeSlider`

Alias en minúsculas: `ui.range_slider`

Rango con dos deslizadores.

```text
ui.RangeSlider(low=20, high=80, min=0, max=100, step=1, label=None, on_change=None)
```

```python
ui.RangeSlider(20, 80, label="Precio")
```

### `ui.Rating`

Alias en minúsculas: `ui.rating`

Valoración por estrellas.

```text
ui.Rating(value=0, max_stars=5, label=None, on_change=None, read_only=False, size=6)
```

```python
ui.Rating(4, label="Valoración", on_change=lambda e: None)
```

### `ui.SearchInput`

Alias en minúsculas: `ui.search_input`

Buscador con eventos en vivo.

```text
ui.SearchInput(*children)
```

```python
ui.SearchInput("", label="Buscar", live=True, on_input=lambda e: None)
```

### `ui.SegmentedControl`

Alias en minúsculas: `ui.segmented_control`

Selector de segmentos.

```text
ui.SegmentedControl(items=None, value="", on_change=None, label=None, full_width=False)
```

```python
ui.SegmentedControl([("d", "Día"), ("s", "Semana")], value="s", label="Vista")
```

### `ui.Select`

Alias en minúsculas: `ui.select`

Lista desplegable.

```text
ui.Select(options=None, value="", name=None, placeholder=None, size=size.md, label=None, help_text=None, error=None, required=False, disabled=False, multiple=False, width=None, icon=None)
```

```python
ui.Select([("es", "Español"), ("en", "English")], label="Idioma", value="es")
```

### `ui.Slider`

Alias en minúsculas: `ui.slider`

Deslizador numérico.

```text
ui.Slider(value=50, min=0, max=100, step=1, label=None, show_value=True, unit="", live=False, on_change=None)
```

```python
ui.Slider(64, label="Volumen", unit=" %")
```

### `ui.Stepper`

Alias en minúsculas: `ui.stepper`

Contador con botones − / +.

```text
ui.Stepper(value=0, min=None, max=None, step=1, label=None, on_click=None)
```

```python
ui.Stepper(2, label="Pasajeros", min=0, max=9)
```

### `ui.Switch`

Alias en minúsculas: `ui.switch`

Interruptor de encendido/apagado.

```text
ui.Switch(label=None, checked=False, name=None, disabled=False, size=size.md, help_text=None)
```

```python
ui.Switch("Recordarme", checked=True, help_text="En este equipo")
```

### `ui.TagInput`

Alias en minúsculas: `ui.tag_input`

Etiquetas con alta y baja.

```text
ui.TagInput(tags=None, label=None, placeholder="Añadir y pulsar Enter", on_add=None, on_remove=None)
```

```python
ui.TagInput(["python", "tailwind"], label="Etiquetas")
```

### `ui.TextInput`

Alias en minúsculas: `ui.text_input`

Alias de `Input` para texto.

```text
ui.TextInput(value="", name=None, placeholder=None, size=size.md, icon=None, trailing=None, label=None, help_text=None, error=None, required=False, disabled=False, readonly=False, invalid=None, live=False, debounce=220, horizontal=False, autofocus=False, autocomplete=None, width=None)
```

```python
ui.TextInput("valor inicial", label="Texto")
```

### `ui.Textarea`

Alias en minúsculas: `ui.textarea`

Área de texto multilínea.

```text
ui.Textarea(value="", rows=4, name=None, placeholder=None, label=None, help_text=None, error=None, required=False, disabled=False, resize="y", invalid=None, live=False, width=None)
```

```python
ui.Textarea("", label="Notas", rows=4, placeholder="Escribe aquí…")
```

### `ui.TimeInput`

Alias en minúsculas: `ui.time_input`

Selector de hora.

```text
ui.TimeInput(value="")
```

```python
ui.TimeInput("09:30", label="Hora")
```

### `ui.ToggleGroup`

Alias en minúsculas: `ui.toggle_group`

Botones de alternancia.

```text
ui.ToggleGroup(items=None, values=None, on_change=None)
```

```python
ui.ToggleGroup([("b", "Negrita"), ("i", "Cursiva")], values=["b"])
```

### `ui.ValidationSummary`

Alias en minúsculas: `ui.validation_summary`

Resumen de errores de validación.

```text
ui.ValidationSummary(errors=None, title="Revisa los siguientes campos")
```

```python
ui.ValidationSummary(["El nombre es obligatorio", "Correo inválido"])
```

### `ui.WeekInput`

Alias en minúsculas: `ui.week_input`

Selector de semana.

```text
ui.WeekInput(value="")
```

```python
ui.WeekInput("2026-W05", label="Semana")
```


## Datos y tablas

### `ui.DataTable`

Alias en minúsculas: `ui.data_table`

Tabla con orden, búsqueda, selección y paginación.

```text
ui.DataTable(columns=None, rows=None, sort=None, direction="asc", page=1, page_size=10, selectable=False, selected=None, search="", searchable=False, search_placeholder="Buscar…", empty="No hay resultados", on_sort=None, on_page=None, on_select=None, on_search=None, total=None)
```

```python
ui.DataTable(columns=[{"key": "nombre", "label": "Nombre", "sortable": True}], rows=[{"id": 1, "nombre": "Ana"}], total=1, page=1, searchable=True)
```

### `ui.DescriptionItem`

Alias en minúsculas: `ui.description_item`

Término y definición.

```text
ui.DescriptionItem(term, definition)
```

```python
ui.DescriptionItem("Licencia", "MIT")
```

### `ui.DescriptionList`

Alias en minúsculas: `ui.description_list`

Lista de definiciones.

```text
ui.DescriptionList(*children)
```

```python
ui.DescriptionList(ui.DescriptionItem("Versión", "0.1.0"))
```

### `ui.EmptyState`

Alias en minúsculas: `ui.empty_state`

Estado vacío con acción.

```text
ui.EmptyState(*children, icon=icons.inbox, title="Nada por aquí", description=None)
```

```python
ui.EmptyState(title="Sin proyectos", description="Crea el primero para empezar.", icon=ui.icons.inbox)
```

### `ui.JsonView`

Alias en minúsculas: `ui.json_view`

Visualizador de JSON.

```text
ui.JsonView(data=None, max_h="96")
```

```python
ui.JsonView({"id": 42, "tags": ["a", "b"], "activo": True})
```

### `ui.KeyValueGrid`

Alias en minúsculas: `ui.key_value_grid`

Pares clave/valor.

```text
ui.KeyValueGrid(items=None, columns=2)
```

```python
ui.KeyValueGrid({"Nombre": "interui", "Versión": "0.1.0"})
```

### `ui.ListGroup`

Alias en minúsculas: `ui.list_group`

Lista agrupada.

```text
ui.ListGroup(*children, divided=True)
```

```python
ui.ListGroup(ui.ListItem(title="Reunión", subtitle="10:00", icon=ui.icons.users, meta="3"))
```

### `ui.ListItem`

Alias en minúsculas: `ui.list_item`

Elemento de lista con icono y meta.

```text
ui.ListItem(*children, title=None, subtitle=None, icon=None, meta=None, active=False)
```

```python
ui.ListItem(title="Informe", subtitle="Ayer", icon=ui.icons.file, meta="PDF")
```

### `ui.LogView`

Alias en minúsculas: `ui.log_view`

Visor de registros con niveles.

```text
ui.LogView(lines=None, max_h="80", title=None)
```

```python
ui.LogView([{"level": "info", "time": "09:12", "message": "inicio"}], title="app.log")
```

### `ui.Stat`

Alias en minúsculas: `ui.stat`

Indicador con valor y variación.

```text
ui.Stat(label, value, delta=None, positive=True, icon=None, hint=None)
```

```python
ui.Stat("Ingresos", "24.980 €", delta="+12 %", icon=ui.icons.chart)
```

### `ui.StatGrid`

Alias en minúsculas: `ui.stat_grid`

Rejilla de indicadores.

```text
ui.StatGrid(*children, columns=4)
```

```python
ui.StatGrid(ui.Stat("A", "1"), ui.Stat("B", "2"), columns=2)
```

### `ui.Table`

Alias en minúsculas: `ui.table`

Tabla estática.

```text
ui.Table(headers=None, rows=None, caption=None, striped=False, zebra=None, hover=True, hover_bg=None, compact=False, cell_pad=None, header_pad=None, bordered=False, footer=None, align=None, empty="Sin datos", header_bg=None, header_color=None, cell_colors=None, column_bg=None, selected=None, selected_bg=None, on_row_click=None, on_row_dblclick=None, on_row_context=None, context_menu=None, context_width="12rem", surface=True)
```

```python
ui.Table(headers=["Nombre", "Rol"], rows=[["Ana", "Admin"], ["Luis", "Editor"]], striped=True)
```

### `ui.Timeline`

Alias en minúsculas: `ui.timeline`

Línea de tiempo.

```text
ui.Timeline(*children)
```

```python
ui.Timeline(ui.TimelineItem("Pedido creado", time="09:12", icon=ui.icons.check))
```

### `ui.TimelineItem`

Alias en minúsculas: `ui.timeline_item`

Hito de la línea de tiempo.

```text
ui.TimelineItem(title, description=None, time=None, icon=None, tone=tone.primary, last=False)
```

```python
ui.TimelineItem("Pago confirmado", time="09:15", tone=ui.tone.success, last=True)
```

### `ui.Tree`

Alias en minúsculas: `ui.tree`

Árbol jerárquico.

```text
ui.Tree(*children)
```

```python
ui.Tree(ui.TreeNode("src", icon=ui.icons.folder, expanded=True, children=[ui.TreeNode("app.py", icon=ui.icons.file)]))
```

### `ui.TreeNode`

Alias en minúsculas: `ui.tree_node`

Nodo de árbol plegable.

```text
ui.TreeNode(label, icon=None, children=None, expanded=False, on_toggle=None, on_click=None, level=0)
```

```python
ui.TreeNode("src", icon=ui.icons.folder, expanded=True)
```


## Retroalimentación

### `ui.Alert`

Alias en minúsculas: `ui.alert`

Aviso con nivel y cierre.

```text
ui.Alert(*children, title=None, level="info", icon=None, dismissible=False, bordered=True)
```

```python
ui.Alert("Todo correcto.", level="success", title="Listo", dismissible=True)
```

### `ui.Banner`

Alias en minúsculas: `ui.banner`

Franja de aviso a todo el ancho.

```text
ui.Banner(*children, level="info", icon=None)
```

```python
ui.Banner("Mantenimiento programado", level="warning")
```

### `ui.Callout`

Alias en minúsculas: `ui.callout`

Alias de `Alert`.

```text
ui.Callout(*children, title=None, level="info", icon=None, dismissible=False, bordered=True)
```

```python
ui.Callout("Revisa la configuración.", level="warning")
```

### `ui.ConfirmDialog`

Alias en minúsculas: `ui.confirm_dialog`

Diálogo de confirmación gestionado en Python.

```text
ui.ConfirmDialog(*children, title="¿Estás seguro?", confirm_label="Confirmar", cancel_label="Cancelar", on_confirm=None, on_cancel=None, level="danger", open=False)
```

```python
ui.ConfirmDialog("Esta acción no se puede deshacer.", title="¿Eliminar?", dialog_id="confirmar")
```

### `ui.Hint`

Alias en minúsculas: `ui.hint`

Texto de ayuda pequeño.

```text
ui.Hint(*children)
```

```python
ui.Hint("Se guarda automáticamente")
```

### `ui.InlineToast`

Alias en minúsculas: `ui.inline_toast`

Aviso compacto en línea.

```text
ui.InlineToast(*children, title=None, level="info")
```

```python
ui.InlineToast("Guardado correctamente", level="success")
```

### `ui.LoadingOverlay`

Alias en minúsculas: `ui.loading_overlay`

Superpone un cargando sobre su contenido.

```text
ui.LoadingOverlay(*children, message="Cargando…")
```

```python
ui.LoadingOverlay(ui.Text("contenido"), message="Cargando…")
```

### `ui.Meter`

Alias en minúsculas: `ui.meter`

Medidor con color según el valor.

```text
ui.Meter(value=0, max_value=100, label=None)
```

```python
ui.Meter(82, label="Memoria")
```

### `ui.Progress`

Alias en minúsculas: `ui.progress`

Barra de progreso determinada o indeterminada.

```text
ui.Progress(value=0, max_value=100, label=None, show_value=False, tone=tone.primary, size=size.md, striped=False, indeterminate=False)
```

```python
ui.Progress(72, label="Subiendo", show_value=True)
```

### `ui.ProgressRing`

Alias en minúsculas: `ui.progress_ring`

Anillo de progreso.

```text
ui.ProgressRing(value=0, max_value=100, size=96, thickness=8, label=None, tone=tone.primary)
```

```python
ui.ProgressRing(72, label="72 %")
```

### `ui.Skeleton`

Alias en minúsculas: `ui.skeleton`

Marcador de carga.

```text
ui.Skeleton(width="full", height="4", circle=False, lines=1)
```

```python
ui.Skeleton(lines=3, height="3")
```

### `ui.Snackbar`

Alias en minúsculas: `ui.snackbar`

Aviso flotante con icono o imagen, acción y cierre opcional.

```text
ui.Snackbar(message="", title=None, icon=None, image=None, variant=variant.info, action=None, dismissible=True, position="bottom_right", duration=0)
```

```python
ui.Snackbar("Proyecto archivado", title="Hecho", icon=ui.icons.check, action=("Deshacer", lambda e: None), variant=ui.variant.success)
```

### `ui.StatusDot`

Alias en minúsculas: `ui.status_dot`

Punto de estado.

```text
ui.StatusDot(label=None, tone=tone.success, pulse=False)
```

```python
ui.StatusDot("Operativo", tone=ui.tone.success, pulse=True)
```


## Contenedores y superposiciones

### `ui.Accordion`

Alias en minúsculas: `ui.accordion`

Lista de secciones plegables.

```text
ui.Accordion(items=None, default_open=0)
```

```python
ui.Accordion([("Uno", ui.Text("contenido 1")), ("Dos", ui.Text("contenido 2"))])
```

### `ui.Card`

Alias en minúsculas: `ui.card`

Tarjeta con cabecera, cuerpo y pie.

```text
ui.Card(*children, title=None, description=None, footer=None, icon=None, actions=None, padding=True, hover=False, radius="md", elevated=True, header_bg=None, header_color=None, header_border=None, header_pad=None, header_font=None, footer_bg=None)
```

```python
ui.Card(title="Tarjeta", description="Con cabecera", icon=ui.icons.layers)(ui.Text("cuerpo"))
```

### `ui.Collapse`

Alias en minúsculas: `ui.collapse`

Sección plegable en el cliente.

```text
ui.Collapse(*children, title="Detalles", open=False)
```

```python
ui.Collapse(ui.Text("contenido oculto"), title="Más información")
```

### `ui.Drawer`

Alias en minúsculas: `ui.drawer`

Panel lateral deslizante.

```text
ui.Drawer(*children, drawer_id="drawer", side="right", title=None, size=size.md, open=False)
```

```python
ui.Drawer(ui.Text("Panel lateral"), drawer_id="detalle", title="Detalle")
```

### `ui.Dropdown`

Alias en minúsculas: `ui.dropdown`

Botón con menú desplegable.

```text
ui.Dropdown(*children, label="Opciones", icon=None, variant=variant.outline, align="left")
```

```python
ui.Dropdown(ui.MenuItem("Editar", icon=ui.icons.edit), ui.MenuItem("Borrar", danger=True), label="Acciones")
```

### `ui.Footer`

Alias en minúsculas: `ui.footer`

Pie de página.

```text
ui.Footer(*children)
```

```python
ui.Footer(ui.Text("© 2026 interui"))
```

### `ui.Hero`

Alias en minúsculas: `ui.hero`

Bloque destacado con degradado.

```text
ui.Hero(*children, eyebrow=None)
```

```python
ui.Hero(ui.Title("Bienvenido"), eyebrow="Novedad")
```

### `ui.Menu`

Alias en minúsculas: `ui.menu`

Contenedor de menú.

```text
ui.Menu(*children)
```

```python
ui.Menu(ui.MenuItem("Inicio", icon=ui.icons.home), ui.MenuItem("Ajustes", icon=ui.icons.settings))
```

### `ui.MenuItem`

Alias en minúsculas: `ui.menu_item`

Entrada de menú.

```text
ui.MenuItem(label="", icon=None, shortcut=None, danger=False, disabled=False, href=None, on_click=None)
```

```python
ui.MenuItem("Duplicar", icon=ui.icons.copy, shortcut="⌘D")
```

### `ui.Modal`

Alias en minúsculas: `ui.modal`

Diálogo modal; `.trigger()` crea el botón que lo abre.

```text
ui.Modal(*children, dialog_id="modal", title=None, description=None, footer=None, size=size.md, open=False, closable=True)
```

```python
ui.Modal(ui.Text("Contenido del modal"), dialog_id="alta", title="Nueva ficha")
```

### `ui.PageHeader`

Alias en minúsculas: `ui.page_header`

Cabecera de página con migas y acciones.

```text
ui.PageHeader(title, subtitle=None, actions=None, breadcrumb=None)
```

```python
ui.PageHeader("Proyectos", subtitle="12 activos", actions=ui.Button("Nuevo", icon=ui.icons.plus))
```

### `ui.Panel`

Alias en minúsculas: `ui.panel`

Superficie con padding.

```text
ui.Panel(*children, tone=tone.muted, padding=4)
```

```python
ui.Panel(ui.Text("contenido"), tone=ui.tone.muted)
```

### `ui.Paper`

Alias en minúsculas: `ui.paper`

Hoja con sombra.

```text
ui.Paper(*children)
```

```python
ui.Paper(ui.Text("hoja con sombra"))
```

### `ui.Popover`

Alias en minúsculas: `ui.popover`

Panel emergente anclado.

```text
ui.Popover(*children, trigger="Abrir", title=None)
```

```python
ui.Popover(ui.Text("detalle"), trigger="Ver más", title="Información")
```

### `ui.Section`

Alias en minúsculas: `ui.section`

Sección con título y acciones.

```text
ui.Section(*children, title=None, subtitle=None, actions=None)
```

```python
ui.Section(ui.Text("contenido"), title="Sección", subtitle="Con subtítulo")
```

### `ui.Sheet`

Alias en minúsculas: `ui.sheet`

Hoja inferior.

```text
ui.Sheet(*children, sheet_id="sheet", title=None, open=False)
```

```python
ui.Sheet(ui.Text("Hoja inferior"), sheet_id="hoja", title="Opciones")
```

### `ui.Splitter`

Alias en minúsculas: `ui.splitter`

Dos paneles redimensionables.

```text
ui.Splitter(first, second, direction="horizontal", initial="50%")
```

```python
ui.Splitter(ui.Text("izquierda"), ui.Text("derecha"))
```

### `ui.StatusBar`

Alias en minúsculas: `ui.status_bar`

Barra inferior de estado.

```text
ui.StatusBar(*children)
```

```python
ui.StatusBar(ui.Text("Listo"), ui.Badge("local", variant=ui.variant.success))
```

### `ui.TitleBar`

Alias en minúsculas: `ui.title_bar`

Barra de título propia para ventanas sin marco.

```text
ui.TitleBar(title=None, *children, icon=None, controls=True)
```

```python
ui.TitleBar("Mi app", icon=ui.icons.layers)
```

### `ui.Toolbar`

Alias en minúsculas: `ui.toolbar`

Barra de herramientas.

```text
ui.Toolbar(*children, sticky=False)
```

```python
ui.Toolbar(ui.Button("Nuevo", size=ui.size.sm), ui.Button("Filtrar", variant=ui.variant.outline, size=ui.size.sm))
```

### `ui.Tooltip`

Alias en minúsculas: `ui.tooltip`

Ayuda emergente al pasar el ratón.

```text
ui.Tooltip(*children, content="", placement="top")
```

```python
ui.Tooltip(ui.Button("?", variant=ui.variant.outline), content="Ayuda contextual")
```

### `ui.Well`

Alias en minúsculas: `ui.well`

Caja hundida para contenido secundario.

```text
ui.Well(*children)
```

```python
ui.Well(ui.Text("bloque hundido"))
```


## Shell de aplicación, menús y barras

### `ui.AppShell`

Alias en minúsculas: `ui.app_shell`

Armazón completo: barra de título, cabecera/menús, barra lateral, contenido con scroll y barra de estado.

```text
ui.AppShell(*children, title_bar=None, header=None, sidebar=None, status=None, footer=None, sidebar_position=side.left, sidebar_width="w-64", menu_label="Menú", collapsible=True)
```

```python
ui.AppShell(ui.Container(pad=ui.pad.py_6)(ui.Text("contenido")), title_bar=ui.TitleBar("Mi app", icon=ui.icons.layers), header=ui.MenuBar({"Archivo": [ui.ContextItem("Salir", icon=ui.icons.power)]}, brand="Mi app"), sidebar=ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True)), status=ui.StatusBar(ui.Text("Listo")))
```

### `ui.CommandBar`

Alias en minúsculas: `ui.command_bar`

Barra de comandos: buscador en vivo + acciones a la derecha.

```text
ui.CommandBar(*children, search="", search_placeholder="Buscar…", on_search=None)
```

```python
ui.CommandBar(ui.Button("Nuevo", icon=ui.icons.plus, variant=ui.variant.primary), search_placeholder="Buscar…")
```

### `ui.ContextItem`

Alias en minúsculas: `ui.context_item`

Entrada de menú contextual (icono, atajo, peligro, deshabilitada).

```text
ui.ContextItem(label="", icon=None, shortcut=None, danger=False, disabled=False, href=None, on_click=None)
```

```python
ui.ContextItem("Abrir", icon=ui.icons.folder, shortcut="Ctrl+O", on_click=lambda: None)
```

### `ui.ContextMenu`

Alias en minúsculas: `ui.context_menu`

Envuelve contenido y abre un menú con el botón derecho.

```text
ui.ContextMenu(*children, min_width="12rem", hint=None)
```

```python
ui.ContextMenu(ui.ContextItem("Abrir", icon=ui.icons.folder), "-", ui.ContextItem("Borrar", icon=ui.icons.trash, danger=True))(ui.Text("Clic derecho aquí"))
```

### `ui.MenuBar`

Alias en minúsculas: `ui.menu_bar`

Barra de menús de la ventana (`Archivo`, `Editar`…) con desplegables.

```text
ui.MenuBar(menus=None, brand=None, logo="layers", icons=None, actions=None, sticky=True)
```

```python
ui.MenuBar({"Archivo": [ui.ContextItem("Nuevo", icon=ui.icons.plus, shortcut="Ctrl+N"), "-", ui.ContextItem("Salir", icon=ui.icons.power, danger=True)], "Ver": [ui.ContextItem("Tema oscuro", icon=ui.icons.moon)]}, brand="Mi app")
```

### `ui.MenuButton`

Alias en minúsculas: `ui.menu_button`

Botón que despliega un menú de acciones en cualquier punto de la interfaz.

```text
ui.MenuButton(label="Menú", items=None, icon=None, variant=variant.ghost, size=size.sm, align="left")
```

```python
ui.MenuButton("Acciones", icon=ui.icons.settings, items=[ui.ContextItem("Editar", icon=ui.icons.edit), ui.ContextItem("Eliminar", icon=ui.icons.trash, danger=True)])
```

### `ui.NotificationButton`

Alias en minúsculas: `ui.notification_button`

Campana con contador y panel de notificaciones.

```text
ui.NotificationButton(count=0, items=None)
```

```python
ui.NotificationButton(3, items=[ui.ContextItem("Nueva tarea asignada", icon=ui.icons.check)])
```


## Navegación

### `ui.Breadcrumb`

Alias en minúsculas: `ui.breadcrumb`

Migas de pan.

```text
ui.Breadcrumb(items=None, separator="chevron")
```

```python
ui.Breadcrumb([("/", "Inicio"), ("/proyectos", "Proyectos"), ("x", "interui")])
```

### `ui.CommandItem`

Alias en minúsculas: `ui.command_item`

Acción de la paleta.

```text
ui.CommandItem(label="", hint=None, icon=icons.search, on_click=None)
```

```python
ui.CommandItem("Nuevo proyecto", hint="N", icon=ui.icons.plus)
```

### `ui.CommandPalette`

Alias en minúsculas: `ui.command_palette`

Paleta de comandos con filtrado instantáneo.

```text
ui.CommandPalette(*children, placeholder="Buscar acciones…")
```

```python
ui.CommandPalette(ui.CommandItem("Ir al inicio", hint="G H", icon=ui.icons.home))
```

### `ui.NavLink`

Alias en minúsculas: `ui.nav_link`

Enlace de navegación con estado activo.

```text
ui.NavLink(label="", href="#", icon=None, active=False, badge=None, on_click=None)
```

```python
ui.NavLink("Equipo", href="/equipo", icon=ui.icons.users)
```

### `ui.Navbar`

Alias en minúsculas: `ui.navbar`

Barra superior de navegación.

```text
ui.Navbar(*children, brand=None, logo="layers", sticky=True)
```

```python
ui.Navbar(ui.NavLink("Inicio", href="/", active=True), brand="Mi app")
```

### `ui.Pagination`

Alias en minúsculas: `ui.pagination`

Paginación con eventos a Python.

```text
ui.Pagination(page=1, pages=1, on_page=None, window=5)
```

```python
ui.Pagination(3, pages=12, on_page=lambda e: None)
```

### `ui.Sidebar`

Alias en minúsculas: `ui.sidebar`

Barra lateral.

```text
ui.Sidebar(*children, title=None, width="w-64")
```

```python
ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True), title="Navegación")
```

### `ui.SidebarItem`

Alias en minúsculas: `ui.sidebar_item`

Elemento de barra lateral.

```text
ui.SidebarItem(label="", icon=None, active=False, badge=None, on_click=None, children=None)
```

```python
ui.SidebarItem("Informes", icon=ui.icons.chart, badge=2)
```

### `ui.Steps`

Alias en minúsculas: `ui.steps`

Pasos de un asistente.

```text
ui.Steps(items=None, current=0, on_step=None)
```

```python
ui.Steps(["Cuenta", "Perfil", "Pago"], current=1)
```

### `ui.TabBar`

Alias en minúsculas: `ui.tab_bar`

Alias de `Tabs`.

```text
ui.TabBar(tabs=None, active=None, on_change=None, variant=variant.line, size=size.md)
```

```python
ui.Tabs([("a", "Uno", ui.Text("A"))], active="a", variant=ui.variant.pills)
```

### `ui.Tabs`

Alias en minúsculas: `ui.tabs`

Pestañas; cambian en el cliente o en Python.

```text
ui.Tabs(tabs=None, active=None, on_change=None, variant=variant.line, size=size.md)
```

```python
ui.Tabs([("a", "Uno", ui.Text("panel A")), ("b", "Dos", ui.Text("panel B"))], active="a")
```


## Gráficos

### `ui.AreaChart`

Alias en minúsculas: `ui.area_chart`

Área con relleno.

```text
ui.AreaChart(series=None)
```

```python
ui.AreaChart({"2025": [8, 14, 18, 16, 25]}, labels=["Ene", "Feb", "Mar", "Abr", "May"])
```

### `ui.BarChart`

Alias en minúsculas: `ui.bar_chart`

Barras verticales.

```text
ui.BarChart(series=None, horizontal=False, radius=4)
```

```python
ui.BarChart([[18, 26, 12, 30]], labels=["L", "M", "X", "J"], show_values=True)
```

### `ui.ChartCard`

Alias en minúsculas: `ui.chart_card`

Tarjeta con gráfico.

```text
ui.ChartCard(chart, title=None, subtitle=None)
```

```python
ui.ChartCard(ui.Sparkline([1, 3, 2, 5]), title="Tendencia", subtitle="Últimos 7 días")
```

### `ui.ColumnChart`

Alias en minúsculas: `ui.column_chart`

Alias de `BarChart`.

```text
ui.ColumnChart(series=None, horizontal=False, radius=4)
```

```python
ui.ColumnChart([[5, 9, 3]], labels=["a", "b", "c"])
```

### `ui.DonutChart`

Alias en minúsculas: `ui.donut_chart`

Anillo con total.

```text
ui.DonutChart(data=None)
```

```python
ui.DonutChart({"A": 60, "B": 40})
```

### `ui.Gauge`

Alias en minúsculas: `ui.gauge`

Arco de progreso.

```text
ui.Gauge(value=0, max_value=100, label=None, color="#4f46e5", size=180)
```

```python
ui.Gauge(64, label="CPU")
```

### `ui.Legend`

Alias en minúsculas: `ui.legend`

Leyenda de series.

```text
ui.Legend(items=None)
```

```python
ui.Legend(["Ventas", "Costes"])
```

### `ui.LineChart`

Alias en minúsculas: `ui.line_chart`

Gráfico de líneas.

```text
ui.LineChart(series=None, smooth=False, fill=False)
```

```python
ui.LineChart([[3, 6, 4, 9, 7]], labels=["L", "M", "X", "J", "V"])
```

### `ui.PieChart`

Alias en minúsculas: `ui.pie_chart`

Gráfico circular.

```text
ui.PieChart(data=None, donut=False, thickness=0.55)
```

```python
ui.PieChart({"Directo": 42, "Social": 28, "Búsqueda": 30})
```

### `ui.ScatterChart`

Alias en minúsculas: `ui.scatter_chart`

Dispersión de puntos.

```text
ui.ScatterChart(series=None, labels=None, height=260, show_grid=True, show_legend=True, show_values=False, colors=None)
```

```python
ui.ScatterChart([[3, 7, 2, 9]])
```

### `ui.Sparkline`

Alias en minúsculas: `ui.sparkline`

Mini gráfico de tendencia.

```text
ui.Sparkline(data=None, color="#4f46e5", height=32, width=120, fill=True)
```

```python
ui.Sparkline([4, 8, 6, 12, 9, 14])
```


## Medios

### `ui.Audio`

Alias en minúsculas: `ui.audio`

Reproductor de audio.

```text
ui.Audio(src="", controls=True)
```

```python
ui.Audio("https://ejemplo.com/audio.mp3")
```

### `ui.Avatar`

Alias en minúsculas: `ui.avatar`

Avatar con iniciales o foto.

```text
ui.Avatar(src=None, name="", initials=None, size=size.md, status=None, ring=True)
```

```python
ui.Avatar(name="Ana Ruiz", size=ui.size.lg, status="online")
```

### `ui.AvatarGroup`

Alias en minúsculas: `ui.avatar_group`

Avatares apilados.

```text
ui.AvatarGroup(*children, max_items=4)
```

```python
ui.AvatarGroup(ui.Avatar(name="Ana Ruiz"), ui.Avatar(name="Luis Paz"), max_items=2)
```

### `ui.Carousel`

Alias en minúsculas: `ui.carousel`

Carrusel controlado por Python.

```text
ui.Carousel(slides=None, index=0, on_change=None)
```

```python
ui.Carousel([ui.Text("diapositiva 1"), ui.Text("diapositiva 2")], index=0)
```

### `ui.Figure`

Alias en minúsculas: `ui.figure`

Imagen con pie de foto.

```text
ui.Figure(image, caption=None)
```

```python
ui.Figure(ui.Image("foto.png", alt="Foto"), caption="Figura 1")
```

### `ui.Gallery`

Alias en minúsculas: `ui.gallery`

Rejilla de imágenes.

```text
ui.Gallery(*children, columns=3, gap=3)
```

```python
ui.Gallery(ui.Image("a.png", alt="A"), ui.Image("b.png", alt="B"), columns=2)
```

### `ui.IconBadge`

Alias en minúsculas: `ui.icon_badge`

Icono en una caja de color.

```text
ui.IconBadge(icon=icons.check, tone=tone.primary, size=size.md)
```

```python
ui.IconBadge("zap", tone=ui.tone.primary)
```

### `ui.Image`

Alias en minúsculas: `ui.image`

Imagen con proporción y ajuste.

```text
ui.Image(src="", alt="", ratio=None, fit="cover", rounded="lg", width=None, height=None)
```

```python
ui.Image("https://picsum.photos/seed/a/600/400", alt="Paisaje", ratio="video")
```

### `ui.Video`

Alias en minúsculas: `ui.video`

Reproductor de vídeo.

```text
ui.Video(src="", poster=None, controls=True, autoplay=False, loop=False, muted=True, rounded="xl")
```

```python
ui.Video("https://ejemplo.com/video.mp4", poster="portada.jpg")
```


## Avanzados

### `ui.Canvas`

Alias en minúsculas: `ui.canvas`

Lienzo para dibujar con JS.

```text
ui.Canvas(width=400, height=200, script=None)
```

```python
ui.Canvas(width=400, height=200)
```

### `ui.CodeEditor`

Alias en minúsculas: `ui.code_editor`

Editor de código con numeración.

```text
ui.CodeEditor(value="", language=None, line_numbers=True, readonly=False, rows=14, max_h="none", placeholder=None, on_change=None)
```

```python
ui.CodeEditor("print(1)", language="python", max_h="64")
```

### `ui.Html`

Alias en minúsculas: `ui.html`

HTML literal (no escapa nada).

```text
ui.Html(markup="")
```

```python
ui.Html("<b>HTML literal</b>")
```

### `ui.Iframe`

Alias en minúsculas: `ui.iframe`

Contenido incrustado aislado.

```text
ui.Iframe(src=None, srcdoc=None, height="420", sandbox="allow-scripts allow-forms allow-popups")
```

```python
ui.Iframe(srcdoc="<h1>Hola</h1>", height="60")
```

### `ui.KeyValueEditor`

Alias en minúsculas: `ui.key_value_editor`

Editor de pares clave/valor.

```text
ui.KeyValueEditor(items=None, on_change=None, on_add=None, on_remove=None)
```

```python
ui.KeyValueEditor({"API_URL": "https://api.ejemplo.com"})
```

### `ui.Markdown`

Alias en minúsculas: `ui.markdown`

Subconjunto de Markdown.

```text
ui.Markdown(text="")
```

```python
ui.Markdown("# Título\n\n- uno\n- dos\n\n**negrita** y `código`")
```

### `ui.ProgressTable`

Alias en minúsculas: `ui.progress_table`

Tabla con barras de progreso.

```text
ui.ProgressTable(rows=None, max_value=100)
```

```python
ui.ProgressTable([{"label": "Diseño", "value": 100}, {"label": "Código", "value": 60}])
```

### `ui.RichTextEditor`

Alias en minúsculas: `ui.rich_text_editor`

Editor de texto enriquecido.

```text
ui.RichTextEditor(value="", on_change=None, min_h="40", toolbar=True)
```

```python
ui.RichTextEditor("<b>Texto</b> editable", min_h="32")
```

### `ui.Terminal`

Alias en minúsculas: `ui.terminal`

Vista de terminal.

```text
ui.Terminal(lines=None, prompt="$", title="terminal", max_h="72")
```

```python
ui.Terminal(["pip install interui", "python app.py"], title="zsh")
```


## Iconos

### `ui.Icon`

Alias en minúsculas: `ui.icon`

Icono SVG del set incluido (`ui.ICON_NAMES`).

```text
ui.Icon(name="check", size=5, stroke=None, class_=None)
```

```python
ui.Icon(ui.icons.check, size=6, color=ui.colors.emerald_600)
```

### `ui.IconGrid`

Alias en minúsculas: `ui.icon_grid`

Catálogo buscable de los 200+ iconos incluidos; `on_pick` recibe el nombre.

```text
ui.IconGrid(names=None, size=5, columns=8, searchable=False, on_pick=None)
```

```python
ui.IconGrid(columns=8)
```


## Etiquetas html

### `ui.A`

Alias en minúsculas: `ui.a`

Enlace `<a>` con estilo de enlace.

```text
ui.A(*children, href="#")
```

```python
ui.A("Enlace", href="/ruta")
```

### `ui.Article`

Alias en minúsculas: `ui.article`

Contenedor semántico `<article>`.

```text
ui.Article(*children)
```

```python
ui.Article("Contenido del artículo")
```

### `ui.Aside`

Alias en minúsculas: `ui.aside`

Contenido lateral `<aside>`.

```text
ui.Aside(*children)
```

```python
ui.Aside("Nota lateral")
```

### `ui.B`

Alias en minúsculas: `ui.b`

Negrita visual `<b>`.

```text
ui.B(*children)
```

```python
ui.B("negrita")
```

### `ui.Br`

Alias en minúsculas: `ui.br`

Salto de línea `<br>`.

```python
ui.Br()
```

### `ui.Details`

Alias en minúsculas: `ui.details`

Sección desplegable nativa `<details>`.

```text
ui.Details(*children, open=False)
```

```python
ui.Details(ui.Summary("Más detalles"), ui.Text("contenido"))
```

### `ui.DetailsBlock`

Alias en minúsculas: `ui.details_block`

Alias de `Details`.

```text
ui.DetailsBlock(*children, open=False)
```

```python
ui.DetailsBlock(ui.Summary("Detalles"), ui.Text("contenido"))
```

### `ui.Div`

Alias en minúsculas: `ui.div`

Caja genérica `<div>`.

```text
ui.Div(*children)
```

```python
ui.Div("contenido")
```

### `ui.Figcaption`

Alias en minúsculas: `ui.figcaption`

Pie de figura.

```text
ui.Figcaption(*children)
```

```python
ui.Figcaption("Pie de figura")
```

### `ui.Figure`

Alias en minúsculas: `ui.figure`

Figura genérica.

```text
ui.Figure(*children)
```

```python
ui.Figure(ui.Image("foto.png", alt="Foto"), caption="Figura 1")
```

### `ui.H1`

Alias en minúsculas: `ui.h1`

Encabezado `<h1>` con estilo.

```text
ui.H1(*children)
```

```python
ui.H1("Título 1")
```

### `ui.H2`

Alias en minúsculas: `ui.h2`

Encabezado `<h2>` con estilo.

```text
ui.H2(*children)
```

```python
ui.H2("Título 2")
```

### `ui.H3`

Alias en minúsculas: `ui.h3`

Encabezado `<h3>` con estilo.

```text
ui.H3(*children)
```

```python
ui.H3("Título 3")
```

### `ui.H4`

Alias en minúsculas: `ui.h4`

Encabezado `<h4>` con estilo.

```text
ui.H4(*children)
```

```python
ui.H4("Título 4")
```

### `ui.H5`

Alias en minúsculas: `ui.h5`

Encabezado `<h5>` con estilo.

```text
ui.H5(*children)
```

```python
ui.H5("Título 5")
```

### `ui.H6`

Alias en minúsculas: `ui.h6`

Encabezado `<h6>` con estilo.

```text
ui.H6(*children)
```

```python
ui.H6("Título 6")
```

### `ui.Header`

Alias en minúsculas: `ui.header`

Cabecera semántica.

```text
ui.Header(*children)
```

```python
ui.Header("cabecera")
```

### `ui.Hr`

Alias en minúsculas: `ui.hr`

Línea separadora `<hr>`.

```python
ui.Hr()
```

### `ui.I`

Alias en minúsculas: `ui.i`

Cursiva visual `<i>`.

```text
ui.I(*children)
```

```python
ui.I("cursiva")
```

### `ui.Img`

Alias en minúsculas: `ui.img`

Imagen `<img>` sin recorte.

```text
ui.Img(src="", alt="")
```

```python
ui.Img("foto.png", alt="Foto")
```

### `ui.Li`

Alias en minúsculas: `ui.li`

Elemento de lista `<li>`.

```text
ui.Li(*children)
```

```python
ui.Li("elemento")
```

### `ui.Main`

Alias en minúsculas: `ui.main`

Contenido principal (`flex-1`).

```text
ui.Main(*children)
```

```python
ui.Main("contenido principal")
```

### `ui.Nav`

Alias en minúsculas: `ui.nav`

Contenedor de navegación.

```text
ui.Nav(*children)
```

```python
ui.Nav("navegación")
```

### `ui.Ol`

Alias en minúsculas: `ui.ol`

Lista numerada `<ol>`.

```text
ui.Ol(*children)
```

```python
ui.Ol(ui.Li("primero"), ui.Li("segundo"))
```

### `ui.P`

Alias en minúsculas: `ui.p`

Párrafo `<p>`.

```text
ui.P(*children)
```

```python
ui.P("párrafo")
```

### `ui.Pre`

Alias en minúsculas: `ui.pre`

Texto preformateado.

```text
ui.Pre(*children)
```

```python
ui.Pre("texto preformateado")
```

### `ui.S`

Alias en minúsculas: `ui.s`

Texto tachado.

```text
ui.S(*children)
```

```python
ui.S("tachado")
```

### `ui.Section`

Alias en minúsculas: `ui.section`

Sección HTML (`ui.Section` es la versión con título).

```text
ui.Section(*children)
```

```python
ui.Section(ui.Text("contenido"), title="Sección", subtitle="Con subtítulo")
```

### `ui.Span`

Alias en minúsculas: `ui.span`

Texto en línea `<span>`.

```text
ui.Span(*children)
```

```python
ui.Span("texto en línea")
```

### `ui.Sub`

Alias en minúsculas: `ui.sub`

Subíndice.

```text
ui.Sub(*children)
```

```python
ui.Sub("sub")
```

### `ui.Summary`

Alias en minúsculas: `ui.summary`

Encabezado de un `Details`.

```text
ui.Summary(*children)
```

```python
ui.Summary("Resumen")
```

### `ui.Sup`

Alias en minúsculas: `ui.sup`

Superíndice.

```text
ui.Sup(*children)
```

```python
ui.Sup("sup")
```

### `ui.Template`

Alias en minúsculas: `ui.template`

Envoltura de composición sin semántica.

```text
ui.Template(*children)
```

```python
ui.Template("contenido")
```

### `ui.Time`

Alias en minúsculas: `ui.time`

Fecha/hora semántica.

```text
ui.Time(*children)
```

```python
ui.Time("2026-01-31", datetime="2026-01-31")
```

### `ui.U`

Alias en minúsculas: `ui.u`

Subrayado.

```text
ui.U(*children)
```

```python
ui.U("subrayado")
```

### `ui.Ul`

Alias en minúsculas: `ui.ul`

Lista con viñetas `<ul>`.

```text
ui.Ul(*children)
```

```python
ui.Ul(ui.Li("uno"), ui.Li("dos"))
```
