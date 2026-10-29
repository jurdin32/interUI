"""Lo guardado, a partir de un formulario.

Un `ui.ModelForm` ya sabe **qué campos** tiene y **cómo se llaman** (`fields` y
`labels` de su `forms.py`). Estas dos piezas usan eso mismo para enseñar la
tabla y el contador, así que una vista solo las coloca:

```python
form = PersonaForm()
return ui.Screen(
    ui.Container(pad=ui.pad.py_10)(
        ui.Heading("Personas", level=1),
        ui.Muted(ui.RecordCounter(form)),
        form,
        ui.RecordTable(form),
    )
)
```

Cambiar `fields` o `labels` en el formulario cambia el formulario **y** la
tabla; la vista no se toca.
"""

from __future__ import annotations

from typing import Any, Literal, Sequence

from . import db as _db
from .base import Component
from .context import RenderContext
from .controls.buttons import Button
from .controls.data import Table
from .controls.feedback import Alert
from .controls.inputs import Input, Select
from .controls.layout import Card
from .controls.typography import Badge, Heading, Muted
from .forms import ModelForm
from .grid import Container, Stack
from .html import escape
from .orm import Model
from .simple import state as _state
from .style import tw
from .tema import theme_default
from .theme import Color, Token, gap, juntar_estilos, margin, pad, paint, style_attr, tone

__all__ = ["RecordCounter", "RecordPage", "RecordTable", "RowAction"]


def _model_of(form: ModelForm) -> type[Model]:
    model = form.model
    if model is None:
        raise TypeError(
            "Necesita un formulario con modelo: `ui.RecordTable(PersonaForm())`."
        )
    return model


def _records(model: type[Model]) -> list[Any] | None:
    """Los registros guardados, o ``None`` si la tabla todavía no existe."""
    try:
        return list(model.objects.all())
    except _db.DatabaseError:
        return None


def _plural(name: str) -> str:
    """``Persona`` → ``Personas``: el título por defecto de la página."""
    return name if name.endswith("s") else f"{name}s"


def _ordenar(records: list[Any], campo: str, desc: bool) -> list[Any]:
    """Ordena por un campo; los huecos al final y sin reventar con tipos mixtos."""

    try:
        return sorted(
            records,
            key=lambda record: (
                getattr(record, campo, None) is None,
                getattr(record, campo, None),
            ),
            reverse=desc,
        )
    except TypeError:
        # Campos con tipos mezclados (o textos y números): se comparan como texto.
        return sorted(
            records,
            key=lambda record: (
                getattr(record, campo, None) is None,
                str(getattr(record, campo, "")).lower(),
            ),
            reverse=desc,
        )


def _cell(value: Any) -> Any:
    """Un booleano se ve como etiqueta y un hueco como raya."""
    if isinstance(value, bool):
        return Badge("sí" if value else "no")
    return "—" if value is None or value == "" else value


class RowAction:
    """Un botón de icono al final de cada fila: editar, borrar…

    ```python
    ui.RecordTable(
        PersonaForm(),
        actions=[
            ui.RowAction("Editar", icon=ui.icons.edit, on_click=editar),
            ui.RowAction("Eliminar", icon=ui.icons.trash, danger=True,
                         confirm="¿Eliminar esta persona?", on_click=borrar),
        ],
    )
    ```

    El handler recibe **el registro** de esa fila: ``def editar(registro): ...``.
    """

    def __init__(
        self,
        label: str,
        *,
        icon: str | None = None,
        on_click: Any = None,
        danger: bool = False,
        confirm: Any = None,
        variant: str | None = None,
        **options: Any,
    ) -> None:
        self.label = label
        self.icon = icon or ("trash" if danger else "edit")
        self.on_click = on_click
        self.danger = danger
        self.confirm = confirm
        self.variant = variant or ("ghost")
        self.options = options

    def build(self, record: Any) -> Component:
        """El botón de esta fila, ya conectado al registro."""

        def ejecutar() -> None:
            if self.on_click is not None:
                self.on_click(record)

        handler: Any = ejecutar
        if self.confirm:
            def preguntar() -> None:
                from .dialogs import dialog

                dialog.confirm(self.confirm, on_accept=ejecutar)

            handler = preguntar

        props = dict(self.options)
        if self.danger:
            props["class_"] = tw(
                "text-rose-600 hover:bg-rose-50 dark:text-rose-400 "
                "dark:hover:bg-rose-500/10",
                props.get("class_"),
            )
        return Button(
            icon=self.icon,
            variant=self.variant,
            size="sm",
            title=self.label,
            aria={"label": self.label},
            on_click=handler,
            **props,
        )

    def item(self, record: Any) -> Any:
        """La misma acción como entrada de menú contextual."""
        from .controls.shell import ContextItem

        def ejecutar() -> None:
            if self.on_click is not None:
                self.on_click(record)

        handler: Any = ejecutar
        if self.confirm:
            def preguntar() -> None:
                from .dialogs import dialog

                dialog.confirm(self.confirm, on_accept=ejecutar)

            handler = preguntar
        return ContextItem(self.label, icon=self.icon, danger=self.danger, on_click=handler)


