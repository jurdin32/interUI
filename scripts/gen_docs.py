"""Genera `docs/controles.md` desde el código, con un ejemplo por control.

Uso:
    python scripts/gen_docs.py          # regenera la documentación
    python scripts/gen_docs.py --check  # falla si la documentación está desfasada

Cada ejemplo es una **expresión Python evaluable** que devuelve un componente.
`tests/test_docs.py` evalúa y renderiza todos los ejemplos, así que la
documentación no puede quedar desactualizada sin que fallen las pruebas.
"""

from __future__ import annotations

import importlib
import inspect
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

OUTPUT = ROOT / "docs" / "controles.md"
ICON_OUTPUT = ROOT / "docs" / "iconos.md"

from interui.simple import RESERVED_ALIASES, snake_case  # noqa: E402  (tras ajustar sys.path)

GROUPS: list[tuple[str, str]] = [
    ("ventana y estructura", "interui.grid"),
    ("tipografía y texto", "interui.controls.typography"),
    ("botones y acciones", "interui.controls.buttons"),
    ("formularios", "interui.controls.inputs"),
    ("datos y tablas", "interui.controls.data"),
    ("retroalimentación", "interui.controls.feedback"),
    ("contenedores y superposiciones", "interui.controls.layout"),
    ("shell de aplicación, menús y barras", "interui.controls.shell"),
    ("navegación", "interui.controls.navigation"),
    ("gráficos", "interui.controls.charts"),
    ("medios", "interui.controls.media"),
    ("avanzados", "interui.controls.advanced"),
    ("iconos", "interui.icons"),
    ("etiquetas HTML", "interui.controls.tags"),
]

