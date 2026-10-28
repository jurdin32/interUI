"""Servidor local sin dependencias: HTTP estático + WebSocket + subida de ficheros.

Implementa el handshake y el framing de RFC 6455 sobre ``socket``/``hashlib``,
de modo que el núcleo del framework funciona con la biblioteca estándar.
"""

from __future__ import annotations

import base64
import hashlib
import json
import mimetypes
import os
import posixpath
import re
import socket
import struct
import threading
import time
import urllib.parse
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .log import log

__all__ = ["Server", "WebSocket", "encode_frame", "read_frame"]

_WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
STATIC_DIR = Path(__file__).parent / "static"

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._\- ]+")


# ---------------------------------------------------------------------------
# WebSocket (RFC 6455)
# ---------------------------------------------------------------------------
def _accept_key(key: str) -> str:
    digest = hashlib.sha1((key + _WS_GUID).encode("ascii")).digest()
    return base64.b64encode(digest).decode("ascii")


def encode_frame(payload: bytes, opcode: int = 0x1) -> bytes:
    header = bytearray([0x80 | opcode])
    length = len(payload)
    if length < 126:
        header.append(length)
    elif length < 65536:
        header.append(126)
        header += struct.pack("!H", length)
    else:
        header.append(127)
        header += struct.pack("!Q", length)
    return bytes(header) + payload


def _read_exact(reader: Any, size: int) -> bytes:
    chunks: list[bytes] = []
    remaining = size
    while remaining > 0:
        chunk = reader.read(remaining)
        if not chunk:
            raise ConnectionError("conexión cerrada")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def read_frame(reader: Any) -> tuple[bool, int, bytes]:
    head = _read_exact(reader, 2)
    first, second = head[0], head[1]
    fin = bool(first & 0x80)
    opcode = first & 0x0F
    masked = bool(second & 0x80)
    length = second & 0x7F
    if length == 126:
        length = struct.unpack("!H", _read_exact(reader, 2))[0]
    elif length == 127:
        length = struct.unpack("!Q", _read_exact(reader, 8))[0]
    mask = _read_exact(reader, 4) if masked else b""
    payload = _read_exact(reader, length) if length else b""
    if masked and payload:
        payload = bytes(byte ^ mask[i % 4] for i, byte in enumerate(payload))
    return fin, opcode, payload


class WebSocket:
    """Conexión WebSocket mínima, segura para envíos desde varios hilos."""

    def __init__(self, rfile: Any, wfile: Any, sock: socket.socket) -> None:
        self.rfile = rfile
        self.wfile = wfile
        self.sock = sock
        self.alive = True
        self._send_lock = threading.Lock()
        self.id = uuid.uuid4().hex[:8]
        # Ventana nativa que abrió esta conexión (``?w=``); ``None`` = principal.
        self.window_id: str | None = None

    # -- envío -----------------------------------------------------------
    def send_text(self, text: str) -> None:
        self._send(encode_frame(text.encode("utf-8"), 0x1))

    def send_json(self, payload: dict[str, Any]) -> None:
        self.send_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))

    def _send(self, data: bytes) -> None:
        if not self.alive:
            return
        with self._send_lock:
            try:
                self.wfile.write(data)
                self.wfile.flush()
            except (BrokenPipeError, ConnectionError, OSError):
                self.alive = False

    # -- recepción -------------------------------------------------------
    def receive(self) -> str | None:
        """Devuelve el siguiente mensaje de texto o ``None`` al cerrar."""
        buffer = bytearray()
        while True:
            try:
                fin, opcode, payload = read_frame(self.rfile)
            except (ConnectionError, OSError, struct.error):
                self.alive = False
                return None
            if opcode == 0x8:
                self.close()
                return None
            if opcode == 0x9:
                self._send(encode_frame(payload, 0xA))
                continue
            if opcode == 0xA:
                continue
            buffer.extend(payload)
            if fin:
                try:
                    return buffer.decode("utf-8")
                except UnicodeDecodeError:
                    buffer.clear()

    def close(self) -> None:
        if self.alive:
            self.alive = False
            try:
                self._send(encode_frame(b"", 0x8))
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Servidor HTTP
# ---------------------------------------------------------------------------
class Server:
    """Sirve la app en ``http://host:port`` y atiende el canal WebSocket."""

    def __init__(self, app: Any, host: str = "127.0.0.1", port: int = 0) -> None:
        self.app = app
        self.host = host
        self.requested_port = port
        self.clients: set[WebSocket] = set()
        self._clients_lock = threading.Lock()
        self._httpd: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = port

    # -- ciclo de vida ---------------------------------------------------
    def start(self) -> int:
        handler = _make_handler(self)
        self._httpd = ThreadingHTTPServer((self.host, self.requested_port), handler)
        self._httpd.daemon_threads = True
        self.port = self._httpd.server_address[1]
        self._thread = threading.Thread(target=self._httpd.serve_forever, name="interui-server", daemon=True)
        self._thread.start()
        return self.port

    def stop(self) -> None:
        with self._clients_lock:
            clients = list(self.clients)
            self.clients.clear()
        for client in clients:
            client.close()
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None

    @property
    def url(self) -> str:
        host = "127.0.0.1" if self.host in ("0.0.0.0", "", "::") else self.host
        return f"http://{host}:{self.port}/"

    # -- clientes --------------------------------------------------------
    def register(self, ws: WebSocket) -> None:
        with self._clients_lock:
            self.clients.add(ws)

    def unregister(self, ws: WebSocket) -> None:
        with self._clients_lock:
            self.clients.discard(ws)

    def broadcast(self, message: dict[str, Any]) -> int:
        with self._clients_lock:
            targets = list(self.clients)
        sent = 0
        for client in targets:
            if client.alive:
                client.send_json(message)
                sent += 1
        return sent

    @property
    def has_clients(self) -> bool:
        with self._clients_lock:
            return any(client.alive for client in self.clients)


