"""Gráficos SVG sin dependencias externas."""

from __future__ import annotations

import math
from typing import Any, Sequence

from ..base import Component
from ..context import RenderContext
from ..html import escape
from ..style import tw
from ..theme import css_value

__all__ = [
    "LineChart", "AreaChart", "BarChart", "ColumnChart", "ScatterChart",
    "PieChart", "DonutChart", "Sparkline", "Gauge", "ChartCard", "Legend",
]

PALETTE = ["#4f46e5", "#10b981", "#f59e0b", "#f43f5e", "#0ea5e9", "#a855f7", "#14b8a6"]


def _series_of(series: Sequence[Any] | dict[str, Any] | None) -> list[dict[str, Any]]:
    if series is None:
        return []
    if isinstance(series, dict):
        return [{"name": key, "data": list(value)} for key, value in series.items()]
    out = []
    for index, item in enumerate(series):
        if isinstance(item, dict):
            out.append({"name": str(item.get("name", f"Serie {index + 1}")), "data": list(item.get("data", []))})
        else:
            out.append({"name": f"Serie {index + 1}", "data": list(item)})
    return out


class _ChartBase(Component):
    tag = "div"

    width = 640
    height = 260
    padding = (18, 18, 34, 44)

    def __init__(
        self,
        series: Sequence[Any] | dict[str, Any] | None = None,
        *,
        labels: Sequence[Any] | None = None,
        height: int = 260,
        show_grid: bool = True,
        show_legend: bool = True,
        show_values: bool = False,
        colors: Sequence[str] | None = None,
        **props: Any,
    ) -> None:
        self.series = _series_of(series)
        self.labels = [str(label) for label in (labels or [])]
        self.chart_height = height
        self.show_grid = show_grid
        self.show_legend = show_legend
        self.show_values = show_values
        self.colors = list(colors or PALETTE)
        props["base_class"] = tw("flex w-full flex-col gap-3", props.get("base_class"))
        super().__init__(**props)

    # -- geometría -------------------------------------------------------
    def _bounds(self) -> tuple[float, float]:
        values = [value for serie in self.series for value in serie["data"] if value is not None]
        if not values:
            return 0.0, 1.0
        low, high = min(values), max(values)
        if low > 0:
            low = 0.0
        if high == low:
            high = low + 1
        else:
            high = high + (high - low) * 0.08
        return low, high

    def _x(self, index: int, count: int) -> float:
        left, right = self.padding[3], self.width - self.padding[1]
        if count <= 1:
            return (left + right) / 2
        return left + (right - left) * index / (count - 1)

    def _y(self, value: float, low: float, high: float) -> float:
        top, bottom = self.padding[0], self.height - self.padding[2]
        return bottom - (value - low) / (high - low) * (bottom - top)

    def _grid(self, low: float, high: float) -> str:
        if not self.show_grid:
            return ""
        parts = []
        for step in range(5):
            value = low + (high - low) * step / 4
            y = self._y(value, low, high)
            parts.append(
                f'<line x1="{self.padding[3]}" y1="{y:.1f}" x2="{self.width - self.padding[1]}" '
                f'y2="{y:.1f}" stroke="currentColor" stroke-opacity="0.12" stroke-width="1"/>'
                f'<text x="{self.padding[3] - 8}" y="{y + 3:.1f}" text-anchor="end" font-size="9" '
                f'fill="currentColor" fill-opacity="0.55">{_fmt(value)}</text>'
            )
        return "".join(parts)

    def _x_labels(self, count: int) -> str:
        if not self.labels:
            return ""
        bottom = self.height - self.padding[2] + 14
        parts = []
        for index, label in enumerate(self.labels[:count]):
            x = self._x(index, count)
            parts.append(
                f'<text x="{x:.1f}" y="{bottom}" text-anchor="middle" font-size="9" '
                f'fill="currentColor" fill-opacity="0.55">{escape(label)}</text>'
            )
        return "".join(parts)

    def _legend(self) -> str:
        if not self.show_legend or len(self.series) < 2:
            return ""
        items = "".join(
            f'<span class="inline-flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">'
            f'<span class="h-2 w-2 rounded-full" style="background:{self.colors[index % len(self.colors)]}"></span>'
            f"{escape(serie['name'])}</span>"
            for index, serie in enumerate(self.series)
        )
        return f'<div class="flex flex-wrap items-center gap-x-4 gap-y-1">{items}</div>'

    def _svg(self, body: str) -> str:
        return (
            f'<svg viewBox="0 0 {self.width} {self.height}" class="h-auto w-full text-slate-500 '
            f'dark:text-slate-400" preserveAspectRatio="none" role="img">{body}</svg>'
        )

    def content(self, ctx: RenderContext, path: str) -> str:
        return self._legend() + self._render_chart()

    def _render_chart(self) -> str:  # pragma: no cover - implementado por subclases
        return ""