DESCRIPTIONS: dict[str, str] = {
    "Screen": "Raíz de la ventana: ocupa todo el alto y define el fondo del tema.",
    "Container": "Centra el contenido y limita el ancho máximo.",
    "Row": "Fila de la rejilla de 12 columnas.",
    "Col": "Columna responsive (`span`, `sm`, `md`, `lg`, `xl`, `xxl`).",
    "Stack": "Apila hijos en vertical u horizontal con separación uniforme.",
    "Grid": "Rejilla nativa de CSS (columnas por breakpoint).",
    "Center": "Centra el contenido en ambos ejes.",
    "Spacer": "Empuja el contenido en un flexbox.",
    "Divider": "Separador con etiqueta opcional.",
    "AspectRatio": "Mantiene una proporción fija.",
    "ScrollArea": "Área con scroll y altura máxima.",
    "Title": "Título principal con subtítulo.",
    "Heading": "Encabezado `h1`–`h6`.",
    "Text": "Texto con tamaño, tono y peso.",
    "Paragraph": "Párrafo con interlineado relajado.",
    "Muted": "Texto secundario atenuado.",
    "Lead": "Entradilla destacada.",
    "Small": "Nota de tamaño reducido.",
    "Strong": "Texto en negrita semántica.",
    "Em": "Texto en cursiva semántica.",
    "Mark": "Texto resaltado.",
    "Code": "Código en línea.",
    "CodeBlock": "Bloque de código con botón de copiar.",
    "Kbd": "Tecla de teclado.",
    "Label": "Etiqueta de campo.",
    "Link": "Enlace interno o externo.",
    "Badge": "Etiqueta compacta con variantes de color.",
    "Chip": "Etiqueta con botón de borrado.",
    "Blockquote": "Cita con autor opcional.",
    "Announcement": "Franja de anuncio a todo el ancho.",
    "IconGrid": "Catálogo buscable de los 200+ iconos incluidos; `on_pick` recibe el nombre.",
    "AppShell": (
        "Armazón completo: barra de título, cabecera/menús, barra lateral, contenido con "
        "scroll y barra de estado."
    ),
    "MenuBar": "Barra de menús de la ventana (`Archivo`, `Editar`…) con desplegables.",
    "MenuButton": "Botón que despliega un menú de acciones en cualquier punto de la interfaz.",
    "ContextMenu": "Envuelve contenido y abre un menú con el botón derecho.",
    "ContextItem": "Entrada de menú contextual (icono, atajo, peligro, deshabilitada).",
    "CommandBar": "Barra de comandos: buscador en vivo + acciones a la derecha.",
    "NotificationButton": "Campana con contador y panel de notificaciones.",
    "Button": "Botón con variantes, tamaños, iconos y estado de carga.",
    "IconButton": "Botón cuadrado solo con icono.",
    "ButtonGroup": "Botones pegados horizontal o verticalmente.",
    "CopyButton": "Copia un texto al portapapeles sin ir al servidor.",
    "Fab": "Botón flotante de acción.",
    "Spinner": "Indicador de carga animado.",
    "Input": "Campo de texto con etiqueta, ayuda, error e iconos.",
    "TextInput": "Alias de `Input` para texto.",
    "EmailInput": "Campo de correo.",
    "SearchInput": "Buscador con eventos en vivo.",
    "PasswordInput": "Contraseña con botón para mostrarla.",
    "NumberInput": "Campo numérico con `min`, `max`, `step`.",
    "Textarea": "Área de texto multilínea.",
    "Select": "Lista desplegable.",
    "MultiSelect": "Selección múltiple.",
    "Combobox": "Texto con sugerencias (`datalist`).",
    "Datalist": "Lista de sugerencias suelta.",
    "Checkbox": "Casilla con etiqueta.",
    "CheckboxGroup": "Grupo de casillas.",
    "Radio": "Opción de radio individual.",
    "RadioGroup": "Grupo de radios, en lista o tarjetas.",
    "Switch": "Interruptor de encendido/apagado.",
    "Slider": "Deslizador numérico.",
    "RangeSlider": "Rango con dos deslizadores.",
    "Stepper": "Contador con botones − / +.",
    "SegmentedControl": "Selector de segmentos.",
    "ToggleGroup": "Botones de alternancia.",
    "Rating": "Valoración por estrellas.",
    "TagInput": "Etiquetas con alta y baja.",
    "OtpInput": "Código de un solo uso.",
    "ColorInput": "Selector de color.",
    "FileInput": "Selector de archivos (se suben al proceso local).",
    "Dropzone": "Zona de arrastrar y soltar archivos.",
    "DateInput": "Selector de fecha.",
    "TimeInput": "Selector de hora.",
    "DateTimeInput": "Fecha y hora.",
    "MonthInput": "Selector de mes.",
    "WeekInput": "Selector de semana.",
    "DateRangeInput": "Rango de fechas.",
    "Form": "Formulario que envía todos los campos a Python.",
    "FormField": "Envuelve un control con etiqueta, ayuda y error.",
    "Fieldset": "Grupo de campos con leyenda.",
    "ValidationSummary": "Resumen de errores de validación.",
    "HiddenInput": "Campo oculto.",
    "Table": "Tabla estática.",
    "DataTable": "Tabla con orden, búsqueda, selección y paginación.",
    "ListGroup": "Lista agrupada.",
    "ListItem": "Elemento de lista con icono y meta.",
    "Tree": "Árbol jerárquico.",
    "TreeNode": "Nodo de árbol plegable.",
    "Timeline": "Línea de tiempo.",
    "TimelineItem": "Hito de la línea de tiempo.",
    "Stat": "Indicador con valor y variación.",
    "StatGrid": "Rejilla de indicadores.",
    "DescriptionList": "Lista de definiciones.",
    "DescriptionItem": "Término y definición.",
    "KeyValueGrid": "Pares clave/valor.",
    "JsonView": "Visualizador de JSON.",
    "LogView": "Visor de registros con niveles.",
    "EmptyState": "Estado vacío con acción.",
    "ProgressTable": "Tabla con barras de progreso.",
    "Alert": "Aviso con nivel y cierre.",
    "Callout": "Alias de `Alert`.",
    "Banner": "Franja de aviso a todo el ancho.",
    "Progress": "Barra de progreso determinada o indeterminada.",
    "ProgressRing": "Anillo de progreso.",
    "Meter": "Medidor con color según el valor.",
    "Skeleton": "Marcador de carga.",
    "LoadingOverlay": "Superpone un cargando sobre su contenido.",
    "StatusDot": "Punto de estado.",
    "InlineToast": "Aviso compacto en línea.",
    "Snackbar": "Aviso flotante con icono o imagen, acción y cierre opcional.",
    "ConfirmDialog": "Diálogo de confirmación gestionado en Python.",
    "Hint": "Texto de ayuda pequeño.",
    "Card": "Tarjeta con cabecera, cuerpo y pie.",
    "Panel": "Superficie con padding.",
    "Paper": "Hoja con sombra.",
    "Well": "Caja hundida para contenido secundario.",
    "Section": "Sección con título y acciones.",
    "Toolbar": "Barra de herramientas.",
    "PageHeader": "Cabecera de página con migas y acciones.",
    "Hero": "Bloque destacado con degradado.",
    "Footer": "Pie de página.",
    "Navbar": "Barra superior de navegación.",
    "Sidebar": "Barra lateral.",
    "SidebarItem": "Elemento de barra lateral.",
    "NavLink": "Enlace de navegación con estado activo.",
    "TitleBar": "Barra de título propia para ventanas sin marco.",
    "StatusBar": "Barra inferior de estado.",
    "Modal": "Diálogo modal; `.trigger()` crea el botón que lo abre.",
    "Drawer": "Panel lateral deslizante.",
    "Sheet": "Hoja inferior.",
    "Collapse": "Sección plegable en el cliente.",
    "Accordion": "Lista de secciones plegables.",
    "Splitter": "Dos paneles redimensionables.",
    "Tooltip": "Ayuda emergente al pasar el ratón.",
    "Popover": "Panel emergente anclado.",
    "Dropdown": "Botón con menú desplegable.",
    "Menu": "Contenedor de menú.",
    "MenuItem": "Entrada de menú.",
    "Tabs": "Pestañas; cambian en el cliente o en Python.",
    "TabBar": "Alias de `Tabs`.",
    "Breadcrumb": "Migas de pan.",
    "Pagination": "Paginación con eventos a Python.",
    "Steps": "Pasos de un asistente.",
    "CommandPalette": "Paleta de comandos con filtrado instantáneo.",
    "CommandItem": "Acción de la paleta.",
    "LineChart": "Gráfico de líneas.",
    "AreaChart": "Área con relleno.",
    "BarChart": "Barras verticales.",
    "ColumnChart": "Alias de `BarChart`.",
    "ScatterChart": "Dispersión de puntos.",
    "PieChart": "Gráfico circular.",
    "DonutChart": "Anillo con total.",
    "Sparkline": "Mini gráfico de tendencia.",
    "Gauge": "Arco de progreso.",
    "Legend": "Leyenda de series.",
    "ChartCard": "Tarjeta con gráfico.",
    "Image": "Imagen con proporción y ajuste.",
    "Figure": "Imagen con pie de foto.",
    "Avatar": "Avatar con iniciales o foto.",
    "AvatarGroup": "Avatares apilados.",
    "Video": "Reproductor de vídeo.",
    "Audio": "Reproductor de audio.",
    "Carousel": "Carrusel controlado por Python.",
    "Gallery": "Rejilla de imágenes.",
    "IconBadge": "Icono en una caja de color.",
    "Html": "HTML literal (no escapa nada).",
    "CodeEditor": "Editor de código con numeración.",
    "RichTextEditor": "Editor de texto enriquecido.",
    "Markdown": "Subconjunto de Markdown.",
    "Terminal": "Vista de terminal.",
    "Iframe": "Contenido incrustado aislado.",
    "Canvas": "Lienzo para dibujar con JS.",
    "KeyValueEditor": "Editor de pares clave/valor.",
    "Icon": "Icono SVG del set incluido (`ui.ICON_NAMES`).",
    "LinkButton": "Botón con apariencia de botón que navega a `href`.",
}

