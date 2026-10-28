# Historial de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
La versión vive en `interui/__init__.py` (`__version__`) y cada release se
etiqueta como `vX.Y.Z`.

## [0.5.0] — sin publicar

### Añadido

- **Estilos con notación de punto** (`interui.theme`): `colors.red_500`,
  `pad.py_6`, `radius.xxl`, `shadow.md`, `font.lg.semibold`, `width.full`,
  `flex.center`, `side.right`, `layer.blocking`. Los argumentos (`bg=`, `pad=`,
  `rounded=`…) se resuelven en el componente base, así que funcionan en todos los
  controles, con variantes (`hover_bg`, `dark_bg`, `md_pad`, `md_hover_bg`) y
  valores literales (`colors.hex("#0f172a")`, `gradient.br(a, b)`,
  `pad.py("18px")`).
- **Iconos con notación de punto** (`ui.icons`): los 204 iconos como atributo
  (`icons.car`, `icons.chevron_down`), alias (`icons.close`, `icons.exit`),
  dibujables como hijo y llamables con opciones (`icons.car(size=6)`). Nuevo
  icono `car`.
- **Snackbars** (`ui.Snackbar`) con texto, icono **o** imagen, acción con handler
  de Python, variantes, posición y duración. `app.notify()` y `toast()` aceptan
  `title`, `icon`, `image`, `duration` y `action`.
- **Multiventana**: `app.open_window(route, title=…)`, `app.windows`,
  `app.main_window`, `app.current_window`; por ventana `close()`, `dispose()`,
  `navigate()` y `set_title()`. Cada ventana tiene su propia conexión.
- **Niveles de cierre**: `app.close()` (solo esa ventana), `app.dispose(ventana)`
  y `app.exit()`/`app.quit()` (todo). Funciona también en modo navegador.
- **Niveles de modal**: `Dialog(layer=layer.blocking)` bloquea el primer plano
  (sin aspa, sin `Escape`, sin fondo) y no deja abrir otros diálogos.
- **Posición del sidebar**: `AppShell(sidebar_position=side.left|side.right)`,
  también `start`/`end` y señales.
- **Datos**: `interui.json` como configuración del proyecto, `interui init`
  (asistente), `interui db makemigrations|migrate|status`, modelos al estilo de
  Django (`ui.Model`, `Int`, `Str`, `LongText`, `Bool`, `Float`, `Date`,
  `DateTime`, `Json`, `Blob`, `FK`) y migraciones con estado completo.
  Motores: `sqlite` y `file` sin dependencias; `postgres`, `mysql` y `mongo` con
  extras (`interui[postgres]`, etc.).
- **CLI**: comandos `init` y `db`; `doctor`, `assets`, `dev`, `run`, `new`,
  `build` y `update` siguen igual.
- **Armar la interfaz por partes**, con la misma notación de punto:
  `shell.sidebar = ui.Sidebar(...)`, `shell.add = ui.Container(...)`,
  `card += ui.text("Hola")`, `bar["Archivo"] = [ui.ContextItem(...)]`.
  `add` funciona como llamada, como asignación y como `+=` en todos los controles.
- **Diseño adaptable**: en ventanas de menos de 768 px el sidebar del `AppShell`
  se convierte en un panel deslizante con su botón y fondo para cerrarlo; los
  diálogos se limitan a la altura de la ventana con scroll interno; las imágenes
  se ajustan al ancho; la barra de estado baja de línea; el cajón lateral y la
  barra de menús usan anchos y desplazamientos relativos.

### Cambiado

- `icon=` acepta los tokens de `ui.icons` en todos los controles.
- `Text`, `Button` y compañía aceptan `variant`, `tone` y `size` como tokens.
- `Sidebar(width=…)` se respeta al colocar el sidebar a la derecha.
- `App.run(window="browser"|"none")` termina con `app.exit()` en lugar de quedar
  bloqueado.
- `AppShell` usa `h-dvh` (alto real de la ventana) y el contenido `<main>` no
  desborda en horizontal.
- `Dialog`: el cuerpo siempre tiene scroll cuando el alto no alcanza; el ancho
  sigue siendo el de `width=`.
- `Image`: sin proporción fija se ajusta al ancho (`max-w-full`, `h-auto`).
- `StatusBar`: altura mínima y elementos que bajan de línea.
- `Drawer`: anchos relativos (`w-[min(90vw,18rem)]` y equivalentes).
- `MenuBar`: desplazamiento horizontal y laterales sin encoger.

### Documentación

- `docs/datos.md` reescrita de cero: `interui.json` creado a mano (con todas las
  claves y sus valores por defecto), modelos campo por campo, el ORM con tablas de
  métodos y operadores, migraciones explicadas, un CRUD completo dentro de la
  interfaz y una tabla de errores frecuentes con su solución.
- `docs/datos.md` y `docs/estilos.md` se validan en las pruebas: cada bloque
  `python` se compila y la app de ejemplo se renderiza.

### Corregido

- `AppShell(sidebar_width=…)` no hacía nada.
- Carrera al cerrar la app justo después de arrancar el servidor.
- `Icon` ignoraba el color y el estilo en línea.
- Los `Switch` no se veían marcados: el desplazamiento del pulsador estaba en el
  elemento equivocado y los valores de las señales se convertían a texto
  (`Signal('x'=True)`) en lugar de leerse. Ahora `Signal` se imprime con su
  valor y `Switch`/`Checkbox`/`Input`/`Slider` aceptan señales.
- Los controles de la API corta (`window(...)`) no se actualizaban al cambiar una
  señal: ahora `Switch`, `Checkbox`, `Input` y `Slider` resuelven su valor en
  cada render.
- `Progress`, `ProgressRing`, `Meter` y `Gauge` fallaban con señales.
- `margin.mr`, `margin.mb` y `margin.ml` generaban el padding equivocado.
- `ui.dialog.info(...)` y `ui.toast(...)` dentro de un handler de una app creada
  con `ui.App(...)` se abrían en la app implícita (o no aparecían). Ahora usan la
  ventana que está ejecutando el handler.
- `"name": ":memory:"` en SQLite creaba un archivo llamado `:memory:`; ahora es
  una base efímera, útil para tests y demos.

## [0.4.0]

- Aviso de versión nueva dentro de la app y guía de actualización.
- `interui update` y caché de la consulta durante 24 h.

## [0.3.0]

- Diálogos, menús, armazón de aplicación (`AppShell`) e iconos propios (202).
- Alias estáticos para que Pylance resuelva la API compacta.

## [0.2.0]

- API compacta: `window`, `text`, `button`, `state`, `row`, `toast`…
- Distribución por Git además del clon de desarrollo.

## [0.1.0]

- Primera versión: componentes, rejilla de 12 columnas, catálogo de controles,
  servidor local con WebSocket propio y ventana nativa opcional.
