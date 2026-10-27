"""Catálogo completo de controles de interui.

    python examples/03_catalog.py

Cada sección muestra el control y, debajo, la llamada de Python que lo genera.
"""

from __future__ import annotations

from typing import Any, Callable

import interui as ui

app = ui.App("Catálogo interui", width=1280, height=860)


def demo(component: Any, code: str) -> ui.Component:
    return ui.Card(class_="h-full")(
        component,
        ui.CodeBlock(code.strip(), language="python", max_h="64"),
    )


def section_basics() -> ui.Component:
    return ui.Stack(
        ui.Section(title="Tipografía")(
            ui.Row(
                ui.Col(span=12, lg=6)(
                    demo(
                        ui.Stack(
                            ui.Title("Encabezado principal", subtitle="Con subtítulo descriptivo"),
                            ui.Text("Texto normal con contenido del framework.", size="base"),
                            ui.Paragraph("Párrafo con interlineado relajado para lectura larga."),
                            ui.Lead("Texto de entrada, algo más grande y atenuado."),
                            ui.Muted("Texto secundario en gris."),
                            ui.Stack(
                                ui.Badge("neutral"),
                                ui.Badge("primary", variant="primary"),
                                ui.Badge("success", variant="success", dot=True),
                                ui.Badge("warning", variant="warning"),
                                ui.Badge("danger", variant="danger"),
                                ui.Badge("info", variant="info", icon="zap"),
                                gap=2,
                                direction="row",
                                wrap=True,
                            ),
                            ui.Stack(
                                ui.Kbd("Ctrl"), ui.Kbd("K"), ui.Text("abre la paleta"),
                                gap=2, direction="row", align="center",
                            ),
                            ui.Blockquote("La simplicidad es la máxima sofisticación.", cite="Leonardo"),
                            gap=3,
                        ),
                        """
Title("Encabezado principal", subtitle="...")
Text("Texto normal", size="base")
Lead("Texto de entrada")
Badge("success", variant="success", dot=True)
Kbd("Ctrl") + Text("abre la paleta")
Blockquote("...", cite="Leonardo")
""",
                    )
                ),
                ui.Col(span=12, lg=6)(
                    demo(
                        ui.Stack(
                            ui.Card(
                                title="Tarjeta con icono",
                                description="Cabecera, cuerpo y pie",
                                icon="layers",
                                actions=[("Ver", None, "ghost")],
                                footer=ui.Badge("actualizado hace 2 min", variant="info"),
                            )(
                                ui.Text("Las tarjetas agrupan contenido relacionado."),
                                ui.Progress(72, label="Uso del plan", show_value=True),
                            ),
                            ui.StatGrid(
                                ui.Stat("Ingresos", "24.980 €", delta="+12,4 %", icon="chart"),
                                ui.Stat("Usuarios", "1.284", delta="-2,1 %", positive=False, icon="users"),
                                columns=2,
                            ),
                            ui.Hint("Pasa el ratón por los iconos para ver la ayuda."),
                            gap=3,
                        ),
                        """
Card(title="Tarjeta", description="...", icon="layers",
     footer=Badge("hace 2 min"))(Text("..."))

StatGrid(
    Stat("Ingresos", "24.980 €", delta="+12,4 %"),
    Stat("Usuarios", "1.284", positive=False),
    columns=2,
)
""",
                    )
                ),
            )
        ),
        ui.Section(title="Iconos", subtitle="Set incluido, sin dependencias")(
            ui.Card()(
                ui.Stack(
                    *[
                        ui.Stack(
                            ui.Icon(name, size=5, class_="text-slate-500 dark:text-slate-300"),
                            ui.Small(name),
                            gap=1,
                            align="center",
                        )
                        for name in list(ui.ICON_NAMES)[:24]
                    ],
                    direction="row",
                    wrap=True,
                    gap=5,
                ),
                ui.Muted(f"{len(ui.ICON_NAMES)} iconos disponibles: ui.Icon('check', size=5)"),
            )
        ),
    )


