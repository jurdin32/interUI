# Referencia de controles

Todos los controles se importan desde `interui`:

```python
import interui as ui

ui.Card(title="Hola")(
    ui.Text("Contenido"),
    ui.Button("Pulsar", on_click=lambda: print("clic")),
)
```

Convenciones comunes a **todos** los controles:

| Propiedad | Tipo | Descripción |
|---|---|---|
| `class_` | `str` | Clases Tailwind extra. Sobrescriben las del control (`tw()` resuelve conflictos). |
| `id` | `str` | Identificador estable (si no se indica se genera por posición en el árbol). |
| `key` | `Any` | Sufijo estable para el `id` dentro de listas. |
| `visible` / `when` | `bool` / `callable` | No renderiza el control. |
| `hidden` | `bool` | Renderiza con `hidden` de Tailwind. |
| `style` | `str` / `dict` | Estilos en línea. |
| `data` | `dict` | Atributos `data-*`. |
| `aria` | `dict` | Atributos `aria-*` (`{"label": "..."}`) |
| `on_click`, `on_change`, `on_input`, `on_submit`, `on_keydown`, `on_enter`, … | `callable` | Handlers que se ejecutan en Python (ver README). |

> Esta página se genera desde el propio código (`tests` verifican que el catálogo
> exportado coincide con lo documentado).


## Rejilla y estructura

| Control | Firma | Qué hace |
|---|---|---|
| `ui.AspectRatio` | `*children, ratio="video", **props` | Mantiene proporción (`video`, `square` o `16/9`). |
| `ui.Center` | `*children, **props` | Centra el contenido en ambos ejes. |
| `ui.Col` | `*children, span=12, sm=None, md=None, lg=None, xl=None, xxl=None, offset=None, order=None, **props` | Columna de la rejilla de 12. |
| `ui.Container` | `*children, size="xl", padded=True, **props` | Ancho máximo centrado con padding lateral responsive. |
| `ui.Divider` | `label=None, orientation="horizontal", **props` | Separador horizontal o vertical, con etiqueta opcional. |
| `ui.Grid` | `*children, cols=1, sm=None, md=None, lg=None, xl=None, gap=4, **props` | Rejilla nativa de Tailwind (número de columnas por breakpoint). |
| `ui.Row` | `*children, gap=4, gap_y=None, align="stretch", justify="start", cols=12, dense=False, **props` | Fila de la rejilla (``grid-cols-12``). |
| `ui.Screen` | `*children, **props` | Contenedor a pantalla completa con scroll vertical. |
| `ui.ScrollArea` | `*children, max_h="80", axis="y", **props` | Área con scroll y altura máxima. |
| `ui.Spacer` | `**props` | Empuja el contenido en un flexbox. |
| `ui.Stack` | `*children, direction="col", gap=4, align="stretch", justify="start", wrap=False, **props` | Apila hijos en vertical u horizontal con separación uniforme. |

## Tipografía

| Control | Firma | Qué hace |
|---|---|---|
| `ui.Announcement` | `*children, variant="primary", **props` | Franja destacada de una línea (banner superior). |
| `ui.Badge` | `label="", variant="neutral", size="md", dot=False, icon=None, pill=True, **props` | Etiqueta compacta con variantes de color. |
| `ui.Blockquote` | `*children, cite=None, **props` | Cita con autor opcional. |
| `ui.Chip` | `label="", on_remove=None, variant="neutral", **props` | Etiqueta con botón de borrado opcional. |
| `ui.Code` | `*children, **props` | Fragmento de código en línea. |
| `ui.CodeBlock` | `code="", language=None, filename=None, max_h="none", **props` | Bloque de código con botón de copia al portapapeles. |
| `ui.Em` | `*children, **props` | — |
| `ui.Heading` | `*children, level=2, tone="default", **props` | Encabezado `h1`–`h6` con tamaños predefinidos. |
| `ui.Kbd` | `*children, **props` | Tecla de teclado (`Ctrl`, `Esc`). |
| `ui.Label` | `*children, required=False, for_=None, **props` | Etiqueta de campo (`label`), con marca de obligatorio. |
| `ui.Lead` | `*children, **props` | Entradilla destacada. |
| `ui.Link` | `*children, href="#", external=False, **props` | Enlace interno o externo. |
| `ui.Mark` | `*children, **props` | Texto resaltado. |
| `ui.Muted` | `*children, **props` | Texto secundario atenuado. |
| `ui.Paragraph` | `*children, tone="default", size="base", **props` | Párrafo con interlineado relajado. |
| `ui.Small` | `*children, **props` | — |
| `ui.Strong` | `*children, **props` | — |
| `ui.Text` | `*children, size="base", tone="default", weight=None, leading=None, truncate=False, **props` | Texto con tamaño, tono, peso y truncado. |
| `ui.Title` | `*children, subtitle=None, **props` | Título principal con subtítulo. |

