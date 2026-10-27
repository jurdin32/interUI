"""Conjunto de iconos vectoriales incluidos (sin dependencias externas).

Los trazos son geometría propia pensada para 24x24 con ``stroke-width`` 1.8, de
modo que heredan color y grosor del texto.
"""

from __future__ import annotations

from typing import Any, Callable, Sequence

from .base import Component, bind_many
from .html import escape
from .style import tw

__all__ = ["Icon", "ICONS", "ICON_NAMES", "IconGrid"]

ICONS: dict[str, str] = {
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18"/><path d="M6 6l12 12"/>',
    "plus": '<path d="M12 5v14"/><path d="M5 12h14"/>',
    "minus": '<path d="M5 12h14"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
    "menu": '<path d="M4 6h16"/><path d="M4 12h16"/><path d="M4 18h16"/>',
    "more-h": '<circle cx="5.5" cy="12" r="1.4" fill="currentColor" stroke="none"/>'
              '<circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/>'
              '<circle cx="18.5" cy="12" r="1.4" fill="currentColor" stroke="none"/>',
    "more-v": '<circle cx="12" cy="5.5" r="1.4" fill="currentColor" stroke="none"/>'
              '<circle cx="12" cy="12" r="1.4" fill="currentColor" stroke="none"/>'
              '<circle cx="12" cy="18.5" r="1.4" fill="currentColor" stroke="none"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-up": '<path d="m6 15 6-6 6 6"/>',
    "chevron-left": '<path d="m15 6-6 6 6 6"/>',
    "chevron-right": '<path d="m9 6 6 6-6 6"/>',
    "arrow-left": '<path d="M20 12H4"/><path d="m10 6-6 6 6 6"/>',
    "arrow-right": '<path d="M4 12h16"/><path d="m14 6 6 6-6 6"/>',
    "arrow-up": '<path d="M12 20V4"/><path d="m6 10 6-6 6 6"/>',
    "arrow-down": '<path d="M12 4v16"/><path d="m6 14 6 6 6-6"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6 8-6s8 2 8 6"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.3 2.9-5.5 6.5-5.5s6.5 2.2 6.5 5.5"/>'
             '<path d="M17 5.2a3.5 3.5 0 0 1 0 6.6"/><path d="M18.5 14.6c2 .7 3 2.3 3 4.4"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M12 3v2.5M12 18.5V21M3 12h2.5M18.5 12H21'
                'M5.6 5.6l1.8 1.8M16.6 16.6l1.8 1.8M18.4 5.6l-1.8 1.8M7.4 16.6l-1.8 1.8"/>',
    "sliders": '<path d="M4 7h6M14 7h6M4 17h10M18 17h2"/>'
               '<circle cx="12" cy="7" r="2"/><circle cx="16" cy="17" r="2"/>',
    "home": '<path d="M3 11.5 12 4l9 7.5"/><path d="M6 10.5V20h12v-9.5"/>',
    "folder": '<path d="M3 7.5A1.5 1.5 0 0 1 4.5 6H9l2 2.5h8.5A1.5 1.5 0 0 1 21 10v8.5A1.5 1.5 0 0 1 '
              '19.5 20h-15A1.5 1.5 0 0 1 3 18.5z"/>',
    "file": '<path d="M6 3.5A1.5 1.5 0 0 1 7.5 2H14l4 4v14.5A1.5 1.5 0 0 1 16.5 22h-9A1.5 1.5 0 0 1 '
            '6 20.5z"/><path d="M14 2v4.5h4"/>',
    "trash": '<path d="M4 7h16"/><path d="M9.5 7V4.5h5V7"/><path d="M6.5 7 7.5 20.5h9L17.5 7"/>',
    "edit": '<path d="M4 20h4L20 8l-4-4L4 16z"/><path d="m14.5 5.5 4 4"/>',
    "copy": '<rect x="9" y="9" width="11" height="11" rx="2"/>'
            '<path d="M15 6.5V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h1.5"/>',
    "download": '<path d="M12 4v10"/><path d="m7.5 9.5 4.5 4.5 4.5-4.5"/><path d="M4 19.5h16"/>',
    "upload": '<path d="M12 15V5"/><path d="M7.5 9.5 12 5l4.5 4.5"/><path d="M4 19.5h16"/>',
    "star": '<path d="m12 3.5 2.6 5.6 6 .8-4.4 4.2 1.1 6-5.3-2.9-5.3 2.9 1.1-6L3.4 9.9l6-.8z"/>',
    "heart": '<path d="M12 20s-7.5-4.6-7.5-9.3A4.2 4.2 0 0 1 12 8a4.2 4.2 0 0 1 7.5 2.7'
             'C19.5 15.4 12 20 12 20z"/>',
    "info": '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.5"/>'
            '<circle cx="12" cy="7.8" r=".95" fill="currentColor" stroke="none"/>',
    "alert": '<path d="M12 3.5 21 20H3z"/><path d="M12 9.5v4.5"/>'
             '<circle cx="12" cy="17" r=".95" fill="currentColor" stroke="none"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8 12.5 2.8 2.8L16 9.5"/>',
    "x-circle": '<circle cx="12" cy="12" r="9"/><path d="m9 9 6 6M15 9l-6 6"/>',
    "bell": '<path d="M6.5 10a5.5 5.5 0 0 1 11 0c0 4 1.5 5.5 1.5 5.5H5s1.5-1.5 1.5-5.5z"/>'
            '<path d="M10 19a2 2 0 0 0 4 0"/>',
    "calendar": '<rect x="3.5" y="5" width="17" height="16" rx="2"/><path d="M3.5 10h17"/>'
                '<path d="M8 3v4M16 3v4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5V12l3 2"/>',
    "mail": '<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="m3.5 7 8.5 6 8.5-6"/>',
    "lock": '<rect x="4.5" y="10" width="15" height="10.5" rx="2"/>'
            '<path d="M8 10V7.5a4 4 0 0 1 8 0V10"/>',
    "unlock": '<rect x="4.5" y="10" width="15" height="10.5" rx="2"/>'
              '<path d="M8 10V7.5a4 4 0 0 1 7.5-2"/>',
    "eye": '<path d="M2.5 12S6 6.5 12 6.5 21.5 12 21.5 12 18 17.5 12 17.5 2.5 12 2.5 12z"/>'
           '<circle cx="12" cy="12" r="3"/>',
    "eye-off": '<path d="M4 4l16 16"/><path d="M9.5 5.4A10 10 0 0 1 12 5c6 0 9.5 7 9.5 7a17 17 0 0 1-3.2 4"/>'
               '<path d="M6.2 7.6A16 16 0 0 0 2.5 12S6 19 12 19a9.5 9.5 0 0 0 3.7-.7"/>'
               '<path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/>',
    "filter": '<path d="M3.5 5.5h17l-6.5 7.5V20l-4-2v-5z"/>',
    "grid": '<rect x="3.5" y="3.5" width="7" height="7" rx="1.5"/>'
            '<rect x="13.5" y="3.5" width="7" height="7" rx="1.5"/>'
            '<rect x="3.5" y="13.5" width="7" height="7" rx="1.5"/>'
            '<rect x="13.5" y="13.5" width="7" height="7" rx="1.5"/>',
    "columns": '<rect x="3.5" y="4" width="17" height="16" rx="2"/><path d="M9.5 4v16M14.5 4v16"/>',
    "list": '<path d="M8 6.5h12M8 12h12M8 17.5h12"/>'
            '<circle cx="4" cy="6.5" r="1" fill="currentColor" stroke="none"/>'
            '<circle cx="4" cy="12" r="1" fill="currentColor" stroke="none"/>'
            '<circle cx="4" cy="17.5" r="1" fill="currentColor" stroke="none"/>',
    "play": '<path d="M8 4.5 19 12 8 19.5z"/>',
    "pause": '<path d="M9 5v14M15 5v14"/>',
    "refresh": '<path d="M20 12a8 8 0 1 1-2.6-5.9"/><path d="M20 4.5V10h-5.5"/>',
    "external": '<path d="M14 4h6v6"/><path d="M20 4 11 13"/>'
                '<path d="M18 14v5.5A1.5 1.5 0 0 1 16.5 21h-11A1.5 1.5 0 0 1 4 19.5v-11A1.5 1.5 0 0 1 '
                '5.5 7H11"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2'
           'M5.2 5.2l1.6 1.6M17.2 17.2l1.6 1.6M18.8 5.2l-1.6 1.6M6.8 17.2l-1.6 1.6"/>',
    "moon": '<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4 8.5 8.5 0 1 0 20 14.5z"/>',
    "image": '<rect x="3.5" y="4.5" width="17" height="15" rx="2"/><circle cx="9" cy="10" r="1.6"/>'
             '<path d="m4.5 17.5 4.8-4.8 3.7 3.7 2.5-2.5 4 4"/>',
    "camera": '<path d="M3 8.5A1.5 1.5 0 0 1 4.5 7h2L8 4.5h8L17.5 7h2A1.5 1.5 0 0 1 21 8.5v10'
              'A1.5 1.5 0 0 1 19.5 20h-15A1.5 1.5 0 0 1 3 18.5z"/><circle cx="12" cy="13" r="3.5"/>',
    "chart": '<path d="M4 20V4"/><path d="M4 20h16"/><rect x="7" y="12" width="3" height="5" rx="1"/>'
             '<rect x="12" y="8" width="3" height="9" rx="1"/><rect x="17" y="5" width="3" height="12" rx="1"/>',
    "pie": '<path d="M12 3.5A8.5 8.5 0 1 0 20.5 12H12z"/><path d="M14.5 3.5A6.5 6.5 0 0 1 20.5 9.5h-6z"/>',
    "activity": '<path d="M3 12h4l2.5-6 4 12 2.5-6h5"/>',
    "cart": '<circle cx="9" cy="19.5" r="1.5"/><circle cx="17" cy="19.5" r="1.5"/>'
            '<path d="M2.5 4h2.2l2.6 11h11l2.2-8H6"/>',
    "credit-card": '<rect x="2.5" y="5.5" width="19" height="13" rx="2"/><path d="M2.5 10h19"/>',
    "phone": '<path d="M6.5 3.5h3l1.5 4-2 1.5a11 11 0 0 0 5 5l1.5-2 4 1.5v3a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 '
             '4.5 5.7 2 2 0 0 1 6.5 3.5z"/>',
    "pin": '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "code": '<path d="m8 6-5 6 5 6"/><path d="m16 6 5 6-5 6"/>',
    "terminal": '<rect x="3" y="4.5" width="18" height="15" rx="2"/><path d="m7.5 10 2.5 2.5-2.5 2.5"/>'
                '<path d="M13 15h4"/>',
    "database": '<ellipse cx="12" cy="6" rx="8" ry="3"/>'
                '<path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6"/>'
                '<path d="M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    "server": '<rect x="3" y="4" width="18" height="6.5" rx="1.5"/>'
              '<rect x="3" y="13.5" width="18" height="6.5" rx="1.5"/>'
              '<path d="M7 7.2h.01M7 16.8h.01"/>',
    "cloud": '<path d="M6.5 18.5A4 4 0 0 1 7 10.6a5.5 5.5 0 0 1 10.4 1.4 3.5 3.5 0 0 1-.4 6.5z"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/>'
             '<path d="M12 3c2.5 2.6 3.8 5.7 3.8 9S14.5 18.4 12 21c-2.5-2.6-3.8-5.7-3.8-9S9.5 5.6 12 3z"/>',
    "wifi": '<path d="M2.5 9a14 14 0 0 1 19 0"/><path d="M6 12.5a9 9 0 0 1 12 0"/>'
            '<path d="M9.5 16a4.5 4.5 0 0 1 5 0"/>'
            '<circle cx="12" cy="19.5" r="1" fill="currentColor" stroke="none"/>',
    "link": '<path d="M10 13.5a4 4 0 0 0 5.7 0l2.8-2.8a4 4 0 0 0-5.7-5.7L11.5 6.3"/>'
            '<path d="M14 10.5a4 4 0 0 0-5.7 0L5.5 13.3a4 4 0 0 0 5.7 5.7l1.3-1.3"/>',
    "share": '<circle cx="18" cy="5.5" r="2.5"/><circle cx="6" cy="12" r="2.5"/>'
             '<circle cx="18" cy="18.5" r="2.5"/><path d="m8.2 10.8 7.6-4M8.2 13.2l7.6 4"/>',
    "send": '<path d="M21 4 3 11l7 2.5L13 21z"/><path d="m10 13.5 5-5"/>',
    "inbox": '<path d="M3.5 13.5 6 5.5h12l2.5 8v5a2 2 0 0 1-2 2h-13a2 2 0 0 1-2-2z"/>'
             '<path d="M3.5 13.5H9l1 2.5h4l1-2.5h5.5"/>',
    "shield": '<path d="M12 3l7.5 3v6c0 4.5-3 7.8-7.5 9-4.5-1.2-7.5-4.5-7.5-9V6z"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="m11 12 8-8"/><path d="m16 4 4 4"/><path d="m13 7 4 4"/>',
    "sort": '<path d="M8 6v12"/><path d="m5 9 3-3 3 3"/><path d="M16 18V6"/><path d="m13 15 3 3 3-3"/>',
    "help": '<circle cx="12" cy="12" r="9"/>'
            '<path d="M9.5 9.5a2.6 2.6 0 1 1 3.5 2.4c-.7.3-1 .9-1 1.6v.5"/>'
            '<circle cx="12" cy="17" r=".95" fill="currentColor" stroke="none"/>',
    "zap": '<path d="M13 3 5 13.5h5L11 21l8-10.5h-5z"/>',
    "target": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="4.5"/>'
              '<circle cx="12" cy="12" r="1" fill="currentColor" stroke="none"/>',
    "bookmark": '<path d="M6 3.5h12v17l-6-4.5-6 4.5z"/>',
    "tag": '<path d="M3.5 11.5v-7h7l9 9-7 7z"/><circle cx="8" cy="8" r="1.3"/>',
    "layers": '<path d="m12 3 8.5 4.5L12 12 3.5 7.5z"/><path d="m3.5 12 8.5 4.5 8.5-4.5"/>'
              '<path d="m3.5 16.5 8.5 4.5 8.5-4.5"/>',
    "box": '<path d="M12 3 3.5 7.5v9L12 21l8.5-4.5v-9z"/><path d="m3.5 7.5 8.5 4.5 8.5-4.5"/>'
           '<path d="M12 12v9"/>',
    "loader": '<path d="M12 3a9 9 0 1 0 9 9"/>',
    "maximize": '<path d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5"/>',
    "minimize": '<path d="M9 4v5H4M20 9h-5V4M15 20v-5h5M4 15h5v5"/>',
    "log-in": '<path d="M10 4H5.5A1.5 1.5 0 0 0 4 5.5v13A1.5 1.5 0 0 0 5.5 20H10"/>'
              '<path d="M15 8l4 4-4 4"/><path d="M19 12H9"/>',
    "log-out": '<path d="M14 4h4.5A1.5 1.5 0 0 1 20 5.5v13A1.5 1.5 0 0 1 18.5 20H14"/>'
               '<path d="M9 8 5 12l4 4"/><path d="M5 12h10"/>',
    "power": '<path d="M12 4v8"/><path d="M7.5 6.5a7 7 0 1 0 9 0"/>',
    "wrench": '<path d="M15.5 4a4.5 4.5 0 0 0-4 6.6L4 18.1 6 20l7.5-7.5A4.5 4.5 0 1 0 15.5 4z"/>',
    "cpu": '<rect x="7" y="7" width="10" height="10" rx="1.5"/>'
           '<path d="M4 10h3M4 14h3M17 10h3M17 14h3M10 4v3M14 4v3M10 17v3M14 17v3"/>',
}