def section_buttons() -> ui.Component:
    return ui.Stack(
        ui.Section(title="Variantes")(
            ui.Card()(
                ui.Stack(
                    ui.Button("Primario", variant="primary"),
                    ui.Button("Secundario", variant="secondary"),
                    ui.Button("Contorno", variant="outline"),
                    ui.Button("Fantasma", variant="ghost"),
                    ui.Button("Suave", variant="soft"),
                    ui.Button("Éxito", variant="success"),
                    ui.Button("Aviso", variant="warning"),
                    ui.Button("Peligro", variant="danger"),
                    direction="row", wrap=True, gap=2,
                ),
                ui.Divider("tamaños"),
                ui.Stack(
                    ui.Button("xs", size="xs"),
                    ui.Button("sm", size="sm"),
                    ui.Button("md", size="md"),
                    ui.Button("lg", size="lg"),
                    ui.Button("xl", size="xl"),
                    direction="row", wrap=True, gap=2, align="center",
                ),
                ui.Divider("estados"),
                ui.Stack(
                    ui.Button("Cargando", loading=True),
                    ui.Button("Deshabilitado", disabled=True),
                    ui.Button("Con icono", icon="download"),
                    ui.Button("Icono final", icon_right="arrow-right", variant="outline"),
                    ui.Button("Píldora", pill=True, variant="soft"),
                    ui.Button("Enlace", variant="link"),
                    direction="row", wrap=True, gap=2,
                ),
                ui.Divider("iconos y grupos"),
                ui.Stack(
                    ui.IconButton("settings", label="Ajustes"),
                    ui.IconButton("trash", label="Borrar", variant="ghost"),
                    ui.IconButton("bell", label="Avisos", variant="outline"),
                    ui.CopyButton("texto copiado"),
                    ui.ButtonGroup(
                        ui.Button("Día", variant="outline", size="sm"),
                        ui.Button("Semana", variant="outline", size="sm"),
                        ui.Button("Mes", variant="outline", size="sm"),
                    ),
                    direction="row", wrap=True, gap=2, align="center",
                ),
            )
        ),
    )


def section_forms() -> ui.Component:
    name = app.state("form_name", "")
    bio = app.state("form_bio", "")
    remember = app.state("form_remember", True)

    return ui.Row(
        ui.Col(span=12, lg=6)(
            ui.Card(title="Entradas de texto")(
                ui.Input(name.get(), label="Nombre", placeholder="Ana Ruiz", icon="user",
                         required=True, on_input=lambda e: name.set(e.text)),
                ui.EmailInput("", label="Correo", help_text="Nunca compartiremos tu dirección."),
                ui.PasswordInput("", label="Contraseña"),
                ui.SearchInput("", label="Búsqueda", live=True),
                ui.NumberInput(3, label="Cantidad", min=0, max=99),
                ui.Textarea(bio.get(), label="Biografía", rows=3,
                            placeholder="Cuéntanos algo…",
                            on_input=lambda e: bio.set(e.text)),
                ui.Hint(f"Nombre escrito: {name.get() or '—'}")
            ),
        ),
        ui.Col(span=12, lg=6)(
            ui.Card(title="Selección")(
                ui.Select(
                    [("es", "Español"), ("en", "English"), ("fr", "Français")],
                    label="Idioma", value="es", placeholder="Elige idioma",
                ),
                ui.MultiSelect(
                    [("a", "Opción A"), ("b", "Opción B"), ("c", "Opción C")],
                    values=["a"], label="Múltiple",
                ),
                ui.Combobox("", items=["Madrid", "Barcelona", "Valencia"], label="Ciudad con sugerencias"),
                ui.SegmentedControl(
                    [("day", "Día"), ("week", "Semana"), ("month", "Mes")],
                    value="week", label="Vista", full_width=True,
                ),
                ui.ToggleGroup(
                    [("b", "Negrita"), ("i", "Cursiva"), ("u", "Subrayado")],
                    values=["b"],
                ),
                ui.Switch("Recordarme", checked=remember.get(),
                          on_change=lambda e: remember.set(bool(e.checked))),
            ),
        ),
        ui.Col(span=12)(
            ui.Card(title="Controles especiales")(
                ui.Row(
                    ui.Col(span=12, md=6, lg=4)(
                        ui.Stack(
                            ui.Checkbox("Acepto los términos", checked=True),
                            ui.Checkbox("Suscripción al boletín"),
                            ui.CheckboxGroup(["Correo", "Push", "SMS"], values=["Push"], label="Canales"),
                            gap=2,
                        )
                    ),
                    ui.Col(span=12, md=6, lg=4)(
                        ui.Stack(
                            ui.RadioGroup(["Tarjeta", "Transferencia", "Bizum"], value="Bizum",
                                          label="Método de pago"),
                            ui.Slider(64, label="Volumen", unit=" %"),
                            ui.RangeSlider(20, 80, label="Rango de precio"),
                            gap=3,
                        )
                    ),
                    ui.Col(span=12, md=12, lg=4)(
                        ui.Stack(
                            ui.OtpInput(6, label="Código de verificación"),
                            ui.Rating(4, label="Valoración"),
                            ui.Stepper(2, label="Pasajeros"),
                            ui.ColorInput("#4f46e5", label="Color de marca"),
                            gap=3,
                        )
                    ),
                ),
                ui.Divider("fechas"),
                ui.Row(
                    ui.Col(span=12, md=6, lg=3)(ui.DateInput("", label="Fecha")),
                    ui.Col(span=12, md=6, lg=3)(ui.TimeInput("", label="Hora")),
                    ui.Col(span=12, md=6, lg=3)(ui.DateTimeInput("", label="Fecha y hora")),
                    ui.Col(span=12, md=6, lg=3)(ui.MonthInput("", label="Mes")),
                ),
                ui.Divider("ficheros"),
                ui.Row(
                    ui.Col(span=12, md=6)(ui.FileInput(label="Adjuntar", multiple=True)),
                    ui.Col(span=12, md=6)(ui.Dropzone(label="Suelta archivos aquí")),
                ),
                ui.Divider("etiquetas"),
                ui.TagInput(["python", "tailwind"], label="Etiquetas"),
            )
        ),
    )