def _fmt(value: float) -> str:
    if abs(value) >= 1000:
        return f"{value / 1000:.1f}k"
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.1f}"


class LineChart(_ChartBase):
    def __init__(self, series: Sequence[Any] | dict[str, Any] | None = None, *, smooth: bool = False,
                 fill: bool = False, **props: Any) -> None:
        self.smooth = smooth
        self.fill = fill
        super().__init__(series, **props)

    def _render_chart(self) -> str:
        low, high = self._bounds()
        count = max((len(serie["data"]) for serie in self.series), default=0)
        layers = [self._grid(low, high)]
        for index, serie in enumerate(self.series):
            colour = self.colors[index % len(self.colors)]
            points = [
                (self._x(position, count), self._y(value, low, high))
                for position, value in enumerate(serie["data"])
                if value is not None
            ]
            if not points:
                continue
            path = _path(points, self.smooth)
            if self.fill:
                area = (
                    f"{path} L {points[-1][0]:.1f},{self.height - self.padding[2]:.1f} "
                    f"L {points[0][0]:.1f},{self.height - self.padding[2]:.1f} Z"
                )
                layers.append(f'<path d="{area}" fill="{colour}" fill-opacity="0.14" stroke="none"/>')
            layers.append(
                f'<path d="{path}" fill="none" stroke="{colour}" stroke-width="2.2" '
                f'stroke-linecap="round" stroke-linejoin="round"/>'
            )
            for x, y in points:
                layers.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="white" stroke="{colour}" stroke-width="2"/>'
                )
        layers.append(self._x_labels(count))
        return self._svg("".join(layers))


def _path(points: list[tuple[float, float]], smooth: bool) -> str:
    if not points:
        return ""
    if not smooth or len(points) < 3:
        return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    path = [f"M {points[0][0]:.1f},{points[0][1]:.1f}"]
    for index in range(len(points) - 1):
        x0, y0 = points[index]
        x1, y1 = points[index + 1]
        cx = (x0 + x1) / 2
        path.append(f"C {cx:.1f},{y0:.1f} {cx:.1f},{y1:.1f} {x1:.1f},{y1:.1f}")
    return " ".join(path)


class AreaChart(LineChart):
    def __init__(self, series: Sequence[Any] | dict[str, Any] | None = None, **props: Any) -> None:
        props.setdefault("smooth", True)
        props.setdefault("fill", True)
        super().__init__(series, **props)


class BarChart(_ChartBase):
    def __init__(self, series: Sequence[Any] | dict[str, Any] | None = None, *, horizontal: bool = False,
                 radius: int = 4, **props: Any) -> None:
        self.horizontal = horizontal
        self.radius = radius
        super().__init__(series, **props)

    def _render_chart(self) -> str:
        low, high = self._bounds()
        count = max((len(serie["data"]) for serie in self.series), default=0)
        if count == 0:
            return self._svg("")
        layers = [self._grid(low, high)] if not self.horizontal else []
        plot_left = self.padding[3]
        plot_right = self.width - self.padding[1]
        slot = (plot_right - plot_left) / max(count, 1)
        groups = max(1, len(self.series))
        bar_width = max(3.0, (slot * 0.7) / groups)
        baseline = self._y(max(low, 0), low, high)
        for series_index, serie in enumerate(self.series):
            colour = self.colors[series_index % len(self.colors)]
            for position, value in enumerate(serie["data"]):
                if value is None:
                    continue
                centre = plot_left + slot * position + slot / 2
                offset = (series_index - (groups - 1) / 2) * bar_width
                x = centre + offset - bar_width / 2
                y = self._y(value, low, high)
                height = max(1.0, baseline - y)
                layers.append(
                    f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" height="{height:.1f}" '
                    f'rx="{self.radius}" fill="{colour}" fill-opacity="0.9"/>'
                )
                if self.show_values:
                    layers.append(
                        f'<text x="{x + bar_width / 2:.1f}" y="{y - 4:.1f}" text-anchor="middle" '
                        f'font-size="8" fill="currentColor" fill-opacity="0.6">{_fmt(value)}</text>'
                    )
        if self.labels:
            bottom = self.height - self.padding[2] + 14
            for position, label in enumerate(self.labels[:count]):
                centre = plot_left + slot * position + slot / 2
                layers.append(
                    f'<text x="{centre:.1f}" y="{bottom}" text-anchor="middle" font-size="9" '
                    f'fill="currentColor" fill-opacity="0.55">{escape(label)}</text>'
                )
        return self._svg("".join(layers))