ICON_NAMES = tuple(sorted(ICONS))

_SIZE = {n: f"h-{n} w-{n}" for n in range(3, 13)}


class Icon(Component):
    """Icono SVG en línea; hereda ``currentColor`` y el grosor del trazo."""

    tag = ""

    def __init__(
        self,
        name: str = "check",
        *,
        size: int | str = 5,
        stroke: float | None = None,
        class_: str | None = None,
        **props: Any,
    ) -> None:
        super().__init__(**props)
        self.name = name
        self.size = size
        self.stroke = stroke
        self.class_ = class_

    def render(self, ctx: Any, path: str) -> str:
        paths = ICONS.get(self.name) or ICONS["help"]
        if isinstance(self.size, int):
            size_class = _SIZE.get(self.size, f"h-{self.size} w-{self.size}")
        else:
            size_class = str(self.size)
        classes = tw("shrink-0", size_class, self.class_)
        width = f' stroke-width="{self.stroke}"' if self.stroke else ' stroke-width="1.8"'
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
            f' stroke="currentColor"{width} stroke-linecap="round" stroke-linejoin="round"'
            f' class="{classes}" aria-hidden="true">{paths}</svg>'
        )


# ---------------------------------------------------------------------------
# Ampliación del set (apps modernas: editores, paneles, comercio, sistema)
# ---------------------------------------------------------------------------
EXTRA_ICONS: dict[str, str] = {
    # flechas y navegación
    "arrow-up-right": '<path d="M7 17 17 7"/><path d="M9 7h8v8"/>',
    "arrow-down-left": '<path d="M17 7 7 17"/><path d="M15 17H7V9"/>',
    "arrow-down-right": '<path d="M7 7l10 10"/><path d="M17 9v8H9"/>',
    "arrow-up-left": '<path d="M17 17 7 7"/><path d="M9 15V7h8"/>',
    "chevrons-left": '<path d="m11 17-5-5 5-5"/><path d="m18 17-5-5 5-5"/>',
    "chevrons-right": '<path d="m13 7 5 5-5 5"/><path d="m6 7 5 5-5 5"/>',
    "chevrons-up": '<path d="m7 11 5-5 5 5"/><path d="m7 18 5-5 5 5"/>',
    "chevron-up-down": '<path d="m7 9 5-5 5 5"/><path d="m7 15 5 5 5-5"/>',
    "undo": '<path d="M9 7 4 12l5 5"/><path d="M4 12h9a6 6 0 0 1 0 12"/>',
    "redo": '<path d="m15 7 5 5-5 5"/><path d="M20 12h-9a6 6 0 0 0 0 12"/>',
    "corner-up-right": '<path d="M6 18V9a3 3 0 0 1 3-3h9"/><path d="m15 3 4 3-4 3"/>',
    # edición y texto
    "bold": '<path d="M7 4h6a4 4 0 0 1 0 8H7z"/><path d="M7 12h7a4 4 0 0 1 0 8H7z"/>',
    "italic": '<path d="M15 4H9"/><path d="M15 20H9"/><path d="M14 4 10 20"/>',
    "underline": '<path d="M7 5v6a5 5 0 0 0 10 0V5"/><path d="M5 20h14"/>',
    "strikethrough": '<path d="M5 12h14"/><path d="M16 7a4 4 0 0 0-4-2c-2.5 0-4 1.3-4 3 0 1 .6 1.8 1.6 2.4"/>'
                     '<path d="M8 17a4 4 0 0 0 4 2c2.5 0 4-1.3 4-3 0-.8-.4-1.5-1.1-2"/>',
    "align-left": '<path d="M4 6h16M4 12h10M4 18h13"/>',
    "align-center": '<path d="M4 6h16M7 12h10M6 18h12"/>',
    "align-right": '<path d="M4 6h16M10 12h10M7 18h13"/>',
    "list-ordered": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="M4 5h1v4"/><path d="M4 15h2v1l-2 2h2"/>',
    "list-checks": '<path d="M10 6h10M10 12h10M10 18h10"/><path d="m3 6 1.5 1.5L7 5"/>'
                   '<path d="m3 12 1.5 1.5L7 11"/><path d="m3 18 1.5 1.5L7 17"/>',
    "indent": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="m4 8 4 4-4 4"/>',
    "outdent": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="m8 8-4 4 4 4"/>',
    "scissors": '<circle cx="6" cy="6" r="2.5"/><circle cx="6" cy="18" r="2.5"/>'
                '<path d="M8.2 7.8 20 18"/><path d="M8.2 16.2 20 6"/>',
    "paste": '<path d="M9 4h6v3H9z"/><path d="M7 6H5.5A1.5 1.5 0 0 0 4 7.5v12A1.5 1.5 0 0 0 5.5 21h13'
             'A1.5 1.5 0 0 0 20 19.5v-12A1.5 1.5 0 0 0 18.5 6H17"/>',
    "clipboard": '<rect x="6" y="4.5" width="12" height="16.5" rx="2"/>'
                 '<path d="M9 3.5h6v2H9z"/><path d="M9 11h6M9 15h4"/>',
    "save": '<path d="M5 4h11l3 3v13H5z"/><path d="M8 4v5h7V4"/><rect x="8" y="13" width="8" height="7"/>',
    "printer": '<path d="M7 8V4h10v4"/><rect x="4" y="8" width="16" height="7" rx="2"/>'
               '<path d="M7 15h10v5H7z"/>',
    # medios
    "volume": '<path d="M5 9v6h3l5 4V5l-5 4z"/><path d="M16 9a4 4 0 0 1 0 6"/>',
    "volume-x": '<path d="M5 9v6h3l5 4V5l-5 4z"/><path d="m16 9 4 6M20 9l-4 6"/>',
    "mic": '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0 0 14 0"/>'
           '<path d="M12 18v3"/>',
    "mic-off": '<path d="M9 5a3 3 0 0 1 6 0v5"/><path d="M9 11v0a3 3 0 0 0 4.5 2.6"/>'
               '<path d="M5 11a7 7 0 0 0 11 5.7"/><path d="M12 18v3"/><path d="m4 4 16 16"/>',
    "video": '<rect x="3" y="6" width="12" height="12" rx="2"/><path d="m15 11 6-3v8l-6-3z"/>',
    "video-off": '<path d="M3 8v8a2 2 0 0 0 2 2h10"/><path d="m15 11 6-3v8l-3-1.5"/>'
                 '<path d="m4 4 16 16"/>',
    "headphones": '<path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3" y="13" width="4" height="6" rx="2"/>'
                  '<rect x="17" y="13" width="4" height="6" rx="2"/>',
    "music": '<circle cx="7" cy="17" r="2.5"/><circle cx="18" cy="15" r="2.5"/>'
             '<path d="M9.5 17V6l11-2v11"/>',
    "cast": '<path d="M3 18a6 6 0 0 1 6 6"/><path d="M3 14a10 10 0 0 1 10 10"/><rect x="3" y="4" width="18" height="12" rx="2"/>',
    # archivos
    "folder-open": '<path d="M3 8V6.5A1.5 1.5 0 0 1 4.5 5H9l2 2.5h6.5A1.5 1.5 0 0 1 19 9v1"/>'
                   '<path d="M3.5 10h17l-2.2 9.2a1.5 1.5 0 0 1-1.5 1.1H6.2a1.5 1.5 0 0 1-1.5-1.1z"/>',
    "folder-plus": '<path d="M3 7.5A1.5 1.5 0 0 1 4.5 6H9l2 2.5h8.5A1.5 1.5 0 0 1 21 10v8.5'
                   'A1.5 1.5 0 0 1 19.5 20h-15A1.5 1.5 0 0 1 3 18.5z"/><path d="M12 11v5M9.5 13.5h5"/>',
    "file-text": '<path d="M6 3.5A1.5 1.5 0 0 1 7.5 2H14l4 4v14.5A1.5 1.5 0 0 1 16.5 22h-9'
                 'A1.5 1.5 0 0 1 6 20.5z"/><path d="M14 2v4.5h4"/><path d="M9 12h6M9 16h6"/>',
    "file-plus": '<path d="M6 3.5A1.5 1.5 0 0 1 7.5 2H14l4 4v14.5A1.5 1.5 0 0 1 16.5 22h-9'
                 'A1.5 1.5 0 0 1 6 20.5z"/><path d="M14 2v4.5h4"/><path d="M12 11v6M9 14h6"/>',
    "archive": '<rect x="3" y="4" width="18" height="4.5" rx="1.5"/>'
               '<path d="M4.5 8.5h15V19A1.5 1.5 0 0 1 18 20.5H6A1.5 1.5 0 0 1 4.5 19z"/>'
               '<path d="M10 12.5h4"/>',
    "paperclip": '<path d="M20 11.5 12 19.5a4.5 4.5 0 0 1-6.4-6.4l8-8a3 3 0 0 1 4.3 4.3l-8 8'
                 'a1.5 1.5 0 0 1-2.2-2.2l7-7"/>',
    # interfaz
    "layout": '<rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="M3.5 9h17M9.5 9v11.5"/>',
    "sidebar": '<rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="M9 3.5v17"/>',
    "panel-left": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M9 4v16"/>',
    "panel-right": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M15 4v16"/>',
    "table": '<rect x="3" y="4.5" width="18" height="15" rx="2"/><path d="M3 10h18M3 15h18M9 10v9.5M15 10v9.5"/>',
    "mouse-pointer": '<path d="m5 3 14 8-6 1.5L10 20z"/>',
    "hand": '<path d="M8 12V5.5a1.5 1.5 0 0 1 3 0V11"/><path d="M11 11V4.5a1.5 1.5 0 0 1 3 0V11"/>'
            '<path d="M14 11V6.5a1.5 1.5 0 0 1 3 0V13"/>'
            '<path d="M8 12v-1a1.5 1.5 0 0 0-3 0v5a6 6 0 0 0 6 6h2a6 6 0 0 0 6-6v-3"/>',
    "move": '<path d="M12 3v18M3 12h18"/><path d="m9 6 3-3 3 3M9 18l3 3 3-3M6 9l-3 3 3 3M18 9l3 3-3 3"/>',
    "expand": '<path d="M9 4H4v5M15 4h5v5M15 20h5v-5M9 20H4v-5"/>',
    "shrink": '<path d="M4 9h5V4M20 9h-5V4M20 15h-5v5M4 15h5v5"/>',
    "square": '<rect x="4" y="4" width="16" height="16" rx="3"/>',
    "circle": '<circle cx="12" cy="12" r="8.5"/>',
    "circle-dot": '<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="3.5"/>',
    "badge-check": '<path d="m12 3 2.2 1.6 2.7-.2 1 2.5 2.3 1.4-.7 2.6.7 2.6-2.3 1.4-1 2.5-2.7-.2L12 21'
                   'l-2.2-1.6-2.7.2-1-2.5L3.8 15l.7-2.6-.7-2.6L6.1 8.4l1-2.5 2.7.2z"/>'
                   '<path d="m9 12 2 2 4-4"/>',
    "bookmark-plus": '<path d="M6 3.5h12v17l-6-4.5-6 4.5z"/><path d="M12 7v5M9.5 9.5h5"/>',
    "square-check": '<rect x="4" y="4" width="16" height="16" rx="3"/><path d="m8.5 12.5 2.5 2.5L16 9.5"/>',
    "timer": '<circle cx="12" cy="13.5" r="7.5"/><path d="M12 9.5v4l2.5 2"/><path d="M9 2.5h6"/>',
    # estado
    "alert-triangle": '<path d="M12 3.5 21 20H3z"/><path d="M12 9.5v4.5"/>'
                      '<circle cx="12" cy="17" r=".95" fill="currentColor" stroke="none"/>',
    "alert-circle": '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5"/>'
                    '<circle cx="12" cy="16.5" r=".95" fill="currentColor" stroke="none"/>',
    "loader-2": '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8'
                'M18.4 5.6l-2.8 2.8M8.4 15.6l-2.8 2.8"/>',
    # comercio
    "wallet": '<rect x="3" y="6" width="18" height="13" rx="2"/>'
              '<path d="M3 10h18"/><circle cx="17" cy="14.5" r="1.2" fill="currentColor" stroke="none"/>',
    "banknote": '<rect x="2.5" y="6.5" width="19" height="11" rx="2"/><circle cx="12" cy="12" r="2.8"/>'
                '<path d="M6 12h.01M18 12h.01"/>',
    "receipt": '<path d="M6 3.5h12v17l-3-2-3 2-3-2-3 2z"/><path d="M9 8h6M9 12h6"/>',
    "ticket": '<path d="M4 8.5V6h16v2.5a3 3 0 0 0 0 7V18H4v-2.5a3 3 0 0 0 0-7z"/>'
              '<path d="M12 7v10" stroke-dasharray="2 2"/>',
    "gift": '<rect x="3.5" y="8.5" width="17" height="11.5" rx="1.5"/><path d="M3.5 12.5h17"/>'
            '<path d="M12 8.5V20"/><path d="M12 8.5C10 8.5 8 7.6 8 6s1.6-2 2.6-1.2S12 8.5 12 8.5z"/>'
            '<path d="M12 8.5c2 0 4-.9 4-2.5s-1.6-2-2.6-1.2S12 8.5 12 8.5z"/>',
    "shopping-bag": '<path d="M5 8h14l-1 12H6z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>',
    "store": '<path d="M4 9.5V19h16V9.5"/><path d="M3 9.5 5.5 4h13L21 9.5a3 3 0 0 1-6 0 3 3 0 0 1-6 0 3 3 0 0 1-6 0z"/>',
    # comunicación
    "message-circle": '<path d="M21 12a8.5 8.5 0 0 1-12.3 7.6L4 21l1.5-4.4A8.5 8.5 0 1 1 21 12z"/>',
    "message-square": '<path d="M4 5.5h16v10.5H9L4 20z"/>',
    "thumbs-up": '<path d="M7 20V10l4-7 1.5.8a2 2 0 0 1 1 2.4L12.5 9H19a2 2 0 0 1 2 2.4l-1.4 6.6'
                 'A2 2 0 0 1 17.6 20z"/><path d="M7 10H4v10h3"/>',
    "thumbs-down": '<path d="M7 4v10l4 7 1.5-.8a2 2 0 0 0 1-2.4L12.5 15H19a2 2 0 0 0 2-2.4l-1.4-6.6'
                   'A2 2 0 0 0 17.6 4z"/><path d="M7 14H4V4h3"/>',
    "at-sign": '<circle cx="12" cy="12" r="4"/><path d="M16 8v5a3 3 0 0 0 6 0v-1a10 10 0 1 0-4 8"/>',
    "hash": '<path d="M9 4 7 20M17 4l-2 16M4 9h16M3 15h16"/>',
    # desarrollo
    "git-branch": '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="9" r="2"/>'
                  '<path d="M6 7v10"/><path d="M18 11c0 4-6 3-6 6"/>',
    "git-commit": '<circle cx="12" cy="12" r="3.5"/><path d="M3 12h5.5M15.5 12H21"/>',
    "git-merge": '<circle cx="6" cy="5" r="2"/><circle cx="6" cy="19" r="2"/><circle cx="18" cy="12" r="2"/>'
                 '<path d="M6 7v10"/><path d="M18 10c0-3-4-3-6-3s-6 0-6-2"/>',
    "braces": '<path d="M9 3.5c-2 0-2.5 1-2.5 2.5v3c0 1.5-.8 2.5-2.5 3 1.7.5 2.5 1.5 2.5 3v3'
              'c0 1.5.5 2.5 2.5 2.5"/><path d="M15 3.5c2 0 2.5 1 2.5 2.5v3c0 1.5.8 2.5 2.5 3'
              '-1.7.5-2.5 1.5-2.5 3v3c0 1.5-.5 2.5-2.5 2.5"/>',
    "bug": '<rect x="7" y="7" width="10" height="12" rx="5"/><path d="M9 3.5 10.5 6M15 3.5 13.5 6"/>'
           '<path d="M4 11h3M17 11h3M4 16h3M17 16h3M7 19.5 5.5 21M17 19.5l1.5 1.5"/>',
    "flask": '<path d="M9 3h6"/><path d="M10 3v6l-5.5 9.5A1.5 1.5 0 0 0 5.8 21h12.4a1.5 1.5 0 0 0 1.3-2.5L14 9V3"/>'
             '<path d="M7 15h10"/>',
    "package": '<path d="M12 3 3.5 7.5v9L12 21l8.5-4.5v-9z"/><path d="m3.5 7.5 8.5 4.5 8.5-4.5"/>'
               '<path d="M12 12v9"/><path d="m7.5 5 8.5 4.5"/>',
    "boxes": '<path d="M12 3 8 5.2v4.6L12 12l4-2.2V5.2z"/><path d="M6 12 2 14.2v4.6L6 21l4-2.2v-4.6z"/>'
             '<path d="M18 12l-4 2.2v4.6L18 21l4-2.2v-4.6z"/>',
    "component": '<path d="m12 3 3.5 3.5L12 10 8.5 6.5z"/><path d="m6.5 8.5 3.5 3.5-3.5 3.5L3 12z"/>'
                 '<path d="m17.5 8.5 3.5 3.5-3.5 3.5L14 12z"/><path d="m12 14 3.5 3.5L12 21l-3.5-3.5z"/>',
    "regex": '<path d="M12 5v8M8.5 7l7 4M15.5 7l-7 4"/><circle cx="6" cy="18" r="2"/>',
    "terminal-2": '<rect x="3" y="4.5" width="18" height="15" rx="2"/><path d="m7 10 2.5 2.5L7 15"/>'
                  '<path d="M13 15h4"/>',
    # sistema
    "hard-drive": '<rect x="3" y="6" width="18" height="6" rx="2"/><rect x="3" y="12" width="18" height="6" rx="2"/>'
                  '<path d="M7 9h.01M7 15h.01"/>',
    "keyboard": '<rect x="2.5" y="6.5" width="19" height="11" rx="2"/><path d="M6 10h.01M9.5 10h.01'
                'M13 10h.01M16.5 10h.01M6 13.5h.01M18 13.5h.01M10 13.5h4"/>',
    "monitor": '<rect x="3" y="4.5" width="18" height="12" rx="2"/><path d="M9 20h6M12 16.5V20"/>',
    "smartphone": '<rect x="7" y="2.5" width="10" height="19" rx="2"/><path d="M11 18.5h2"/>',
    "tablet": '<rect x="4.5" y="3" width="15" height="18" rx="2"/><path d="M11 18h2"/>',
    "thermometer": '<path d="M12 14V5a2.5 2.5 0 0 1 5 0v9a4 4 0 1 1-5 0z"/><path d="M14.5 9v6"/>',
    "battery": '<rect x="2.5" y="8" width="17" height="8" rx="2"/><path d="M21.5 11v2"/>'
               '<rect x="5" y="10" width="6" height="4" fill="currentColor" stroke="none"/>',
    "plug": '<path d="M9 3v5M15 3v5"/><path d="M6 8h12v3a6 6 0 0 1-12 0z"/><path d="M12 17v4"/>',
    "fan": '<circle cx="12" cy="12" r="2.2"/><path d="M12 9.8V4.5M13.9 13.1l4.6 2.7M10.1 13.1l-4.6 2.7"/>',
    "gauge": '<path d="M4 18a8 8 0 1 1 16 0"/><path d="m12 14 4-4"/><circle cx="12" cy="14" r="1.6"/>',
    # varios
    "sparkles": '<path d="m12 3 1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/>'
                '<path d="m18.5 15 1 2.5 2.5 1-2.5 1-1 2.5-1-2.5-2.5-1 2.5-1z"/>',
    "flag": '<path d="M5 3.5v17"/><path d="M5 4.5h11l-1.5 3.5L16 11.5H5z"/>',
    "trophy": '<path d="M8 4.5h8v5a4 4 0 0 1-8 0z"/><path d="M8 6H5.5A2.5 2.5 0 0 0 8 10.5"/>'
              '<path d="M16 6h2.5A2.5 2.5 0 0 1 16 10.5"/><path d="M12 13.5V17"/><path d="M8.5 20.5h7"/>',
    "award": '<circle cx="12" cy="9" r="5.5"/><path d="m8.5 13.5-1 8 4.5-2.5 4.5 2.5-1-8"/>',
    "map": '<path d="m3 6.5 6-2.5 6 2.5 6-2.5v13l-6 2.5-6-2.5-6 2.5z"/><path d="M9 4v13M15 6.5v13"/>',
    "map-pin": '<path d="M12 21s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z"/><circle cx="12" cy="10" r="2.5"/>',
    "navigation": '<path d="m3.5 11 17-7-7 17-2.5-7z"/>',
    "compass": '<circle cx="12" cy="12" r="9"/><path d="m15.5 8.5-2 5-5 2 2-5z"/>',
    "crosshair": '<circle cx="12" cy="12" r="9"/><path d="M12 3v5M12 16v5M3 12h5M16 12h5"/>',
    "anchor": '<circle cx="12" cy="5.5" r="2.5"/><path d="M12 8v12"/>'
              '<path d="M7 12H4a8 8 0 0 0 16 0h-3"/>',
    "flame": '<path d="M12 21c3.5 0 6-2.3 6-5.5 0-4-4-6.5-4-10.5-2 1-3 2.6-3 4.5-1-1-1.5-2-1.5-3'
             '-1.6 1.7-3.5 4.6-3.5 9C6 18.7 8.5 21 12 21z"/>',
    "droplet": '<path d="M12 3.5c3.5 4 6 6.8 6 10a6 6 0 0 1-12 0c0-3.2 2.5-6 6-10z"/>',
    "sunrise": '<path d="M12 3v3M4.2 10.2 6 12M19.8 10.2 18 12M2.5 18h19"/>'
               '<path d="M7 18a5 5 0 0 1 10 0"/><path d="m9.5 6.5 2.5-2.5 2.5 2.5"/>',
    "sunset": '<path d="M12 9V6M4.2 12.2 6 14M19.8 12.2 18 14M2.5 18h19"/>'
              '<path d="M7 18a5 5 0 0 1 10 0"/><path d="m9.5 6.5 2.5 2.5 2.5-2.5"/>',
    "leaf": '<path d="M4.5 19.5c-2-6 2-14 15-15 0 13-8 17-15 15z"/><path d="M9 15c2-3 4.5-5 8-6.5"/>',
    "snowflake": '<path d="M12 3v18M4.2 7.5l15.6 9M19.8 7.5 4.2 16.5"/>'
                 '<path d="m9 4.5 3 3 3-3M9 19.5l3-3 3 3"/>',
}