def section_data() -> ui.Component:
    rows = [
        ["Ana Ruiz", "ana@ejemplo.com", ui.Badge("Admin", variant="primary")],
        ["Luis Paz", "luis@ejemplo.com", ui.Badge("Editor", variant="neutral")],
        ["Marta Gil", "marta@ejemplo.com", ui.Badge("Lector", variant="outline")],
    ]
    return ui.Stack(
        ui.Section(title="Tablas")(
            ui.Card()(
                ui.Table(
                    headers=["Nombre", "Correo", "Rol"],
                    rows=rows,
                    striped=True,
                    caption="Equipo",
                    footer=["3 personas", "", ""],
                )
            ),
            ui.Card()(
                ui.DataTable(
                    columns=[
                        {"key": "name", "label": "Nombre", "sortable": True},
                        {"key": "email", "label": "Correo", "sortable": True},
                        {"key": "role", "label": "Rol", "align": "right"},
                    ],
                    rows=[
                        {"id": 1, "name": "Ana Ruiz", "email": "ana@ejemplo.com", "role": "Admin"},
                        {"id": 2, "name": "Luis Paz", "email": "luis@ejemplo.com", "role": "Editor"},
                        {"id": 3, "name": "Marta Gil", "email": "marta@ejemplo.com", "role": "Lector"},
                    ],
                    page=1, page_size=2, total=3,
                    searchable=True, selectable=True,
                )
            ),
        ),
        ui.Section(title="Listas y árboles")(
            ui.Row(
                ui.Col(span=12, lg=6)(
                    ui.Card(title="Lista agrupada")(
                        ui.ListGroup(
                            ui.ListItem(title="Reunión de equipo", subtitle="Hoy · 10:00", icon="users", meta="3"),
                            ui.ListItem(title="Revisar PR #42", subtitle="Ayer", icon="code", meta="1"),
                            ui.ListItem(title="Despliegue", subtitle="Viernes", icon="upload"),
                        )
                    ),
                    ui.Card(title="Línea de tiempo")(
                        ui.Timeline(
                            ui.TimelineItem("Pedido creado", time="09:12", icon="check"),
                            ui.TimelineItem("Pago confirmado", time="09:15", tone="success", icon="check"),
                            ui.TimelineItem("En reparto", time="11:40", tone="warning", icon="send", last=True),
                        )
                    ),
                ),
                ui.Col(span=12, lg=6)(
                    ui.Card(title="Árbol")(
                        ui.Tree(
                            ui.TreeNode("src", icon="folder", expanded=True, children=[
                                ui.TreeNode("interui", icon="folder", expanded=True, children=[
                                    ui.TreeNode("app.py", icon="file"),
                                    ui.TreeNode("base.py", icon="file"),
                                    ui.TreeNode("controls", icon="folder", children=[
                                        ui.TreeNode("inputs.py", icon="file"),
                                    ]),
                                ]),
                                ui.TreeNode("tests", icon="folder"),
                            ]),
                        )
                    ),
                    ui.Card(title="Definiciones")(
                        ui.DescriptionList(
                            ui.DescriptionItem("Nombre", "interui"),
                            ui.DescriptionItem("Versión", ui.Badge("0.1.0", variant="primary")),
                            ui.DescriptionItem("Licencia", "MIT"),
                        )
                    ),
                ),
            )
        ),
        ui.Row(
            ui.Col(span=12, lg=6)(
                ui.Card(title="JSON")(
                    ui.JsonView({"id": 42, "tags": ["a", "b"], "activo": True, "score": 9.5})
                )
            ),
            ui.Col(span=12, lg=6)(
                ui.Card(title="Registros")(
                    ui.LogView(
                        [
                            {"level": "info", "time": "09:12", "message": "Servidor iniciado"},
                            {"level": "ok", "time": "09:13", "message": "Conexión establecida"},
                            {"level": "warn", "time": "09:20", "message": "Latencia alta"},
                            {"level": "error", "time": "09:21", "message": "Timeout"},
                        ],
                        title="app.log",
                    )
                ),
            ),
        ),
    )


