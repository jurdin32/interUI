"""Retroalimentación: alertas, progreso, esqueletos y avisos."""

from __future__ import annotations

import math
from typing import Any

from ..base import Component
from ..context import RenderContext
from ..html import escape
from ..icons import Icon
from ..style import tw
from ..ui import ALERT_VARIANTS

__all__ = [
    "Alert", "Banner", "Callout", "Progress", "ProgressRing", "Meter", "Skeleton",
    "LoadingOverlay", "StatusDot", "InlineToast", "ConfirmDialog", "Hint",
]

LEVEL_ICONS = {
    "info": "info",
    "success": "check-circle",
    "warning": "alert",
    "danger": "alert",
    "neutral": "info",
}


class Alert(Component):
    tag = "div"

    def __init__(
        self,
        *children: Any,
        title: Any = None,
        level: str = "info",
        icon: str | None = None,
        dismissible: bool = False,
        bordered: bool = True,
        **props: Any,
    ) -> None:
        self.title = title
        self.level = level
        self.icon = icon if icon is not None else LEVEL_ICONS.get(level, "info")
        self.dismissible = dismissible
        props["role"] = "alert"
        if dismissible:
            props["data"] = {"iui-dismissible": "true", **(props.get("data") or {})}
        props["base_class"] = tw(
            "flex items-start gap-3 rounded-xl p-3.5 text-sm",
            "border" if bordered else "",
            ALERT_VARIANTS.get(level, ALERT_VARIANTS["info"]),
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        body = render_children(self.children, ctx, path)
        head = ""
        if self.title:
            head = f'<p class="font-semibold">{escape(self.title)}</p>'
        icon = (
            f'<span class="mt-0.5 shrink-0">{Icon(self.icon, size=5).render(ctx, path + "-ic")}</span>'
            if self.icon
            else ""
        )
        close = (
            '<button type="button" data-iui-dismiss="" aria-label="Cerrar" '
            'class="ml-auto shrink-0 rounded-md p-1 opacity-60 transition hover:bg-black/5 hover:opacity-100">'
            + Icon("x", size=4).render(ctx, path + "-x")
            + "</button>"
            if self.dismissible
            else ""
        )
        return f'{icon}<div class="flex min-w-0 flex-1 flex-col gap-0.5">{head}{body}</div>{close}'


class Banner(Component):
    tag = "div"

    def __init__(self, *children: Any, level: str = "info", icon: str | None = None, **props: Any) -> None:
        self.level = level
        self.icon = icon if icon is not None else LEVEL_ICONS.get(level, "info")
        tones = {
            "info": "bg-sky-600 text-white",
            "success": "bg-emerald-600 text-white",
            "warning": "bg-amber-500 text-slate-950",
            "danger": "bg-rose-600 text-white",
            "neutral": "bg-slate-900 text-white",
        }
        props["base_class"] = tw(
            "flex w-full items-center justify-center gap-2 px-4 py-2 text-center text-sm font-medium",
            tones.get(level, tones["info"]),
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        return (
            Icon(self.icon, size=4).render(ctx, path + "-ic")
            + render_children(self.children, ctx, path)
        )


Callout = Alert


class Progress(Component):
    tag = "div"

    def __init__(
        self,
        value: float = 0,
        *,
        max_value: float = 100,
        label: Any = None,
        show_value: bool = False,
        tone: str = "primary",
        size: str = "md",
        striped: bool = False,
        indeterminate: bool = False,
        **props: Any,
    ) -> None:
        self.value = value
        self.max_value = max_value or 100
        self.label = label
        self.show_value = show_value
        self.tone = tone
        self.size = size
        self.striped = striped
        self.indeterminate = indeterminate
        props["base_class"] = tw("flex w-full flex-col gap-1.5", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        tones = {
            "primary": "bg-indigo-600",
            "success": "bg-emerald-500",
            "warning": "bg-amber-500",
            "danger": "bg-rose-500",
            "neutral": "bg-slate-500",
        }
        heights = {"xs": "h-1", "sm": "h-1.5", "md": "h-2", "lg": "h-3"}
        percent = 0.0 if self.indeterminate else max(0.0, min(100.0, (self.value / self.max_value) * 100))
        bar_cls = tw(
            "h-full rounded-full transition-all duration-500",
            tones.get(self.tone, tones["primary"]),
            "animate-pulse" if self.indeterminate else "",
            "bg-[linear-gradient(45deg,rgba(255,255,255,.25)_25%,transparent_25%,transparent_50%,rgba(255,255,255,.25)_50%,rgba(255,255,255,.25)_75%,transparent_75%,transparent)] bg-[length:1rem_1rem]"
            if self.striped
            else "",
        )
        width = "100%" if self.indeterminate else f"{percent:.1f}%"
        head = ""
        if self.label or self.show_value:
            shown = f"{self.value:g}/{self.max_value:g}"
            head = (
                '<div class="flex items-center justify-between text-xs font-medium text-slate-600 '
                f'dark:text-slate-300"><span>{escape(self.label or "")}</span>'
                + (f"<span>{shown}</span>" if self.show_value else "")
                + "</div>"
            )
        return (
            f"{head}"
            f'<div class="w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800 '
            f'{heights.get(self.size, heights["md"])}" role="progressbar" aria-valuenow="{percent:.0f}" '
            f'aria-valuemin="0" aria-valuemax="100"><div class="{bar_cls}" style="width:{width}"></div></div>'
        )


class ProgressRing(Component):
    tag = "div"

    def __init__(
        self,
        value: float = 0,
        *,
        max_value: float = 100,
        size: int = 96,
        thickness: int = 8,
        label: Any = None,
        tone: str = "primary",
        **props: Any,
    ) -> None:
        self.value = value
        self.max_value = max_value or 100
        self.size = size
        self.thickness = thickness
        self.label = label
        self.tone = tone
        props["base_class"] = tw("inline-flex flex-col items-center gap-1", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        tones = {
            "primary": "#4f46e5",
            "success": "#10b981",
            "warning": "#f59e0b",
            "danger": "#f43f5e",
        }
        radius = (self.size - self.thickness) / 2
        circumference = 2 * math.pi * radius
        percent = max(0.0, min(1.0, self.value / self.max_value))
        offset = circumference * (1 - percent)
        return (
            f'<svg width="{self.size}" height="{self.size}" viewBox="0 0 {self.size} {self.size}" '
            'class="-rotate-90">'
            f'<circle cx="{self.size / 2}" cy="{self.size / 2}" r="{radius}" fill="none" '
            'stroke="currentColor" class="text-slate-200 dark:text-slate-800" '
            f'stroke-width="{self.thickness}"/>'
            f'<circle cx="{self.size / 2}" cy="{self.size / 2}" r="{radius}" fill="none" '
            f'stroke="{tones.get(self.tone, tones["primary"])}" stroke-width="{self.thickness}" '
            f'stroke-linecap="round" stroke-dasharray="{circumference:.1f}" '
            f'stroke-dashoffset="{offset:.1f}" class="transition-all duration-500"/></svg>'
            + (
                f'<span class="text-sm font-semibold text-slate-800 dark:text-slate-100">'
                f"{escape(self.label if self.label is not None else f'{percent * 100:.0f}%')}</span>"
            )
        )


class Meter(Component):
    tag = "div"

    def __init__(self, value: float = 0, *, max_value: float = 100, label: Any = None, **props: Any) -> None:
        self.value = value
        self.max_value = max_value or 100
        self.label = label
        props["base_class"] = tw("flex flex-col gap-1", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        percent = max(0.0, min(100.0, (self.value / self.max_value) * 100))
        tone = "bg-emerald-500" if percent >= 70 else "bg-amber-500" if percent >= 35 else "bg-rose-500"
        return (
            '<div class="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400">'
            f"<span>{escape(self.label or '')}</span><span>{percent:.0f}%</span></div>"
            '<div class="h-2 w-full overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">'
            f'<div class="h-full rounded-full {tone} transition-all" style="width:{percent:.1f}%"></div></div>'
        )


class Skeleton(Component):
    tag = "div"

    def __init__(
        self,
        *,
        width: str = "full",
        height: str = "4",
        circle: bool = False,
        lines: int = 1,
        **props: Any,
    ) -> None:
        self.width = width
        self.height = height
        self.circle = circle
        self.lines = lines
        props["base_class"] = tw("flex flex-col gap-2", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        if self.circle:
            return (
                f'<div class="h-{self.height} w-{self.height} animate-pulse rounded-full bg-slate-200 '
                'dark:bg-slate-800"></div>'
            )
        return "".join(
            f'<div class="h-{self.height} w-{self.width} animate-pulse rounded-md bg-slate-200 '
            f'dark:bg-slate-800{" opacity-70" if index else ""}"></div>'
            for index in range(max(1, self.lines))
        )


class LoadingOverlay(Component):
    tag = "div"

    def __init__(self, *children: Any, message: Any = "Cargando…", **props: Any) -> None:
        self.message = message
        props["base_class"] = tw(
            "relative overflow-hidden rounded-xl", props.get("base_class")
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        return (
            render_children(self.children, ctx, path)
            + '<div class="absolute inset-0 z-10 flex flex-col items-center justify-center gap-2 '
            'bg-white/70 backdrop-blur-sm dark:bg-slate-950/70">'
            '<span class="h-6 w-6 animate-spin rounded-full border-2 border-slate-300 '
            'border-t-indigo-600 dark:border-slate-700 dark:border-t-indigo-400"></span>'
            f'<span class="text-xs font-medium text-slate-600 dark:text-slate-300">{escape(self.message)}</span>'
            "</div>"
        )


class StatusDot(Component):
    tag = "span"

    def __init__(self, label: Any = None, *, tone: str = "success", pulse: bool = False, **props: Any) -> None:
        self.label = label
        self.tone = tone
        self.pulse = pulse
        props["base_class"] = tw(
            "inline-flex items-center gap-1.5 text-xs font-medium text-slate-600 dark:text-slate-300",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        tones = {
            "success": "bg-emerald-500",
            "primary": "bg-indigo-500",
            "warning": "bg-amber-500",
            "danger": "bg-rose-500",
            "neutral": "bg-slate-400",
        }
        return (
            f'<span class="relative flex h-2 w-2"><span class="absolute inline-flex h-full w-full '
            f'rounded-full {tones.get(self.tone, tones["success"])}'
            + (" animate-ping opacity-60" if self.pulse else "")
            + f'"></span><span class="relative inline-flex h-2 w-2 rounded-full '
            f'{tones.get(self.tone, tones["success"])}"></span></span>'
            + (escape(self.label) if self.label else "")
        )


class InlineToast(Component):
    tag = "div"

    def __init__(self, *children: Any, title: Any = None, level: str = "info", **props: Any) -> None:
        self.title = title
        self.level = level
        props["base_class"] = tw(
            "flex items-start gap-2 rounded-lg px-3 py-2 text-sm shadow-lg ring-1 ring-inset",
            ALERT_VARIANTS.get(level, ALERT_VARIANTS["info"]),
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        return (
            Icon(LEVEL_ICONS.get(self.level, "info"), size=4).render(ctx, path + "-ic")
            + '<span class="flex flex-col">'
            + (f'<b class="font-semibold">{escape(self.title)}</b>' if self.title else "")
            + render_children(self.children, ctx, path)
            + "</span>"
        )


class ConfirmDialog(Component):
    """Diálogo de confirmación que delega la decisión en Python."""

    tag = "div"

    def __init__(
        self,
        *children: Any,
        title: Any = "¿Estás seguro?",
        confirm_label: str = "Confirmar",
        cancel_label: str = "Cancelar",
        on_confirm: Any = None,
        on_cancel: Any = None,
        level: str = "danger",
        open: bool = False,
        **props: Any,
    ) -> None:
        self.title = title
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        self.level = level
        self.open = open
        if on_confirm is not None:
            props["on_confirm"] = on_confirm
        if on_cancel is not None:
            props["on_cancel"] = on_cancel
        props["base_class"] = tw(
            "fixed inset-0 z-50 items-center justify-center bg-slate-950/50 p-4 backdrop-blur-sm",
            "flex" if open else "hidden",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def attr_map(self, ctx: RenderContext, uid: str) -> dict[str, Any]:
        return {"data-iui-dialog": self.explicit_id or uid}

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        uid = ctx.uid(path, self.key, self.explicit_id)
        ctx.bind(f"{uid}-yes", "click", self.handlers.get("confirm"))
        ctx.bind(f"{uid}-no", "click", self.handlers.get("cancel"))
        tones = {"danger": "bg-rose-600 hover:bg-rose-500", "primary": "bg-indigo-600 hover:bg-indigo-500"}
        return (
            '<div class="w-full max-w-md rounded-2xl bg-white p-5 shadow-xl dark:bg-slate-900">'
            f'<h3 class="text-base font-semibold text-slate-900 dark:text-white">{escape(self.title)}</h3>'
            f'<div class="mt-2 text-sm text-slate-600 dark:text-slate-300">{render_children(self.children, ctx, path)}</div>'
            '<div class="mt-5 flex justify-end gap-2">'
            f'<button type="button" id="{escape(uid)}-no" data-iui-emit="click" '
            'class="h-9 rounded-lg border border-slate-300 px-3 text-sm font-medium text-slate-700 '
            'transition hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800">'
            f"{escape(self.cancel_label)}</button>"
            f'<button type="button" id="{escape(uid)}-yes" data-iui-emit="click" '
            f'class="h-9 rounded-lg px-3 text-sm font-medium text-white shadow-sm {tones.get(self.level, tones["danger"])}">'
            f"{escape(self.confirm_label)}</button>"
            "</div></div>"
        )


class Hint(Component):
    tag = "p"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("text-xs text-slate-500 dark:text-slate-400", props.get("base_class"))
        super().__init__(*children, **props)
