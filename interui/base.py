"""Componente base: árbol declarativo que se compila a HTML."""

from __future__ import annotations

from typing import Any, Callable, Iterable, Sequence

from .context import RenderContext
from .html import Markup, element, escape, flatten, is_safe
from .state import Signal
from .style import tw
from .theme import resolve_style_props

__all__ = ["Component", "Fragment", "render", "render_children", "bind_many"]

EVENT_PROPS = {
    "on_click": "click",
    "on_dblclick": "dblclick",
    "on_change": "change",
    "on_input": "input",
    "on_submit": "submit",
    "on_keydown": "keydown",
    "on_keyup": "keyup",
    "on_key": "keydown",
    "on_escape": "escape",
    "on_focus": "focus",
    "on_blur": "blur",
    "on_enter": "enter",
    "on_mouseenter": "mouseenter",
    "on_mouseleave": "mouseleave",
    "on_contextmenu": "contextmenu",
    "on_dragstart": "dragstart",
    "on_dragover": "dragover",
    "on_drop": "drop",
    "on_scroll": "scroll",
    "on_select": "select",
    "on_open": "open",
    "on_close": "close",
    "on_toggle": "toggle",
    "on_sort": "sort",
    "on_page": "page",
    "on_search": "search",
    "on_remove": "remove",
    "on_add": "add",
    "on_upload": "upload",
    "on_error": "error",
    "on_load": "load",
}

class Component:
    """Nodo del árbol de interfaz.

    Se instancia como ``Component(*hijos, **props)`` y se puede encadenar:
    ``Card("Hola")(Text("mundo"))``.
    """

    tag = "div"
    base_class = ""
    void = False

    def __init__(self, *children: Any, **props: Any) -> None:
        self.children: list[Any] = flatten(children)
        self.explicit_id: str | None = props.pop("id", None)
        self.key: Any = props.pop("key", None)
        self.class_: Any = props.pop("class_", None)
        self.style: Any = props.pop("style", None)
        self.visible: bool = props.pop("visible", True)
        self.when: Any = props.pop("when", True)
        self.aria: dict[str, Any] = props.pop("aria", None) or {}
        self.data: dict[str, Any] = props.pop("data", None) or {}
        extra_base = props.pop("base_class", None)
        self.hidden: bool = bool(props.pop("hidden", False))
        self.role: str | None = props.pop("role", None)
        # `title=` aquí es el atributo HTML; no debe pisar el título de contenido
        # que algunos controles (EmptyState, ListItem, TimelineItem…) ya fijaron.
        self.title: str | None = props.pop("title", getattr(self, "title", None))
        self.tabindex: Any = props.pop("tabindex", None)
        style_classes, style_declarations = resolve_style_props(props)
        if extra_base:
            self.base_class = tw(self.base_class, extra_base)
        if style_classes:
            self.base_class = tw(self.base_class, *style_classes)
        if style_declarations:
            self.style = _merge_style(self.style, style_declarations)
        self.handlers: dict[str, Callable[..., Any]] = {}
        self.props: dict[str, Any] = {}
        for name, value in props.items():
            event = EVENT_PROPS.get(name)
            if event is not None:
                if value is not None:
                    self.handlers[event] = value
            else:
                self.props[name] = value
        self._declared_events: list[str] = []

    # ------------------------------------------------------------------
    # construcción
    # ------------------------------------------------------------------
    def __call__(self, *children: Any, **options: Any) -> "Component":
        if options:
            names = ", ".join(sorted(options))
            raise TypeError(
                f"{type(self).__name__}(...)(...) no acepta opciones con nombre ({names}). "
                "Pásalas al constructor del componente."
            )
        self.children.extend(flatten(children))
        return self

    def add(self, *children: Any) -> "Component":
        return self.__call__(*children)

    def clone(self, **overrides: Any) -> "Component":
        import copy as _copy

        style_classes, style_declarations = resolve_style_props(overrides)
        twin = _copy.copy(self)
        twin.children = list(self.children)
        twin.handlers = dict(self.handlers)
        twin.props = dict(self.props)
        for name, value in overrides.items():
            if name == "class_":
                twin.class_ = tw(twin.class_, value)
            elif name == "key":
                twin.key = value
            elif name == "id":
                twin.explicit_id = value
            else:
                twin.props[name] = value
        if style_classes:
            twin.base_class = tw(twin.base_class, *style_classes)
        if style_declarations:
            twin.style = _merge_style(twin.style, style_declarations)
        return twin

    # ------------------------------------------------------------------
    # render
    # ------------------------------------------------------------------
    def _shown(self) -> bool:
        if not self.visible or self.hidden:
            return False
        when = self.when
        if callable(when):
            when = when()
        return bool(when)

    def event_names(self, ctx: RenderContext) -> list[str]:
        return list(self.handlers)

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        """Atributos HTML propios del componente (los hijos lo sobreescriben)."""
        return {}

    def classes(self, ctx: RenderContext, uid: str) -> str:
        return tw(self.base_class, self.class_)

    def content(self, ctx: RenderContext, path: str) -> str:
        return render_children(self.children, ctx, path)

    def render(self, ctx: RenderContext, path: str) -> str:
        if not self._shown():
            return ""
        uid = ctx.uid(path, self.key, self.explicit_id)
        for event, handler in self.handlers.items():
            if handler is not None:
                ctx.bind(uid, event, handler)

        attrs: dict[str, Any] = {"id": uid}
        classes = self.classes(ctx, uid)
        if classes:
            attrs["class"] = classes
        if self.style:
            attrs["style"] = _style_text(self.style)
        if self.role:
            attrs["role"] = self.role
        if self.title:
            attrs["title"] = self.title
        if self.tabindex is not None:
            attrs["tabindex"] = self.tabindex
        for key, value in self.aria.items():
            attrs[f"aria-{key.replace('_', '-')}"] = value
        attrs.update({f"data-{k.replace('_', '-')}": v for k, v in self.data.items()})

        extra = self.attr_map(ctx, uid)
        attrs.update(extra)
        attrs.update(self.props)

        events = self.event_names(ctx)
        if events:
            attrs["data-iui-on"] = ",".join(sorted(set(events)))

        body = "" if self.void else self.content(ctx, path)
        return self.wrap(element(self.tag, body, **attrs), ctx, uid)

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        """Permite que un control se envuelva (etiqueta, ayuda, marca visual)."""
        return html

    # -- utilidades ------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover
        return f"<{type(self).__name__} {self.props or ''}>"


