# Guía de escritorio

`interui` renderiza HTML dentro de una **ventana nativa**. Esta guía cubre el
ciclo de vida, el puente con el sistema operativo, la personalización de la
ventana y el empaquetado en ejecutables para macOS, Windows y Linux.

## 1. Ciclo de vida

```python
app = App("Mi app", width=1100, height=720, theme="light")

@app.page("/")
def index(): ...

app.run()                       # ventana nativa (por defecto)
app.run(window="browser")       # navegador del sistema (solo depuración)
app.run(window="none")          # solo servidor (tests, integración con otros procesos)
```

Secuencia interna:

1. Se levanta un servidor local en `127.0.0.1` con puerto efímero.
2. Se crea la ventana nativa (`pywebview`) apuntando a esa URL.
3. Al conectar el primer cliente se renderiza la vista y se pinta.
4. Cada evento viaja por WebSocket, se ejecuta en Python y la vista se re-renderiza.
5. Al cerrar la ventana se ejecutan los hooks `@app.on_close` y el servidor se apaga.

```python
@app.on_close
def guardar() -> None:
    print("adiós")
```

Parámetros útiles de `App`:

| Parámetro | Por defecto | Descripción |
|---|---|---|
| `title` | `"interui"` | Título de la ventana y del menú del sistema. |
| `width`, `height` | `1180`, `780` | Tamaño inicial. |
| `theme` | `"light"` | `"light"` u `"dark"`. |
| `frameless` | `False` | Sin marco del sistema (usa `TitleBar`). |
| `resizable` | `True` | Ventana redimensionable. |
| `data_dir` | por plataforma | Datos de la app (registro, ajustes). |
| `menus` | `[]` | Menús nativos (`webview.Menu`) en macOS/Windows. |
| `dev` | `False` | Sin caché de estáticos. |

`app.run(...)` acepta además `port`, `host`, `debug` (herramientas de desarrollo),
`gui` (`"edgechromium"`, `"gtk"`, `"qt"`…) y `on_top`.

## 2. Ventana sin marco

```python
app = App("Mi app", frameless=True)

ui.Screen(
    ui.TitleBar("Mi app", icon="layers"),   # arrastrar + minimizar/maximizar/cerrar
    ui.Main(class_="flex-1 overflow-y-auto")(...),
    ui.StatusBar(ui.Text("Listo")),
    class_="flex flex-col h-screen",
)
```

`TitleBar` usa la zona `pywebview-drag-region` para mover la ventana y los
botones nativos (`data-iui-native`) para minimizar, maximizar y cerrar. Si
prefieres el marco del sistema, no uses `frameless` y omite `TitleBar`.

## 3. Puente con el sistema operativo

Desde Python:

```python
ruta = app.native.save_text("informe.txt", texto)          # diálogo de guardado
datos = app.native.read_text(file_types=("Texto (*.txt)",))  # (ruta, contenido)
carpeta = app.native.pick_folder()
app.native.notify("Proceso terminado", "120 registros")
app.native.clipboard_write("texto")
app.native.set_title("Mi app · informe.txt")
app.native.set_always_on_top(True)
```

Desde JavaScript (dentro de la ventana):

```js
const archivo = await window.interui.native.openFile();
await window.interui.native.save("datos.json", JSON.stringify(datos));
await window.interui.native.notify("Hola", "desde JS");
const info = await window.interui.native.info();
```

Y desde HTML, sin escribir JS:

```python
ui.Button("Cerrar", data={"iui-native": "close"})
ui.Button("Pantalla completa", data={"iui-native": "fullscreen"})
ui.Link("Documentación", href="https://tailwindcss.com", )  # se abre fuera de la app
ui.Button("Guardar copia", data={"iui-download": "copia.txt|contenido"})
```

### Diálogos que no congelan la app

En macOS los diálogos se abren como *sheet* anclado a la ventana
(`beginSheetModalForWindow:`), de modo que aparecen encima de la app y el bucle
de eventos sigue vivo. En Windows/Linux se usa el diálogo nativo de `pywebview`
en un hilo propio. Si necesitas ejecutar un diálogo desde un handler, hazlo
normalmente: la interfaz no se bloquea, solo espera la respuesta ese handler.

## 4. Datos persistentes

`app.data_dir` apunta a:

| Sistema | Ruta |
|---|---|
| macOS | `~/Library/Application Support/<slug>` |
| Windows | `%APPDATA%\<slug>` |
| Linux | `$XDG_DATA_HOME/<slug>` (o `~/.local/share/<slug>`) |

Puedes sobreescribirla con `App(data_dir=...)` o la variable
`INTERUI_DATA_DIR`. Allí viven también los registros (`interui.log`), la caché del
motor web y lo que guardes tú:

```python
from pathlib import Path

ajustes = Path(app.data_dir) / "ajustes.json"
```

## 5. Empaquetado

```bash
pip install pyinstaller
interui build app.py --name MiApp            # dist/MiApp (carpeta)
interui build app.py --name MiApp --onefile  # un solo archivo
interui build app.py --icon app.icns         # macOS
interui build app.py --icon app.ico          # Windows
interui build app.py --console               # conserva la consola (depuración)
```

El comando genera el `.spec`, añade `interui/static` como dato y ejecuta
`--collect-all webview`.

### Comprobaciones previas

```bash
interui doctor      # pywebview, CSS compilado, Node, PyInstaller
```

### Por plataforma

**macOS**

- Salida: `dist/MiApp.app`.
- Firma y notarización necesarias para distribuir fuera de tu equipo:
  `codesign --deep --force --sign "Developer ID Application: …" dist/MiApp.app`.
- El motor es WebKit del sistema: no hay runtime extra.

**Windows**

- Salida: `dist/MiApp\MiApp.exe`.
- El equipo destino necesita **WebView2 Runtime** (preinstalado en Windows
  10/11 actualizados; instalador Evergreen disponible para el resto).
- Empaqueta en Windows: PyInstaller no genera `.exe` desde macOS/Linux.
- En apps `--windowed` no hay `stdout`; revisa `<data_dir>\interui.log`.

**Linux**

- Salida: `dist/MiApp/MiApp`.
- Dependencias: `libgtk-3-0` y `libwebkit2gtk-4.1-0` (o `webkit2gtk4.1` en Fedora).
- Para distribuir, considera AppImage o un paquete `.deb`/`.rpm` que declare esas
  dependencias.

### Estructura que debe viajar con la app

```
MiApp/
├── MiApp(.exe)
├── interui/static/{app.css, interui.js, shell.html, favicon.svg}
└── …binarios de webview…
```

Si `app.css` falta, la ventana se abre sin estilos: vuelve a empaquetar después
de `interui assets`.

## 6. Modo navegador (solo para depurar)

```bash
interui run app.py --window browser --debug
```

Útil para inspeccionar con las herramientas del navegador. En ese modo
`app.native` no abre diálogos del sistema y `window.interui.desktop` es `false`;
todo lo demás (rejilla, controles, eventos, estado) funciona igual.

## 7. Buenas prácticas

- Mantén los handlers rápidos: se ejecutan mientras el cliente espera el nuevo
  render. Para tareas largas, lanza un `threading.Thread` y actualiza el estado
  al terminar (`app.set_state`), lo que refresca la vista.
- No uses rutas absolutas de tu máquina en el código; parte de `app.data_dir`.
- Evita `ui.Html()` con datos del usuario: no escapa nada.
- Define `@app.on_close` para guardar ajustes y cerrar recursos.
- Prueba en los tres sistemas si vas a distribuir; los diálogos y notificaciones
  son la parte más dependiente del sistema operativo.
