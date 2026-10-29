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
from .theme import Token, gap, margin

__all__ = ["ModelForm", "FormModal", "form_dialog"]


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


#: Icono que se pone solo, según el nombre del campo.
_ICON_HINTS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("email", "correo", "mail"), "mail"),
    (("telefono", "teléfono", "phone", "celular", "movil", "móvil"), "phone"),
    (("nombre", "nombres", "name", "apellido"), "user"),
    (("direccion", "dirección", "address", "domicilio"), "map-pin"),
    (("cedula", "cédula", "documento", "dni", "ruc", "codigo", "código"), "hash"),
    (("ciudad", "pais", "país", "empresa"), "building"),
    (("precio", "valor", "monto", "total", "salario"), "tag"),
    (("clave", "password", "contrasena", "contraseña"), "lock"),
)


def _icon_for(name: str) -> str | None:
    """Icono sugerido por el nombre del campo (``email`` → correo)."""
    lower = name.lower()
    for hints, icon in _ICON_HINTS:
        if any(hint in lower for hint in hints):
            return icon
    return None


def _handler(signal: Any, errores: Any) -> Callable[[Any], None]:
    """Guarda el valor en la señal y retira los errores en cuanto se escribe."""

    def handler(event: Any) -> None:
        if errores.get():
            errores.set([])
        signal.set(event.checked if event.checked is not None else event.value)

    return handler


def _control(
    name: str,
    field: Any,
    value: Any,
    *,
    label: str,
    required: bool,
    on_change: Any,
    icon: str | None = None,
    placeholder: str | None = None,
) -> Component:
    """El control que corresponde al tipo del campo."""
    kind = field.type
    extra: dict[str, Any] = {}
    if placeholder:
        extra["placeholder"] = placeholder
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
    if kind in ("text", "json"):
        return Textarea(
            value=value, label=label, required=required, on_input=on_change, rows=3, **extra
        )
    if isinstance(field, Email) or any(hint in lower for hint in ("email", "correo", "mail")):
        return EmailInput(
            value=value, label=label, required=required, on_input=on_change,
            icon=icon, **extra,
        )
    if kind == "date":
        return DateInput(
            value=value, label=label, required=required, on_input=on_change,
            icon=icon, **extra,
        )
    if kind == "datetime":
        return DateTimeInput(
            value=value, label=label, required=required, on_input=on_change,
            icon=icon, **extra,
        )
    if kind in ("int", "real"):
        return NumberInput(
            value=value, label=label, required=required, on_input=on_change,
            icon=icon, **extra,
        )
    return Input(
        value=value, label=label, required=required, on_input=on_change, icon=icon, **extra
    )


# ---------------------------------------------------------------------------
# formulario
# ---------------------------------------------------------------------------
#: Opciones que van a la tarjeta del formulario (y a su cabecera y pie).
_CARD_KEYS = (
    "bg", "border", "rounded", "shadow", "ring", "pad", "radius", "elevated",
    "header", "header_bg", "header_color", "header_border", "header_pad",
    "header_font", "footer_bg",
)


