"""Ventana de escritorio nativa y puente con el sistema operativo.

``interui`` no es un framework web: la aplicación corre en una ventana nativa
(WebKit en macOS, WebView2 en Windows, WebKitGTK en Linux) servida desde un
proceso local que muere al cerrar la ventana. Este módulo encapsula todo lo que
toca el sistema operativo:

* creación y control de la ventana (tamaño, título, foco, pantalla completa),
* diálogos nativos de archivo/carpeta sin congelar la interfaz,
* notificaciones y portapapeles en las tres plataformas,
* apertura de enlaces externos en el navegador del sistema,
* puente ``window.pywebview.api`` para llamar a Python desde JavaScript.

El mismo archivo funciona en macOS, Windows y Linux: cada rama está aislada por
``platform.system()`` y solo importa bibliotecas del sistema cuando corresponde.
"""

from __future__ import annotations

import base64
import platform
import re
import shutil
import subprocess
import sys
import threading
from pathlib import Path
from typing import Any, Callable, Sequence

__all__ = [
    "DesktopError", "DesktopWindow", "Native", "NativeBridge",
    "available", "desktop_info",
]


class DesktopError(RuntimeError):
    """La ventana nativa o una función del sistema no está disponible."""


# ---------------------------------------------------------------------------
# Disponibilidad
# ---------------------------------------------------------------------------
def _webview() -> Any:
    try:
        import webview  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001 - ImportError o backend roto
        raise DesktopError(
            "No se pudo cargar la ventana nativa (pywebview).\n"
            '  Instálalo con: pip install "interui[desktop]"\n'
            f"  Detalle: {exc}"
        ) from exc
    return webview


def available() -> bool:
    """``True`` si la ventana nativa puede abrirse en esta máquina."""
    try:
        _webview()
    except DesktopError:
        return False
    return True


def desktop_info() -> dict[str, Any]:
    """Diagnóstico usado por ``interui doctor``."""
    info: dict[str, Any] = {
        "python": sys.version.split()[0],
        "platform": f"{platform.system()} {platform.release()}",
        "pywebview": False,
        "backend": None,
        "requirements": _requirements_hint(),
    }
    try:
        import webview  # noqa: F401

        info["pywebview"] = True
        info["backend"] = {
            "Darwin": "WebKit (Cocoa)",
            "Windows": "WebView2 (Chromium)",
            "Linux": "WebKitGTK",
        }.get(platform.system(), "desconocido")
    except Exception:  # noqa: BLE001
        info["pywebview"] = False
    return info


def _requirements_hint() -> str:
    """Qué necesita el sistema operativo para mostrar la ventana."""
    system = platform.system()
    if system == "Darwin":
        return "incluido en macOS (WebKit); no requiere instalación adicional"
    if system == "Windows":
        return "WebView2 Runtime (preinstalado en Windows 10/11 actualizados)"
    if system == "Linux":
        return "GTK 3 + WebKitGTK 4.1 (apt install libgtk-3-0 libwebkit2gtk-4.1-0)"
    return "sin información para esta plataforma"


def _enum(name: str) -> Any:
    """``webview.FileDialog.OPEN`` con respaldo a las constantes antiguas."""
    webview = _webview()
    dialog = getattr(webview, "FileDialog", None)
    if dialog is not None:
        return getattr(dialog, name)
    return getattr(webview, f"{name}_DIALOG")


_EXTENSION = re.compile(r"\*\.([A-Za-z0-9_+-]+)")


def _extensions(file_types: Sequence[str] | None) -> list[str]:
    """Extrae extensiones de filtros como ``"Texto (*.txt;*.md)"``."""
    out: list[str] = []
    for spec in file_types or ():
        for extension in _EXTENSION.findall(str(spec)):
            if extension not in out:
                out.append(extension)
    return out


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _version() -> str:
    try:
        from . import __version__

        return __version__
    except Exception:  # noqa: BLE001  # pragma: no cover
        return "0"