class Fragment(Component):
    """Agrupa hijos sin emitir un elemento contenedor."""

    tag = ""

    def render(self, ctx: RenderContext, path: str) -> str:
        if not self._shown():
            return ""
        return self.content(ctx, path)


def bind_many(ctx: RenderContext, uid: str, handlers: dict[str, Any], suffixes: Sequence[str]) -> None:
    """Registra los handlers del contenedor en varios hijos (ids ``uid-sufijo``)."""
    for event, handler in handlers.items():
        if handler is None:
            continue
        for suffix in suffixes:
            ctx.bind(f"{uid}-{suffix}", event, handler)


def _merge_style(style: Any, declarations: dict[str, str]) -> Any:
    """Combina el ``style=`` del usuario con las declaraciones de los tokens."""
    if not declarations:
        return style
    if not style:
        return dict(declarations)
    if isinstance(style, dict):
        return {**declarations, **style}
    return f"{_style_text(declarations)}; {style}"


def _style_text(style: Any) -> str:
    if isinstance(style, str):
        return style
    if isinstance(style, dict):
        return "; ".join(
            f"{str(k).replace('_', '-')}: {v}" for k, v in style.items() if v is not None
        )
    return str(style)


def render_children(children: Sequence[Any], ctx: RenderContext, path: str) -> str:
    out: list[str] = []
    for index, child in enumerate(children):
        if child is None or child is True or child is False:
            continue
        if isinstance(child, Component):
            out.append(child.render(ctx, ctx.child(path, index)))
        elif isinstance(child, Signal):
            # `text("Pulsaciones: ", count)` se actualiza solo en cada render.
            out.append(escape(child.get()))
        elif isinstance(child, Markup):
            out.append(str(child))
        elif isinstance(child, str):
            if getattr(type(child), "_is_icon_name", False):
                # ``icons.car`` como hijo se dibuja; un texto normal se escapa.
                from .icons import Icon

                out.append(Icon(child).render(ctx, ctx.child(path, index)))
            else:
                out.append(escape(child))
        elif isinstance(child, (int, float)):
            out.append(escape(child))
        elif callable(child) and not isinstance(child, type):
            # Contenido calculado en el momento de pintar (texto reactivo).
            out.append(render_children([child()], ctx, ctx.child(path, index)))
        elif isinstance(child, Iterable):
            out.append(render_children(list(child), ctx, path))
        else:
            out.append(escape(child))
    return "".join(out)


def render(component: Any, ctx: RenderContext | None = None) -> str:
    """Renderiza un componente (o un valor suelto) a HTML."""
    ctx = ctx or RenderContext()
    if isinstance(component, Component):
        return component.render(ctx, "r")
    if component is None:
        return ""
    if is_safe(component):
        return str(component)
    return escape(component)