ICONS.update(EXTRA_ICONS)
ICON_NAMES = tuple(sorted(ICONS))


class _Picker:
    """Adapta un callback ``on_pick(nombre)`` al evento `change` del cliente."""

    def __init__(self, callback: Callable[[str], Any]) -> None:
        self.callback = callback

    def __call__(self, event: Any) -> None:
        self.callback(getattr(event, "value", "") or "")


class IconGrid(Component):
    """Muestra todos los iconos con su nombre (catálogo / selector visual)."""

    tag = "div"

    def __init__(
        self,
        *,
        names: Sequence[str] | None = None,
        size: int = 5,
        columns: int = 8,
        searchable: bool = False,
        on_pick: Callable[[str], Any] | None = None,
        **props: Any,
    ) -> None:
        self.icon_names = list(names or ICON_NAMES)
        self.icon_size = size
        self.columns = columns
        self.searchable = searchable
        self.on_pick = on_pick
        if on_pick is not None:
            props["on_change"] = _Picker(on_pick)
        props["base_class"] = tw("flex flex-col gap-3", props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: Any, path: str) -> str:
        head = ""
        if self.searchable:
            head = (
                '<input type="search" data-iui-command="%s" placeholder="Buscar icono…" '
                'class="h-9 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm '
                'focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/25 focus:outline-none '
                'dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"/>'
            ) % f"{path}-grid"
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, self.handlers, [f"i{index}" for index in range(len(self.icon_names))])
        cells = []
        for index, name in enumerate(self.icon_names):
            button = ""
            if self.on_pick is not None:
                button = (
                    f' data-iui-emit="change" data-iui-value="{name}"'
                )
            cells.append(
                f'<button type="button" id="{escape(uid)}-i{index}" data-iui-item '
                f'title="{name}"{button} class="group flex flex-col items-center gap-1 rounded-lg '
                'border border-transparent p-2 text-slate-600 transition hover:border-slate-200 '
                'hover:bg-slate-50 dark:text-slate-300 dark:hover:border-slate-700 '
                'dark:hover:bg-slate-800">'
                f"{Icon(name, size=self.icon_size).render(ctx, f'{path}-i{index}')}"
                '<span class="max-w-full truncate text-[10px] text-slate-400 group-hover:text-slate-600 '
                f'dark:group-hover:text-slate-200">{escape(name)}</span></button>'
            )
        grid = (
            f'<div id="{escape(path)}-grid" class="grid gap-1" '
            f'style="grid-template-columns: repeat({self.columns}, minmax(0, 1fr))">'
            f'{"".join(cells)}</div>'
        )
        return head + grid