def _applescript(text: str) -> str:
    escaped = str(text).replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


# ---------------------------------------------------------------------------
# Portapapeles: macOS / Windows / Linux (Wayland y X11)
# ---------------------------------------------------------------------------
def _run_with_input(command: list[str], data: bytes) -> bool:
    try:
        subprocess.run(command, input=data, check=True, timeout=5)
        return True
    except (OSError, subprocess.SubprocessError):
        return False


def _run_capture(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, check=True, timeout=5)
        output = result.stdout
        return output.decode("utf-8", errors="replace") if isinstance(output, bytes) else str(output)
    except (OSError, subprocess.SubprocessError):
        return ""


def _win_clipboard_write(text: str) -> bool:  # pragma: no cover - solo Windows
    """Portapapeles Unicode vía ``ctypes`` (sin depender de ``clip.exe``)."""
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        data = str(text).encode("utf-16-le") + b"\x00\x00"

        kernel32.GlobalAlloc.restype = wintypes.HGLOBAL
        kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
        kernel32.GlobalLock.restype = wintypes.LPVOID
        kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        if not handle:
            return False
        pointer = kernel32.GlobalLock(handle)
        if not pointer:
            kernel32.GlobalFree(handle)
            return False
        ctypes.memmove(pointer, data, len(data))
        kernel32.GlobalUnlock(handle)

        if not user32.OpenClipboard(None):
            return False
        try:
            user32.EmptyClipboard()
            user32.SetClipboardData(CF_UNICODETEXT, handle)
        finally:
            user32.CloseClipboard()
        return True
    except Exception:  # noqa: BLE001
        return False


def _win_clipboard_read() -> str:  # pragma: no cover - solo Windows
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        CF_UNICODETEXT = 13
        kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
        kernel32.GlobalLock.restype = wintypes.LPCWSTR
        kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]

        if not user32.OpenClipboard(None):
            return ""
        try:
            handle = user32.GetClipboardData(CF_UNICODETEXT)
            if not handle:
                return ""
            pointer = kernel32.GlobalLock(handle)
            if not pointer:
                return ""
            try:
                return ctypes.wstring_at(pointer)
            finally:
                kernel32.GlobalUnlock(handle)
        finally:
            user32.CloseClipboard()
    except Exception:  # noqa: BLE001
        return ""


# ---------------------------------------------------------------------------
# Puente expuesto al JavaScript (window.pywebview.api.*)
# ---------------------------------------------------------------------------
class NativeBridge:
    """Métodos invocables desde JS con ``await interui.native.*``."""

    def __init__(self, desktop: "DesktopWindow") -> None:
        self._desktop = desktop

    def save_file(self, name: str, content: str, encoding: str = "utf-8") -> dict[str, Any]:
        return self._desktop.save_file(name, content, encoding=encoding)

    def open_file(self, multiple: bool = False, file_types: Sequence[str] | None = None) -> dict[str, Any]:
        return self._desktop.open_file(multiple=multiple, file_types=file_types)

    def pick_folder(self) -> dict[str, Any]:
        return self._desktop.pick_folder()

    def reveal(self, path: str) -> bool:
        return self._desktop.reveal(path)

    def set_title(self, title: str) -> bool:
        self._desktop.set_title(title)
        return True

    def minimize(self) -> bool:
        self._desktop.minimize()
        return True

    def toggle_maximize(self) -> bool:
        return self._desktop.toggle_maximize()

    def toggle_fullscreen(self) -> bool:
        self._desktop.toggle_fullscreen()
        return True

    def close(self) -> bool:
        threading.Thread(target=self._desktop.close, name="interui-close", daemon=True).start()
        return True

    def set_always_on_top(self, value: bool = True) -> bool:
        self._desktop.set_always_on_top(value)
        return True

    def notify(self, title: str, message: str = "") -> bool:
        return self._desktop.notify(title, message)

    def open_external(self, url: str) -> bool:
        return self._desktop.open_external(url)

    def clipboard_write(self, text: str) -> bool:
        return self._desktop.clipboard_write(text)

    def clipboard_read(self) -> str:
        return self._desktop.clipboard_read()

    def info(self) -> dict[str, Any]:
        return self._desktop.info()


