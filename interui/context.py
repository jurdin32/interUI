"""Contexto de renderizado: identidades estables y registro de handlers."""

from __future__ import annotations

import re
from typing import Any, Callable

__all__ = ["RenderContext"]

_SLUG = re.compile(r"[^a-zA-Z0-9_\-]+")


def slug(text: str) -> str:
    return _SLUG.sub("-", str(text)).strip("-") or "x"


class RenderContext:
    """Se crea uno por cada render completo de la aplicación."""

    __slots__ = ("app", "bindings", "meta", "assets", "page", "_counter")

    def __init__(self, app: Any = None, page: str | None = None) -> None:
        self.app = app
        self.page = page
        self.bindings: dict[str, dict[str, Callable[..., Any]]] = {}
        self.meta: dict[str, dict[str, Any]] = {}
        self.assets: list[str] = []
        self._counter = 0

    # -- identidades ------------------------------------------------------
    def uid(self, path: str, key: Any = None, explicit: str | None = None) -> str:
        if explicit:
            return slug(explicit)
        if key is not None:
            return f"{path}-{slug(key)}"
        return path

    def auto_id(self, prefix: str = "iui") -> str:
        self._counter += 1
        return f"{prefix}-{self._counter}"

    # -- handlers ---------------------------------------------------------
    def bind(self, uid: str, event: str, handler: Callable[..., Any]) -> None:
        self.bindings.setdefault(uid, {})[event] = handler

    def meta_for(self, uid: str, **values: Any) -> None:
        self.meta.setdefault(uid, {}).update(values)

    def child(self, path: str, index: int, key: Any = None) -> str:
        suffix = f"-{slug(key)}" if key is not None else ""
        return f"{path}-{index}{suffix}"