def _make_handler(server: Server) -> type[BaseHTTPRequestHandler]:
    app = server.app

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "interui"

        # -- helpers ----------------------------------------------------
        def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A003
            if getattr(app, "verbose", False):
                super().log_message(fmt, *args)

        def _send_bytes(self, status: int, body: bytes, content_type: str, extra: dict[str, str] | None = None) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            for key, value in (extra or {}).items():
                self.send_header(key, value)
            self.end_headers()
            self.wfile.write(body)

        def _send_json(self, status: int, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self._send_bytes(status, body, "application/json; charset=utf-8")

        # -- rutas ------------------------------------------------------
        def do_GET(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            route = parsed.path
            if route == "/ws":
                self._handle_websocket()
                return
            if route.startswith("/static/"):
                self._serve_static(route[len("/static/"):])
                return
            if route.startswith("/uploads/"):
                self._serve_upload(route[len("/uploads/"):])
                return
            if route == "/favicon.ico":
                self._serve_static("favicon.svg")
                return
            if route == "/__interui/health":
                self._send_json(200, {"ok": True, "port": server.port})
                return
            self._serve_app(route)

        def do_POST(self) -> None:  # noqa: N802
            parsed = urllib.parse.urlparse(self.path)
            if parsed.path == "/api/upload":
                self._handle_upload()
                return
            self._send_json(404, {"error": "no encontrado"})

        # -- app --------------------------------------------------------
        def _serve_app(self, route: str) -> None:
            if not app.has_page(route):
                self._send_bytes(404, b"<h1>404</h1><p>Ruta no registrada en la aplicacion.</p>",
                                 "text/html; charset=utf-8")
                return
            try:
                html = app.bootstrap_html(route)
            except Exception as exc:  # pragma: no cover - guardia
                html = app.error_html(exc)
                self._send_bytes(500, html.encode("utf-8"), "text/html; charset=utf-8")
                return
            self._send_bytes(200, html.encode("utf-8"), "text/html; charset=utf-8")

        def _serve_static(self, relative: str) -> None:
            relative = posixpath.normpath(relative).lstrip("/")
            target = (STATIC_DIR / relative).resolve()
            if not str(target).startswith(str(STATIC_DIR.resolve())) or not target.is_file():
                self._send_bytes(404, b"no encontrado", "text/plain; charset=utf-8")
                return
            ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            if ctype.startswith("text/") or ctype in ("application/javascript", "image/svg+xml"):
                ctype += "; charset=utf-8"
            self._send_bytes(200, target.read_bytes(), ctype)

        def _serve_upload(self, relative: str) -> None:
            target = (app.upload_dir / posixpath.normpath(relative).lstrip("/")).resolve()
            if not str(target).startswith(str(app.upload_dir.resolve())) or not target.is_file():
                self._send_bytes(404, b"no encontrado", "text/plain; charset=utf-8")
                return
            ctype = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
            self._send_bytes(200, target.read_bytes(), ctype)

        def _handle_upload(self) -> None:
            try:
                length = int(self.headers.get("Content-Length") or 0)
            except ValueError:
                length = 0
            if length <= 0:
                self._send_json(400, {"error": "cuerpo vacío"})
                return
            if length > app.max_upload_bytes:
                self._send_json(413, {"error": "archivo demasiado grande"})
                return
            data = self.rfile.read(length)
            raw_name = urllib.parse.unquote(self.headers.get("X-File-Name") or "archivo")
            name = _SAFE_NAME.sub("_", os.path.basename(raw_name)).strip() or "archivo"
            mime = self.headers.get("X-File-Type") or "application/octet-stream"
            token = uuid.uuid4().hex[:12]
            folder = app.upload_dir / token
            folder.mkdir(parents=True, exist_ok=True)
            (folder / name).write_bytes(data)
            self._send_json(
                200,
                {
                    "name": name,
                    "size": len(data),
                    "mime": mime,
                    "path": str(folder / name),
                    "url": f"/uploads/{token}/{urllib.parse.quote(name)}",
                    "token": token,
                },
            )

        # -- websocket --------------------------------------------------
        def _handle_websocket(self) -> None:
            key = self.headers.get("Sec-WebSocket-Key")
            if not key or "websocket" not in (self.headers.get("Upgrade") or "").lower():
                self._send_json(400, {"error": "se requiere websocket"})
                return
            accept = _accept_key(key)
            self.wfile.write(
                (
                    "HTTP/1.1 101 Switching Protocols\r\n"
                    "Upgrade: websocket\r\n"
                    "Connection: Upgrade\r\n"
                    f"Sec-WebSocket-Accept: {accept}\r\n\r\n"
                ).encode("ascii")
            )
            self.wfile.flush()
            self.close_connection = True

            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            ws = WebSocket(self.rfile, self.wfile, self.connection)
            ws.window_id = (query.get("w") or [None])[0]
            server.register(ws)
            try:
                app.on_client_connect(ws)
                while ws.alive:
                    raw = ws.receive()
                    if raw is None:
                        break
                    try:
                        message = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    app.handle_message(ws, message)
            except (ConnectionError, OSError):
                pass
            finally:
                ws.alive = False
                server.unregister(ws)
                app.on_client_disconnect(ws)

    return Handler


def serve_forever_blocking(app: Any, host: str = "127.0.0.1", port: int = 0) -> None:
    server = Server(app, host, port)
    server.start()
    log(f"interui escuchando en {server.url}")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        server.stop()
