"""Mezcla inteligente de clases Tailwind.

``tw()`` resuelve conflictos de utilidades (``p-2`` + ``p-6`` -> ``p-6``) para que
puedas sobreescribir el estilo de cualquier control pasando ``class_="..."``
sin tener que pelear con el orden del CSS generado.
"""

from __future__ import annotations

import re
from typing import Any

__all__ = ["tw", "cl"]

_SIZES = set("xs sm base lg xl 2xl 3xl 4xl 5xl 6xl 7xl 8xl 9xl".split())
_FONT_WEIGHTS = set("thin extralight light normal medium semibold bold extrabold black".split())
_ALIGN = set("left center right justify start end".split())
_TRACKING = set("tighter tight normal wide wider widest".split())
_LEADING = set("none tight snug normal relaxed loose".split())
_BORDER_STYLES = set("solid dashed dotted double hidden none".split())
_BORDER_WIDTHS = set("0 2 4 8".split())
_RADIUS = set("none sm md lg xl 2xl 3xl full".split())
_SHADOW = set("none sm md lg xl 2xl inner".split())
_BG_ATTACH = set("fixed local scroll".split())
_BG_CLIP = set("border padding content text".split())
_BG_ORIGIN = set("border padding content".split())
_BG_SIZE = set("auto cover contain".split())
_BG_REPEAT = set("repeat no-repeat repeat-x repeat-y round space".split())

_DISPLAY = set(
    "block inline inline-block flex grid hidden inline-flex inline-grid contents table "
    "table-row table-cell table-caption table-column flow-root list-item".split()
)
_FLEX_DIRECTION = set("flex-row flex-row-reverse flex-col flex-col-reverse".split())
_FLEX_WRAP = set("flex-wrap flex-wrap-reverse flex-nowrap".split())
_FLEX_SIZED = set("flex-1 flex-auto flex-initial flex-none".split())
_POSITION = set("static fixed absolute relative sticky".split())
_TEXT_TRANSFORM = set("uppercase lowercase capitalize normal-case".split())
_WHITESPACE = set(
    "whitespace-normal whitespace-nowrap whitespace-pre whitespace-pre-line "
    "whitespace-pre-wrap whitespace-break-spaces".split()
)
_BREAK = set("break-normal break-words break-all break-keep".split())
_OVERFLOW = set("overflow-auto overflow-hidden overflow-clip overflow-visible overflow-scroll".split())
_OBJECT_FIT = set("object-contain object-cover object-fill object-none object-scale-down".split())
_OBJECT_POS = set("object-bottom object-center object-left object-right object-top "
                  "object-left-bottom object-left-top object-right-bottom object-right-top".split())

_VARIANT_RE = re.compile(r"^((?:[a-zA-Z0-9_\-\*\[\]&>+.,:#=()%@/]+:)+)(.*)$")
_LENGTH_HINT = re.compile(r"(?:px|rem|em|%|ch|vh|vw|pt|fr)\b|clamp\(|calc\(")

