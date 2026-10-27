"""Sistema de rejilla de 12 columnas sobre Tailwind CSS.

La rejilla es *responsive*: cada ``Col`` declara cuántas columnas ocupa en cada
breakpoint y Tailwind genera las utilidades ``sm:col-span-6``, ``lg:col-span-4``…
"""

from __future__ import annotations

from typing import Any

from .base import Component
from .style import tw

__all__ = [
    "Container", "Row", "Col", "Stack", "Spacer", "Divider", "Center",
    "AspectRatio", "ScrollArea", "Grid", "Screen", "BREAKPOINTS",
]

BREAKPOINTS = ("sm", "md", "lg", "xl", "2xl")


def _span_classes(prefix: str, value: Any, variant: str | None = None) -> list[str]:
    if value is None:
        return []
    v = f"{variant}:" if variant else ""
    if value in ("full", True):
        return [f"{v}{prefix}-full"]
    if value == "auto":
        return [f"{v}{prefix}-auto"]
    return [f"{v}{prefix}-{int(value)}"]


class Container(Component):
    """Ancho máximo centrado con padding lateral responsive."""

    def __init__(self, *children: Any, size: str = "xl", padded: bool = True, **props: Any) -> None:
        widths = {
            "sm": "max-w-screen-sm",
            "md": "max-w-screen-md",
            "lg": "max-w-screen-lg",
            "xl": "max-w-7xl",
            "full": "max-w-none",
            "prose": "max-w-3xl",
        }
        base = tw(
            "mx-auto w-full",
            "px-4 sm:px-6 lg:px-8" if padded else "",
            widths.get(size, "max-w-7xl"),
        )
        props["base_class"] = tw(base, props.get("base_class"))
        super().__init__(*children, **props)


class Row(Component):
    """Fila de la rejilla (``grid-cols-12``)."""

    def __init__(
        self,
        *children: Any,
        gap: int | str = 4,
        gap_y: int | str | None = None,
        align: str = "stretch",
        justify: str = "start",
        cols: int = 12,
        dense: bool = False,
        **props: Any,
    ) -> None:
        align_map = {
            "start": "items-start", "center": "items-center", "end": "items-end",
            "stretch": "items-stretch", "baseline": "items-baseline",
        }
        justify_map = {
            "start": "justify-start", "center": "justify-center", "end": "justify-end",
            "between": "justify-between", "around": "justify-around", "evenly": "justify-evenly",
        }
        gap_cls = f"gap-{gap}" if isinstance(gap, int) or str(gap).isdigit() else f"gap-{gap}"
        base = tw(
            "grid w-full",
            f"grid-cols-{cols}",
            gap_cls,
            f"gap-y-{gap_y}" if gap_y is not None else "",
            align_map.get(align, f"items-{align}"),
            justify_map.get(justify, ""),
            "grid-flow-row-dense" if dense else "",
        )
        props["base_class"] = tw(base, props.get("base_class"))
        super().__init__(*children, **props)


class Col(Component):
    """Columna de la rejilla de 12.

    ``Col(span=12, md=6, lg=4)`` ocupa el 100 % en móvil, la mitad en tablet y un
    tercio en escritorio.
    """

    def __init__(
        self,
        *children: Any,
        span: Any = 12,
        sm: Any = None,
        md: Any = None,
        lg: Any = None,
        xl: Any = None,
        xxl: Any = None,
        offset: int | None = None,
        order: int | str | None = None,
        **props: Any,
    ) -> None:
        classes: list[str] = []
        classes += _span_classes("col-span", span)
        for variant, value in (("sm", sm), ("md", md), ("lg", lg), ("xl", xl), ("2xl", xxl)):
            classes += _span_classes("col-span", value, variant)
        if offset:
            classes.append(f"col-start-{int(offset) + 1}")
        if order is not None:
            classes.append(f"order-{order}")
        classes.append("min-w-0")
        props["base_class"] = tw(" ".join(classes), props.get("base_class"))
        super().__init__(*children, **props)