ColumnChart = BarChart


class ScatterChart(_ChartBase):
    def _render_chart(self) -> str:
        low, high = self._bounds()
        count = max((len(serie["data"]) for serie in self.series), default=0)
        layers = [self._grid(low, high)]
        for index, serie in enumerate(self.series):
            colour = self.colors[index % len(self.colors)]
            for position, value in enumerate(serie["data"]):
                if value is None:
                    continue
                x = self._x(position, count)
                y = self._y(value, low, high)
                layers.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.4" fill="{colour}" fill-opacity="0.8"/>')
        layers.append(self._x_labels(count))
        return self._svg("".join(layers))


class PieChart(_ChartBase):
    def __init__(self, data: dict[str, float] | Sequence[Any] | None = None, *, donut: bool = False,
                 thickness: float = 0.55, **props: Any) -> None:
        items = list(data.items()) if isinstance(data, dict) else [_pair(item) for item in (data or [])]
        self.values = [(str(label), float(value)) for label, value in items]
        self.donut = donut
        self.thickness = thickness
        super().__init__(None, **props)
        self.height = 260

    def _render_chart(self) -> str:
        total = sum(value for _label, value in self.values) or 1.0
        cx, cy = 320, 130
        radius = 100
        inner = radius * (1 - self.thickness) if self.donut else 0
        start = -math.pi / 2
        slices = []
        for index, (label, value) in enumerate(self.values):
            angle = value / total * math.tau
            end = start + angle
            colour = self.colors[index % len(self.colors)]
            large = 1 if angle > math.pi else 0
            x0, y0 = cx + radius * math.cos(start), cy + radius * math.sin(start)
            x1, y1 = cx + radius * math.cos(end), cy + radius * math.sin(end)
            if inner > 0:
                xi0, yi0 = cx + inner * math.cos(end), cy + inner * math.sin(end)
                xi1, yi1 = cx + inner * math.cos(start), cy + inner * math.sin(start)
                path = (
                    f"M {x0:.1f},{y0:.1f} A {radius},{radius} 0 {large} 1 {x1:.1f},{y1:.1f} "
                    f"L {xi0:.1f},{yi0:.1f} A {inner},{inner} 0 {large} 0 {xi1:.1f},{yi1:.1f} Z"
                )
            else:
                path = f"M {cx},{cy} L {x0:.1f},{y0:.1f} A {radius},{radius} 0 {large} 1 {x1:.1f},{y1:.1f} Z"
            slices.append(f'<path d="{path}" fill="{colour}" stroke="white" stroke-width="1.5"/>')
            mid = start + angle / 2
            lx = cx + (radius * 0.68) * math.cos(mid)
            ly = cy + (radius * 0.68) * math.sin(mid)
            if angle > 0.28:
                slices.append(
                    f'<text x="{lx:.1f}" y="{ly + 3:.1f}" text-anchor="middle" font-size="10" '
                    f'font-weight="600" fill="white">{value / total * 100:.0f}%</text>'
                )
            start = end
        legend = "".join(
            f'<span class="inline-flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">'
            f'<span class="h-2 w-2 rounded-sm" style="background:{self.colors[index % len(self.colors)]}"></span>'
            f"{escape(label)} · {_fmt(value)}</span>"
            for index, (label, value) in enumerate(self.values)
        )
        body = "".join(slices)
        if self.donut:
            body += (
                f'<text x="{cx}" y="{cy - 2}" text-anchor="middle" font-size="22" font-weight="700" '
                f'fill="currentColor">{_fmt(total)}</text>'
                f'<text x="{cx}" y="{cy + 16}" text-anchor="middle" font-size="10" '
                f'fill="currentColor" fill-opacity="0.5">total</text>'
            )
        return (
            f'<svg viewBox="0 0 {self.width} {self.height}" class="h-auto w-full text-slate-800 '
            f'dark:text-slate-200">{body}</svg>'
            f'<div class="flex flex-wrap items-center gap-x-4 gap-y-1">{legend}</div>'
        )


def _pair(item: Any) -> tuple[Any, Any]:
    if isinstance(item, dict):
        return item.get("label", ""), item.get("value", 0)
    if isinstance(item, (tuple, list)):
        return item[0], item[1] if len(item) > 1 else 0
    return item, item


class DonutChart(PieChart):
    def __init__(self, data: dict[str, float] | Sequence[Any] | None = None, **props: Any) -> None:
        props.setdefault("donut", True)
        super().__init__(data, **props)


