# Guía de la rejilla

`interui` incluye una rejilla de **12 columnas responsive** construida con las
utilidades de Tailwind (`grid-cols-12`, `col-span-*`, `md:col-span-*`…). No hay
CSS propio: todo son clases que Tailwind compila, así que puedes mezclar la
rejilla con cualquier utilidad.

## Conceptos

| Pieza | Clase base | Para qué |
|---|---|---|
| `Row` | `grid grid-cols-12` | Contenedor de columnas. |
| `Col` | `col-span-*` + variantes | Ancho de cada columna por breakpoint. |
| `Container` | `mx-auto max-w-*` + padding | Centra y limita el ancho del contenido. |
| `Grid` | `grid grid-cols-N` | Rejilla nativa de Tailwind (filas homogéneas). |
| `Stack` | `flex flex-col/row` | Apilado con separación (no es rejilla). |

## Breakpoints

| Variante | Ancho mínimo | Uso típico |
|---|---|---|
| base | 0 | móvil / ventana estrecha |
| `sm` | 640 px | ventana mediana |
| `md` | 768 px | tablet |
| `lg` | 1024 px | escritorio |
| `xl` | 1280 px | escritorio grande |
| `xxl` | 1536 px | pantallas amplias |

En una app de escritorio el usuario redimensiona la ventana: la rejilla se
reacomoda sola.

## Patrones

### Columnas iguales

```python
ui.Row(
    *[ui.Col(span=12, md=6, lg=3)(ui.Card(title=f"Tarjeta {i}")(ui.Text("…")))
      for i in range(4)],
    gap=4,
)
```

### Contenido + barra lateral

```python
ui.Row(
    ui.Col(span=12, lg=8)(ui.Card(title="Contenido principal")(ui.Text("…"))),
    ui.Col(span=12, lg=4)(ui.Card(title="Ajustes")(ui.Text("…"))),
)
```

### Formulario a dos columnas con una fila completa

```python
ui.Row(
    ui.Col(span=12, md=6)(ui.Input(label="Nombre")),
    ui.Col(span=12, md=6)(ui.EmailInput(label="Correo")),
    ui.Col(span=12)(ui.Textarea(label="Notas")),
    gap=4,
)
```

### Desplazamiento y orden

```python
ui.Row(
    ui.Col(span=12, md=6, offset=3)(ui.Card(title="Centrado")(ui.Text("…"))),
    ui.Col(span=12, md=6, order=1)(ui.Card(title="Primero")(ui.Text("…"))),
)
```

`offset=3` genera `col-start-4`; `order=1` genera `order-1`.

### Tarjetas de altura uniforme

`Row` usa `items-stretch` por defecto y `Col` añade `min-w-0`, así que las
tarjetas de una fila igualan altura sin trucos:

```python
ui.Row(*[ui.Col(span=12, lg=4)(ui.Card(h=ui.height.full)(ui.Text("…"))) for _ in range(3)])
```

### Rejilla nativa (sin columnas de 12)

```python
ui.Grid(
    *[ui.Card(title=f"{i}")(ui.Text("…")) for i in range(6)],
    cols=1, sm=2, md=3, lg=6, gap=4,
)
```

### Separación y alineación

```python
ui.Row(
    ui.Col(span=6)(ui.Text("izquierda")),
    ui.Col(span=6)(ui.Text("derecha")),
    gap=8,        # gap-8
    gap_y=4,      # gap-y-4
    align="center",   # items-center
    justify="between",# justify-between
)
```

## Anchos especiales

| Valor | Clase generada | Significado |
|---|---|---|
| `span=12` | `col-span-12` | 100 % |
| `span="full"` | `col-span-full` | toda la fila |
| `span="auto"` | `col-span-auto` | tamaño del contenido |
| `xl=6` | `xl:col-span-6` | 50 % desde 1280 px |

## Sobrescribir la rejilla

`class_` siempre gana sobre el valor por defecto (la última clase manda):

```python
ui.Col(span=12, md=6, class_="md:col-span-4")   # md:col-span-4 sustituye a md:col-span-6
```

## Errores frecuentes

- **Poner `Col` fuera de `Row`**: `Col` no crea la rejilla; necesita el `grid` de
  `Row` (o `Grid`).
- **Olvidar `min-w-0` en columnas con textos largos**: `Col` ya lo incluye; si usas
  un `div` propio, añádelo para permitir el truncado.
- **Contenedores anidados sin `w-full`**: `Row` ya es `w-full`.
- **Esperar 12 columnas dentro de `Grid`**: `Grid` es la rejilla nativa de Tailwind
  (`grid-cols-N`), no la de 12.