def section_feedback() -> ui.Component:
    return ui.Row(
        ui.Col(span=12, lg=7)(
            ui.Card(title="Alertas")(
                ui.Alert("Todo ha ido bien.", level="success", title="Correcto"),
                ui.Alert("Revisa la configuración antes de continuar.", level="warning", title="Atención"),
                ui.Alert("No se pudo conectar con el servidor.", level="danger", title="Error", dismissible=True),
                ui.Alert("Novedad: soporte para temas oscuros.", level="info"),
            ),
            ui.Card(title="Progreso")(
                ui.Progress(35, label="Subiendo archivos", show_value=True, size="md"),
                ui.Progress(70, label="Con rayas", striped=True, tone="success"),
                ui.Progress(0, label="Indeterminado", indeterminate=True, tone="warning"),
                ui.Stack(
                    ui.ProgressRing(72, label="72 %"),
                    ui.Gauge(64, label="CPU"),
                    ui.Meter(82, label="Memoria"),
                    direction="row", gap=6, align="center", wrap=True,
                ),
            ),
        ),
        ui.Col(span=12, lg=5)(
            ui.Card(title="Estado vacío")(
                ui.EmptyState(
                    ui.Button("Crear proyecto", icon="plus"),
                    title="Sin proyectos",
                    description="Crea tu primer proyecto para empezar.",
                    icon="inbox",
                )
            ),
            ui.Card(title="Esqueletos")(
                ui.Stack(
                    ui.Skeleton(circle=True, height="10"),
                    ui.Stack(
                        ui.Skeleton(height="3", width="2/3"),
                        ui.Skeleton(height="3", width="full"),
                        ui.Skeleton(height="3", width="1/2"),
                        gap=2,
                    ),
                    direction="row", gap=3, align="center",
                )
            ),
            ui.Card(title="Avisos en línea")(
                ui.Stack(
                    ui.InlineToast("Guardado correctamente", level="success"),
                    ui.InlineToast("Sin conexión", level="danger"),
                    ui.Stack(
                        ui.StatusDot("Operativo", tone="success", pulse=True),
                        ui.StatusDot("Mantenimiento", tone="warning"),
                        ui.StatusDot("Caído", tone="danger"),
                        direction="row", gap=4,
                    ),
                    gap=2,
                )
            ),
        ),
    )


