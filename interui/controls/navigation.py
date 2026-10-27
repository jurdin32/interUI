"""Navegación: pestañas, migas, paginación, pasos y barras."""

from __future__ import annotations

from typing import Any, Sequence

from ..base import Component, bind_many
from ..context import RenderContext
from ..html import escape
from ..icons import Icon
from ..style import tw

__all__ = [
    "Tabs", "Breadcrumb", "Pagination", "Steps", "Navbar", "Sidebar", "SidebarItem",
    "NavLink", "CommandPalette", "CommandItem", "TabBar",
]


def _item(item: Any) -> tuple[str, str, Any]:
    if isinstance(item, dict):
        return str(item.get("key", item.get("label", ""))), str(item.get("label", "")), item.get("content")
    if isinstance(item, (tuple, list)):
        key = str(item[0])
        label = str(item[1]) if len(item) > 1 else key
        content = item[2] if len(item) > 2 else None
        return key, label, content
    return str(item), str(item), None


class Tabs(Component):
    """Pestañas. Sin ``on_change`` cambian en el navegador; con él, en Python."""

    tag = "div"

    def __init__(
        self,
        tabs: Sequence[Any] | None = None,
        *,
        active: Any = None,
        on_change: Any = None,
        variant: str = "line",
        size: str = "md",
        **props: Any,
    ) -> None:
        self.tabs = [_item(tab) for tab in (tabs or [])]
        self.active = str(active) if active is not None else (self.tabs[0][0] if self.tabs else "")
        self.variant = variant
        self.size = size
        if on_change is not None:
            props["on_change"] = on_change
        props["base_class"] = tw("flex flex-col gap-4", props.get("base_class"))
        super().__init__(**props)

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, self.handlers, [f"t{index}" for index in range(len(self.tabs))])
        return super().render(ctx, path)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        uid = ctx.uid(path, self.key, self.explicit_id)
        bar: list[str] = []
        panels: list[str] = []
        for index, (key, label, content) in enumerate(self.tabs):
            selected = key == self.active
            if self.variant == "pills":
                classes = (
                    "rounded-lg px-3 py-1.5 text-sm font-medium transition "
                    + ("bg-white text-slate-900 shadow-sm dark:bg-slate-800 dark:text-white"
                       if selected
                       else "text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-slate-100")
                )
                bar_cls = "inline-flex items-center gap-1 rounded-xl bg-slate-100 p-1 dark:bg-slate-900"
            elif self.variant == "enclosed":
                classes = (
                    "-mb-px rounded-t-lg border border-b-0 px-3 py-2 text-sm font-medium transition "
                    + ("border-slate-200 bg-white text-slate-900 dark:border-slate-700 dark:bg-slate-900 dark:text-white"
                       if selected
                       else "border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200")
                )
                bar_cls = "flex items-center gap-1 border-b border-slate-200 dark:border-slate-700"
            else:
                classes = (
                    "-mb-px border-b-2 px-1 py-2 text-sm font-medium transition "
                    + ("border-indigo-600 text-indigo-600 dark:border-indigo-400 dark:text-indigo-400"
                       if selected
                       else "border-transparent text-slate-500 hover:border-slate-300 hover:text-slate-800 "
                           "dark:text-slate-400 dark:hover:text-slate-200")
                )
                bar_cls = "flex items-center gap-5 overflow-x-auto border-b border-slate-200 dark:border-slate-800"
            if self.handlers.get("change"):
                trigger = (
                    f'id="{escape(uid)}-t{index}" data-iui-emit="change" data-iui-value="{escape(key)}"'
                )
            else:
                trigger = f'data-iui-tab="{escape(uid)}-p{index}"'
            bar.append(
                f'<button type="button" {trigger} {("disabled " if False else "")}class="{classes}">{escape(label)}</button>'
            )
            panels.append(
                f'<div id="{escape(uid)}-p{index}" data-iui-panel role="tabpanel"'
                + ("" if selected else ' class="hidden"')
                + ">"
                + (
                    content.render(ctx, f"{path}-p{index}")
                    if isinstance(content, Component)
                    else render_children([content], ctx, f"{path}-p{index}")
                )
                + "</div>"
            )
        return (
            f'<div data-iui-tabgroup><div class="{bar_cls}" data-iui-tabbar role="tablist">'
            f'{"".join(bar)}</div><div class="pt-1">{"".join(panels)}</div></div>'
        )