def gap_value(value: Any) -> Any:
    """`field_gap`: un número (``3``), un token de `gap` o una clase ``gap-4``."""
    if value is None:
        return gap.all_3
    if isinstance(value, Token):
        return value
    text = str(value)
    if text.startswith("gap-"):
        return text
    return gap.all(value) if callable(gap.all) else f"gap-{text}"


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
    #: Icono de cada campo: ``icons = {"email": ui.icons.mail}``.
    icons: dict[str, str] | None = None
    #: Texto de ayuda dentro del campo: ``placeholders = {"email": "tu@correo.com"}``.
    placeholders: dict[str, str] | None = None
    #: Registro que se está editando (``None`` = alta nueva).
    instance: Model | None = None
    #: `False` oculta el título de la tarjeta (dentro de un diálogo, por ejemplo).
    show_title: bool = True
    #: `False` dibuja los campos sin la tarjeta que los envuelve.
    card: bool = True
    #: Opciones de `ui.Card` cuando hay tarjeta (`bg`, `border`, `pad`…).
    #: Los colores pasados al propio formulario se añaden aquí solos.
    card_options: dict[str, Any] | None = None
    #: Separación entre campos (`gap.all_3` por defecto; `1`, `4`, `ui.gap.all_6`…).
    field_gap: Any = None
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
        icons: dict[str, str] | None = None,
        placeholders: dict[str, str] | None = None,
        field_gap: Any = None,
        card_options: dict[str, Any] | None = None,
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
        declared_icons = icons if icons is not None else getattr(type(self), "icons", None)
        self.form_icons = dict(declared_icons or {})
        declared_hints = (
            placeholders if placeholders is not None else getattr(type(self), "placeholders", None)
        )
        self.form_placeholders = dict(declared_hints or {})
        self.instance = instance
        self._pending: dict[str, Any] | None = None
        self.submit_label = submit_label or getattr(type(self), "submit_label", "Guardar")
        self.prefix = prefix or getattr(type(self), "prefix", None)
        self.on_saved = on_saved if on_saved is not None else getattr(type(self), "on_saved", None)
        # El color de fondo del formulario va a su tarjeta, que es lo que se ve.
        self.field_gap = (
            field_gap if field_gap is not None else getattr(type(self), "field_gap", None)
        )
        # Todo lo que afecta a la tarjeta y a su cabecera se puede declarar
        # directamente en la clase: `header_bg = ui.colors.slate_100` en forms.py.
        self.card_options: dict[str, Any] = dict(
            card_options or getattr(type(self), "card_options", None) or {}
        )
        from .tema import por_defecto

        for nombre in _CARD_KEYS:
            # Prioridad: lo que se pasa al crear > lo declarado en la clase > tema.
            if nombre in props:
                self.card_options.setdefault(nombre, props.pop(nombre))
                continue
            declarado = getattr(type(self), nombre, None)
            if declarado is not None:
                self.card_options.setdefault(nombre, declarado)
                continue
            del_tema = por_defecto(type(self), nombre)
            if del_tema is not None:
                self.card_options.setdefault(nombre, del_tema)
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

    def icon(self, name: str) -> str | None:
        """Icono del campo: lo que diga `icons` o el que sugiere su nombre."""
        if name in self.form_icons:
            return self.form_icons[name] or None
        return _icon_for(name)

    def fresh(self) -> "ModelForm":
        """Otro formulario igual, con sus propios valores (para un modal)."""
        return type(self)(
            model=self.model,
            fields=self.form_fields,
            exclude=self.form_exclude,
            labels=self.form_labels,
            icons=self.form_icons,
            placeholders=self.form_placeholders,
            submit_label=self.submit_label,
            title=self.form_title,
        )

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
                    icon=self.icon(name),
                    placeholder=self.form_placeholders.get(name),
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

        if not self.card:
            return Stack(
                *([ValidationSummary(errores.get())] if errores.get() else []),
                *controles,
                Button(self.submit_label, icon="check", on_click=guardar, margin=margin.t_6),
                gap=gap.all_3,
            ).render(ctx, f"{path}-form")

        card = Card(
            *([ValidationSummary(errores.get())] if errores.get() else []),
            Stack(*controles, gap=gap_value(self.field_gap)),
            Button(self.submit_label, icon="check", on_click=guardar, margin=margin.t_4),
            title=(self.form_title or f"Nuevo {model.__name__.lower()}")
            if self.show_title
            else None,
            **self.card_options,
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
    node.card = False

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
        icon=False,
        width=width,
        scrollable=True,
        buttons=[(cancel_label, cerrar, "outline")],
        **options,
    )
    # Los formularios en modal comparten prefijo de señales: solo puede haber
    # uno abierto. Si ya había otro (doble clic rápido en otra fila), se cierra.
    dialog.form_dialog = True
    for abierto in application.dialogs:
        if getattr(abierto, "form_dialog", False) and abierto is not dialog:
            application.close_dialog(abierto)
    application.show_dialog(dialog)
    return dialog


class FormModal:
    """Un formulario en modal, **declarado como clase** (para su propio archivo).

    ```python
    class PersonaModal(ui.FormModal):
        form = PersonaForm
        title = "Nueva persona"
        width = "lg"
        options = dict(
            header_bg=ui.colors.slate_100,
            body_pad=ui.pad.p_5,
            gap=4,
        )

    PersonaModal.open()                     # alta
    PersonaModal.open(instance=persona)     # edición
    ```

    Todo lo que hay en `options` va al `Dialog`: `bg`, `rounded`, `shadow`,
    `header_bg`, `header_color`, `header_border`, `header_pad`, `title_font`,
    `footer_bg`, `footer_pad`, `body_pad`, `gap`, `backdrop`…
    """

    #: Formulario (clase o instancia).
    form: Any = None
    #: Título del modal; sin él se usa el del formulario.
    title: Any = None
    width: str = "lg"
    cancel_label: str = "Cerrar"
    #: Opciones del `Dialog` (colores, esquinas, espaciados…).
    options: dict[str, Any] = {}

    def __init__(self, **overrides: Any) -> None:
        self.overrides = dict(overrides)

    @classmethod
    def open(
        cls,
        instance: Model | None = None,
        *,
        title: Any = None,
        **options: Any,
    ) -> Any:
        """Abre el modal (alta si `instance` es ``None``)."""
        form = cls.form
        if form is None:
            raise TypeError(
                f"{cls.__name__} necesita un formulario: `form = MiForm` en la clase."
            )
        from .tema import estilos_de

        combinadas = {
            **estilos_de(cls),
            **dict(getattr(cls, "options", {}) or {}),
            **options,
        }
        return form_dialog(
            form,
            instance=instance,
            title=title or getattr(cls, "title", None),
            width=cls.width,
            cancel_label=cls.cancel_label,
            **combinadas,
        )
