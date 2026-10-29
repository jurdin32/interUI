# Historial de cambios

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
La versión vive en `interui/__init__.py` (`__version__`) y cada release se
etiqueta como `vX.Y.Z`.

## [0.5.0] — sin publicar

### Añadido

- **El proyecto solo lleva configuración**: `startproject` ya no crea
  `mi_app/models.py`, `views.py` ni `urls.py`. Todo eso vive en las apps
  (`iui startapp`), así que un proyecto se compone de `mi_app/app.py` +
  `interui.json`. Si ninguna vista registra `/`, el framework pone una
  bienvenida («Hola mundo» y la pista de qué páginas hay o cómo crear la
  primera).
- **`app.layout`**: el armazón de la ventana (`AppShell` con barra de título,
  menú y estado) se escribe una vez y envuelve **todas** las páginas; las vistas
  devuelven solo su contenido y el menú no desaparece al navegar. Las entradas
  de menú aceptan `href="/ruta"` y navegan sin recargar.
- **`ui.RecordPage(form, title=…)`**: la página completa de un registro
  (título, contador, formulario y tabla) en una llamada. La vista de una app
  generada por `startapp` queda en una línea.
- **`labels` en `ModelForm`**: el nombre visible de cada campo se declara en
  `forms.py` (`labels = {"fecha_nacimiento": "Fecha de nacimiento"}`) y lo usan
  el formulario, los mensajes de error y la tabla.
- **`ui.RecordTable(form)` y `ui.RecordCounter(form)`**: pintan lo guardado con
  las columnas y nombres que declara el formulario, y avisan si falta `migrate`.
  La vista generada por `startapp` baja a diez líneas sin funciones auxiliares.
- **Icono en el título de cada menú**: `MenuBar(..., icons={"Registros":
  ui.icons.users})`, o `("Registros", items, ui.icons.users)` en la forma de
  lista. El nombre de la app (`brand` + `logo`) mantiene su icono propio.
- **Asistente de proyecto**: `iui startproject` sin nombre pregunta el nombre
  corto y el **nombre largo** de la ventana, la carpeta, el motor de base de
  datos (con su ruta o conexión), el tema y si crear y aplicar ya la migración
  inicial. `--title`, `--theme` y `--no-input` permiten saltarse preguntas;
  `interui init` pregunta también el nombre largo.
- **Documentación reorganizada** como un sitio de documentación: índice
  ([`docs/indice.md`](docs/indice.md)), tutorial, anatomía de un proyecto
  ([`docs/proyecto.md`](docs/proyecto.md)), referencia de comandos
  ([`docs/comandos.md`](docs/comandos.md)) y de configuración
  ([`docs/configuracion.md`](docs/configuracion.md)). Una prueba comprueba que
  los enlaces y las anclas de toda la documentación existen.
- **Formularios por modelo**: `ui.ModelForm` genera el alta completa de un
  modelo (un control por campo, etiquetas, obligatorios, `unique`, guardado en la
  base de datos y repintado de la página). Se declara como clase en el
  `forms.py` de cada app y la vista solo lo coloca:
  `VentaForm(ui.ModelForm)` con `model`, `fields`, `title`, `submit_label`,
  `exclude`, `prefix` y `on_saved`. El atajo `ui.ModelForm(Modelo)` crea uno sin
  declarar clase. Documentado en [`docs/formularios.md`](docs/formularios.md).
- **Campos `ui.Email()` y `ui.Choice()`**: dos atajos de `Str` que no cambian
  la columna pero sí el formulario. `Email` usa el control de correo y `Choice`
  un desplegable con sus `choices` (lista de valores o de pares
  `(valor, etiqueta)`), con `default` y validación de que el valor esté entre
  las opciones.
- **`ui.state()` funciona dentro de las vistas** de un proyecto: la señal se
  crea en la app activa, no en la app implícita de la API compacta, así que
  conserva lo que escribe el usuario entre repintados. Sin `name`, la señal se
  identifica por el lugar del código donde se llama (archivo, función, línea e
  instrucción), de modo que dos `state()` distintos nunca comparten clave y el
  mismo `state()` siempre devuelve la misma señal.
- **`iui startapp <app>`** (también `python iui.py startapp <app>`): crea una app
  dentro del proyecto con `models.py`, `forms.py`, `views.py`, `urls.py` y
  `README.md` **listos para usar** (formulario de alta, aviso si falta la base de
  datos y tabla con lo guardado), la apunta en `apps` de `interui.json` y añade
  su `models.py` a las migraciones. El formulario decide campos y nombres
  (`fields`, `labels`) y la vista solo coloca el formulario y su tabla.
  Sus rutas se registran solas (`App.from_config()` importa `<app>/urls.py`), sin
  registrar nada a mano; un solo `migrate` pone al día todas las apps.
  `Config.model_paths()`, `Config.installed_apps()` y `migrations.models` aceptan
  ahora una lista de archivos.