_GROUP_BY_PREFIX = {
    "p": "padding", "px": "padding-x", "py": "padding-y",
    "pt": "padding-t", "pb": "padding-b", "pl": "padding-l", "pr": "padding-r",
    "ps": "padding-s", "pe": "padding-e",
    "m": "margin", "mx": "margin-x", "my": "margin-y",
    "mt": "margin-t", "mb": "margin-b", "ml": "margin-l", "mr": "margin-r",
    "ms": "margin-s", "me": "margin-e",
    "w": "width", "min-w": "min-width", "max-w": "max-width",
    "h": "height", "min-h": "min-height", "max-h": "max-height",
    "size": "size",
    "gap": "gap", "gap-x": "gap-x", "gap-y": "gap-y",
    "space-x": "space-x", "space-y": "space-y",
    "grid-cols": "grid-cols", "grid-rows": "grid-rows",
    "col-span": "col-span", "row-span": "row-span",
    "auto-cols": "auto-cols", "auto-rows": "auto-rows",
    "col-start": "col-start", "col-end": "col-end",
    "row-start": "row-start", "row-end": "row-end",
    "items": "items", "justify": "justify", "justify-items": "justify-items",
    "justify-self": "justify-self", "self": "self",
    "content": "content", "place-items": "place-items", "place-content": "place-content",
    "overflow": "overflow", "overflow-x": "overflow-x", "overflow-y": "overflow-y",
    "z": "z", "order": "order", "basis": "basis", "grow": "grow", "shrink": "shrink",
    "opacity": "opacity", "leading": "leading", "tracking": "tracking",
    "cursor": "cursor", "select": "select",
    "transition": "transition", "duration": "duration", "ease": "ease",
    "delay": "delay", "translate-x": "translate-x", "translate-y": "translate-y",
    "scale": "scale", "rotate": "rotate", "aspect": "aspect",
    "line-clamp": "line-clamp", "origin": "origin",
    "inset": "inset", "inset-x": "inset-x", "inset-y": "inset-y",
    "top": "top", "bottom": "bottom", "left": "left", "right": "right",
    "backdrop-blur": "backdrop-blur", "blur": "blur",
    "columns": "columns", "divide-x": "divide-x", "divide-y": "divide-y",
    "font": "font-family", "rounded-t": "radius-t", "rounded-r": "radius-r",
    "rounded-b": "radius-b", "rounded-l": "radius-l", "rounded-tl": "radius-tl",
    "rounded-tr": "radius-tr", "rounded-bl": "radius-bl", "rounded-br": "radius-br",
    "rounded-s": "radius-s", "rounded-e": "radius-e",
    "list": "list-style-type", "align": "vertical-align",
}


def _is_length(value: str) -> bool:
    return bool(_LENGTH_HINT.search(value)) or value in _SIZES


