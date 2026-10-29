# Formularios

Un formulario es un archivo más de la app: se declara en `forms.py` y la vista
solo lo coloca en la página. No hay que construir los campos a mano, ni escribir
la validación, ni acordarse de guardar: `ui.ModelForm` lo hace mirando el modelo.

```text
mi_app/
└── ventas/
    ├── models.py     ← las tablas
    ├── forms.py      ← los formularios
    ├── views.py      ← las páginas (usan los formularios)
    └── urls.py       ← qué vista responde a cada ruta
```

`startapp` ya crea los tres archivos conectados y funcionando: si ejecutas
`makemigrations`, `migrate` y abres `/ventas`, tienes un alta de registros con
su tabla. Esta página explica cómo cambiar esos campos y qué más se puede hacer.

---

## 1. El modelo primero

El formulario sale del modelo, así que empieza por ahí:

```python
# ventas/models.py
import interui as ui


class Cliente(ui.Model):
    nombre = ui.Str(max_length=120)
    email = ui.Str(max_length=120, unique=True)
    telefono = ui.Str(max_length=30, null=True)
    activo = ui.Bool(default=True)

    class Meta:
        table = "clientes"
```

| Campo | Se convierte en |
|---|---|
| `Str` | campo de texto (o de correo, si el nombre lleva `email`, `correo` o `mail`) |
| `Email` | campo de correo |
| `Choice` | desplegable con las opciones de `choices` |
| `LongText` | área de texto |
| `Int`, `Float` | campo numérico |
| `Date`, `DateTime` | selector de fecha / fecha y hora |
| `Bool` | interruptor |
| `Json` | área de texto |

Los campos automáticos (`Auto`) y las claves primarias no aparecen: los pone la
base de datos.

---

## 2. El formulario

```python
# ventas/forms.py
import interui as ui

from ventas.models import Cliente


class ClienteForm(ui.ModelForm):
    model = Cliente
    fields = ["nombre", "email", "telefono", "activo"]
    title = "Nuevo cliente"
```

Eso es todo. Un control por campo, con su etiqueta, la validación de
obligatorios hecha en Python y el botón **Guardar** conectado.

| Atributo | Para qué | Por defecto |
|---|---|---|
| `model` | el modelo del que salen los campos | obligatorio |
| `fields` | qué campos se muestran y en qué orden | todos los editables |
| `exclude` | qué campos dejar fuera | `()` |
| `labels` | el nombre visible de cada campo | el nombre del campo |
| `title` | título de la tarjeta | «Nuevo cliente» |
| `submit_label` | texto del botón | `"Guardar"` |
| `on_saved` | función que recibe el registro guardado | `None` |

### Los nombres de los campos

`labels` cambia el texto que se ve: en el formulario **y** en la tabla de la
vista, porque los dos leen del formulario. Sin `labels`, el nombre del campo
(`fecha_nacimiento`) se muestra con espacios y mayúscula («Fecha nacimiento»).

```python
class ClienteForm(ui.ModelForm):
    model = Cliente
    fields = ["nombre", "email", "fecha_nacimiento"]
    labels = {
        "nombre": "Nombre completo",
        "email": "Correo electrónico",
        "fecha_nacimiento": "Fecha de nacimiento",
    }
```

Este archivo es el único sitio donde se decide **qué campos salen** y **cómo se
llaman**: `fields` manda sobre el orden y `labels` sobre los nombres.

Si el modelo tiene muchos campos y solo quieres cambiar un par, usa `exclude`:

```python
class ClienteForm(ui.ModelForm):
    model = Cliente
    exclude = ["telefono"]
```

### Sin declarar clase

Para un formulario suelto, dentro de una vista o de un ejemplo:

```python
ui.ModelForm(Cliente)
```

Es el mismo formulario con los valores por defecto.

> El nombre empieza por mayúscula porque es un componente. `ui.Form` (y su
> alias `ui.form`) son otra cosa: la etiqueta HTML `<form>`.

---

## 3. La vista

La vista no sabe nada de campos, nombres ni validación. Estas diez líneas son
todo:

```python
# ventas/views.py
import interui as ui

from ventas.forms import ClienteForm


def lista() -> ui.Component:
    return ui.RecordPage(ClienteForm(), title="Clientes")
```

Eso pinta el título, el contador, el formulario y la tabla. Y si prefieres
colocarlo por partes (para añadir un resumen, una búsqueda, otra tarjeta…):

```python
def lista() -> ui.Component:
    form = ClienteForm(margin=ui.margin.t_6)
    return ui.Screen(
        ui.Container(pad=ui.pad.py_10)(
            ui.Heading("Clientes", level=1),
            ui.Muted(ui.RecordCounter(form)),      # «3 registros guardados»
            form,                                  # el formulario
            ui.RecordTable(form),                  # la tabla de lo guardado
        )
    )
```

| Pieza | Qué pinta |
|---|---|
| `ui.RecordPage(form, title=…)` | la página entera: título + contador + formulario + tabla |
| `ClienteForm(...)` | la tarjeta con los campos y el botón |
| `ui.RecordTable(form)` | la tabla con lo guardado, con las columnas y nombres del formulario |
| `ui.RecordCounter(form)` | el contador (`0 registros guardados`, `1 registro guardado`…) |