TabBar = Tabs


class Breadcrumb(Component):
    tag = "nav"

    def __init__(
        self,
        items: Sequence[Any] | None = None,
        *,
        separator: str = "chevron",
        **props: Any,
    ) -> None:
        self.items = [_item(item) for item in (items or [])]
        self.separator = separator
        props["aria"] = {"label": "migas de pan", **(props.get("aria") or {})}
        props["base_class"] = tw("flex items-center gap-1 text-sm", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        parts: list[str] = []
        total = len(self.items)
        for index, (key, label, _content) in enumerate(self.items):
            last = index == total - 1
            if key.startswith("/") or key.startswith("http"):
                parts.append(
                    f'<a href="{escape(key)}" class="rounded px-1 py-0.5 text-slate-500 transition '
                    f'hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 dark:hover:bg-slate-800 '
                    f'dark:hover:text-slate-100">{escape(label)}</a>'
                )
            else:
                parts.append(
                    f'<span class="px-1 py-0.5 {"font-medium text-slate-900 dark:text-slate-100" if last else "text-slate-500 dark:text-slate-400"}">'
                    f"{escape(label)}</span>"
                )
            if not last:
                sep = (
                    Icon("chevron-right", size=3, class_="text-slate-300 dark:text-slate-600").render(ctx, f"{path}-s{index}")
                    if self.separator == "chevron"
                    else f'<span class="text-slate-300">{escape(self.separator)}</span>'
                )
                parts.append(sep)
        return "".join(parts)


class Pagination(Component):
    tag = "nav"

    def __init__(
        self,
        page: int = 1,
        *,
        pages: int = 1,
        on_page: Any = None,
        window: int = 5,
        **props: Any,
    ) -> None:
        self.page = max(1, int(page))
        self.pages = max(1, int(pages))
        self.window = window
        if on_page is not None:
            props["on_page"] = on_page
        props["aria"] = {"label": "paginación", **(props.get("aria") or {})}
        props["base_class"] = tw("flex items-center gap-1", props.get("base_class"))
        super().__init__(**props)

    def _numbers(self) -> list[int]:
        half = self.window // 2
        start = max(1, min(self.page - half, self.pages - self.window + 1))
        return [number for number in range(start, min(self.pages, start + self.window - 1) + 1)]

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        numbers = set(self._numbers()) | {1, self.page, self.pages}
        bind_many(ctx, uid, self.handlers, [f"p{number}" for number in sorted(numbers)])
        return super().render(ctx, path)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        base = (
            "inline-flex h-8 min-w-8 items-center justify-center rounded-md px-2 text-sm font-medium transition "
        )
        parts: list[str] = []
        for number in sorted(set(self._numbers()) | {1, self.page, self.pages}):
            active = number == self.page
            parts.append(
                f'<button type="button" id="{escape(uid)}-p{number}" data-iui-emit="page" '
                f'data-iui-value="{number}" data-iui-cast="int" class="{base}'
                + ("bg-indigo-600 text-white shadow-sm"
                   if active
                   else "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800")
                + f'">{number}</button>'
            )
        return "".join(parts)


class Steps(Component):
    tag = "ol"

    def __init__(
        self,
        items: Sequence[Any] | None = None,
        *,
        current: int = 0,
        on_step: Any = None,
        **props: Any,
    ) -> None:
        self.items = [str(_item(item)[1]) for item in (items or [])]
        self.current = current
        if on_step is not None:
            props["on_change"] = on_step
        props["base_class"] = tw("flex w-full items-center gap-2", props.get("base_class"))
        super().__init__(**props)

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, self.handlers, [f"s{index}" for index in range(len(self.items))])
        return super().render(ctx, path)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        parts: list[str] = []
        for index, label in enumerate(self.items):
            done = index < self.current
            current = index == self.current
            circle = (
                "bg-emerald-500 text-white"
                if done
                else "bg-indigo-600 text-white ring-4 ring-indigo-100 dark:ring-indigo-500/20"
                if current
                else "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400"
            )
            inner = (
                Icon("check", size=3).render(ctx, f"{uid}-ci{index}")
                if done
                else f'<span class="text-xs font-semibold">{index + 1}</span>'
            )
            parts.append(
                '<div class="flex flex-1 items-center gap-2">'
                f'<button type="button" id="{escape(uid)}-s{index}" data-iui-emit="change" '
                f'data-iui-value="{index}" data-iui-cast="int" class="flex items-center gap-2">'
                f'<span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-full {circle}">{inner}</span>'
                f'<span class="text-xs font-medium {("text-slate-900 dark:text-white" if current or done else "text-slate-400")}">'
                f"{escape(label)}</span></button>"
                + (
                    '<span class="h-px flex-1 bg-slate-200 dark:bg-slate-800"></span>'
                    if index < len(self.items) - 1
                    else ""
                )
                + "</div>"
            )
        return "".join(parts)


