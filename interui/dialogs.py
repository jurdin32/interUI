"""Ventanas modales: avisos, confirmaciones, entradas y diálogos propios.

Todos los diálogos son componentes que se pintan **encima** de la página y viven
en el estado de la aplicación, así que se abren y cierran desde Python sin
bloquear el canal de eventos:

```python
from interui import dialog

dialog.info("Proceso terminado")
dialog.confirm("¿Eliminar el proyecto?", on_accept=borrar)
dialog.input("Nombre del proyecto", title="Nuevo", on_accept=crear)
dialog.custom(ui.text("contenido"), title="A medida", buttons=[("Hecho", cerrar)])
```

Tipos incluidos: ``show``, ``info``, ``success``, ``warning``, ``error``,
``critical``, ``confirm``, ``input``, ``form`` y ``custom``.

Handlers:

* ``on_accept`` recibe el ``UIEvent``; en diálogos con campos, los valores están
  en ``evento.data["values"]`` (y en ``evento.value`` si hay un solo campo).
* Puedes pasar una señal en lugar de una función: ``dialog.input(..., on_accept=nombre)``.
* ``on_cancel`` / ``on_close`` se ejecutan al cancelar, con Escape o al pulsar el fondo.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Sequence

from .base import Component, render_children
from .context import RenderContext
from .controls.buttons import Button
from .controls.tags import Div
from .events import UIEvent, invoke
from .html import escape
from .icons import Icon
from .style import tw

__all__ = [
    "Dialog", "DialogHost", "DialogAPI", "dialog",
    "show", "info", "success", "warning", "error", "critical", "alert",
    "confirm", "input", "form", "custom", "close",
]

# nivel -> (icono, color del icono, color del botón principal)
LEVELS: dict[str, tuple[str, str, str]] = {
    "info": ("info", "bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300", "primary"),
    "success": ("check-circle", "bg-emerald-100 text-emerald-700 dark:bg-emerald-500/15 dark:text-emerald-300", "success"),
    "warning": ("alert", "bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300", "warning"),
    "error": ("x-circle", "bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300", "danger"),
    "critical": ("alert", "bg-rose-100 text-rose-700 dark:bg-rose-500/15 dark:text-rose-300", "danger"),
    "question": ("help", "bg-indigo-100 text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-300", "primary"),
    "neutral": ("info", "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300", "primary"),
}

WIDTHS = {
    "xs": "max-w-xs",
    "sm": "max-w-sm",
    "md": "max-w-md",
    "lg": "max-w-lg",
    "xl": "max-w-2xl",
    "full": "max-w-4xl",
}


class Dialog(Component):
    """Diálogo modal declarativo.

    Normalmente se crea con los atajos (``dialog.info``, ``dialog.confirm``…), pero
    puedes instanciarlo directamente para tener control total::

        Dialog(
            ui.text("¿Continuar?"),
            title="Aviso",
            level="warning",
            buttons=[("Cancelar", None, "outline"), ("Continuar", aceptar, "primary")],
        )
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        title: Any = None,
        message: Any = None,
        kind: str = "show",
        level: str | None = None,
        icon: str | None = None,
        buttons: Sequence[Any] | None = None,
        fields: Sequence[Any] | None = None,
        values: dict[str, Any] | None = None,
        on_accept: Callable[..., Any] | None = None,
        on_cancel: Callable[..., Any] | None = None,
        on_close: Callable[..., Any] | None = None,
        accept_label: str = "Aceptar",
        cancel_label: str = "Cancelar",
        close_label: str = "Cerrar",
        closable: bool = True,
        dismissible: bool = True,
        width: str = "md",
        scrollable: bool = False,
        **props: Any,
    ) -> None:
        self.dialog_title = title
        self.message = message
        self.kind = kind
        self.level = level or _default_level(kind)
        self.icon = icon or LEVELS.get(self.level, LEVELS["neutral"])[0]
        self.buttons = list(buttons) if buttons is not None else None
        self.fields = list(fields or [])
        self.values = dict(values or {})
        self.on_accept = on_accept
        self.on_cancel = on_cancel
        self.on_close = on_close
        self.accept_label = accept_label
        self.cancel_label = cancel_label
        self.close_label = close_label
        self.closable = closable
        self.dismissible = dismissible
        self.width = width
        self.scrollable = scrollable
        self.app = props.pop("_app", None)
        if dismissible:
            props.setdefault("on_escape", self._escape)
        props["role"] = "dialog"
        props["aria"] = {"modal": "true", **(props.get("aria") or {})}
        props["base_class"] = tw(
            "iui-dialog fixed inset-0 z-[60] flex items-center justify-center p-4",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    # -- ciclo de vida ---------------------------------------------------
    def close(self) -> "Dialog":
        """Cierra el diálogo (lo quita del estado de la aplicación)."""
        application = self.app or _current_app()
        if application is not None:
            application.close_dialog(self)
        return self

    # -- handlers --------------------------------------------------------
    def _finish(self, event: UIEvent) -> None:
        values = dict(event.data.get("form") or {})
        if values:
            event.data["values"] = values
            if len(values) == 1 and event.value is None:
                event.value = next(iter(values.values()))
        self.close()
        if self.on_accept is not None:
            invoke(self.on_accept, event)

    def _cancel(self, event: UIEvent | None = None) -> None:
        self.close()
        if self.on_cancel is not None:
            invoke(self.on_cancel, event or UIEvent(id=self.explicit_id or "dialog", event="cancel"))

    def _escape(self, event: Any = None) -> None:
        self._cancel(event if isinstance(event, UIEvent) else None)

    def _dismiss(self, event: Any = None) -> None:
        self.close()
        if self.on_close is not None:
            invoke(self.on_close, event if isinstance(event, UIEvent) else UIEvent(id="dialog", event="close"))

    # -- render ----------------------------------------------------------
    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        backdrop = Div(
            id=f"{uid}-backdrop",
            base_class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm",
            aria={"hidden": "true"},
            **({"on_click": self._dismiss} if self.dismissible else {}),
        )
        panel = Div(
            base_class=tw(
                "relative z-10 flex w-full flex-col overflow-hidden rounded-2xl bg-white "
                "shadow-2xl ring-1 ring-slate-900/5 dark:bg-slate-900 dark:ring-slate-700/40 "
                "iui-dialog-panel",
                WIDTHS.get(self.width, WIDTHS["md"]),
                "max-h-[85vh]" if self.scrollable else "",
            ),
            **({"aria": {"labelledby": f"{uid}-title"}} if self.dialog_title else {}),
        )
        if self.dialog_title or self.icon:
            panel(self._header(ctx, uid))

        body = Div(
            base_class=tw(
                "flex flex-col gap-3 px-5 py-4",
                "overflow-y-auto" if self.scrollable else "",
            )
        )
        body(*self._body(ctx, path))
        footer = Div(
            base_class="flex flex-wrap items-center justify-end gap-2 border-t border-slate-100 "
            "px-5 py-3 dark:border-slate-800"
        )

        if self.fields:
            footer(self._cancel_button(uid), self._accept_button(uid, submit=True))
            form = _Tag(
                "form",
                body,
                footer,
                id=f"{uid}-form",
                base_class="flex flex-col",
                novalidate=True,
                on_submit=self._finish,
            )
            panel(form)
        else:
            footer(*self._simple_buttons(ctx, uid))
            panel(body, footer)

        return backdrop.render(ctx, f"{path}-bd") + panel.render(ctx, f"{path}-pn")

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        attrs: dict[str, Any] = {}
        if self.dialog_title:
            attrs["data-dialog-title"] = True
        return attrs

    def reveal(self, ctx: RenderContext, path: str) -> str:  # pragma: no cover - sin uso
        return ""

    def _header(self, ctx: RenderContext, uid: str) -> Component:
        tone = LEVELS.get(self.level, LEVELS["neutral"])[1]
        box = Div(base_class="flex items-start gap-3 border-b border-slate-100 px-5 py-4 "
                              "dark:border-slate-800")
        if self.icon:
            badge = Div(
                base_class=f"flex h-10 w-10 shrink-0 items-center justify-center rounded-full {tone}"
            )(Icon(self.icon, size=5))
            box(badge)
        if self.dialog_title:
            title = _Tag(
                "h2",
                self.dialog_title,
                id=f"{uid}-title",
                base_class="min-w-0 truncate text-base font-semibold text-slate-900 dark:text-white",
            )
            box(Div(base_class="flex min-w-0 flex-col gap-0.5")(title))
        if self.closable:
            from .controls.buttons import IconButton

            box(
                IconButton(
                    "x",
                    id=f"{uid}-x",
                    label="Cerrar",
                    size="sm",
                    variant="ghost",
                    class_="ml-auto",
                    on_click=self._dismiss,
                )
            )
        return box

    def _body(self, ctx: RenderContext, path: str) -> list[Component]:
        items: list[Component] = []
        if self.message is not None:
            items.append(
                Component(
                    tag="p",
                    base_class="text-sm leading-relaxed text-slate-600 dark:text-slate-300",
                )(self.message)
            )
        if self.fields:
            items.extend(self._fields(ctx, path))
        items.extend(self.children)
        return items

    def _fields(self, ctx: RenderContext, path: str) -> list[Component]:
        from .controls.inputs import Input, Textarea

        out: list[Component] = []
        for index, field in enumerate(self.fields):
            if isinstance(field, Component):
                out.append(field)
                continue
            options = dict(field)
            name = str(options.pop("name", f"campo{index + 1}"))
            kind = str(options.pop("type", "text"))
            label = options.pop("label", name.capitalize())
            value = self.values.get(name, options.pop("value", ""))
            if kind in ("textarea", "multiline"):
                out.append(Textarea(value, label=label, name=name, **options))
            else:
                out.append(Input(value, label=label, name=name, **{"type": kind, **options}))
        return out

    def _cancel_button(self, uid: str) -> Component:
        return Button(
            self.cancel_label,
            id=f"{uid}-cancel",
            variant="outline",
            on_click=self._cancel,
        )

    def _accept_button(self, uid: str, *, submit: bool) -> Component:
        variant = LEVELS.get(self.level, LEVELS["neutral"])[2]
        return Button(
            self.accept_label,
            id=f"{uid}-ok",
            variant=variant,
            submit=submit,
            on_click=None if submit else self._finish,
        )

    def _simple_buttons(self, ctx: RenderContext, uid: str) -> list[Component]:
        if self.buttons is not None:
            out: list[Component] = []
            for index, item in enumerate(self.buttons):
                label, handler, variant = _button_spec(item)
                out.append(
                    Button(
                        label,
                        id=f"{uid}-b{index}",
                        variant=variant,
                        on_click=handler or (lambda: None),
                    )
                )
            return out
        if self.kind in ("confirm", "input", "form"):
            return [self._cancel_button(uid), self._accept_button(uid, submit=False)]
        variant = LEVELS.get(self.level, LEVELS["neutral"])[2]
        return [
            Button(
                self.close_label,
                id=f"{uid}-close",
                variant=variant,
                on_click=self._dismiss,
            )
        ]

def _button_spec(item: Any) -> tuple[Any, Any, str]:
    if isinstance(item, (tuple, list)):
        label = item[0]
        handler = item[1] if len(item) > 1 else None
        variant = str(item[2]) if len(item) > 2 else "outline"
        return label, handler, variant
    return item, None, "outline"


def _variant_classes(variant: str) -> str:
    from .ui import BUTTON_VARIANTS

    return BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS["primary"])


