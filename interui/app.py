"""Aplicación interui: rutas, estado, render y ventana."""

from __future__ import annotations

import json
import os
import platform
import re
import tempfile
import threading
import time
import traceback
import webbrowser
from pathlib import Path
from typing import Any, Callable

from .base import Component
from .context import RenderContext
from .desktop import DesktopError, DesktopWindow, Native, available as desktop_available
from .events import Attachment, UIEvent, invoke
from .html import escape
from .log import log, log_file
from .server import STATIC_DIR, Server, WebSocket
from .state import Signal

__all__ = ["App"]

_PARAM = re.compile(r"<(?:(?P<kind>\w+):)?(?P<name>\w+)>")
_TYPES: dict[str, Callable[[str], Any]] = {
    "int": int,
    "float": float,
    "str": str,
    "path": str,
}


class App:
    """Aplicación de escritorio/navegador basada en HTML + Tailwind."""

    def __init__(
        self,
        *args: Any,
        title: str = "interui",
        theme: str = "light",
        width: int = 1180,
        height: int = 780,
        dev: bool = False,
        verbose: bool = False,
        max_upload_mb: int = 64,
        data_dir: str | Path | None = None,
        menus: list[Any] | None = None,
        resizable: bool = True,
        frameless: bool = False,
    ) -> None:
        if args:
            title = str(args[0])
        self.title = title
        self.theme = theme
        self.width = width
        self.height = height
        self.dev = dev or bool(os.environ.get("INTERUI_DEV"))
        self.verbose = verbose
        self.max_upload_bytes = max_upload_mb * 1024 * 1024

        self._routes: list[tuple[str, re.Pattern[str], Callable[..., Any], str | None, list[tuple[str, str]]]] = []
        self._state: dict[str, Any] = {}
        self._signals: dict[str, Signal] = {}
        self._bindings: dict[str, dict[str, dict[str, Callable[..., Any]]]] = {}
        self._client_pages: dict[str, str] = {}
        self._lock = threading.RLock()
        self._in_handler = False

        self.upload_dir = Path(tempfile.gettempdir()) / "interui-uploads"
        self.upload_dir.mkdir(parents=True, exist_ok=True)

        self.server: Server | None = None
        self.resizable = resizable
        self.frameless = frameless
        self.menus = list(menus or [])
        self._on_start: list[Callable[[], None]] = []
        self._on_close: list[Callable[[], Any]] = []
        self._desktop: DesktopWindow | None = None
        self._native = Native(self)
        self.data_dir = Path(data_dir) if data_dir else _default_data_dir(self.title)
        log_file(self.data_dir / "interui.log")

    # ------------------------------------------------------------------
    # rutas
    # ------------------------------------------------------------------
    def page(self, path: str = "/", *, title: str | None = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Registra una vista. ``<int:id>`` produce parámetros tipados."""

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            params: list[tuple[str, str]] = [(m.group("name"), m.group("kind") or "str") for m in _PARAM.finditer(path)]
            regex = re.compile("^" + _PARAM.sub(lambda m: f"(?P<{m.group('name')}>[^/]+)", path) + "$")
            self._routes.append((path, regex, func, title, params))
            return func

        return decorator

    def has_page(self, route: str) -> bool:
        return self._resolve(route) is not None

    def _resolve(self, route: str) -> tuple[Callable[..., Any], dict[str, Any], str | None] | None:
        candidate = route.rstrip("/") or "/"
        for _path, regex, func, title, params in self._routes:
            match = regex.match(candidate) or regex.match(route)
            if not match:
                continue
            values: dict[str, Any] = {}
            for name, kind in params:
                caster = _TYPES.get(kind, str)
                values[name] = caster(match.group(name))
            return func, values, title
        return None

    @property
    def routes(self) -> list[str]:
        return [path for path, *_ in self._routes]

    # ------------------------------------------------------------------
    # estado
    # ------------------------------------------------------------------
    def state(self, name: str, default: Any = None) -> Signal:
        if name not in self._signals:
            self._signals[name] = Signal(self, name, default)
            self._state.setdefault(name, default)
        return self._signals[name]

    def set_state(self, name: str, value: Any) -> None:
        self.state(name).set(value)

    def get_state(self, name: str, default: Any = None) -> Any:
        return self._state.get(name, default)

    def schedule_refresh(self) -> None:
        """Re-renderiza; si se llama fuera de un handler lo hace de inmediato."""
        if self._in_handler:
            return
        threading.Thread(target=self.refresh, name="interui-refresh", daemon=True).start()

    # ------------------------------------------------------------------
    # render
    # ------------------------------------------------------------------
    def render_page(self, route: str) -> tuple[str, str, dict[str, dict[str, Callable[..., Any]]]]:
        resolved = self._resolve(route)
        if resolved is None:
            raise LookupError(f"Ruta no registrada: {route}")
        func, params, title = resolved
        ctx = RenderContext(self, page=route)
        result = func(**params)
        page_title = title or self.title
        if isinstance(result, tuple) and len(result) == 2:
            page_title, result = str(result[0]), result[1]
        if isinstance(result, Component):
            html = result.render(ctx, "app")
        elif result is None:
            html = ""
        else:
            html = escape(result)
        return page_title, f'<div id="iui-root" data-iui-page="{escape(route)}">{html}</div>', ctx.bindings

    def error_html(self, exc: BaseException) -> str:
        detail = traceback.format_exc()
        return (
            "<!doctype html><html><head><meta charset='utf-8'><title>interui - error</title></head>"
            "<body style='font-family:ui-monospace,monospace;padding:2rem;background:#0f172a;color:#e2e8f0'>"
            f"<h1 style='color:#fb7185'>{escape(type(exc).__name__)}: {escape(exc)}</h1>"
            f"<pre style='white-space:pre-wrap'>{escape(detail)}</pre></body></html>"
        )

    def bootstrap_html(self, route: str) -> str:
        title, body, bindings = self.render_page(route)
        shell = (STATIC_DIR / "shell.html").read_text(encoding="utf-8")
        try:
            version = str(int((STATIC_DIR / "app.css").stat().st_mtime))
        except OSError:
            version = "0"
        config = {
            "page": route,
            "title": title,
            "theme": self.theme,
            "dev": self.dev,
            "app": self.title,
        }
        return (
            shell.replace("%%TITLE%%", escape(title))
            .replace("%%THEME%%", escape(self.theme))
            .replace("%%CONFIG%%", json.dumps(config, ensure_ascii=False))
            .replace("%%VERSION%%", version)
            .replace("%%CONTENT%%", body)
        )

    def _push_render(self, ws: WebSocket) -> None:
        route = self._client_pages.get(ws.id, "/")
        try:
            title, body, bindings = self.render_page(route)
        except Exception as exc:  # noqa: BLE001
            self._bindings[ws.id] = {}
            ws.send_json(
                {
                    "t": "crash",
                    "message": f"{type(exc).__name__}: {exc}",
                    "detail": traceback.format_exc(),
                }
            )
            return
        with self._lock:
            self._bindings[ws.id] = bindings
        ws.send_json(
            {
                "t": "render",
                "html": body,
                "title": title,
                "page": route,
                "theme": self.theme,
            }
        )

    def refresh(self) -> None:
        """Re-renderiza todas las vistas conectadas."""
        if self.server is None:
            return
        for ws in list(self.server.clients):
            if ws.alive:
                self._push_render(ws)

    # ------------------------------------------------------------------
    # mensajes del cliente
    # ------------------------------------------------------------------
    def on_client_connect(self, ws: WebSocket) -> None:
        with self._lock:
            self._client_pages.setdefault(ws.id, "/")
        ws.send_json({"t": "ready", "app": self.title, "theme": self.theme})
        self._push_render(ws)
        if self._desktop is not None:
            # La ventana se creó oculta: se muestra con el primer render listo.
            self._desktop.reveal_when_ready()

    def on_client_disconnect(self, ws: WebSocket) -> None:
        with self._lock:
            self._bindings.pop(ws.id, None)
            self._client_pages.pop(ws.id, None)

    def handle_message(self, ws: WebSocket, message: dict[str, Any]) -> None:
        kind = message.get("t")
        if kind == "hello":
            with self._lock:
                self._client_pages[ws.id] = message.get("page") or "/"
            self._push_render(ws)
            return
        if kind == "nav":
            target = str(message.get("path") or "/")
            if not self.has_page(target):
                ws.send_json({"t": "toast", "level": "error", "message": f"Ruta inexistente: {target}"})
                return
            with self._lock:
                self._client_pages[ws.id] = target
            self._push_render(ws)
            return
        if kind == "ping":
            ws.send_json({"t": "pong"})
            return
        if kind == "event":
            self._dispatch(ws, message)
            return

    def _dispatch(self, ws: WebSocket, message: dict[str, Any]) -> None:
        uid = str(message.get("id") or "")
        event_name = str(message.get("e") or "click")
        handlers = self._bindings.get(ws.id, {}).get(uid, {})
        handler = handlers.get(event_name) or handlers.get("*")
        files = [
            Attachment(
                name=str(item.get("name")),
                size=int(item.get("size") or 0),
                mime=str(item.get("mime") or ""),
                path=str(item.get("path") or ""),
                url=str(item.get("url") or ""),
            )
            for item in (message.get("files") or [])
        ]
        event = UIEvent(
            id=uid,
            event=event_name,
            value=message.get("v"),
            checked=message.get("checked"),
            key=message.get("key"),
            mods=message.get("mods") or {},
            files=files,
            data=message.get("data") or {},
            target=message.get("target"),
        )
        if handler is not None:
            self._in_handler = True
            try:
                invoke(handler, event)
            except Exception as exc:  # noqa: BLE001
                detail = traceback.format_exc()
                if self.verbose:
                    log(detail, error=True)
                ws.send_json({"t": "toast", "level": "error", "message": f"{type(exc).__name__}: {exc}"})
            finally:
                self._in_handler = False
        self._push_render(ws)

    # ------------------------------------------------------------------
    # escritorio
    # ------------------------------------------------------------------
    @property
    def native(self) -> Native:
        """Acceso a diálogos, notificaciones y controles de ventana."""
        return self._native

    def on_close(self, func: Callable[[], Any]) -> Callable[[], Any]:
        """Registra un hook que se ejecuta al cerrarse la ventana."""
        self._on_close.append(func)
        if self._desktop is not None:
            self._desktop.on_closing(func)
        return func

    def _shutdown(self) -> None:
        for hook in self._on_close:
            try:
                hook()
            except Exception:  # noqa: BLE001
                if self.verbose:
                    traceback.print_exc()
        if self.server is not None:
            self.server.stop()
            self.server = None

    # ------------------------------------------------------------------
    # utilidades para el usuario
    # ------------------------------------------------------------------
    def notify(self, message: str, level: str = "info") -> None:
        if self.server is not None:
            self.server.broadcast({"t": "toast", "message": message, "level": level})

    def navigate(self, path: str) -> None:
        if self.server is not None:
            self.server.broadcast({"t": "nav", "path": path})

    def eval_js(self, code: str) -> None:
        if self.server is not None:
            self.server.broadcast({"t": "eval", "js": code})

    def on_start(self, func: Callable[[], None]) -> Callable[[], None]:
        self._on_start.append(func)
        return func

    # ------------------------------------------------------------------
    # ejecución
    # ------------------------------------------------------------------
    def run(
        self,
        window: str = "desktop",
        *,
        port: int = 0,
        host: str = "127.0.0.1",
        debug: bool = False,
        gui: str | None = None,
        on_top: bool = False,
    ) -> None:
        """Abre la aplicación en una ventana nativa de escritorio.

        ``window`` acepta ``"desktop"`` (ventana nativa, por defecto),
        ``"browser"`` (navegador del sistema, útil para depurar) o ``"none"``
        (solo servidor, útil para pruebas).
        """
        if not self._routes:
            raise RuntimeError("Registra al menos una página con @app.page(...)")
        if window == "auto":
            window = "desktop"
        if window not in ("desktop", "browser", "none"):
            raise ValueError("window debe ser 'desktop', 'browser' o 'none'")

        if window == "desktop" and not desktop_available():
            log(
                '[interui] pywebview no está disponible: pip install "interui[desktop]".\n'
                "[interui] Abriendo en el navegador como alternativa.",
                error=True,
            )
            window = "browser"

        self.server = Server(self, host, port)
        self.server.start()
        url = self.server.url
        if not (STATIC_DIR / "app.css").exists():
            log("[interui] aviso: falta interui/static/app.css; ejecuta `npm run build` en frontend/", error=True)

        for hook in self._on_start:
            hook()

        log(f"[interui] {self.title} -> {url}")
        try:
            if window == "desktop":
                self._desktop = DesktopWindow(self)
                for hook in self._on_close:
                    self._desktop.on_closing(hook)
                self._desktop.create(url, debug=debug, on_top=on_top)
                # La ventana se crea visible; este temporizador solo cubre el caso
                # de que ninguna vista llegue a conectarse (p. ej. fallo de red).
                threading.Timer(4.0, self._desktop.reveal_when_ready).start()
                self._desktop.start(debug=debug, gui=gui)
            elif window == "browser":
                webbrowser.open(url)
                while True:
                    time.sleep(0.5)
            else:
                while True:
                    time.sleep(0.5)
        except KeyboardInterrupt:
            log("\n[interui] cerrando…")
        except DesktopError as exc:
            log(f"[interui] {exc}", error=True)
            raise
        finally:
            self._shutdown()
            self._desktop = None


def _default_data_dir(title: str) -> Path:
    """Directorio de datos por aplicación (registro webview, caché, ajustes)."""
    override = os.environ.get("INTERUI_DATA_DIR")
    if override:
        base = Path(override).expanduser()
    else:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "app"
        system = platform.system()
        if system == "Darwin":
            base = Path.home() / "Library" / "Application Support" / slug
        elif system == "Windows":
            base = Path(os.environ.get("APPDATA", Path.home())) / slug
        else:
            base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")) / slug
    try:
        base.mkdir(parents=True, exist_ok=True)
    except OSError:
        # Directorio de solo lectura: se sigue usando para rutas, sin datos persistidos.
        pass
    return base