## Botones

| Control | Firma | Qué hace |
|---|---|---|
| `ui.Button` | `*children, label=None, variant="primary", size="md", icon=None, icon_right=None, loading=False, disabled=False, submit=False, full_width=False, href=None, pill=False, **props` | Botón con variantes, tamaños, icono, carga y enlace. |
| `ui.ButtonGroup` | `*children, vertical=False, **props` | Agrupa botones pegados horizontal o verticalmente. |
| `ui.CopyButton` | `text, label="Copiar", icon="copy", **props` | Botón que copia un texto al portapapeles sin ir al servidor. |
| `ui.Fab` | `icon="plus", label=None, **props` | Botón flotante de acción. |
| `ui.IconButton` | `icon="more-h", label=None, variant="ghost", size="md", loading=False, disabled=False, href=None, **props` | Botón cuadrado solo con icono. |
| `ui.LinkButton` | `*children, label=None, variant="primary", size="md", icon=None, icon_right=None, loading=False, disabled=False, submit=False, full_width=False, href=None, pill=False, **props` | — |
| `ui.Spinner` | `size=4, class_=None, **props` | Indicador de carga animado. |

## Formularios

| Control | Firma | Qué hace |
|---|---|---|
| `ui.Checkbox` | `label=None, checked=False, value="on", name=None, disabled=False, help_text=None, indeterminate=False, **props` | Casilla con etiqueta y ayuda. |
| `ui.CheckboxGroup` | `items=None, values=None, name=None, label=None, help_text=None, columns=1, on_change=None, **props` | Grupo de casillas con nombre compartido. |
| `ui.ColorInput` | `value="#4f46e5", label=None, name=None, on_change=None, **props` | Selector de color con campo hexadecimal. |
| `ui.Combobox` | `value="", items=None, label=None, help_text=None, error=None, placeholder=None, name=None, on_change=None, **props` | Campo de texto con sugerencias del navegador (``<datalist>``). |
| `ui.Datalist` | `items=None, **props` | Lista de sugerencias para un campo. |
| `ui.DateInput` | `value="", **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.DateRangeInput` | `start="", end="", label=None, start_label="Desde", end_label="Hasta", on_change=None, **props` | Rango de fechas (desde/hasta). |
| `ui.DateTimeInput` | `value="", **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.Dropzone` | `*children, label="Arrastra archivos aquí", hint="o haz clic para seleccionarlos", accept=None, multiple=True, **props` | Zona de arrastrar y soltar archivos. |
| `ui.EmailInput` | `*children, **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.Fieldset` | `*children, legend=None, **props` | Grupo de campos con leyenda. |
| `ui.FileInput` | `accept=None, multiple=False, label=None, help_text=None, name=None, **props` | Selector de archivos con subida al servidor. |
| `ui.Form` | `*children, on_submit=None, layout="stack", gap=4, **props` | Formulario que envía el conjunto de campos a Python. |
| `ui.FormField` | `*children, label=None, help_text=None, error=None, required=False, for_=None, horizontal=False, **props` | Envuelve un control con etiqueta, ayuda y error. |
| `ui.HiddenInput` | `value="", name=None, **props` | Campo oculto. |
| `ui.Input` | `value="", name=None, placeholder=None, size="md", icon=None, trailing=None, label=None, help_text=None, error=None, required=False, disabled=False, readonly=False, invalid=None, live=False, debounce=220, horizontal=False, autofocus=False, autocomplete=None, **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.MonthInput` | `value="", **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.MultiSelect` | `options=None, values=None, **props` | Selección múltiple de opciones. |
| `ui.NumberInput` | `value="", min=None, max=None, step=None, **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.OtpInput` | `length=6, value="", label=None, on_change=None, size="md", **props` | Código de un solo uso: una caja por dígito con auto-avance. |
| `ui.PasswordInput` | `*children, **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.Radio` | `label=None, checked=False, value="on", name="radio", disabled=False, help_text=None, **props` | Opción de radio individual. |
| `ui.RadioGroup` | `items=None, value="", name="radio", label=None, help_text=None, cards=False, columns=1, on_change=None, **props` | Grupo de radios, en lista o tarjetas. |
| `ui.RangeSlider` | `low=20, high=80, min=0, max=100, step=1, label=None, on_change=None, **props` | Dos deslizadores (mínimo y máximo) para representar un rango. |
| `ui.Rating` | `value=0, max_stars=5, label=None, on_change=None, read_only=False, size=6, **props` | Valoración por estrellas. |
| `ui.SearchInput` | `*children, **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.SegmentedControl` | `items=None, value="", on_change=None, label=None, full_width=False, **props` | Selector de segmentos (estilo iOS). |
| `ui.Select` | `options=None, value="", name=None, placeholder=None, size="md", label=None, help_text=None, error=None, required=False, disabled=False, multiple=False, **props` | Lista desplegable (una o varias opciones). |
| `ui.Slider` | `value=50, min=0, max=100, step=1, label=None, show_value=True, unit="", live=False, on_change=None, **props` | Deslizador numérico. |
| `ui.Stepper` | `value=0, min=None, max=None, step=1, label=None, on_click=None, **props` | Contador numérico con botones − / + enlazados al servidor. |
| `ui.Switch` | `label=None, checked=False, name=None, disabled=False, size="md", help_text=None, **props` | Interruptor de encendido/apagado. |
| `ui.TagInput` | `tags=None, label=None, placeholder="Añadir y pulsar Enter", on_add=None, on_remove=None, **props` | Etiquetas con alta/baja. |
| `ui.TextInput` | `value="", name=None, placeholder=None, size="md", icon=None, trailing=None, label=None, help_text=None, error=None, required=False, disabled=False, readonly=False, invalid=None, live=False, debounce=220, horizontal=False, autofocus=False, autocomplete=None, **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.Textarea` | `value="", rows=4, name=None, placeholder=None, label=None, help_text=None, error=None, required=False, disabled=False, resize="y", invalid=None, live=False, **props` | Área de texto multilínea. |
| `ui.TimeInput` | `value="", **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |
| `ui.ToggleGroup` | `items=None, values=None, on_change=None, **props` | Conjunto de botones de alternancia. |
| `ui.ValidationSummary` | `errors=None, title="Revisa los siguientes campos", **props` | Resumen de errores de validación. |
| `ui.WeekInput` | `value="", **props` | Campo de una línea. Acepta etiqueta, ayuda, error e iconos. |

## Datos

| Control | Firma | Qué hace |
|---|---|---|
| `ui.DataTable` | `columns=None, rows=None, sort=None, direction="asc", page=1, page_size=10, selectable=False, selected=None, search="", searchable=False, search_placeholder="Buscar…", empty="No hay resultados", on_sort=None, on_page=None, on_select=None, on_search=None, total=None, **props` | Tabla con orden, búsqueda, selección y paginación controladas por Python. |
| `ui.DescriptionItem` | `term, definition, **props` | Término y definición. |
| `ui.DescriptionList` | `*children, **props` | Lista de definiciones. |
| `ui.EmptyState` | `*children, icon="inbox", title="Nada por aquí", description=None, **props` | Estado vacío con acción. |
| `ui.JsonView` | `data=None, max_h="96", **props` | Visualizador de JSON con resaltado. |
| `ui.KeyValueGrid` | `items=None, columns=2, **props` | Pares clave/valor en rejilla. |
| `ui.ListGroup` | `*children, divided=True, **props` | Lista de elementos agrupados. |
| `ui.ListItem` | `*children, title=None, subtitle=None, icon=None, meta=None, active=False, **props` | Elemento de lista con icono, título y meta. |
| `ui.LogView` | `lines=None, max_h="80", title=None, **props` | Visor de registros con niveles. |
| `ui.Stat` | `label, value, delta=None, positive=True, icon=None, hint=None, **props` | Indicador con valor y variación. |
| `ui.StatGrid` | `*children, columns=4, **props` | Rejilla de indicadores. |
| `ui.Table` | `headers=None, rows=None, caption=None, striped=False, hover=True, compact=False, bordered=False, footer=None, align=None, empty="Sin datos", **props` | Tabla estática con estilos de cabecera, cebra y hover. |
| `ui.Timeline` | `*children, **props` | Línea de tiempo. |
| `ui.TimelineItem` | `title, description=None, time=None, icon=None, tone="primary", last=False, **props` | Hito de la línea de tiempo. |
| `ui.Tree` | `*children, **props` | Árbol jerárquico. |
| `ui.TreeNode` | `label, icon=None, children=None, expanded=False, on_toggle=None, on_click=None, level=0, **props` | Nodo de árbol plegable. |

## Retroalimentación

| Control | Firma | Qué hace |
|---|---|---|
| `ui.Alert` | `*children, title=None, level="info", icon=None, dismissible=False, bordered=True, **props` | Aviso con nivel, título y cierre. |
| `ui.Banner` | `*children, level="info", icon=None, **props` | Franja de aviso a todo el ancho. |
| `ui.Callout` | `*children, title=None, level="info", icon=None, dismissible=False, bordered=True, **props` | — |
| `ui.ConfirmDialog` | `*children, title="¿Estás seguro?", confirm_label="Confirmar", cancel_label="Cancelar", on_confirm=None, on_cancel=None, level="danger", open=False, **props` | Diálogo de confirmación que delega la decisión en Python. |
| `ui.Hint` | `*children, **props` | Texto de ayuda pequeño. |
| `ui.InlineToast` | `*children, title=None, level="info", **props` | Aviso compacto en línea. |
| `ui.LoadingOverlay` | `*children, message="Cargando…", **props` | Superpone un cargando sobre su contenido. |
| `ui.Meter` | `value=0, max_value=100, label=None, **props` | Medidor con color según el valor. |
| `ui.Progress` | `value=0, max_value=100, label=None, show_value=False, tone="primary", size="md", striped=False, indeterminate=False, **props` | Barra de progreso determinada o indeterminada. |
| `ui.ProgressRing` | `value=0, max_value=100, size=96, thickness=8, label=None, tone="primary", **props` | Anillo de progreso. |
| `ui.Skeleton` | `width="full", height="4", circle=False, lines=1, **props` | Marcador de carga. |
| `ui.StatusDot` | `label=None, tone="success", pulse=False, **props` | Punto de estado con pulso opcional. |

## Contenedores y superposiciones

| Control | Firma | Qué hace |
|---|---|---|
| `ui.Accordion` | `items=None, default_open=0, **props` | Lista de secciones plegables independientes. |
| `ui.Card` | `*children, title=None, description=None, footer=None, icon=None, actions=None, padding=True, hover=False, radius="md", elevated=True, **props` | Tarjeta con cabecera, cuerpo y pie opcionales. |
| `ui.Collapse` | `*children, title="Detalles", open=False, **props` | Sección plegable gestionada en el navegador (sin ir al servidor). |
| `ui.Drawer` | `*children, drawer_id="drawer", side="right", title=None, size="md", open=False, **props` | Panel lateral deslizante. |
| `ui.Dropdown` | `*children, label="Opciones", icon=None, variant="outline", align="left", **props` | Botón con menú desplegable gestionado en el cliente. |
| `ui.Footer` | `*children, **props` | Pie de página. |
| `ui.Hero` | `*children, eyebrow=None, **props` | Bloque destacado con degradado. |
| `ui.Menu` | `*children, **props` | Contenedor de menú. |
| `ui.MenuItem` | `label="", icon=None, shortcut=None, danger=False, href=None, on_click=None, **props` | Entrada de menú con icono y atajo. |
| `ui.Modal` | `*children, dialog_id="modal", title=None, description=None, footer=None, size="md", open=False, closable=True, **props` | Diálogo modal. Ábrelo con ``Modal.trigger()`` o ``data-iui-modal``. |
| `ui.PageHeader` | `title, subtitle=None, actions=None, breadcrumb=None, **props` | Cabecera de página con migas y acciones. |
| `ui.Panel` | `*children, tone="muted", padding=4, **props` | Superficie neutra con padding uniforme. |
| `ui.Paper` | `*children, **props` | Hoja con sombra y borde. |
| `ui.Popover` | `*children, trigger="Abrir", title=None, **props` | Panel emergente anclado a un botón. |
| `ui.Section` | `*children, title=None, subtitle=None, actions=None, **props` | Sección con título y acciones. |
| `ui.Sheet` | `*children, sheet_id="sheet", title=None, open=False, **props` | Hoja inferior. |
| `ui.Splitter` | `first, second, direction="horizontal", initial="50%", **props` | Dos paneles redimensionables (usa ``resize`` nativo del navegador). |
| `ui.StatusBar` | `*children, **props` | Barra inferior para mensajes de estado de la aplicación. |
| `ui.TitleBar` | `*children, title=None, icon=None, controls=True, **props` | Barra de título propia para ventanas sin marco (frameless). |
| `ui.Toolbar` | `*children, sticky=False, **props` | Barra de herramientas. |
| `ui.Tooltip` | `*children, content="", placement="top", **props` | Ayuda emergente al pasar el ratón. |
| `ui.Well` | `*children, **props` | Caja hundida para contenido secundario. |

## Navegación

| Control | Firma | Qué hace |
|---|---|---|
| `ui.Breadcrumb` | `items=None, separator="chevron", **props` | Migas de pan. |
| `ui.CommandItem` | `label="", hint=None, icon="search", on_click=None, **props` | Acción de la paleta. |
| `ui.CommandPalette` | `*children, placeholder="Buscar acciones…", **props` | Buscador de acciones con filtrado instantáneo en el navegador. |
| `ui.NavLink` | `label="", href="#", icon=None, active=False, badge=None, on_click=None, **props` | Enlace de navegación con estado activo. |
| `ui.Navbar` | `*children, brand=None, logo="layers", sticky=True, **props` | Barra superior de navegación. |
| `ui.Pagination` | `page=1, pages=1, on_page=None, window=5, **props` | Paginación con eventos a Python. |
| `ui.Sidebar` | `*children, title=None, width="w-64", **props` | Barra lateral. |
| `ui.SidebarItem` | `label="", icon=None, active=False, badge=None, on_click=None, children=None, **props` | Elemento de barra lateral. |
| `ui.Steps` | `items=None, current=0, on_step=None, **props` | Pasos de un asistente. |
| `ui.TabBar` | `tabs=None, active=None, on_change=None, variant="line", size="md", **props` | Pestañas. Sin ``on_change`` cambian en el navegador; con él, en Python. |
| `ui.Tabs` | `tabs=None, active=None, on_change=None, variant="line", size="md", **props` | Pestañas. Sin ``on_change`` cambian en el navegador; con él, en Python. |

## Gráficos

| Control | Firma | Qué hace |
|---|---|---|
| `ui.AreaChart` | `series=None, **props` | Área suavizada con relleno. |
| `ui.BarChart` | `series=None, horizontal=False, radius=4, **props` | Barras verticales. |
| `ui.ChartCard` | `chart, title=None, subtitle=None, **props` | Tarjeta con título y gráfico. |
| `ui.ColumnChart` | `series=None, horizontal=False, radius=4, **props` | Alias de `BarChart`. |
| `ui.DonutChart` | `data=None, **props` | Anillo con total en el centro. |
| `ui.Gauge` | `value=0, max_value=100, label=None, color="#4f46e5", size=180, **props` | Aguja/arco de progreso. |
| `ui.Legend` | `items=None, **props` | Leyenda de series. |
| `ui.LineChart` | `series=None, smooth=False, fill=False, **props` | Gráfico de líneas (varias series). |
| `ui.PieChart` | `data=None, donut=False, thickness=0.55, **props` | Gráfico circular con leyenda. |
| `ui.ScatterChart` | `series=None, labels=None, height=260, show_grid=True, show_legend=True, show_values=False, colors=None, **props` | Dispersión de puntos. |
| `ui.Sparkline` | `data=None, color="#4f46e5", height=32, width=120, fill=True, **props` | Mini gráfico de tendencia. |

## Medios

| Control | Firma | Qué hace |
|---|---|---|
| `ui.Audio` | `src="", controls=True, **props` | Reproductor de audio. |
| `ui.Avatar` | `src=None, name="", initials=None, size="md", status=None, ring=True, **props` | Avatar con iniciales o foto y estado. |
| `ui.AvatarGroup` | `*children, max_items=4, **props` | Avatares apilados con contador. |
| `ui.Carousel` | `slides=None, index=0, on_change=None, **props` | Carrusel controlado por Python (``index`` + ``on_change``). |
| `ui.Figure` | `image, caption=None, **props` | Imagen con pie de foto. |
| `ui.Gallery` | `*children, columns=3, gap=3, **props` | Rejilla de imágenes. |
| `ui.IconBadge` | `icon="check", tone="primary", size="md", **props` | Icono dentro de una caja de color. |
| `ui.Image` | `src="", alt="", ratio=None, fit="cover", rounded="lg", width=None, height=None, **props` | Imagen con proporción y ajuste. |
| `ui.Video` | `src="", poster=None, controls=True, autoplay=False, loop=False, muted=True, rounded="xl", **props` | Reproductor de vídeo. |

## Avanzados

| Control | Firma | Qué hace |
|---|---|---|
| `ui.Canvas` | `width=400, height=200, script=None, **props` | Lienzo para dibujar con JS. |
| `ui.CodeEditor` | `value="", language=None, line_numbers=True, readonly=False, rows=14, max_h="none", placeholder=None, on_change=None, **props` | Editor de código simple: área de texto monoespaciada con numeración. |
| `ui.Html` | `markup="", **props` | Escotilla de escape: inserta HTML literal (confía en el contenido). |
| `ui.Iframe` | `src=None, srcdoc=None, height="420", sandbox="allow-scripts allow-forms allow-popups", **props` | Contenido incrustado aislado. |
| `ui.KeyValueEditor` | `items=None, on_change=None, on_add=None, on_remove=None, **props` | Editor de pares clave/valor con alta y baja de filas. |
| `ui.Markdown` | `text="", **props` | Renderizador markdown ligero (subconjunto habitual). |
| `ui.ProgressTable` | `rows=None, max_value=100, **props` | Tabla compacta con barras de progreso por fila. |
| `ui.RichTextEditor` | `value="", on_change=None, min_h="40", toolbar=True, **props` | Editor de texto enriquecido (``contenteditable`` + comandos nativos). |
| `ui.Terminal` | `lines=None, prompt="$", title="terminal", max_h="72", **props` | Vista de terminal con prompt. |

## Etiquetas html

| Control | Firma | Qué hace |
|---|---|---|
| `ui.A` | `*children, href="#", **props` | — |
| `ui.Article` | `*children, **props` | — |
| `ui.Aside` | `*children, **props` | — |
| `ui.B` | `*children, **props` | — |
| `ui.Br` | `**props` | — |
| `ui.Details` | `*children, open=False, **props` | — |
| `ui.DetailsBlock` | `*children, open=False, **props` | — |
| `ui.Div` | `*children, **props` | — |
| `ui.Figcaption` | `*children, **props` | — |
| `ui.Figure` | `*children, **props` | Imagen con pie de foto. |
| `ui.H1` | `*children, **props` | — |
| `ui.H2` | `*children, **props` | — |
| `ui.H3` | `*children, **props` | — |
| `ui.H4` | `*children, **props` | — |
| `ui.H5` | `*children, **props` | — |
| `ui.H6` | `*children, **props` | — |
| `ui.Header` | `*children, **props` | — |
| `ui.Hr` | `**props` | — |
| `ui.I` | `*children, **props` | — |
| `ui.Img` | `src="", alt="", **props` | — |
| `ui.Li` | `*children, **props` | — |
| `ui.Main` | `*children, **props` | — |
| `ui.Nav` | `*children, **props` | — |
| `ui.Ol` | `*children, **props` | — |
| `ui.P` | `*children, **props` | — |
| `ui.Pre` | `*children, **props` | — |
| `ui.S` | `*children, **props` | — |
| `ui.Section` | `*children, **props` | Sección con título y acciones. |
| `ui.Span` | `*children, **props` | — |
| `ui.Sub` | `*children, **props` | — |
| `ui.Summary` | `*children, **props` | — |
| `ui.Sup` | `*children, **props` | — |
| `ui.Template` | `*children, **props` | Envoltura sin etiqueta semántica útil para composición. |
| `ui.Time` | `*children, **props` | — |
| `ui.U` | `*children, **props` | — |
| `ui.Ul` | `*children, **props` | — |

