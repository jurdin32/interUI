"""Registro de mensajes compatible con apps empaquetadas.

En Windows, un ejecutable creado con ``--windowed`` no tiene ``stdout`` ni
``stderr`` (son ``None``). Escribir con ``print`` en ese caso lanzaría
``AttributeError`` y cerraría la aplicación. ``log()`` escribe en la consola
cuando existe y, si no, en ``<data_dir>/interui.log``.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

__all__ = ["log", "log_file"]

_file: Path | None = None


def log_file(path: str | Path | None = None) -> Path | None:
    """Fija el archivo de registro (``None`` para desactivarlo)."""
    global _file
    _file = Path(path) if path is not None else None
    return _file


def log(message: str = "", *, error: bool = False) -> None:
    """Escribe un mensaje sin romper la app si no hay consola."""
    stream = sys.stderr if error else sys.stdout
    if stream is not None:
        try:
            print(message, file=stream, flush=True)
            return
        except (OSError, ValueError):  # consola cerrada o redirigida a un pipe muerto
            pass
    if _file is None:
        return
    try:
        _file.parent.mkdir(parents=True, exist_ok=True)
        with open(_file, "a", encoding="utf-8") as handle:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            handle.write(f"[{stamp}] {message}\n")
    except OSError:
        pass
