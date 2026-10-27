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

| Propiedad | Tipo | Efecto |
|---|---|---|
| `class_` | `str` | Clases Tailwind extra; sustituyen a las del control cuando chocan. |
| `id` | `str` | Identificador estable (por defecto se genera por posición). |
| `key` | `Any` | Sufijo estable del `id` dentro de listas. |
| `visible` / `when` | `bool` / `callable` | No renderiza el control. |
| `hidden` | `bool` | Renderiza oculto (`hidden`). |
| `style` | `str` / `dict` | Estilos en línea. |
| `data` | `dict` | Atributos `data-*` (comportamientos del cliente). |
| `aria` | `dict` | Atributos `aria-*`. |
| `on_*` | `callable` | Handler en Python (`on_click`, `on_change`, `on_input`, `on_submit`, `on_enter`, …). |

Los hijos se pasan como posicionales y se pueden añadir después con `(...)`:

```python
card = ui.Card(title="Hola")
card(ui.Text("mundo"))
```


## Ventana y estructura

### `ui.AspectRatio`

Mantiene una proporción fija.

```text
ui.AspectRatio(*children, ratio="video")
```

```python
ui.AspectRatio(ui.Center(ui.Text("16:9")), ratio="video")
```

### `ui.Center`

Centra el contenido en ambos ejes.

```text
ui.Center(*children)
```

```python
ui.Center(ui.Text("centrado"), class_="h-40")
```

### `ui.Col`

Columna responsive (`span`, `sm`, `md`, `lg`, `xl`, `xxl`).

```text
ui.Col(*children, span=12, sm=None, md=None, lg=None, xl=None, xxl=None, offset=None, order=None)
```

```python
ui.Row(ui.Col(span=12, md=6, lg=4)(ui.Text("12 → 6 → 4 columnas")))
```

### `ui.Container`

Centra el contenido y limita el ancho máximo.

```text
ui.Container(*children, size="xl", padded=True)
```

```python
ui.Container(size="prose")(ui.Text("ancho limitado y centrado"))
```

### `ui.Divider`

Separador con etiqueta opcional.

```text
ui.Divider(label=None, orientation="horizontal")
```

```python
ui.Divider("o")
```

### `ui.Grid`

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

Raíz de la ventana: ocupa todo el alto y define el fondo del tema.

```text
ui.Screen(*children)
```

```python
ui.Screen(ui.Text("contenido de la ventana"), class_="p-6")
```

### `ui.ScrollArea`

Área con scroll y altura máxima.

```text
ui.ScrollArea(*children, max_h="80", axis="y")
```

```python
ui.ScrollArea(ui.Text("mucho contenido"), max_h="48")
```

### `ui.Spacer`

Empuja el contenido en un flexbox.

```python
ui.Stack(ui.Text("izq"), ui.Spacer(), ui.Text("der"), direction="row")
```

### `ui.Stack`

Apila hijos en vertical u horizontal con separación uniforme.

```text
ui.Stack(*children, direction="col", gap=4, align="stretch", justify="start", wrap=False)
```

```python
ui.Stack(ui.Text("uno"), ui.Text("dos"), direction="row", gap=3)
```


## Tipografía y texto

### `ui.Announcement`

Franja de anuncio a todo el ancho.

```text
ui.Announcement(*children, variant="primary")
```

```python
ui.Announcement("Nueva versión disponible")
```

### `ui.Badge`

Etiqueta compacta con variantes de color.

```text
ui.Badge(label="", variant="neutral", size="md", dot=False, icon=None, pill=True)
```

```python
ui.Badge("nuevo", variant="success", dot=True)
```

### `ui.Blockquote`

Cita con autor opcional.

```text
ui.Blockquote(*children, cite=None)
```

```python
ui.Blockquote("La simplicidad es la máxima sofisticación.", cite="Leonardo")
```

### `ui.Chip`

Etiqueta con botón de borrado.

```text
ui.Chip(label="", on_remove=None, variant="neutral")
```

```python
ui.Chip("python", variant="primary")
```

### `ui.Code`

Código en línea.

```text
ui.Code(*children)
```

```python
ui.Code("pip install interui")
```

### `ui.CodeBlock`

Bloque de código con botón de copiar.

```text
ui.CodeBlock(code="", language=None, filename=None, max_h="none")
```

```python
ui.CodeBlock("print('hola')", language="python", filename="demo.py")
```

### `ui.Em`

Texto en cursiva semántica.

```text
ui.Em(*children)
```

```python
ui.Em("énfasis")
```

### `ui.Heading`

Encabezado `h1`–`h6`.

```text
ui.Heading(*children, level=2, tone="default")
```

```python
ui.Heading("Sección", level=2)
```

### `ui.Kbd`

Tecla de teclado.

```text
ui.Kbd(*children)
```

```python
ui.Stack(ui.Kbd("Ctrl"), ui.Kbd("K"), direction="row", gap=1)
```

### `ui.Label`

Etiqueta de campo.

```text
ui.Label(*children, required=False, for_=None)
```

```python
ui.Label("Correo electrónico", for_="campo", required=True)
```

### `ui.Lead`

Entradilla destacada.

```text
ui.Lead(*children)
```

```python
ui.Lead("Entradilla que resume el contenido.")
```

### `ui.Link`

Enlace interno o externo.

```text
ui.Link(*children, href="#", external=False)
```

```python
ui.Link("Documentación", href="https://tailwindcss.com")
```

### `ui.Mark`

Texto resaltado.

```text
ui.Mark(*children)
```

```python
ui.Mark("resaltado")
```

### `ui.Muted`

Texto secundario atenuado.

```text
ui.Muted(*children)
```

```python
ui.Muted("Texto secundario")
```