#: Marca de «no se pasó este argumento» (así ``page_size=None`` es válido).
_FALTA = object()


def gap_value(value: Any, default: Any = None) -> Any:
    """`gap`/`page_gap`: un número (``4``), un token de `gap` o ``gap-4``."""
    if value is None:
        return default if default is not None else gap.all_4
    if isinstance(value, Token):
        return value
    text = str(value)
    if text.startswith("gap-"):
        return text
    return f"gap-{text}"


def _acciones(acciones: Any, menu: Any, clase: type) -> list[Any]:
    """Normaliza `actions`: lista, `False`/`None` (ninguna) o `True` (las del menú)."""
    if acciones is None or acciones is False:
        return []
    if acciones is True:
        # «Ponme los botones de las acciones que ya declaré en el menú».
        if isinstance(menu, (list, tuple)) and menu:
            return list(menu)
        raise TypeError(
            f"{clase.__name__}: `actions = True` usa las acciones del menú "
            "contextual, pero `context_menu` está vacío. Declara "
            "`context_menu = [ui.RowAction(...)]` o pasa "
            "`actions = [ui.RowAction(...)]`."
        )
    if not isinstance(acciones, (list, tuple)):
        raise TypeError(
            f"{clase.__name__}: `actions` debe ser una lista de ui.RowAction, "
            f"`False` (sin botones) o `True` (los del menú); llegó {acciones!r}."
        )
    return list(acciones)


def _util(prefix: str, value: Any) -> str:
    """``_util("bg", colors.slate_100)`` → ``bg-slate-100`` (vacío si no hay).

    Un token completo (``ui.font.xl.bold`` = ``text-xl font-bold``) se usa tal
    cual; un color de la paleta recibe el prefijo del argumento.
    """
    if value is None or value == "":
        return ""
    if isinstance(value, Token):
        return str(value)
    text = str(value)
    if isinstance(value, Color) or not (text.startswith(prefix) or text.startswith(f"{prefix}-")):
        text = f"{prefix}-{text}"
    return text


def _es_tabla(valor: Any) -> bool:
    """¿Es una tabla declarada (la clase de ``tables.py`` o una instancia)?"""
    if isinstance(valor, RecordTable):
        return True
    return isinstance(valor, type) and issubclass(valor, RecordTable)


#: Opciones de la franja de la página que también se pueden declarar en
#: `forms.py` (es donde vive el formulario, y ahí se busca primero lo suyo).
_CLAVES_FRANJA = (
    "title_bg",
    "title_color",
    "title_font",
    "title_border",
    "title_pad",
    "title_align",
    "title_full_width",
    "title_rounded",
    "counter_color",
    "page_gap",
)


def _es_formulario(valor: Any) -> bool:
    """¿Es un formulario de modelo (la clase de ``forms.py`` o una instancia)?"""
    if isinstance(valor, ModelForm):
        return True
    return isinstance(valor, type) and issubclass(valor, ModelForm)


def _form_of(form: Any) -> Any:
    """El formulario, ya instanciado (acepta la clase o la instancia)."""
    if form is None:
        return None
    return form() if isinstance(form, type) else form


def _preferir_tema(nombre: str, valor: Any, clase: type) -> Any:
    """`valor` si la app lo declaró de verdad; si no, lo que diga el tema.

    Los atributos de `RecordTable` son valores de fábrica: si la clase de la app
    no los cambia, `estilos.py` puede fijarlos sin que la vista repita nada.
    """
    del_tema = theme_default(clase, nombre)
    if del_tema is None:
        return valor
    if valor is None or valor == getattr(RecordTable, nombre, None):
        return del_tema
    return valor