# Descripciones propias de las etiquetas HTML
TAG_DESCRIPTIONS: dict[str, str] = {
    # etiquetas HTML
    "A": "Enlace `<a>` con estilo de enlace.",
    "Article": "Contenedor semántico `<article>`.",
    "Aside": "Contenido lateral `<aside>`.",
    "B": "Negrita visual `<b>`.",
    "Br": "Salto de línea `<br>`.",
    "Details": "Sección desplegable nativa `<details>`.",
    "DetailsBlock": "Alias de `Details`.",
    "Div": "Caja genérica `<div>`.",
    "Figcaption": "Pie de figura.",
    "Figure": "Figura genérica.",
    "H1": "Encabezado `<h1>` con estilo.",
    "H2": "Encabezado `<h2>` con estilo.",
    "H3": "Encabezado `<h3>` con estilo.",
    "H4": "Encabezado `<h4>` con estilo.",
    "H5": "Encabezado `<h5>` con estilo.",
    "H6": "Encabezado `<h6>` con estilo.",
    "Header": "Cabecera semántica.",
    "Hr": "Línea separadora `<hr>`.",
    "I": "Cursiva visual `<i>`.",
    "Img": "Imagen `<img>` sin recorte.",
    "Li": "Elemento de lista `<li>`.",
    "Main": "Contenido principal (`flex-1`).",
    "Nav": "Contenedor de navegación.",
    "Ol": "Lista numerada `<ol>`.",
    "P": "Párrafo `<p>`.",
    "Pre": "Texto preformateado.",
    "S": "Texto tachado.",
    "Section": "Sección HTML (`ui.Section` es la versión con título).",
    "Span": "Texto en línea `<span>`.",
    "Sub": "Subíndice.",
    "Summary": "Encabezado de un `Details`.",
    "Sup": "Superíndice.",
    "Template": "Envoltura de composición sin semántica.",
    "Time": "Fecha/hora semántica.",
    "U": "Subrayado.",
    "Ul": "Lista con viñetas `<ul>`.",
}

