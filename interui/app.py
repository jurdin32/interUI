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
from contextvars import ContextVar
from pathlib import Path
from typing import Any, Callable

from .base import Component
from .context import RenderContext
from .desktop import (
    DesktopError, DesktopWindow, Native, Window, available as desktop_available,
)
from .events import Attachment, UIEvent, invoke
from .html import escape
from .log import log, log_file
from .server import STATIC_DIR, Server, WebSocket
from .state import Signal
from . import updates as _updates

__all__ = ["App"]

_PARAM = re.compile(r"<(?:(?P<kind>\w+):)?(?P<name>\w+)>")
_TYPES: dict[str, Callable[[str], Any]] = {
    "int": int,
    "float": float,
    "str": str,
    "path": str,
}


#: App que está ejecutando un handler en este momento. La usan los diálogos
#: (`ui.dialog.info` y compañía) para saber sobre qué ventana abrirse.
_ACTIVE_APP: ContextVar[Any] = ContextVar("interui_active_app", default=None)


def active_app() -> Any:
    """La app que está despachando un evento, o ``None`` fuera de un handler."""
    return _ACTIVE_APP.get()


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
        check_updates: bool | None = None,
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
        self._dialogs: list[Any] = []
        self._on_start: list[Callable[[], None]] = []
        self._on_close: list[Callable[[], Any]] = []
        self._desktop: DesktopWindow | None = None
        self._windows: dict[str, Window] = {}
        self._local = threading.local()
        self._stopped = False
        self._shutdown_done = False
        self._native = Native(self)
        self.check_updates = check_updates
        self.update: _updates.UpdateInfo | None = None
        self.config: Any = None
        self._update_thread: threading.Thread | None = None
        self.data_dir = Path(data_dir) if data_dir else _default_data_dir(self.title)
        log_file(self.data_dir / "interui.log")

    # ------------------------------------------------------------------
    # configuración
    # ------------------------------------------------------------------
    @classmethod
    def from_config(cls, path: "str | Path | None" = None, **overrides: Any) -> "App":
        """Crea la app con los valores de ``interui.json``.

        Deja la configuración en ``app.config`` y registra las bases de datos,
        así que ``Model`` y las migraciones funcionan sin llamar a nada más.
        """
        from . import db as db_module
        from .config import load as load_config

        settings = load_config(path)
        options = {**settings.app_options(), **overrides}
        application = cls(**options)
        application.config = settings
        db_module.configure(settings)
        return application

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
        if self._dialogs:
            from .dialogs import DialogHost

            html += DialogHost(*self._dialogs).render(ctx, "dlg")
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
        window = self._window_for(ws)
        route = window.route if window is not None else "/"
        with self._lock:
            self._client_pages.setdefault(ws.id, route)
        ws.send_json({"t": "ready", "app": self.title, "theme": self.theme})
        self._push_render(ws)
        if self.update is not None and self.update.available:
            ws.send_json(self.update.to_payload())
        if self._desktop is not None:
            # La ventana se creó oculta: se muestra con el primer render listo.
            self._desktop.reveal_when_ready()

    def on_client_disconnect(self, ws: WebSocket) -> None:
        with self._lock:
            self._bindings.pop(ws.id, None)
            self._client_pages.pop(ws.id, None)

    def handle_message(self, ws: WebSocket, message: dict[str, Any]) -> None:
        self._local.ws = ws
        try:
            self._handle_message(ws, message)
        finally:
            self._local.ws = None

    def _handle_message(self, ws: WebSocket, message: dict[str, Any]) -> None:
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
        handler = handlers.get(event_name)
        if handler is None:
            handler = handlers.get("*")
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
            token = _ACTIVE_APP.set(self)
            try:
                invoke(handler, event)
            except Exception as exc:  # noqa: BLE001
                detail = traceback.format_exc()
                if self.verbose:
                    log(detail, error=True)
                ws.send_json({"t": "toast", "level": "error", "message": f"{type(exc).__name__}: {exc}"})
            finally:
                _ACTIVE_APP.reset(token)
                self._in_handler = False
        self._push_render(ws)

    # ------------------------------------------------------------------
    # diálogos
    # ------------------------------------------------------------------
    @property
    def dialogs(self) -> list[Any]:
        """Diálogos abiertos (se pintan encima de la página actual)."""
        return list(self._dialogs)

    @property
    def blocking_dialog(self) -> Any:
        """Diálogo de primer plano abierto, si lo hay."""
        for item in reversed(self._dialogs):
            if getattr(item, "is_blocking", False):
                return item
        return None

    def show_dialog(self, component: Any, *, force: bool = False) -> Any:
        """Abre un diálogo modal encima de la vista actual.

        Mientras haya uno de primer plano (``layer=layer.blocking``) no se abre
        nada más: se devuelve el que bloquea. ``force=True`` lo salta.
        """
        blocking = self.blocking_dialog
        if blocking is not None and blocking is not component and not force:
            log("[interui] hay un diálogo de primer plano abierto: acéptalo antes", error=True)
            return blocking
        self._dialogs.append(component)
        if not self._in_handler:
            self.refresh()
        return component

    def close_dialog(self, component: Any = None) -> None:
        """Cierra un diálogo concreto o el último abierto."""
        if component is None:
            if self._dialogs and getattr(self._dialogs[-1], "is_blocking", False):
                log("[interui] un diálogo de primer plano solo se cierra aceptándolo", error=True)
                return
            if self._dialogs:
                self._dialogs.pop()
        else:
            self._dialogs = [item for item in self._dialogs if item is not component]
        if not self._in_handler:
            self.refresh()

    def close_all_dialogs(self) -> None:
        self._dialogs.clear()
        if not self._in_handler:
            self.refresh()

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
        if self._shutdown_done:
            return
        self._shutdown_done = True
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
    # ventanas
    # ------------------------------------------------------------------
    @property
    def windows(self) -> list["Window"]:
        """Ventanas abiertas, la principal primero."""
        main = self._windows.get("main")
        rest = [item for key, item in self._windows.items() if key != "main"]
        return ([main] if main is not None else []) + rest

    @property
    def main_window(self) -> "Window | None":
        """Ventana principal (``None`` antes de ``run()``)."""
        return self._windows.get("main")

    @property
    def current_window(self) -> "Window | None":
        """Ventana que está ejecutando el handler actual, o la principal."""
        ws = getattr(self._local, "ws", None)
        ident = getattr(ws, "window_id", None) if ws is not None else None
        if ident and ident in self._windows:
            return self._windows[ident]
        return self._windows.get("main")

    def _window_for(self, ws: WebSocket) -> "Window | None":
        return self._windows.get(getattr(ws, "window_id", None) or "main")

    def _forget_window(self, window: "Window") -> None:
        if self._windows.get(window.ident) is window:
            del self._windows[window.ident]

    def clients_for(self, ident: str) -> list[WebSocket]:
        """Conexiones abiertas por una ventana concreta."""
        if self.server is None:
            return []
        return [
            ws
            for ws in list(self.server.clients)
            if ws.alive and (getattr(ws, "window_id", None) or "main") == ident
        ]

    def open_window(
        self,
        route: str = "/",
        *,
        title: str | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> "Window":
        """Abre **otra** ventana nativa en ``route`` (multiventana).

        Cada ventana tiene su propio canal: se puede cerrar con
        ``ventana.close()`` sin tocar el resto ni el servidor.
        """
        if not self.has_page(route):
            raise ValueError(f"Ruta inexistente: {route}")
        if self._desktop is None or self._desktop.webview is None or self.server is None:
            raise DesktopError(
                "open_window() necesita la ventana nativa en marcha: llama antes a "
                'app.run() con window="desktop" e instala "interui[desktop]".'
            )
        ident = f"w{len(self._windows)}"
        window = Window(self, ident, title or self.title, route)
        native = DesktopWindow(self)
        try:
            native.create(
                self._url_for(route, ident),
                title=window.title,
                width=width,
                height=height,
            )
        except Exception as exc:  # noqa: BLE001 - el motor nativo puede rechazarlo
            raise DesktopError(
                f"No se pudo abrir otra ventana ({type(exc).__name__}: {exc}). "
                "Algunos motores solo permiten ventanas antes de app.run()."
            ) from exc
        window.native = native
        self._windows[ident] = window
        return window

    def _url_for(self, route: str, ident: str) -> str:
        base = self.server.url.rstrip("/") if self.server is not None else ""
        separator = "&" if "?" in route else "?"
        return f"{base}{route}{separator}w={ident}"

    # ------------------------------------------------------------------
    # utilidades para el usuario
    # ------------------------------------------------------------------
    def notify(
        self,
        message: str,
        level: str = "info",
        *,
        title: str | None = None,
        icon: Any = None,
        image: str | None = None,
        duration: int = 4200,
        action: dict[str, str] | None = None,
    ) -> None:
        """Snackbar flotante en todas las ventanas.

        ``icon`` acepta un nombre (``ui.icons.check``) o marcado SVG, ``image``
        una URL y ``action`` ``{"label": "Deshacer", "js": "…"}``. Para acciones
        en Python usa el control :class:`interui.Snackbar`.
        """
        if self.server is None:
            return
        payload: dict[str, Any] = {
            "t": "toast",
            "message": message,
            "level": level,
            "duration": duration,
        }
        if title:
            payload["title"] = str(title)
        if icon:
            payload["icon"] = _icon_markup(icon)
        if image:
            payload["image"] = str(image)
        if action:
            payload["action"] = dict(action)
        self.server.broadcast(payload)

    def navigate(self, path: str) -> None:
        if self.server is not None:
            self.server.broadcast({"t": "nav", "path": path})

    def eval_js(self, code: str) -> None:
        if self.server is not None:
            self.server.broadcast({"t": "eval", "js": code})

    # -- tres niveles de cierre ----------------------------------------
    def close(self) -> None:
        """Cierra **solo** la ventana que ejecuta el handler.

        Las demás ventanas y el servidor siguen vivos. Si era la última, la
        aplicación termina (no hay dónde mostrarse).
        """
        window = self.current_window
        if window is None:
            self.quit()
            return
        window.close()
        if not self._windows:
            self.quit()

    def dispose(self, window: "Window | None" = None) -> None:
        """Cierra y libera una ventana (la actual por defecto). No apaga la app."""
        target = window or self.current_window
        if target is None:
            self.quit()
            return
        target.dispose()
        if not self._windows:
            self.quit()

    def exit(self) -> None:
        """Cierra **todas** las ventanas y apaga el servidor."""
        self.quit()

    def quit(self) -> None:
        """Cierra todas las ventanas y detiene el servidor.

        Es seguro llamarlo desde un handler de un botón: el bucle de ``run()``
        termina en cuanto las ventanas se destruyen.
        """
        self._stopped = True
        for window in [item for item in self.windows if item.ident != "main"]:
            window.close()
        if self._desktop is not None:
            self._desktop.close()
        for window in list(self._windows.values()):
            window.close()
        if self._desktop is None and self.server is not None:
            threading.Thread(target=self._shutdown, name="interui-quit", daemon=True).start()

    def set_theme(self, theme: str = "dark") -> None:
        """Cambia el tema del cliente: ``"claro"``/``"light"`` o ``"oscuro"``/``"dark"``."""
        value = "dark" if theme.lower() in ("oscuro", "dark") else "light"
        self.theme = value
        if self.server is not None:
            self.server.broadcast({"t": "theme", "theme": value})

    def toggle_theme(self) -> str:
        """Alterna claro/oscuro y devuelve el tema activo."""
        self.set_theme("light" if self.theme == "dark" else "dark")
        return self.theme

    def on_start(self, func: Callable[[], None]) -> Callable[[], None]:
        self._on_start.append(func)
        return func

    # ------------------------------------------------------------------
    # actualizaciones
    # ------------------------------------------------------------------
    @property
    def update_available(self) -> bool:
        """``True`` si al arrancar se detectó una versión más nueva de interUI."""
        return self.update is not None and self.update.available

    def check_updates_now(self, *, broadcast: bool = True) -> _updates.UpdateInfo | None:
        """Consulta la última versión publicada (bloquea; normalmente no hace falta)."""
        info = _updates.check(cache_dir=self.data_dir)
        if info is not None and info.available:
            self.update = info
            log(f"[interui] {info.message()}\n[interui] actualizar: {info.command}")
            # Re-renderiza para que las vistas que usan app.update_available
            # (badges, banners propios) reflejen la novedad, y avisa al cliente.
            self.refresh()
            if broadcast and self.server is not None:
                self.server.broadcast(info.to_payload())
        return info

    def start_update_check(self) -> None:
        """Comprueba si hay versión nueva en segundo plano y avisa a la interfaz."""
        if self.check_updates is False or self._update_thread is not None:
            return

        def worker() -> None:
            time.sleep(1.0)  # deja que la ventana pinte antes de tocar la red
            try:
                self.check_updates_now()
            except Exception:  # noqa: BLE001 - una actualización nunca rompe la app
                if self.verbose:
                    traceback.print_exc()

        self._update_thread = threading.Thread(target=worker, name="interui-update", daemon=True)
        self._update_thread.start()

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

        server = Server(self, host, port)
        self.server = server
        server.start()
        url = server.url
        if "main" not in self._windows:
            self._windows["main"] = Window(self, "main", self.title, "/")
        if not (STATIC_DIR / "app.css").exists():
            log("[interui] aviso: falta interui/static/app.css; ejecuta `npm run build` en frontend/", error=True)

        for hook in self._on_start:
            hook()

        self.start_update_check()

        log(f"[interui] {self.title} -> {url}")
        try:
            if window == "desktop":
                self._desktop = DesktopWindow(self)
                if "main" in self._windows:
                    self._windows["main"].native = self._desktop
                for hook in self._on_close:
                    self._desktop.on_closing(hook)
                self._desktop.create(url, debug=debug, on_top=on_top)
                # La ventana se crea visible; este temporizador solo cubre el caso
                # de que ninguna vista llegue a conectarse (p. ej. fallo de red).
                threading.Timer(4.0, self._desktop.reveal_when_ready).start()
                self._desktop.start(debug=debug, gui=gui)
            elif window == "browser":
                webbrowser.open(url)
                while not self._stopped:
                    time.sleep(0.2)
            else:
                while not self._stopped:
                    time.sleep(0.2)
        except KeyboardInterrupt:
            log("\n[interui] cerrando…")
        except DesktopError as exc:
            log(f"[interui] {exc}", error=True)
            raise
        finally:
            self._shutdown()
            self._desktop = None


def _icon_markup(icon: Any) -> str:
    """SVG en línea a partir de un nombre de icono o de marcado propio."""
    text = str(icon)
    if text.lstrip().startswith("<"):
        return text
    from .icons import ICONS

    paths = ICONS.get(text)
    if paths is None:
        return ""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" '
        'stroke="currentColor" stroke-width="1.8" stroke-linecap="round" '
        f'stroke-linejoin="round" class="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true">{paths}</svg>'
    )


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