class Sparkline(Component):
    tag = "span"

    def __init__(self, data: Sequence[float] | None = None, *, color: str = "#4f46e5",
                 height: int = 32, width: int = 120, fill: bool = True, **props: Any) -> None:
        self.data = [float(value) for value in (data or [])]
        self.color = css_value(color)
        self.spark_height = height
        self.spark_width = width
        self.fill = fill
        props["base_class"] = tw("inline-block", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        if len(self.data) < 2:
            return ""
        low, high = min(self.data), max(self.data)
        span = high - low or 1
        step = self.spark_width / (len(self.data) - 1)
        points = [
            (index * step, self.spark_height - (value - low) / span * (self.spark_height - 4) - 2)
            for index, value in enumerate(self.data)
        ]
        line = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        area = f"{line} L {self.spark_width:.1f},{self.spark_height} L 0,{self.spark_height} Z"
        return (
            f'<svg viewBox="0 0 {self.spark_width} {self.spark_height}" width="{self.spark_width}" '
            f'height="{self.spark_height}" preserveAspectRatio="none">'
            + (f'<path d="{area}" fill="{self.color}" fill-opacity="0.12" stroke="none"/>' if self.fill else "")
            + f'<path d="{line}" fill="none" stroke="{self.color}" stroke-width="1.8" '
            'stroke-linecap="round" stroke-linejoin="round"/></svg>'
        )


class Gauge(Component):
    tag = "div"

    def __init__(self, value: float = 0, *, max_value: float = 100, label: Any = None,
                 color: str = "#4f46e5", size: int = 180, **props: Any) -> None:
        self.value = value
        self.max_value = max_value or 100
        self.gauge_label = label
        self.color = css_value(color)
        self.gauge_size = size
        props["base_class"] = tw("inline-flex flex-col items-center", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        percent = max(0.0, min(1.0, self.value / self.max_value))
        size = self.gauge_size
        radius = size * 0.4
        cx, cy = size / 2, size * 0.58
        circumference = math.pi * radius
        offset = circumference * (1 - percent)
        return (
            f'<svg width="{size}" height="{size * 0.68}" viewBox="0 0 {size} {size * 0.68}">'
            f'<path d="M {cx - radius},{cy} A {radius},{radius} 0 0 1 {cx + radius},{cy}" fill="none" '
            'stroke="currentColor" class="text-slate-200 dark:text-slate-800" stroke-width="12" stroke-linecap="round"/>'
            f'<path d="M {cx - radius},{cy} A {radius},{radius} 0 0 1 {cx + radius},{cy}" fill="none" '
            f'stroke="{self.color}" stroke-width="12" stroke-linecap="round" '
            f'stroke-dasharray="{circumference:.1f}" stroke-dashoffset="{offset:.1f}" '
            'class="transition-all duration-500"/>'
            f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="20" font-weight="700" '
            f'fill="currentColor">{self.value:g}</text></svg>'
            + (
                f'<span class="text-xs text-slate-500 dark:text-slate-400">{escape(self.gauge_label)}</span>'
                if self.gauge_label
                else ""
            )
        )


class Legend(Component):
    tag = "div"

    def __init__(self, items: Sequence[Any] | None = None, **props: Any) -> None:
        self.items = list(items or [])
        props["base_class"] = tw("flex flex-wrap items-center gap-x-4 gap-y-1", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return "".join(
            f'<span class="inline-flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">'
            f'<span class="h-2 w-2 rounded-full" style="background:{PALETTE[index % len(PALETTE)]}"></span>'
            f"{escape(_pair(item)[0])}</span>"
            for index, item in enumerate(self.items)
        )


class ChartCard(Component):
    tag = "div"

    def __init__(self, chart: Any, *, title: Any = None, subtitle: Any = None, **props: Any) -> None:
        self.chart = chart
        self.chart_title = title
        self.subtitle = subtitle
        props["base_class"] = tw(
            "flex flex-col gap-3 rounded-2xl border border-slate-200 bg-white p-4 shadow-sm "
            "dark:border-slate-800 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        head = ""
        if self.chart_title or self.subtitle:
            head = (
                '<div class="flex flex-col">'
                + (f'<h3 class="text-sm font-semibold text-slate-900 dark:text-white">{escape(self.chart_title)}</h3>'
                   if self.chart_title else "")
                + (f'<p class="text-xs text-slate-500 dark:text-slate-400">{escape(self.subtitle)}</p>'
                   if self.subtitle else "")
                + "</div>"
            )
        body = self.chart.render(ctx, path + "-c") if isinstance(self.chart, Component) else escape(self.chart)
        return head + body
