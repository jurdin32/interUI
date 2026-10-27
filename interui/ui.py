"""Tokens visuales compartidos por todos los controles.

Todas las clases son literales para que Tailwind pueda detectarlas al escanear
el código Python.
"""

from __future__ import annotations

from typing import Any

from .html import escape, raw
from .style import tw

__all__ = [
    "BUTTON_VARIANTS", "BUTTON_SIZES", "BADGE_VARIANTS", "ALERT_VARIANTS",
    "INPUT_SIZES", "RADIUS", "SURFACE", "TEXT_MUTED", "field_shell", "sizes",
]

RADIUS = "rounded-lg"

SURFACE = (
    "rounded-2xl border border-slate-200 bg-white shadow-sm "
    "dark:border-slate-800 dark:bg-slate-900"
)

TEXT_MUTED = "text-slate-500 dark:text-slate-400"

BUTTON_SIZES = {
    "xs": "h-7 gap-1 rounded-md px-2 text-xs",
    "sm": "h-8 gap-1.5 rounded-md px-3 text-sm",
    "md": "h-10 gap-2 rounded-lg px-4 text-sm",
    "lg": "h-11 gap-2 rounded-lg px-5 text-base",
    "xl": "h-12 gap-2.5 rounded-xl px-6 text-base",
}

BUTTON_VARIANTS = {
    "primary": (
        "bg-indigo-600 text-white shadow-sm hover:bg-indigo-500 active:bg-indigo-700 "
        "focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
    ),
    "secondary": (
        "bg-slate-100 text-slate-900 hover:bg-slate-200 active:bg-slate-300 "
        "dark:bg-slate-800 dark:text-slate-100 dark:hover:bg-slate-700"
    ),
    "outline": (
        "border border-slate-300 bg-white text-slate-800 hover:bg-slate-50 "
        "dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:hover:bg-slate-800"
    ),
    "ghost": "text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800",
    "soft": (
        "bg-indigo-50 text-indigo-700 hover:bg-indigo-100 "
        "dark:bg-indigo-500/15 dark:text-indigo-300 dark:hover:bg-indigo-500/25"
    ),
    "danger": "bg-rose-600 text-white shadow-sm hover:bg-rose-500 active:bg-rose-700",
    "success": "bg-emerald-600 text-white shadow-sm hover:bg-emerald-500 active:bg-emerald-700",
    "warning": "bg-amber-500 text-slate-950 shadow-sm hover:bg-amber-400",
    "link": "px-0 text-indigo-600 underline-offset-4 hover:underline dark:text-indigo-400",
}

BADGE_VARIANTS = {
    "neutral": "bg-slate-100 text-slate-700 ring-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:ring-slate-700",
    "primary": "bg-indigo-50 text-indigo-700 ring-indigo-200 dark:bg-indigo-500/15 dark:text-indigo-300 dark:ring-indigo-500/30",
    "success": "bg-emerald-50 text-emerald-700 ring-emerald-200 dark:bg-emerald-500/15 dark:text-emerald-300 dark:ring-emerald-500/30",
    "warning": "bg-amber-50 text-amber-800 ring-amber-200 dark:bg-amber-500/15 dark:text-amber-300 dark:ring-amber-500/30",
    "danger": "bg-rose-50 text-rose-700 ring-rose-200 dark:bg-rose-500/15 dark:text-rose-300 dark:ring-rose-500/30",
    "info": "bg-sky-50 text-sky-700 ring-sky-200 dark:bg-sky-500/15 dark:text-sky-300 dark:ring-sky-500/30",
    "outline": "bg-transparent text-slate-600 ring-slate-300 dark:text-slate-300 dark:ring-slate-700",
}

ALERT_VARIANTS = {
    "info": "border-sky-200 bg-sky-50 text-sky-900 dark:border-sky-500/30 dark:bg-sky-500/10 dark:text-sky-200",
    "success": "border-emerald-200 bg-emerald-50 text-emerald-900 dark:border-emerald-500/30 dark:bg-emerald-500/10 dark:text-emerald-200",
    "warning": "border-amber-200 bg-amber-50 text-amber-900 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-200",
    "danger": "border-rose-200 bg-rose-50 text-rose-900 dark:border-rose-500/30 dark:bg-rose-500/10 dark:text-rose-200",
    "neutral": "border-slate-200 bg-slate-50 text-slate-800 dark:border-slate-700 dark:bg-slate-800/60 dark:text-slate-200",
}

INPUT_SIZES = {
    "sm": "h-8 px-2.5 text-sm",
    "md": "h-10 px-3 text-sm",
    "lg": "h-11 px-4 text-base",
}

INPUT_BASE = (
    "w-full rounded-lg border border-slate-300 bg-white text-slate-900 shadow-sm "
    "placeholder:text-slate-400 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 "
    "focus:outline-none disabled:cursor-not-allowed disabled:bg-slate-100 disabled:text-slate-500 "
    "dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 "
    "dark:placeholder:text-slate-500 dark:disabled:bg-slate-800"
)


def sizes(kind: str, size: str) -> str:
    table = {"button": BUTTON_SIZES, "input": INPUT_SIZES}[kind]
    return table.get(size, table["md"])


def field_shell(
    control: str,
    uid: str,
    *,
    label: Any = None,
    help_text: Any = None,
    error: Any = None,
    required: bool = False,
    horizontal: bool = False,
    class_: Any = None,
) -> str:
    """Envuelve un control con etiqueta, texto de ayuda y error."""
    if not (label or help_text or error):
        return control
    label_html = ""
    if label:
        required_mark = '<span class="text-rose-500">*</span>' if required else ""
        label_html = (
            f'<label for="{escape(uid)}" class="flex items-center gap-1 text-sm font-medium '
            'text-slate-700 dark:text-slate-200">'
            f"{escape(label)}{required_mark}</label>"
        )
    help_html = ""
    if help_text and not error:
        help_html = f'<p class="text-xs text-slate-500 dark:text-slate-400">{escape(help_text)}</p>'
    error_html = ""
    if error:
        error_html = f'<p class="text-xs font-medium text-rose-600 dark:text-rose-400">{escape(error)}</p>'
    wrapper = tw(
        "flex flex-col gap-1.5",
        "sm:grid sm:grid-cols-[10rem_1fr] sm:items-center sm:gap-4" if horizontal else "",
        class_,
    )
    body = f"{label_html}<div class=\"flex flex-col gap-1.5\">{control}{help_html}{error_html}</div>"
    return f'<div class="{wrapper}">{body}</div>'


def icon_svg(paths: str, size_class: str, color_class: str = "", extra: str = "") -> str:
    classes = tw("shrink-0", size_class, color_class, extra)
    return raw(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" class="{classes}" aria-hidden="true">{paths}</svg>'
    )
