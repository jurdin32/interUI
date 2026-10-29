# Comandos

Hay dos formas de invocar a interUI y hacen lo mismo:

- **`iui`** (o `interui`, es el mismo ejecutable) para trabajar desde cualquier
  carpeta: crear un proyecto, abrir un archivo suelto, empaquetar.
- **`python iui.py`** dentro de un proyecto para las tareas del día a día.

Si no quieres instalar el ejecutable en el `PATH`, `python -m interui` acepta los
mismos comandos.

```bash
iui doctor                  # ¿está todo instalado?
python -m interui doctor    # equivalente
```

Todos los comandos devuelven `0` si han ido bien y un código distinto de cero si
algo falló, así que se pueden encadenar en scripts.

---

## Índice

| Comando | Para qué |
|---|---|
| [`startproject`](#startproject) | crea un proyecto completo (con asistente). |
| [`startapp`](#startapp) | crea una app dentro de un proyecto. |
| [`run`](#run) | abre un archivo suelto que define una `App`. |
| [`db`](#db) | migraciones: `makemigrations`, `migrate`, `status`. |
| [`new`](#new) | un proyecto de un solo archivo, sin base de datos. |
| [`init`](#init) | asistente que añade `interui.json` a una carpeta. |
| [`build`](#build) | empaqueta un ejecutable autónomo. |
| [`doctor`](#doctor) | comprueba el entorno. |
| [`update`](#update) | busca versiones nuevas de interUI. |
| [`assets`](#assets-y-dev) | recompila Tailwind. |
| [`dev`](#assets-y-dev) | Tailwind en modo *watch*. |

---

## `startproject`

Crea la estructura completa. **Sin nombre abre un asistente** que pregunta el
nombre largo de la ventana, la base de datos, el tema y si aplicar ya la
migración inicial.

```bash
iui startproject                    # asistente
iui startproject mi_app             # con nombre; en terminal pregunta el resto
iui startproject mi_app --no-input  # todo por defecto, sin preguntas
```

```text
Nombre del proyecto (carpeta y paquete) [mi_app]: Mi Tienda
Nombre largo (el que se ve en la ventana) [Mi Tienda]: Mi Tienda — Gestión
Carpeta donde crearlo [.]:
Motor de base de datos:
  1. SQLite (un archivo, sin servidor)
  2. PostgreSQL
  3. MySQL / MariaDB
  4. MongoDB
  5. Archivos JSON (sin servidor)
Elige un número [1]: 1
  Ruta del archivo [data/app.db]: data/tienda.db
Tema inicial (light/dark) [light]: dark
¿Crear y aplicar la migración inicial ahora? (s/n) [n]: s
```

| Opción | Para qué |
|---|---|
| `name` | Nombre del proyecto; también el de la carpeta y el paquete. Si lo omites, se pregunta. |
| `destination` | Carpeta donde crear el proyecto (por defecto, la actual). |
| `--title` | Nombre largo que se ve en la ventana. |
| `--theme {light,dark}` | Tema inicial. |
| `--db` | `sqlite` (por defecto), `file`, `postgres`, `mysql` o `mongo`. |
| `--database` | Ruta del archivo (SQLite, archivos) o nombre de la base. |
| `--host`, `--port`, `--user`, `--password` | Conexión del motor de servidor. |
| `--migrate` | Crea y aplica la migración inicial al terminar. |
| `--no-input` | No pregunta nada; usa los valores por defecto. |
| `--force` | Escribe aunque la carpeta no esté vacía. |

Si pasas un parámetro por línea de comandos, el asistente no lo vuelve a
preguntar:

```bash
iui startproject tienda --db sqlite --database data/tienda.db --migrate
```

Lo que crea es **lo mínimo**: la estructura del proyecto y una ventana con una
etiqueta centrada que dice «Hola mundo». Sin menús, sin tablas y sin páginas de
ejemplo; a partir de ahí lo haces crecer tú.

```text
mi_app/
├── main.py          ← abre la ventana
├── iui.py           ← comandos
├── interui.json     ← configuración
├── mi_app/          ← app.py, urls.py, views.py, models.py
├── migrations/
└── data/
```

Archivo por archivo: [proyecto.md](proyecto.md).

---

## `startapp`

Crea una app dentro del proyecto y la registra sola: una carpeta con
`models.py`, `forms.py`, `views.py`, `urls.py` y `README.md`, todos **listos
para usar**. La página `/ventas` ya funciona: formulario de alta, validación y
tabla con lo guardado.

```bash
cd mi_app
python iui.py startapp ventas          # dentro del proyecto
iui startapp ventas                    # desde cualquier subcarpeta del proyecto
iui startapp ventas --config ruta/interui.json
```

| Opción | Para qué |
|---|---|
| `name` | Nombre de la app; también el de la carpeta (se normaliza: `Mi App` → `mi_app`). |
| `--config` | Ruta explícita de `interui.json` (si no, se busca hacia arriba). |
| `--force` | Sobrescribe los archivos si la carpeta ya existe. |

Qué hace exactamente:

1. escribe `ventas/__init__.py`, `models.py`, `forms.py`, `views.py`, `urls.py` y `README.md`;
2. añade `"ventas"` a `apps` en `interui.json`;
3. añade `ventas/models.py` a `migrations.models`.

Después:

```bash
python iui.py makemigrations
python iui.py migrate
python main.py
```

| Archivo | Qué trae |
|---|---|
| `models.py` | `Venta` con `nombre`, `descripcion` y `activo`. |
| `forms.py` | `VentaForm(ui.ModelForm)`: un control por campo, obligatorios y `unique`. |
| `views.py` | `inicio()`: el formulario, el aviso si falta la base de datos y la tabla. |
| `urls.py` | `urlpatterns = [ui.path("ventas", inicio, name="ventas")]`. |

Solo tienes que cambiar los campos del modelo: el formulario y la tabla se
adaptan. Los detalles están en [Formularios](formularios.md).

---

## `run`

Abre un archivo que define una instancia de `App`. Útil para ejemplos sueltos y
para depurar antes de montar el proyecto completo.

```bash
iui run examples/05_crud.py
iui run mi_app.py --debug
```

| Opción | Para qué |
|---|---|
| `script` | Archivo Python que crea una `App` (en una variable o como resultado de `window(...)`). |
| `--window {desktop,auto,browser,none}` | `desktop` (por defecto) abre la ventana nativa; `auto` acepta el navegador si falta pywebview; `browser` es solo para depurar; `none` levanta solo el servidor local. |
| `--debug` | Abre las herramientas de desarrollo del motor web. |
| `--port`, `--host` | Servidor local (por defecto `127.0.0.1` y puerto aleatorio). |
| `--title`, `--width`, `--height`, `--theme` | Sobrescriben lo que diga el archivo. |
| `--verbose` | Muestra cada petición HTTP en la consola. |

---

## `db`

Migraciones del proyecto. Lee `interui.json` (o la ruta que le pases con
`--config`) y trabaja sobre los modelos declarados en `migrations.models`.

```bash
python iui.py makemigrations          # genera la migración de los cambios
python iui.py makemigrations inicial  # con nombre propio
python iui.py migrate                 # aplica las pendientes
python iui.py status                  # estado de todas
```

| Subcomando | Qué hace |
|---|---|
| `makemigrations [nombre]` | Compara los modelos con la última migración y escribe `migrations/000N_nombre.json`. Si no hay cambios, lo dice y no crea nada. |
| `migrate` | Aplica en orden las migraciones pendientes. |
| `status` | Lista las migraciones con `✔` (aplicada) o `·` (pendiente) y sus operaciones. |

| Opción | Para qué |
|---|---|
| `--force` | Permite cambios que **borran datos** (`RemoveField`, `DeleteModel`). Sin él, se niega y te enseña qué se perdería. |
| `--config` | Ruta de `interui.json`. |

> **Antes de borrar una columna**, haz una copia de `data/`. `--force` no avisa
> dos veces: aplica la migración y los datos de esa columna desaparecen.

---

## `new`

Un proyecto de un solo archivo (`app.py` + `README.md`), sin base de datos ni
migraciones. Para prototipos y ejemplos.

```bash
iui new ideas
cd ideas
python app.py
```

---

## `init`

Añade `interui.json`, `app.py`, `models.py` y `migrations/` a una carpeta que ya
existe (por ejemplo, un proyecto que empezó como script suelto).

```bash
iui init mi_carpeta --db sqlite
iui init . --no-input
```

Acepta las mismas opciones de base de datos y tema que `startproject`, más
`--name`, `--title` y `--migrate`.

---

## `build`

Genera un ejecutable autónomo con PyInstaller. El CSS, el JS y los binarios del
motor web se incluyen solos.

```bash
pip install pyinstaller
iui build mi_app.py --name MiApp
iui build mi_app.py --name MiApp --onefile
iui build mi_app.py --icon app.icns
```

| Opción | Para qué |
|---|---|
| `script` | Archivo de entrada que abre la app. |
| `--name` | Nombre del ejecutable. |
| `--output` | Carpeta de salida (por defecto `build-out`). |
| `--onefile` | Un solo archivo; tarda más en abrir. |
| `--console` | Mantiene la consola visible (para depurar). |
| `--icon` | `.icns` en macOS, `.ico` en Windows. |

Resultado: `build-out/dist/<nombre>` (o `.app` en macOS). Más detalle en
[escritorio.md](escritorio.md#6-empaquetado).

---

## `doctor`

Comprueba que el entorno puede abrir ventanas: intérprete, `pywebview`, motor
del sistema, CSS compilado y Node (solo si vas a recompilar estilos).

```bash
iui doctor
```

Si algo falta, dice exactamente qué instalar. Es el primer comando que hay que
ejecutar cuando «la ventana no aparece».

---

## `update`

Comprueba si hay una versión más nueva publicada y muestra el comando para
actualizar.

```bash
iui update
iui update --run          # ejecuta la actualización
iui update --timeout 10   # red lenta
```

La app también avisa sola al arrancar, en segundo plano. Se desactiva con
`INTERUI_NO_UPDATE_CHECK=1`. Guía completa: [actualizar.md](actualizar.md).

---

## `assets` y `dev`

Solo hacen falta si tocas la parte visual (paleta, clases nuevas de Tailwind):

```bash
iui assets    # recompila interui/static/app.css una vez
iui dev       # recompila al guardar (modo watch)
```

Requieren Node.js y `frontend/` con sus dependencias instaladas. Si no cambias
estilos, no los necesitas: el paquete ya trae el CSS compilado.

---

## `python iui.py`: comandos del proyecto

Dentro de un proyecto, `iui.py` es el atajo que conoce la configuración local.

```bash
python iui.py                   # abre la ventana (igual que `run`)
python iui.py run
python iui.py startapp ventas
python iui.py makemigrations
python iui.py migrate
python iui.py status
python iui.py shell
python iui.py check
```

| Comando | Qué hace |
|---|---|
| `run` | Abre la ventana con la `App` del proyecto. Acepta `--debug` y `--verbose`. |
| `startapp` | Crea una app y la registra. |
| `makemigrations`, `migrate`, `status` | Igual que `iui db …`. |
| `shell` | Consola interactiva de Python con tus modelos, `ui` y `db` cargados. |
| `check` | Valida `interui.json` y enseña la base de datos configurada. Útil en CI. |

Ejemplo de `check`:

```text
[interui] configuración correcta: /ruta/mi_app/interui.json
[interui] app: mi_app
[interui] base de datos: default: sqlite · sqlite:///data/app.db
```

---

## Resumen de códigos de salida

| Código | Significado |
|---|---|
| `0` | Todo correcto. |
| `1` | Error de configuración, carpeta no vacía, falta el nombre del proyecto o fallo al abrir la ventana. |
| otro | El código que devolvió la herramienta externa (`build`). |
| `130` | `Ctrl+C`. |
