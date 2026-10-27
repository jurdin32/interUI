"""Tipografía, etiquetas y textos."""

from __future__ import annotations

from typing import Any

from ..base import Component
from ..context import RenderContext
from ..html import escape
from ..icons import Icon
from ..style import tw
from ..ui import BADGE_VARIANTS

__all__ = [
    "Heading", "Title", "Text", "Paragraph", "Muted", "Lead", "Label", "Strong",
    "Em", "Code", "Kbd", "Mark", "Small", "Link", "Badge", "Chip", "Blockquote",
    "CodeBlock", "Announcement",
]

HEADING_SIZES = {
    1: "text-4xl font-bold tracking-tight sm:text-5xl",
    2: "text-3xl font-semibold tracking-tight",
    3: "text-2xl font-semibold tracking-tight",
    4: "text-xl font-semibold",
    5: "text-lg font-semibold",
    6: "text-base font-semibold",
}

TEXT_SIZES = {
    "xs": "text-xs",
    "sm": "text-sm",
    "base": "text-[15px]",
    "lg": "text-lg",
    "xl": "text-xl",
}

TEXT_TONES = {
    "default": "text-slate-900 dark:text-slate-100",
    "muted": "text-slate-500 dark:text-slate-400",
    "subtle": "text-slate-400 dark:text-slate-500",
    "primary": "text-indigo-600 dark:text-indigo-400",
    "success": "text-emerald-600 dark:text-emerald-400",
    "warning": "text-amber-600 dark:text-amber-400",
    "danger": "text-rose-600 dark:text-rose-400",
    "inherit": "",
}


