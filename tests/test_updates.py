"""Comprobación de actualizaciones y aviso de versión nueva."""

from __future__ import annotations

import json
import urllib.error

import pytest

import interui as ui
from interui import updates


@pytest.fixture(autouse=True)
def _sin_red(monkeypatch: pytest.MonkeyPatch) -> None:
    """Por defecto, ninguna prueba toca la red: simula «sin conexión»."""

    def offline(*_args, **_kwargs):
        raise urllib.error.URLError("sin red (pruebas)")

    monkeypatch.setattr(updates, "_fetch_json", offline)
    updates.set_override(None)
    yield
    updates.set_override(None)


class FakeSocket:
    def __init__(self) -> None:
        self.sent: list[dict] = []
        self.id = "fake"
        self.alive = True

    def send_json(self, payload: dict) -> None:
        self.sent.append(payload)

    def close(self) -> None:
        self.alive = False


# --- versiones -----------------------------------------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        ("0.3.0", (0, 3, 0)),
        ("v0.3.0", (0, 3, 0)),
        ("1.10.2", (1, 10, 2)),
        ("release-2.0", (2, 0)),
        ("sin números", (0,)),
    ],
)
def test_parse_version(value: str, expected: tuple[int, ...]) -> None:
    assert updates.parse_version(value) == expected


def test_is_newer_compara_numéricamente() -> None:
    assert updates.is_newer("0.4.0", "0.3.0")
    assert updates.is_newer("0.3.10", "0.3.9")
    assert updates.is_newer("v1.0.0", "0.99.99")
    assert not updates.is_newer("0.3.0", "0.3.0")
    assert not updates.is_newer("0.2.1", "0.3.0")


def test_current_version_es_la_del_paquete() -> None:
    assert updates.current_version() == ui.__version__


# --- comando de actualización --------------------------------------------------


def test_instalacion_desde_pypi(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates, "_direct_url", lambda: {})
    assert updates.install_info() == ("pypi", "pip install -U interui[desktop]")


def test_instalacion_desde_git(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates, "_direct_url", lambda: {"url": "https://github.com/jurdin32/interUI"})
    origin, command = updates.install_info()
    assert origin == "git"
    assert command.startswith("pip install -U ")
    assert "git+https://github.com/jurdin32/interUI.git" in command


def test_instalacion_local_en_editable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        updates,
        "_direct_url",
        lambda: {"url": "file:///tmp/mi%20copia", "dir_info": {"editable": True}},
    )
    origin, command = updates.install_info()
    assert origin == "local"
    assert "git -C" in command and "pull" in command
    assert "mi copia" in command, "la URL se decodifica"


