"""Tablas, listas y visualización de datos."""

from __future__ import annotations

import json
from typing import Any, Sequence

from ..base import Component, bind_many
from ..context import RenderContext
from ..html import escape
from ..icons import Icon
from ..style import tw
from ..theme import Color, Token

__all__ = [
    "Table", "DataTable", "ListGroup", "ListItem", "Tree", "TreeNode", "Timeline",
    "TimelineItem", "Stat", "StatGrid", "DescriptionList", "DescriptionItem",
    "JsonView", "LogView", "EmptyState", "KeyValueGrid",
]

ALIGN = {"left": "text-left", "center": "text-center", "right": "text-right"}


def _cell(ctx: RenderContext, value: Any, path: str) -> str:
    if isinstance(value, Component):
        return value.render(ctx, path)
    return escape(value)


def _parametros(handler: Any) -> int:
    """Cuántos argumentos posicionales obligatorios pide un handler."""
    import inspect

    try:
        firma = inspect.signature(handler)
    except (TypeError, ValueError):  # pragma: no cover - callables opacos
        return 0
    return len(
        [
            name
            for name, param in firma.parameters.items()
            if param.default is param.empty
            and param.kind in (param.POSITIONAL_ONLY, param.POSITIONAL_OR_KEYWORD)
        ]
    )


def _con_fila(handler: Any, row_index: int, row: list[Any]) -> Any:
    """Handler de fila: recibe la fila, o ``(indice, fila)``, o nada.

    Nunca recibe el evento del navegador: para eso están los handlers normales
    del componente, que sí lo reciben.
    """
    total = _parametros(handler)
    if total >= 2:
        return lambda *args: handler(row_index, row)
    if total == 1:
        return lambda *args: handler(row)
    return lambda *args: handler()