class Heading(Component):
    def __init__(self, *children: Any, level: int = 2, tone: str = "default", **props: Any) -> None:
        self.tag = f"h{max(1, min(6, int(level)))}"
        props["base_class"] = tw(
            "font-sans", HEADING_SIZES.get(level, HEADING_SIZES[2]), TEXT_TONES.get(tone, ""),
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Title(Heading):
    def __init__(self, *children: Any, subtitle: Any = None, **props: Any) -> None:
        super().__init__(*children, level=1, **props)
        self.children = list(self.children)
        if subtitle:
            self.children.append(Paragraph(str(subtitle), tone="muted", class_="mt-2"))


class Text(Component):
    tag = "p"

    def __init__(
        self,
        *children: Any,
        size: str = "base",
        tone: str = "default",
        weight: str | None = None,
        leading: str | None = None,
        truncate: bool = False,
        **props: Any,
    ) -> None:
        props["base_class"] = tw(
            TEXT_SIZES.get(size, "text-[15px]"),
            TEXT_TONES.get(tone, ""),
            f"font-{weight}" if weight else "",
            f"leading-{leading}" if leading else "",
            "truncate" if truncate else "",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Paragraph(Component):
    tag = "p"

    def __init__(self, *children: Any, tone: str = "default", size: str = "base", **props: Any) -> None:
        props["base_class"] = tw(
            TEXT_SIZES.get(size, "text-[15px]"), TEXT_TONES.get(tone, ""), "leading-relaxed",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Muted(Paragraph):
    def __init__(self, *children: Any, **props: Any) -> None:
        super().__init__(*children, tone="muted", size="sm", **props)


class Lead(Paragraph):
    def __init__(self, *children: Any, **props: Any) -> None:
        super().__init__(*children, tone="muted", size="lg", **props)


class Label(Component):
    tag = "label"

    def __init__(self, *children: Any, required: bool = False, for_: str | None = None, **props: Any) -> None:
        props["base_class"] = tw(
            "text-sm font-medium text-slate-700 dark:text-slate-200", props.get("base_class")
        )
        if for_:
            props["for"] = for_
        super().__init__(*children, **props)
        if required:
            self.children.append(Component(tag="span", base_class="text-rose-500")("*"))


class Strong(Component):
    tag = "strong"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("font-semibold text-slate-900 dark:text-white", props.get("base_class"))
        super().__init__(*children, **props)


class Em(Component):
    tag = "em"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("italic", props.get("base_class"))
        super().__init__(*children, **props)


class Code(Component):
    tag = "code"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(
            "rounded-md bg-slate-100 px-1.5 py-0.5 font-mono text-[0.85em] text-rose-600 "
            "dark:bg-slate-800 dark:text-rose-300",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Kbd(Component):
    tag = "kbd"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(
            "inline-flex min-w-[1.75rem] items-center justify-center rounded-md border border-slate-300 "
            "border-b-2 bg-slate-50 px-1.5 py-0.5 font-sans text-[11px] font-medium text-slate-600 "
            "dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Mark(Component):
    tag = "mark"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("rounded bg-amber-200 px-0.5 text-slate-900", props.get("base_class"))
        super().__init__(*children, **props)


class Small(Component):
    tag = "small"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("text-xs text-slate-500 dark:text-slate-400", props.get("base_class"))
        super().__init__(*children, **props)


class Link(Component):
    tag = "a"

    def __init__(self, *children: Any, href: str = "#", external: bool = False, **props: Any) -> None:
        props["href"] = href
        if external:
            props.setdefault("target", "_blank")
            props.setdefault("rel", "noopener noreferrer")
        props["base_class"] = tw(
            "font-medium text-indigo-600 underline-offset-4 transition hover:underline "
            "dark:text-indigo-400",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Badge(Component):
    tag = "span"

    def __init__(
        self,
        label: Any = "",
        *,
        variant: str = "neutral",
        size: str = "md",
        dot: bool = False,
        icon: str | None = None,
        pill: bool = True,
        **props: Any,
    ) -> None:
        sizes = {
            "sm": "px-1.5 py-0.5 text-[10px] gap-1",
            "md": "px-2 py-0.5 text-xs gap-1",
            "lg": "px-2.5 py-1 text-sm gap-1.5",
        }
        props["base_class"] = tw(
            "inline-flex items-center font-medium ring-1 ring-inset",
            "rounded-full" if pill else "rounded-md",
            sizes.get(size, sizes["md"]),
            BADGE_VARIANTS.get(variant, BADGE_VARIANTS["neutral"]),
            props.get("base_class"),
        )
        super().__init__(**props)
        if dot:
            self.children.append(
                Component(tag="span", base_class="h-1.5 w-1.5 rounded-full bg-current opacity-70")
            )
        if icon:
            self.children.append(Icon(icon, size=3))
        self.children.append(label)


class Chip(Component):
    tag = "span"

    def __init__(
        self,
        label: Any = "",
        *,
        on_remove: Any = None,
        variant: str = "neutral",
        **props: Any,
    ) -> None:
        props["base_class"] = tw(
            "inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset",
            BADGE_VARIANTS.get(variant, BADGE_VARIANTS["neutral"]),
            props.get("base_class"),
        )
        super().__init__(**props)
        self.children.append(label)
        if on_remove is not None:
            remove = Component(
                tag="button",
                base_class="ml-0.5 rounded-full p-0.5 opacity-60 transition hover:bg-black/10 hover:opacity-100",
                type="button",
                on_click=on_remove,
                aria={"label": "Quitar"},
            )(Icon("x", size=3))
            self.children.append(remove)


class Blockquote(Component):
    tag = "blockquote"

    def __init__(self, *children: Any, cite: str | None = None, **props: Any) -> None:
        props["base_class"] = tw(
            "border-l-4 border-indigo-400 bg-slate-50 py-2 pl-4 pr-3 italic text-slate-700 "
            "dark:border-indigo-500 dark:bg-slate-900 dark:text-slate-300",
            "rounded-r-lg",
            props.get("base_class"),
        )
        super().__init__(*children, **props)
        if cite:
            self.children.append(
                Component(tag="footer", base_class="mt-1 text-xs not-italic text-slate-500")(
                    f"— {cite}"
                )
            )


class CodeBlock(Component):
    """Bloque de código con botón de copia al portapapeles."""

    tag = "div"

    def __init__(
        self,
        code: str = "",
        *,
        language: str | None = None,
        filename: str | None = None,
        max_h: str = "none",
        **props: Any,
    ) -> None:
        self.code = code
        self.language = language
        self.filename = filename
        self.max_h = max_h
        props["base_class"] = tw(
            "overflow-hidden rounded-xl border border-slate-800 bg-slate-950 text-slate-100 shadow-sm",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        header = ""
        if self.filename or self.language:
            header = (
                '<div class="flex items-center justify-between gap-3 border-b border-slate-800 '
                'bg-slate-900/80 px-4 py-2 text-xs text-slate-400">'
                f'<span class="font-mono">{escape(self.filename or self.language or "")}</span>'
                '<button type="button" data-iui-copy="' + escape(self.code) + '" '
                'class="inline-flex items-center gap-1 rounded-md px-2 py-1 transition hover:bg-slate-800 '
                'hover:text-slate-200">copiar</button></div>'
            )
        overflow = "overflow-auto" if self.max_h != "none" else "overflow-x-auto"
        height = f" max-h-{self.max_h}" if self.max_h != "none" else ""
        return (
            f"{header}<pre class=\"{overflow}{height} p-4 text-[13px] leading-relaxed\">"
            f'<code class="font-mono">{escape(self.code)}</code></pre>'
        )


class Announcement(Component):
    """Franja destacada de una línea (banner superior)."""

    tag = "div"

    def __init__(self, *children: Any, variant: str = "primary", **props: Any) -> None:
        tones = {
            "primary": "bg-indigo-600 text-white",
            "dark": "bg-slate-900 text-white",
            "soft": "bg-indigo-50 text-indigo-800 dark:bg-indigo-500/10 dark:text-indigo-200",
        }
        props["base_class"] = tw(
            "flex w-full items-center justify-center gap-2 px-4 py-2 text-center text-sm",
            tones.get(variant, tones["primary"]),
            props.get("base_class"),
        )
        super().__init__(*children, **props)