def test_instalacion_desde_wheel_local(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    wheel = tmp_path / "interui-0.4.0-py3-none-any.whl"
    wheel.write_bytes(b"")
    # `as_uri()` arma el mismo `file:///C:/...` que escribe pip en Windows.
    monkeypatch.setattr(updates, "_direct_url", lambda: {"url": wheel.as_uri()})
    origin, command = updates.install_info()
    assert origin == "wheel"
    # El comando cita la ruta (en Windows lleva `\\` y espacios).
    assert command.startswith("pip install -U ")
    assert str(wheel) in command


def test_install_command_sin_extra(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates, "_direct_url", lambda: {})
    assert updates.install_command(with_gui=False) == "pip install -U interui"


# --- comprobación ---------------------------------------------------------------


def test_check_con_override_no_toca_la_red(monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_a, **_k):
        raise AssertionError("no debe consultar la red")

    monkeypatch.setattr(updates, "_fetch_json", boom)
    updates.set_override("9.9.9")
    info = updates.check()
    assert info is not None
    assert info.latest == "9.9.9"
    assert info.available is True
    assert info.command


def test_check_desactivado_por_entorno(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INTERUI_NO_UPDATE_CHECK", "1")
    assert updates.enabled() is False
    assert updates.check() is None


def test_check_usa_las_etiquetas_de_github(monkeypatch: pytest.MonkeyPatch) -> None:
    tags = [{"name": "v0.2.0"}, {"name": "v0.10.0"}, {"name": "v0.9.1"}]

    def fake_fetch(url, timeout):
        assert "api.github.com" in url
        return tags

    monkeypatch.setattr(updates, "_fetch_json", fake_fetch)
    info = updates.check(force=True)
    assert info is not None
    assert info.latest == "v0.10.0"
    assert info.available is True
    assert info.source == "github"


def test_check_cae_a_pypi_si_github_falla(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_fetch(url, timeout):
        if "api.github.com" in url:
            raise urllib.error.URLError("sin red")
        return {"info": {"version": "7.7.7"}}

    monkeypatch.setattr(updates, "_fetch_json", fake_fetch)
    info = updates.check(force=True)
    assert info is not None
    assert info.latest == "7.7.7"
    assert info.source == "pypi"


def test_check_devuelve_none_sin_conexion(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_fetch(url, timeout):
        raise urllib.error.URLError("sin red")

    monkeypatch.setattr(updates, "_fetch_json", fake_fetch)
    assert updates.check(force=True) is None


def test_check_reutiliza_la_cache(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "update-check.json").write_text(
        json.dumps({"checked_at": __import__("time").time(), "latest": "5.0.0"}), encoding="utf-8"
    )

    def boom(*_a, **_k):
        raise AssertionError("no debe consultar la red si hay caché")

    monkeypatch.setattr(updates, "_fetch_json", boom)
    info = updates.check(cache_dir=tmp_path)
    assert info is not None
    assert info.latest == "5.0.0"


def test_check_ignora_cache_caducada(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    (tmp_path / "update-check.json").write_text(
        json.dumps({"checked_at": 0, "latest": "5.0.0"}), encoding="utf-8"
    )
    monkeypatch.setattr(updates, "_fetch_json", lambda url, timeout: [{"name": "v6.0.0"}])
    info = updates.check(cache_dir=tmp_path, ttl=10)
    assert info is not None
    assert info.latest == "v6.0.0"


def test_check_escribe_la_cache(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates, "_fetch_json", lambda url, timeout: [{"name": "v8.0.0"}])
    updates.check(cache_dir=tmp_path, force=True)
    data = json.loads((tmp_path / "update-check.json").read_text(encoding="utf-8"))
    assert data["latest"] == "v8.0.0"
    assert data["checked_at"] > 0


def test_check_sin_cache_dir_no_falla(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates, "_fetch_json", lambda url, timeout: [{"name": "v8.0.0"}])
    assert updates.check(force=True) is not None


# --- resultado ------------------------------------------------------------------


def test_update_info_mensaje_y_payload() -> None:
    info = updates.UpdateInfo(current="0.3.0", latest="0.4.0", command="pip install -U interui")
    assert info.available is True
    assert "0.4.0" in info.message() and "0.3.0" in info.message()
    payload = info.to_payload()
    assert payload["t"] == "update"
    assert payload["latest"] == "0.4.0"
    assert payload["command"] == "pip install -U interui"
    assert payload["url"].startswith("https://github.com/jurdin32/interUI")


def test_update_info_al_dia() -> None:
    info = updates.UpdateInfo(current="0.3.0", latest="0.3.0")
    assert info.available is False
    assert "actualizado" in info.message()


# --- integración con la app -----------------------------------------------------


def test_app_avisa_al_conectarse_si_hay_version_nueva(tmp_path) -> None:
    app = ui.App("Pruebas", data_dir=tmp_path / "data")
    app.update = updates.UpdateInfo(
        current="0.3.0", latest="0.4.0", command="pip install -U interui"
    )
    assert app.update_available is True

    @app.page("/")
    def index():
        return ui.Screen(ui.Text("hola"))

    ws = FakeSocket()
    app.on_client_connect(ws)
    kinds = [message["t"] for message in ws.sent]
    assert "update" in kinds
    update_msg = next(message for message in ws.sent if message["t"] == "update")
    assert update_msg["latest"] == "0.4.0"
    assert update_msg["command"]


def test_app_sin_version_nueva_no_avisa(tmp_path) -> None:
    app = ui.App("Pruebas", data_dir=tmp_path / "data")

    @app.page("/")
    def index():
        return ui.Screen(ui.Text("hola"))

    ws = FakeSocket()
    app.on_client_connect(ws)
    assert "update" not in [message["t"] for message in ws.sent]
    assert app.update_available is False


def test_app_puede_desactivar_la_comprobacion(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(updates, "check", lambda **_k: pytest.fail("no debe consultar"))
    app = ui.App("Pruebas", data_dir=tmp_path / "data", check_updates=False)
    app.start_update_check()
    assert app._update_thread is None


def test_check_updates_now_guarda_y_emite(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        updates, "check", lambda **_k: updates.UpdateInfo(current="0.3.0", latest="0.4.0")
    )
    app = ui.App("Pruebas", data_dir=tmp_path / "data")

    class FakeServer:
        def __init__(self) -> None:
            self.broadcasted: list[dict] = []

        def broadcast(self, payload: dict) -> None:
            self.broadcasted.append(payload)

    app.server = FakeServer()
    refrescos: list[bool] = []
    app.refresh = lambda: refrescos.append(True)  # type: ignore[method-assign]

    info = app.check_updates_now()
    assert info is not None and info.available
    assert app.update_available is True
    assert app.server.broadcasted[0]["t"] == "update"
    assert refrescos == [True], "las vistas deben re-renderizarse para mostrar app.update_available"


def test_icono_de_version_nueva_en_la_interfaz(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Una vista que usa app.update_available muestra el aviso tras la comprobación."""
    monkeypatch.setattr(
        updates, "check", lambda **_k: updates.UpdateInfo(current="0.3.0", latest="0.4.0")
    )
    app = ui.App("Pruebas", data_dir=tmp_path / "data")

    @app.page("/")
    def index():
        extra = ui.Badge(f"Nueva {app.update.latest}") if app.update_available else ui.Text("al día")
        return ui.Screen(extra)

    _t, before, _b = app.render_page("/")
    assert "al día" in before
    app.check_updates_now(broadcast=False)
    _t, after, _b = app.render_page("/")
    assert "Nueva 0.4.0" in after


# --- CLI ------------------------------------------------------------------------


def test_cli_update_muestra_el_comando(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    from interui import cli

    monkeypatch.setattr(
        updates, "check", lambda **_k: updates.UpdateInfo(current="0.3.0", latest="0.4.0")
    )
    code = cli.main(["update"])
    out = capsys.readouterr().out
    assert code == 0
    assert "0.4.0" in out
    assert "pip install -U" in out


def test_cli_update_sin_conexion(monkeypatch: pytest.MonkeyPatch, capsys) -> None:
    from interui import cli

    monkeypatch.setattr(updates, "check", lambda **_k: None)
    code = cli.main(["update"])
    out = capsys.readouterr().out
    assert code == 1
    assert "No se pudo consultar" in out


def test_cli_update_run_ejecuta_el_comando(monkeypatch: pytest.MonkeyPatch) -> None:
    from interui import cli

    ejecutado: list[str] = []
    monkeypatch.setattr(
        updates, "check", lambda **_k: updates.UpdateInfo(current="0.3.0", latest="0.4.0", command="pip install -U interui")
    )
    monkeypatch.setattr(updates, "run_upgrade", lambda command: ejecutado.append(command) or 0)
    assert cli.main(["update", "--run"]) == 0
    # El comando que se ejecuta es el que corresponde a cómo está instalado.
    assert ejecutado == [updates.install_command()]

    # `--install` y `--upgrade` son sinónimos.
    assert cli.main(["update", "--install"]) == 0
    assert len(ejecutado) == 2


def test_run_upgrade_ejecuta_varios_pasos(monkeypatch: pytest.MonkeyPatch) -> None:
    """`git pull && pip install -e` se ejecuta como dos comandos, sin shell."""
    import subprocess
    import sys

    llamadas: list[list[str]] = []

    def falso(parts, *_a, **_k):
        llamadas.append(list(parts))
        return 0

    monkeypatch.setattr(subprocess, "call", falso)
    code = updates.run_upgrade('git -C "/tmp/mi copia" pull && pip install -U -e "/tmp/mi copia"')

    assert code == 0
    assert llamadas[0] == ["git", "-C", "/tmp/mi copia", "pull"]
    assert llamadas[1] == [sys.executable, "-m", "pip", "install", "-U", "-e", "/tmp/mi copia"]


def test_run_upgrade_se_para_en_el_primer_error(monkeypatch: pytest.MonkeyPatch) -> None:
    import subprocess

    llamadas: list[list[str]] = []

    def falso(parts, *_a, **_k):
        llamadas.append(list(parts))
        return 2

    monkeypatch.setattr(subprocess, "call", falso)
    assert updates.run_upgrade("git pull && pip install -U -e /tmp/x") == 2
    assert len(llamadas) == 1, "no debe seguir después de un fallo"