def _utility_key(util: str) -> str:
    """Devuelve la clave de conflicto de una utilidad Tailwind."""
    if util in _DISPLAY:
        return "display"
    if util == "sr-only":
        return "sr"
    if util in _FLEX_DIRECTION:
        return "flex-direction"
    if util in _FLEX_WRAP:
        return "flex-wrap"
    if util in _FLEX_SIZED or util.startswith("flex-["):
        return "flex"
    if util in _POSITION:
        return "position"
    if util in _TEXT_TRANSFORM:
        return "text-transform"
    if util in _WHITESPACE:
        return "whitespace"
    if util in _BREAK:
        return "word-break"
    if util in _OVERFLOW:
        return "overflow"
    if util in _OBJECT_FIT:
        return "object-fit"
    if util in _OBJECT_POS:
        return "object-position"
    if util in ("truncate", "italic", "underline", "overline", "line-through", "no-underline"):
        return util
    if util in ("border-collapse", "border-separate"):
        return "border-collapse"
    if util in ("table-auto", "table-fixed"):
        return "table-layout"

    if util.startswith("text-"):
        rest = util[5:]
        if rest in _SIZES or (rest.startswith("[") and _is_length(rest)):
            return "font-size"
        if rest in _ALIGN:
            return "text-align"
        if rest in _TRACKING:
            return "tracking"
        if rest.startswith(("ellipsis", "clip")):
            return "text-overflow"
        if rest.startswith(("wrap", "nowrap", "balance", "pretty")):
            return "text-wrap"
        if rest in _FONT_WEIGHTS:
            return "font-weight"
        return "text-color"

    if util.startswith("font-"):
        rest = util[5:]
        return "font-weight" if rest in _FONT_WEIGHTS else "font-family"

    if util.startswith("border-"):
        rest = util[7:]
        if rest in _BORDER_STYLES:
            return "border-style"
        if rest in _BORDER_WIDTHS or rest == "" or rest.startswith("["):
            return "border-width"
        if rest in _RADIUS:
            return "radius"
        if rest in ("x", "y", "t", "b", "l", "r", "s", "e"):
            return f"border-{rest}"
        if rest[0] in "xytblrse" and rest[1:2] == "-":
            return f"border-{rest[0]}"
        return "border-color"

    if util == "border":
        return "border-width"

    if util.startswith("rounded"):
        parts = util[len("rounded"):].lstrip("-").split("-")
        corner = parts[0]
        if corner in ("t", "r", "b", "l", "s", "e", "tl", "tr", "bl", "br", "ss", "se", "es", "ee"):
            return f"radius-{corner}"
        return "radius"

    if util.startswith("shadow"):
        rest = util[6:].lstrip("-")
        return "shadow" if rest in _SHADOW or rest == "" else "shadow-color"

    if util.startswith("bg-"):
        rest = util[3:]
        if rest in _BG_SIZE:
            return "bg-size"
        if rest in _BG_REPEAT:
            return "bg-repeat"
        if rest in _BG_ATTACH:
            return "bg-attachment"
        if rest in _BG_CLIP:
            return "bg-clip"
        if rest in _BG_ORIGIN:
            return "bg-origin"
        if rest.startswith(("gradient", "none", "url", "[")):
            return "bg-image"
        if rest in ("fixed", "local", "scroll"):
            return "bg-attachment"
        if rest in _POSITION:
            return "bg-attachment"
        if rest.split("-")[0] in ("top", "bottom", "left", "right", "center"):
            return "bg-position"
        return "bg-color"

    if util.startswith("fill-"):
        return "fill"
    if util.startswith("stroke-"):
        return "stroke-width" if util[7:] in _BORDER_WIDTHS else "stroke"

    if util.startswith("divide-"):
        rest = util[7:]
        if rest in ("x", "y") or rest.startswith(("x-", "y-")):
            return "divide-width"
        if rest in _BORDER_STYLES:
            return "divide-style"
        return "divide-color"

    if util.startswith("ring"):
        rest = util[4:].lstrip("-")
        if util == "ring" or rest in _BORDER_WIDTHS or rest in ("1", "3"):
            return "ring-width"
        if rest == "inset":
            return "ring-inset"
        if util.startswith("ring-offset-"):
            return "ring-offset"
        return "ring-color"

    if util.startswith("outline"):
        rest = util[7:].lstrip("-")
        if rest in ("", "none", "dashed", "dotted", "double"):
            return "outline-style"
        if rest in _BORDER_WIDTHS:
            return "outline-width"
        return "outline-color"

    # longest-prefix match against known groups
    best = None
    for prefix, group in _GROUP_BY_PREFIX.items():
        if util == prefix or util.startswith(prefix + "-"):
            if best is None or len(prefix) > len(best[0]):
                best = (prefix, group)
    if best is not None:
        return best[1]

    return util.split("-")[0]


def _key(util: str) -> str:
    variants = ""
    body = util
    match = _VARIANT_RE.match(util)
    if match:
        variants, body = match.group(1), match.group(2)
    stripped = body.lstrip("-")
    if stripped.startswith("-"):
        stripped = stripped[1:]
    return f"{variants}|{_utility_key(stripped)}"


def tw(*classes: Any) -> str:
    """Combina clases Tailwind; la última aparición de cada utilidad gana."""
    collected: list[str] = []
    for item in classes:
        if not item:
            continue
        if isinstance(item, (list, tuple, set, frozenset)):
            collected.extend(tw(*item).split())
        elif isinstance(item, (dict,)):
            collected.extend(tw(*[k for k, v in item.items() if v]).split())
        else:
            collected.extend(str(item).split())

    seen: dict[str, int] = {}
    result: list[str] = []
    for util in collected:
        key = _key(util)
        if key in seen:
            result[seen[key]] = ""
        seen[key] = len(result)
        result.append(util)
    return " ".join(part for part in result if part)


cl = tw