def section_navigation() -> ui.Component:
    return ui.Stack(
        ui.Card(title="Pestañas")(
            ui.Tabs(
                [
                    ("resumen", "Resumen", ui.Text("Contenido del resumen.")),
                    ("detalle", "Detalle", ui.Text("Contenido del detalle.")),
                    ("historial", "Historial", ui.Text("Contenido del historial.")),
                ],
                active="resumen",
                on_change=lambda e: None,
            ),
            ui.Tabs(
                [("a", "Píldoras A", ui.Text("Panel A")), ("b", "Píldoras B", ui.Text("Panel B"))],
                active="a", variant="pills",
            ),
        ),
        ui.Row(
            ui.Col(span=12, lg=6)(
                ui.Card(title="Migas y paginación")(
                    ui.Breadcrumb([("/", "Inicio"), ("/proyectos", "Proyectos"), ("actual", "interui")]),
                    ui.Pagination(4, pages=12),
                    ui.Steps(["Cuenta", "Perfil", "Pago", "Listo"], current=1),
                    gap=4,
                )
            ),
            ui.Col(span=12, lg=6)(
                ui.Card(title="Menús y paleta")(
                    ui.Stack(
                        ui.Dropdown(
                            ui.MenuItem("Editar", icon="edit", shortcut="⌘E"),
                            ui.MenuItem("Duplicar", icon="copy"),
                            ui.MenuItem("Eliminar", icon="trash", danger=True),
                            label="Acciones", icon="settings",
                        ),
                        ui.Popover(ui.Text("Contenido del popover con detalles."), trigger="Popover", title="Título"),
                        ui.Tooltip(ui.Button("Pasa el ratón", variant="outline"), content="Soy un tooltip"),
                        direction="row", gap=2, align="center", wrap=True,
                    ),
                    ui.Divider("paleta de comandos"),
                    ui.CommandPalette(
                        ui.CommandItem("Ir al inicio", hint="G H", icon="home"),
                        ui.CommandItem("Nuevo proyecto", hint="N", icon="plus"),
                        ui.CommandItem("Ajustes", hint="⌘,", icon="settings"),
                    ),
                )
            ),
        ),
        ui.Card(title="Barra y menú lateral")(
            ui.Navbar(
                ui.Stack(
                    ui.NavLink("Inicio", href="/", icon="home", active=True),
                    ui.NavLink("Proyectos", href="/proyectos", icon="folder", badge="3"),
                    ui.NavLink("Equipo", href="/equipo", icon="users"),
                    direction="row", gap=1,
                ),
                brand="interui",
            ),
            ui.Divider(),
            ui.Row(
                ui.Col(span=12, md=4)(
                    ui.Sidebar(
                        ui.SidebarItem("Panel", icon="grid", active=True),
                        ui.SidebarItem("Informes", icon="chart", badge=2),
                        ui.SidebarItem("Ajustes", icon="settings"),
                        title="Navegación",
                    )
                ),
                ui.Col(span=12, md=8)(ui.EmptyState(title="Contenido", icon="layers")),
            ),
        ),
    )


def section_overlays() -> ui.Component:
    return ui.Row(
        ui.Col(span=12, lg=6)(
            ui.Card(title="Modales")(
                ui.Stack(
                    ui.Modal(
                        ui.Text("Este es el contenido del modal."),
                        ui.Stack(
                            ui.Button("Cancelar", variant="outline", data={"iui-close": "demo-modal"}),
                            ui.Button("Confirmar", data={"iui-close": "demo-modal"}),
                            direction="row", gap=2,
                        ),
                        dialog_id="demo-modal",
                        title="Título del modal",
                        description="Subtítulo explicativo",
                    ).trigger("Abrir modal"),
                    ui.Drawer(
                        ui.Text("Panel lateral con contenido."),
                        drawer_id="demo-drawer",
                        title="Detalle",
                    ).trigger("Abrir cajón"),
                    ui.Sheet(ui.Text("Contenido de la hoja inferior."), sheet_id="demo-sheet",
                             title="Hoja inferior"),
                    ui.ConfirmDialog(
                        "Esta acción no se puede deshacer.",
                        title="¿Eliminar proyecto?",
                        on_confirm=lambda e: app.notify("Proyecto eliminado", "success"),
                    ),
                    direction="row", gap=2, wrap=True, align="center",
                ),
                ui.Hint("El botón de la hoja se abre con data={'iui-modal': 'demo-sheet'}."),
            )
        ),
        ui.Col(span=12, lg=6)(
            ui.Card(title="Plegables")(
                ui.Accordion(
                    [
                        ("¿Qué es interui?", ui.Text("Un framework declarativo de UI.")),
                        ("¿Necesito Node?", ui.Text("Solo para recompilar Tailwind.")),
                        ("¿Funciona sin internet?", ui.Text("Sí, todo es local.")),
                    ]
                ),
                ui.Divider(),
                ui.Collapse(
                    ui.Text("El contenido plegado se muestra aquí."),
                    title="Más información",
                    open=True,
                ),
                ui.Divider(),
                ui.Splitter(ui.Text("Panel izquierdo redimensionable"), ui.Text("Panel derecho")),
            )
        ),
    )


