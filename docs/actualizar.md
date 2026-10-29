# Actualizar interUI

Esta es la página de referencia para mantener interUI al día. Si llegaste aquí
desde el aviso que aparece al abrir tu aplicación, abajo tienes el comando exacto
que te toca.

- Última versión publicada: <https://github.com/jurdin32/interUI/releases>
- Historial de cambios (commits): <https://github.com/jurdin32/interUI/commits/main>
- Problemas y sugerencias: <https://github.com/jurdin32/interUI/issues>

---

## 1. La forma fácil: un solo comando

```bash
iui update --run
```

Eso es todo. El comando:

1. pregunta a GitHub cuál es la última versión,
2. mira **cómo está instalado** interUI en ese intérprete,
3. ejecuta lo que toque (descargar de GitHub, actualizar el clon o `pip -U`),
4. y avisa de que reinicies tu aplicación.

Si solo quieres ver el comando sin ejecutarlo:

```bash
iui update
```

`iui`, `interui` y `python -m interui` hacen lo mismo; dentro de un proyecto
también puedes usar `python iui.py update --run`.

> **Ojo con el intérprete.** Actualiza el `pip` del entorno desde el que abres tu
> app. Si tienes dos entornos (uno para el editor y otro para la terminal), el
> aviso seguirá saliendo porque la app sigue importando la versión antigua.
> Comprueba a cuál apunta con
> `python -c "import interui; print(interui.__file__)"`.

---

## 2. Comando de actualización, caso por caso

Esto es lo que ejecuta `iui update --run` en cada situación. El framework lo
detecta solo y te muestra el comando correcto en el aviso de la app.

**Instalado desde GitHub** (la forma disponible hoy, porque el paquete aún no
está en PyPI):

```bash
pip install -U --force-reinstall "interui[desktop] @ git+https://github.com/jurdin32/interUI.git"
```

`--force-reinstall` no es opcional: la versión no cambia entre commits, así que
sin él `pip` contesta «already satisfied» y no descarga nada.

Para moverte a una versión concreta en lugar de a la última de `main`:

```bash
pip install -U "interui[desktop] @ git+https://github.com/jurdin32/interUI.git@v0.5.0"
```

**Instalado desde PyPI** (cuando se publique el primer release):

```bash
pip install -U interui[desktop]
```

**Clon de desarrollo instalado en modo editable**:

```bash
git -C /ruta/a/interUI pull        # trae los cambios del repositorio
pip install -U -e /ruta/a/interUI  # solo si cambió pyproject.toml
```

En modo enlace (`-e`) los cambios del código se ven al instante: casi siempre
basta con `git pull` y volver a abrir la app.

> Usa el `pip` del entorno donde corre tu aplicación (por ejemplo
> `.venv/bin/python -m pip install -U ...`). Si instalas con otro intérprete,
> el aviso seguirá apareciendo porque la app importa la versión anterior.

---

## 3. Cómo saber qué versión tienes

```bash
python -c "import interui; print(interui.__version__)"
interui update            # consulta la última publicada y muestra el comando
interui update --run      # además ejecuta la actualización
```

Si el aviso de la app insiste después de actualizar, comprueba que actualizaste
el intérprete correcto:

```bash
python -c "import interui, sys; print(sys.executable, interui.__version__, interui.__file__)"
```

---

## 4. El aviso dentro de la aplicación

Al arrancar, interUI consulta en segundo plano (sin bloquear la ventana) cuál es
la última versión publicada. Si es más nueva que la instalada:

- escribe una línea en el log (`[interui] Hay una versión nueva…`),
- muestra un aviso flotante con el comando para copiar y un enlace a esta página,
- expone `app.update_available` y `app.update` para que puedas reaccionar:

```python
import interui as ui

app = ui.App("Mi app")


@app.page("/")
def index():
    extra = (
        ui.Badge(f"Nueva versión {app.update.latest}", variant=ui.variant.warning)
        if app.update_available
        else None
    )
    return ui.Screen(ui.Container(pad=ui.pad.py_6)(ui.heading("Hola"), extra))


app.run()
```

El aviso se puede descartar («Ahora no») y no vuelve a molestar para esa misma
versión. Si quieres una comprobación puntual desde Python:

```python
import interui as ui

info = ui.updates.check()
if info and info.available:
    print(info.message())
    print(info.command)
```

### Desactivar la comprobación

Para redes cerradas, auditorías o CI. Cualquiera de estas dos opciones la anula:

```python
app = ui.App("Mi app", check_updates=False)
```

```bash
export INTERUI_NO_UPDATE_CHECK=1
```

También se puede ajustar el tiempo de espera de la consulta:

```python
info = ui.updates.check(timeout=5.0, force=True)
```

El resultado se guarda en `app.data_dir/update-check.json` durante 24 h, así que
abrir la app muchas veces no genera más peticiones.

---

## 5. Actualizar una app ya empaquetada

Si distribuiste tu aplicación como ejecutable (`interui build`), el binario lleva
interUI dentro: actualizar el paquete de Python **no** cambia los ejecutables ya
generados. Para esos casos:

1. actualiza interUI en el entorno de desarrollo,
2. vuelve a empaquetar (`interui build app.py --name MiApp`),
3. distribuye el nuevo ejecutable.

Dentro de un ejecutable, el aviso de versión nueva sigue funcionando (le indica al
usuario final qué versión de interUI hay detrás), pero la actualización la
controlas tú al publicar una nueva compilación.

---

## 6. Problemas frecuentes

| Síntoma | Causa y solución |
|---|---|
| `Successfully installed interui-0.2.1` y la app sigue en 0.2.1 | Instalaste con otro intérprete; usa `python -m pip` del mismo entorno. |
| Pip dice que ya está actualizado pero hay versión nueva | En instalaciones desde Git, pip no actualiza si el número de versión no cambió: espera a un release con versión mayor o usa `--force-reinstall`. |
| `No se pudo consultar la última versión` | Sin conexión o proxy bloqueando `api.github.com` / `pypi.org`. Actualiza a mano con el comando mostrado. |
| El aviso no desaparece tras actualizar | Cierra y abre la app; la comprobación se repite al arrancar (caché de 24 h). |
| Quiero el aviso también en producción | Está activado por defecto; solo se desactiva con `check_updates=False` o `INTERUI_NO_UPDATE_CHECK=1`. |
