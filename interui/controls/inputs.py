"""Controles de formulario: entradas de texto, selección, fechas, ficheros…"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

from ..base import Component, bind_many
from ..context import RenderContext
from ..html import escape
from ..icons import Icon
from ..state import value_of
from ..style import tw
from ..theme import utility
from ..ui import INPUT_BASE, INPUT_SIZES, field_shell

__all__ = [
    "Input", "TextInput", "EmailInput", "SearchInput", "PasswordInput", "NumberInput",
    "Textarea", "Select", "MultiSelect", "Combobox", "Datalist",
    "Checkbox", "CheckboxGroup", "Radio", "RadioGroup", "Switch", "Slider", "RangeSlider",
    "DateInput", "TimeInput", "DateTimeInput", "DateRangeInput", "MonthInput", "WeekInput",
    "ColorInput", "FileInput", "Dropzone", "OtpInput", "Rating", "TagInput",
    "SegmentedControl", "ToggleGroup", "HiddenInput", "Form", "FormField", "Fieldset",
    "ValidationSummary", "Stepper",
]

INVALID = (
    "border-rose-400 text-rose-900 focus:border-rose-500 focus:ring-rose-500/30 "
    "dark:border-rose-500/60"
)
ICON_BOX = "pointer-events-none absolute inset-y-0 flex items-center text-slate-400 dark:text-slate-500"


def _options(items: Iterable[Any] | None) -> list[tuple[str, str, bool]]:
    result: list[tuple[str, str, bool]] = []
    for item in items or []:
        if isinstance(item, dict):
            result.append(
                (
                    str(item.get("value", item.get("label", ""))),
                    str(item.get("label", item.get("value", ""))),
                    bool(item.get("disabled", False)),
                )
            )
        elif isinstance(item, (tuple, list)):
            value = item[0]
            label = item[1] if len(item) > 1 else item[0]
            disabled = bool(item[2]) if len(item) > 2 else False
            result.append((str(value), str(label), disabled))
        else:
            result.append((str(item), str(item), False))
    return result


class Input(Component):
    """Campo de una línea. Acepta etiqueta, ayuda, error e iconos."""

    tag = "input"
    void = True
    input_type = "text"

    def __init__(
        self,
        value: Any = "",
        *,
        name: str | None = None,
        placeholder: str | None = None,
        size: str = "md",
        icon: str | None = None,
        trailing: Any = None,
        label: Any = None,
        help_text: Any = None,
        error: Any = None,
        required: bool = False,
        disabled: bool = False,
        readonly: bool = False,
        invalid: bool | None = None,
        live: bool = False,
        debounce: int = 220,
        horizontal: bool = False,
        autofocus: bool = False,
        autocomplete: str | None = None,
        **props: Any,
    ) -> None:
        self.size = size
        self.icon = icon
        self.trailing = trailing
        self.label = label
        self.help_text = help_text
        self.error = error
        self.required = required
        self.horizontal = horizontal
        self.invalid = invalid if invalid is not None else bool(error)
        self.live = live
        self.debounce = debounce

        props.setdefault("type", self.input_type)
        props["value"] = "" if value is None else value
        if name:
            props["name"] = name
        if placeholder:
            props["placeholder"] = placeholder
        if value_of(required, False):
            props["required"] = True
        if value_of(disabled, False):
            props["disabled"] = True
        if value_of(readonly, False):
            props["readonly"] = True
        if autofocus:
            props["data"] = {**(props.get("data") or {}), "iui-autofocus": "true"}
        if autocomplete:
            props["autocomplete"] = autocomplete
        if live:
            props.setdefault("data", {})
            props["data"] = {**props["data"], "iui-debounce": debounce}
        super().__init__(**props)

    def classes(self, ctx: RenderContext, uid: str) -> str:
        return tw(
            INPUT_BASE,
            INPUT_SIZES.get(self.size, INPUT_SIZES["md"]),
            INVALID if self.invalid else "",
            "pl-10" if self.icon else "",
            "pr-10" if self.trailing is not None else "",
            self.base_class,
            self.class_,
        )

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        if self.icon or self.trailing is not None:
            lead = (
                f'<span class="{ICON_BOX} left-3">{Icon(self.icon, size=4).render(ctx, uid + "-i")}</span>'
                if self.icon
                else ""
            )
            tail = ""
            if self.trailing is not None:
                if isinstance(self.trailing, str):
                    tail = f'<span class="{ICON_BOX} right-3">{Icon(self.trailing, size=4).render(ctx, uid + "-t")}</span>'
                elif isinstance(self.trailing, Component):
                    tail = (
                        f'<span class="absolute inset-y-0 right-2 flex items-center">'
                        f"{self.trailing.render(ctx, uid + '-t')}</span>"
                    )
                else:
                    tail = f'<span class="{ICON_BOX} right-3">{escape(self.trailing)}</span>'
            html = f'<div class="relative">{lead}{html}{tail}</div>'
        return field_shell(
            html,
            uid,
            label=self.label,
            help_text=self.help_text,
            error=self.error,
            required=self.required,
            horizontal=self.horizontal,
        )


class TextInput(Input):
    pass


class EmailInput(Input):
    input_type = "email"

    def __init__(self, *args: Any, **props: Any) -> None:
        props.setdefault("icon", "mail")
        props.setdefault("placeholder", "tu@correo.com")
        super().__init__(*args, **props)


class SearchInput(Input):
    input_type = "search"

    def __init__(self, *args: Any, **props: Any) -> None:
        props.setdefault("icon", "search")
        props.setdefault("placeholder", "Buscar…")
        super().__init__(*args, **props)


class PasswordInput(Input):
    input_type = "password"

    def __init__(self, *args: Any, **props: Any) -> None:
        props.setdefault("icon", "lock")
        props.setdefault("placeholder", "••••••••")
        super().__init__(*args, **props)

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        toggle = (
            f'<button type="button" data-iui-reveal="{escape(uid)}" '
            'class="absolute inset-y-0 right-2 my-auto flex h-8 w-8 items-center justify-center '
            'rounded-md text-slate-400 transition hover:bg-slate-100 hover:text-slate-700 '
            'dark:hover:bg-slate-800 dark:hover:text-slate-200" aria-label="Mostrar contraseña">'
            + Icon("eye", size=4).render(ctx, uid + "-e")
            + "</button>"
        )
        lead = (
            f'<span class="{ICON_BOX} left-3">{Icon(self.icon, size=4).render(ctx, uid + "-i")}</span>'
            if self.icon
            else ""
        )
        boxed = f'<div class="relative">{lead}{html}{toggle}</div>'
        return field_shell(
            boxed,
            uid,
            label=self.label,
            help_text=self.help_text,
            error=self.error,
            required=self.required,
            horizontal=self.horizontal,
        )

    def classes(self, ctx: RenderContext, uid: str) -> str:
        return tw(
            INPUT_BASE,
            INPUT_SIZES.get(self.size, INPUT_SIZES["md"]),
            INVALID if self.invalid else "",
            "pl-10" if self.icon else "",
            "pr-10",
            self.base_class,
            self.class_,
        )


class NumberInput(Input):
    input_type = "number"

    def __init__(
        self,
        value: Any = "",
        *,
        min: Any = None,
        max: Any = None,
        step: Any = None,
        **props: Any,
    ) -> None:
        if min is not None:
            props["min"] = min
        if max is not None:
            props["max"] = max
        props["step"] = step if step is not None else 1
        super().__init__(value, **props)


class Textarea(Component):
    tag = "textarea"

    def __init__(
        self,
        value: Any = "",
        *,
        rows: int = 4,
        name: str | None = None,
        placeholder: str | None = None,
        label: Any = None,
        help_text: Any = None,
        error: Any = None,
        required: bool = False,
        disabled: bool = False,
        resize: str = "y",
        invalid: bool | None = None,
        live: bool = False,
        **props: Any,
    ) -> None:
        self.label = label
        self.help_text = help_text
        self.error = error
        self.required = required
        self.value = "" if value is None else str(value)
        self.invalid = invalid if invalid is not None else bool(error)
        props["rows"] = rows
        if name:
            props["name"] = name
        if placeholder:
            props["placeholder"] = placeholder
        if required:
            props["required"] = True
        if disabled:
            props["disabled"] = True
        if live:
            props["data"] = {**(props.get("data") or {}), "iui-debounce": 220}
        props["base_class"] = tw(
            INPUT_BASE, "min-h-[5rem] px-3 py-2 text-sm leading-relaxed",
            INVALID if self.invalid else "",
            {"none": "resize-none", "y": "resize-y", "x": "resize-x", "both": "resize"}.get(resize, "resize-y"),
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return escape(self.value)

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        return field_shell(
            html, uid, label=self.label, help_text=self.help_text, error=self.error,
            required=self.required,
        )


class Select(Component):
    tag = "select"

    def __init__(
        self,
        options: Sequence[Any] | None = None,
        *,
        value: Any = "",
        name: str | None = None,
        placeholder: str | None = None,
        size: str = "md",
        label: Any = None,
        help_text: Any = None,
        error: Any = None,
        required: bool = False,
        disabled: bool = False,
        multiple: bool = False,
        **props: Any,
    ) -> None:
        self.options = _options(options)
        self.value = "" if value is None else str(value)
        self.placeholder = placeholder
        self.label = label
        self.help_text = help_text
        self.error = error
        self.required = required
        self.multiple = multiple
        if name:
            props["name"] = name
        if required:
            props["required"] = True
        if disabled:
            props["disabled"] = True
        if multiple:
            props["multiple"] = True
            props.setdefault("size", len(self.options) or 4)
        props["value"] = self.value
        props["base_class"] = tw(
            INPUT_BASE,
            INPUT_SIZES.get(size, INPUT_SIZES["md"]),
            "iui-select" if not multiple else "iui-select px-2 py-2",
            INVALID if error else "",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        parts: list[str] = []
        if self.placeholder:
            parts.append(
                f'<option value="" disabled{" selected" if not self.value else ""}>'
                f"{escape(self.placeholder)}</option>"
            )
        for option_value, option_label, disabled in self.options:
            selected = option_value == self.value
            parts.append(
                f'<option value="{escape(option_value)}"'
                + (' selected' if selected else "")
                + (" disabled" if disabled else "")
                + f">{escape(option_label)}</option>"
            )
        return "".join(parts)

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        return field_shell(
            html, uid, label=self.label, help_text=self.help_text, error=self.error,
            required=self.required,
        )



class MultiSelect(Select):
    def __init__(self, options: Sequence[Any] | None = None, *, values: Sequence[Any] | None = None, **props: Any) -> None:
        values = [str(v) for v in (values or [])]
        props.pop("value", None)
        super().__init__(options, value="", multiple=True, **props)
        self.values = values

    def content(self, ctx: RenderContext, path: str) -> str:
        parts: list[str] = []
        for option_value, option_label, disabled in self.options:
            selected = option_value in self.values
            parts.append(
                f'<option value="{escape(option_value)}"'
                + (" selected" if selected else "")
                + (" disabled" if disabled else "")
                + f">{escape(option_label)}</option>"
            )
        return "".join(parts)


class Datalist(Component):
    tag = "datalist"

    def __init__(self, items: Sequence[Any] | None = None, **props: Any) -> None:
        self.items = _options(items)
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return "".join(
            f'<option value="{escape(value)}">{escape(label)}</option>'
            for value, label, _disabled in self.items
        )


class Combobox(Component):
    """Campo de texto con sugerencias del navegador (``<datalist>``)."""

    tag = "div"

    def __init__(
        self,
        value: Any = "",
        *,
        items: Sequence[Any] | None = None,
        label: Any = None,
        help_text: Any = None,
        error: Any = None,
        placeholder: str | None = None,
        name: str | None = None,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.value = "" if value is None else str(value)
        self.items = items or []
        self.label = label
        self.help_text = help_text
        self.error = error
        self.placeholder = placeholder
        self.name = name
        if on_change is not None:
            props["on_change"] = on_change
        props["base_class"] = tw("flex flex-col gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        list_id = f"{uid}-list"
        field = Input(
            self.value,
            placeholder=self.placeholder,
            name=self.name,
            icon="search",
            label=self.label,
            help_text=self.help_text,
            error=self.error,
        )
        field.props["list"] = list_id
        field.handlers["change"] = self.handlers.get("change")
        inner = field.render(ctx, ctx.child(path, 0))
        options = "".join(
            f'<option value="{escape(value)}"></option>'
            for value, _label, _disabled in _options(self.items)
        )
        return f'{inner}<datalist id="{escape(list_id)}">{options}</datalist>'


class Checkbox(Component):
    tag = "input"
    void = True

    def __init__(
        self,
        label: Any = None,
        *,
        checked: bool = False,
        value: Any = "on",
        name: str | None = None,
        disabled: bool = False,
        help_text: Any = None,
        indeterminate: bool = False,
        **props: Any,
    ) -> None:
        self.label = label
        self.help_text = help_text
        self.source_checked = checked
        self.source_disabled = disabled
        self.source_value = value
        props.setdefault("type", "checkbox")
        if name:
            props["name"] = name
        if indeterminate:
            props["data"] = {**(props.get("data") or {}), "iui-indeterminate": "true"}
        props["base_class"] = tw(
            "h-4 w-4 shrink-0 rounded border-slate-300 text-indigo-600 shadow-sm transition "
            "focus:ring-2 focus:ring-indigo-500/40 disabled:cursor-not-allowed disabled:opacity-50 "
            "dark:border-slate-600 dark:bg-slate-800",
            props.get("base_class"),
        )
        super().__init__(**props)

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        attrs: dict[str, Any] = {"value": value_of(self.source_value, "on")}
        if value_of(self.source_checked, False):
            attrs["checked"] = True
        if value_of(self.source_disabled, False):
            attrs["disabled"] = True
        return attrs

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        if self.label is None and not self.help_text:
            return html
        text = ""
        if self.label is not None:
            text = f'<span class="text-sm text-slate-700 dark:text-slate-200">{escape(self.label)}</span>'
        elif self.help_text:
            text = f'<span class="text-sm text-slate-500">{escape(self.help_text)}</span>'
        return (
            f'<label for="{escape(uid)}" class="inline-flex cursor-pointer items-start gap-2.5 leading-5">'
            f"{html}{text}</label>"
        )


class CheckboxGroup(Component):
    tag = "div"

    def __init__(
        self,
        items: Sequence[Any] | None = None,
        *,
        values: Sequence[Any] | None = None,
        name: str | None = None,
        label: Any = None,
        help_text: Any = None,
        columns: int = 1,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.items = _options(items)
        self.values = {str(v) for v in (values or [])}
        self.name = name
        self.label = label
        self.help_text = help_text
        self.columns = columns
        if on_change is not None:
            props["on_change"] = on_change
        props["base_class"] = tw(
            "grid gap-2", f"grid-cols-{columns}", props.get("base_class")
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        parts = [
            Checkbox(
                label, checked=value in self.values, value=value, name=self.name, disabled=disabled
            ).render(ctx, ctx.child(path, index))
            for index, (value, label, disabled) in enumerate(self.items)
        ]
        body = "".join(parts)
        if self.label:
            uid = ctx.uid(path, self.key, self.explicit_id)
            return field_shell(
                f'<div class="{self.classes(ctx, uid)}">{body}</div>',
                uid,
                label=self.label,
                help_text=self.help_text,
            )
        return body

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, self.handlers, [str(index) for index in range(len(self.items))])
        return super().render(ctx, path)


class Radio(Component):
    tag = "input"
    void = True

    def __init__(
        self,
        label: Any = None,
        *,
        checked: bool = False,
        value: Any = "on",
        name: str | None = "radio",
        disabled: bool = False,
        help_text: Any = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.help_text = help_text
        props.setdefault("type", "radio")
        props["value"] = value
        if checked:
            props["checked"] = True
        if disabled:
            props["disabled"] = True
        if name:
            props["name"] = name
        props["base_class"] = tw(
            "h-4 w-4 shrink-0 border-slate-300 text-indigo-600 shadow-sm transition "
            "focus:ring-2 focus:ring-indigo-500/40 disabled:cursor-not-allowed disabled:opacity-50 "
            "dark:border-slate-600 dark:bg-slate-800",
            props.get("base_class"),
        )
        super().__init__(**props)

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        if self.label is None and not self.help_text:
            return html
        text = f'<span class="text-sm text-slate-700 dark:text-slate-200">{escape(self.label)}</span>'
        hint = (
            f'<span class="block text-xs text-slate-500 dark:text-slate-400">{escape(self.help_text)}</span>'
            if self.help_text
            else ""
        )
        return (
            f'<label for="{escape(uid)}" class="inline-flex cursor-pointer items-start gap-2.5 leading-5">'
            f'{html}<span class="flex flex-col">{text}{hint}</span></label>'
        )


class RadioGroup(Component):
    tag = "div"

    def __init__(
        self,
        items: Sequence[Any] | None = None,
        *,
        value: Any = "",
        name: str = "radio",
        label: Any = None,
        help_text: Any = None,
        cards: bool = False,
        columns: int = 1,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.items = _options(items)
        self.value = "" if value is None else str(value)
        self.name = name
        self.label = label
        self.help_text = help_text
        self.cards = cards
        self.columns = columns
        if on_change is not None:
            props["on_change"] = on_change
        props["base_class"] = tw(
            "grid gap-2", f"grid-cols-{columns}", props.get("base_class")
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        parts: list[str] = []
        for index, (value, label, disabled) in enumerate(self.items):
            selected = value == self.value
            if self.cards:
                parts.append(
                    '<label class="flex cursor-pointer items-start gap-3 rounded-xl border p-3 transition '
                    + ("border-indigo-500 bg-indigo-50/70 ring-1 ring-indigo-500 dark:bg-indigo-500/10"
                       if selected else
                       "border-slate-200 hover:border-slate-300 dark:border-slate-700 dark:hover:border-slate-600")
                    + '">'
                    + f'<input type="radio" id="{escape(uid)}-{index}" name="{escape(self.name)}" '
                    + f'value="{escape(value)}"'
                    + (" checked" if selected else "")
                    + (" disabled" if disabled else "")
                    + ' data-iui-on="change" class="mt-0.5 h-4 w-4 text-indigo-600 '
                      'focus:ring-indigo-500/40 dark:bg-slate-800"/>'
                    + f'<span class="text-sm font-medium text-slate-800 dark:text-slate-100">{escape(label)}</span>'
                    + "</label>"
                )
            else:
                radio = Radio(label, checked=selected, value=value, name=self.name, disabled=disabled)
                parts.append(radio.render(ctx, ctx.child(path, index)))
        body = "".join(parts)
        if self.label:
            return field_shell(
                f'<div class="{self.classes(ctx, uid)}">{body}</div>', uid,
                label=self.label, help_text=self.help_text,
            )
        return body

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        for event, handler in self.handlers.items():
            for index in range(len(self.items)):
                ctx.bind(f"{uid}-{index}", event, handler)
        return super().render(ctx, path)


class Switch(Component):
    tag = "input"
    void = True

    def __init__(
        self,
        label: Any = None,
        *,
        checked: bool = False,
        name: str | None = None,
        disabled: bool = False,
        size: str = "md",
        help_text: Any = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.help_text = help_text
        self.switch_size = size
        self.source_checked = checked
        self.source_disabled = disabled
        props.setdefault("type", "checkbox")
        props["role"] = "switch"
        if name:
            props["name"] = name
        props["base_class"] = "peer sr-only"
        super().__init__(**props)

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        attrs: dict[str, Any] = {}
        if value_of(self.source_checked, False):
            attrs["checked"] = True
        if value_of(self.source_disabled, False):
            attrs["disabled"] = True
        return attrs

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        dims = {"sm": ("h-5 w-9", "h-4 w-4", "peer-checked:[&>span]:translate-x-4"),
                "md": ("h-6 w-11", "h-5 w-5", "peer-checked:[&>span]:translate-x-5"),
                "lg": ("h-7 w-13", "h-6 w-6", "peer-checked:[&>span]:translate-x-6")}
        track, knob, shift = dims.get(self.switch_size, dims["md"])
        # ``peer-checked:[&>span]:…`` tiene que ir en el track: es el hermano del
        # input. En el knob (nieto) el selector `~ span > span` no aplica.
        body = (
            f'<span class="relative inline-flex {track} shrink-0 items-center rounded-full bg-slate-300 '
            f'transition peer-checked:bg-indigo-600 peer-focus-visible:ring-2 peer-focus-visible:ring-indigo-500/40 '
            f'peer-disabled:opacity-50 dark:bg-slate-700 {shift}">'
            f'<span class="{knob} translate-x-0.5 rounded-full bg-white shadow transition"></span></span>'
        )
        text = ""
        if self.label is not None or self.help_text:
            text = '<span class="flex flex-col">'
            if self.label is not None:
                text += f'<span class="text-sm font-medium text-slate-800 dark:text-slate-100">{escape(self.label)}</span>'
            if self.help_text:
                text += f'<span class="text-xs text-slate-500 dark:text-slate-400">{escape(self.help_text)}</span>'
            text += "</span>"
        return (
            f'<label for="{escape(uid)}" class="inline-flex cursor-pointer items-center gap-3">'
            f"{html}{body}{text}</label>"
        )


class Slider(Component):
    tag = "input"
    void = True

    def __init__(
        self,
        value: Any = 50,
        *,
        min: Any = 0,
        max: Any = 100,
        step: Any = 1,
        label: Any = None,
        show_value: bool = True,
        unit: str = "",
        live: bool = False,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.show_value = show_value
        self.unit = unit
        self.current = value_of(value, 50)
        props.setdefault("type", "range")
        props["value"] = value
        props["min"] = min
        props["max"] = max
        props["step"] = step
        if on_change is not None:
            props["on_change"] = on_change
            if live:
                props["on_input"] = on_change
        props["base_class"] = tw(
            "h-2 w-full cursor-pointer appearance-none rounded-full bg-slate-200 accent-indigo-600 "
            "dark:bg-slate-700",
            props.get("base_class"),
        )
        super().__init__(**props)

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        head = ""
        if self.label or self.show_value:
            head = (
                '<div class="mb-1.5 flex items-center justify-between text-sm">'
                f'<span class="font-medium text-slate-700 dark:text-slate-200">{escape(self.label or "")}</span>'
                + (
                    f'<span class="font-mono text-xs text-slate-500 dark:text-slate-400">'
                    f"{escape(self.current)}{escape(self.unit)}</span>"
                    if self.show_value
                    else ""
                )
                + "</div>"
            )
        return f'<div class="flex flex-col">{head}{html}</div>'


class RangeSlider(Component):
    """Dos deslizadores (mínimo y máximo) para representar un rango."""

    tag = "div"

    def __init__(
        self,
        low: Any = 20,
        high: Any = 80,
        *,
        min: Any = 0,
        max: Any = 100,
        step: Any = 1,
        label: Any = None,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.low, self.high = low, high
        self.min, self.max, self.step = min, max, step
        self.label = label
        if on_change is not None:
            props["on_change"] = on_change
        props["base_class"] = tw("flex flex-col gap-3", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        low = Slider(self.low, min=self.min, max=self.max, step=self.step, label="Mínimo", unit="")
        high = Slider(self.high, min=self.min, max=self.max, step=self.step, label="Máximo", unit="")
        head = (
            f'<div class="flex items-center justify-between text-sm font-medium text-slate-700 dark:text-slate-200">'
            f'<span>{escape(self.label or "Rango")}</span>'
            f'<span class="font-mono text-xs text-slate-500">{escape(self.low)} – {escape(self.high)}</span></div>'
        )
        body = (
            f'<div class="flex items-center gap-4">'
            f"{low.render(ctx, f'{uid}-lo')}"
            f"{high.render(ctx, f'{uid}-hi')}"
            f"</div>"
        )
        for which in ("lo", "hi"):
            for event, handler in self.handlers.items():
                ctx.bind(f"{uid}-{which}", event, handler)
        return head + body


class _DateBase(Input):
    def __init__(self, value: Any = "", **props: Any) -> None:
        props.setdefault("icon", "calendar")
        super().__init__(value, **props)


class DateInput(_DateBase):
    input_type = "date"


class TimeInput(_DateBase):
    input_type = "time"

    def __init__(self, value: Any = "", **props: Any) -> None:
        props.setdefault("icon", "clock")
        super().__init__(value, **props)


class DateTimeInput(_DateBase):
    input_type = "datetime-local"


class MonthInput(_DateBase):
    input_type = "month"


class WeekInput(_DateBase):
    input_type = "week"


class DateRangeInput(Component):
    tag = "div"

    def __init__(
        self,
        start: Any = "",
        end: Any = "",
        *,
        label: Any = None,
        start_label: str = "Desde",
        end_label: str = "Hasta",
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.start, self.end = start, end
        self.label = label
        self.start_label = start_label
        self.end_label = end_label
        if on_change is not None:
            props["on_change"] = on_change
        props["base_class"] = tw("flex flex-col gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        a = DateInput(self.start, label=self.start_label)
        b = DateInput(self.end, label=self.end_label)
        bind_many(ctx, uid, self.handlers, ["0", "1"])
        head = (
            f'<span class="text-sm font-medium text-slate-700 dark:text-slate-200">{escape(self.label)}</span>'
            if self.label
            else ""
        )
        return (
            f"{head}<div class=\"grid grid-cols-2 gap-3\">"
            f"{a.render(ctx, ctx.child(path, 0))}{b.render(ctx, ctx.child(path, 1))}</div>"
        )


class ColorInput(Component):
    tag = "div"

    def __init__(
        self,
        value: str = "#4f46e5",
        *,
        label: Any = None,
        name: str | None = None,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.value = value or "#4f46e5"
        self.label = label
        self.name = name
        if on_change is not None:
            props["on_change"] = on_change
            props["on_input"] = on_change
        props["base_class"] = tw("flex flex-col gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        picker = (
            f'<input type="color" id="{escape(uid)}" value="{escape(self.value)}"'
            + (f' name="{escape(self.name)}"' if self.name else "")
            + ' data-iui-on="input,change"'
            ' class="h-10 w-14 cursor-pointer rounded-lg border border-slate-300 bg-white p-1 '
            'dark:border-slate-700 dark:bg-slate-900"/>'
        )
        hexbox = (
            f'<input type="text" value="{escape(self.value)}" data-iui-sync="{escape(uid)}" '
            'class="h-10 w-32 rounded-lg border border-slate-300 bg-white px-3 font-mono text-sm '
            'uppercase text-slate-800 shadow-sm focus:border-indigo-500 focus:ring-2 '
            'focus:ring-indigo-500/30 focus:outline-none dark:border-slate-700 dark:bg-slate-900 '
            'dark:text-slate-100"/>'
        )
        body = f'<div class="flex items-center gap-2">{picker}{hexbox}</div>'
        return field_shell(body, uid, label=self.label)


class FileInput(Component):
    tag = "input"
    void = True

    def __init__(
        self,
        *,
        accept: str | None = None,
        multiple: bool = False,
        label: Any = None,
        help_text: Any = None,
        name: str | None = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.help_text = help_text
        props.setdefault("type", "file")
        if accept:
            props["accept"] = accept
        if multiple:
            props["multiple"] = True
        if name:
            props["name"] = name
        props["data"] = {**(props.get("data") or {}), "iui-upload": "true"}
        props["base_class"] = tw(
            "block w-full cursor-pointer rounded-lg border border-slate-300 bg-white text-sm "
            "file:mr-3 file:cursor-pointer file:border-0 file:bg-slate-100 file:px-3 file:py-2 "
            "file:text-sm file:font-medium file:text-slate-700 hover:file:bg-slate-200 "
            "dark:border-slate-700 dark:bg-slate-900 dark:file:bg-slate-800 dark:file:text-slate-200 "
            "text-slate-500 dark:text-slate-400",
            props.get("base_class"),
        )
        super().__init__(**props)

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        return field_shell(html, uid, label=self.label, help_text=self.help_text)


class Dropzone(Component):
    tag = "div"

    def __init__(
        self,
        *children: Any,
        label: Any = "Arrastra archivos aquí",
        hint: Any = "o haz clic para seleccionarlos",
        accept: str | None = None,
        multiple: bool = True,
        **props: Any,
    ) -> None:
        self.label = label
        self.hint = hint
        self.accept = accept
        self.multiple = multiple
        props["base_class"] = tw(
            "relative flex flex-col items-center justify-center gap-2 rounded-2xl border-2 "
            "border-dashed border-slate-300 bg-slate-50 px-6 py-10 text-center transition "
            "hover:border-indigo-400 hover:bg-indigo-50/40 dark:border-slate-700 dark:bg-slate-900 "
            "dark:hover:border-indigo-500 dark:hover:bg-indigo-500/5",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        hidden = (
            f'<input type="file" id="{escape(uid)}" class="absolute inset-0 cursor-pointer opacity-0"'
            + (f' accept="{escape(self.accept)}"' if self.accept else "")
            + (" multiple" if self.multiple else "")
            + ' data-iui-upload="true" data-iui-on="change"/>'
        )
        inner = (
            '<span class="pointer-events-none flex flex-col items-center gap-1">'
            + Icon("upload", size=8).render(ctx, uid + "-ic")
            + f'<span class="mt-1 text-sm font-medium text-slate-700 dark:text-slate-200">{escape(self.label)}</span>'
            f'<span class="text-xs text-slate-500 dark:text-slate-400">{escape(self.hint)}</span></span>'
        )
        return hidden + inner

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        return {"data-iui-dropzone": uid}


class OtpInput(Component):
    """Código de un solo uso: una caja por dígito con auto-avance."""

    tag = "div"

    def __init__(
        self,
        length: int = 6,
        *,
        value: str = "",
        label: Any = None,
        on_change: Any = None,
        size: str = "md",
        **props: Any,
    ) -> None:
        self.length = length
        self.value = (value or "").ljust(length)[:length]
        self.label = label
        self.size = size
        if on_change is not None:
            props["on_input"] = on_change
            props["on_change"] = on_change
        props["base_class"] = tw("flex flex-col gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        cell = {"sm": "h-10 w-9 text-base", "md": "h-12 w-11 text-lg", "lg": "h-14 w-13 text-xl"}.get(
            self.size, "h-12 w-11 text-lg"
        )
        boxes = []
        for index in range(self.length):
            digit = self.value[index].strip()
            next_id = f"{uid}-{index + 1}" if index + 1 < self.length else ""
            boxes.append(
                f'<input type="text" inputmode="numeric" maxlength="1" '
                f'id="{escape(uid)}-{index}" value="{escape(digit)}" '
                f'data-iui-on="input,change" data-iui-index="{index}"'
                + (f' data-iui-otp-next="{escape(next_id)}"' if next_id else "")
                + f' class="{cell} rounded-lg border border-slate-300 bg-white text-center font-mono '
                'font-semibold text-slate-900 shadow-sm focus:border-indigo-500 focus:ring-2 '
                'focus:ring-indigo-500/30 focus:outline-none dark:border-slate-700 dark:bg-slate-900 '
                'dark:text-slate-100"/>'
            )
            ctx.bind(f"{uid}-{index}", "input", self.handlers.get("input"))
            ctx.bind(f"{uid}-{index}", "change", self.handlers.get("change"))
        head = (
            f'<span class="text-sm font-medium text-slate-700 dark:text-slate-200">{escape(self.label)}</span>'
            if self.label
            else ""
        )
        return head + f'<div class="flex items-center gap-2">{"".join(boxes)}</div>'

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        for event, handler in self.handlers.items():
            for index in range(self.length):
                ctx.bind(f"{uid}-{index}", event, handler)
        return super().render(ctx, path)


class Rating(Component):
    tag = "div"

    def __init__(
        self,
        value: int = 0,
        *,
        max_stars: int = 5,
        label: Any = None,
        on_change: Any = None,
        read_only: bool = False,
        size: int = 6,
        **props: Any,
    ) -> None:
        self.value = int(value or 0)
        self.max_stars = max_stars
        self.label = label
        self.read_only = read_only
        self.star_size = size
        if on_change is not None:
            props["on_change"] = on_change
        props["base_class"] = tw("flex flex-col gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, self.handlers, [f"i{index}" for index in range(1, self.max_stars + 1)])
        stars = []
        for index in range(1, self.max_stars + 1):
            filled = index <= self.value
            color = "text-amber-400" if filled else "text-slate-300 dark:text-slate-600"
            if self.read_only:
                stars.append(f'<span class="{color}">{Icon("star", size=self.star_size).render(ctx, f"{uid}-{index}")}</span>')
            else:
                stars.append(
                    f'<button type="button" id="{escape(uid)}-i{index}" data-iui-emit="change" '
                    f'data-iui-value="{index}" data-iui-cast="int" '
                    f'aria-label="{index} de {self.max_stars}" '
                    f'class="{color} transition hover:scale-110 hover:text-amber-500">'
                    f'{Icon("star", size=self.star_size).render(ctx, f"{uid}-{index}")}</button>'
                )
        head = (
            f'<span class="text-sm font-medium text-slate-700 dark:text-slate-200">{escape(self.label)}</span>'
            if self.label
            else ""
        )
        return head + f'<div class="flex items-center gap-1">{"".join(stars)}</div>'


class TagInput(Component):
    tag = "div"

    def __init__(
        self,
        tags: Sequence[str] | None = None,
        *,
        label: Any = None,
        placeholder: str = "Añadir y pulsar Enter",
        on_add: Any = None,
        on_remove: Any = None,
        **props: Any,
    ) -> None:
        self.tags = [str(tag) for tag in (tags or [])]
        self.label = label
        self.placeholder = placeholder
        if on_add is not None:
            props["on_enter"] = on_add
        self.on_remove = on_remove
        props["base_class"] = tw("flex flex-col gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, {"change": self.on_remove}, [f"i{index}" for index in range(len(self.tags))])
        chips = "".join(
            f'<span class="inline-flex items-center gap-1 rounded-full bg-indigo-50 px-2.5 py-1 text-xs '
            f'font-medium text-indigo-700 ring-1 ring-inset ring-indigo-200 dark:bg-indigo-500/15 '
            f'dark:text-indigo-300 dark:ring-indigo-500/30">{escape(tag)}'
            + (
                f'<button type="button" id="{escape(uid)}-i{index}" data-iui-emit="change" '
                f'data-iui-value="{escape(tag)}" aria-label="Quitar {escape(tag)}" '
                'class="rounded-full p-0.5 opacity-60 transition hover:bg-indigo-200/60 hover:opacity-100">'
                "✕</button>"
                if self.on_remove is not None
                else ""
            )
            + "</span>"
            for index, tag in enumerate(self.tags)
        )
        field = (
            f'<input type="text" id="{escape(uid)}-input" placeholder="{escape(self.placeholder)}" '
            'data-iui-on="enter" class="min-w-[8rem] flex-1 border-0 bg-transparent p-1 text-sm '
            'text-slate-900 placeholder:text-slate-400 focus:outline-none dark:text-slate-100"/>'
        )
        box = (
            f'<div class="flex flex-wrap items-center gap-2 rounded-lg border border-slate-300 bg-white '
            f'p-2 shadow-sm focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/30 '
            f'dark:border-slate-700 dark:bg-slate-900">{chips}{field}</div>'
        )
        ctx.bind(f"{uid}-input", "enter", self.handlers.get("enter"))
        return field_shell(box, f"{uid}-input", label=self.label)


class SegmentedControl(Component):
    tag = "div"

    def __init__(
        self,
        items: Sequence[Any] | None = None,
        *,
        value: Any = "",
        on_change: Any = None,
        label: Any = None,
        full_width: bool = False,
        **props: Any,
    ) -> None:
        self.items = _options(items)
        self.value = "" if value is None else str(value)
        self.label = label
        self.full_width = full_width
        if on_change is not None:
            props["on_change"] = on_change
        props["role"] = "tablist"
        props["base_class"] = tw(
            "inline-flex items-center gap-1 rounded-xl bg-slate-100 p-1 dark:bg-slate-800",
            "w-full" if full_width else "",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, self.handlers, [f"i{index}" for index in range(len(self.items))])
        buttons = []
        for index, (value, label, disabled) in enumerate(self.items):
            active = value == self.value
            buttons.append(
                f'<button type="button" id="{escape(uid)}-i{index}" role="tab" '
                f'aria-selected="{"true" if active else "false"}" '
                f'data-iui-emit="change" data-iui-value="{escape(value)}"'
                + (" disabled" if disabled else "")
                + ' class="'
                + ("flex-1 " if self.full_width else "")
                + "rounded-lg px-3 py-1.5 text-sm font-medium transition "
                + ("bg-white text-slate-900 shadow-sm dark:bg-slate-900 dark:text-white"
                   if active
                   else "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100")
                + f'">{escape(label)}</button>'
            )
        body = "".join(buttons)
        if self.label:
            return field_shell(body, ctx.uid(path, self.key, self.explicit_id), label=self.label)
        return body


class ToggleGroup(Component):
    tag = "div"

    def __init__(
        self,
        items: Sequence[Any] | None = None,
        *,
        values: Sequence[Any] | None = None,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.items = _options(items)
        self.values = {str(v) for v in (values or [])}
        if on_change is not None:
            props["on_change"] = on_change
        props["role"] = "group"
        props["base_class"] = tw("inline-flex flex-wrap items-center gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, self.handlers, [f"i{index}" for index in range(len(self.items))])
        buttons = []
        for index, (value, label, disabled) in enumerate(self.items):
            active = value in self.values
            buttons.append(
                f'<button type="button" id="{escape(uid)}-i{index}" data-iui-emit="change" '
                f'data-iui-value="{escape(value)}"'
                + (" disabled" if disabled else "")
                + ' aria-pressed="'
                + ("true" if active else "false")
                + '" class="inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm '
                'font-medium transition '
                + ("border-indigo-500 bg-indigo-50 text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-300"
                   if active
                   else "border-slate-300 text-slate-600 hover:bg-slate-50 dark:border-slate-700 "
                        "dark:text-slate-300 dark:hover:bg-slate-800")
                + f'">{escape(label)}</button>'
            )
        return "".join(buttons)


class HiddenInput(Component):
    tag = "input"
    void = True

    def __init__(self, value: Any = "", *, name: str | None = None, **props: Any) -> None:
        props.setdefault("type", "hidden")
        props["value"] = "" if value is None else value
        if name:
            props["name"] = name
        super().__init__(**props)


class Form(Component):
    tag = "form"

    def __init__(
        self,
        *children: Any,
        on_submit: Any = None,
        layout: str = "stack",
        gap: int = 4,
        **props: Any,
    ) -> None:
        self.fields = list(children)
        if on_submit is not None:
            props["on_submit"] = on_submit
        props.setdefault("novalidate", True)
        props["base_class"] = tw(
            "flex flex-col" if layout != "grid" else "grid grid-cols-12",
            utility("gap", gap),
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        return render_children(self.fields, ctx, path)


class FormField(Component):
    """Envuelve un control con etiqueta, ayuda y error."""

    tag = "div"

    def __init__(
        self,
        *children: Any,
        label: Any = None,
        help_text: Any = None,
        error: Any = None,
        required: bool = False,
        for_: str | None = None,
        horizontal: bool = False,
        **props: Any,
    ) -> None:
        self.field_label = label
        self.help_text = help_text
        self.error = error
        self.required = required
        self.for_ = for_
        self.horizontal = horizontal
        props["base_class"] = tw(
            "flex flex-col gap-1.5",
            "sm:grid sm:grid-cols-[10rem_1fr] sm:items-center sm:gap-4" if horizontal else "",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        head = ""
        if self.field_label:
            mark = '<span class="text-rose-500">*</span>' if self.required else ""
            target = f' for="{escape(self.for_)}"' if self.for_ else ""
            head = (
                f'<label{target} class="flex items-center gap-1 text-sm font-medium text-slate-700 '
                f'dark:text-slate-200">{escape(self.field_label)}{mark}</label>'
            )
        hint = ""
        if self.error:
            hint = f'<p class="text-xs font-medium text-rose-600 dark:text-rose-400">{escape(self.error)}</p>'
        elif self.help_text:
            hint = f'<p class="text-xs text-slate-500 dark:text-slate-400">{escape(self.help_text)}</p>'
        body = render_children(self.children, ctx, path)
        return f'{head}<div class="flex flex-col gap-1.5">{body}{hint}</div>'


class Fieldset(Component):
    tag = "fieldset"

    def __init__(self, *children: Any, legend: Any = None, **props: Any) -> None:
        self.legend = legend
        props["base_class"] = tw(
            "min-w-0 rounded-xl border border-slate-200 p-4 dark:border-slate-800",
            "flex flex-col gap-4",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        head = (
            f'<legend class="px-1 text-sm font-semibold text-slate-800 dark:text-slate-100">'
            f"{escape(self.legend)}</legend>"
            if self.legend
            else ""
        )
        return head + render_children(self.children, ctx, path)


class ValidationSummary(Component):
    tag = "div"

    def __init__(self, errors: Sequence[Any] | None = None, title: Any = "Revisa los siguientes campos", **props: Any) -> None:
        self.errors = list(errors or [])
        props["base_class"] = tw(
            "rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-900 "
            "dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200",
            props.get("base_class"),
        )
        # `title` es el encabezado del resumen: lo guarda `Component`.
        super().__init__(title=title, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        if not self.errors:
            return ""
        items = "".join(f'<li class="ml-4 list-disc">{escape(error)}</li>' for error in self.errors)
        return f'<p class="font-semibold">{escape(self.title)}</p><ul class="mt-2 space-y-1">{items}</ul>'


class Stepper(Component):
    """Contador numérico con botones − / + enlazados al servidor."""

    tag = "div"

    def __init__(
        self,
        value: int = 0,
        *,
        min: int | None = None,
        max: int | None = None,
        step: int = 1,
        label: Any = None,
        on_click: Any = None,
        **props: Any,
    ) -> None:
        self.value = int(value)
        self.min, self.max, self.step_value = min, max, step
        self.label = label
        if on_click is not None:
            props["on_click"] = on_click
        props["base_class"] = tw("flex flex-col gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        dec = (self.min is None or self.value - self.step_value >= self.min)
        inc = (self.max is None or self.value + self.step_value <= self.max)
        btn = (
            "flex h-9 w-9 items-center justify-center rounded-lg border border-slate-300 text-slate-600 "
            "transition hover:bg-slate-100 disabled:opacity-40 dark:border-slate-700 dark:text-slate-300 "
            "dark:hover:bg-slate-800"
        )
        ctx.bind(f"{uid}-dec", "click", self.handlers.get("click"))
        ctx.bind(f"{uid}-inc", "click", self.handlers.get("click"))
        return (
            '<div class="inline-flex items-center gap-1">'
            f'<button type="button" id="{escape(uid)}-dec" data-iui-emit="click" data-iui-value="-{self.step_value}" '
            f'data-iui-cast="int" class="{btn}"{" disabled" if not dec else ""}>−</button>'
            f'<span class="min-w-12 rounded-lg border border-slate-200 bg-slate-50 px-3 py-1.5 text-center '
            f'font-mono text-sm text-slate-800 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100">'
            f"{self.value}</span>"
            f'<button type="button" id="{escape(uid)}-inc" data-iui-emit="click" data-iui-value="{self.step_value}" '
            f'data-iui-cast="int" class="{btn}"{" disabled" if not inc else ""}>+</button>'
            "</div>"
        )