# Un ejemplo por control: expresión evaluable que devuelve un componente.
SNIPPETS: dict[str, str] = {
    # -- ventana y estructura -------------------------------------------
    "Screen": 'ui.Screen(ui.Text("contenido de la ventana"), class_="p-6")',
    "Container": 'ui.Container(size="prose")(ui.Text("ancho limitado y centrado"))',
    "Row": 'ui.Row(ui.Col(span=6)(ui.Text("izquierda")), ui.Col(span=6)(ui.Text("derecha")))',
    "Col": 'ui.Row(ui.Col(span=12, md=6, lg=4)(ui.Text("12 → 6 → 4 columnas")))',
    "Stack": 'ui.Stack(ui.Text("uno"), ui.Text("dos"), direction="row", gap=3)',
    "Grid": 'ui.Grid(ui.Text("a"), ui.Text("b"), cols=1, md=2, gap=4)',
    "Center": 'ui.Center(ui.Text("centrado"), class_="h-40")',
    "Spacer": 'ui.Stack(ui.Text("izq"), ui.Spacer(), ui.Text("der"), direction="row")',
    "Divider": 'ui.Divider("o")',
    "AspectRatio": 'ui.AspectRatio(ui.Center(ui.Text("16:9")), ratio="video")',
    "ScrollArea": 'ui.ScrollArea(ui.Text("mucho contenido"), max_h="48")',
    # -- tipografía ------------------------------------------------------
    "Title": 'ui.Title("Mi aplicación", subtitle="Subtítulo descriptivo")',
    "Heading": 'ui.Heading("Sección", level=2)',
    "Text": 'ui.Text("Texto normal", size=ui.size.lg, tone=ui.tone.muted, weight="medium")',
    "Paragraph": 'ui.Paragraph("Un párrafo con interlineado relajado para leer cómodo.")',
    "Muted": 'ui.Muted("Texto secundario")',
    "Lead": 'ui.Lead("Entradilla que resume el contenido.")',
    "Small": 'ui.Small("nota al pie")',
    "Strong": 'ui.Strong("importante")',
    "Em": 'ui.Em("énfasis")',
    "Mark": 'ui.Mark("resaltado")',
    "Code": 'ui.Code("pip install interui")',
    "CodeBlock": 'ui.CodeBlock("print(\'hola\')", language="python", filename="demo.py")',
    "Kbd": 'ui.Stack(ui.Kbd("Ctrl"), ui.Kbd("K"), direction="row", gap=1)',
    "Label": 'ui.Label("Correo electrónico", for_="campo", required=True)',
    "Link": 'ui.Link("Documentación", href="https://example.com")',
    "Badge": 'ui.Badge("nuevo", variant=ui.variant.success, dot=True)',
    "Chip": 'ui.Chip("python", variant=ui.variant.primary)',
    "Blockquote": 'ui.Blockquote("La simplicidad es la máxima sofisticación.", cite="Leonardo")',
    "Announcement": 'ui.Announcement("Nueva versión disponible")',
    "IconGrid": 'ui.IconGrid(columns=8)',
    "AppShell": (
        'ui.AppShell(ui.Container(pad=ui.pad.py_6)(ui.Text("contenido")), '
        'title_bar=ui.TitleBar("Mi app", icon=ui.icons.layers), '
        'header=ui.MenuBar({"Archivo": [ui.ContextItem("Salir", icon=ui.icons.power)]}, brand="Mi app"), '
        'sidebar=ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True)), '
        'status=ui.StatusBar(ui.Text("Listo")))'
    ),
    "MenuBar": (
        'ui.MenuBar({"Archivo": [ui.ContextItem("Nuevo", icon=ui.icons.plus, shortcut="Ctrl+N"), '
        '"-", ui.ContextItem("Salir", icon=ui.icons.power, danger=True)], '
        '"Ver": [ui.ContextItem("Tema oscuro", icon=ui.icons.moon)]}, brand="Mi app")'
    ),
    "MenuButton": (
        'ui.MenuButton("Acciones", icon=ui.icons.settings, items=[ui.ContextItem("Editar", icon=ui.icons.edit), '
        'ui.ContextItem("Eliminar", icon=ui.icons.trash, danger=True)])'
    ),
    "ContextMenu": (
        'ui.ContextMenu(ui.ContextItem("Abrir", icon=ui.icons.folder), "-", '
        'ui.ContextItem("Borrar", icon=ui.icons.trash, danger=True))(ui.Text("Clic derecho aquí"))'
    ),
    "ContextItem": 'ui.ContextItem("Abrir", icon=ui.icons.folder, shortcut="Ctrl+O", on_click=lambda: None)',
    "CommandBar": (
        'ui.CommandBar(ui.Button("Nuevo", icon=ui.icons.plus, variant=ui.variant.primary), search_placeholder="Buscar…")'
    ),
    "NotificationButton": (
        'ui.NotificationButton(3, items=[ui.ContextItem("Nueva tarea asignada", icon=ui.icons.check)])'
    ),
    # -- botones ---------------------------------------------------------
    "Button": 'ui.Button("Guardar", icon=ui.icons.check, variant=ui.variant.primary, on_click=lambda: None)',
    "IconButton": 'ui.IconButton("settings", label="Ajustes", variant=ui.variant.outline)',
    "ButtonGroup": 'ui.ButtonGroup(ui.Button("Día", variant=ui.variant.outline), ui.Button("Semana", variant=ui.variant.outline))',
    "CopyButton": 'ui.CopyButton("texto que se copia")',
    "Fab": 'ui.Fab("plus", label="Nuevo")',
    "Spinner": 'ui.Spinner(size=5)',
    "LinkButton": 'ui.Button("Ir a ajustes", href="/ajustes", variant=ui.variant.outline)',
    # -- formularios -----------------------------------------------------
    "Input": 'ui.Input("", label="Nombre", placeholder="Ana Ruiz", icon=ui.icons.user, required=True)',
    "TextInput": 'ui.TextInput("valor inicial", label="Texto")',
    "EmailInput": 'ui.EmailInput("", label="Correo", help_text="No lo compartiremos")',
    "SearchInput": 'ui.SearchInput("", label="Buscar", live=True, on_input=lambda e: None)',
    "PasswordInput": 'ui.PasswordInput("", label="Contraseña")',
    "NumberInput": 'ui.NumberInput(3, label="Cantidad", min=0, max=99)',
    "Textarea": 'ui.Textarea("", label="Notas", rows=4, placeholder="Escribe aquí…")',
    "Select": 'ui.Select([("es", "Español"), ("en", "English")], label="Idioma", value="es")',
    "MultiSelect": 'ui.MultiSelect([("a", "A"), ("b", "B"), ("c", "C")], values=["a"], label="Opciones")',
    "Combobox": 'ui.Combobox("", items=["Madrid", "Barcelona"], label="Ciudad")',
    "Datalist": 'ui.Datalist(["uno", "dos"])',
    "Checkbox": 'ui.Checkbox("Acepto los términos", checked=True)',
    "CheckboxGroup": 'ui.CheckboxGroup(["Correo", "Push", "SMS"], values=["Push"], label="Canales")',
    "Radio": 'ui.Radio("Tarjeta", value="card", name="pago", checked=True)',
    "RadioGroup": 'ui.RadioGroup(["Tarjeta", "Bizum"], value="Bizum", label="Pago")',
    "Switch": 'ui.Switch("Recordarme", checked=True, help_text="En este equipo")',
    "Slider": 'ui.Slider(64, label="Volumen", unit=" %")',
    "RangeSlider": 'ui.RangeSlider(20, 80, label="Precio")',
    "Stepper": 'ui.Stepper(2, label="Pasajeros", min=0, max=9)',
    "SegmentedControl": 'ui.SegmentedControl([("d", "Día"), ("s", "Semana")], value="s", label="Vista")',
    "ToggleGroup": 'ui.ToggleGroup([("b", "Negrita"), ("i", "Cursiva")], values=["b"])',
    "Rating": 'ui.Rating(4, label="Valoración", on_change=lambda e: None)',
    "TagInput": 'ui.TagInput(["python"], label="Etiquetas")',
    "OtpInput": 'ui.OtpInput(6, label="Código de verificación")',
    "ColorInput": 'ui.ColorInput("#4f46e5", label="Color de marca")',
    "FileInput": 'ui.FileInput(label="Adjuntar", accept=".pdf,.txt", multiple=True)',
    "Dropzone": 'ui.Dropzone(label="Suelta archivos aquí", accept=".csv")',
    "DateInput": 'ui.DateInput("2026-01-31", label="Fecha")',
    "TimeInput": 'ui.TimeInput("09:30", label="Hora")',
    "DateTimeInput": 'ui.DateTimeInput("2026-01-31T09:30", label="Fecha y hora")',
    "MonthInput": 'ui.MonthInput("2026-01", label="Mes")',
    "WeekInput": 'ui.WeekInput("2026-W05", label="Semana")',
    "DateRangeInput": 'ui.DateRangeInput("2026-01-01", "2026-01-31", label="Periodo")',
    "Form": 'ui.Form(ui.Input("", label="Nombre"), ui.Button("Enviar", submit=True), on_submit=lambda e: None)',
    "FormField": 'ui.FormField(ui.Input(""), label="Nombre", help_text="Como en tu DNI", required=True)',
    "Fieldset": 'ui.Fieldset(ui.Input("", label="Calle"), legend="Dirección")',
    "ValidationSummary": 'ui.ValidationSummary(["El nombre es obligatorio", "Correo inválido"])',
    "HiddenInput": 'ui.HiddenInput("abc123", name="token")',
    # -- datos -----------------------------------------------------------
    "Table": 'ui.Table(headers=["Nombre", "Rol"], rows=[["Ana", "Admin"], ["Luis", "Editor"]], striped=True)',
    "DataTable": 'ui.DataTable(columns=[{"key": "nombre", "label": "Nombre", "sortable": True}], rows=[{"id": 1, "nombre": "Ana"}], total=1, page=1, searchable=True)',
    "ListGroup": 'ui.ListGroup(ui.ListItem(title="Reunión", subtitle="10:00", icon=ui.icons.users, meta="3"))',
    "ListItem": 'ui.ListItem(title="Informe", subtitle="Ayer", icon=ui.icons.file, meta="PDF")',
    "Tree": 'ui.Tree(ui.TreeNode("src", icon=ui.icons.folder, expanded=True, children=[ui.TreeNode("app.py", icon=ui.icons.file)]))',
    "TreeNode": 'ui.TreeNode("src", icon=ui.icons.folder, expanded=True)',
    "Timeline": 'ui.Timeline(ui.TimelineItem("Pedido creado", time="09:12", icon=ui.icons.check))',
    "TimelineItem": 'ui.TimelineItem("Pago confirmado", time="09:15", tone=ui.tone.success, last=True)',
    "Stat": 'ui.Stat("Ingresos", "24.980 €", delta="+12 %", icon=ui.icons.chart)',
    "StatGrid": 'ui.StatGrid(ui.Stat("A", "1"), ui.Stat("B", "2"), columns=2)',
    "DescriptionList": 'ui.DescriptionList(ui.DescriptionItem("Versión", "0.1.0"))',
    "DescriptionItem": 'ui.DescriptionItem("Licencia", "MIT")',
    "KeyValueGrid": 'ui.KeyValueGrid({"Nombre": "interui", "Versión": "0.1.0"})',
    "JsonView": 'ui.JsonView({"id": 42, "tags": ["a", "b"], "activo": True})',
    "LogView": 'ui.LogView([{"level": "info", "time": "09:12", "message": "inicio"}], title="app.log")',
    "EmptyState": 'ui.EmptyState(title="Sin proyectos", description="Crea el primero para empezar.", icon=ui.icons.inbox)',
    "ProgressTable": 'ui.ProgressTable([{"label": "Diseño", "value": 100}, {"label": "Código", "value": 60}])',
    # -- retroalimentación ----------------------------------------------
    "Alert": 'ui.Alert("Todo correcto.", level="success", title="Listo", dismissible=True)',
    "Callout": 'ui.Callout("Revisa la configuración.", level="warning")',
    "Banner": 'ui.Banner("Mantenimiento programado", level="warning")',
    "Progress": 'ui.Progress(72, label="Subiendo", show_value=True)',
    "ProgressRing": 'ui.ProgressRing(72, label="72 %")',
    "Meter": 'ui.Meter(82, label="Memoria")',
    "Skeleton": 'ui.Skeleton(lines=3, height="3")',
    "LoadingOverlay": 'ui.LoadingOverlay(ui.Text("contenido"), message="Cargando…")',
    "StatusDot": 'ui.StatusDot("Operativo", tone=ui.tone.success, pulse=True)',
    "InlineToast": 'ui.InlineToast("Guardado correctamente", level="success")',
    "Snackbar": (
        'ui.Snackbar("Proyecto archivado", title="Hecho", icon=ui.icons.check, '
        'action=("Deshacer", lambda e: None), variant=ui.variant.success)'
    ),
    "ConfirmDialog": 'ui.ConfirmDialog("Esta acción no se puede deshacer.", title="¿Eliminar?", dialog_id="confirmar")',
    "Hint": 'ui.Hint("Se guarda automáticamente")',
    # -- contenedores ----------------------------------------------------
    "Card": 'ui.Card(title="Tarjeta", description="Con cabecera", icon=ui.icons.layers)(ui.Text("cuerpo"))',
    "Panel": 'ui.Panel(ui.Text("contenido"), tone=ui.tone.muted)',
    "Paper": 'ui.Paper(ui.Text("hoja con sombra"))',
    "Well": 'ui.Well(ui.Text("bloque hundido"))',
    "Section": 'ui.Section(ui.Text("contenido"), title="Sección", subtitle="Con subtítulo")',
    "Toolbar": 'ui.Toolbar(ui.Button("Nuevo", size=ui.size.sm), ui.Button("Filtrar", variant=ui.variant.outline, size=ui.size.sm))',
    "PageHeader": 'ui.PageHeader("Proyectos", subtitle="12 activos", actions=ui.Button("Nuevo", icon=ui.icons.plus))',
    "Hero": 'ui.Hero(ui.Title("Bienvenido"), eyebrow="Novedad")',
    "Footer": 'ui.Footer(ui.Text("© 2026 interui"))',
    "Navbar": 'ui.Navbar(ui.NavLink("Inicio", href="/", active=True), brand="Mi app")',
    "Sidebar": 'ui.Sidebar(ui.SidebarItem("Panel", icon=ui.icons.grid, active=True), title="Navegación")',
    "SidebarItem": 'ui.SidebarItem("Informes", icon=ui.icons.chart, badge=2)',
    "NavLink": 'ui.NavLink("Equipo", href="/equipo", icon=ui.icons.users)',
    "TitleBar": 'ui.TitleBar("Mi app", icon=ui.icons.layers)',
    "StatusBar": 'ui.StatusBar(ui.Text("Listo"), ui.Badge("local", variant=ui.variant.success))',
    "Modal": 'ui.Modal(ui.Text("Contenido del modal"), dialog_id="alta", title="Nueva ficha")',
    "Drawer": 'ui.Drawer(ui.Text("Panel lateral"), drawer_id="detalle", title="Detalle")',
    "Sheet": 'ui.Sheet(ui.Text("Hoja inferior"), sheet_id="hoja", title="Opciones")',
    "Collapse": 'ui.Collapse(ui.Text("contenido oculto"), title="Más información")',
    "Accordion": 'ui.Accordion([("Uno", ui.Text("contenido 1")), ("Dos", ui.Text("contenido 2"))])',
    "Splitter": 'ui.Splitter(ui.Text("izquierda"), ui.Text("derecha"))',
    "Tooltip": 'ui.Tooltip(ui.Button("?", variant=ui.variant.outline), content="Ayuda contextual")',
    "Popover": 'ui.Popover(ui.Text("detalle"), trigger="Ver más", title="Información")',
    "Dropdown": 'ui.Dropdown(ui.MenuItem("Editar", icon=ui.icons.edit), ui.MenuItem("Borrar", danger=True), label="Acciones")',
    "Menu": 'ui.Menu(ui.MenuItem("Inicio", icon=ui.icons.home), ui.MenuItem("Ajustes", icon=ui.icons.settings))',
    "MenuItem": 'ui.MenuItem("Duplicar", icon=ui.icons.copy, shortcut="⌘D")',
    # -- navegación ------------------------------------------------------
    "Tabs": 'ui.Tabs([("a", "Uno", ui.Text("panel A")), ("b", "Dos", ui.Text("panel B"))], active="a")',
    "TabBar": 'ui.Tabs([("a", "Uno", ui.Text("A"))], active="a", variant=ui.variant.pills)',
    "Breadcrumb": 'ui.Breadcrumb([("/", "Inicio"), ("/proyectos", "Proyectos"), ("x", "interui")])',
    "Pagination": 'ui.Pagination(3, pages=12, on_page=lambda e: None)',
    "Steps": 'ui.Steps(["Cuenta", "Perfil", "Pago"], current=1)',
    "CommandPalette": 'ui.CommandPalette(ui.CommandItem("Ir al inicio", hint="G H", icon=ui.icons.home))',
    "CommandItem": 'ui.CommandItem("Nuevo proyecto", hint="N", icon=ui.icons.plus)',
    # -- gráficos --------------------------------------------------------
    "LineChart": 'ui.LineChart([[3, 6, 4, 9, 7]], labels=["L", "M", "X", "J", "V"])',
    "AreaChart": 'ui.AreaChart({"2025": [8, 14, 18, 16, 25]}, labels=["Ene", "Feb", "Mar", "Abr", "May"])',
    "BarChart": 'ui.BarChart([[18, 26, 12, 30]], labels=["L", "M", "X", "J"], show_values=True)',
    "ColumnChart": 'ui.ColumnChart([[5, 9, 3]], labels=["a", "b", "c"])',
    "ScatterChart": 'ui.ScatterChart([[3, 7, 2, 9]])',
    "PieChart": 'ui.PieChart({"Directo": 42, "Social": 28, "Búsqueda": 30})',
    "DonutChart": 'ui.DonutChart({"A": 60, "B": 40})',
    "Sparkline": 'ui.Sparkline([4, 8, 6, 12, 9, 14])',
    "Gauge": 'ui.Gauge(64, label="CPU")',
    "Legend": 'ui.Legend(["Ventas", "Costes"])',
    "ChartCard": 'ui.ChartCard(ui.Sparkline([1, 3, 2, 5]), title="Tendencia", subtitle="Últimos 7 días")',
    # -- medios ----------------------------------------------------------
    "Image": 'ui.Image("https://picsum.photos/seed/a/600/400", alt="Paisaje", ratio="video")',
    "Figure": 'ui.Figure(ui.Image("foto.png", alt="Foto"), caption="Figura 1")',
    "Avatar": 'ui.Avatar(name="Ana Ruiz", size=ui.size.lg, status="online")',
    "AvatarGroup": 'ui.AvatarGroup(ui.Avatar(name="Ana Ruiz"), ui.Avatar(name="Luis Paz"), max_items=2)',
    "Video": 'ui.Video("https://ejemplo.com/video.mp4", poster="portada.jpg")',
    "Audio": 'ui.Audio("https://ejemplo.com/audio.mp3")',
    "Carousel": 'ui.Carousel([ui.Text("diapositiva 1"), ui.Text("diapositiva 2")], index=0)',
    "Gallery": 'ui.Gallery(ui.Image("a.png", alt="A"), ui.Image("b.png", alt="B"), columns=2)',
    "IconBadge": 'ui.IconBadge("zap", tone=ui.tone.primary)',
    # -- avanzados -------------------------------------------------------
    "Html": 'ui.Html("<b>HTML literal</b>")',
    "CodeEditor": 'ui.CodeEditor("print(1)", language="python", max_h="64")',
    "RichTextEditor": 'ui.RichTextEditor("<b>Texto</b> editable", min_h="32")',
    "Markdown": 'ui.Markdown("# Título\\n\\n- uno\\n- dos\\n\\n**negrita** y `código`")',
    "Terminal": 'ui.Terminal(["pip install interui", "python app.py"], title="zsh")',
    "Iframe": 'ui.Iframe(srcdoc="<h1>Hola</h1>", height="60")',
    "Canvas": 'ui.Canvas(width=400, height=200)',
    "KeyValueEditor": 'ui.KeyValueEditor({"API_URL": "https://api.ejemplo.com"})',
    # -- iconos ----------------------------------------------------------
    "Icon": 'ui.Icon(ui.icons.check, size=6, color=ui.colors.emerald_600)',
}

