"""Contenedores, tarjetas, modales, menús y superposiciones."""

from __future__ import annotations

from typing import Any, Sequence

from ..base import Component
from ..context import RenderContext
from ..html import escape
from ..icons import Icon
from ..style import tw
from .buttons import Button

__all__ = [
    "Card", "Panel", "Section", "Paper", "Toolbar", "PageHeader", "Hero", "Footer",
    "Modal", "Drawer", "Sheet", "Accordion", "Collapse", "Splitter", "Tooltip",
    "Popover", "Dropdown", "Menu", "MenuItem", "Well", "TitleBar", "StatusBar",
]

RADII = {"none": "rounded-none", "sm": "rounded-lg", "md": "rounded-xl", "lg": "rounded-2xl", "xl": "rounded-3xl"}


class Card(Component):
    """Tarjeta con cabecera, cuerpo y pie opcionales."""

    tag = "div"

    def __init__(
        self,
        *children: Any,
        title: Any = None,
        description: Any = None,
        footer: Any = None,
        icon: str | None = None,
        actions: Any = None,
        padding: bool = True,
        hover: bool = False,
        radius: str = "md",
        elevated: bool = True,
        **props: Any,
    ) -> None:
        self.card_title = title
        self.description = description
        self.footer = footer
        self.icon = icon
        self.actions = actions
        self.padding = padding
        props["base_class"] = tw(
            "flex flex-col overflow-hidden border border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-900",
            RADII.get(radius, RADII["md"]),
            "shadow-sm" if elevated else "",
            "transition hover:-translate-y-0.5 hover:shadow-md" if hover else "",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        head = ""
        if self.card_title or self.description or self.actions or self.icon:
            icon = (
                f'<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg '
                f'bg-indigo-50 text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-300">'
                f"{Icon(self.icon, size=4).render(ctx, path + '-ic')}</span>"
                if self.icon
                else ""
            )
            titles = (
                '<div class="flex min-w-0 flex-col">'
                + (
                    f'<h3 class="truncate text-base font-semibold text-slate-900 dark:text-white">'
                    f"{escape(self.card_title)}</h3>"
                    if self.card_title
                    else ""
                )
                + (
                    f'<p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{escape(self.description)}</p>'
                    if self.description
                    else ""
                )
                + "</div>"
            )
            action_html = ""
            if isinstance(self.actions, Component):
                action_html = self.actions.render(ctx, path + "-ac")
            elif self.actions:
                action_html = "".join(
                    Button(label, variant=variant, size="sm", on_click=handler).render(ctx, f"{path}-a{i}")
                    for i, (label, handler, variant) in enumerate(_action_tuples(self.actions))
                )
            head = (
                f'<div class="flex items-start gap-3 border-b border-slate-100 px-4 py-3 '
                f'dark:border-slate-800">{icon}{titles}'
                f'<div class="ml-auto flex items-center gap-2">{action_html}</div></div>'
            )
        body = render_children(self.children, ctx, path)
        body = f'<div class="{"p-4" if self.padding else ""} flex flex-col gap-3">{body}</div>' if body else ""
        foot = ""
        if self.footer is not None:
            foot = (
                '<div class="flex items-center gap-2 border-t border-slate-100 bg-slate-50/60 px-4 py-3 '
                'text-sm dark:border-slate-800 dark:bg-slate-800/40">'
                + (
                    self.footer.render(ctx, path + "-ft")
                    if isinstance(self.footer, Component)
                    else escape(self.footer)
                )
                + "</div>"
            )
        return f"{head}{body}{foot}"


def _action_tuples(actions: Sequence[Any]) -> list[tuple[str, Any, str]]:
    out = []
    for item in actions:
        if isinstance(item, (tuple, list)):
            label = item[0]
            handler = item[1] if len(item) > 1 else None
            variant = item[2] if len(item) > 2 else "ghost"
            out.append((str(label), handler, variant))
        else:
            out.append((str(item), None, "ghost"))
    return out


class Panel(Component):
    """Superficie neutra con padding uniforme."""

    def __init__(self, *children: Any, tone: str = "muted", padding: int = 4, **props: Any) -> None:
        tones = {
            "muted": "bg-slate-50 dark:bg-slate-900/60",
            "white": "bg-white dark:bg-slate-900",
            "primary": "bg-indigo-50 dark:bg-indigo-500/10",
        }
        props["base_class"] = tw(
            "flex flex-col gap-3 rounded-xl border border-slate-200 dark:border-slate-800",
            tones.get(tone, tones["muted"]),
            f"p-{padding}",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Well(Component):
    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(
            "rounded-lg bg-slate-100 p-3 text-sm text-slate-700 dark:bg-slate-800 dark:text-slate-200",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Section(Component):
    tag = "section"

    def __init__(
        self,
        *children: Any,
        title: Any = None,
        subtitle: Any = None,
        actions: Any = None,
        **props: Any,
    ) -> None:
        self.section_title = title
        self.subtitle = subtitle
        self.actions = actions
        props["base_class"] = tw("flex flex-col gap-4", props.get("base_class"))
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        head = ""
        if self.section_title or self.subtitle or self.actions:
            action_html = (
                self.actions.render(ctx, path + "-ac")
                if isinstance(self.actions, Component)
                else "".join(
                    Button(label, variant=variant, size="sm", on_click=handler).render(ctx, f"{path}-a{i}")
                    for i, (label, handler, variant) in enumerate(_action_tuples(self.actions or []))
                )
            )
            head = (
                '<div class="flex flex-wrap items-end justify-between gap-3">'
                '<div class="flex flex-col">'
                + (
                    f'<h2 class="text-lg font-semibold tracking-tight text-slate-900 dark:text-white">'
                    f"{escape(self.section_title)}</h2>"
                    if self.section_title
                    else ""
                )
                + (
                    f'<p class="text-sm text-slate-500 dark:text-slate-400">{escape(self.subtitle)}</p>'
                    if self.subtitle
                    else ""
                )
                + f'</div><div class="flex items-center gap-2">{action_html}</div></div>'
            )
        return head + render_children(self.children, ctx, path)


class Paper(Component):
    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(
            "rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 dark:bg-slate-900 "
            "dark:ring-slate-800",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Toolbar(Component):
    tag = "div"

    def __init__(self, *children: Any, sticky: bool = False, **props: Any) -> None:
        props["role"] = "toolbar"
        props["base_class"] = tw(
            "flex flex-wrap items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 "
            "shadow-sm dark:border-slate-800 dark:bg-slate-900",
            "sticky top-0 z-20" if sticky else "",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class PageHeader(Component):
    tag = "div"

    def __init__(
        self,
        title: Any,
        *,
        subtitle: Any = None,
        actions: Any = None,
        breadcrumb: Any = None,
        **props: Any,
    ) -> None:
        self.page_title = title
        self.subtitle = subtitle
        self.actions = actions
        self.breadcrumb = breadcrumb
        props["base_class"] = tw("flex flex-col gap-1", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        crumb = self.breadcrumb.render(ctx, path + "-bc") if isinstance(self.breadcrumb, Component) else ""
        action_html = self.actions.render(ctx, path + "-ac") if isinstance(self.actions, Component) else ""
        return (
            f"{crumb}"
            '<div class="flex flex-wrap items-end justify-between gap-3">'
            '<div class="flex flex-col">'
            f'<h1 class="text-2xl font-semibold tracking-tight text-slate-900 dark:text-white">'
            f"{escape(self.page_title)}</h1>"
            + (
                f'<p class="mt-0.5 text-sm text-slate-500 dark:text-slate-400">{escape(self.subtitle)}</p>'
                if self.subtitle
                else ""
            )
            + f'</div><div class="flex items-center gap-2">{action_html}</div></div>'
        )


class Hero(Component):
    tag = "section"

    def __init__(self, *children: Any, eyebrow: Any = None, **props: Any) -> None:
        self.eyebrow = eyebrow
        props["base_class"] = tw(
            "relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 via-indigo-500 "
            "to-violet-600 px-8 py-12 text-white shadow-lg",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        eyebrow = (
            f'<span class="mb-3 inline-flex rounded-full bg-white/15 px-3 py-1 text-xs font-medium '
            f'backdrop-blur">{escape(self.eyebrow)}</span>'
            if self.eyebrow
            else ""
        )
        return (
            f'<div class="relative z-10 flex flex-col items-start gap-4">{eyebrow}'
            f'<div class="flex flex-col gap-3">{render_children(self.children, ctx, path)}</div></div>'
            '<div class="pointer-events-none absolute -right-16 -top-16 h-64 w-64 rounded-full '
            'bg-white/10 blur-2xl"></div>'
        )


class Footer(Component):
    tag = "footer"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(
            "mt-8 border-t border-slate-200 py-6 text-sm text-slate-500 dark:border-slate-800 "
            "dark:text-slate-400",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Modal(Component):
    """Diálogo modal. Ábrelo con ``Modal.trigger()`` o ``data-iui-modal``."""

    tag = "div"

    def __init__(
        self,
        *children: Any,
        dialog_id: str = "modal",
        title: Any = None,
        description: Any = None,
        footer: Any = None,
        size: str = "md",
        open: bool = False,
        closable: bool = True,
        **props: Any,
    ) -> None:
        self.dialog_id = dialog_id
        self.modal_title = title
        self.description = description
        self.footer = footer
        self.size = size
        self.open = open
        self.closable = closable
        props["id"] = dialog_id
        props["aria"] = {"modal": "true", **(props.get("aria") or {})}
        props["role"] = "dialog"
        props["base_class"] = tw(
            "fixed inset-0 z-50 items-center justify-center p-4",
            "flex" if open else "hidden",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def trigger(self, label: Any = "Abrir", **kwargs: Any) -> Button:
        kwargs.setdefault("variant", "primary")
        return Button(label, data={"iui-modal": self.dialog_id}, **kwargs)

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        return {"data-iui-dialog": self.dialog_id}

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        widths = {"sm": "max-w-sm", "md": "max-w-lg", "lg": "max-w-2xl", "xl": "max-w-4xl", "full": "max-w-[95vw]"}
        head = ""
        if self.modal_title or self.description:
            head = (
                '<div class="flex items-start gap-3 border-b border-slate-100 px-5 py-4 dark:border-slate-800">'
                '<div class="flex flex-col gap-0.5">'
                + (
                    f'<h2 class="text-base font-semibold text-slate-900 dark:text-white">{escape(self.modal_title)}</h2>'
                    if self.modal_title
                    else ""
                )
                + (
                    f'<p class="text-sm text-slate-500 dark:text-slate-400">{escape(self.description)}</p>'
                    if self.description
                    else ""
                )
                + "</div>"
                + (
                    f'<button type="button" data-iui-close="{escape(self.dialog_id)}" aria-label="Cerrar" '
                    'class="ml-auto rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 '
                    'hover:text-slate-700 dark:hover:bg-slate-800 dark:hover:text-slate-200">'
                    + Icon("x", size=4).render(ctx, path + "-x")
                    + "</button>"
                    if self.closable
                    else ""
                )
                + "</div>"
            )
        body = render_children(self.children, ctx, path)
        foot = ""
        if self.footer is not None:
            foot = (
                '<div class="flex justify-end gap-2 border-t border-slate-100 px-5 py-3 '
                'dark:border-slate-800">'
                + (
                    self.footer.render(ctx, path + "-ft")
                    if isinstance(self.footer, Component)
                    else escape(self.footer)
                )
                + "</div>"
            )
        backdrop = (
            f'<div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" '
            f'data-iui-close="{escape(self.dialog_id)}"></div>'
        )
        panel = (
            f'<div class="relative z-10 flex w-full {widths.get(self.size, widths["md"])} flex-col '
            'overflow-hidden rounded-2xl bg-white shadow-2xl ring-1 ring-slate-900/5 '
            f'dark:bg-slate-900 dark:ring-slate-700/40">{head}'
            f'<div class="flex flex-col gap-3 px-5 py-4">{body}</div>{foot}</div>'
        )
        return backdrop + panel


class Drawer(Component):
    tag = "div"

    def __init__(
        self,
        *children: Any,
        drawer_id: str = "drawer",
        side: str = "right",
        title: Any = None,
        size: str = "md",
        open: bool = False,
        **props: Any,
    ) -> None:
        self.drawer_id = drawer_id
        self.side = side
        self.drawer_title = title
        self.size = size
        self.open = open
        props["id"] = drawer_id
        props["base_class"] = tw("fixed inset-0 z-50", "block" if open else "hidden", props.get("base_class"))
        super().__init__(*children, **props)

    def trigger(self, label: Any = "Abrir", **kwargs: Any) -> Button:
        kwargs.setdefault("variant", "outline")
        return Button(label, data={"iui-modal": self.drawer_id}, **kwargs)

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        return {"data-iui-dialog": self.drawer_id}

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        widths = {"sm": "w-72", "md": "w-96", "lg": "w-[32rem]", "full": "w-full"}
        align = "justify-end" if self.side == "right" else "justify-start"
        head = (
            '<div class="flex items-center justify-between border-b border-slate-100 px-4 py-3 '
            f'dark:border-slate-800"><h2 class="text-base font-semibold text-slate-900 dark:text-white">'
            f"{escape(self.drawer_title or '')}</h2>"
            f'<button type="button" data-iui-close="{escape(self.drawer_id)}" aria-label="Cerrar" '
            'class="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800">'
            + Icon("x", size=4).render(ctx, path + "-x")
            + "</button></div>"
        )
        return (
            f'<div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" '
            f'data-iui-close="{escape(self.drawer_id)}"></div>'
            f'<div class="absolute inset-y-0 {align} flex"><div class="flex h-full '
            f'{widths.get(self.size, widths["md"])} flex-col bg-white shadow-2xl dark:bg-slate-900">'
            f"{head}"
            f'<div class="flex flex-1 flex-col gap-3 overflow-y-auto p-4">'
            f"{render_children(self.children, ctx, path)}</div></div></div>"
        )


class Sheet(Component):
    tag = "div"

    def __init__(self, *children: Any, sheet_id: str = "sheet", title: Any = None, open: bool = False, **props: Any) -> None:
        self.sheet_id = sheet_id
        self.sheet_title = title
        self.open = open
        props["id"] = sheet_id
        props["base_class"] = tw("fixed inset-0 z-50", "block" if open else "hidden", props.get("base_class"))
        super().__init__(*children, **props)

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        return {"data-iui-dialog": self.sheet_id}

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        return (
            f'<div class="absolute inset-0 bg-slate-950/50 backdrop-blur-sm" '
            f'data-iui-close="{escape(self.sheet_id)}"></div>'
            '<div class="absolute inset-x-0 bottom-0 max-h-[85vh] overflow-y-auto rounded-t-3xl '
            'bg-white p-5 shadow-2xl dark:bg-slate-900">'
            '<div class="mx-auto mb-3 h-1.5 w-10 rounded-full bg-slate-300 dark:bg-slate-700"></div>'
            + (
                f'<h2 class="mb-3 text-base font-semibold text-slate-900 dark:text-white">'
                f"{escape(self.sheet_title)}</h2>"
                if self.sheet_title
                else ""
            )
            + render_children(self.children, ctx, path)
            + "</div>"
        )


class Collapse(Component):
    """Sección plegable gestionada en el navegador (sin ir al servidor)."""

    tag = "div"

    def __init__(
        self,
        *children: Any,
        title: Any = "Detalles",
        open: bool = False,
        **props: Any,
    ) -> None:
        self.collapse_title = title
        self.open = open
        props["base_class"] = tw(
            "overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        uid = ctx.uid(path, self.key, self.explicit_id)
        return (
            f'<button type="button" data-iui-collapse="{escape(uid)}-body" '
            'class="flex w-full items-center justify-between gap-2 px-4 py-3 text-left text-sm '
            'font-medium text-slate-800 transition hover:bg-slate-50 dark:text-slate-100 '
            'dark:hover:bg-slate-800/60">'
            f"<span>{escape(self.collapse_title)}</span>"
            + Icon("chevron-down", size=4, class_="text-slate-400").render(ctx, uid + "-c")
            + "</button>"
            f'<div id="{escape(uid)}-body" data-open="{"true" if self.open else "false"}" '
            + ('class="px-4 pb-4 pt-1 text-sm text-slate-600 dark:text-slate-300">'
               if self.open
               else 'class="hidden px-4 pb-4 pt-1 text-sm text-slate-600 dark:text-slate-300">')
            + render_children(self.children, ctx, path)
            + "</div>"
        )


class Accordion(Component):
    """Lista de secciones plegables independientes."""

    tag = "div"

    def __init__(
        self,
        items: Sequence[Any] | None = None,
        *,
        default_open: int | None = 0,
        **props: Any,
    ) -> None:
        self.items = list(items or [])
        self.default_open = default_open
        props["base_class"] = tw(
            "flex flex-col divide-y divide-slate-200 overflow-hidden rounded-xl border "
            "border-slate-200 dark:divide-slate-800 dark:border-slate-800",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        uid = ctx.uid(path, self.key, self.explicit_id)
        blocks = []
        for index, item in enumerate(self.items):
            if isinstance(item, dict):
                title = item.get("title", "")
                content = item.get("content", "")
            else:
                title, content = item[0], item[1] if len(item) > 1 else ""
            is_open = self.default_open == index
            body = (
                render_children([content], ctx, f"{path}-{index}")
                if isinstance(content, Component)
                else escape(content)
            )
            blocks.append(
                f'<div class="bg-white dark:bg-slate-900">'
                f'<button type="button" data-iui-collapse="{escape(uid)}-a{index}" '
                'class="flex w-full items-center justify-between gap-2 px-4 py-3 text-left text-sm '
                'font-medium text-slate-800 transition hover:bg-slate-50 dark:text-slate-100 '
                'dark:hover:bg-slate-800/60">'
                f"<span>{escape(title)}</span>"
                + Icon("chevron-down", size=4, class_="text-slate-400").render(ctx, f"{uid}-ac{index}")
                + "</button>"
                + f'<div id="{escape(uid)}-a{index}" data-open="{"true" if is_open else "false"}" '
                + ('class="' if is_open else 'class="hidden ')
                + 'px-4 pb-4 text-sm text-slate-600 dark:text-slate-300">'
                + body
                + "</div></div>"
            )
        return "".join(blocks)


class Splitter(Component):
    """Dos paneles redimensionables (usa ``resize`` nativo del navegador)."""

    tag = "div"

    def __init__(
        self,
        first: Any,
        second: Any,
        *,
        direction: str = "horizontal",
        initial: str = "50%",
        **props: Any,
    ) -> None:
        self.first = first
        self.second = second
        self.direction = direction
        self.initial = initial
        props["base_class"] = tw(
            "flex overflow-hidden rounded-xl border border-slate-200 dark:border-slate-800",
            "flex-row" if direction == "horizontal" else "flex-col",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        resize = "resize-x" if self.direction == "horizontal" else "resize-y"
        first = render_children([self.first], ctx, f"{path}-0")
        second = render_children([self.second], ctx, f"{path}-1")
        return (
            f'<div class="{resize} min-h-24 overflow-auto bg-slate-50/50 p-3 dark:bg-slate-900/40" '
            f'style="{"width" if self.direction == "horizontal" else "height"}:{escape(self.initial)}">'
            f"{first}</div>"
            '<div class="shrink-0 bg-slate-200 dark:bg-slate-800 '
            + ("w-1 cursor-col-resize" if self.direction == "horizontal" else "h-1 cursor-row-resize")
            + '"></div>'
            f'<div class="flex-1 overflow-auto p-3">{second}</div>'
        )


class Tooltip(Component):
    tag = "span"

    def __init__(
        self,
        *children: Any,
        content: Any = "",
        placement: str = "top",
        **props: Any,
    ) -> None:
        self.tooltip = content
        self.placement = placement
        props["base_class"] = tw("group relative inline-flex", props.get("base_class"))
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        place = {
            "top": "bottom-full left-1/2 mb-2 -translate-x-1/2",
            "bottom": "top-full left-1/2 mt-2 -translate-x-1/2",
            "left": "right-full top-1/2 mr-2 -translate-y-1/2",
            "right": "left-full top-1/2 ml-2 -translate-y-1/2",
        }.get(self.placement, "bottom-full left-1/2 mb-2 -translate-x-1/2")
        return (
            render_children(self.children, ctx, path)
            + f'<span role="tooltip" class="pointer-events-none absolute z-50 {place} whitespace-nowrap '
            'rounded-md bg-slate-900 px-2 py-1 text-xs font-medium text-white opacity-0 shadow-lg '
            'transition group-hover:opacity-100 dark:bg-slate-700">'
            f"{escape(self.tooltip)}</span>"
        )


class Popover(Component):
    tag = "span"

    def __init__(
        self,
        *children: Any,
        trigger: Any = "Abrir",
        title: Any = None,
        **props: Any,
    ) -> None:
        self.trigger_label = trigger
        self.popover_title = title
        props["base_class"] = tw("relative inline-flex", props.get("base_class"))
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        uid = ctx.uid(path, self.key, self.explicit_id)
        return (
            f'<button type="button" data-iui-toggle="{escape(uid)}-pop" '
            'class="inline-flex h-9 items-center gap-1.5 rounded-lg border border-slate-300 px-3 '
            'text-sm font-medium text-slate-700 transition hover:bg-slate-50 dark:border-slate-700 '
            'dark:text-slate-200 dark:hover:bg-slate-800">'
            f"{escape(self.trigger_label)}</button>"
            f'<div id="{escape(uid)}-pop" class="absolute left-0 top-full z-40 mt-2 hidden w-72 '
            'rounded-xl border border-slate-200 bg-white p-4 shadow-xl dark:border-slate-700 '
            'dark:bg-slate-900">'
            + (
                f'<p class="mb-2 text-sm font-semibold text-slate-900 dark:text-white">'
                f"{escape(self.popover_title)}</p>"
                if self.popover_title
                else ""
            )
            + render_children(self.children, ctx, path)
            + "</div>"
        )


class MenuItem(Component):
    """Entrada de un menú: barra de menús, desplegable o menú contextual.

    ```python
    ui.MenuItem("Guardar", icon="save", shortcut="Ctrl+S", on_click=guardar)
    ```
    """

    tag = "button"

    def __init__(
        self,
        label: Any = "",
        *,
        icon: str | None = None,
        shortcut: str | None = None,
        danger: bool = False,
        disabled: bool = False,
        href: str | None = None,
        on_click: Any = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.icon = icon
        self.shortcut = shortcut
        if href is not None:
            self.tag = "a"
            props["href"] = href
        else:
            props.setdefault("type", "button")
        if on_click is not None:
            props["on_click"] = on_click
        if disabled:
            props["disabled"] = True
            props["aria-disabled"] = "true"
        props["role"] = "menuitem"
        props["data"] = {**props.get("data", {}), "iui-menu-item": "true"}
        props["base_class"] = tw(
            "flex w-full items-center gap-2 px-3 py-1.5 text-left text-sm transition "
            "disabled:cursor-not-allowed disabled:opacity-40",
            "text-rose-600 hover:bg-rose-50 dark:text-rose-400 dark:hover:bg-rose-500/10"
            if danger
            else "text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return (
            (Icon(self.icon, size=4, class_="text-slate-400").render(ctx, path + "-ic") if self.icon else "")
            + f'<span class="flex-1">{escape(self.label)}</span>'
            + (f'<span class="text-xs text-slate-400">{escape(self.shortcut)}</span>' if self.shortcut else "")
        )


class Menu(Component):
    tag = "div"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["role"] = "menu"
        props["base_class"] = tw(
            "flex min-w-44 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white py-1 "
            "shadow-lg dark:border-slate-700 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Dropdown(Component):
    """Botón con menú desplegable gestionado en el cliente."""

    tag = "div"

    def __init__(
        self,
        *children: Any,
        label: Any = "Opciones",
        icon: str | None = None,
        variant: str = "outline",
        align: str = "left",
        **props: Any,
    ) -> None:
        self.label = label
        self.icon = icon
        self.variant = variant
        self.align = align
        props["base_class"] = tw("relative inline-block text-left", props.get("base_class"))
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        uid = ctx.uid(path, self.key, self.explicit_id)
        align = "left-0" if self.align == "left" else "right-0"
        button = Button(
            self.label,
            variant=self.variant,
            size="sm",
            icon=self.icon,
            icon_right="chevron-down",
            data={"iui-toggle": f"{uid}-menu"},
        ).render(ctx, f"{uid}-btn")
        return (
            f"{button}"
            f'<div id="{escape(uid)}-menu" role="menu" class="absolute {align} top-full z-40 mt-1 hidden '
            'min-w-44 flex-col overflow-hidden rounded-xl border border-slate-200 bg-white py-1 '
            'shadow-lg dark:border-slate-700 dark:bg-slate-900">'
            f"{render_children(self.children, ctx, path)}</div>"
        )


class TitleBar(Component):
    """Barra de título propia para ventanas sin marco (frameless).

    Los botones llaman al puente nativo, no al navegador. La zona arrastrable
    usa ``pywebview-drag-region``, que pywebview reconoce para mover la ventana.
    """

    tag = "div"

    def __init__(
        self,
        *children: Any,
        title: Any = None,
        icon: str | None = None,
        controls: bool = True,
        **props: Any,
    ) -> None:
        self.bar_title = title
        self.icon = icon
        self.controls = controls
        props["base_class"] = tw(
            "flex h-11 w-full shrink-0 select-none items-center gap-3 border-b border-slate-200 "
            "bg-white/85 px-3 backdrop-blur dark:border-slate-800 dark:bg-slate-950/85",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        left = ""
        if self.icon or self.bar_title:
            left = (
                '<div class="pywebview-drag-region flex flex-1 items-center gap-2">'
                + (
                    f'<span class="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-600 text-white">'
                    f"{Icon(self.icon, size=3).render(ctx, path + '-ic')}</span>"
                    if self.icon
                    else ""
                )
                + (
                    f'<span class="text-xs font-medium text-slate-600 dark:text-slate-300">'
                    f"{escape(self.bar_title)}</span>"
                    if self.bar_title
                    else ""
                )
                + "</div>"
            )
        body = render_children(self.children, ctx, path)
        button = (
            "flex h-7 w-7 items-center justify-center rounded-md text-slate-500 transition "
            "hover:bg-slate-200 dark:text-slate-400 dark:hover:bg-slate-700"
        )
        controls = ""
        if self.controls:
            controls = (
                '<div class="flex items-center gap-0.5">'
                f'<button type="button" data-iui-native="minimize" aria-label="Minimizar" class="{button}">'
                + Icon("minus", size=3).render(ctx, path + "-mi")
                + "</button>"
                f'<button type="button" data-iui-native="maximize" aria-label="Maximizar" class="{button}">'
                + Icon("maximize", size=3).render(ctx, path + "-ma")
                + "</button>"
                '<button type="button" data-iui-native="close" aria-label="Cerrar" '
                'class="flex h-7 w-7 items-center justify-center rounded-md text-slate-500 transition '
                'hover:bg-rose-500 hover:text-white dark:text-slate-400">'
                + Icon("x", size=3).render(ctx, path + "-cl")
                + "</button></div>"
            )
        return left + body + controls


class StatusBar(Component):
    """Barra inferior para mensajes de estado de la aplicación."""

    tag = "footer"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(
            "flex h-7 w-full shrink-0 items-center gap-3 border-t border-slate-200 bg-slate-50 "
            "px-3 text-[11px] text-slate-500 dark:border-slate-800 dark:bg-slate-900 "
            "dark:text-slate-400",
            props.get("base_class"),
        )
        super().__init__(*children, **props)
