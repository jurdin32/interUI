"""Conjunto de iconos vectoriales incluidos (sin dependencias externas).

Los trazos son geometría propia pensada para 24x24 con ``stroke-width`` 1.8, de
modo que heredan color y grosor del texto.
"""

from __future__ import annotations

from typing import Any

from .base import Component
from .style import tw

__all__ = ["Icon", "ICONS", "ICON_NAMES"]

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