- **`main.py` en los proyectos**: punto de entrada único que aplica las
  migraciones pendientes, construye la `App` y abre la ventana. `iui.py` queda
  para los comandos (`startapp`, `makemigrations`, `migrate`, `status`, `shell`).
- **`examples/proyecto_tareas/`**: proyecto completo de ejemplo con una app
  `notas` y SQLite.
- `App.page()` sustituye la ruta si ya existía, en lugar de duplicarla.

### Corregido

- **`iui update --run` (`--install`, `--upgrade`) actualiza de verdad** en las
  cuatro formas de instalación, sin copiar comandos: detecta el origen, ejecuta
  los pasos (`git pull` + `pip -e` en modo enlace) y avisa al terminar. Para las
  instalaciones desde GitHub usa `--force-reinstall`, porque la versión no cambia
  entre commits y `pip` respondía «already satisfied».

- **Los desplegables de `MenuBar`, `MenuButton` y `ContextMenu` ya no se quedan
  detrás del contenido.** Los paneles de menú se pintaban en `absolute` dentro
  de la barra, y su `overflow-x: auto` los recortaba: el menú se abría pero no se
  veía. Ahora van en `position: fixed` con `z-index` alto y el runtime los coloca
  bajo su disparador (y hacia arriba si no caben abajo), así que ningún
  contenedor con `overflow` los oculta.
- **`AppShell(collapsible=False)`**: el sidebar se queda siempre visible aunque
  la ventana sea estrecha (antes pasaba siempre a panel deslizante).
- **`TitleBar("Mi app", icon=…)` pone el título de verdad**: antes el primer
  argumento se trataba como un hijo y el nombre aparecía suelto, al otro lado de
  la barra. La firma es `TitleBar(title, *children, …)`.
- **Dos ventanas en el mismo proceso**: `window()` registraba la página `/` una
  sola vez, así que la segunda `App` se quedaba sin ruta. Ahora se registra por
  app.
- **`ValidationSummary` ya muestra su título**: el texto de `title=` se pintaba
  vacío porque el componente base se quedaba con el atributo.

### Cambiado

- **El proyecto que crea `startproject` es mínimo**: una ventana con una
  etiqueta centrada que dice «Hola mundo». Antes traía un armazón con menú
  lateral, dos páginas y un modelo `Tarea` de ejemplo; ahora no hay `layout.py`,
  ni rutas de ejemplo, ni tablas: solo la estructura y una vista. Añadir una app
  sigue siendo `python iui.py startapp <app>`.

- **`app.run(window="desktop")` ya no abre el navegador por su cuenta** si falta
  `pywebview`: falla con un `DesktopError` que explica cómo instalarlo. Para
  aceptar el navegador como alternativa hay que decirlo: `window="auto"`.
- Los refrescos de estado se agrupan en un solo hilo (antes se abría uno por
  cambio, con re-renders fuera de orden); `_in_handler` pasa a ser por hilo.
- SQLite ejecuta la consulta y el `fetchall()` bajo el mismo bloqueo, para que
  dos ventanas no compartan la conexión a mitad de lectura.
- El diálogo nativo de macOS espera como máximo 120 s (antes 900 s) y avisa en
  lugar de dejar la ventana bloqueada.

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
  declarativos (`ui.Model`, `Int`, `Str`, `LongText`, `Bool`, `Float`, `Date`,
  `DateTime`, `Json`, `Blob`, `FK`) y migraciones con estado completo.
  Motores: `sqlite` y `file` sin dependencias; `postgres`, `mysql` y `mongo` con
  extras (`interui[postgres]`, etc.).
- **CLI**: comandos `init` y `db`; `doctor`, `assets`, `dev`, `run`, `new`,
  `build` y `update` siguen igual.
- **`iui` y `iui startproject`**: el comando corto hace lo mismo que `interui` y
  `startproject` crea la estructura completa, solo para
  escritorio:
  `iui.py` (comandos), `interui.json` (configuración), `mi_app/` con `app.py`,
  `urls.py`, `views.py`, `layout.py` y `models.py`, más `migrations/` y `data/`.
  El `iui.py` del proyecto trae `run`, `makemigrations`, `migrate`, `status`,
  `shell` (consola con los modelos cargados) y `check`.
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

- **El tutorial se reescribió como 12 pasos en orden**: ventana vacía → contenido
  → menú → botones → estado → rejilla → varias vistas → formulario → tabla →
  persistencia → formulario desde el modelo → proyecto. Cada paso es un archivo
  que se ejecuta tal cual, con «qué vas a ver», «cómo se lee» y el enlace a la
  referencia. Las pruebas ejecutan y renderizan todos los ejemplos, incluidos los
  de `window(...)`, que antes solo se compilaban.

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
