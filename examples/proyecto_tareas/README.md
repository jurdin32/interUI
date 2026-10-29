# proyecto_tareas

Proyecto de ejemplo de **interUI**: aplicación de **escritorio** (ventana nativa,
sin navegador y sin servidor que desplegar) con una app `notas` que guarda en
SQLite.

Se generó con los dos comandos de andamiaje y luego se rellenó la app:

```bash
iui startproject proyecto_tareas
cd proyecto_tareas
iui startapp notas
```

## Arrancar

```bash
pip install -r requirements.txt
python main.py
```

`main.py` es el punto de entrada: aplica las migraciones pendientes, crea la
`App` (configuración + base de datos + rutas) y abre la ventana nativa.

Si prefieres controlar el esquema a mano:

```bash
python iui.py makemigrations
python iui.py migrate
python main.py
```

## Estructura

```
proyecto_tareas/
├── main.py                  ← punto de entrada: crea todo y abre la ventana
├── iui.py                   ← comandos del proyecto
├── interui.json             ← configuración
├── proyecto_tareas/         ← el paquete del proyecto
│   ├── app.py               ← crea la App y registra las rutas
│   ├── urls.py              ← ruta → vista del proyecto
│   ├── views.py             ← la portada
│   ├── layout.py            ← armazón: menú lateral, título y estado
│   └── models.py            ← modelos del proyecto (ninguno todavía)
├── notas/                   ← una app del proyecto (`iui startapp notas`)
│   ├── models.py            ← Nota (tabla «notas»)
│   ├── views.py             ← lista, alta y borrado
│   └── urls.py              ← /notas
├── migrations/              ← migraciones generadas (se versionan)
└── data/                    ← SQLite (no se versiona)
```

## Por qué no hay `urls.py` con las rutas de `notas`

`notas` está declarada en `apps` de `interui.json`, así que `App.from_config()`
importa `notas/urls.py` y registra sus rutas al arrancar. Para añadir otra app:

```bash
python iui.py startapp clientes
python iui.py makemigrations
python iui.py migrate
```

## Comandos

```bash
python iui.py run              # abre la ventana (igual que python main.py)
python iui.py startapp <app>   # crea una app dentro del proyecto
python iui.py makemigrations   # genera la migración de los modelos
python iui.py migrate          # aplica las migraciones
python iui.py status           # estado de las migraciones
python iui.py shell            # consola con los modelos cargados
python iui.py check            # revisa interui.json y la base de datos
```