class Table(Component):
    """Tabla estática con estilos de cabecera, cebra y hover.

    Todo el aspecto se puede cambiar sin escribir CSS: colores de encabezado,
    cebra, hover, color por columna y fila seleccionada. También admite
    interacción por fila (clic, doble clic y menú contextual).

    ```python
    ui.Table(
        headers=["Nombre", "Correo"],
        rows=[["Ana", "ana@x.com"]],
        header_bg=ui.colors.slate_100,
        header_color=ui.colors.slate_700,
        striped=True,
        on_row_dblclick=lambda indice, fila: abrir(fila),
    )
    ```
    """

    tag = "div"

    def __init__(
        self,
        headers: Sequence[Any] | None = None,
        rows: Sequence[Sequence[Any]] | None = None,
        *,
        caption: str | None = None,
        striped: bool = False,
        zebra: Any = None,
        hover: bool = True,
        hover_bg: Any = None,
        compact: bool = False,
        bordered: bool = False,
        footer: Sequence[Any] | None = None,
        align: Sequence[str] | None = None,
        empty: Any = "Sin datos",
        header_bg: Any = None,
        header_color: Any = None,
        cell_colors: dict[int | str, Any] | None = None,
        column_bg: dict[int | str, Any] | None = None,
        selected: int | None = None,
        selected_bg: Any = None,
        on_row_click: Any = None,
        on_row_dblclick: Any = None,
        on_row_context: Any = None,
        context_menu: Any = None,
        context_width: str = "12rem",
        **props: Any,
    ) -> None:
        self.headers = list(headers or [])
        self.rows = [list(row) for row in (rows or [])]
        self.caption = caption
        self.striped = striped
        self.zebra = zebra
        self.hover = hover
        self.hover_bg = hover_bg
        self.compact = compact
        self.bordered = bordered
        self.footer = list(footer or [])
        self.align = list(align or [])
        self.empty = empty
        self.header_bg = header_bg
        self.header_color = header_color
        self.cell_colors = dict(cell_colors or {})
        self.column_bg = dict(column_bg or {})
        self.selected = selected
        self.selected_bg = selected_bg or "indigo-50"
        self.on_row_click = on_row_click
        self.on_row_dblclick = on_row_dblclick
        self.on_row_context = on_row_context
        self.context_menu = context_menu
        self.context_width = context_width
        self.row_events: dict[str, Any] = {}
        if on_row_click is not None:
            self.row_events["click"] = on_row_click
        if on_row_dblclick is not None:
            self.row_events["dblclick"] = on_row_dblclick
        if on_row_context is not None:
            self.row_events["contextmenu"] = on_row_context
        props["base_class"] = tw(
            "w-full overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm "
            "dark:border-slate-800 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(**props)

    # -- ayudas de estilo -----------------------------------------------
    def _clase(self, prefix: str, value: Any, extra: str = "") -> str:
        """``_clase("bg", colors.slate_100)`` → ``bg-slate-100``."""
        if value is None or value == "":
            return extra
        text = str(value)
        if isinstance(value, Color) or not (text.startswith(prefix) or text.startswith(f"{prefix}-")):
            text = f"{prefix}-{text}"
        return tw(text, extra)

    def content(self, ctx: RenderContext, path: str) -> str:
        pad = "px-3 py-1.5" if self.compact else "px-4 py-3"
        head_bg = self._clase("bg", self.header_bg)
        head = ""
        if self.headers:
            cells = []
            for index, header in enumerate(self.headers):
                align = ALIGN.get(self.align[index] if index < len(self.align) else "left", "")
                tone = self._clase("text", self.header_color, "text-xs font-semibold uppercase tracking-wide")
                if self.header_color is None:
                    tone = tw(tone, "text-slate-500 dark:text-slate-400")
                cells.append(
                    f'<th scope="col" class="{pad} {align} {tone}">'
                    f"{_cell(ctx, header, f'{path}-h{index}')}</th>"
                )
            head = (
                '<thead class="border-b border-slate-200 dark:border-slate-800 '
                f'dark:bg-slate-800/50 {head_bg}"><tr>{"".join(cells)}</tr></thead>'
            )

        hover = ""
        if self.hover:
            hover = self._clase(
                "hover:bg", self.hover_bg, "transition" if self.hover_bg is None else ""
            )
            if self.hover_bg is None:
                hover = tw(hover, "hover:bg-slate-50 dark:hover:bg-slate-800/50")
        border = "border-b border-slate-100 dark:border-slate-800" if self.bordered else ""

        interactiva = bool(self.row_events) or self.context_menu is not None
        paneles: list[str] = []
        body_rows = []
        for row_index, row in enumerate(self.rows):
            zebra = ""
            if self.striped and row_index % 2 == 1:
                zebra = self._clase("bg", self.zebra)
                if self.zebra is None:
                    zebra = tw(zebra, "bg-slate-50/60 dark:bg-slate-800/30")
            elegida = self.selected is not None and row_index == self.selected
            seleccion = self._clase("bg", self.selected_bg) if elegida else ""
            cells = []
            for column, value in enumerate(row):
                align = ALIGN.get(self.align[column] if column < len(self.align) else "left", "")
                color = self.cell_colors.get(column, self.cell_colors.get(str(column)))
                fondo = self.column_bg.get(column, self.column_bg.get(str(column)))
                tono = self._clase("text", color)
                if color is None:
                    tono = tw(tono, "text-sm text-slate-700 dark:text-slate-200")
                else:
                    tono = tw(tono, "text-sm")
                celda = self._clase("bg", fondo, align)
                cells.append(
                    f'<td class="{pad} {celda} {tono}">'
                    f"{_cell(ctx, value, f'{path}-r{row_index}-c{column}')}</td>"
                )
            extras = tw(zebra, hover, border, seleccion)
            if self.context_menu is not None:
                extras = tw(extras, "cursor-context-menu")
            elif interactiva:
                extras = tw(extras, "cursor-pointer")
            attrs_parts = [f'class="{extras}"'] if extras else []
            if interactiva:
                fila_uid = ctx.uid(f"{path}-fila{row_index}", None, None)
                for evento, handler in self.row_events.items():
                    ctx.bind(fila_uid, evento, _con_fila(handler, row_index, row))
                if self.row_events:
                    attrs_parts.insert(0, f'id="{escape(fila_uid)}"')
                    attrs_parts.append(f'data-iui-on="{",".join(sorted(self.row_events))}"')
                items = self._items_of(row_index, row)
                if items is not None:
                    panel_id = f"{fila_uid}-menu"
                    attrs_parts.append(f'data-iui-context="{escape(panel_id)}"')
                    from .shell import context_panel

                    paneles.append(
                        context_panel(
                            items,
                            ctx,
                            f"{path}-menu{row_index}",
                            panel_id=panel_id,
                            min_width=self.context_width,
                        )
                    )
            attrs = (" " + " ".join(attrs_parts)) if attrs_parts else ""
            body_rows.append(f"<tr{attrs}>{''.join(cells)}</tr>")

        if not body_rows:
            span = max(1, len(self.headers) or 1)
            body_rows.append(
                f'<tr><td colspan="{span}" class="px-4 py-10 text-center text-sm text-slate-500 '
                f'dark:text-slate-400">{escape(self.empty)}</td></tr>'
            )

        foot = ""
        if self.footer:
            cells = "".join(
                f'<td class="{pad} text-sm font-medium text-slate-700 dark:text-slate-200">'
                f"{_cell(ctx, value, f'{path}-f{index}')}</td>"
                for index, value in enumerate(self.footer)
            )
            foot = (
                '<tfoot class="border-t border-slate-200 bg-slate-50/80 dark:border-slate-800 '
                f'dark:bg-slate-800/50"><tr>{cells}</tr></tfoot>'
            )

        caption = (
            f'<caption class="caption-top px-4 pb-2 text-left text-xs text-slate-500">{escape(self.caption)}</caption>'
            if self.caption
            else ""
        )
        rows_html = "".join(body_rows)
        return (
            f'<table data-iui-table class="min-w-full border-collapse">{caption}{head}'
            f'<tbody class="divide-y divide-slate-100 dark:divide-slate-800">{rows_html}</tbody>'
            f"{foot}</table>" + "".join(paneles)
        )

    def _items_of(self, row_index: int, row: list[Any]) -> list[Any] | None:
        """Entradas del menú contextual de una fila (o ``None`` si no hay)."""
        menu = self.context_menu
        if menu is None:
            return None
        if not callable(menu):
            items = menu
        elif _parametros(menu) >= 2:
            items = menu(row_index, row)
        else:
            items = menu(row)
        return [item for item in (items or []) if item is not None]


def _row_value(row: Any, key: str) -> Any:
    """Valor de una celda admitiendo filas dict o secuencias."""
    if isinstance(row, dict):
        return row.get(key, "")
    if key.isdigit():
        index = int(key)
        return row[index] if 0 <= index < len(row) else ""
    return ""


class DataTable(Component):
    """Tabla con orden, búsqueda, selección y paginación controladas por Python."""

    tag = "div"

    def __init__(
        self,
        columns: Sequence[dict[str, Any]] | None = None,
        rows: Sequence[dict[str, Any] | Sequence[Any]] | None = None,
        *,
        sort: str | None = None,
        direction: str = "asc",
        page: int = 1,
        page_size: int = 10,
        selectable: bool = False,
        selected: Sequence[Any] | None = None,
        search: str = "",
        searchable: bool = False,
        search_placeholder: str = "Buscar…",
        empty: Any = "No hay resultados",
        on_sort: Any = None,
        on_page: Any = None,
        on_select: Any = None,
        on_search: Any = None,
        total: int | None = None,
        **props: Any,
    ) -> None:
        self.columns = list(columns or [])
        self.rows = list(rows or [])
        self.sort = sort
        self.direction = direction
        self.page = max(1, int(page))
        self.page_size = max(1, int(page_size))
        self.selectable = selectable
        self.selected = {str(value) for value in (selected or [])}
        self.search = search
        self.searchable = searchable
        self.search_placeholder = search_placeholder
        self.empty = empty
        self.total = total if total is not None else len(self.rows)
        if on_sort is not None:
            props["on_sort"] = on_sort
        if on_page is not None:
            props["on_page"] = on_page
        if on_select is not None:
            props["on_change"] = on_select
        if on_search is not None:
            props["on_input"] = on_search
        props["base_class"] = tw(
            "flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm "
            "dark:border-slate-800 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(**props)

    def _pages(self) -> int:
        return max(1, -(-self.total // self.page_size))

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        suffixes = [f"h{index}" for index in range(len(self.columns))]
        bind_many(ctx, uid, {"sort": self.handlers.get("sort")}, suffixes)
        bind_many(ctx, uid, {"page": self.handlers.get("page")},
                  [f"p{number}" for number in range(1, self._pages() + 1)])
        if self.selectable:
            bind_many(ctx, uid, {"change": self.handlers.get("change")},
                      [f"r{index}" for index in range(len(self.rows))])
        if self.searchable:
            bind_many(ctx, uid, {"input": self.handlers.get("input")}, ["search"])
        return super().render(ctx, path)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        parts: list[str] = []

        if self.searchable:
            parts.append(
                '<div class="relative">'
                f'<input type="search" id="{escape(uid)}-search" value="{escape(self.search)}" '
                f'placeholder="{escape(self.search_placeholder)}" data-iui-on="input" '
                'data-iui-debounce="200" class="h-9 w-full rounded-lg border border-slate-300 '
                'bg-white pl-9 pr-3 text-sm text-slate-800 placeholder:text-slate-400 '
                'focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/30 focus:outline-none '
                'dark:border-slate-700 dark:bg-slate-950 dark:text-slate-100"/>'
                f'<span class="pointer-events-none absolute inset-y-0 left-2.5 flex items-center text-slate-400">'
                f"{Icon('search', size=4).render(ctx, uid + '-si')}</span></div>"
            )

        head_cells = []
        if self.selectable:
            head_cells.append('<th class="w-10 px-3 py-2"></th>')
        for index, column in enumerate(self.columns):
            key = str(column.get("key", ""))
            label = column.get("label", key)
            align = ALIGN.get(column.get("align", "left"), "")
            sortable = bool(column.get("sortable"))
            arrow = ""
            if sortable:
                if self.sort == key:
                    arrow = Icon(
                        "chevron-up" if self.direction == "asc" else "chevron-down", size=3
                    ).render(ctx, f"{uid}-a{index}")
                else:
                    arrow = Icon("sort", size=3, class_="opacity-40").render(ctx, f"{uid}-a{index}")
            inner = (
                f'<span class="inline-flex items-center gap-1">{escape(label)}'
                + (arrow if sortable else "")
                + "</span>"
            )
            if sortable:
                head_cells.append(
                    f'<th class="{align} px-3 py-2"><button type="button" id="{escape(uid)}-h{index}" '
                    f'data-iui-emit="sort" data-iui-value="{escape(key)}" '
                    'class="inline-flex items-center gap-1 text-xs font-semibold uppercase '
                    f'tracking-wide text-slate-500 transition hover:text-slate-900 '
                    f'dark:text-slate-400 dark:hover:text-slate-100">{inner}</button></th>'
                )
            else:
                head_cells.append(
                    f'<th class="{align} px-3 py-2 text-xs font-semibold uppercase tracking-wide '
                    f'text-slate-500 dark:text-slate-400">{inner}</th>'
                )

        body_rows = []
        for row_index, row in enumerate(self.rows):
            key = str(row.get("id", row_index)) if isinstance(row, dict) else str(row_index)
            cells = []
            if self.selectable:
                cells.append(
                    '<td class="w-10 px-3 py-2">'
                    f'<input type="checkbox" id="{escape(uid)}-r{row_index}" '
                    f'data-iui-on="change" data-iui-index="{row_index}" '
                    f'value="{escape(key)}"{" checked" if key in self.selected else ""} '
                    'class="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500/40 '
                    'dark:border-slate-600 dark:bg-slate-800"/></td>'
                )
            for column in self.columns:
                column_key = str(column.get("key", ""))
                align = ALIGN.get(column.get("align", "left"), "")
                value = _row_value(row, column_key)
                renderer = column.get("render")
                if callable(renderer):
                    value = renderer(row)
                cells.append(
                    f'<td class="{align} px-3 py-2 text-sm text-slate-700 dark:text-slate-200">'
                    f"{_cell(ctx, value, f'{path}-r{row_index}-c{column_key}')}</td>"
                )
            body_rows.append(
                '<tr class="border-t border-slate-100 transition hover:bg-slate-50 '
                f'dark:border-slate-800 dark:hover:bg-slate-800/40">{"".join(cells)}</tr>'
            )

        if not body_rows:
            span = len(self.columns) + (1 if self.selectable else 0)
            body_rows.append(
                f'<tr><td colspan="{max(1, span)}" class="px-3 py-10 text-center text-sm text-slate-500 '
                f'dark:text-slate-400">{escape(self.empty)}</td></tr>'
            )

        parts.append(
            '<div class="overflow-x-auto"><table class="min-w-full border-collapse">'
            f'<thead class="bg-slate-50/70 dark:bg-slate-800/40"><tr>{"".join(head_cells)}</tr></thead>'
            f'<tbody>{"".join(body_rows)}</tbody></table></div>'
        )

        if self._pages() > 1:
            first = (self.page - 1) * self.page_size + 1
            last = min(self.total, self.page * self.page_size)
            buttons = []
            for number in range(1, self._pages() + 1):
                active = number == self.page
                buttons.append(
                    f'<button type="button" id="{escape(uid)}-p{number}" data-iui-emit="page" '
                    f'data-iui-value="{number}" data-iui-cast="int" '
                    'class="h-8 min-w-8 rounded-md px-2 text-sm font-medium transition '
                    + ("bg-indigo-600 text-white shadow-sm"
                       if active
                       else "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800")
                    + f'">{number}</button>'
                )
            parts.append(
                '<div class="flex flex-wrap items-center justify-between gap-2 px-1 text-xs text-slate-500 '
                f'dark:text-slate-400"><span>Mostrando {first}–{last} de {self.total}</span>'
                f'<div class="flex items-center gap-1">{"".join(buttons)}</div></div>'
            )

        return "".join(parts)


class ListGroup(Component):
    tag = "ul"

    def __init__(self, *children: Any, divided: bool = True, **props: Any) -> None:
        props["base_class"] = tw(
            "flex flex-col overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm "
            "dark:border-slate-800 dark:bg-slate-900",
            "divide-y divide-slate-100 dark:divide-slate-800" if divided else "",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class ListItem(Component):
    tag = "li"

    def __init__(
        self,
        *children: Any,
        title: Any = None,
        subtitle: Any = None,
        icon: str | None = None,
        meta: Any = None,
        active: bool = False,
        **props: Any,
    ) -> None:
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.meta = meta
        props["base_class"] = tw(
            "flex items-center gap-3 px-4 py-3 text-sm transition",
            "bg-indigo-50/70 dark:bg-indigo-500/10" if active else "hover:bg-slate-50 dark:hover:bg-slate-800/50",
            "cursor-pointer" if props.get("on_click") else "",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        lead = (
            f'<span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-slate-100 '
            f'text-slate-500 dark:bg-slate-800 dark:text-slate-300">'
            f"{Icon(self.icon, size=4).render(ctx, path + '-ic')}</span>"
            if self.icon
            else ""
        )
        body = render_children(self.children, ctx, path)
        if self.title or self.subtitle:
            body = (
                '<div class="flex min-w-0 flex-col">'
                f'<span class="truncate font-medium text-slate-800 dark:text-slate-100">{escape(self.title or "")}</span>'
                + (
                    f'<span class="truncate text-xs text-slate-500 dark:text-slate-400">{escape(self.subtitle)}</span>'
                    if self.subtitle
                    else ""
                )
                + f"</div>{body}"
            )
        tail = (
            f'<span class="ml-auto shrink-0 text-xs text-slate-400">{escape(self.meta)}</span>'
            if self.meta is not None
            else ""
        )
        return f"{lead}<div class=\"flex min-w-0 flex-1 flex-col\">{body}</div>{tail}"


class TreeNode(Component):
    tag = "div"

    def __init__(
        self,
        label: Any,
        *,
        icon: str | None = None,
        children: Sequence[Any] | None = None,
        expanded: bool = False,
        on_toggle: Any = None,
        on_click: Any = None,
        level: int = 0,
        **props: Any,
    ) -> None:
        self.label = label
        self.icon = icon
        self.nodes = list(children or [])
        self.expanded = expanded
        self.level = level
        if on_toggle is not None:
            props["on_toggle"] = on_toggle
        if on_click is not None:
            props["on_click"] = on_click
        props["base_class"] = "flex flex-col"
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        pad = 8 + self.level * 16
        chevron = ""
        if self.nodes:
            chevron = (
                f'<button type="button" id="{escape(uid)}-t" data-iui-emit="toggle" '
                'class="flex h-5 w-5 items-center justify-center rounded text-slate-400 transition '
                'hover:bg-slate-200 dark:hover:bg-slate-700">'
                + Icon("chevron-down" if self.expanded else "chevron-right", size=3).render(ctx, uid + "-ci")
                + "</button>"
            )
        ctx.bind(f"{uid}-t", "toggle", self.handlers.get("toggle"))
        icon = (
            f'<span class="text-slate-400">{Icon(self.icon, size=4).render(ctx, uid + "-ic")}</span>'
            if self.icon
            else ""
        )
        row = (
            f'<div class="flex items-center gap-1.5 rounded-md py-1 pr-2 text-sm text-slate-700 '
            f'transition hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800" '
            f'style="padding-left:{pad}px">{chevron}{icon}'
            f'<span class="truncate">{escape(self.label)}</span></div>'
        )
        body = ""
        if self.expanded and self.nodes:
            body = "".join(
                node.render(ctx, ctx.child(path, index)) for index, node in enumerate(self.nodes)
            )
        return row + (f'<div class="flex flex-col">{body}</div>' if body else "")


class Tree(Component):
    tag = "div"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(
            "flex flex-col rounded-xl border border-slate-200 bg-white p-2 shadow-sm "
            "dark:border-slate-800 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class TimelineItem(Component):
    tag = "li"

    def __init__(
        self,
        title: Any,
        *,
        description: Any = None,
        time: Any = None,
        icon: str | None = None,
        tone: str = "primary",
        last: bool = False,
        **props: Any,
    ) -> None:
        self.title = title
        self.description = description
        self.time = time
        self.icon = icon
        self.tone = tone
        self.last = last
        props["base_class"] = tw("relative flex gap-4 pb-6", "" if last else "border-l border-slate-200 dark:border-slate-700")
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        tones = {
            "primary": "bg-indigo-600 text-white",
            "success": "bg-emerald-600 text-white",
            "warning": "bg-amber-500 text-slate-950",
            "danger": "bg-rose-600 text-white",
            "neutral": "bg-slate-200 text-slate-600 dark:bg-slate-700 dark:text-slate-200",
        }
        icon = Icon(self.icon or "check", size=3).render(ctx, path + "-ic")
        return (
            f'<span class="absolute -left-3 flex h-6 w-6 items-center justify-center rounded-full '
            f'ring-4 ring-white dark:ring-slate-950 {tones.get(self.tone, tones["primary"])}">{icon}</span>'
            '<div class="ml-6 flex flex-col">'
            f'<span class="text-sm font-semibold text-slate-800 dark:text-slate-100">{escape(self.title)}</span>'
            + (
                f'<span class="mt-0.5 text-sm text-slate-600 dark:text-slate-300">{escape(self.description)}</span>'
                if self.description
                else ""
            )
            + (
                f'<span class="mt-1 text-xs text-slate-400">{escape(self.time)}</span>'
                if self.time
                else ""
            )
            + "</div>"
        )


class Timeline(Component):
    tag = "ol"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("ml-3 flex flex-col", props.get("base_class"))
        super().__init__(*children, **props)


class Stat(Component):
    tag = "div"

    def __init__(
        self,
        label: Any,
        value: Any,
        *,
        delta: Any = None,
        positive: bool = True,
        icon: str | None = None,
        hint: Any = None,
        **props: Any,
    ) -> None:
        self.label = label
        self.value = value
        self.delta = delta
        self.positive = positive
        self.icon = icon
        self.hint = hint
        props["base_class"] = tw(
            "flex flex-col gap-1 rounded-xl border border-slate-200 bg-white p-4 shadow-sm "
            "dark:border-slate-800 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        head = (
            '<div class="flex items-center justify-between">'
            f'<span class="text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">'
            f"{escape(self.label)}</span>"
            + (
                f'<span class="text-slate-300 dark:text-slate-600">'
                f"{Icon(self.icon, size=4).render(ctx, path + '-ic')}</span>"
                if self.icon
                else ""
            )
            + "</div>"
        )
        delta = ""
        if self.delta is not None:
            tone = "text-emerald-600 dark:text-emerald-400" if self.positive else "text-rose-600 dark:text-rose-400"
            delta = (
                f'<span class="inline-flex items-center gap-0.5 text-xs font-medium {tone}">'
                + Icon("arrow-up" if self.positive else "arrow-down", size=3).render(ctx, path + "-d")
                + f"{escape(self.delta)}</span>"
            )
        return (
            f"{head}<div class=\"flex items-baseline gap-2\">"
            f'<span class="text-2xl font-semibold tracking-tight text-slate-900 dark:text-white">'
            f"{escape(self.value)}</span>{delta}</div>"
            + (
                f'<span class="text-xs text-slate-400">{escape(self.hint)}</span>'
                if self.hint
                else ""
            )
        )


class StatGrid(Component):
    tag = "div"

    def __init__(self, *children: Any, columns: int = 4, **props: Any) -> None:
        props["base_class"] = tw(
            "grid gap-4",
            f"grid-cols-1 sm:grid-cols-2 lg:grid-cols-{columns}",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class DescriptionItem(Component):
    tag = "div"

    def __init__(self, term: Any, definition: Any, **props: Any) -> None:
        self.term = term
        self.definition = definition
        props["base_class"] = tw(
            "flex flex-col gap-0.5 border-b border-slate-100 py-2 last:border-0 "
            "sm:grid sm:grid-cols-3 sm:gap-4 dark:border-slate-800",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return (
            f'<dt class="text-sm text-slate-500 dark:text-slate-400">{escape(self.term)}</dt>'
            f'<dd class="text-sm font-medium text-slate-800 sm:col-span-2 dark:text-slate-100">'
            f"{_cell(ctx, self.definition, path + '-d')}</dd>"
        )


class DescriptionList(Component):
    tag = "dl"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("flex flex-col", props.get("base_class"))
        super().__init__(*children, **props)


class KeyValueGrid(Component):
    tag = "div"

    def __init__(self, items: dict[str, Any] | Sequence[tuple[str, Any]] | None = None, *, columns: int = 2, **props: Any) -> None:
        self.items = list(items.items()) if isinstance(items, dict) else list(items or [])
        props["base_class"] = tw("grid gap-x-6 gap-y-3", f"grid-cols-1 sm:grid-cols-{columns}",
                                 props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return "".join(
            '<div class="flex flex-col gap-0.5">'
            f'<span class="text-xs uppercase tracking-wide text-slate-400">{escape(key)}</span>'
            f'<span class="text-sm font-medium text-slate-800 dark:text-slate-100">'
            f"{_cell(ctx, value, f'{path}-{index}')}</span></div>"
            for index, (key, value) in enumerate(self.items)
        )


TOKEN = (
    (r'"(?:\\.|[^"\\])*"(?=\s*:)', "text-sky-300"),
    (r'"(?:\\.|[^"\\])*"', "text-emerald-300"),
    (r"\b(true|false|null)\b", "text-rose-300"),
    (r"-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b", "text-amber-300"),
)


class JsonView(Component):
    tag = "div"

    def __init__(self, data: Any = None, *, max_h: str = "96", **props: Any) -> None:
        self.data = data
        self.max_h = max_h
        props["base_class"] = tw(
            "overflow-hidden rounded-xl border border-slate-800 bg-slate-950",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:

        try:
            text = json.dumps(self.data, indent=2, ensure_ascii=False, default=str)
        except (TypeError, ValueError):
            text = str(self.data)
        escaped = escape(text)
        highlight = escaped
        import re as _re

        for pattern, colour in TOKEN:
            highlight = _re.sub(
                pattern,
                lambda match, colour=colour: f'<span class="{colour}">{match.group(0)}</span>',
                highlight,
            )
        return (
            f'<pre class="max-h-{self.max_h} overflow-auto p-4 text-[12.5px] leading-relaxed text-slate-300">'
            f'<code class="font-mono">{highlight}</code></pre>'
        )


class LogView(Component):
    tag = "div"

    def __init__(self, lines: Sequence[Any] | None = None, *, max_h: str = "80", title: Any = None, **props: Any) -> None:
        self.lines = list(lines or [])
        self.max_h = max_h
        self.title = title
        props["base_class"] = tw(
            "overflow-hidden rounded-xl border border-slate-800 bg-slate-950 font-mono",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        tones = {
            "info": "text-sky-300",
            "ok": "text-emerald-300",
            "warn": "text-amber-300",
            "error": "text-rose-300",
            "debug": "text-slate-500",
        }
        rows = []
        for line in self.lines:
            if isinstance(line, dict):
                level = str(line.get("level", "info"))
                text = f"{line.get('time', '')} {line.get('message', '')}".strip()
            else:
                level, text = "info", str(line)
            rows.append(
                f'<div class="whitespace-pre-wrap px-3 py-0.5 {tones.get(level, tones["info"])}">{escape(text)}</div>'
            )
        head = (
            '<div class="flex items-center gap-2 border-b border-slate-800 bg-slate-900/60 px-3 py-2 '
            f'text-[11px] uppercase tracking-wide text-slate-400">{escape(self.title)}</div>'
            if self.title
            else ""
        )
        body = "".join(rows)
        if not body:
            body = '<div class="px-3 text-slate-600">sin registros</div>'
        return (
            f'{head}<div class="max-h-{self.max_h} overflow-auto py-2 text-[12px] leading-relaxed">'
            f"{body}</div>"
        )


class EmptyState(Component):
    tag = "div"

    def __init__(
        self,
        *children: Any,
        icon: str = "inbox",
        title: Any = "Nada por aquí",
        description: Any = None,
        **props: Any,
    ) -> None:
        self.icon = icon
        self.title = title
        self.description = description
        props["base_class"] = tw(
            "flex flex-col items-center justify-center gap-2 rounded-2xl border border-dashed "
            "border-slate-300 bg-slate-50/60 px-6 py-12 text-center dark:border-slate-700 dark:bg-slate-900/40",
            props.get("base_class"),
        )
        super().__init__(*children, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from ..base import render_children

        return (
            f'<span class="flex h-12 w-12 items-center justify-center rounded-full bg-slate-100 '
            f'text-slate-400 dark:bg-slate-800 dark:text-slate-500">'
            f"{Icon(self.icon, size=6).render(ctx, path + '-ic')}</span>"
            f'<p class="mt-2 text-sm font-semibold text-slate-800 dark:text-slate-100">{escape(self.title)}</p>'
            + (
                f'<p class="max-w-sm text-sm text-slate-500 dark:text-slate-400">{escape(self.description)}</p>'
                if self.description
                else ""
            )
            + render_children(self.children, ctx, path)
        )