class Stack(Component):
    """Apila hijos en vertical u horizontal con separación uniforme."""

    def __init__(
        self,
        *children: Any,
        direction: str = "col",
        gap: int | str = 4,
        align: str = "stretch",
        justify: str = "start",
        wrap: bool = False,
        **props: Any,
    ) -> None:
        align_map = {
            "start": "items-start", "center": "items-center", "end": "items-end",
            "stretch": "items-stretch", "baseline": "items-baseline",
        }
        justify_map = {
            "start": "justify-start", "center": "justify-center", "end": "justify-end",
            "between": "justify-between", "around": "justify-around", "evenly": "justify-evenly",
        }
        base = tw(
            "flex",
            "flex-col" if direction in ("col", "column", "v", "vertical") else "flex-row",
            f"gap-{gap}",
            align_map.get(align, f"items-{align}"),
            justify_map.get(justify, ""),
            "flex-wrap" if wrap else "",
        )
        props["base_class"] = tw(base, props.get("base_class"))
        super().__init__(*children, **props)


class Spacer(Component):
    """Empuja el contenido en un flexbox."""

    base_class = "flex-1"

    def __init__(self, **props: Any) -> None:
        super().__init__(**props)


class Divider(Component):
    tag = "hr"

    def __init__(self, label: str | None = None, orientation: str = "horizontal", **props: Any) -> None:
        if label:
            self.tag = "div"
        self.label = label
        self.orientation = orientation
        base = tw(
            "border-slate-200 dark:border-slate-700",
            "w-full border-t my-4" if orientation == "horizontal" else "h-full border-l mx-4",
            "flex items-center gap-3 border-0 my-4" if label else "",
        )
        props["base_class"] = tw(base, props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: Any, path: str) -> str:
        if not self.label:
            return ""
        from .html import escape

        return (
            '<span class="h-px flex-1 bg-slate-200 dark:bg-slate-700"></span>'
            f'<span class="text-xs font-medium uppercase tracking-wide text-slate-400">{escape(self.label)}</span>'
            '<span class="h-px flex-1 bg-slate-200 dark:bg-slate-700"></span>'
        )


class Center(Component):
    base_class = "flex items-center justify-center"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(Center.base_class, props.get("base_class"))
        super().__init__(*children, **props)


class AspectRatio(Component):
    def __init__(self, *children: Any, ratio: str = "video", **props: Any) -> None:
        ratios = {"video": "aspect-video", "square": "aspect-square", "wide": "aspect-[21/9]"}
        cls = ratios.get(ratio, f"aspect-[{ratio}]")
        props["base_class"] = tw(f"relative w-full {cls} overflow-hidden", props.get("base_class"))
        super().__init__(*children, **props)


class ScrollArea(Component):
    def __init__(self, *children: Any, max_h: str = "80", axis: str = "y", **props: Any) -> None:
        overflow = {"y": "overflow-y-auto", "x": "overflow-x-auto", "both": "overflow-auto"}[axis]
        props["base_class"] = tw(
            f"max-h-{max_h} {overflow} rounded-lg [scrollbar-width:thin]", props.get("base_class")
        )
        super().__init__(*children, **props)


class Grid(Component):
    """Rejilla nativa de Tailwind (número de columnas por breakpoint)."""

    def __init__(
        self,
        *children: Any,
        cols: int | str = 1,
        sm: int | None = None,
        md: int | None = None,
        lg: int | None = None,
        xl: int | None = None,
        gap: int | str = 4,
        **props: Any,
    ) -> None:
        classes = [f"grid grid-cols-{cols} gap-{gap} w-full"]
        for variant, value in (("sm", sm), ("md", md), ("lg", lg), ("xl", xl)):
            if value is not None:
                classes.append(f"{variant}:grid-cols-{value}")
        props["base_class"] = tw(" ".join(classes), props.get("base_class"))
        super().__init__(*children, **props)


class Screen(Component):
    """Contenedor a pantalla completa con scroll vertical."""

    base_class = "min-h-screen w-full bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(Screen.base_class, props.get("base_class"))
        super().__init__(*children, **props)
