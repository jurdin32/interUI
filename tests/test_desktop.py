"""Pruebas de la capa de escritorio sin abrir ventanas reales."""

from __future__ import annotations

from pathlib import Path

import pytest

import interui as ui
from interui import desktop
from interui.desktop import DesktopError, Native, NativeBridge

# La ventana nativa necesita el extra `desktop` (pywebview). Sin él, la matriz
# `test` del CI no puede ejecutar estas pruebas: se saltan y las corre la tarea
# `desktop`, que sí lo instala.
pytest.importorskip("webview", reason="necesita pywebview (extra `desktop`)")


class FakeWindow:
    def __init__(self, choice: str | None = None) -> None:
        self.choice = choice
        self.title = None
        self.minimized = False
        self.maximized = False
        self.restored = False
        self.fullscreen = False
        self.destroyed = False
        self.on_top = False
        self.dialog_calls: list[tuple] = []

    def create_file_dialog(self, dialog_type, **kwargs):
        self.dialog_calls.append((dialog_type, kwargs))
        return (self.choice,) if self.choice else None

    def set_title(self, title):
        self.title = title

    def minimize(self):
        self.minimized = True

    def maximize(self):
        self.maximized = True

    def restore(self):
        self.restored = True

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen

    def destroy(self):
        self.destroyed = True


class FakeWebview:
    OPEN_DIALOG = 10
    SAVE_DIALOG = 20
    FOLDER_DIALOG = 30


@pytest.fixture(autouse=True)
def _generic_platform(monkeypatch):
    """Fuerza la ruta de diálogo genérica: los tests no abren ventanas reales."""
    monkeypatch.setattr(desktop.platform, "system", lambda: "TestOS")


def make_desktop(tmp_path: Path, choice: str | None = None) -> desktop.DesktopWindow:
    app = ui.App("Escritorio", data_dir=tmp_path / "data")
    window = desktop.DesktopWindow(app)
    window.webview = FakeWebview()
    window.window = FakeWindow(choice)
    app._desktop = window
    return window


def test_native_requires_window(tmp_path):
    app = ui.App("Sin ventana", data_dir=tmp_path / "data")
    with pytest.raises(DesktopError):
        Native(app).open_file()


def test_native_facade_detects_window(tmp_path):
    window = make_desktop(tmp_path)
    native = Native(window.app)
    assert native.window is window
    assert native.info()["desktop"] is True


def test_open_file_reads_contents(tmp_path):
    target = tmp_path / "datos.txt"
    target.write_text("hola", encoding="utf-8")
    window = make_desktop(tmp_path, choice=str(target))
    result = Native(window.app).open_file(multiple=False)
    assert result["cancelled"] is False
    assert result["files"][0]["name"] == "datos.txt"
    assert result["files"][0]["size"] == 4
    assert result["files"][0]["path"] == str(target)


def test_read_text_returns_path_and_content(tmp_path):
    target = tmp_path / "nota.md"
    target.write_text("# hola", encoding="utf-8")
    window = make_desktop(tmp_path, choice=str(target))
    assert Native(window.app).read_text() == (str(target), "# hola")


def test_open_file_cancelled(tmp_path):
    window = make_desktop(tmp_path, choice=None)
    assert Native(window.app).open_file()["cancelled"] is True
    assert Native(window.app).read_text() is None


def test_save_text_writes_file(tmp_path):
    target = tmp_path / "salida.csv"
    window = make_desktop(tmp_path, choice=str(target))
    path = Native(window.app).save_text("salida.csv", "a,b\n1,2\n")
    assert path == str(target)
    assert target.read_text(encoding="utf-8") == "a,b\n1,2\n"


def test_save_bytes_writes_binary(tmp_path):
    target = tmp_path / "imagen.bin"
    window = make_desktop(tmp_path, choice=str(target))
    Native(window.app).save_bytes("imagen.bin", b"\x00\x01\x02")
    assert target.read_bytes() == b"\x00\x01\x02"


def test_save_cancelled_returns_none(tmp_path):
    window = make_desktop(tmp_path, choice=None)
    assert Native(window.app).save_text("x.txt", "y") is None


def test_pick_folder(tmp_path):
    window = make_desktop(tmp_path, choice=str(tmp_path))
    assert Native(window.app).pick_folder() == str(tmp_path)


def test_window_controls(tmp_path):
    window = make_desktop(tmp_path)
    native = Native(window.app)
    native.set_title("Nuevo título")
    assert window.window.title == "Nuevo título"
    assert window.app.title == "Nuevo título"
    native.minimize()
    assert window.window.minimized
    assert native.toggle_maximize() is True
    assert window.window.maximized
    assert native.toggle_maximize() is False
    assert window.window.restored
    native.toggle_fullscreen()
    assert window.window.fullscreen
    native.set_always_on_top(True)
    assert window.window.on_top
    native.close()
    assert window.window.destroyed


def test_closing_hooks_run_on_close(tmp_path):
    window = make_desktop(tmp_path)
    fired: list[str] = []
    window.on_closing(lambda: fired.append("hook"))
    window._on_closing()
    assert fired == ["hook"]


def test_bridge_methods_are_json_ready(tmp_path):
    target = tmp_path / "b.txt"
    window = make_desktop(tmp_path, choice=str(target))
    bridge = NativeBridge(window)
    assert bridge.set_title("T") is True
    assert bridge.minimize() is True
    assert isinstance(bridge.info(), dict)
    assert bridge.save_file("b.txt", "contenido")["size"] == len("contenido")
    assert target.read_text(encoding="utf-8") == "contenido"


def test_desktop_info_shape():
    info = desktop.desktop_info()
    assert {"python", "platform", "pywebview", "backend"} <= set(info)


def test_saved_bytes_use_base64_in_bridge(tmp_path):
    import base64

    target = tmp_path / "c.bin"
    window = make_desktop(tmp_path, choice=str(target))
    payload = base64.b64encode(b"abc").decode("ascii")
    bridge = NativeBridge(window)
    assert bridge.save_file("c.bin", payload, encoding="base64")["cancelled"] is False
    assert target.read_bytes() == b"abc"