Sin `title`, el título es el plural del modelo (`Persona` → «Personas»). Las
columnas de la tabla se pueden acortar sin tocar el formulario:
`ui.RecordTable(form, columns=["nombre", "email"])`.

`RecordTable` y `RecordCounter` reciben **el formulario**, no el modelo: así no
hay que repetir la lista de campos y, si añades una columna en `forms.py`,
aparece en la tabla sin tocar la vista. Si la tabla de la base de datos todavía
no existe (falta `migrate`), `RecordTable` muestra un aviso en su lugar en vez de
romper la página.

> ¿Quieres otra tabla (un resumen, una búsqueda)? Escribe tu `ui.Table` con las
> filas que necesites; `RecordTable` es solo el caso más común hecho.

```python
# ventas/urls.py
from ventas import views

urlpatterns = [
    ("/clientes", views.lista, "Clientes"),
]


def register(app) -> None:
    for path, view, title in urlpatterns:
        app.page(path, title=title)(view)
```

Al pulsar **Guardar** pasan tres cosas: se validan los campos, se crea el
registro con `Cliente.objects.create(...)` y la página se repinta sola para
mostrarlo en la tabla. Si algo falta, los errores salen en la tarjeta y no se
guarda nada; en cuanto corriges un campo, el aviso desaparece.

---

## 4. Dónde viven los valores

Los valores de los campos son **señales** de la app en la que se está pintando
el formulario. Por eso el usuario puede escribir sin que el texto desaparezca
cuando la página se repinta, y por eso el formulario puede vivir en su propio
archivo sin recibir nada de la vista.

Cada formulario usa una clave por campo:

```text
form_clientes_nombre
form_clientes_email
form_clientes_errores
```

Si necesitas dos formularios del mismo modelo en la misma página, dale un
`prefix` distinto a cada uno para que no compartan claves:

```python
ClienteForm(prefix="principal")
ClienteForm(prefix="rapido")
```

---

## 5. Guardar y hacer algo más

`on_saved` recibe el registro recién creado. Sirve para avisar, navegar o
rellenar otra parte de la pantalla:

```python
class ClienteForm(ui.ModelForm):
    model = Cliente

    def on_saved(self, cliente) -> None:
        ui.toast(f"{cliente.nombre} añadido", "success")
        ui.current_app().navigate("/clientes")
```

También puedes pasarlo sin declarar clase:

```python
ClienteForm = ui.ModelForm(Cliente, on_saved=lambda cliente: ui.toast(cliente.nombre, "success"))
```

---

## 6. Validar más de lo que dice el modelo

`ModelForm` ya comprueba lo obligatorio y los campos `unique`. Para reglas
propias, sobrescribe `guardar()` o valida antes con `ui.state`. Lo más simple es
añadir la comprobación al modelo con un método y llamarlo desde la vista:

```python
class ClienteForm(ui.ModelForm):
    model = Cliente

    def on_saved(self, cliente) -> None:
        if not cliente.email.endswith("@empresa.com"):
            ui.toast("Correo externo: revísalo", "warning")
```

Si necesitas un formulario que **no** salga de un modelo (una búsqueda, unos
ajustes), no uses `ModelForm`: compón los controles y guarda los valores en
señales con `ui.state`.

---

## 7. `ui.state()` en las vistas

Dentro de una vista puedes crear señales con `ui.state` igual que en un ejemplo
de un solo archivo:

```python
def buscador() -> ui.Component:
    filtro = ui.state("")

    return ui.Screen(
        ui.Input(filtro.get(), label="Buscar", on_input=filtro),
        ui.Text(lambda: f"Buscando: {filtro.get()}", size=ui.size.sm, tone=ui.tone.muted),
    )
```

La señal pertenece a la app del proyecto (no a una app implícita), así que se
mantiene entre repintados y navegaciones. El valor inicial solo se aplica la
primera vez: si vuelves a llamar a `ui.state("")` sobre una señal ya creada, no
la reinicia.

| Forma | Cuándo |
|---|---|
| `ui.state(valor)` | señal suelta dentro de una vista |
| `ui.state(valor, name="clave")` | cuando quieres un nombre fijo y legible |
| `app.state("clave", valor)` | en `main.py` o en un archivo de un solo uso |

---

## 8. Errores frecuentes

| Síntoma | Causa |
|---|---|
| `AttributeError: module 'interui' has no attribute 'Xxx'` | el campo no existe: los disponibles son `Int`, `Str`, `Email`, `Choice`, `LongText`, `Bool`, `Float`, `Date`, `DateTime`, `Json`, `Blob` y `FK` |
| `TypeError: ModelForm necesita un modelo` | falta `model = ...` en la clase |
| Un campo del modelo no sale en el formulario | está en `exclude`, o lo genera la base de datos (`Auto`, `auto_now_add`, `auto_now`) |
| La tabla dice «Todavía no hay registros» tras guardar | falta `python iui.py migrate`: la tabla no existe |
| Dos formularios se pisan el texto | comparten `prefix`; dale uno distinto a cada uno |
| `ui.state("x", "")` falla | la firma es `ui.state(valor, name="x")` |

---

## Siguiente paso

- [Datos](datos.md): consultas, filtros y migraciones.
- [Controles](controles.md): todos los campos disponibles y sus opciones.
- [Anatomía de un proyecto](proyecto.md): dónde va cada archivo.