# Etiquetas HTML: el ejemplo se genera a partir de la firma y un contenido típico.
TAG_CONTENT: dict[str, str] = {
    "A": '"Enlace", href="/ruta"',
    "Article": '"Contenido del artículo"',
    "Aside": '"Nota lateral"',
    "B": '"negrita"',
    "Br": "",
    "Details": 'ui.Summary("Más detalles"), ui.Text("contenido")',
    "DetailsBlock": 'ui.Summary("Detalles"), ui.Text("contenido")',
    "Div": '"contenido"',
    "Figcaption": '"Pie de figura"',
    "Figure": "ui.Img(\"foto.png\", alt=\"Foto\")",
    "H1": '"Título 1"',
    "H2": '"Título 2"',
    "H3": '"Título 3"',
    "H4": '"Título 4"',
    "H5": '"Título 5"',
    "H6": '"Título 6"',
    "Header": '"cabecera"',
    "Hr": "",
    "I": '"cursiva"',
    "Img": '"foto.png", alt="Foto"',
    "Li": '"elemento"',
    "Main": '"contenido principal"',
    "Nav": '"navegación"',
    "Ol": 'ui.Li("primero"), ui.Li("segundo")',
    "P": '"párrafo"',
    "Pre": '"texto preformateado"',
    "S": '"tachado"',
    "Section": '"sección"',
    "Span": '"texto en línea"',
    "Sub": '"sub"',
    "Summary": '"Resumen"',
    "Sup": '"sup"',
    "Template": '"contenido"',
    "Time": '"2026-01-31", datetime="2026-01-31"',
    "U": '"subrayado"',
    "Ul": 'ui.Li("uno"), ui.Li("dos")',
}