### `ui.Paragraph`

Párrafo con interlineado relajado.

```text
ui.Paragraph(*children, tone="default", size="base")
```

```python
ui.Paragraph("Un párrafo con interlineado relajado para leer cómodo.")
```

### `ui.Small`

Nota de tamaño reducido.

```text
ui.Small(*children)
```

```python
ui.Small("nota al pie")
```

### `ui.Strong`

Texto en negrita semántica.

```text
ui.Strong(*children)
```

```python
ui.Strong("importante")
```

### `ui.Text`

Texto con tamaño, tono y peso.

```text
ui.Text(*children, size="base", tone="default", weight=None, leading=None, truncate=False)
```

```python
ui.Text("Texto normal", size="lg", tone="muted", weight="medium")
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

Botón con variantes, tamaños, iconos y estado de carga.

```text
ui.Button(*children, label=None, variant="primary", size="md", icon=None, icon_right=None, loading=False, disabled=False, submit=False, full_width=False, href=None, pill=False)
```

```python
ui.Button("Guardar", icon="check", variant="primary", on_click=lambda: None)
```

### `ui.ButtonGroup`

Botones pegados horizontal o verticalmente.

```text
ui.ButtonGroup(*children, vertical=False)
```

```python
ui.ButtonGroup(ui.Button("Día", variant="outline"), ui.Button("Semana", variant="outline"))
```

### `ui.CopyButton`

Copia un texto al portapapeles sin ir al servidor.

```text
ui.CopyButton(text, label="Copiar", icon="copy")
```

```python
ui.CopyButton("texto que se copia")
```

### `ui.Fab`

Botón flotante de acción.

```text
ui.Fab(icon="plus", label=None)
```

```python
ui.Fab("plus", label="Nuevo")
```

### `ui.IconButton`

Botón cuadrado solo con icono.

```text
ui.IconButton(icon="more-h", label=None, variant="ghost", size="md", loading=False, disabled=False, href=None)
```

```python
ui.IconButton("settings", label="Ajustes", variant="outline")
```

### `ui.LinkButton`

Botón con apariencia de botón que navega a `href`.

```text
ui.LinkButton(*children, label=None, variant="primary", size="md", icon=None, icon_right=None, loading=False, disabled=False, submit=False, full_width=False, href=None, pill=False)
```

```python
ui.Button("Ir a ajustes", href="/ajustes", variant="outline")
```

### `ui.Spinner`

Indicador de carga animado.

```text
ui.Spinner(size=4, class_=None)
```

```python
ui.Spinner(size=5)
```


## Formularios

### `ui.Checkbox`

Casilla con etiqueta.

```text
ui.Checkbox(label=None, checked=False, value="on", name=None, disabled=False, help_text=None, indeterminate=False)
```

```python
ui.Checkbox("Acepto los términos", checked=True)
```

### `ui.CheckboxGroup`

Grupo de casillas.

```text
ui.CheckboxGroup(items=None, values=None, name=None, label=None, help_text=None, columns=1, on_change=None)
```

```python
ui.CheckboxGroup(["Correo", "Push", "SMS"], values=["Push"], label="Canales")
```

### `ui.ColorInput`

Selector de color.

```text
ui.ColorInput(value="#4f46e5", label=None, name=None, on_change=None)
```

```python
ui.ColorInput("#4f46e5", label="Color de marca")
```

### `ui.Combobox`

Texto con sugerencias (`datalist`).

```text
ui.Combobox(value="", items=None, label=None, help_text=None, error=None, placeholder=None, name=None, on_change=None)
```

```python
ui.Combobox("", items=["Madrid", "Barcelona"], label="Ciudad")
```

### `ui.Datalist`

Lista de sugerencias suelta.

```text
ui.Datalist(items=None)
```

```python
ui.Datalist(["uno", "dos"])
```

### `ui.DateInput`

Selector de fecha.

```text
ui.DateInput(value="")
```

```python
ui.DateInput("2026-01-31", label="Fecha")
```

### `ui.DateRangeInput`

Rango de fechas.

```text
ui.DateRangeInput(start="", end="", label=None, start_label="Desde", end_label="Hasta", on_change=None)
```

```python
ui.DateRangeInput("2026-01-01", "2026-01-31", label="Periodo")
```

### `ui.DateTimeInput`

Fecha y hora.

```text
ui.DateTimeInput(value="")
```

```python
ui.DateTimeInput("2026-01-31T09:30", label="Fecha y hora")
```

### `ui.Dropzone`

Zona de arrastrar y soltar archivos.

```text
ui.Dropzone(*children, label="Arrastra archivos aquí", hint="o haz clic para seleccionarlos", accept=None, multiple=True)
```

```python
ui.Dropzone(label="Suelta archivos aquí", accept=".csv")
```

### `ui.EmailInput`

Campo de correo.

```text
ui.EmailInput(*children)
```

```python
ui.EmailInput("", label="Correo", help_text="No lo compartiremos")
```

### `ui.Fieldset`

Grupo de campos con leyenda.

```text
ui.Fieldset(*children, legend=None)
```

```python
ui.Fieldset(ui.Input("", label="Calle"), legend="Dirección")
```

### `ui.FileInput`

Selector de archivos (se suben al proceso local).

```text
ui.FileInput(accept=None, multiple=False, label=None, help_text=None, name=None)
```

```python
ui.FileInput(label="Adjuntar", accept=".pdf,.txt", multiple=True)
```

### `ui.Form`

Formulario que envía todos los campos a Python.

```text
ui.Form(*children, on_submit=None, layout="stack", gap=4)
```

```python
ui.Form(ui.Input("", label="Nombre"), ui.Button("Enviar", submit=True), on_submit=lambda e: None)
```

### `ui.FormField`

Envuelve un control con etiqueta, ayuda y error.

```text
ui.FormField(*children, label=None, help_text=None, error=None, required=False, for_=None, horizontal=False)
```

```python
ui.FormField(ui.Input(""), label="Nombre", help_text="Como en tu DNI", required=True)
```

### `ui.HiddenInput`

Campo oculto.

```text
ui.HiddenInput(value="", name=None)
```

```python
ui.HiddenInput("abc123", name="token")
```

### `ui.Input`

Campo de texto con etiqueta, ayuda, error e iconos.

```text
ui.Input(value="", name=None, placeholder=None, size="md", icon=None, trailing=None, label=None, help_text=None, error=None, required=False, disabled=False, readonly=False, invalid=None, live=False, debounce=220, horizontal=False, autofocus=False, autocomplete=None)
```

```python
ui.Input("", label="Nombre", placeholder="Ana Ruiz", icon="user", required=True)
```

### `ui.MonthInput`

Selector de mes.

```text
ui.MonthInput(value="")
```

```python
ui.MonthInput("2026-01", label="Mes")
```

### `ui.MultiSelect`

Selección múltiple.

```text
ui.MultiSelect(options=None, values=None)
```

```python
ui.MultiSelect([("a", "A"), ("b", "B"), ("c", "C")], values=["a"], label="Opciones")
```

### `ui.NumberInput`

Campo numérico con `min`, `max`, `step`.

```text
ui.NumberInput(value="", min=None, max=None, step=None)
```

```python
ui.NumberInput(3, label="Cantidad", min=0, max=99)
```

### `ui.OtpInput`

Código de un solo uso.

```text
ui.OtpInput(length=6, value="", label=None, on_change=None, size="md")
```

```python
ui.OtpInput(6, label="Código de verificación")
```

### `ui.PasswordInput`

Contraseña con botón para mostrarla.

```text
ui.PasswordInput(*children)
```

```python
ui.PasswordInput("", label="Contraseña")
```

### `ui.Radio`

Opción de radio individual.

```text
ui.Radio(label=None, checked=False, value="on", name="radio", disabled=False, help_text=None)
```

```python
ui.Radio("Tarjeta", value="card", name="pago", checked=True)
```

### `ui.RadioGroup`

Grupo de radios, en lista o tarjetas.

```text
ui.RadioGroup(items=None, value="", name="radio", label=None, help_text=None, cards=False, columns=1, on_change=None)
```

```python
ui.RadioGroup(["Tarjeta", "Bizum"], value="Bizum", label="Pago")
```

### `ui.RangeSlider`

Rango con dos deslizadores.

```text
ui.RangeSlider(low=20, high=80, min=0, max=100, step=1, label=None, on_change=None)
```

```python
ui.RangeSlider(20, 80, label="Precio")
```

### `ui.Rating`

Valoración por estrellas.

```text
ui.Rating(value=0, max_stars=5, label=None, on_change=None, read_only=False, size=6)
```

```python
ui.Rating(4, label="Valoración", on_change=lambda e: None)
```

### `ui.SearchInput`

Buscador con eventos en vivo.

```text
ui.SearchInput(*children)
```

```python
ui.SearchInput("", label="Buscar", live=True, on_input=lambda e: None)
```

### `ui.SegmentedControl`

Selector de segmentos.

```text
ui.SegmentedControl(items=None, value="", on_change=None, label=None, full_width=False)
```

```python
ui.SegmentedControl([("d", "Día"), ("s", "Semana")], value="s", label="Vista")
```

### `ui.Select`

Lista desplegable.

```text
ui.Select(options=None, value="", name=None, placeholder=None, size="md", label=None, help_text=None, error=None, required=False, disabled=False, multiple=False)
```

```python
ui.Select([("es", "Español"), ("en", "English")], label="Idioma", value="es")
```

### `ui.Slider`

Deslizador numérico.

```text
ui.Slider(value=50, min=0, max=100, step=1, label=None, show_value=True, unit="", live=False, on_change=None)
```

```python
ui.Slider(64, label="Volumen", unit=" %")
```

### `ui.Stepper`

Contador con botones − / +.

```text
ui.Stepper(value=0, min=None, max=None, step=1, label=None, on_click=None)
```

```python
ui.Stepper(2, label="Pasajeros", min=0, max=9)
```

### `ui.Switch`

Interruptor de encendido/apagado.

```text
ui.Switch(label=None, checked=False, name=None, disabled=False, size="md", help_text=None)
```

```python
ui.Switch("Recordarme", checked=True, help_text="En este equipo")
```

### `ui.TagInput`

Etiquetas con alta y baja.

```text
ui.TagInput(tags=None, label=None, placeholder="Añadir y pulsar Enter", on_add=None, on_remove=None)
```

```python
ui.TagInput(["python", "tailwind"], label="Etiquetas")
```

### `ui.TextInput`

Alias de `Input` para texto.

```text
ui.TextInput(value="", name=None, placeholder=None, size="md", icon=None, trailing=None, label=None, help_text=None, error=None, required=False, disabled=False, readonly=False, invalid=None, live=False, debounce=220, horizontal=False, autofocus=False, autocomplete=None)
```

```python
ui.TextInput("valor inicial", label="Texto")
```

### `ui.Textarea`

Área de texto multilínea.

```text
ui.Textarea(value="", rows=4, name=None, placeholder=None, label=None, help_text=None, error=None, required=False, disabled=False, resize="y", invalid=None, live=False)
```

```python
ui.Textarea("", label="Notas", rows=4, placeholder="Escribe aquí…")
```

### `ui.TimeInput`

Selector de hora.

```text
ui.TimeInput(value="")
```

```python
ui.TimeInput("09:30", label="Hora")
```

### `ui.ToggleGroup`

Botones de alternancia.

```text
ui.ToggleGroup(items=None, values=None, on_change=None)
```

```python
ui.ToggleGroup([("b", "Negrita"), ("i", "Cursiva")], values=["b"])
```

### `ui.ValidationSummary`

Resumen de errores de validación.

```text
ui.ValidationSummary(errors=None, title="Revisa los siguientes campos")
```

```python
ui.ValidationSummary(["El nombre es obligatorio", "Correo inválido"])
```

### `ui.WeekInput`

Selector de semana.

```text
ui.WeekInput(value="")
```

```python
ui.WeekInput("2026-W05", label="Semana")
```


## Datos y tablas

### `ui.DataTable`

Tabla con orden, búsqueda, selección y paginación.

```text
ui.DataTable(columns=None, rows=None, sort=None, direction="asc", page=1, page_size=10, selectable=False, selected=None, search="", searchable=False, search_placeholder="Buscar…", empty="No hay resultados", on_sort=None, on_page=None, on_select=None, on_search=None, total=None)
```

```python
ui.DataTable(columns=[{"key": "nombre", "label": "Nombre", "sortable": True}], rows=[{"id": 1, "nombre": "Ana"}], total=1, page=1, searchable=True)
```

### `ui.DescriptionItem`

Término y definición.

```text
ui.DescriptionItem(term, definition)
```

```python
ui.DescriptionItem("Licencia", "MIT")
```

### `ui.DescriptionList`

Lista de definiciones.

```text
ui.DescriptionList(*children)
```

```python
ui.DescriptionList(ui.DescriptionItem("Versión", "0.1.0"))
```

### `ui.EmptyState`

Estado vacío con acción.

```text
ui.EmptyState(*children, icon="inbox", title="Nada por aquí", description=None)
```

```python
ui.EmptyState(title="Sin proyectos", description="Crea el primero para empezar.", icon="inbox")
```

### `ui.JsonView`

Visualizador de JSON.

```text
ui.JsonView(data=None, max_h="96")
```

```python
ui.JsonView({"id": 42, "tags": ["a", "b"], "activo": True})
```

### `ui.KeyValueGrid`

Pares clave/valor.

```text
ui.KeyValueGrid(items=None, columns=2)
```

```python
ui.KeyValueGrid({"Nombre": "interui", "Versión": "0.1.0"})
```

### `ui.ListGroup`

Lista agrupada.

```text
ui.ListGroup(*children, divided=True)
```

```python
ui.ListGroup(ui.ListItem(title="Reunión", subtitle="10:00", icon="users", meta="3"))
```

### `ui.ListItem`

Elemento de lista con icono y meta.

```text
ui.ListItem(*children, title=None, subtitle=None, icon=None, meta=None, active=False)
```

```python
ui.ListItem(title="Informe", subtitle="Ayer", icon="file", meta="PDF")
```

### `ui.LogView`

Visor de registros con niveles.

```text
ui.LogView(lines=None, max_h="80", title=None)
```

```python
ui.LogView([{"level": "info", "time": "09:12", "message": "inicio"}], title="app.log")
```

### `ui.Stat`

Indicador con valor y variación.

```text
ui.Stat(label, value, delta=None, positive=True, icon=None, hint=None)
```

```python
ui.Stat("Ingresos", "24.980 €", delta="+12 %", icon="chart")
```

### `ui.StatGrid`

Rejilla de indicadores.

```text
ui.StatGrid(*children, columns=4)
```

```python
ui.StatGrid(ui.Stat("A", "1"), ui.Stat("B", "2"), columns=2)
```

### `ui.Table`

Tabla estática.

```text
ui.Table(headers=None, rows=None, caption=None, striped=False, hover=True, compact=False, bordered=False, footer=None, align=None, empty="Sin datos")
```

```python
ui.Table(headers=["Nombre", "Rol"], rows=[["Ana", "Admin"], ["Luis", "Editor"]], striped=True)
```

### `ui.Timeline`

Línea de tiempo.

```text
ui.Timeline(*children)
```

```python
ui.Timeline(ui.TimelineItem("Pedido creado", time="09:12", icon="check"))
```

### `ui.TimelineItem`

Hito de la línea de tiempo.

```text
ui.TimelineItem(title, description=None, time=None, icon=None, tone="primary", last=False)
```

```python
ui.TimelineItem("Pago confirmado", time="09:15", tone="success", last=True)
```

### `ui.Tree`

Árbol jerárquico.

```text
ui.Tree(*children)
```

```python
ui.Tree(ui.TreeNode("src", icon="folder", expanded=True, children=[ui.TreeNode("app.py", icon="file")]))
```

### `ui.TreeNode`

Nodo de árbol plegable.

```text
ui.TreeNode(label, icon=None, children=None, expanded=False, on_toggle=None, on_click=None, level=0)
```

```python
ui.TreeNode("src", icon="folder", expanded=True)
```


## Retroalimentación

### `ui.Alert`

Aviso con nivel y cierre.

```text
ui.Alert(*children, title=None, level="info", icon=None, dismissible=False, bordered=True)
```

```python
ui.Alert("Todo correcto.", level="success", title="Listo", dismissible=True)
```

### `ui.Banner`

Franja de aviso a todo el ancho.

```text
ui.Banner(*children, level="info", icon=None)
```

```python
ui.Banner("Mantenimiento programado", level="warning")
```

### `ui.Callout`

Alias de `Alert`.

```text
ui.Callout(*children, title=None, level="info", icon=None, dismissible=False, bordered=True)
```

```python
ui.Callout("Revisa la configuración.", level="warning")
```

### `ui.ConfirmDialog`

Diálogo de confirmación gestionado en Python.

```text
ui.ConfirmDialog(*children, title="¿Estás seguro?", confirm_label="Confirmar", cancel_label="Cancelar", on_confirm=None, on_cancel=None, level="danger", open=False)
```

```python
ui.ConfirmDialog("Esta acción no se puede deshacer.", title="¿Eliminar?", dialog_id="confirmar")
```

### `ui.Hint`

Texto de ayuda pequeño.

```text
ui.Hint(*children)
```

```python
ui.Hint("Se guarda automáticamente")
```

### `ui.InlineToast`

Aviso compacto en línea.

```text
ui.InlineToast(*children, title=None, level="info")
```

```python
ui.InlineToast("Guardado correctamente", level="success")
```

### `ui.LoadingOverlay`

Superpone un cargando sobre su contenido.

```text
ui.LoadingOverlay(*children, message="Cargando…")
```

```python
ui.LoadingOverlay(ui.Text("contenido"), message="Cargando…")
```

### `ui.Meter`

Medidor con color según el valor.

```text
ui.Meter(value=0, max_value=100, label=None)
```

```python
ui.Meter(82, label="Memoria")
```

### `ui.Progress`

Barra de progreso determinada o indeterminada.

```text
ui.Progress(value=0, max_value=100, label=None, show_value=False, tone="primary", size="md", striped=False, indeterminate=False)
```

```python
ui.Progress(72, label="Subiendo", show_value=True)
```

### `ui.ProgressRing`

Anillo de progreso.

```text
ui.ProgressRing(value=0, max_value=100, size=96, thickness=8, label=None, tone="primary")
```

```python
ui.ProgressRing(72, label="72 %")
```

### `ui.Skeleton`

Marcador de carga.

```text
ui.Skeleton(width="full", height="4", circle=False, lines=1)
```

```python
ui.Skeleton(lines=3, height="3")
```

### `ui.StatusDot`

Punto de estado.

```text
ui.StatusDot(label=None, tone="success", pulse=False)
```

```python
ui.StatusDot("Operativo", tone="success", pulse=True)
```


## Contenedores y superposiciones

### `ui.Accordion`

Lista de secciones plegables.

```text
ui.Accordion(items=None, default_open=0)
```

```python
ui.Accordion([("Uno", ui.Text("contenido 1")), ("Dos", ui.Text("contenido 2"))])
```

### `ui.Card`

Tarjeta con cabecera, cuerpo y pie.

```text
ui.Card(*children, title=None, description=None, footer=None, icon=None, actions=None, padding=True, hover=False, radius="md", elevated=True)
```

```python
ui.Card(title="Tarjeta", description="Con cabecera", icon="layers")(ui.Text("cuerpo"))
```

### `ui.Collapse`

Sección plegable en el cliente.

```text
ui.Collapse(*children, title="Detalles", open=False)
```

```python
ui.Collapse(ui.Text("contenido oculto"), title="Más información")
```

### `ui.Drawer`

Panel lateral deslizante.

```text
ui.Drawer(*children, drawer_id="drawer", side="right", title=None, size="md", open=False)
```

```python
ui.Drawer(ui.Text("Panel lateral"), drawer_id="detalle", title="Detalle")
```

### `ui.Dropdown`

Botón con menú desplegable.

```text
ui.Dropdown(*children, label="Opciones", icon=None, variant="outline", align="left")
```

```python
ui.Dropdown(ui.MenuItem("Editar", icon="edit"), ui.MenuItem("Borrar", danger=True), label="Acciones")
```

### `ui.Footer`

Pie de página.

```text
ui.Footer(*children)
```

```python
ui.Footer(ui.Text("© 2026 interui"))
```

### `ui.Hero`

Bloque destacado con degradado.

```text
ui.Hero(*children, eyebrow=None)
```

```python
ui.Hero(ui.Title("Bienvenido"), eyebrow="Novedad")
```

### `ui.Menu`

Contenedor de menú.

```text
ui.Menu(*children)
```

```python
ui.Menu(ui.MenuItem("Inicio", icon="home"), ui.MenuItem("Ajustes", icon="settings"))
```

### `ui.MenuItem`

Entrada de menú.

```text
ui.MenuItem(label="", icon=None, shortcut=None, danger=False, href=None, on_click=None)
```

```python
ui.MenuItem("Duplicar", icon="copy", shortcut="⌘D")
```

### `ui.Modal`

Diálogo modal; `.trigger()` crea el botón que lo abre.

```text
ui.Modal(*children, dialog_id="modal", title=None, description=None, footer=None, size="md", open=False, closable=True)
```

```python
ui.Modal(ui.Text("Contenido del modal"), dialog_id="alta", title="Nueva ficha")
```

### `ui.PageHeader`

Cabecera de página con migas y acciones.

```text
ui.PageHeader(title, subtitle=None, actions=None, breadcrumb=None)
```

```python
ui.PageHeader("Proyectos", subtitle="12 activos", actions=ui.Button("Nuevo", icon="plus"))
```

### `ui.Panel`

Superficie con padding.

```text
ui.Panel(*children, tone="muted", padding=4)
```

```python
ui.Panel(ui.Text("contenido"), tone="muted")
```

### `ui.Paper`

Hoja con sombra.

```text
ui.Paper(*children)
```

```python
ui.Paper(ui.Text("hoja con sombra"))
```

### `ui.Popover`

Panel emergente anclado.

```text
ui.Popover(*children, trigger="Abrir", title=None)
```

```python
ui.Popover(ui.Text("detalle"), trigger="Ver más", title="Información")
```

### `ui.Section`

Sección con título y acciones.

```text
ui.Section(*children, title=None, subtitle=None, actions=None)
```

```python
ui.Section(ui.Text("contenido"), title="Sección", subtitle="Con subtítulo")
```

### `ui.Sheet`

Hoja inferior.

```text
ui.Sheet(*children, sheet_id="sheet", title=None, open=False)
```

```python
ui.Sheet(ui.Text("Hoja inferior"), sheet_id="hoja", title="Opciones")
```

### `ui.Splitter`

Dos paneles redimensionables.

```text
ui.Splitter(first, second, direction="horizontal", initial="50%")
```

```python
ui.Splitter(ui.Text("izquierda"), ui.Text("derecha"))
```

### `ui.StatusBar`

Barra inferior de estado.

```text
ui.StatusBar(*children)
```

```python
ui.StatusBar(ui.Text("Listo"), ui.Badge("local", variant="success"))
```

### `ui.TitleBar`

Barra de título propia para ventanas sin marco.

```text
ui.TitleBar(*children, title=None, icon=None, controls=True)
```

```python
ui.TitleBar("Mi app", icon="layers")
```

### `ui.Toolbar`

Barra de herramientas.

```text
ui.Toolbar(*children, sticky=False)
```

```python
ui.Toolbar(ui.Button("Nuevo", size="sm"), ui.Button("Filtrar", variant="outline", size="sm"))
```

### `ui.Tooltip`

Ayuda emergente al pasar el ratón.

```text
ui.Tooltip(*children, content="", placement="top")
```

```python
ui.Tooltip(ui.Button("?", variant="outline"), content="Ayuda contextual")
```

### `ui.Well`

Caja hundida para contenido secundario.

```text
ui.Well(*children)
```

```python
ui.Well(ui.Text("bloque hundido"))
```


## Navegación

### `ui.Breadcrumb`

Migas de pan.

```text
ui.Breadcrumb(items=None, separator="chevron")
```

```python
ui.Breadcrumb([("/", "Inicio"), ("/proyectos", "Proyectos"), ("x", "interui")])
```

### `ui.CommandItem`

Acción de la paleta.

```text
ui.CommandItem(label="", hint=None, icon="search", on_click=None)
```

```python
ui.CommandItem("Nuevo proyecto", hint="N", icon="plus")
```

### `ui.CommandPalette`

Paleta de comandos con filtrado instantáneo.

```text
ui.CommandPalette(*children, placeholder="Buscar acciones…")
```

```python
ui.CommandPalette(ui.CommandItem("Ir al inicio", hint="G H", icon="home"))
```

### `ui.NavLink`

Enlace de navegación con estado activo.

```text
ui.NavLink(label="", href="#", icon=None, active=False, badge=None, on_click=None)
```

```python
ui.NavLink("Equipo", href="/equipo", icon="users")
```

### `ui.Navbar`

Barra superior de navegación.

```text
ui.Navbar(*children, brand=None, logo="layers", sticky=True)
```

```python
ui.Navbar(ui.NavLink("Inicio", href="/", active=True), brand="Mi app")
```

### `ui.Pagination`

Paginación con eventos a Python.

```text
ui.Pagination(page=1, pages=1, on_page=None, window=5)
```

```python
ui.Pagination(3, pages=12, on_page=lambda e: None)
```

### `ui.Sidebar`

Barra lateral.

```text
ui.Sidebar(*children, title=None, width="w-64")
```

```python
ui.Sidebar(ui.SidebarItem("Panel", icon="grid", active=True), title="Navegación")
```

### `ui.SidebarItem`

Elemento de barra lateral.

```text
ui.SidebarItem(label="", icon=None, active=False, badge=None, on_click=None, children=None)
```

```python
ui.SidebarItem("Informes", icon="chart", badge=2)
```

### `ui.Steps`

Pasos de un asistente.

```text
ui.Steps(items=None, current=0, on_step=None)
```

```python
ui.Steps(["Cuenta", "Perfil", "Pago"], current=1)
```

### `ui.TabBar`

Alias de `Tabs`.

```text
ui.TabBar(tabs=None, active=None, on_change=None, variant="line", size="md")
```

```python
ui.Tabs([("a", "Uno", ui.Text("A"))], active="a", variant="pills")
```

### `ui.Tabs`

Pestañas; cambian en el cliente o en Python.

```text
ui.Tabs(tabs=None, active=None, on_change=None, variant="line", size="md")
```

```python
ui.Tabs([("a", "Uno", ui.Text("panel A")), ("b", "Dos", ui.Text("panel B"))], active="a")
```


## Gráficos

### `ui.AreaChart`

Área con relleno.

```text
ui.AreaChart(series=None)
```

```python
ui.AreaChart({"2025": [8, 14, 18, 16, 25]}, labels=["Ene", "Feb", "Mar", "Abr", "May"])
```

### `ui.BarChart`

Barras verticales.

```text
ui.BarChart(series=None, horizontal=False, radius=4)
```

```python
ui.BarChart([[18, 26, 12, 30]], labels=["L", "M", "X", "J"], show_values=True)
```

### `ui.ChartCard`

Tarjeta con gráfico.

```text
ui.ChartCard(chart, title=None, subtitle=None)
```

```python
ui.ChartCard(ui.Sparkline([1, 3, 2, 5]), title="Tendencia", subtitle="Últimos 7 días")
```

### `ui.ColumnChart`

Alias de `BarChart`.

```text
ui.ColumnChart(series=None, horizontal=False, radius=4)
```

```python
ui.ColumnChart([[5, 9, 3]], labels=["a", "b", "c"])
```

### `ui.DonutChart`

Anillo con total.

```text
ui.DonutChart(data=None)
```

```python
ui.DonutChart({"A": 60, "B": 40})
```

### `ui.Gauge`

Arco de progreso.

```text
ui.Gauge(value=0, max_value=100, label=None, color="#4f46e5", size=180)
```

```python
ui.Gauge(64, label="CPU")
```

### `ui.Legend`

Leyenda de series.

```text
ui.Legend(items=None)
```

```python
ui.Legend(["Ventas", "Costes"])
```

### `ui.LineChart`

Gráfico de líneas.

```text
ui.LineChart(series=None, smooth=False, fill=False)
```

```python
ui.LineChart([[3, 6, 4, 9, 7]], labels=["L", "M", "X", "J", "V"])
```

### `ui.PieChart`

Gráfico circular.

```text
ui.PieChart(data=None, donut=False, thickness=0.55)
```

```python
ui.PieChart({"Directo": 42, "Social": 28, "Búsqueda": 30})
```

### `ui.ScatterChart`

Dispersión de puntos.

```text
ui.ScatterChart(series=None, labels=None, height=260, show_grid=True, show_legend=True, show_values=False, colors=None)
```

```python
ui.ScatterChart([[3, 7, 2, 9]])
```

### `ui.Sparkline`

Mini gráfico de tendencia.

```text
ui.Sparkline(data=None, color="#4f46e5", height=32, width=120, fill=True)
```

```python
ui.Sparkline([4, 8, 6, 12, 9, 14])
```


## Medios

### `ui.Audio`

Reproductor de audio.

```text
ui.Audio(src="", controls=True)
```

```python
ui.Audio("https://ejemplo.com/audio.mp3")
```

### `ui.Avatar`

Avatar con iniciales o foto.

```text
ui.Avatar(src=None, name="", initials=None, size="md", status=None, ring=True)
```

```python
ui.Avatar(name="Ana Ruiz", size="lg", status="online")
```

### `ui.AvatarGroup`

Avatares apilados.

```text
ui.AvatarGroup(*children, max_items=4)
```

```python
ui.AvatarGroup(ui.Avatar(name="Ana Ruiz"), ui.Avatar(name="Luis Paz"), max_items=2)
```

### `ui.Carousel`

Carrusel controlado por Python.

```text
ui.Carousel(slides=None, index=0, on_change=None)
```

```python
ui.Carousel([ui.Text("diapositiva 1"), ui.Text("diapositiva 2")], index=0)
```

### `ui.Figure`

Imagen con pie de foto.

```text
ui.Figure(image, caption=None)
```

```python
ui.Figure(ui.Image("foto.png", alt="Foto"), caption="Figura 1")
```

### `ui.Gallery`

Rejilla de imágenes.

```text
ui.Gallery(*children, columns=3, gap=3)
```

```python
ui.Gallery(ui.Image("a.png", alt="A"), ui.Image("b.png", alt="B"), columns=2)
```

### `ui.IconBadge`

Icono en una caja de color.

```text
ui.IconBadge(icon="check", tone="primary", size="md")
```

```python
ui.IconBadge("zap", tone="primary")
```

### `ui.Image`

Imagen con proporción y ajuste.

```text
ui.Image(src="", alt="", ratio=None, fit="cover", rounded="lg", width=None, height=None)
```

```python
ui.Image("https://picsum.photos/seed/a/600/400", alt="Paisaje", ratio="video")
```

### `ui.Video`

Reproductor de vídeo.

```text
ui.Video(src="", poster=None, controls=True, autoplay=False, loop=False, muted=True, rounded="xl")
```

```python
ui.Video("https://ejemplo.com/video.mp4", poster="portada.jpg")
```


## Avanzados

### `ui.Canvas`

Lienzo para dibujar con JS.

```text
ui.Canvas(width=400, height=200, script=None)
```

```python
ui.Canvas(width=400, height=200)
```

### `ui.CodeEditor`

Editor de código con numeración.

```text
ui.CodeEditor(value="", language=None, line_numbers=True, readonly=False, rows=14, max_h="none", placeholder=None, on_change=None)
```

```python
ui.CodeEditor("print(1)", language="python", max_h="64")
```

### `ui.Html`

HTML literal (no escapa nada).

```text
ui.Html(markup="")
```

```python
ui.Html("<b>HTML literal</b>")
```

### `ui.Iframe`

Contenido incrustado aislado.

```text
ui.Iframe(src=None, srcdoc=None, height="420", sandbox="allow-scripts allow-forms allow-popups")
```

```python
ui.Iframe(srcdoc="<h1>Hola</h1>", height="60")
```

### `ui.KeyValueEditor`

Editor de pares clave/valor.

```text
ui.KeyValueEditor(items=None, on_change=None, on_add=None, on_remove=None)
```

```python
ui.KeyValueEditor({"API_URL": "https://api.ejemplo.com"})
```

### `ui.Markdown`

Subconjunto de Markdown.

```text
ui.Markdown(text="")
```

```python
ui.Markdown("# Título\n\n- uno\n- dos\n\n**negrita** y `código`")
```

### `ui.ProgressTable`

Tabla con barras de progreso.

```text
ui.ProgressTable(rows=None, max_value=100)
```

```python
ui.ProgressTable([{"label": "Diseño", "value": 100}, {"label": "Código", "value": 60}])
```

### `ui.RichTextEditor`

Editor de texto enriquecido.

```text
ui.RichTextEditor(value="", on_change=None, min_h="40", toolbar=True)
```

```python
ui.RichTextEditor("<b>Texto</b> editable", min_h="32")
```

### `ui.Terminal`

Vista de terminal.

```text
ui.Terminal(lines=None, prompt="$", title="terminal", max_h="72")
```

```python
ui.Terminal(["pip install interui", "python app.py"], title="zsh")
```


## Iconos

### `ui.Icon`

Icono SVG del set incluido (`ui.ICON_NAMES`).

```text
ui.Icon(name="check", size=5, stroke=None, class_=None)
```

```python
ui.Icon("check", size=6, class_="text-emerald-600")
```


## Etiquetas html

### `ui.A`

Enlace `<a>` con estilo de enlace.

```text
ui.A(*children, href="#")
```

```python
ui.A("Enlace", href="/ruta")
```

### `ui.Article`

Contenedor semántico `<article>`.

```text
ui.Article(*children)
```

```python
ui.Article("Contenido del artículo")
```

### `ui.Aside`

Contenido lateral `<aside>`.

```text
ui.Aside(*children)
```

```python
ui.Aside("Nota lateral")
```

### `ui.B`

Negrita visual `<b>`.

```text
ui.B(*children)
```

```python
ui.B("negrita")
```

### `ui.Br`

Salto de línea `<br>`.

```python
ui.Br()
```

### `ui.Details`

Sección desplegable nativa `<details>`.

```text
ui.Details(*children, open=False)
```

```python
ui.Details(ui.Summary("Más detalles"), ui.Text("contenido"))
```

### `ui.DetailsBlock`

Alias de `Details`.

```text
ui.DetailsBlock(*children, open=False)
```

```python
ui.DetailsBlock(ui.Summary("Detalles"), ui.Text("contenido"))
```

### `ui.Div`

Caja genérica `<div>`.

```text
ui.Div(*children)
```

```python
ui.Div("contenido")
```

### `ui.Figcaption`

Pie de figura.

```text
ui.Figcaption(*children)
```

```python
ui.Figcaption("Pie de figura")
```

### `ui.Figure`

Figura genérica.

```text
ui.Figure(*children)
```

```python
ui.Figure(ui.Image("foto.png", alt="Foto"), caption="Figura 1")
```

### `ui.H1`

Encabezado `<h1>` con estilo.

```text
ui.H1(*children)
```

```python
ui.H1("Título 1")
```

### `ui.H2`

Encabezado `<h2>` con estilo.

```text
ui.H2(*children)
```

```python
ui.H2("Título 2")
```

### `ui.H3`

Encabezado `<h3>` con estilo.

```text
ui.H3(*children)
```

```python
ui.H3("Título 3")
```

### `ui.H4`

Encabezado `<h4>` con estilo.

```text
ui.H4(*children)
```

```python
ui.H4("Título 4")
```

### `ui.H5`

Encabezado `<h5>` con estilo.

```text
ui.H5(*children)
```

```python
ui.H5("Título 5")
```

### `ui.H6`

Encabezado `<h6>` con estilo.

```text
ui.H6(*children)
```

```python
ui.H6("Título 6")
```

### `ui.Header`

Cabecera semántica.

```text
ui.Header(*children)
```

```python
ui.Header("cabecera")
```

### `ui.Hr`

Línea separadora `<hr>`.

```python
ui.Hr()
```

### `ui.I`

Cursiva visual `<i>`.

```text
ui.I(*children)
```

```python
ui.I("cursiva")
```

### `ui.Img`

Imagen `<img>` sin recorte.

```text
ui.Img(src="", alt="")
```

```python
ui.Img("foto.png", alt="Foto")
```

### `ui.Li`

Elemento de lista `<li>`.

```text
ui.Li(*children)
```

```python
ui.Li("elemento")
```

### `ui.Main`

Contenido principal (`flex-1`).

```text
ui.Main(*children)
```

```python
ui.Main("contenido principal")
```

### `ui.Nav`

Contenedor de navegación.

```text
ui.Nav(*children)
```

```python
ui.Nav("navegación")
```

### `ui.Ol`

Lista numerada `<ol>`.

```text
ui.Ol(*children)
```

```python
ui.Ol(ui.Li("primero"), ui.Li("segundo"))
```

### `ui.P`

Párrafo `<p>`.

```text
ui.P(*children)
```

```python
ui.P("párrafo")
```

### `ui.Pre`

Texto preformateado.

```text
ui.Pre(*children)
```

```python
ui.Pre("texto preformateado")
```

### `ui.S`

Texto tachado.

```text
ui.S(*children)
```

```python
ui.S("tachado")
```

### `ui.Section`

Sección HTML (`ui.Section` es la versión con título).

```text
ui.Section(*children)
```

```python
ui.Section(ui.Text("contenido"), title="Sección", subtitle="Con subtítulo")
```

### `ui.Span`

Texto en línea `<span>`.

```text
ui.Span(*children)
```

```python
ui.Span("texto en línea")
```

### `ui.Sub`

Subíndice.

```text
ui.Sub(*children)
```

```python
ui.Sub("sub")
```

### `ui.Summary`

Encabezado de un `Details`.

```text
ui.Summary(*children)
```

```python
ui.Summary("Resumen")
```

### `ui.Sup`

Superíndice.

```text
ui.Sup(*children)
```

```python
ui.Sup("sup")
```

### `ui.Template`

Envoltura de composición sin semántica.

```text
ui.Template(*children)
```

```python
ui.Template("contenido")
```

### `ui.Time`

Fecha/hora semántica.

```text
ui.Time(*children)
```

```python
ui.Time("2026-01-31", datetime="2026-01-31")
```

### `ui.U`

Subrayado.

```text
ui.U(*children)
```

```python
ui.U("subrayado")
```

### `ui.Ul`

Lista con viñetas `<ul>`.

```text
ui.Ul(*children)
```

```python
ui.Ul(ui.Li("uno"), ui.Li("dos"))
```
