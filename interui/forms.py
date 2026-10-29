"""Formularios a partir de un modelo: ``ui.ModelForm``.

Un formulario se declara en el ``forms.py`` de la app y la vista solo lo usa::

    # persona/forms.py
    import interui as ui

    from persona.models import Persona


    class PersonaForm(ui.ModelForm):
        model = Persona
        fields = ["nombre", "apellido", "email"]
        title = "Nueva persona"


    # persona/views.py
    def inicio() -> ui.Component:
        return PersonaForm()

Cada campo del modelo se convierte en su control (texto, correo, fecha, número
o interruptor), la validación de obligatorios y de ``unique`` se hace en Python
y el registro se guarda al pulsar el botón. Los valores viven en señales de la
app activa, así que no se pierden entre repintados.

Para un formulario suelto, sin declarar clase: ``ui.ModelForm(Persona)``.
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

from . import db as _db
from .base import Component
from .context import RenderContext
from .controls.buttons import Button
from .controls.inputs import (
    DateInput,
    DateTimeInput,
    EmailInput,
    Input,
    NumberInput,
    Select,
    Switch,
    Textarea,
    ValidationSummary,
)
from .controls.layout import Card
from .grid import Stack
from .orm import Choice, Email, Model
from .simple import state as _state
from .simple import toast as _toast
from .theme import gap, margin

__all__ = ["ModelForm", "form_dialog"]


# ---------------------------------------------------------------------------
# campos del modelo -> controles
# ---------------------------------------------------------------------------
def _label(name: str) -> str:
    """``fecha_nacimiento`` → ``Fecha nacimiento``."""
    words = name.replace("_", " ").strip()
    return words[:1].upper() + words[1:]


def _required(field: Any) -> bool:
    if field.primary_key or field.auto or field.auto_now_add or field.auto_now:
        return False
    if field.type == "bool":
        return False
    return not field.null and field.get_default() is None


def _initial(field: Any) -> Any:
    value = field.get_default()
    if field.type == "bool":
        return bool(value)
    return "" if value is None else value


def _handler(signal: Any, errores: Any) -> Callable[[Any], None]:
    """Guarda el valor en la señal y retira los errores en cuanto se escribe."""

    def handler(event: Any) -> None:
        if errores.get():
            errores.set([])
        signal.set(event.checked if event.checked is not None else event.value)

    return handler


def _control(
    name: str, field: Any, value: Any, *, label: str, required: bool, on_change: Any
) -> Component:
    """El control que corresponde al tipo del campo."""
    kind = field.type
    lower = name.lower()

    if isinstance(field, Choice):
        return Select(
            field.choices,
            value=value,
            label=label,
            required=required,
            on_change=on_change,
        )
    if kind == "bool":
        return Switch(label, checked=value, on_change=on_change)
    if kind == "date":
        return DateInput(value=value, label=label, required=required, on_input=on_change)
    if kind == "datetime":
        return DateTimeInput(value=value, label=label, required=required, on_input=on_change)
    if kind in ("int", "real"):
        return NumberInput(value=value, label=label, required=required, on_input=on_change)
    if kind in ("text", "json"):
        return Textarea(
            value=value, label=label, required=required, on_input=on_change, rows=3
        )
    if isinstance(field, Email) or any(hint in lower for hint in ("email", "correo", "mail")):
        return EmailInput(value=value, label=label, required=required, on_input=on_change)
    return Input(value=value, label=label, required=required, on_input=on_change)


# ---------------------------------------------------------------------------
# formulario
# ---------------------------------------------------------------------------
class ModelForm(Component):
    """Formulario de alta generado a partir de un modelo.

    Se declara como clase (recomendado, en ``forms.py``):

    ```python
    class PersonaForm(ui.ModelForm):
        model = Persona
        fields = ["nombre", "apellido", "email"]
        title = "Nueva persona"
    ```

    o se usa el atajo: ``ui.ModelForm(Persona)``.
    """

    tag = "div"
    model: type[Model] | None = None
    fields: Sequence[str] | None = None
    exclude: Sequence[str] = ()
    labels: dict[str, str] | None = None
    #: Registro que se está editando (``None`` = alta nueva).
    instance: Model | None = None
    #: `False` oculta el título de la tarjeta (dentro de un diálogo, por ejemplo).
    show_title: bool = True
    submit_label: str = "Guardar"
    title: Any = None
    prefix: str | None = None
    on_saved: Callable[[Any], None] | None = None

    def __init__(
        self,
        model: type[Model] | None = None,
        *,
        fields: Sequence[str] | None = None,
        exclude: Sequence[str] | None = None,
        labels: dict[str, str] | None = None,
        instance: Model | None = None,
        submit_label: str | None = None,
        title: Any = None,
        prefix: str | None = None,
        on_saved: Callable[[Any], None] | None = None,
        **props: Any,
    ) -> None:
        declared_title = title if title is not None else getattr(type(self), "title", None)
        # El atributo HTML `title` no se usa aquí: el título es el de la tarjeta.
        self.title = None
        self.form_title = declared_title
        self.model = model or getattr(type(self), "model", None)
        self.form_fields = fields if fields is not None else getattr(type(self), "fields", None)
        declared_exclude = exclude if exclude is not None else getattr(type(self), "exclude", ())
        self.form_exclude = tuple(declared_exclude or ())
        declared_labels = labels if labels is not None else getattr(type(self), "labels", None)
        self.form_labels = dict(declared_labels or {})
        self.instance = instance
        self._pending: dict[str, Any] | None = None
        self.submit_label = submit_label or getattr(type(self), "submit_label", "Guardar")
        self.prefix = prefix or getattr(type(self), "prefix", None)
        self.on_saved = on_saved if on_saved is not None else getattr(type(self), "on_saved", None)
        super().__init__(**props)

    # -- campos ----------------------------------------------------------
    def field_names(self) -> list[str]:
        model = self.model
        if model is None:
            raise TypeError(
                "ModelForm necesita un modelo: `model = TuModelo` en la clase "
                "o `ui.ModelForm(TuModelo)`."
            )
        if self.form_fields:
            names = list(self.form_fields)
        else:
            names = [
                name
                for name, field in model._fields.items()
                if not field.auto and not field.primary_key
                and not field.auto_now_add and not field.auto_now
            ]
        return [name for name in names if name not in self.form_exclude and name in model._fields]

    def label(self, name: str) -> str:
        """Nombre visible del campo: lo que diga `labels` o el campo con espacios.

        Es el mismo texto que usa el formulario, así que una vista puede pintar
        una tabla o un encabezado sin repetir los nombres a mano.
        """
        return self.form_labels.get(name) or _label(name)

    def load(self, record: Model) -> "ModelForm":
        """Rellena el formulario con un registro guardado; al guardar, lo actualiza."""
        self.instance = record
        self._pending = {name: getattr(record, name, None) for name in self.field_names()}
        return self

    def _duplicado(self, model: type[Model], name: str, value: Any) -> bool:
        """¿Otro registro ya usa ese valor? (el que se edita no cuenta)."""
        otros = [
            item
            for item in model.objects.filter(**{name: value})
            if self.instance is None or item.pk != self.instance.pk
        ]
        return bool(otros)

    def content(self, ctx: RenderContext, path: str) -> str:
        model = self.model
        assert model is not None  # lo garantiza field_names()
        base = self.prefix or f"form_{model.table}"
        errores = _state([], name=f"{base}_errores")

        controles: list[Component] = []
        bindings: list[tuple[str, Any, Any]] = []
        pending = self._pending
        for name in self.field_names():
            field = model._fields[name]
            inicial = _initial(field)
            if pending and pending.get(name) is not None:
                inicial = pending[name]
            signal = _state(inicial, name=f"{base}_{name}")
            if pending:
                signal.set(pending.get(name))
            bindings.append((name, field, signal))
            controles.append(
                _control(
                    name,
                    field,
                    signal.get(),
                    label=self.label(name),
                    required=_required(field),
                    on_change=_handler(signal, errores),
                )
            )

        if pending:
            self._pending = None

        def guardar() -> None:
            problemas: list[str] = []
            valores: dict[str, Any] = {}
            for name, field, signal in bindings:
                value = signal.get()
                if isinstance(value, str):
                    value = value.strip()
                if value == "":
                    value = None
                if value is None:
                    if _required(field):
                        problemas.append(f"{self.label(name)} es obligatorio.")
                    continue
                if isinstance(field, Choice) and str(value) not in field.option_values:
                    problemas.append(f"{self.label(name)}: elige una de las opciones.")
                    continue
                if field.unique and self._duplicado(model, name, value):
                    problemas.append(
                        f"Ya existe un registro con ese {self.label(name).lower()}."
                    )
                    continue
                valores[name] = value

            errores.set(problemas)
            if problemas:
                return

            try:
                if self.instance is not None:
                    for name, value in valores.items():
                        setattr(self.instance, name, value)
                    saved = self.instance.save()
                else:
                    saved = model.objects.create(**valores)
            except _db.DatabaseError as exc:
                errores.set([f"No se pudo guardar: {exc}"])
                return

            for _name, field, signal in bindings:
                signal.set(_initial(field))
            self.instance = None
            _toast("Registro guardado", "success")
            if self.on_saved is not None:
                self.on_saved(saved)

        card = Card(
            *([ValidationSummary(errores.get())] if errores.get() else []),
            Stack(*controles, gap=gap.all_3),
            Button(self.submit_label, icon="check", on_click=guardar, margin=margin.t_4),
            title=(self.form_title or f"Nuevo {model.__name__.lower()}")
            if self.show_title
            else None,
        )
        return card.render(ctx, f"{path}-card")


def form_dialog(
    form: Any,
    *,
    instance: Model | None = None,
    title: Any = None,
    width: str = "lg",
    cancel_label: str = "Cerrar",
    on_saved: Callable[[Any], None] | None = None,
    **options: Any,
) -> Any:
    """Abre un formulario en un diálogo modal y lo cierra al guardar.

    ```python
    def editar(registro) -> None:
        ui.form_dialog(PersonaForm, instance=registro, title="Editar persona")
    ```

    Acepta la clase (crea el formulario) o una instancia. Al guardar se cierra
    solo y la página se repinta con el cambio.
    """
    from .app import active_app
    from .dialogs import Dialog

    application = active_app()
    if application is None:
        raise RuntimeError(
            "form_dialog se abre desde un handler (un botón o una acción de tabla)."
        )

    node = form() if isinstance(form, type) else form
    if instance is not None:
        node.load(instance)
    # Un prefijo propio: los valores del diálogo no pisan los del formulario de
    # la página (misma tabla, mismas claves de señal).
    if not node.prefix:
        node.prefix = "dialogo"
    node.show_title = False

    def cerrar() -> None:
        application.close_dialog()

    previous = node.on_saved

    def al_guardar(record: Any) -> None:
        cerrar()
        if previous is not None:
            previous(record)
        if on_saved is not None:
            on_saved(record)

    node.on_saved = al_guardar

    dialog = Dialog(
        node,
        title=title or node.form_title or "Formulario",
        width=width,
        scrollable=True,
        buttons=[(cancel_label, cerrar, "outline")],
        **options,
    )
    application.show_dialog(dialog)
    return dialog