def auto_snippet(name: str) -> str:
    body = TAG_CONTENT.get(name, "")
    return f"ui.{name}({body})" if body else f"ui.{name}()"


def controls_of(module_name: str) -> list[tuple[str, Any]]:
    from interui.base import Component

    module = importlib.import_module(module_name)
    out = []
    for name in getattr(module, "__all__", []):
        obj = getattr(module, name, None)
        # Solo controles: los tokens de diseño (IconName, Word…) no se documentan aquí.
        if inspect.isclass(obj) and issubclass(obj, Component):
            out.append((name, obj))
    return sorted(set(out), key=lambda item: item[0])


#: Parámetros cuyo valor por defecto es un token de ``interui.theme``/``icons``.
TOKEN_PARAMS = {
    "icon": ("icons",),
    "variant": ("variant", "tone"),
    "tone": ("tone",),
    "size": ("size",),
    "layer": ("layer",),
    "sidebar_position": ("side",),
}


def _token_text(name: str, value: str) -> str | None:
    """Devuelve ``namespace.valor`` si el texto por defecto es un token válido."""
    import interui as ui

    for namespace in TOKEN_PARAMS.get(name, ()):
        target = getattr(ui, namespace, None)
        if target is None:
            continue
        for candidate in (value.replace("-", "_"), value):
            if isinstance(candidate, str) and hasattr(target, candidate):
                return f"{namespace}.{candidate}"
    return None