def _default_level(kind: str) -> str:
    return {
        "info": "info",
        "show": "neutral",
        "success": "success",
        "warning": "warning",
        "error": "error",
        "critical": "critical",
        "confirm": "question",
        "input": "question",
        "form": "question",
        "custom": "neutral",
    }.get(kind, "neutral")


class _Tag(Component):
    """Componente con etiqueta arbitraria (form, p, fieldset…)."""

    def __init__(self, tag: str, *children: Any, **props: Any) -> None:
        self.tag = tag
        super().__init__(*children, **props)


class DialogHost(Component):
    """Contenedor de los diálogos activos. La aplicación lo inserta sola."""

    tag = "div"

    def __init__(self, *dialogs: Component, **props: Any) -> None:
        props["base_class"] = tw("relative z-[60]", props.get("base_class"))
        super().__init__(*dialogs, **props)


# ---------------------------------------------------------------------------
# API de conveniencia
# ---------------------------------------------------------------------------
class DialogAPI:
    """Atajos: ``dialog.info(...)``, ``dialog.confirm(...)``, ``dialog.input(...)``."""

    # -- avisos ----------------------------------------------------------
    def show(self, message: Any = None, **options: Any) -> Dialog:
        return self._open("show", "neutral", message, options)

    def info(self, message: Any = None, **options: Any) -> Dialog:
        return self._open("info", "info", message, options)

    def success(self, message: Any = None, **options: Any) -> Dialog:
        return self._open("success", "success", message, options)

    def warning(self, message: Any = None, **options: Any) -> Dialog:
        return self._open("warning", "warning", message, options)

    def error(self, message: Any = None, **options: Any) -> Dialog:
        return self._open("error", "error", message, options)

    def critical(self, message: Any = None, **options: Any) -> Dialog:
        return self._open("critical", "critical", message, options)

    def alert(self, message: Any = None, *, level: str = "info", **options: Any) -> Dialog:
        return self._open(level, level, message, options)

    # -- interacción -----------------------------------------------------
    def confirm(
        self,
        message: Any = None,
        *,
        title: Any = "¿Confirmar?",
        on_accept: Callable[..., Any] | None = None,
        on_cancel: Callable[..., Any] | None = None,
        **options: Any,
    ) -> Dialog:
        return self._open(
            "confirm", "question", message,
            {"title": title, "on_accept": on_accept, "on_cancel": on_cancel, **options},
        )

    def input(
        self,
        label: Any = "Valor",
        *,
        title: Any = "Introducir dato",
        value: Any = "",
        placeholder: str | None = None,
        name: str = "value",
        on_accept: Callable[..., Any] | None = None,
        on_cancel: Callable[..., Any] | None = None,
        **options: Any,
    ) -> Dialog:
        field = {"name": name, "label": label, "value": value}
        if placeholder:
            field["placeholder"] = placeholder
        return self._open(
            "input", "question", None,
            {
                "title": title,
                "fields": [field],
                "on_accept": on_accept,
                "on_cancel": on_cancel,
                "accept_label": options.pop("accept_label", "Aceptar"),
                **options,
            },
        )

    def form(
        self,
        fields: Sequence[Any],
        *,
        title: Any = "Formulario",
        on_accept: Callable[..., Any] | None = None,
        on_cancel: Callable[..., Any] | None = None,
        **options: Any,
    ) -> Dialog:
        return self._open(
            "form", "question", options.pop("message", None),
            {"title": title, "fields": fields, "on_accept": on_accept,
             "on_cancel": on_cancel, **options},
        )

    def custom(
        self,
        *children: Any,
        title: Any = None,
        buttons: Sequence[Any] | None = None,
        on_close: Callable[..., Any] | None = None,
        level: str = "neutral",
        **options: Any,
    ) -> Dialog:
        return self._open(
            "custom", level, options.pop("message", None),
            {"title": title, "buttons": buttons, "on_close": on_close,
             "children": children, **options},
        )

    def close(self, target: Dialog | None = None) -> None:
        application = _current_app()
        if application is not None:
            application.close_dialog(target)

    # -- interno ---------------------------------------------------------
    def _open(self, kind: str, level: str, message: Any, options: dict[str, Any]) -> Dialog:
        application = _current_app()
        children = options.pop("children", ())
        node = Dialog(
            *children,
            message=message,
            kind=kind,
            level=options.pop("level", level),
            _app=application,
            **options,
        )
        if application is not None:
            application.show_dialog(node)
        return node


def _current_app() -> Any:
    from .simple import current_app

    return current_app()


dialog = DialogAPI()

# Atajos de módulo equivalentes a `dialog.*`
show = dialog.show
info = dialog.info
success = dialog.success
warning = dialog.warning
error = dialog.error
critical = dialog.critical
alert = dialog.alert
confirm = dialog.confirm
input = dialog.input
form = dialog.form
custom = dialog.custom
close = dialog.close

_ = Iterable
