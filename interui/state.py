"""Estado reactivo: señales simples ligadas a la aplicación."""

from __future__ import annotations

from typing import Any, Callable

__all__ = ["Signal", "number_of", "value_of"]


class Signal:
    """Valor compartido que, al cambiar, provoca un re-render automático."""

    __slots__ = ("_app", "name", "default")

    def __init__(self, app: Any, name: str, default: Any = None) -> None:
        self._app = app
        self.name = name
        self.default = default

    @property
    def value(self) -> Any:
        return self._app._state.get(self.name, self.default)

    def get(self, default: Any = None) -> Any:
        if self.name in self._app._state:
            return self._app._state[self.name]
        return self.default if default is None else default

    def set(self, value: Any) -> Any:
        if self._app._state.get(self.name) == value:
            return value
        self._app._state[self.name] = value
        self._app.schedule_refresh()
        return value

    def update(self, fn: Callable[[Any], Any]) -> Any:
        return self.set(fn(self.value))

    def inc(self, amount: Any = 1) -> Any:
        """``on_click=contador.inc`` incrementa sin escribir lambdas."""
        return self.set(self.get(0) + amount)

    def dec(self, amount: Any = 1) -> Any:
        return self.inc(-amount)

    def toggle(self) -> bool:
        return self.set(not self.get())

    def push(self, item: Any) -> list[Any]:
        current = list(self.get([]))
        current.append(item)
        self.set(current)
        return current

    def clear(self) -> None:
        self.set([])

    def __call__(self, *args: Any) -> Any:
        if args:
            return self.set(args[0])
        return self.get()

    # ``value=nombre`` debe escribir el valor, no ``Signal('x'=...)``.
    # (Para los booleanos se resuelve en el control con ``value_of``: definir
    # ``__bool__`` haría que una señal vacía se confundiera con ``None`` en
    # sitios como ``handler = handlers.get(x) or handlers.get("*")``.)
    def __str__(self) -> str:
        value = self.get()
        return "" if value is None else str(value)

    def __iadd__(self, other: Any) -> "Signal":  # type: ignore[override]
        self.set(self.get(0) + other)
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return f"Signal({self.name!r}={self.value!r})"


def value_of(value: Any, default: Any = None) -> Any:
    """Resuelve una señal o una función; deja el resto igual.

    Sirve para que ``Progress(valor)``, ``Switch(checked=activo)`` y compañía
    acepten señales sin que el control sepa que lo son.
    """
    if isinstance(value, Signal):
        return value.get()
    if callable(value) and not isinstance(value, type):
        return value()
    return default if value is None else value


def number_of(value: Any, default: float = 0.0) -> float:
    """Igual que :func:`value_of`, pero garantiza un número."""
    resolved = value_of(value, default)
    try:
        return float(resolved)
    except (TypeError, ValueError):
        return default