def signature_of(cls: Any) -> str:
    try:
        signature = inspect.signature(cls.__init__)
    except (TypeError, ValueError):  # pragma: no cover
        return ""
    parts = []
    for name, param in signature.parameters.items():
        if name in ("self", "props"):
            continue
        if param.kind is param.VAR_POSITIONAL:
            parts.append("*children")
        elif param.kind is param.VAR_KEYWORD:
            parts.append("**props")
        else:
            text = name
            if param.default is not param.empty:
                default = param.default
                if isinstance(default, str):
                    token = _token_text(name, default)
                    text += f"={token}" if token else f'="{default}"'
                elif default is None or isinstance(default, (int, float, bool)):
                    text += f"={default}"
                else:
                    text += "=…"
            parts.append(text)
    return ", ".join(parts)


def description_for(module_name: str, name: str) -> str:
    """Descripción del control, distinguiendo homónimos entre módulos.

    ``Figure`` existe en medios (imagen con pie) y en etiquetas HTML; ``Section``
    en contenedores (con título) y como etiqueta. Cada uno tiene su texto.
    """
    if module_name.endswith(".tags"):
        return TAG_DESCRIPTIONS.get(name, "")
    return DESCRIPTIONS.get(name, "")


def snippet_for(name: str) -> str:
    return SNIPPETS.get(name) or auto_snippet(name)


