"""Medios: imágenes, avatares, vídeo, audio y galerías."""

from __future__ import annotations

from typing import Any, Sequence

from ..base import Component, bind_many
from ..context import RenderContext
from ..html import escape
from ..icons import Icon
from ..style import tw
from ..theme import utility

__all__ = ["Image", "Figure", "Avatar", "AvatarGroup", "Video", "Audio", "Carousel", "Gallery", "IconBadge"]


class Image(Component):
    tag = "img"

    def __init__(
        self,
        src: str = "",
        *,
        alt: str = "",
        ratio: str | None = None,
        fit: str = "cover",
        rounded: str = "lg",
        width: int | None = None,
        height: int | None = None,
        **props: Any,
    ) -> None:
        props["src"] = src
        props["alt"] = alt
        props["loading"] = props.pop("loading", "lazy")
        if width:
            props["width"] = width
        if height:
            props["height"] = height
        fit_cls = {"cover": "object-cover", "contain": "object-contain", "fill": "object-fill"}.get(
            fit, "object-cover"
        )
        ratios = {"square": "aspect-square", "video": "aspect-video", "wide": "aspect-[21/9]"}
        props["base_class"] = tw(
            "block max-w-full",
            fit_cls,
            utility("rounded", rounded),
            ratios.get(ratio or "", f"{ratios[ratio]}" if ratio in ratios else ""),
            "h-full w-full object-center" if ratio else "h-auto",
            props.get("base_class"),
        )
        super().__init__(**props)


