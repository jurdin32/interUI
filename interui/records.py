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
from .controls.data import Table
from .controls.feedback import Alert
from .controls.layout import Card
from .controls.typography import Badge, Heading, Muted
from .forms import ModelForm
from .grid import Container
from .html import escape
from .orm import Model
from .theme import margin, pad, tone

__all__ = ["RecordCounter", "RecordPage", "RecordTable"]


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
        **props: Any,
    ) -> None:
        self.form = form
        self.columns = list(columns) if columns is not None else form.field_names()
        self.empty = empty
        self.card = card
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        records = _records(_model_of(self.form))
        if records is None:
            return Alert(
                "Falta la base de datos. Ejecuta `python iui.py migrate` y vuelve a abrir.",
                title="Sin base de datos",
                level=tone.warning,
            ).render(ctx, f"{path}-alerta")

        table = Table(
            headers=[self.form.label(name) for name in self.columns],
            rows=[
                [_cell(getattr(record, name)) for name in self.columns]
                for record in records
            ],
            empty=self.empty,
        )
        if not self.card:
            return table.render(ctx, f"{path}-tabla")
        return Card(table, pad=pad.all_2).render(ctx, f"{path}-tabla")


class RecordPage(Component):
    """La página completa de un registro: título, contador, formulario y tabla.

    Es lo que devuelve una vista normal::

        def inicio() -> ui.Component:
            return ui.RecordPage(PersonaForm(), title="Personas")

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
        pad_: Any = None,
        **props: Any,
    ) -> None:
        self.form = form
        self.page_title = title
        self.show_counter = counter
        self.show_table = table
        self.page_pad = pad_ if pad_ is not None else pad.py_8
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        form = self.form
        titulo = self.page_title
        if titulo is None:
            titulo = _plural(_model_of(form).__name__)

        pieces: list[Any] = [Heading(titulo, level=1)]
        if self.show_counter:
            pieces.append(Muted(RecordCounter(form)))
        pieces.append(form)
        if self.show_table:
            pieces.append(RecordTable(form, margin=margin.t_6))
        return Container(*pieces, pad=self.page_pad).render(ctx, f"{path}-page")


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