# ---------------------------------------------------------------------------
# Ventana nativa
# ---------------------------------------------------------------------------
class DesktopWindow:
    """Envoltorio de la ventana nativa con acceso al ciclo de vida."""

    def __init__(self, app: Any) -> None:
        self.app = app
        self.window: Any = None
        self.webview: Any = None
        self._visible = False
        self._maximized = False
        self._closing_hooks: list[Callable[[], Any]] = []

    # -- ciclo de vida ---------------------------------------------------
    def create(self, url: str, *, debug: bool = False, on_top: bool = False) -> Any:
        webview = _webview()
        self.webview = webview
        app = self.app
        (Path(app.data_dir) / "webview").mkdir(parents=True, exist_ok=True)

        self.window = webview.create_window(
            app.title,
            url,
            js_api=NativeBridge(self),
            width=app.width,
            height=app.height,
            min_size=(min(480, app.width), min(360, app.height)),
            resizable=app.resizable,
            frameless=app.frameless,
            easy_drag=app.frameless,
            hidden=False,
            on_top=on_top,
            confirm_close=False,
            background_color="#f8fafc" if app.theme != "dark" else "#020617",
            text_select=True,
            zoomable=True,
            menu=list(getattr(app, "menus", []) or []),
        )
        self.window.events.closing += self._on_closing
        self._visible = True
        return self.window

    def start(self, debug: bool = False, gui: str | None = None) -> None:
        if self.window is None:
            raise DesktopError("La ventana no se ha creado todavía.")
        kwargs: dict[str, Any] = {
            "debug": debug,
            "private_mode": False,
            "storage_path": str(Path(self.app.data_dir) / "webview"),
        }
        if gui:
            # windows: "edgechromium" | "cef" | "mshtml"; linux: "gtk" | "qt"
            kwargs["gui"] = gui
        self.webview.start(**kwargs)

    def reveal_when_ready(self) -> None:
        """Muestra la ventana si aún está oculta (red de seguridad)."""
        if self._visible or self.window is None:
            return
        self._visible = True
        try:
            self.window.show()
        except Exception:  # noqa: BLE001 - la ventana pudo cerrarse
            pass

    def on_closing(self, hook: Callable[[], Any]) -> Callable[[], Any]:
        self._closing_hooks.append(hook)
        return hook

    def _on_closing(self) -> None:
        for hook in self._closing_hooks:
            try:
                hook()
            except Exception:  # noqa: BLE001
                if getattr(self.app, "verbose", False):
                    import traceback

                    traceback.print_exc()

    # -- archivos --------------------------------------------------------
    def _require(self) -> Any:
        if self.window is None:
            raise DesktopError("No hay ninguna ventana de escritorio activa.")
        return self.window

    def open_file(self, *, multiple: bool = False, file_types: Sequence[str] | None = None) -> dict[str, Any]:
        self._require()
        paths = self._dialog("open", multiple=multiple, file_types=file_types)
        files: list[dict[str, Any]] = []
        for path in paths:
            try:
                size = Path(path).stat().st_size
            except OSError:
                size = 0
            files.append(
                {
                    "name": Path(path).name,
                    "path": path,
                    "size": size,
                    "mime": "",
                    "url": Path(path).as_uri(),
                }
            )
        return {"files": files, "cancelled": not files}

    def save_file(self, name: str, content: str, *, encoding: str = "utf-8") -> dict[str, Any]:
        self._require()
        paths = self._dialog("save", save_name=name)
        if not paths:
            return {"cancelled": True, "path": None}
        path = Path(paths[0])
        data = base64.b64decode(content) if encoding == "base64" else content.encode("utf-8")
        path.write_bytes(data)
        return {"cancelled": False, "path": str(path), "size": len(data)}

    def pick_folder(self) -> dict[str, Any]:
        self._require()
        paths = self._dialog("folder")
        return {"path": paths[0] if paths else None, "cancelled": not paths}

    # -- diálogos --------------------------------------------------------
    def _dialog(
        self,
        kind: str,
        *,
        multiple: bool = False,
        file_types: Sequence[str] | None = None,
        save_name: str = "",
    ) -> list[str]:
        """Abre un diálogo nativo sin congelar la ventana.

        En macOS se usa una *sheet* anclada a la ventana: aparece encima de la
        app y el bucle de eventos sigue vivo. El ``runModal`` de pywebview
        bloquea el bucle principal y, si el panel queda detrás de la ventana, la
        aplicación parece colgada. En Windows y Linux se usa el diálogo nativo
        de pywebview en un hilo propio.
        """
        if platform.system() == "Darwin":
            try:
                return self._dialog_macos(
                    kind, multiple=multiple, file_types=file_types, save_name=save_name
                )
            except Exception:  # noqa: BLE001 - sin PyObjC se usa la vía genérica
                if getattr(self.app, "verbose", False):
                    import traceback

                    traceback.print_exc()
        return self._dialog_webview(
            kind, multiple=multiple, file_types=file_types, save_name=save_name
        )

    def _dialog_webview(
        self,
        kind: str,
        *,
        multiple: bool,
        file_types: Sequence[str] | None,
        save_name: str,
    ) -> list[str]:
        dialog_type = {"open": _enum("OPEN"), "save": _enum("SAVE"), "folder": _enum("FOLDER")}[kind]
        kwargs: dict[str, Any] = {
            "allow_multiple": bool(multiple),
            "file_types": tuple(file_types or ()),
        }
        if kind == "save":
            kwargs["save_filename"] = save_name

        result: dict[str, Any] = {}

        def run() -> None:
            try:
                result["paths"] = self.window.create_file_dialog(dialog_type, **kwargs)
            except Exception as exc:  # noqa: BLE001
                result["error"] = exc

        worker = threading.Thread(target=run, name="interui-dialog", daemon=True)
        worker.start()
        worker.join()
        if "error" in result:
            raise DesktopError(f"El diálogo nativo falló: {result['error']}")
        return [str(path) for path in _as_list(result.get("paths"))]

    def _dialog_macos(
        self,
        kind: str,
        *,
        multiple: bool,
        file_types: Sequence[str] | None,
        save_name: str,
    ) -> list[str]:  # pragma: no cover - solo macOS
        from AppKit import NSApp, NSOpenPanel, NSSavePanel
        from PyObjCTools import AppHelper

        done = threading.Event()
        payload: dict[str, list[str]] = {"paths": []}

        def show() -> None:
            if kind == "save":
                panel = NSSavePanel.savePanel()
                if save_name:
                    panel.setNameFieldStringValue_(save_name)
                if hasattr(panel, "setCanCreateDirectories_"):
                    panel.setCanCreateDirectories_(True)
            else:
                panel = NSOpenPanel.openPanel()
                panel.setCanChooseFiles_(kind == "open")
                panel.setCanChooseDirectories_(kind == "folder")
                panel.setAllowsMultipleSelection_(bool(multiple))
                extensions = _extensions(file_types)
                if extensions and hasattr(panel, "setAllowedFileTypes_"):
                    try:
                        panel.setAllowedFileTypes_(extensions)
                    except Exception:  # noqa: BLE001 - API obsoleta en macOS recientes
                        pass

            def handler(response: int) -> None:
                try:
                    if response == 1:  # NSModalResponseOK
                        urls = [panel.URL()] if kind == "save" else list(panel.URLs() or [])
                        payload["paths"] = [str(url.path()) for url in urls if url is not None]
                finally:
                    done.set()

            NSApp.activateIgnoringOtherApps_(True)
            host = self._ns_window()
            if host is not None:
                panel.beginSheetModalForWindow_completionHandler_(host, handler)
            else:
                panel.beginWithCompletionHandler_(handler)

        AppHelper.callAfter(show)
        if not done.wait(timeout=900):
            return []
        return payload["paths"]

    def _ns_window(self) -> Any:
        """NSWindow real de la ventana (solo macOS).

        ``pywebview`` no expone el ``NSWindow`` en ``Window``: vive en la
        instancia del backend, indexada por ``uid``. Sin esta referencia el
        diálogo no puede anclarse como *sheet* y aparece detrás de la app.
        """
        if platform.system() != "Darwin" or self.window is None:
            return None
        try:
            from webview.platforms import cocoa

            view = cocoa.BrowserView.instances.get(getattr(self.window, "uid", ""))
            return getattr(view, "window", None) if view is not None else None
        except Exception:  # noqa: BLE001 - backend distinto o sin PyObjC
            return None

    def reveal(self, path: str) -> bool:
        target = Path(path)
        try:
            if platform.system() == "Darwin":
                subprocess.Popen(["open", "-R", str(target)])
            elif platform.system() == "Windows":
                subprocess.Popen(["explorer", f"/select,{target}"])
            else:
                subprocess.Popen(["xdg-open", str(target.parent)])
            return True
        except OSError:
            return False

    # -- ventana ---------------------------------------------------------
    def set_title(self, title: str) -> None:
        self._require().set_title(title)
        self.app.title = title

    def minimize(self) -> None:
        self._require().minimize()

    def toggle_maximize(self) -> bool:
        window = self._require()
        self._maximized = not self._maximized
        if self._maximized:
            window.maximize()
        else:
            window.restore()
        return self._maximized

    def toggle_fullscreen(self) -> None:
        self._require().toggle_fullscreen()

    def close(self) -> None:
        if self.window is not None:
            self.window.destroy()

    def set_always_on_top(self, value: bool = True) -> None:
        self._require().on_top = bool(value)

    # -- sistema ---------------------------------------------------------
    def notify(self, title: str, message: str = "") -> bool:
        """Notificación del sistema en macOS, Windows y Linux."""
        system = platform.system()
        if system == "Darwin":
            try:
                script = (
                    f"display notification {_applescript(message)} "
                    f"with title {_applescript(title)}"
                )
                subprocess.Popen(
                    ["osascript", "-e", script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except OSError:
                return False
        if system == "Windows":  # pragma: no cover - solo Windows
            try:
                import ctypes

                ctypes.windll.user32.MessageBoxW(0, str(message), str(title), 0x40 | 0x10000)
                return True
            except Exception:  # noqa: BLE001
                return False
        if shutil.which("notify-send"):
            try:
                subprocess.Popen(
                    ["notify-send", str(title), str(message)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return True
            except OSError:
                return False
        if shutil.which("zenity"):
            try:
                subprocess.Popen(
                    ["zenity", "--info", f"--title={title}", f"--text={message}"],
                    stdout=subprocess.DEVNULL,
                )
                return True
            except OSError:
                return False
        return False

    def open_external(self, url: str) -> bool:
        import webbrowser

        return bool(webbrowser.open(url))

    def clipboard_write(self, text: str) -> bool:
        system = platform.system()
        if system == "Darwin":
            return _run_with_input(["pbcopy"], str(text).encode("utf-8"))
        if system == "Windows":
            return _win_clipboard_write(text)
        for command in (
            ["wl-copy"],
            ["xclip", "-selection", "clipboard"],
            ["xsel", "--clipboard", "--input"],
        ):
            if shutil.which(command[0]) and _run_with_input(command, str(text).encode("utf-8")):
                return True
        return False

    def clipboard_read(self) -> str:
        system = platform.system()
        if system == "Darwin":
            return _run_capture(["pbpaste"])
        if system == "Windows":
            return _win_clipboard_read()
        for command in (
            ["wl-paste", "--no-newline"],
            ["xclip", "-selection", "clipboard", "-o"],
            ["xsel", "--clipboard", "--output"],
        ):
            if shutil.which(command[0]):
                return _run_capture(command)
        return ""

    def info(self) -> dict[str, Any]:
        return {
            "title": self.app.title,
            "desktop": True,
            "platform": platform.system(),
            "python": sys.version.split()[0],
            "frozen": bool(getattr(sys, "frozen", False)),
            "data_dir": str(self.app.data_dir),
            "version": _version(),
        }


# ---------------------------------------------------------------------------
# Fachada para usar desde Python
# ---------------------------------------------------------------------------
class Native:
    """Acceso desde los handlers de Python al sistema operativo.

    ``app.native.save_text("datos.csv", texto)`` abre el diálogo nativo y guarda.
    """

    def __init__(self, app: Any) -> None:
        self.app = app

    @property
    def window(self) -> DesktopWindow | None:
        return getattr(self.app, "_desktop", None)

    @property
    def active(self) -> bool:
        window = self.window
        return window is not None and window.window is not None

    def _require(self) -> DesktopWindow:
        window = self.window
        if window is None:
            raise DesktopError(
                "Esta operación requiere la ventana nativa. Ejecuta app.run() e instala "
                '"interui[desktop]".'
            )
        return window

    # -- archivos --------------------------------------------------------
    def open_file(self, *, multiple: bool = False, file_types: Sequence[str] | None = None) -> dict[str, Any]:
        return self._require().open_file(multiple=multiple, file_types=file_types)

    def read_text(self, *, file_types: Sequence[str] | None = None) -> tuple[str, str] | None:
        """Abre un diálogo y devuelve ``(ruta, contenido)``, o ``None`` si se cancela."""
        result = self.open_file(file_types=file_types)
        if result["cancelled"]:
            return None
        path = result["files"][0]["path"]
        return path, Path(path).read_text(encoding="utf-8", errors="replace")

    def save_text(self, name: str, content: str) -> str | None:
        return self._require().save_file(name, content).get("path")

    def save_bytes(self, name: str, data: bytes) -> str | None:
        encoded = base64.b64encode(data).decode("ascii")
        return self._require().save_file(name, encoded, encoding="base64").get("path")

    def pick_folder(self) -> str | None:
        return self._require().pick_folder().get("path")

    def reveal(self, path: str) -> bool:
        return self._require().reveal(path)

    # -- ventana ---------------------------------------------------------
    def set_title(self, title: str) -> None:
        self._require().set_title(title)

    def minimize(self) -> None:
        self._require().minimize()

    def toggle_maximize(self) -> bool:
        return self._require().toggle_maximize()

    def toggle_fullscreen(self) -> None:
        self._require().toggle_fullscreen()

    def close(self) -> None:
        self._require().close()

    def set_always_on_top(self, value: bool = True) -> None:
        self._require().set_always_on_top(value)

    def on_closing(self, hook: Callable[[], Any]) -> Callable[[], Any]:
        return self._require().on_closing(hook)

    # -- sistema ---------------------------------------------------------
    def notify(self, title: str, message: str = "") -> bool:
        return self._require().notify(title, message)

    def open_external(self, url: str) -> bool:
        import webbrowser

        return bool(webbrowser.open(url))

    def clipboard_write(self, text: str) -> bool:
        window = self.window
        return window.clipboard_write(text) if window is not None else False

    def clipboard_read(self) -> str:
        window = self.window
        return window.clipboard_read() if window is not None else ""

    def info(self) -> dict[str, Any]:
        window = self.window
        if window is None:
            return {
                "desktop": False,
                "platform": platform.system(),
                "python": sys.version.split()[0],
            }
        return window.info()