class Figure(Component):
    tag = "figure"

    def __init__(self, image: Any, *, caption: Any = None, **props: Any) -> None:
        self.image = image
        self.caption = caption
        props["base_class"] = tw("flex flex-col gap-2", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        body = render_children([self.image], ctx, path)
        cap = (
            f'<figcaption class="text-xs text-slate-500 dark:text-slate-400">{escape(self.caption)}</figcaption>'
            if self.caption
            else ""
        )
        return f'<div class="overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800">{body}</div>{cap}'


class Avatar(Component):
    tag = "span"

    def __init__(
        self,
        *,
        src: str | None = None,
        name: Any = "",
        initials: str | None = None,
        size: str = "md",
        status: str | None = None,
        ring: bool = True,
        **props: Any,
    ) -> None:
        self.src = src
        self.name = name
        self.initials = initials or _initials(name)
        self.status = status
        sizes = {"xs": "h-6 w-6 text-[10px]", "sm": "h-8 w-8 text-xs", "md": "h-10 w-10 text-sm",
                 "lg": "h-12 w-12 text-base", "xl": "h-16 w-16 text-lg"}
        props["title"] = props.get("title") or (str(name) if name else None)
        props["base_class"] = tw(
            "relative inline-flex shrink-0 items-center justify-center overflow-visible rounded-full",
            sizes.get(size, sizes["md"]),
            "ring-2 ring-white dark:ring-slate-950" if ring else "",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        inner = (
            f'<img src="{escape(self.src)}" alt="{escape(self.name)}" '
            'class="h-full w-full rounded-full object-cover"/>'
            if self.src
            else f'<span class="flex h-full w-full items-center justify-center rounded-full bg-indigo-100 '
                 f'font-semibold text-indigo-700 dark:bg-indigo-500/20 dark:text-indigo-300">'
                 f"{escape(self.initials)}</span>"
        )
        dot = ""
        if self.status:
            tones = {"online": "bg-emerald-500", "busy": "bg-rose-500", "away": "bg-amber-500",
                     "offline": "bg-slate-400"}
            dot = (
                f'<span class="absolute -bottom-0.5 -right-0.5 h-3 w-3 rounded-full border-2 '
                f'border-white dark:border-slate-950 {tones.get(self.status, tones["offline"])}"></span>'
            )
        return inner + dot


def _initials(name: Any) -> str:
    parts = [part for part in str(name or "").split() if part]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


class AvatarGroup(Component):
    tag = "div"

    def __init__(self, *children: Any, max_items: int = 4, **props: Any) -> None:
        self.max_items = max_items
        props["base_class"] = tw("flex items-center -space-x-2", props.get("base_class"))
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        items = list(self.children)
        shown = items[: self.max_items]
        rest = len(items) - len(shown)
        extra = (
            f'<span class="inline-flex h-10 w-10 items-center justify-center rounded-full bg-slate-200 '
            f'text-xs font-semibold text-slate-600 ring-2 ring-white dark:bg-slate-800 '
            f'dark:text-slate-300 dark:ring-slate-950">+{rest}</span>'
            if rest > 0
            else ""
        )
        return render_children(shown, ctx, path) + extra


class Video(Component):
    tag = "video"

    def __init__(
        self,
        src: str = "",
        *,
        poster: str | None = None,
        controls: bool = True,
        autoplay: bool = False,
        loop: bool = False,
        muted: bool = True,
        rounded: str = "xl",
        **props: Any,
    ) -> None:
        props["src"] = src
        if poster:
            props["poster"] = poster
        props["controls"] = controls
        if autoplay:
            props["autoplay"] = True
        if loop:
            props["loop"] = True
        if muted:
            props["muted"] = True
        props["base_class"] = tw(
            "w-full bg-black shadow-sm",
            utility("rounded", rounded),
            props.get("base_class"),
        )
        super().__init__(**props)


class Audio(Component):
    tag = "audio"

    def __init__(self, src: str = "", *, controls: bool = True, **props: Any) -> None:
        props["src"] = src
        props["controls"] = controls
        props["base_class"] = tw("w-full", props.get("base_class"))
        super().__init__(**props)


class Carousel(Component):
    """Carrusel controlado por Python (``index`` + ``on_change``)."""

    tag = "div"

    def __init__(
        self,
        slides: Sequence[Any] | None = None,
        *,
        index: int = 0,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.slides = list(slides or [])
        self.index = max(0, min(int(index), max(0, len(self.slides) - 1)))
        if on_change is not None:
            props["on_change"] = on_change
        props["base_class"] = tw("relative overflow-hidden rounded-2xl", props.get("base_class"))
        super().__init__(**props)

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, self.handlers, [f"c{index}" for index in range(len(self.slides))])
        return super().render(ctx, path)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        uid = ctx.uid(path, self.key, self.explicit_id)
        track = "".join(
            '<div class="w-full shrink-0">'
            + (
                slide.render(ctx, f"{path}-s{index}")
                if isinstance(slide, Component)
                else render_children([slide], ctx, f"{path}-s{index}")
            )
            + "</div>"
            for index, slide in enumerate(self.slides)
        )
        dots = "".join(
            f'<button type="button" id="{escape(uid)}-c{index}" data-iui-emit="change" '
            f'data-iui-value="{index}" data-iui-cast="int" aria-label="Ir a la diapositiva {index + 1}" '
            'class="h-2 rounded-full transition-all '
            + ("w-6 bg-white" if index == self.index else "w-2 bg-white/50 hover:bg-white/80")
            + '"></button>'
            for index in range(len(self.slides))
        )
        return (
            '<div class="overflow-hidden">'
            f'<div class="flex transition-transform duration-300" '
            f'style="transform:translateX(-{self.index * 100}%)">{track}</div></div>'
            f'<div class="absolute inset-x-0 bottom-3 flex justify-center gap-1.5">{dots}</div>'
        )


class Gallery(Component):
    tag = "div"

    def __init__(self, *children: Any, columns: int = 3, gap: int = 3, **props: Any) -> None:
        props["base_class"] = tw(
            "grid", f"grid-cols-2 sm:grid-cols-{columns}", utility("gap", gap),
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class IconBadge(Component):
    tag = "span"

    def __init__(self, icon: str = "check", *, tone: str = "primary", size: str = "md", **props: Any) -> None:
        self.icon = icon
        self.tone = tone
        sizes = {"sm": ("h-8 w-8", 4), "md": ("h-10 w-10", 5), "lg": ("h-12 w-12", 6)}
        box, icon_size = sizes.get(size, sizes["md"])
        self.icon_size = icon_size
        tones = {
            "primary": "bg-indigo-50 text-indigo-600 dark:bg-indigo-500/15 dark:text-indigo-300",
            "success": "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/15 dark:text-emerald-300",
            "warning": "bg-amber-50 text-amber-600 dark:bg-amber-500/15 dark:text-amber-300",
            "danger": "bg-rose-50 text-rose-600 dark:bg-rose-500/15 dark:text-rose-300",
            "neutral": "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300",
        }
        props["base_class"] = tw(
            "inline-flex shrink-0 items-center justify-center rounded-xl", box,
            tones.get(tone, tones["primary"]), props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return Icon(self.icon, size=self.icon_size).render(ctx, path + "-ic")
