"""Estado reactivo: señales simples ligadas a la aplicación."""

from __future__ import annotations

from typing import Any, Callable

__all__ = ["Signal"]


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

    def __iadd__(self, other: Any) -> "Signal":  # type: ignore[override]
        self.set(self.get(0) + other)
        return self

    def __repr__(self) -> str:  # pragma: no cover
        return f"Signal({self.name!r}={self.value!r})"