class RecordTable(Component):
    """Tabla con lo guardado, usando las columnas del formulario.

    Todo se puede declarar en una **subclase** (`tables.py` de la app), que es
    lo que hace que la vista quede en una línea:

    ```python
    class PersonaTable(ui.RecordTable):
        form = PersonaForm
        columns = ["cedula", "nombres", "email"]
        striped = True
        header_bg = ui.colors.slate_100
        actions = False
        on_row_dblclick = editar
        context_menu = [ui.RowAction("Eliminar", on_click=borrar, danger=True)]
    ```

    Cualquier atributo de clase se puede pisar al crear la instancia:
    ``PersonaTable(page_size=20)``.

    Si la base de datos aún no tiene la tabla (falta `migrate`), en su lugar
    sale un aviso que dice cómo crearla, en vez de romper la página.
    """

    tag = "div"

    #: Formulario del que salen las columnas (clase o instancia).
    form: Any = None

    # -- opciones declarables -------------------------------------------
    columns: Sequence[str] | None = None
    empty: Any = "Todavía no hay registros"
    card: bool = True
    #: `False` esconde la columna de botones.
    actions: Any = None
    actions_header: Any = ""
    selectable: bool = False
    selected_bg: Any = None
    on_row_click: Any = None
    on_row_dblclick: Any = None
    context_menu: Any = None
    striped: bool = False
    header_bg: Any = None
    header_color: Any = None
    cell_colors: dict[Any, Any] | None = None
    column_bg: dict[Any, Any] | None = None
    hover_bg: Any = None
    zebra: Any = None
    search: bool = False
    search_columns: Sequence[str] | None = None
    search_placeholder: str = "Buscar…"
    page_size: int | None = 10
    page_sizes: Sequence[int] = (10, 15, 20)
    sort: bool = True
    sortable: Sequence[str] | None = None
    order_by: str | None = None
    prefix: str | None = None

    # -- franja de la página (título, contador y botón «Nuevo») ----------
    # `RecordPage(MiTabla)` los toma de aquí, así la vista no los repite.
    title: Any = None
    title_bg: Any = None
    title_color: Any = None
    title_font: Any = None
    title_border: Any = None
    title_pad: Any = None
    title_align: str | None = None
    #: Ocupa todo el ancho de la ventana (la franja, no el contenido).
    title_full_width: bool | None = None
    #: `True` redondeada, `False` esquinas rectas (por defecto, si hay fondo).
    title_rounded: Any = None
    #: Separación entre la franja, el contador, el formulario y la tabla.
    page_gap: Any = None
    counter: bool | None = None
    counter_color: Any = None
    new_label: Any = None
    new_icon: Any = None
    new_variant: str | None = None
    new_size: str | None = None
    #: Modal declarado (`ui.FormModal`) para el botón «Nuevo».
    new_modal: Any = None

    # -- la tarjeta que envuelve la tabla --------------------------------
    #: Opciones de `ui.Card` (`bg`, `border`, `pad`, `class_`…). Los colores
    #: pasados a la propia tabla se añaden aquí solos.
    card_options: dict[str, Any] | None = None
    #: Relleno de las celdas y de los encabezados (`ui.pad.px_2`, `"px-2 py-1"`).
    cell_pad: Any = None
    header_pad: Any = None

    def __init__(
        self,
        form: Any = None,
        *,
        columns: Sequence[str] | None = _FALTA,  # type: ignore[assignment]
        empty: Any = _FALTA,
        card: bool = _FALTA,  # type: ignore[assignment]
        actions: Any = _FALTA,
        actions_header: Any = _FALTA,
        selectable: bool = _FALTA,  # type: ignore[assignment]
        selected_bg: Any = _FALTA,
        on_row_click: Any = _FALTA,
        on_row_dblclick: Any = _FALTA,
        context_menu: Any = _FALTA,
        striped: bool = _FALTA,  # type: ignore[assignment]
        header_bg: Any = _FALTA,
        header_color: Any = _FALTA,
        cell_colors: dict[Any, Any] | None = _FALTA,  # type: ignore[assignment]
        column_bg: dict[Any, Any] | None = _FALTA,  # type: ignore[assignment]
        hover_bg: Any = _FALTA,
        zebra: Any = _FALTA,
        search: bool = _FALTA,  # type: ignore[assignment]
        search_columns: Sequence[str] | None = _FALTA,  # type: ignore[assignment]
        search_placeholder: str = _FALTA,  # type: ignore[assignment]
        page_size: int | None = _FALTA,  # type: ignore[assignment]
        page_sizes: Sequence[int] = _FALTA,  # type: ignore[assignment]
        cell_pad: Any = _FALTA,
        header_pad: Any = _FALTA,
        sort: bool = _FALTA,  # type: ignore[assignment]
        sortable: Sequence[str] | None = _FALTA,  # type: ignore[assignment]
        order_by: str | None = _FALTA,  # type: ignore[assignment]
        prefix: str | None = _FALTA,  # type: ignore[assignment]
        **props: Any,
    ) -> None:
        # Lo que no se pasa usa el atributo de clase (declarado en `tables.py`).
        self.form = _form_of(form if form is not None else type(self).form)
        if self.form is None:
            raise TypeError(
                f"{type(self).__name__} necesita un formulario: "
                "`form = MiForm` en la clase o `MiTabla(MiForm())`."
            )
        columnas = self._opcion("columns", columns)
        self.columns = list(columnas) if columnas is not None else self.form.field_names()
        self.empty = self._opcion("empty", empty)
        self.card = bool(self._opcion("card", card))
        acciones = self._opcion("actions", actions)
        self.actions = _acciones(acciones, self._opcion("context_menu", context_menu), type(self))
        self.actions_header = self._opcion("actions_header", actions_header)
        self.selectable = bool(self._opcion("selectable", selectable))
        self.selected_bg = self._opcion("selected_bg", selected_bg)
        self.on_row_click = self._opcion("on_row_click", on_row_click)
        self.on_row_dblclick = self._opcion("on_row_dblclick", on_row_dblclick)
        self.context_menu = self._opcion("context_menu", context_menu)
        self.striped = bool(self._opcion("striped", striped))
        self.header_bg = self._opcion("header_bg", header_bg)
        self.header_color = self._opcion("header_color", header_color)
        self.cell_colors = dict(self._opcion("cell_colors", cell_colors) or {})
        self.column_bg = dict(self._opcion("column_bg", column_bg) or {})
        self.hover_bg = self._opcion("hover_bg", hover_bg)
        self.zebra = self._opcion("zebra", zebra)
        self.search = bool(self._opcion("search", search))
        buscables = self._opcion("search_columns", search_columns)
        self.search_columns = list(buscables) if buscables else None
        self.search_placeholder = self._opcion("search_placeholder", search_placeholder)
        self.page_size = self._opcion("page_size", page_size)
        self.page_sizes = tuple(self._opcion("page_sizes", page_sizes))
        self.sort = bool(self._opcion("sort", sort))
        ordenables = self._opcion("sortable", sortable)
        self.sortable = list(ordenables) if ordenables else list(self.columns)
        self.order_by = self._opcion("order_by", order_by) or ""
        self.prefix = self._opcion("prefix", prefix)
        # `card_options` se pasa tal cual a la tarjeta; además, los colores que
        # se pongan en la propia tabla (`bg=`, `border=`…) van a la tarjeta, que
        # es la superficie que se ve (el envoltorio queda detrás).
        self.cell_pad = self._opcion("cell_pad", cell_pad)
        self.header_pad = self._opcion("header_pad", header_pad)
        self.card_options: dict[str, Any] = dict(self._opcion("card_options") or {})
        for nombre in ("bg", "border", "rounded", "shadow", "ring"):
            if nombre in props:
                self.card_options.setdefault(nombre, props.pop(nombre))
        super().__init__(**props)

    def _opcion(self, nombre: str, valor: Any = _FALTA) -> Any:
        """Argumento, atributo de la clase o valor del tema global."""
        if valor is not _FALTA:
            return valor
        return _preferir_tema(nombre, getattr(type(self), nombre, None), type(self))

    # -- estado de la tabla ---------------------------------------------
    def _key(self, suffix: str) -> str:
        base = self.prefix or f"tabla_{_model_of(self.form)._table}"
        return f"{base}_{suffix}"

    def _filtrar(self, records: list[Any], texto: str) -> list[Any]:
        """Búsqueda global: el texto en cualquiera de las columnas mostradas."""
        aguja = texto.strip().lower()
        if not aguja:
            return records
        columnas = self.search_columns or self.columns
        filtrados = []
        for record in records:
            valores = [
                str(getattr(record, name) if getattr(record, name) is not None else "")
                for name in columnas
            ]
            if any(aguja in valor.lower() for valor in valores):
                filtrados.append(record)
        return filtrados

    def content(self, ctx: RenderContext, path: str) -> str:
        records = _records(_model_of(self.form))
        if records is None:
            return Alert(
                "Falta la base de datos. Ejecuta `python iui.py migrate` y vuelve a abrir.",
                title="Sin base de datos",
                level=tone.warning,
            ).render(ctx, f"{path}-alerta")

        total = len(records)
        controles: list[Any] = []
        piezas: list[Any] = []

        if self.search:
            busqueda = _state("", name=self._key("busqueda"))
            pagina_signal = _state(0, name=self._key("pagina"))

            def al_buscar(evento: Any) -> None:
                busqueda.set("" if evento.value is None else str(evento.value))
                pagina_signal.set(0)

            controles.append(
                Input(
                    busqueda.get(),
                    label=None,
                    icon="search",
                    placeholder=self.search_placeholder,
                    on_input=al_buscar,
                    margin=margin.b_4,
                )
            )
            records = self._filtrar(records, busqueda.get())
            pieza_pagina: Any = pagina_signal
        else:
            pieza_pagina = _state(0, name=self._key("pagina"))

        # -- ordenación por columna -------------------------------------
        orden = _state(self.order_by.lstrip("-"), name=self._key("orden"))
        sentido = _state(
            "desc" if self.order_by.startswith("-") else "asc", name=self._key("sentido")
        )
        campo = orden.get()
        if campo:
            records = _ordenar(records, campo, sentido.get() == "desc")

        filtrados = len(records)

        if self.page_size and filtrados:
            tamano_signal = _state(self.page_size, name=self._key("tamano"))

            def al_cambiar_tamano(evento: Any) -> None:
                try:
                    tamano_signal.set(int(evento.value))
                except (TypeError, ValueError):
                    tamano_signal.set(self.page_size)
                pieza_pagina.set(0)

            tamano = int(tamano_signal.get() or self.page_size)
            paginas = max(1, (filtrados + tamano - 1) // tamano)
            pagina = min(max(int(pieza_pagina.get() or 0), 0), paginas - 1)
            if pagina != pieza_pagina.get():
                pieza_pagina.set(pagina)
            desde = pagina * tamano
            records = records[desde : desde + tamano]

            def ir_a(destino: int) -> Any:
                return lambda: pieza_pagina.set(max(0, min(destino, paginas - 1)))

            piezas.append(
                Stack(
                    Muted(
                        f"Mostrando {desde + 1}–{desde + len(records)} de {filtrados}",
                        class_="whitespace-nowrap tabular-nums",
                    ),
                    Stack(
                        Select(
                            [(str(tamano), str(tamano)) for tamano in self.page_sizes],
                            value=str(tamano),
                            on_change=al_cambiar_tamano,
                            size="sm",
                            width="w-16",
                            title="Filas por página",
                            aria={"label": "Filas por página"},
                            class_="shrink-0",
                        ),
                        Stack(
                            Button(
                                icon="chevron-left",
                                variant="outline",
                                size="sm",
                                title="Página anterior",
                                aria={"label": "Página anterior"},
                                disabled=pagina == 0,
                                on_click=ir_a(pagina - 1),
                                class_="shrink-0",
                            ),
                            Muted(
                                f"{pagina + 1} de {paginas}",
                                class_="whitespace-nowrap tabular-nums px-1",
                            ),
                            Button(
                                icon="chevron-right",
                                variant="outline",
                                size="sm",
                                title="Página siguiente",
                                aria={"label": "Página siguiente"},
                                disabled=pagina >= paginas - 1,
                                on_click=ir_a(pagina + 1),
                                class_="shrink-0",
                            ),
                            direction="row",
                            align="center",
                            gap=gap.all_1,
                        ),
                        direction="row",
                        align="center",
                        gap=gap.all_2,
                        class_="flex-nowrap shrink-0",
                    ),
                    direction="row",
                    justify="between",
                    align="center",
                    gap=gap.all_3,
                    margin=margin.t_4,
                    class_="flex-wrap",
                )
            )
        elif self.search:
            piezas.append(
                Muted(
                    f"{filtrados} de {total}" if filtrados != total else f"{total} en total",
                    margin=margin.t_3,
                )
            )

        def cabecera(name: str) -> Any:
            etiqueta = self.form.label(name)
            if not self.sort or name not in self.sortable:
                return etiqueta
            activo = campo == name
            icono = ("chevron-up" if sentido.get() == "asc" else "chevron-down") if activo else None

            def al_ordenar() -> None:
                if orden.get() == name:
                    sentido.set("desc" if sentido.get() == "asc" else "asc")
                else:
                    orden.set(name)
                    sentido.set("asc")
                pieza_pagina.set(0)

            return Button(
                etiqueta,
                variant="ghost",
                size="sm",
                icon=icono,
                aria={"label": f"Ordenar por {etiqueta}"},
                on_click=al_ordenar,
                class_="-ml-2",
            )

        headers = [cabecera(name) for name in self.columns]
        rows: list[list[Any]] = [
            [_cell(getattr(record, name)) for name in self.columns] for record in records
        ]
        if self.actions:
            headers.append(self.actions_header)
            for record, row in zip(records, rows):
                row.append(
                    Stack(
                        *[action.build(record) for action in self.actions],
                        direction="row",
                        gap=1,
                        justify="end",
                    )
                )

        seleccion = _state(None, name=self._key("seleccion")) if self.selectable else None

        def clic(indice: int, _fila: Any) -> None:
            registro = records[indice]
            if seleccion is not None:
                seleccion.set(registro.pk)
            if self.on_row_click is not None:
                self.on_row_click(registro)

        def doble_clic(indice: int, _fila: Any) -> None:
            if self.on_row_dblclick is not None:
                self.on_row_dblclick(records[indice])

        def menu(indice: int, _fila: Any) -> list[Any]:
            registro = records[indice]
            if callable(self.context_menu):
                return list(self.context_menu(registro) or ())
            return [action.item(registro) for action in self.context_menu]

        resaltada = None
        if seleccion is not None:
            actual = seleccion.get()
            resaltada = next(
                (index for index, record in enumerate(records) if record.pk == actual), None
            )

        columnas_extra = self.cell_colors
        if columnas_extra:
            columnas_extra = {
                (self.columns.index(clave) if clave in self.columns else clave): valor
                for clave, valor in columnas_extra.items()
            }
        fondos_extra = self.column_bg
        if fondos_extra:
            fondos_extra = {
                (self.columns.index(clave) if clave in self.columns else clave): valor
                for clave, valor in fondos_extra.items()
            }

        table = Table(
            headers=headers,
            rows=rows,
            empty=self.empty if total == 0 else "Ningún resultado para la búsqueda",
            surface=not self.card,
            cell_pad=self.cell_pad,
            header_pad=self.header_pad,
            striped=self.striped,
            zebra=self.zebra,
            hover_bg=self.hover_bg,
            header_bg=self.header_bg,
            header_color=self.header_color,
            cell_colors=columnas_extra,
            column_bg=fondos_extra,
            selected=resaltada,
            selected_bg=self.selected_bg,
            on_row_click=clic if (self.selectable or self.on_row_click) else None,
            on_row_dblclick=doble_clic if self.on_row_dblclick else None,
            context_menu=menu if self.context_menu else None,
        )
        contenido: list[Any] = [*controles, table, *piezas]
        if not self.card:
            return Stack(*contenido, gap=0).render(ctx, f"{path}-tabla")
        tarjeta = Card(*contenido, pad=pad.all_2, **self.card_options)
        return tarjeta.render(ctx, f"{path}-tabla")


class RecordPage(Component):
    """La página de un registro: pinta **solo las piezas que le pasas**.

    ```python
    ui.RecordPage(PersonaForm)                 # solo el formulario
    ui.RecordPage(PersonaTable)                # solo la tabla de `tables.py`
    ui.RecordPage(PersonaForm, PersonaTable)   # el formulario y debajo la tabla
    ui.RecordPage(PersonaTable, PersonaForm)   # la tabla y debajo el formulario
    ```

    Las piezas se colocan **en el orden en que se pasan**, así que decides tú
    qué se ve en cada página. Se admiten formularios (la clase o una instancia)
    y tablas declaradas en `tables.py`; con una tabla, la página toma de ahí el
    formulario y todas sus opciones (columnas, colores, clic, menú…).

    Con `table=True` se añade al final la tabla que sale del formulario (sin
    declararla en `tables.py`), y `form_mode="modal"` cambia el formulario por
    un botón **Nuevo** que lo abre en un diálogo.

    | `form_mode` | Qué se ve |
    |---|---|
    | `"inline"` (por defecto) | el formulario dentro de la página |
    | `"modal"` | un botón **Nuevo** que abre el formulario en un diálogo |
    | `"none"` | ni formulario ni botón: solo el contador y la tabla |

    El armazón (barra de título y menú) no va aquí: eso es `app.layout`.
    """

    tag = "div"

    def __init__(
        self,
        *parts: Any,
        form: Any = None,
        title: Any = None,
        counter: bool = True,
        table: Any = None,
        columns: Sequence[str] | None = None,
        actions: Literal[False] | Sequence[RowAction] | None = None,
        search: bool = False,
        search_columns: Sequence[str] | None = None,
        page_size: int | None = 10,
        page_sizes: Sequence[int] = (10, 15, 20),
        sort: bool = True,
        sortable: Sequence[str] | None = None,
        order_by: str | None = None,
        form_mode: str = "inline",
        new_label: Any = None,
        new_icon: str | None = None,
        new_variant: str | None = None,
        new_size: str | None = None,
        new_modal: Any = None,
        title_bg: Any = None,
        title_color: Any = None,
        title_font: Any = None,
        title_border: Any = None,
        title_pad: Any = None,
        title_align: str | None = None,
        title_full_width: bool | None = None,
        title_rounded: Any = None,
        page_gap: Any = None,
        counter_color: Any = None,
        pad_: Any = None,
        table_options: dict[str, Any] | None = None,
        **props: Any,
    ) -> None:
        modo = str(form_mode or "inline").lower()
        if modo not in ("inline", "modal", "none"):
            raise ValueError(
                f"form_mode desconocido: {form_mode!r}; usa 'inline', 'modal' o 'none'"
            )
        # -- las piezas de la página, en el orden en que se pasan ---------
        piezas: list[tuple[str, Any]] = []
        for parte in parts:
            if _es_tabla(parte):
                piezas.append(("tabla", parte))
            elif _es_formulario(parte):
                piezas.append(("formulario", parte))
            else:
                raise TypeError(
                    "RecordPage acepta formularios y tablas declaradas; recibió "
                    f"{type(parte).__name__}: `ui.RecordPage(PersonaForm, PersonaTable)`."
                )
        if form is not None:
            if _es_tabla(form):
                piezas.insert(0, ("tabla", form))
            elif _es_formulario(form):
                piezas.insert(0, ("formulario", form))
            else:
                raise TypeError(
                    f"form= espera un formulario o una tabla, no {type(form).__name__}."
                )
        if table is True:
            piezas.append(("tabla", True))
        elif table not in (None, False):
            if not _es_tabla(table):
                raise TypeError(
                    f"table= espera una tabla declarada o True, no {type(table).__name__}."
                )
            piezas.append(("tabla", table))

        #: Piezas que se pintan, ya resueltas: `("formulario", MiForm())` y
        #: `("tabla", MiTabla())`; `("tabla", True)` es la tabla del formulario.
        resueltas: list[tuple[str, Any]] = []
        for tipo, valor in piezas:
            if tipo == "tabla" and valor is not True and not isinstance(valor, RecordTable):
                valor = valor()
            resueltas.append((tipo, valor))
        self.piezas = resueltas
        #: Tabla declarada de la página (la primera que se haya pasado). Manda
        #: ella: de ahí salen el formulario y todas sus opciones.
        self.table_component = next(
            (valor for tipo, valor in resueltas if tipo == "tabla" and valor is not True),
            None,
        )
        # El formulario de la página: el que se pasa o el de la tabla declarada.
        primera_forma = next((valor for tipo, valor in resueltas if tipo == "formulario"), None)
        if primera_forma is None and self.table_component is not None:
            primera_forma = self.table_component.form
        if primera_forma is None:
            raise TypeError(
                "RecordPage necesita un formulario o una tabla: "
                "`ui.RecordPage(PersonaForm)`, `ui.RecordPage(PersonaTable)` o "
                "`ui.RecordPage(PersonaForm, PersonaTable)`. Si pasas solo una tabla, "
                "declara su `form` en `tables.py`."
            )
        # Vale la clase (`RecordPage(PersonaForm)`) o una instancia.
        self.form = _form_of(primera_forma)
        self.page_title = title
        self.show_counter = counter
        self.show_table = any(tipo == "tabla" for tipo, _ in resueltas)
        self.columns = list(columns) if columns is not None else None
        self.actions = [] if actions is False else list(actions or ())
        self.table_options: dict[str, Any] = {
            "search": search,
            "search_columns": search_columns,
            "page_size": page_size,
            "page_sizes": page_sizes,
            "sort": sort,
            "sortable": sortable,
            "order_by": order_by,
            # Aspecto e interacción de la tabla (cebra, colores, clic, menú…).
            **(table_options or {}),
        }
        self.form_mode = modo

        # Franja de la página: lo que no se pasa se toma de la tabla declarada
        # (`tables.py`), para que la vista no repita ni el título ni el botón.
        declarada_tabla = type(self.table_component) if self.table_component is not None else None

        def heredado(nombre: str, valor: Any) -> Any:
            if valor is not None:
                return valor
            if declarada_tabla is not None:
                declarado = getattr(declarada_tabla, nombre, None)
                if declarado is not None and declarado != getattr(RecordTable, nombre, None):
                    return declarado
            # La franja también se puede declarar en `forms.py`.
            if nombre in _CLAVES_FRANJA and self.form is not None:
                del_formulario = getattr(type(self.form), nombre, None)
                if del_formulario is not None:
                    return del_formulario
            del_tema = theme_default(type(self), nombre)
            if del_tema is None and declarada_tabla is not None:
                del_tema = theme_default(declarada_tabla, nombre)
            return del_tema

        self.new_label = heredado("new_label", new_label) or "Nuevo"
        self.new_icon = heredado("new_icon", new_icon) or "plus"
        self.new_variant = heredado("new_variant", new_variant) or "primary"
        self.new_size = heredado("new_size", new_size) or "md"
        self.new_modal = heredado("new_modal", new_modal)
        self.title_bg = heredado("title_bg", title_bg)
        self.title_color = heredado("title_color", title_color)
        self.title_font = heredado("title_font", title_font)
        self.title_border = heredado("title_border", title_border)
        self.title_pad = heredado("title_pad", title_pad)
        self.title_align = heredado("title_align", title_align) or "left"
        self.title_full_width = bool(heredado("title_full_width", title_full_width))
        #: `None` = redondeada solo si hay fondo; `False`/`"none"` = esquinas rectas.
        self.title_rounded = heredado("title_rounded", title_rounded)
        self.page_gap = heredado("page_gap", page_gap)
        self.counter_color = heredado("counter_color", counter_color)
        # `counter` es booleano y su valor por defecto es `True`: si la tabla lo
        # declara, manda ella.
        declarado_counter = getattr(declarada_tabla, "counter", None) if declarada_tabla else None
        if declarado_counter is not None:
            self.show_counter = bool(declarado_counter)
        if self.page_title is None and declarada_tabla is not None:
            self.page_title = heredado("title", None)
        self.page_pad = pad_ if pad_ is not None else pad.py_8
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        form = self.form
        titulo = self.page_title
        if titulo is None:
            titulo = _plural(_model_of(form).__name__)

        # -- franja: título, contador y botón «Nuevo» --------------------
        centrado = self.title_align == "center"
        # El título se construye aquí (no con `Heading`) para que `title_font` y
        # `title_color` manden de verdad: las utilidades de Tailwind no se pisan
        # por orden de escritura, así que no se mezclan dos tamaños ni dos colores.
        titulo_color, titulo_estilo = paint("color", self.title_color)
        titulo_clases = tw(
            "font-sans tracking-tight",
            _util("font", self.title_font) if self.title_font else "text-4xl font-bold sm:text-5xl",
            titulo_color or "text-slate-900 dark:text-slate-100",
        )
        contador: Any = None
        if self.show_counter:
            contador_color, contador_estilo = paint("color", self.counter_color)
            contador = (
                Component(
                    tag="p",
                    base_class=tw("text-sm leading-relaxed", contador_color),
                    style=contador_estilo or None,
                )(RecordCounter(form))
                if self.counter_color
                else Muted(RecordCounter(form))
            )
        cabecera = Stack(
            Component(tag="h1", base_class=titulo_clases, style=titulo_estilo or None)(titulo),
            *( [contador] if contador is not None else [] ),
            gap=1,
            align="center" if centrado else "start",
        )
        nuevo = (
            Button(
                self.new_label,
                icon=self.new_icon,
                variant=self.new_variant,
                size=self.new_size,
                on_click=self._abrir_alta,
            )
            if self.form_mode == "modal"
            else None
        )
        if nuevo is not None and not centrado:
            cabecera = Stack(
                cabecera,
                nuevo,
                direction="row",
                justify="between",
                align="center",
                gap=3,
                class_="w-full",
            )
        elif nuevo is not None:
            cabecera = Stack(cabecera, nuevo, gap=3, align="center")

        radio = self.title_rounded
        if radio is None:
            # A lo ancho no se redondea (la franja va de lado a lado).
            radio = "" if self.title_full_width else ("xl" if self.title_bg else "")
        elif radio is True:
            radio = "xl"
        elif radio is False or str(radio) == "none":
            radio = ""
        franja_fondo, franja_fondo_estilo = paint("bg", self.title_bg)
        franja_borde, franja_borde_estilo = paint("border", self.title_border)
        franja = tw(
            franja_fondo,
            "border-b" if self.title_border else "",
            franja_borde,
            _util("rounded", radio) if radio else "",
            self.title_pad or "",
        )
        franja_estilo = juntar_estilos(franja_fondo_estilo, franja_borde_estilo)
        if not franja:
            header: Any = cabecera
        elif self.title_full_width:
            # Franja de lado a lado: el fondo ocupa la ventana y el contenido
            # sigue alineado con la tabla (mismo ancho máximo y padding).
            header = Component(
                tag="div",
                base_class=tw("w-full", franja),
                style=franja_estilo or None,
            )(Container(cabecera, size="xl"))
        else:
            header = Stack(
                cabecera,
                pad=self.title_pad,
                class_=franja,
                style=franja_estilo or None,
            )

        pieces: list[Any] = [header]
        for tipo, valor in self.piezas:
            if tipo == "formulario":
                # En `modal` el formulario vive en el diálogo del botón «Nuevo»;
                # en `none` no se pinta en ningún sitio.
                if self.form_mode == "inline":
                    pieces.append(_form_of(valor))
                continue
            if valor is True:
                # La tabla que sale del formulario, sin declararla en `tables.py`.
                pieces.append(
                    RecordTable(
                        form,
                        columns=self.columns,
                        actions=self.actions,
                        **self.table_options,
                    )
                )
            else:
                # Tabla declarada en `tables.py`: manda ella, la página no la pisa.
                pieces.append(valor)
        # Separación uniforme entre franja, contador, formulario y tabla.
        contenido = Stack(*pieces, gap=gap_value(self.page_gap))
        if pieces and self.title_full_width and self.title_bg:
            return Stack(
                pieces[0],
                Container(Stack(*pieces[1:], gap=gap_value(self.page_gap)), pad=self.page_pad),
                gap=0,
            ).render(ctx, f"{path}-page")
        return Container(contenido, pad=self.page_pad).render(ctx, f"{path}-page")

    def _abrir_alta(self) -> None:
        """Botón **Nuevo**: abre el formulario de alta en un diálogo."""
        if self.new_modal is not None:
            # El modal declarado en `dialogs.py` manda (mismo estilo y medidas).
            self.new_modal.open()
            return
        from .forms import form_dialog

        form_dialog(
            self.form.fresh(),
            title=self.form.form_title or f"Nuevo {_model_of(self.form).__name__.lower()}",
        )


class RecordCounter(Component):
    """``3 registros guardados`` / ``1 registro guardado``, sin la tabla."""

    tag = "span"

    def __init__(
        self,
        form: ModelForm,
        *,
        singular: str = "1 registro guardado",
        plural: str = "{total} registros guardados",
        **props: Any,
    ) -> None:
        self.form = form
        self.singular = singular
        self.plural = plural
        super().__init__(**props)

    def total(self) -> int | None:
        model = _model_of(self.form)
        try:
            return model.objects.count()
        except _db.DatabaseError:
            return None

    def content(self, ctx: RenderContext, path: str) -> str:
        total = self.total()
        if total is None:
            return ""
        if total == 1:
            return escape(self.singular)
        return escape(self.plural.format(total=total))
