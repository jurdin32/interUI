"""Modelo de eventos que viajan del navegador a Python."""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

__all__ = ["Attachment", "UIEvent", "invoke"]


@dataclass(slots=True)
class Attachment:
    """Archivo subido desde un control de fichero."""

    name: str
    size: int
    mime: str
    path: str
    url: str
    content: bytes | None = None

    def read(self) -> bytes:
        if self.content is not None:
            return self.content
        with open(self.path, "rb") as handle:
            return handle.read()

    def read_text(self, encoding: str = "utf-8") -> str:
        return self.read().decode(encoding)


@dataclass(slots=True)
class UIEvent:
    """Evento normalizado de la interfaz."""

    id: str
    event: str
    value: Any = None
    checked: bool | None = None
    key: str | None = None
    mods: dict[str, bool] = field(default_factory=dict)
    files: list[Attachment] = field(default_factory=list)
    data: dict[str, Any] = field(default_factory=dict)
    target: str | None = None

    # -- azúcar sintáctico ------------------------------------------------
    @property
    def name(self) -> str:
        return str(self.data.get("name") or "")

    @property
    def index(self) -> int | None:
        raw = self.data.get("index")
        try:
            return int(raw)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None

    @property
    def text(self) -> str:
        return "" if self.value is None else str(self.value)

    @property
    def as_number(self) -> float | None:
        try:
            return float(self.value)  # type: ignore[arg-type]
        except (TypeError, ValueError):
            return None

    def __iter__(self) -> Iterable[Any]:
        yield self.value
        yield self.checked

    def __repr__(self) -> str:  # pragma: no cover - ayuda de depuración
        bits = [f"id={self.id!r}", f"event={self.event!r}"]
        if self.value is not None:
            bits.append(f"value={self.value!r}")
        if self.checked is not None:
            bits.append(f"checked={self.checked!r}")
        return f"UIEvent({', '.join(bits)})"


def invoke(handler: Callable[..., Any], event: UIEvent) -> Any:
    """Ejecuta un handler en cualquiera de sus formas admitidas.

    * ``lambda: ...``            → sin argumentos
    * ``lambda evento: ...``     → recibe el ``UIEvent``
    * ``una_senal``              → guarda el valor del evento en la señal
      (``input(on_input=nombre)``, ``switch(on_change=activo)``…)
    * método de señal (``count.inc``) → se llama sin argumentos
    """
    setter = getattr(handler, "set", None)
    if callable(setter) and not isinstance(handler, type):
        # Señal pasada directamente como handler.
        value = event.checked if event.checked is not None else event.value
        return setter(value)

    try:
        signature = inspect.signature(handler)
    except (TypeError, ValueError):
        return handler(event)

    # Solo cuentan los parámetros obligatorios: así `on_click=contador.inc`
    # (cuyo `amount` tiene valor por defecto) se llama sin argumentos.
    required = 0
    variadic = False
    for parameter in signature.parameters.values():
        if parameter.kind is parameter.VAR_POSITIONAL:
            variadic = True
        elif parameter.kind in (parameter.POSITIONAL_ONLY, parameter.POSITIONAL_OR_KEYWORD):
            if parameter.default is parameter.empty:
                required += 1
    if variadic or required >= 1:
        return handler(event)
    return handler()
