"""Escapado y utilidades HTML de bajo nivel.

Todo el HTML que produce ``interui`` pasa por aquí, de modo que el contenido
dinámico se escapa siempre (salvo que se envuelva explícitamente en ``Markup``).
"""

from __future__ import annotations

import html as _html
from typing import Any, Iterable

__all__ = ["Markup", "escape", "raw", "is_safe", "attr_string", "element", "VOID"]

VOID = frozenset(
    {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }
)

_TRUE = {"true", "1", "yes", "on"}


class Markup(str):
    """Cadena ya escapada/confiable que no debe volver a escaparse."""

    __slots__ = ()


def raw(value: Any) -> Markup:
    """Marca un valor como HTML seguro (escape hatch deliberado)."""
    return Markup("" if value is None else str(value))


def is_safe(value: Any) -> bool:
    return isinstance(value, Markup)


def escape(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, Markup):
        return str(value)
    return _html.escape(str(value), quote=True)


def attr_string(attrs: dict[str, Any]) -> str:
    """Serializa atributos: ``True`` -> atributo booleano, ``None/False`` -> se omite."""
    parts: list[str] = []
    for name, value in attrs.items():
        if value is None or value is False:
            continue
        name = name.replace("_", "-") if name not in ("class_", "for_") else name
        if name.endswith("_"):
            name = name[:-1]
        if value is True:
            parts.append(name)
            continue
        if isinstance(value, (list, tuple, set, frozenset)):
            value = " ".join(str(v) for v in value if v is not None and v is not False)
        if isinstance(value, dict):
            import json

            value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        parts.append(f'{name}="{_html.escape(str(value), quote=True)}"')
    return (" " + " ".join(parts)) if parts else ""


def element(tag: str, children: Any = "", /, **attrs: Any) -> str:
    """Construye una etiqueta HTML con contenido ya renderizado."""
    all_attrs = attr_string(attrs)
    if tag in VOID:
        return f"<{tag}{all_attrs} />"
    return f"<{tag}{all_attrs}>{children}</{tag}>"


def flatten(children: Iterable[Any]) -> list[Any]:
    out: list[Any] = []
    for child in children:
        if child is None or child is True or child is False:
            continue
        if isinstance(child, (list, tuple, set, frozenset, filter, map, range)):
            out.extend(flatten(child))
        else:
            out.append(child)
    return out