HEADER = """# Referencia de controles de interUI

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
| `class_` | `str` | Escape: clases CSS extra; sustituyen a las del control cuando chocan. |
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
"""


def build_markdown() -> str:
    lines = [HEADER]
    for title, module_name in GROUPS:
        lines.append(f"\n## {title.capitalize()}\n")
        for name, cls in controls_of(module_name):
            description = description_for(module_name, name) or (inspect.getdoc(cls) or "").split("\n")[0]
            alias = snake_case(name)
            lines.append(f"### `ui.{name}`\n")
            if alias != name and alias not in RESERVED_ALIASES:
                lines.append(f"Alias en minúsculas: `ui.{alias}`\n")
            if description:
                lines.append(f"{description.strip()}\n")
            signature = signature_of(cls)
            if signature:
                lines.append("```text")
                lines.append(f"ui.{name}({signature})")
                lines.append("```\n")
            lines.append("```python")
            lines.append(snippet_for(name))
            lines.append("```\n")
    return "\n".join(lines).rstrip() + "\n"


ICON_HEADER = """# Catálogo de iconos

interUI incluye su propio set de iconos vectoriales (trazo 24×24, `stroke-width`
1.8): no depende de ninguna librería externa ni de la red, así que funciona
igual en macOS, Windows y Linux, dentro del ejecutable empaquetado.

Cada icono tiene su nombre con puntos: `icons.car`, `icons.edit`,
`icons.chevron_down`. Los guiones de las utilidades CSS se escriben con `_`.

```python
import interui as ui
from interui import icons

icons.car                     # el nombre: sirve en icon=…
ui.Icon(icons.car, size=6)    # el control
icons.car(size=6, stroke=2)   # el control con opciones
ui.Card(icons.edit, "Editar") # como hijo se dibuja el icono
icons.close                   # alias: close→x, delete→trash, exit→power
ui.icon_grid(columns=10, searchable=True)   # galería navegable
```

Un nombre inexistente falla al instante (`AttributeError` con sugerencias); si el
nombre llega en una variable, `icons("car")`.

Los nombres desconocidos pasados a `ui.Icon(...)` no rompen la interfaz: se dibuja
un icono de ayuda.

> Este archivo se genera desde el código con `python scripts/gen_docs.py`.
"""


def build_icon_markdown() -> str:
    from interui.icons import ICON_NAMES

    lines = [
        ICON_HEADER,
        f"\n{len(ICON_NAMES)} iconos disponibles.\n",
        "\n## Lista de nombres\n",
    ]
    columnas = 4
    filas = -(-len(ICON_NAMES) // columnas)
    lines.append("| " + " | ".join(["Nombre"] * columnas) + " |")
    lines.append("|" + "|".join(["---"] * columnas) + "|")
    for fila in range(filas):
        celdas = []
        for columna in range(columnas):
            index = columna * filas + fila
            celdas.append(f"`{ICON_NAMES[index]}`" if index < len(ICON_NAMES) else "")
        lines.append("| " + " | ".join(celdas) + " |")
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    markdown = build_markdown()
    icons_markdown = build_icon_markdown()
    if "--check" in args:
        stale = []
        for path, content in ((OUTPUT, markdown), (ICON_OUTPUT, icons_markdown)):
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != content:
                stale.append(str(path.relative_to(ROOT)))
        if stale:
            print("Documentación desactualizada: ejecuta python scripts/gen_docs.py")
            for name in stale:
                print(f"  - {name}")
            return 1
        print("docs/controles.md y docs/iconos.md están al día")
        return 0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(markdown, encoding="utf-8")
    ICON_OUTPUT.write_text(icons_markdown, encoding="utf-8")
    total = sum(len(controls_of(module)) for _title, module in GROUPS)
    print(f"{OUTPUT.relative_to(ROOT)} regenerado: {total} controles documentados")
    print(f"{ICON_OUTPUT.relative_to(ROOT)} regenerado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