class NavLink(Component):
    tag = "a"

    def __init__(
        self,
        label: Any = "",
        *,
        href: str = "#",
        icon: str | None = None,
        active: bool = False,
        badge: Any = None,
        on_click: Any = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.icon = icon
        self.active = active
        self.badge = badge
        if on_click is not None:
            props["on_click"] = on_click
            props.setdefault("href", href)
        else:
            props["href"] = href
        props["base_class"] = tw(
            "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition",
            "bg-indigo-50 text-indigo-700 dark:bg-indigo-500/15 dark:text-indigo-300"
            if active
            else "text-slate-600 hover:bg-slate-100 hover:text-slate-900 dark:text-slate-400 "
                 "dark:hover:bg-slate-800 dark:hover:text-slate-100",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return (
            (Icon(self.icon, size=4).render(ctx, path + "-ic") if self.icon else "")
            + f'<span class="flex-1 truncate">{escape(self.label)}</span>'
            + (
                f'<span class="rounded-full bg-indigo-100 px-1.5 text-[10px] font-semibold text-indigo-700 '
                f'dark:bg-indigo-500/20 dark:text-indigo-300">{escape(self.badge)}</span>'
                if self.badge is not None
                else ""
            )
        )


class Navbar(Component):
    tag = "header"

    def __init__(
        self,
        *children: Any,
        brand: Any = None,
        logo: str | None = "layers",
        sticky: bool = True,
        **props: Any,
    ) -> None:
        self.brand = brand
        self.logo = logo
        props["base_class"] = tw(
            "flex w-full items-center gap-4 border-b border-slate-200 bg-white/80 px-4 py-2.5 "
            "backdrop-blur dark:border-slate-800 dark:bg-slate-950/80",
            "sticky top-0 z-30" if sticky else "",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        brand = ""
        if self.brand is not None:
            brand = (
                '<div class="flex items-center gap-2 font-semibold text-slate-900 dark:text-white">'
                + (
                    f'<span class="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-white">'
                    f"{Icon(self.logo, size=4).render(ctx, path + '-lg')}</span>"
                    if self.logo
                    else ""
                )
                + f'<span class="text-sm">{escape(self.brand)}</span></div>'
            )
        return brand + render_children(self.children, ctx, path)


class SidebarItem(Component):
    tag = "div"

    def __init__(
        self,
        label: Any = "",
        *,
        icon: str | None = None,
        active: bool = False,
        badge: Any = None,
        on_click: Any = None,
        children: Sequence[Any] | None = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.icon = icon
        self.active = active
        self.badge = badge
        self.nodes = list(children or [])
        if on_click is not None:
            props["on_click"] = on_click
        props["base_class"] = tw(
            "flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition",
            "cursor-pointer" if on_click else "",
            "bg-slate-900 text-white dark:bg-slate-800"
            if active
            else "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        body = (
            (Icon(self.icon, size=4).render(ctx, path + "-ic") if self.icon else "")
            + f'<span class="flex-1 truncate">{escape(self.label)}</span>'
            + (
                f'<span class="rounded-full bg-white/20 px-1.5 text-[10px] font-semibold">{escape(self.badge)}</span>'
                if self.badge is not None
                else ""
            )
        )
        if self.nodes:
            body += render_children(self.nodes, ctx, path)
        return body


class Sidebar(Component):
    tag = "aside"

    def __init__(self, *children: Any, title: Any = None, width: str = "w-64", **props: Any) -> None:
        self.sidebar_title = title
        self.width = width
        props["base_class"] = tw(
            "flex h-full shrink-0 flex-col gap-1 border-r border-slate-200 bg-white p-3 "
            "dark:border-slate-800 dark:bg-slate-950",
            width,
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        head = (
            f'<p class="px-2 pb-1 pt-2 text-[11px] font-semibold uppercase tracking-wider text-slate-400">'
            f"{escape(self.sidebar_title)}</p>"
            if self.sidebar_title
            else ""
        )
        return head + render_children(self.children, ctx, path)


class CommandItem(Component):
    tag = "button"

    def __init__(
        self,
        label: Any = "",
        *,
        hint: Any = None,
        icon: str | None = "search",
        on_click: Any = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.hint = hint
        self.icon = icon
        props.setdefault("type", "button")
        props["data"] = {"iui-item": "true", **(props.get("data") or {})}
        if on_click is not None:
            props["on_click"] = on_click
        props["base_class"] = tw(
            "flex w-full items-center gap-3 px-3 py-2 text-left text-sm text-slate-700 transition "
            "hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return (
            (Icon(self.icon, size=4, class_="text-slate-400").render(ctx, path + "-ic") if self.icon else "")
            + f'<span class="flex-1 truncate">{escape(self.label)}</span>'
            + (f'<span class="text-xs text-slate-400">{escape(self.hint)}</span>' if self.hint else "")
        )


class CommandPalette(Component):
    """Buscador de acciones con filtrado instantáneo en el navegador."""

    tag = "div"

    def __init__(self, *children: Any, placeholder: str = "Buscar acciones…", **props: Any) -> None:
        self.placeholder = placeholder
        props["base_class"] = tw(
            "flex flex-col overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl "
            "dark:border-slate-700 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        uid = ctx.uid(path, self.key, self.explicit_id)
        return (
            '<div class="flex items-center gap-2 border-b border-slate-100 px-3 dark:border-slate-800">'
            + Icon("search", size=4, class_="text-slate-400").render(ctx, uid + "-si")
            + f'<input type="search" id="{escape(uid)}-q" data-iui-command="{escape(uid)}-list" '
            f'placeholder="{escape(self.placeholder)}" autocomplete="off" '
            'class="h-11 w-full border-0 bg-transparent text-sm text-slate-800 placeholder:text-slate-400 '
            'focus:outline-none dark:text-slate-100"/>'
            '<kbd class="rounded border border-slate-300 px-1.5 text-[10px] text-slate-400 dark:border-slate-600">Esc</kbd>'
            "</div>"
            f'<div id="{escape(uid)}-list" class="max-h-72 overflow-y-auto py-1" data-iui-palette>'
            f'<div data-iui-empty class="hidden px-3 py-6 text-center text-sm text-slate-400">Sin coincidencias</div>'
            f"{render_children(self.children, ctx, path)}</div>"
        )
