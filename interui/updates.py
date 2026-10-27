"""Comprobación de actualizaciones de interUI.

La app consulta (en segundo plano y sin bloquear la ventana) cuál es la última
versión publicada y, si es más nueva que la instalada, muestra un aviso en la
interfaz con el comando exacto para actualizar.

```python
import interui as ui

info = ui.updates.check()
if info and info.available:
    print(info.message())        # "Hay una versión nueva: 0.4.0 (tienes 0.3.0)"
    print(info.command)          # comando listo para copiar y pegar
```

Todo es opcional: ``App(check_updates=False)`` o la variable de entorno
``INTERUI_NO_UPDATE_CHECK=1`` desactivan la consulta por completo (útil en
redes cerradas, CI o pruebas).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

__all__ = [
    "UpdateInfo", "check", "current_version", "install_command", "is_newer",
    "parse_version", "set_override", "run_upgrade", "install_info", "enabled", "CACHE_TTL",
]

REPO = "jurdin32/interUI"
PACKAGE = "interui"
GIT_URL = f"https://github.com/{REPO}.git"
RELEASES_URL = f"https://github.com/{REPO}/releases"
UPDATING_URL = f"https://github.com/{REPO}/blob/main/docs/actualizar.md"
GITHUB_API = f"https://api.github.com/repos/{REPO}/tags"
PYPI_API = f"https://pypi.org/pypi/{PACKAGE}/json"
DEFAULT_TIMEOUT = 2.5
CACHE_TTL = 24 * 60 * 60
USER_AGENT = f"interui-update-check ({PACKAGE})"

_override: str | None = None
_cache: UpdateInfo | None = None


# ---------------------------------------------------------------------------
# versiones
# ---------------------------------------------------------------------------
_VERSION_RE = re.compile(r"(\d+(?:\.\d+)*)")


def parse_version(value: str) -> tuple[int, ...]:
    """``"v0.3.0"`` → ``(0, 3, 0)``; tolera prefijos y sufijos."""
    match = _VERSION_RE.search(str(value or ""))
    if not match:
        return (0,)
    return tuple(int(part) for part in match.group(1).split("."))


def is_newer(candidate: str, reference: str) -> bool:
    """¿``candidate`` es más reciente que ``reference``?"""
    left, right = parse_version(candidate), parse_version(reference)
    width = max(len(left), len(right))
    left += (0,) * (width - len(left))
    right += (0,) * (width - len(right))
    return left > right


def current_version() -> str:
    from . import __version__

    return __version__


# ---------------------------------------------------------------------------
# comando de actualización
# ---------------------------------------------------------------------------
def _direct_url() -> dict[str, Any]:
    """Metadata de instalación (vacío si vino de PyPI)."""
    try:
        from importlib.metadata import PackageNotFoundError, distribution

        raw = distribution(PACKAGE).read_text("direct_url.json")
    except (PackageNotFoundError, OSError, ValueError):  # pragma: no cover - entorno raro
        return {}
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:  # pragma: no cover - metadata corrupta
        return {}
    return data if isinstance(data, dict) else {}


def install_info(with_gui: bool = True) -> tuple[str, str]:
    """Cómo se instaló interUI y el comando para actualizarlo.

    Devuelve ``(origen, comando)`` donde origen es ``"git"``, ``"local"``
    (clon en editable), ``"wheel"`` (archivo .whl local) o ``"pypi"``.
    """
    import shlex
    from urllib.parse import urlparse, unquote

    extra = "[desktop]" if with_gui else ""
    data = _direct_url()
    url = str(data.get("url") or "")
    if url.startswith("file://"):
        path = Path(unquote(urlparse(url).path))
        quoted = shlex.quote(str(path))
        editable = bool(data.get("dir_info", {}).get("editable"))
        if editable or path.is_dir():
            return "local", f"git -C {quoted} pull && pip install -U -e {quoted}"
        # Instalado desde un archivo .whl local: no hay nada que consultar, se
        # reinstala el wheel nuevo cuando lo tengas.
        return "wheel", f"pip install -U {quoted}"
    if url:
        return "git", f'pip install -U "{PACKAGE}{extra} @ git+{GIT_URL}"'
    return "pypi", f"pip install -U {PACKAGE}{extra}"


def install_command(with_gui: bool = True) -> str:
    """Comando para actualizar, adaptado a cómo se instaló interUI."""
    return install_info(with_gui)[1]


# ---------------------------------------------------------------------------
# resultado
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class UpdateInfo:
    """Resultado de la comprobación."""

    current: str
    latest: str
    url: str = UPDATING_URL
    command: str = ""
    source: str = "github"

    def __post_init__(self) -> None:
        if not self.command:
            object.__setattr__(self, "command", install_command())

    @property
    def available(self) -> bool:
        return is_newer(self.latest, self.current)

    def message(self) -> str:
        if self.available:
            return f"Hay una versión nueva de interUI: {self.latest} (tienes {self.current})"
        return f"interUI está actualizado ({self.current})"

    def to_payload(self) -> dict[str, Any]:
        """Mensaje que viaja al cliente para mostrar el aviso."""
        return {
            "t": "update",
            "current": self.current,
            "latest": self.latest,
            "command": self.command or install_command(),
            "url": self.url,
        }


# ---------------------------------------------------------------------------
# red
# ---------------------------------------------------------------------------
def _fetch_json(url: str, timeout: float) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 (URLs fijas)
        return json.loads(response.read().decode("utf-8"))


def _latest_from_github(timeout: float) -> str | None:
    payload = _fetch_json(GITHUB_API, timeout)
    if not isinstance(payload, list):
        return None
    versions = [str(item.get("name", "")) for item in payload if isinstance(item, dict)]
    versions = [version for version in versions if parse_version(version) > (0,)]
    if not versions:
        return None
    return max(versions, key=parse_version)


def _latest_from_pypi(timeout: float) -> str | None:
    payload = _fetch_json(PYPI_API, timeout)
    if not isinstance(payload, dict):
        return None
    version = payload.get("info", {}).get("version")
    return str(version) if version else None


def _cache_path(cache_dir: str | Path | None) -> Path | None:
    if cache_dir is None:
        return None
    return Path(cache_dir) / "update-check.json"


def _read_cache(path: Path | None, ttl: int) -> UpdateInfo | None:
    if path is None or not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    if time.time() - float(data.get("checked_at", 0)) > ttl:
        return None
    latest = data.get("latest")
    if not latest:
        return None
    return UpdateInfo(
        current=current_version(),
        latest=str(latest),
        url=str(data.get("url") or UPDATING_URL),
        command=str(data.get("command") or install_command()),
        source=str(data.get("source") or "cache"),
    )


def _write_cache(path: Path | None, info: UpdateInfo) -> None:
    if path is None:
        return
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "checked_at": time.time(),
                    "latest": info.latest,
                    "url": info.url,
                    "command": info.command,
                    "source": info.source,
                }
            ),
            encoding="utf-8",
        )
    except OSError:  # pragma: no cover - disco de solo lectura
        pass


def set_override(version: str | None) -> None:
    """Fuerza la «última versión» (pruebas y demos). ``None`` vuelve a la red."""
    global _override, _cache
    _override = version
    _cache = None


def enabled() -> bool:
    """La comprobación se puede desactivar con ``INTERUI_NO_UPDATE_CHECK=1``."""
    return not os.environ.get("INTERUI_NO_UPDATE_CHECK")


def check(
    *,
    timeout: float = DEFAULT_TIMEOUT,
    cache_dir: str | Path | None = None,
    ttl: int = CACHE_TTL,
    force: bool = False,
) -> UpdateInfo | None:
    """Devuelve la última versión publicada, o ``None`` si no se pudo saber.

    Nunca lanza por problemas de red: sin conexión (o con la comprobación
    desactivada) simplemente devuelve ``None``.
    """
    global _cache
    if _override:
        return UpdateInfo(current=current_version(), latest=_override)
    if not enabled():
        return None

    cached = _read_cache(_cache_path(cache_dir), ttl) if not force else None
    if cached is not None:
        return cached

    if _cache is not None and not force:
        return _cache

    latest: str | None = None
    source = "github"
    try:
        latest = _latest_from_github(timeout)
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        latest = None
    if latest is None:
        source = "pypi"
        try:
            latest = _latest_from_pypi(timeout)
        except (urllib.error.URLError, OSError, ValueError, TimeoutError):
            return None

    info = UpdateInfo(
        current=current_version(),
        latest=latest,
        url=UPDATING_URL,
        command=install_command(),
        source=source,
    )
    _cache = info
    _write_cache(_cache_path(cache_dir), info)
    return info


def check_async(callback: Any, **kwargs: Any) -> None:
    """Igual que :func:`check` pero en un hilo aparte (no bloquea la interfaz)."""
    import threading

    def worker() -> None:
        try:
            callback(check(**kwargs))
        except Exception:  # noqa: BLE001 - nunca debe tumbar la app
            callback(None)

    threading.Thread(target=worker, name="interui-update-check", daemon=True).start()


def run_upgrade(command: str) -> int:
    """Ejecuta el comando de actualización (lo usa ``interui update --run``)."""
    import subprocess

    parts = command.split()
    if parts and parts[0] == "pip":
        parts = [sys.executable, "-m", "pip", *parts[1:]]
    return subprocess.call(parts)  # noqa: S603 - comando propio, sin entrada del usuario
