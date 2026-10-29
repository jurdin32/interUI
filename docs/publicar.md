# Instalar y publicar interUI

Guía completa para **instalar** el framework y para **publicarlo** como paquete
de Python.

**Estado actual:** publicado — [`interui` en PyPI](https://pypi.org/project/interui/)
(0.5.1). Las secciones 4 y 5 explican cómo sacar una versión nueva.

---

## 1. Instalar interUI (para quien lo usa)

```bash
pip install interui              # núcleo (sin ventana nativa)
pip install "interui[desktop]"   # + pywebview = ventana de escritorio real
```

- `pip install -U "interui[desktop]"` instala la última publicada.
- `pip install "interui[desktop]==0.5.1"` fija una versión concreta.

`requirements.txt`:

```text
interui[desktop] >= 0.5.1
```

### Desde el repositorio (desarrollo local)

```bash
git clone https://github.com/jurdin32/interUI.git
cd interUI
python -m venv venv
./venv/bin/pip install -e ".[desktop,dev]"
./venv/bin/python -m pytest -q
```

`-e` (*editable*) hace que los cambios en el código se apliquen sin reinstalar.

### Desde un wheel ya construido

```bash
python -m build --wheel
pip install dist/interui-0.5.1-py3-none-any.whl
pip install "interui[desktop] @ file://$PWD/dist/interui-0.5.1-py3-none-any.whl"
```

### Instalación solo del comando `interui` (aislada)

```bash
pipx install "interui[desktop]"
```

### En un proyecto concreto (requirements / poetry / uv)

```bash
# requirements.txt
interui[desktop] >= 0.5.1

# poetry
poetry add "interui[desktop]"

# uv
uv add "interui[desktop]"
```

---

## 2. Qué contiene el paquete

```
interui-0.5.1-py3-none-any.whl          (≈ 265 kB)
├── interui/                 # 39 módulos: controles, servidor, escritorio,
│                            #   tokens de estilo, ORM, config y migraciones
├── interui/static/
│   ├── app.css              # CSS precompilado (≈ 668 kB)
│   ├── interui.js           # runtime del cliente (≈ 37 kB)
│   ├── shell.html
│   └── favicon.svg
├── interui/py.typed         # tipos para editores y mypy
├── LICENSE
└── METADATA                 # autoría, URLs, classifiers, licencia MIT
```

El CSS y el JS **viajan dentro del wheel**, así que quien instala no necesita
Node.js, npm ni conexión a internet. Node solo hace falta si quieres
**recompilar** CSS tras cambiar la paleta.

Comprobación tras instalar:

```bash
interui doctor
python -c "import interui; print(interui.__version__)"
```

---

## 3. Construir el paquete

```bash
pip install build twine

python -m build                        # dist/interui-0.5.1.tar.gz + interui-0.5.1-py3-none-any.whl
python -m twine check dist/*           # valida metadatos y README (debe decir PASSED)
```

Verificar el contenido sin instalar:

```bash
python -m zipfile -l dist/interui-0.5.1-py3-none-any.whl
```

La versión sale de `interui/__init__.py` (`__version__`); es lo único que hay que
subir antes de etiquetar.

Prueba de instalación limpia (recomendado antes de publicar):

```bash
python -m venv /tmp/prueba
/tmp/prueba/bin/pip install "interui @ file://$PWD/dist/interui-0.5.1-py3-none-any.whl"
/tmp/prueba/bin/interui init demo --no-input --migrate
/tmp/prueba/bin/python -c "import interui; print(interui.__version__)"
```

### Publicar una versión nueva desde el repositorio

```bash
# 1. versión en interui/__init__.py
# 2. historial
# 3. etiqueta y push
git tag -a v0.5.1 -m "interui 0.5.1"
git push origin main
git push origin v0.5.1
```

Al crear el *release* en GitHub, el workflow `.github/workflows/publish.yml`
construye y publica en PyPI (con *trusted publishing*, sin tokens).

---

## 4. Publicar en TestPyPI (ensayo)

TestPyPI es un PyPI de pruebas: sirve para verificar el envío sin ocupar el
nombre real.

1. Crea una cuenta en https://test.pypi.org y un **API token**.
2. Sube:

```bash
python -m twine upload --repository testpypi dist/*
# usuario: __token__
# contraseña: pypi-AgEIcHlwaS5vcmc...
```

3. Instala desde TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ "interui[desktop]"
```

> El `--extra-index-url` es necesario porque las dependencias (pywebview) no
> están en TestPyPI.

También puedes guardar el token una vez:

```bash
# ~/.pypirc
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-...
```

---

## 5. Publicar en PyPI (definitivo)

1. Crea la cuenta en https://pypi.org y un **API token** (Account settings →
   API tokens). Empieza con un token limitado al proyecto `interui` en cuanto
   exista.
2. Sube:

```bash
python -m twine upload dist/*
```

3. Verifica:

```bash
pip install "interui[desktop]"
interui doctor
```

Una versión publicada **no se puede reemplazar**: si hay un error, sube una
versión nueva (`0.1.1`).

### Publicación automática con GitHub Actions (recomendado)

El repositorio ya incluye [`.github/workflows/publish.yml`](../.github/workflows/publish.yml),
que usa *Trusted Publishing* (OIDC): **no guarda tokens en el repo**.

Configura una vez en https://pypi.org/manage/account/publishing/:

| Campo | Valor |
|---|---|
| PyPI Project Name | `interui` |
| Owner | `jurdin32` |
| Repository name | `interUI` |
| Workflow name | `publish.yml` |
| Environment name | `pypi` |

Y crea los *environments* `pypi` y `testpypi` en Settings → Environments del
repositorio. Después, al publicar un **release** en GitHub, el workflow construye,
valida y sube el paquete automáticamente. También puedes lanzarlo a mano
(Actions → publish → Run workflow) eligiendo TestPyPI.

Los tres campos en los que casi todo el mundo falla:

| Si PyPI dice… | Revisa |
|---|---|
| `invalid-publisher` con el nombre del proyecto | que el **PyPI Project Name** sea `interui`, en minúsculas |
| `invalid-publisher` con el workflow | que **Workflow name** sea el nombre del archivo (`publish.yml`), no una descripción |
| *environment mismatch* | que **Environment name** (`pypi`) sea el mismo que `environment:` del workflow, y que el environment exista en Settings → Environments |

---

## 6. Publicar una versión nueva

La versión tiene **un único origen**: `__version__` en
[`interui/__init__.py`](../interui/__init__.py). `hatchling` la lee desde
`[tool.hatch.version]`, así que no hay que tocar `pyproject.toml`.

```bash
# 1. Subir la versión (semver)
#    interui/__init__.py -> __version__ = "0.2.0"

# 2. Recompilar estilos si cambió la paleta
interui assets

# 3. Pasar las pruebas y el lint
./venv/bin/python -m pytest -q
./venv/bin/ruff check interui tests examples

# 4. Construir y validar
rm -rf dist && ./venv/bin/python -m build
./venv/bin/python -m twine check dist/*

# 5. Commit, tag y release
git add -A && git commit -m "release 0.2.0"
git tag v0.2.0 && git push origin main --tags
```

Con el workflow configurado, crear el release en GitHub publica la versión. Sin
workflow, el paso final es `python -m twine upload dist/*`.

---

## 7. Errores habituales al publicar

| Error | Causa | Solución |
|---|---|---|
| `File already exists` | Versión ya subida | Cambia `__version__`; no se puede sobrescribir. |
| `Invalid or non-existent authentication information` | Token mal copiado | Usa `__token__` como usuario y el token completo como contraseña. |
| `twine check` falla | README o metadatos inválidos | Revisa el mensaje; suele ser una URL relativa rota en el README. |
| `HTTPError: 403 ... not allowed to upload to 'interui'` | El nombre pertenece a otra cuenta | Reclama el nombre en PyPI o usa otro (`interui-ui`). |
| Instalado pero sin estilos | CSS no entró en el wheel | Verifica `interui/static/app.css` con `python -m zipfile -l dist/*.whl`. |
| `No module named 'webview'` | Falta el extra | `pip install "interui[desktop]"`. |
| En Linux la ventana no abre | Faltan GTK/WebKitGTK | `sudo apt install libgtk-3-0 libwebkit2gtk-4.1-0`. |
| En Windows, ventana en blanco | Sin WebView2 Runtime | Instala el runtime Evergreen de Microsoft. |

---

## 8. Comandos de referencia rápida

```bash
# instalar para usar
pip install "interui[desktop]"

# instalar para desarrollar
pip install -e ".[desktop,dev]"

# construir
python -m build

# validar
python -m twine check dist/*

# ensayo
python -m twine upload --repository testpypi dist/*

# publicar
python -m twine upload dist/*

# empaquetar una app creada con interUI en un ejecutable
interui build app.py --name MiApp
```

---

## Actualizar una instalación existente

Los comandos para actualizar (según se haya instalado desde Git, PyPI o en modo
editable), el aviso automático de versión nueva y los problemas frecuentes están
en [actualizar interUI](actualizar.md).
