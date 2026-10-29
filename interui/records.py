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

from typing import Any, Sequence

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
from .theme import gap, margin, pad, tone

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


class RecordTable(Component):
    """Tabla con lo guardado, usando las columnas del formulario.

    Si la base de datos aún no tiene la tabla (falta `migrate`), en su lugar
    sale un aviso que dice cómo crearla, en vez de romper la página.
    """

    tag = "div"

    def __init__(
        self,
        form: ModelForm,
        *,
        columns: Sequence[str] | None = None,
        empty: Any = "Todavía no hay registros",
        card: bool = True,
        actions: Sequence[RowAction] | None = None,
        actions_header: Any = "",
        search: bool = False,
        search_columns: Sequence[str] | None = None,
        search_placeholder: str = "Buscar…",
        page_size: int | None = 10,
        page_sizes: Sequence[int] = (10, 15, 20),
        sort: bool = True,
        sortable: Sequence[str] | None = None,
        order_by: str | None = None,
        prefix: str | None = None,
        **props: Any,
    ) -> None:
        self.form = form
        self.columns = list(columns) if columns is not None else form.field_names()
        self.empty = empty
        self.card = card
        self.actions = list(actions or ())
        self.actions_header = actions_header
        self.search = bool(search)
        self.search_columns = list(search_columns) if search_columns else None
        self.search_placeholder = search_placeholder
        self.page_size = page_size
        self.page_sizes = tuple(page_sizes)
        self.sort = bool(sort)
        self.sortable = list(sortable) if sortable else list(self.columns)
        self.order_by = order_by or ""
        self.prefix = prefix
        super().__init__(**props)

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

        if self.page_size and filtrados > self.page_size:
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
                        f"Mostrando {desde + 1}–{desde + len(records)} de {filtrados}"
                    ),
                    Stack(
                        Select(
                            [(str(tamano), str(tamano)) for tamano in self.page_sizes],
                            value=str(tamano),
                            on_change=al_cambiar_tamano,
                            size="sm",
                            width="w-20",
                        ),
                        Button(
                            icon="chevron-left",
                            variant="outline",
                            size="sm",
                            title="Anterior",
                            aria={"label": "Página anterior"},
                            disabled=pagina == 0,
                            on_click=ir_a(pagina - 1),
                        ),
                        Muted(f"{pagina + 1} / {paginas}"),
                        Button(
                            icon="chevron-right",
                            variant="outline",
                            size="sm",
                            title="Siguiente",
                            aria={"label": "Página siguiente"},
                            disabled=pagina >= paginas - 1,
                            on_click=ir_a(pagina + 1),
                        ),
                        direction="row",
                        align="center",
                        gap=gap.all_2,
                    ),
                    direction="row",
                    justify="between",
                    align="center",
                    gap=gap.all_3,
                    margin=margin.t_4,
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

        table = Table(
            headers=headers,
            rows=rows,
            empty=self.empty if total == 0 else "Ningún resultado para la búsqueda",
        )
        contenido: list[Any] = [*controles, table, *piezas]
        if not self.card:
            return Stack(*contenido, gap=0).render(ctx, f"{path}-tabla")
        return Card(*contenido, pad=pad.all_2).render(ctx, f"{path}-tabla")


class RecordPage(Component):
    """La página de un registro, con lo que pidas.

    ```python
    ui.RecordPage(PersonaForm(), title="Personas")                  # todo
    ui.RecordPage(PersonaForm(), form_mode="modal")                 # tabla + botón «Nuevo»
    ui.RecordPage(PersonaForm(), form_mode="none")                  # solo la tabla
    ui.RecordPage(PersonaForm(), table=False)                       # solo el formulario
    ```

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
        form: ModelForm,
        *,
        title: Any = None,
        counter: bool = True,
        table: bool = True,
        columns: Sequence[str] | None = None,
        actions: Sequence[RowAction] | None = None,
        search: bool = False,
        search_columns: Sequence[str] | None = None,
        page_size: int | None = 10,
        page_sizes: Sequence[int] = (10, 15, 20),
        sort: bool = True,
        sortable: Sequence[str] | None = None,
        order_by: str | None = None,
        form_mode: str = "inline",
        new_label: Any = "Nuevo",
        new_icon: str | None = "plus",
        pad_: Any = None,
        **props: Any,
    ) -> None:
        modo = str(form_mode or "inline").lower()
        if modo not in ("inline", "modal", "none"):
            raise ValueError(
                f"form_mode desconocido: {form_mode!r}; usa 'inline', 'modal' o 'none'"
            )
        self.form = form
        self.page_title = title
        self.show_counter = counter
        self.show_table = table
        self.columns = list(columns) if columns is not None else None
        self.actions = list(actions or ())
        self.table_options: dict[str, Any] = {
            "search": search,
            "search_columns": search_columns,
            "page_size": page_size,
            "page_sizes": page_sizes,
            "sort": sort,
            "sortable": sortable,
            "order_by": order_by,
        }
        self.form_mode = modo
        self.new_label = new_label
        self.new_icon = new_icon
        self.page_pad = pad_ if pad_ is not None else pad.py_8
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        form = self.form
        titulo = self.page_title
        if titulo is None:
            titulo = _plural(_model_of(form).__name__)

        header: Any = Heading(titulo, level=1)
        if self.form_mode == "modal":
            header = Stack(
                header,
                Button(
                    self.new_label,
                    icon=self.new_icon,
                    on_click=self._abrir_alta,
                ),
                direction="row",
                justify="between",
                align="center",
                gap=3,
            )

        pieces: list[Any] = [header]
        if self.show_counter:
            pieces.append(Muted(RecordCounter(form)))
        if self.form_mode == "inline":
            pieces.append(form)
        if self.show_table:
            pieces.append(
                RecordTable(
                    form,
                    columns=self.columns,
                    actions=self.actions,
                    margin=margin.t_6,
                    **self.table_options,
                )
            )
        return Container(*pieces, pad=self.page_pad).render(ctx, f"{path}-page")

    def _abrir_alta(self) -> None:
        """Botón **Nuevo**: abre el formulario de alta en un diálogo."""
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