def section_charts() -> ui.Component:
    return ui.Stack(
        ui.Row(
            ui.Col(span=12, lg=6)(
                ui.ChartCard(
                    ui.AreaChart(
                        [
                            {"name": "2024", "data": [12, 19, 14, 27, 22, 34, 30, 41]},
                            {"name": "2025", "data": [8, 14, 18, 16, 25, 24, 33, 38]},
                        ],
                        labels=["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago"],
                    ),
                    title="Evolución mensual",
                    subtitle="Comparativa interanual",
                )
            ),
            ui.Col(span=12, lg=6)(
                ui.ChartCard(
                    ui.DonutChart({"Directo": 42, "Social": 28, "Búsqueda": 30}),
                    title="Origen del tráfico",
                )
            ),
        ),
        ui.Row(
            ui.Col(span=12, lg=6)(
                ui.ChartCard(
                    ui.BarChart(
                        [[18, 26, 12, 30, 22]],
                        labels=["L", "M", "X", "J", "V"],
                        show_values=True,
                    ),
                    title="Visitas por día",
                )
            ),
            ui.Col(span=12, lg=6)(
                ui.ChartCard(
                    ui.LineChart(
                        {"activos": [3, 6, 4, 9, 7, 12, 10], "nuevos": [1, 2, 2, 4, 3, 6, 5]},
                        labels=["S1", "S2", "S3", "S4", "S5", "S6", "S7"],
                        smooth=True,
                    ),
                    title="Usuarios",
                )
            ),
        ),
        ui.Card(title="Miniaturas")(
            ui.Stack(
                ui.Stack(
                    ui.Small("Ingresos"),
                    ui.Sparkline([4, 8, 6, 12, 9, 14, 11]),
                    ui.Badge("+18 %", variant="success"),
                    direction="row", align="center", gap=3,
                ),
                ui.Stack(
                    ui.Small("Errores"),
                    ui.Sparkline([9, 7, 8, 4, 5, 3, 2], color="#f43f5e"),
                    ui.Badge("-12 %", variant="success"),
                    direction="row", align="center", gap=3,
                ),
                ui.ScatterChart([[3, 7, 2, 9, 5]], labels=["a", "b", "c", "d", "e"]),
                gap=4,
                direction="row",
                wrap=True,
                align="center",
            )
        ),
    )


def section_media() -> ui.Component:
    return ui.Row(
        ui.Col(span=12, lg=6)(
            ui.Card(title="Avatares")(
                ui.Stack(
                    ui.Avatar(name="Ana Ruiz", size="sm"),
                    ui.Avatar(name="Luis Paz", size="md", status="online"),
                    ui.Avatar(name="Marta Gil", size="lg", status="busy"),
                    ui.Avatar(src="https://i.pravatar.cc/80?img=12", name="Foto", size="md"),
                    direction="row", gap=3, align="end",
                ),
                ui.AvatarGroup(
                    ui.Avatar(name="Ana Ruiz"), ui.Avatar(name="Luis Paz"),
                    ui.Avatar(name="Marta Gil"), ui.Avatar(name="Eva Sol"),
                    ui.Avatar(name="Paz Mar"), max_items=4,
                ),
            ),
            ui.Card(title="Galería")(
                ui.Gallery(
                    ui.Figure(
                        ui.Image("https://picsum.photos/seed/a/400/240", alt="Montaña"),
                        caption="Figura 1",
                    ),
                    ui.Figure(
                        ui.Image("https://picsum.photos/seed/b/400/240", alt="Bosque"),
                        caption="Figura 2",
                    ),
                    columns=2,
                )
            ),
        ),
        ui.Col(span=12, lg=6)(
            ui.Card(title="Carrusel")(
                ui.Carousel(
                    [
                        ui.Image("https://picsum.photos/seed/c/800/360", alt="Uno", ratio="video"),
                        ui.Image("https://picsum.photos/seed/d/800/360", alt="Dos", ratio="video"),
                        ui.Image("https://picsum.photos/seed/e/800/360", alt="Tres", ratio="video"),
                    ],
                    index=0,
                )
            ),
            ui.Card(title="Vídeo y audio")(
                ui.AspectRatio(
                    ui.Center(ui.Text("Aquí iría un <video>", tone="muted")),
                    ratio="video",
                    class_="rounded-xl bg-slate-100 dark:bg-slate-800",
                ),
                ui.Audio(""),
            ),
        ),
    )


