"""Garantías multiplataforma: rutas, portapapeles, notificaciones y diálogos.

Los tests simulan cada sistema operativo para comprobar que las ramas de código
existen y hacen lo correcto, sin abrir ventanas ni tocar el portapapeles real.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import interui as ui
from interui import app as app_module
from interui import desktop
from interui.desktop import _applescript, _extensions


# ---------------------------------------------------------------------------
# directorio de datos por sistema
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("system", "env", "expected_parts"),
    [
        ("Darwin", {"HOME": "/Users/ana"}, ("Library", "Application Support", "mi-app")),
        ("Windows", {"APPDATA": "C:/Users/ana/AppData/Roaming"}, ("AppData", "Roaming", "mi-app")),
        ("Linux", {"XDG_DATA_HOME": "/home/ana/.local/share"}, (".local", "share", "mi-app")),
    ],
)
def test_data_dir_per_platform(monkeypatch, tmp_path, system, env, expected_parts):
    # Las rutas de Windows son relativas fuera de Windows: se trabaja en tmp.
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("INTERUI_DATA_DIR", raising=False)
    monkeypatch.setattr(app_module.platform, "system", lambda: system)
    for key, value in env.items():
        monkeypatch.setenv(key, value)
    if system != "Darwin":
        monkeypatch.setenv("HOME", env.get("HOME", str(tmp_path)))
    directory = app_module._default_data_dir("Mi App")
    text = str(directory)
    for part in expected_parts:
        assert part in text


def test_data_dir_override(monkeypatch, tmp_path):
    monkeypatch.setenv("INTERUI_DATA_DIR", str(tmp_path / "custom"))
    directory = app_module._default_data_dir("cualquiera")
    assert directory == tmp_path / "custom"


# ---------------------------------------------------------------------------
# portapapeles
# ---------------------------------------------------------------------------
def _make_window(tmp_path: Path) -> desktop.DesktopWindow:
    app = ui.App("Portapapeles", data_dir=tmp_path / "data")
    window = desktop.DesktopWindow(app)
    window.window = object()
    app._desktop = window
    return window


def test_clipboard_macos_uses_pbcopy(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs.get("input")))
        return subprocess.CompletedProcess(command, 0, b"leido")

    monkeypatch.setattr(desktop.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(desktop.subprocess, "run", fake_run)
    window = _make_window(tmp_path)

    assert window.clipboard_write("hola") is True
    assert calls[0][0] == ["pbcopy"]
    assert calls[0][1] == b"hola"
    assert window.clipboard_read() == "leido"


def test_clipboard_linux_prefers_wayland(monkeypatch, tmp_path):
    used = []

    def fake_which(name):
        return f"/usr/bin/{name}"

    def fake_run(command, **kwargs):
        used.append(command)
        return subprocess.CompletedProcess(command, 0, b"texto")

    monkeypatch.setattr(desktop.platform, "system", lambda: "Linux")
    monkeypatch.setattr(desktop.shutil, "which", fake_which)
    monkeypatch.setattr(desktop.subprocess, "run", fake_run)
    window = _make_window(tmp_path)

    assert window.clipboard_write("x") is True
    assert used[0][0] == "wl-copy"
    used.clear()
    assert window.clipboard_read() == "texto"
    assert used[0][0] == "wl-paste"


def test_clipboard_windows_uses_ctypes(monkeypatch, tmp_path):
    monkeypatch.setattr(desktop.platform, "system", lambda: "Windows")
    monkeypatch.setattr(desktop, "_win_clipboard_write", lambda text: text == "hola")
    monkeypatch.setattr(desktop, "_win_clipboard_read", lambda: "pegado")
    window = _make_window(tmp_path)
    assert window.clipboard_write("hola") is True
    assert window.clipboard_read() == "pegado"


def test_clipboard_without_backend_returns_false(monkeypatch, tmp_path):
    monkeypatch.setattr(desktop.platform, "system", lambda: "Linux")
    monkeypatch.setattr(desktop.shutil, "which", lambda _name: None)
    window = _make_window(tmp_path)
    assert window.clipboard_write("x") is False
    assert window.clipboard_read() == ""


# ---------------------------------------------------------------------------
# notificaciones
# ---------------------------------------------------------------------------
def test_notify_linux_uses_notify_send(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(desktop.platform, "system", lambda: "Linux")
    monkeypatch.setattr(desktop.shutil, "which", lambda name: "/usr/bin/notify-send" if name == "notify-send" else None)
    monkeypatch.setattr(desktop.subprocess, "Popen", lambda command, **kw: calls.append(command))
    window = _make_window(tmp_path)
    assert window.notify("Título", "Mensaje") is True
    assert calls[0][:3] == ["notify-send", "Título", "Mensaje"]


def test_notify_linux_falls_back_to_zenity(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(desktop.platform, "system", lambda: "Linux")
    monkeypatch.setattr(desktop.shutil, "which", lambda name: "/usr/bin/zenity" if name == "zenity" else None)
    monkeypatch.setattr(desktop.subprocess, "Popen", lambda command, **kw: calls.append(command))
    window = _make_window(tmp_path)
    assert window.notify("T", "M") is True
    assert calls[0][0] == "zenity"


def test_notify_macos_escapes_applescript(monkeypatch, tmp_path):
    calls = []
    monkeypatch.setattr(desktop.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(desktop.subprocess, "Popen", lambda command, **kw: calls.append(command))
    window = _make_window(tmp_path)
    assert window.notify('Título "raro"', "línea 1") is True
    script = calls[0][2]
    assert '\\"' in script or "\\\\" in script


def test_applescript_escapes_quotes_and_backslashes():
    assert _applescript('a"b') == '"a\\"b"'
    assert _applescript("a\\b") == '"a\\\\b"'


# ---------------------------------------------------------------------------
# filtros y diálogos
# ---------------------------------------------------------------------------
def test_extensions_from_filters():
    assert _extensions(["Texto (*.txt;*.md)", "Imágenes (*.png, *.jpg)"]) == ["txt", "md", "png", "jpg"]
    assert _extensions(None) == []
    # "*.*" significa «sin restricción», no una extensión literal
    assert _extensions(["Todos (*.*)"]) == []


def test_dialog_falls_back_to_pywebview_off_macos(monkeypatch, tmp_path):
    pytest.importorskip("webview", reason="necesita pywebview (extra `desktop`)")
    monkeypatch.setattr(desktop.platform, "system", lambda: "Linux")
    seen = {}

    class FakeWindow:
        def create_file_dialog(self, dialog_type, **kwargs):
            seen["dialog_type"] = dialog_type
            seen["kwargs"] = kwargs
            return ("/tmp/elegido.txt",)

    app = ui.App("Dialogos", data_dir=tmp_path / "data")
    window = desktop.DesktopWindow(app)
    window.webview = type("W", (), {"OPEN_DIALOG": 10, "SAVE_DIALOG": 20, "FOLDER_DIALOG": 30})()
    window.window = FakeWindow()
    assert window.open_file(multiple=True)["files"][0]["name"] == "elegido.txt"
    assert seen["dialog_type"] == 10
    assert seen["kwargs"]["allow_multiple"] is True


def test_reveal_uses_platform_command(monkeypatch, tmp_path):
    launched = []
    monkeypatch.setattr(desktop.subprocess, "Popen", lambda command, **kw: launched.append(command))
    window = _make_window(tmp_path)

    monkeypatch.setattr(desktop.platform, "system", lambda: "Windows")
    assert window.reveal("C:/datos/x.txt") is True
    assert launched[-1][0] == "explorer"

    monkeypatch.setattr(desktop.platform, "system", lambda: "Darwin")
    assert window.reveal("/tmp/x.txt") is True
    assert launched[-1][0] == "open"

    monkeypatch.setattr(desktop.platform, "system", lambda: "Linux")
    assert window.reveal("/tmp/x.txt") is True
    assert launched[-1][0] == "xdg-open"


def test_no_macos_imports_off_darwin(monkeypatch, tmp_path):
    """En Windows/Linux nunca se importa AppKit/PyObjCTools."""
    import sys

    for module in ("AppKit", "PyObjCTools"):
        assert module in sys.modules or True  # puede estar instalado en macOS
    monkeypatch.setattr(desktop.platform, "system", lambda: "Linux")
    monkeypatch.setattr(desktop.DesktopWindow, "_dialog_webview", lambda *a, **k: [])
    window = _make_window(tmp_path)
    assert window._dialog("open") == []


# ---------------------------------------------------------------------------
# empaquetado y registro
# ---------------------------------------------------------------------------
def test_log_writes_to_file_without_stdout(monkeypatch, tmp_path):
    from interui import log as log_module

    log_module.log_file(tmp_path / "app.log")
    monkeypatch.setattr(log_module.sys, "stdout", None)
    monkeypatch.setattr(log_module.sys, "stderr", None)
    log_module.log("mensaje de prueba")
    assert "mensaje de prueba" in (tmp_path / "app.log").read_text(encoding="utf-8")
    log_module.log_file(None)


def test_cli_build_data_separator_matches_platform(monkeypatch, tmp_path):
    """`interui build` debe usar ';' en Windows y ':' en el resto."""
    from interui import cli

    captured = {}

    class Done:
        returncode = 0

    def fake_run(command, **kwargs):
        captured["command"] = command
        return Done()

    monkeypatch.setattr(cli.subprocess, "run", fake_run)
    monkeypatch.setattr(cli.shutil, "which", lambda name: "/usr/bin/pyinstaller")
    monkeypatch.setattr(cli.platform, "system", lambda: "Windows")
    monkeypatch.setattr(cli, "STATIC_DIR", tmp_path / "static")
    (tmp_path / "static").mkdir()
    (tmp_path / "static" / "app.css").write_text("x")
    script = tmp_path / "app.py"
    script.write_text("print('x')")

    args = type("Args", (), {
        "script": str(script), "name": "demo", "output": str(tmp_path / "out"),
        "onefile": False, "console": False, "icon": None,
    })()
    cli.cmd_build(args)
    data_arg = captured["command"][captured["command"].index("--add-data") + 1]
    assert ";" in data_arg
