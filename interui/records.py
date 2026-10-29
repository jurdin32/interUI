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
from .controls.layout import Card
from .controls.typography import Badge, Heading, Muted
from .forms import ModelForm
from .grid import Container, Stack
from .html import escape
from .orm import Model
from .style import tw
from .theme import margin, pad, tone

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
        **props: Any,
    ) -> None:
        self.form = form
        self.columns = list(columns) if columns is not None else form.field_names()
        self.empty = empty
        self.card = card
        self.actions = list(actions or ())
        self.actions_header = actions_header
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        records = _records(_model_of(self.form))
        if records is None:
            return Alert(
                "Falta la base de datos. Ejecuta `python iui.py migrate` y vuelve a abrir.",
                title="Sin base de datos",
                level=tone.warning,
            ).render(ctx, f"{path}-alerta")

        headers = [self.form.label(name) for name in self.columns]
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

        table = Table(headers=headers, rows=rows, empty=self.empty)
        if not self.card:
            return table.render(ctx, f"{path}-tabla")
        return Card(table, pad=pad.all_2).render(ctx, f"{path}-tabla")


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