def section_advanced() -> ui.Component:
    return ui.Row(
        ui.Col(span=12, lg=6)(
            ui.Card(title="Editor de código")(
                ui.CodeEditor(
                    "def saluda(nombre: str) -> str:\n"
                    "    return f'Hola, {nombre}'\n\n"
                    "print(saluda('mundo'))",
                    language="python",
                    max_h="64",
                )
            ),
            ui.Card(title="Editor enriquecido")(
                ui.RichTextEditor("<b>Texto</b> con <i>formato</i> editable.", min_h="32")
            ),
            ui.Card(title="Pares clave/valor")(
                ui.KeyValueEditor({"API_URL": "https://api.ejemplo.com", "DEBUG": "false"})
            ),
        ),
        ui.Col(span=12, lg=6)(
            ui.Card(title="Markdown")(
                ui.Markdown(
                    "# Título\n\n"
                    "Texto con **negrita**, *cursiva* y `código`.\n\n"
                    "- Elemento uno\n- Elemento dos\n\n"
                    "> Una cita breve.\n\n"
                    "```python\nprint('hola')\n```"
                )
            ),
            ui.Card(title="Terminal")(
                ui.Terminal(["pip install interui", "python app.py"], title="zsh")
            ),
            ui.Card(title="Tabla de progreso")(
                ui.ProgressTable(
                    [
                        {"label": "Diseño", "value": 100},
                        {"label": "Desarrollo", "value": 72},
                        {"label": "Pruebas", "value": 35},
                    ]
                )
            ),
        ),
    )


SECTIONS: list[tuple[str, str, str, Callable[[], ui.Component]]] = [
    ("basics", "Fundamentos", "layers", section_basics),
    ("buttons", "Botones", "zap", section_buttons),
    ("forms", "Formularios", "edit", section_forms),
    ("data", "Datos", "database", section_data),
    ("feedback", "Feedback", "bell", section_feedback),
    ("nav", "Navegación", "menu", section_navigation),
    ("overlays", "Superposiciones", "layers", section_overlays),
    ("charts", "Gráficos", "chart", section_charts),
    ("media", "Medios", "image", section_media),
    ("advanced", "Avanzados", "terminal", section_advanced),
]


def toggle_theme() -> None:
    app.theme = "dark" if app.theme == "light" else "light"


@app.page("/", title="Catálogo de controles")
def index() -> ui.Component:
    active = app.state("catalog_section", SECTIONS[0][0])

    nav = ui.Sidebar(title="Controles", width="w-60")(
        *[
            ui.Stack(
                ui.Icon(icon, size=4, class_="text-slate-400"),
                ui.Text(label, size="sm"),
                ui.Icon("chevron-right", size=3, class_="ml-auto text-slate-300"),
                direction="row",
                align="center",
                gap=2,
                on_click=(lambda key=key: (lambda: active.set(key)))(),
                class_=(
                    "cursor-pointer rounded-lg px-3 py-2 transition "
                    + (
                        "bg-indigo-600 text-white"
                        if key == active.get()
                        else "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
                    )
                ),
            )
            for key, label, icon, _builder in SECTIONS
        ]
    )

    current = next((builder for key, _l, _i, builder in SECTIONS if key == active.get()), section_basics)

    return ui.Screen(
        ui.Navbar(
            ui.Stack(
                ui.Badge("0.1.0", variant="primary"),
                ui.Text("Python · HTML · Tailwind · JS", size="sm", tone="muted"),
                ui.Button("Tema", variant="outline", size="sm", icon="moon", on_click=toggle_theme),
                direction="row",
                align="center",
            ),
            brand="Catálogo interui",
            logo="layers",
        ),
        ui.Stack(
            nav,
            ui.Main(class_="min-w-0 flex-1 overflow-y-auto p-6 max-h-[calc(100vh-3.25rem)]")(
                ui.Container(size="full", padded=False)(
                    ui.Stack(current(), gap=6),
                )
            ),
            direction="row",
            gap=0,
            align="stretch",
            class_="flex-1",
        ),
        class_="flex flex-col",
    )


if __name__ == "__main__":
    app.run()
