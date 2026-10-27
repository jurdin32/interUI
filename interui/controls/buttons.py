"""Botones y acciones."""

from __future__ import annotations

from typing import Any

from ..base import Component
from ..context import RenderContext
from ..icons import Icon
from ..style import tw
from ..ui import BUTTON_SIZES, BUTTON_VARIANTS

__all__ = [
    "Button", "IconButton", "ButtonGroup", "Fab", "LinkButton", "CopyButton", "Spinner",
]


class Spinner(Component):
    tag = "span"

    def __init__(self, size: int = 4, class_: str | None = None, **props: Any) -> None:
        self.size = size
        self.class_ = class_
        super().__init__(**props)

    def render(self, ctx: RenderContext, path: str) -> str:
        classes = tw("inline-block animate-spin", f"h-{self.size} w-{self.size}", self.class_,
                     "text-current")
        return (
            f'<span class="{classes}" role="status" aria-label="cargando">'
            '<svg viewBox="0 0 24 24" fill="none" class="h-full w-full">'
            '<circle cx="12" cy="12" r="9" stroke="currentColor" stroke-opacity="0.25" stroke-width="3"/>'
            '<path d="M21 12a9 9 0 0 0-9-9" stroke="currentColor" stroke-width="3" '
            'stroke-linecap="round"/></svg></span>'
        )


class Button(Component):
    tag = "button"

    def __init__(
        self,
        *children: Any,
        label: Any = None,
        variant: str = "primary",
        size: str = "md",
        icon: str | None = None,
        icon_right: str | None = None,
        loading: bool = False,
        disabled: bool = False,
        submit: bool = False,
        full_width: bool = False,
        href: str | None = None,
        pill: bool = False,
        **props: Any,
    ) -> None:
        self.variant = variant
        self.size = size
        self.icon = icon
        self.icon_right = icon_right
        self.loading = loading
        self.disabled = disabled
        self.text = list(children) if children else ([] if label is None else [label])
        self.full_width = full_width
        self.pill = pill
        if href is not None:
            self.tag = "a"
            props["href"] = href
            if props.get("type") is None:
                props.pop("type", None)
        else:
            props.setdefault("type", "submit" if submit else "button")
        if disabled or loading:
            props["disabled"] = True
            props["aria-disabled"] = "true"
        icon_size = {"xs": 3, "sm": 4, "md": 4, "lg": 5, "xl": 5}.get(size, 4)
        props["base_class"] = tw(
            "inline-flex select-none items-center justify-center whitespace-nowrap font-medium "
            "transition focus:outline-none disabled:pointer-events-none disabled:opacity-50",
            BUTTON_SIZES.get(size, BUTTON_SIZES["md"]),
            BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS["primary"]),
            "w-full" if full_width else "",
            "rounded-full" if pill else "",
            props.get("base_class"),
        )
        super().__init__(**props)
        if loading:
            self.children.append(Spinner(size=icon_size))
        elif icon:
            self.children.append(Icon(icon, size=icon_size))
        self.children.extend(self.text)
        if icon_right:
            self.children.append(Icon(icon_right, size=icon_size))


class IconButton(Component):
    tag = "button"

    def __init__(
        self,
        icon: str = "more-h",
        *,
        label: str | None = None,
        variant: str = "ghost",
        size: str = "md",
        loading: bool = False,
        disabled: bool = False,
        href: str | None = None,
        **props: Any,
    ) -> None:
        self.icon = icon
        self.loading = loading
        self.label = label
        sizes = {"xs": ("h-7 w-7", 3), "sm": ("h-8 w-8", 4), "md": ("h-10 w-10", 4),
                 "lg": ("h-11 w-11", 5), "xl": ("h-12 w-12", 6)}
        box, icon_size = sizes.get(size, sizes["md"])
        self.icon_size = icon_size
        if href is not None:
            self.tag = "a"
            props["href"] = href
        else:
            props.setdefault("type", "button")
        if disabled or loading:
            props["disabled"] = True
        if label:
            props["aria"] = {**(props.get("aria") or {}), "label": label}
            props["title"] = props.get("title") or label
        props["base_class"] = tw(
            "inline-flex items-center justify-center rounded-lg transition focus:outline-none "
            "disabled:pointer-events-none disabled:opacity-50",
            box,
            BUTTON_VARIANTS.get(variant, BUTTON_VARIANTS["ghost"]),
            props.get("base_class"),
        )
        super().__init__(**props)
        self.children.append(Spinner(size=icon_size) if loading else Icon(icon, size=icon_size))


class ButtonGroup(Component):
    """Agrupa botones pegados horizontal o verticalmente."""

    def __init__(self, *children: Any, vertical: bool = False, **props: Any) -> None:
        props["role"] = "group"
        props["base_class"] = tw(
            "inline-flex shadow-sm",
            "flex-col" if vertical else "flex-row",
            "[&>*]:rounded-none",
            "[&>*:first-child]:rounded-t-lg" if vertical else "[&>*:first-child]:rounded-l-lg",
            "[&>*:last-child]:rounded-b-lg" if vertical else "[&>*:last-child]:rounded-r-lg",
            "[&>*]:shadow-none",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Fab(Component):
    tag = "button"

    def __init__(self, icon: str = "plus", *, label: str | None = None, **props: Any) -> None:
        props.setdefault("type", "button")
        props["aria"] = {**(props.get("aria") or {}), "label": label or "acción"}
        props["base_class"] = tw(
            "fixed bottom-6 right-6 z-40 inline-flex h-14 w-14 items-center justify-center rounded-full "
            "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30 transition hover:bg-indigo-500 "
            "active:scale-95",
            props.get("base_class"),
        )
        super().__init__(**props)
        self.children = [Icon(icon, size=6)]


LinkButton = Button


class CopyButton(Component):
    """Botón que copia un texto al portapapeles sin ir al servidor."""

    tag = "button"

    def __init__(self, text: str, *, label: str = "Copiar", icon: str = "copy", **props: Any) -> None:
        props.setdefault("type", "button")
        props["data"] = {"iui-copy": text, **(props.get("data") or {})}
        props["base_class"] = tw(
            "inline-flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium "
            "text-slate-500 transition hover:bg-slate-100 hover:text-slate-800 "
            "dark:text-slate-400 dark:hover:bg-slate-800 dark:hover:text-slate-100",
            props.get("base_class"),
        )
        super().__init__(**props)
        self.children = [Icon(icon, size=3), label]
