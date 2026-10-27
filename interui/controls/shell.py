"""Barra de menús, menús contextuales y armazón de aplicación.

Piezas de «app moderna» que completan la ventana:

* :class:`AppShell` — esqueleto: barra de título, cabecera, barra lateral,
  contenido y barra de estado, con el scroll en el sitio correcto.
* :class:`MenuBar` — barra de menús clásica (Archivo, Editar, Ver…) con
  desplegables que se abren con clic o teclado.
* :class:`ContextMenu` — menú al pulsar con el botón derecho sobre cualquier
  zona de la interfaz.

Todos los elementos ejecutan handlers de Python, como el resto de controles.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

from ..base import Component, render_children
from ..context import RenderContext
from ..html import escape
from ..icons import Icon
from ..style import tw
from .layout import MenuItem

__all__ = [
    "AppShell", "CommandBar", "ContextItem", "ContextMenu", "MenuBar", "MenuButton",
    "NotificationButton",
]

_SEPARATOR = '<div role="separator" class="my-1 h-px bg-slate-100 dark:bg-slate-800"></div>'


def _spec(item: Any) -> tuple[Any, Any, Any, Any, Any]:
    """Normaliza un ítem de menú: (etiqueta, icono, handler, atajo, peligro)."""
    if isinstance(item, dict):
        return (
            item.get("label", ""),
            item.get("icon"),
            item.get("on_click") or item.get("action"),
            item.get("shortcut"),
            bool(item.get("danger", False)),
        )
    if isinstance(item, (tuple, list)):
        label = item[0]
        icon = item[1] if len(item) > 1 else None
        handler = item[2] if len(item) > 2 else None
        shortcut = item[3] if len(item) > 3 else None
        danger = bool(item[4]) if len(item) > 4 else False
        return label, icon, handler, shortcut, danger
    if isinstance(item, Component):
        return None, None, None, None, None
    return item, None, None, None, False


def _is_separator(item: Any) -> bool:
    return isinstance(item, str) and item.strip() in ("-", "--", "---")


def _item_nodes(items: Iterable[Any]) -> list[Any]:
    """Convierte especificaciones (str, dict, tupla, Component) en componentes."""
    nodes: list[Any] = []
    for item in items:
        if isinstance(item, Component):
            nodes.append(item)
        elif _is_separator(item):
            nodes.append(None)
        else:
            label, icon, handler, shortcut, danger = _spec(item)
            nodes.append(
                ContextItem(label, icon=icon, shortcut=shortcut, danger=danger, on_click=handler)
            )
    return nodes


def _render_items(items: Iterable[Any], ctx: RenderContext, path: str) -> str:
    html: list[str] = []
    for index, node in enumerate(_item_nodes(items)):
        html.append(_SEPARATOR if node is None else node.render(ctx, f"{path}-i{index}"))
    return "".join(html)


class ContextItem(MenuItem):
    """Elemento de un menú contextual (misma API que :class:`MenuItem`).

    ```python
    ui.ContextItem("Abrir", icon="folder", on_click=abrir)
    ```
    """


class MenuButton(Component):
    """Botón que despliega un menú (para usar fuera de la barra de menús).

    ```python
    ui.MenuButton(
        "Acciones",
        icon="settings",
        items=[
            ui.ContextItem("Editar", icon="edit", on_click=editar),
            ("Eliminar", "trash", borrar, "Supr", True),
        ],
    )
    ```
    """

    tag = "div"

    def __init__(
        self,
        label: Any = "Menú",
        *,
        items: Sequence[Any] | None = None,
        icon: str | None = None,
        variant: str = "ghost",
        size: str = "sm",
        align: str = "left",
        **props: Any,
    ) -> None:
        self.label = label
        self.items = list(items or [])
        self.icon = icon
        self.variant = variant
        self.size = size
        self.align = align
        props["base_class"] = tw("relative inline-block", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from .buttons import Button

        uid = ctx.uid(path, self.key, self.explicit_id)
        panel_id = f"{uid}-menu"
        trigger = Button(
            self.label,
            id=f"{uid}-trigger",
            variant=self.variant,
            size=self.size,
            icon=self.icon,
            icon_right="chevron-down",
            data={"iui-menu": panel_id},
        )
        panel = (
            f'<div id="{escape(panel_id)}" data-iui-menu-panel role="menu" '
            'class="absolute top-full z-[55] mt-1 hidden min-w-52 flex-col overflow-hidden '
            'rounded-xl border border-slate-200 bg-white py-1 shadow-xl dark:border-slate-700 '
            f'dark:bg-slate-900 {"left-0" if self.align == "left" else "right-0"}">'
            f'{_render_items(self.items, ctx, f"{path}-p")}</div>'
        )
        return trigger.render(ctx, f"{path}-t") + panel


class MenuBar(Component):
    """Barra de menús de la ventana: ``Archivo``, ``Editar``, ``Ver``…

    ```python
    ui.MenuBar(
        {
            "Archivo": [
                ui.ContextItem("Nuevo", icon="plus", shortcut="Ctrl+N", on_click=nuevo),
                ui.ContextItem("Abrir…", icon="folder", on_click=abrir),
                "-",
                ui.ContextItem("Salir", icon="power", on_click=salir, danger=True),
            ],
            "Ver": [ui.ContextItem("Tema oscuro", icon="moon", on_click=tema)],
        },
        brand="Mi app",
    )
    ```
    """

    tag = "div"

    def __init__(
        self,
        menus: dict[str, Sequence[Any]] | Sequence[Any] | None = None,
        *,
        brand: Any = None,
        logo: str | None = "layers",
        actions: Any = None,
        sticky: bool = True,
        **props: Any,
    ) -> None:
        self.menus = list(menus.items()) if isinstance(menus, dict) else list(menus or [])
        self.brand = brand
        self.logo = logo
        self.actions = actions
        props["role"] = "menubar"
        props["base_class"] = tw(
            "flex h-10 w-full items-center gap-1 border-b border-slate-200 bg-white px-2 "
            "dark:border-slate-800 dark:bg-slate-950",
            "sticky top-0 z-40" if sticky else "",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        parts: list[str] = []
        if self.brand is not None:
            parts.append(
                '<div class="flex items-center gap-2 pr-2 text-sm font-semibold text-slate-900 '
                'dark:text-white">'
                + (
                    f'<span class="flex h-6 w-6 items-center justify-center rounded-md bg-indigo-600 '
                    f'text-white">{Icon(self.logo, size=3).render(ctx, f"{uid}-logo")}</span>'
                    if self.logo
                    else ""
                )
                + f"<span class=\"truncate\">{escape(self.brand)}</span></div>"
            )

        for index, entry in enumerate(self.menus):
            if isinstance(entry, (tuple, list)):
                label, items = entry[0], entry[1]
            else:  # pragma: no cover - dict key/value ya normalizado
                label, items = str(entry), []
            panel_id = f"{uid}-m{index}"
            items_html = _render_items(items, ctx, f"{path}-m{index}")
            parts.append(
                f'<div class="relative">'
                f'<button type="button" id="{escape(panel_id)}-trigger" data-iui-menu="{escape(panel_id)}" '
                'role="menuitem" aria-haspopup="true" aria-expanded="false" '
                'class="rounded-md px-2.5 py-1 text-sm text-slate-700 transition hover:bg-slate-100 '
                'aria-expanded:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-800 '
                f'dark:aria-expanded:bg-slate-800">{escape(label)}</button>'
                f'<div id="{escape(panel_id)}" data-iui-menu-panel role="menu" '
                'class="absolute left-0 top-full z-[55] mt-1 hidden min-w-56 flex-col overflow-hidden '
                'rounded-xl border border-slate-200 bg-white py-1 shadow-xl dark:border-slate-700 '
                f'dark:bg-slate-900">{items_html}</div></div>'
            )

        tail = ""
        if self.actions is not None:
            if isinstance(self.actions, Component):
                tail = self.actions.render(ctx, f"{path}-actions")
            else:
                tail = render_children(list(self.actions), ctx, f"{path}-actions")
        spacer = '<div class="flex-1"></div>' if tail else ""
        return "".join(parts) + spacer + tail


class ContextMenu(Component):
    """Envuelve contenido y abre un menú con el botón derecho.

    ```python
    ui.ContextMenu(
        ui.ContextItem("Abrir", icon="folder", on_click=abrir),
        ui.ContextItem("Renombrar", icon="edit", on_click=renombrar),
        "-",
        ui.ContextItem("Eliminar", icon="trash", danger=True, on_click=borrar),
    )(ui.table(headers=["Nombre"], rows=[["a"]]))
    ```
    """

    tag = "div"

    def __init__(
        self,
        *items: Any,
        min_width: str = "12rem",
        hint: Any = None,
        **props: Any,
    ) -> None:
        self.items = list(items)
        self.min_width = min_width
        self.hint = hint
        props["base_class"] = tw("relative", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        panel_id = f"{uid}-ctx"
        rows = _render_items(self.items, ctx, f"{path}-c")
        panel = (
            f'<div id="{escape(panel_id)}" data-iui-context-panel role="menu" '
            f'style="min-width:{escape(self.min_width)}" '
            'class="fixed z-[70] hidden flex-col overflow-hidden rounded-xl border border-slate-200 '
            'bg-white py-1 shadow-2xl dark:border-slate-700 dark:bg-slate-900">'
            f"{rows}</div>"
        )
        body = render_children(self.children, ctx, path)
        hint = (
            f'<p class="mt-1 text-[11px] text-slate-400">{escape(self.hint)}</p>' if self.hint else ""
        )
        return f'<div data-iui-context="{escape(panel_id)}">{body}{hint}</div>{panel}'


class AppShell(Component):
    """Armazón de una aplicación de escritorio.

    Coloca en su sitio la barra de título, la barra de menús o cabecera, la barra
    lateral, el contenido con scroll y la barra de estado:

    ```python
    ui.AppShell(
        title_bar=ui.TitleBar("Mi app", icon="layers"),
        header=ui.MenuBar({"Archivo": [...]}, brand="Mi app"),
        sidebar=ui.Sidebar(ui.SidebarItem("Panel", icon="grid"), title="Navegación"),
        status=ui.StatusBar(ui.Text("Listo")),
        ui.Container(class_="py-6")(ui.text("Contenido")),
    )
    ```
    """

    tag = "div"

    def __init__(
        self,
        *content: Any,
        title_bar: Any = None,
        header: Any = None,
        sidebar: Any = None,
        status: Any = None,
        footer: Any = None,
        sidebar_width: str = "w-64",
        **props: Any,
    ) -> None:
        self.title_bar = title_bar
        self.header = header
        self.sidebar = sidebar
        self.status = status
        self.footer = footer
        self.sidebar_width = sidebar_width
        props["base_class"] = tw(
            "flex h-screen w-full flex-col overflow-hidden bg-slate-50 text-slate-900 "
            "dark:bg-slate-950 dark:text-slate-100",
            props.get("base_class"),
        )
        super().__init__(*content, **props)

    def content(self, ctx: RenderContext, path: str) -> str:
        parts: list[str] = []
        for index, slot in enumerate((self.title_bar, self.header)):
            if slot is None:
                continue
            if isinstance(slot, Component):
                parts.append(slot.render(ctx, f"{path}-h{index}"))
            else:
                parts.append(render_children([slot], ctx, f"{path}-h{index}"))

        inner = render_children(self.children, ctx, f"{path}-main")
        if self.sidebar is not None:
            side = (
                self.sidebar.render(ctx, f"{path}-side")
                if isinstance(self.sidebar, Component)
                else render_children([self.sidebar], ctx, f"{path}-side")
            )
            parts.append(
                f'<div class="flex min-h-0 flex-1 overflow-hidden">{side}'
                f'<main class="min-w-0 flex-1 overflow-y-auto">{inner}</main></div>'
            )
        else:
            parts.append(f'<main class="min-w-0 flex-1 overflow-y-auto">{inner}</main>')

        if self.footer is not None:
            parts.append(
                self.footer.render(ctx, f"{path}-footer")
                if isinstance(self.footer, Component)
                else render_children([self.footer], ctx, f"{path}-footer")
            )
        if self.status is not None:
            parts.append(
                self.status.render(ctx, f"{path}-status")
                if isinstance(self.status, Component)
                else render_children([self.status], ctx, f"{path}-status")
            )
        return "".join(parts)


class CommandBar(Component):
    """Barra de comandos: buscador + acciones, al estilo de apps modernas."""

    tag = "div"

    def __init__(
        self,
        *actions: Any,
        search: str = "",
        search_placeholder: str = "Buscar…",
        on_search: Any = None,
        **props: Any,
    ) -> None:
        self.actions = list(actions)
        self.search = search
        self.search_placeholder = search_placeholder
        self.on_search = on_search
        props["base_class"] = tw(
            "flex flex-wrap items-center gap-2 border-b border-slate-200 bg-white/80 px-3 py-2 "
            "backdrop-blur dark:border-slate-800 dark:bg-slate-950/80",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from .inputs import Input

        uid = ctx.uid(path, self.key, self.explicit_id)
        field = Input(
            self.search,
            id=f"{uid}-search",
            icon="search",
            placeholder=self.search_placeholder,
            live=True,
            on_input=self.on_search,
            class_="max-w-xs",
        )
        return field.render(ctx, f"{path}-s") + render_children(self.actions, ctx, f"{path}-a")


class NotificationButton(Component):
    """Campana con contador y panel de notificaciones."""

    tag = "div"

    def __init__(self, count: int = 0, *, items: Sequence[Any] | None = None, **props: Any) -> None:
        self.count = count
        self.items = list(items or [])
        props["base_class"] = tw("relative", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        from .buttons import IconButton

        uid = ctx.uid(path, self.key, self.explicit_id)
        panel_id = f"{uid}-panel"
        trigger = IconButton(
            "bell", id=f"{uid}-t", label="Notificaciones", data={"iui-toggle": panel_id}
        )
        badge = ""
        if self.count:
            badge = (
                f'<span class="pointer-events-none absolute -right-0.5 -top-0.5 flex h-4 min-w-4 '
                f'items-center justify-center rounded-full bg-rose-500 px-1 text-[10px] font-semibold '
                f'text-white">{escape(self.count)}</span>'
            )
        rows = "".join(
            item.render(ctx, f"{path}-n{index}") if isinstance(item, Component) else escape(item)
            for index, item in enumerate(self.items)
        )
        empty = '<p class="px-3 py-4 text-sm text-slate-400">Sin notificaciones</p>'
        panel = (
            f'<div id="{escape(panel_id)}" class="absolute right-0 top-full z-[55] mt-1 hidden w-72 '
            'flex-col overflow-hidden rounded-xl border border-slate-200 bg-white py-1 shadow-xl '
            f'dark:border-slate-700 dark:bg-slate-900">{rows or empty}</div>'
        )
        return (
            f'<span class="relative">{trigger.render(ctx, f"{path}-tw")}{badge}</span>{panel}'
        )

