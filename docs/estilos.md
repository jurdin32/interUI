# Estilos: notación de punto, sin clases a mano

interUI genera Tailwind por debajo, pero **no escribes clases**. Cada argumento
dice *qué* se cambia y cada token dice *cuánto*:

```python
from interui import Card, Text, colors, pad, radius, shadow, font

Card(
    bg=colors.white,
    border=colors.slate_200,
    pad=pad.all_6,
    rounded=radius.xxl,
    shadow=shadow.md,
)(
    Text("Hola", font=font.lg.semibold, color=colors.slate_700),
)
```

En lugar de:

```python
Card(class_="bg-white border border-slate-200 p-6 rounded-2xl shadow-md")(
    Text("Hola", class_="text-lg font-semibold text-slate-700"),
)
```

Son exactamente lo mismo: los tokens se compilan a esas clases.

> **¿Por qué `py_6` y no `py-6`?** Python no admite `-` en un nombre, así que el
> guion de Tailwind se escribe con `_`. `pad.py_6` se lee igual que `py-6`.

---

## 1. Las tres reglas

1. **El nombre del argumento dice qué se cambia.**
2. **El token dice cuánto.**
3. **Cualquier argumento admite un prefijo de variante** (`hover_`, `dark_`,
   `md_`…).

---

## 2. Argumentos disponibles

| Argumento | Qué cambia | Ejemplo |
|---|---|---|
| `bg` | fondo | `bg=colors.red_500` |
| `color` | color del texto | `color=colors.slate_700` |
| `border` | color del borde | `border=colors.slate_200` |
| `ring` | anillo de foco | `ring=colors.indigo_500` |
| `pad` / `padding` | relleno | `pad=pad.all_6` |
| `margin` | margen | `margin=margin.x_auto` |
| `gap` | separación en flex/grid | `gap=gap.all_4` |
| `rounded` | radio de esquina | `rounded=radius.xl` |
| `shadow` | sombra | `shadow=shadow.md` |
| `w`, `h` | ancho y alto | `w=width.full`, `h=height.n_64` |
| `font` | tipografía | `font=font.lg.semibold` |
| `opacity` | opacidad | `opacity=50` |
| `leading` | interlineado | `leading=font.relaxed` |
| `tracking` | espaciado entre letras | `tracking=font.wider` |
| `z` | capa | `z=10` |
| `flex` | dirección y alineación | `flex=flex.center` |

Todos funcionan en **cualquier** control, porque se resuelven en el componente
base. También se pueden combinar con `class_` y `style`, que siguen disponibles
para lo que no cubran los tokens (y siempre ganan, porque son la vía de escape).

### Valores simples

Si no quieres pensar en tokens, el valor suelto también vale:

```python
Card(pad=6, rounded="xl", shadow="md", w="full", opacity=50)
```

---

## 3. Tokens

### Colores — `colors`

Los 22 colores de Tailwind con sus 11 tonos, más los básicos y una paleta con
significado:

```python
colors.red, colors.red_500, colors.red_700      # rojo (sin tono = 500)
colors.slate_200, colors.emerald_600, colors.zinc_800
colors.white, colors.black, colors.transparent
colors.primary      # indigo-600
colors.success      # emerald-600
colors.warning      # amber-500
colors.danger       # rose-600
colors.info         # sky-600
colors.muted        # slate-500
colors.surface      # white
colors.ink          # slate-900
colors.line         # slate-200
```

El mismo token sirve para fondo, texto, borde o anillo: el prefijo lo pone el
argumento.

```python
Card(bg=colors.primary, color=colors.white, border=colors.indigo_700)
```

### Espaciado — `pad`, `margin`, `gap`

```python
pad.all_6        # p-6      todos los lados
pad.x_4          # px-4     izquierda y derecha
pad.y_6          # py-6     arriba y abajo
pad.t_2          # pt-2     top
pad.r_2, pad.b_2, pad.l_2
pad.s_2, pad.e_2          # lados lógicos (start / end)

margin.x_auto    # mx-auto
margin.mt_2      # mt-2
margin.neg.mt_2  # -mt-2    márgenes negativos con .neg

gap.all_4        # gap-4
gap.x_2          # gap-x-2
gap.y_6          # gap-y-6
```

Los nombres largos también existen: `pad.p_6`, `pad.py_6`, `pad.px_4`,
`pad.pt_2`… (`all_` y `p_` son sinónimos, como `x_` y `px_`).

### Radio, sombra, borde

```python
radius.none, radius.sm, radius.md, radius.lg, radius.xl
radius.xxl        # rounded-2xl   (2xl no es un nombre válido en Python)
radius._2xl       # idéntico a radius.xxl
radius.t_lg       # rounded-t-lg  (t, r, b, l, tl, tr, bl, br)

shadow.sm, shadow.md, shadow.lg, shadow.xl, shadow.inner, shadow.none

border.w_2        # border-2
border.t_2        # border-t-2
border.dashed     # border-dashed
```

### Tipografía — `font`

```python
font.xs, font.sm, font.base, font.lg, font.xl, font.xxl
font.thin, font.normal, font.medium, font.semibold, font.bold, font.black
font.sans, font.serif, font.mono
font.left, font.center, font.right, font.justify
font.uppercase, font.capitalize
font.tight, font.relaxed        # interlineado
font.wide, font.wider           # espaciado entre letras
```

Se encadenan para juntar varias utilidades:

```python
font=font.lg.semibold       # "text-lg font-semibold"
font=font.xl.bold.center    # "text-xl font-bold text-center"
```

### Tamaños y otros

```python
width.full, width.auto, width.screen, width.fit, width.half, width.n_64
height.full, height.screen, height.n_64
opacity.n_50            # opacity-50   (o simplemente opacity=50)
flex.row, flex.col, flex.center, flex.between, flex.wrap, flex.grow
```

### Iconos — `icons`

Los 204 iconos tienen nombre con puntos, y los guiones se escriben con `_`:

```python
icons.car, icons.edit, icons.chevron_down, icons.more_h
```

El token es el nombre (sirve en cualquier `icon=`), se dibuja si lo pones como
hijo y se puede llamar para pasarle opciones:

```python
Button("Guardar", icon=icons.check)      # icon=icons.check
Card(icons.edit, "Editar")               # como hijo se dibuja
icons.car(size=6, stroke=2.2)            # el control con opciones
icons.close                              # alias: close→x, delete→trash, exit→power
```

### Variantes, tonos y tamaños de control — `variant`, `tone`, `size`

Los enumerados que ya existían también tienen nombre:

```python
Button("Guardar", variant=variant.danger, size=size.lg)
Text("hola", tone=tone.muted)
Badge("nuevo", variant=variant.success)
```

`variant`: `primary`, `secondary`, `outline`, `ghost`, `soft`, `link`, `danger`,
`success`, `warning`, `info`, `neutral`, `line`, `dark`.
`tone`: `default`, `muted`, `subtle`, `primary`, `success`, `warning`, `danger`,
`info`, `neutral`, `inherit`.
`size`: `xs`, `sm`, `md`, `lg`, `xl`.

### Posición y capa — `side`, `layer`

```python
AppShell(sidebar=Sidebar(...), sidebar_position=side.right)
Dialog(..., layer=layer.blocking)     # primer plano: solo se cierra aceptando
```

`side`: `left`, `right`, `start`, `end` (además de `top` y `bottom` para otros
usos). Los alias `start`/`end` respetan la dirección de escritura.

`layer`: `page`, `panel`, `modal` (por defecto) y `blocking`/`alert` (primer
plano: sin `Escape`, sin clic en el fondo, sin aspa; mientras esté abierto no se
puede abrir otro diálogo).

---

## 4. Variantes: `hover_`, `focus_`, `dark_`, `md_`…

Basta con prefijar el argumento:

```python
Card(
    bg=colors.white,
    hover_bg=colors.slate_50,
    dark_bg=colors.slate_900,
    focus_ring=colors.indigo_500,
    md_pad=pad.p_8,
    md_hover_bg=colors.slate_100,
)
```

Variantes de estado: `hover_`, `focus_`, `active_`, `disabled_`, `dark_`,
`group_hover_`, `peer_hover_`, `focus_visible_`, `checked_`, `selected_`,
`placeholder_`, `first_`, `last_`, `odd_`, `even_`, `visited_`, `before_`,
`after_`.

Puntos de ruptura: `sm_`, `md_`, `lg_`, `xl_`, `xxl_` (este último es `2xl`).
El punto de ruptura va **primero**: `md_hover_bg`, no `hover_md_bg`.

> Las variantes solo admiten utilidades de Tailwind, no valores literales: la
> razón es que los literales se escriben como CSS en línea y el CSS en línea no
> tiene `:hover`. Si necesitas un hexadecimal en `hover`, usa `class_`.

**Qué viene precompilado.** La hoja de estilos del paquete incluye:

| Familia | Combinaciones listas |
|---|---|
| Colores (`bg`, `text`, `border`, `ring`) | base, `hover:`, `focus:`, `active:`, `dark:` |
| Espaciado (`pad`, `margin`, `gap`) | base y `hover/focus/active/dark` hasta 12, `sm:`…`2xl:` hasta 24 |
| Tamaños (`w`, `h`) | base 0–96 y `sm:`…`2xl:` |

Cruzar las dos familias (`md_hover_bg`, por ejemplo) genera la clase correcta,
pero esa regla tiene que existir en tu hoja: usa `class_=` o recompila con
`interui assets` si vas a abusar de esas combinaciones.

### Adaptarse al tamaño de la ventana

Un patrón típico: poco aire en ventanas pequeñas y más en las grandes.

```python
Container(
    pad=pad.p_4,
    sm_pad=pad.p_6,
    lg_pad=pad.p_10,
)(
    Heading("Panel", font=font.xxl.bold, md_font=font.xxxl.bold),
)
```

Además de los prefijos, estos controles ya son fluidos por sí solos, sin que
escribas nada:

| Control | Qué hace al encoger la ventana |
|---|---|
| `AppShell` | el sidebar se vuelve un panel deslizante con botón (☰); con `collapsible=False` se queda siempre visible; el contenido nunca se aplasta |
| `<main>` del armazón | scroll vertical propio y `overflow-x` oculto |
| `Container` | padding `px-4 → sm:px-6 → lg:px-8` |
| `Row` / `Col` | `span`, `sm`, `md`, `lg`, `xl` por columna |
| `Table`, `DataTable`, `CodeBlock` | se desplazan dentro de su caja, no estiran la página |
| `Dialog`, `ConfirmDialog` | ancho `w-full` con tope y scroll interno si no cabe a lo alto |
| `Image` | `max-w-full` y alto automático si no fijas proporción |
| `Chart` / `Sparkline` | `viewBox` con `w-full` |
| `StatusBar` | los elementos bajan de línea en vez de salirse |
| `Drawer` | anchos relativos (`min(90vw, 18rem)` y compañía) |
| `MenuBar` | desplazamiento horizontal cuando no caben los menús |

### Ancho de un campo

`Input`, `TextInput`, `EmailInput`, `Textarea` y `Select` ocupan todo el ancho
disponible (`w-full`). Cuando necesitas otra medida, se pasa en `width`:

```python
Select([("10", "10"), ("15", "15")], width="w-16")   # 4 rem, como el pie de la tabla
Input("", width="w-40", label="Código")
```

El valor es una clase de ancho de Tailwind y **sustituye** el `w-full` del
control (no se suma a él), así que no hay que pelearse con la clase por defecto.

### Fondo: siempre el que tú digas

`bg=` funciona en **todos** los controles y **sustituye** el color que traen de
fábrica (no se suma: `ui.Card("x", bg=ui.colors.slate_900)` es oscura, no blanca
con una clase de más). Lo mismo con `border=`, `ring=`, `rounded=` y `shadow=`:

```python
ui.Button("Guardar", bg=ui.colors.emerald_600, color=ui.colors.white)
ui.Badge("Nuevo", bg=ui.colors.amber_100, color=ui.colors.amber_800)
ui.Table(headers=["A"], rows=[["1"]], header_bg=ui.colors.slate_200)
ui.H2("Sección", bg=ui.colors.slate_100, pad=ui.pad.p_2)
ui.Card("cuerpo", title="Personas", header_bg=ui.colors.indigo_600,
        header_color=ui.colors.white, footer="pie", footer_bg=ui.colors.slate_50)
```

En los controles que se dibujan **dentro de una tarjeta** (`Card`, `RecordTable`,
`ModelForm`, `RecordPage`), el color va a la tarjeta, que es la superficie que se
ve:

```python
ui.RecordTable(MiForm(), bg=ui.colors.slate_50, border=ui.colors.slate_300)
ui.RecordTable(MiForm(), card_options=dict(bg=ui.colors.slate_50, pad=ui.pad.p_4))
```

| Pieza | Cómo se colorea |
|---|---|
| `Card` | `bg=` la tarjeta; `header_bg`, `header_color`, `header_border`, `header_pad` su cabecera; `footer_bg` el pie |
| `RecordTable` | `bg=` la tarjeta; `header_bg`/`header_color` la fila de encabezados; `striped`/`zebra` las filas; `cell_colors`/`column_bg` por columna; `selected_bg` la fila elegida |
| `ModelForm` | `bg=` la tarjeta; `card_options` el resto |
| `RecordPage` | `title_bg`, `title_color`, `title_border`, `title_pad` la franja del título; `counter_color` el contador |

---

## 5. Colores personalizados, degradados y medidas exactas

Cuando el valor no existe en Tailwind, se pasa un valor literal. interUI lo
emite como **CSS en línea**, así que funciona con la hoja de estilos del paquete,
sin recompilar nada.

```python
Card(bg=colors.hex("#0f172a"))            # también colors.hex("0f172a")
Card(bg=colors.rgb(34, 211, 238))         # colors.rgb(r, g, b, alpha=None)
Card(bg=colors.hsl(190, 95, 54))          # colors.hsl(h, s, l, alpha=None)
Card(color=colors.hex("#22d3ee"))
Card(border=colors.hex("#334155"))
```

### Degradados

```python
bg=gradient(colors.indigo_500, colors.fuchsia_500)        # hacia la derecha
bg=gradient.r(colors.red_500, colors.orange_500)          # →  to right
bg=gradient.br(colors.fuchsia_500, colors.indigo_500)     # ↘  to bottom right
bg=gradient.radial(colors.primary, colors.danger)         # radial
bg=gradient.conic(colors.primary, colors.warning)         # cónico
bg=gradient.r("#000", "#fff")                             # literales también
bg=gradient(colors.primary, colors.ink, direction="45deg")  # cualquier ángulo
```

Direcciones: `r`, `l`, `t`, `b`, `tr`, `tl`, `br`, `bl`; o un ángulo
(`"45deg"`) que se pasa tal cual.

### Medidas exactas

```python
Card(pad=pad.py("18px"))        # padding-block: 18px
Card(pad=pad.x("1.25rem"))      # padding-inline: 1.25rem
Card(margin=margin.mt("2vh"))   # margin-top: 2vh
Card(pad=pad.all(13))           # p-13 (existe en la hoja compilada)
Card(pad=pad.all(999))          # calc(var(--spacing) * 999), sin huecos
```

Los pasos de 0 a 32 usan clases de Tailwind; cualquier otro número se resuelve
con `calc(var(--spacing) * N)`, que es exactamente lo que generaría Tailwind.

---

## 6. Qué pasa con `class_`

`class_` y `style` siguen funcionando y **siempre ganan**:

```python
Card(pad=8, class_="p-2")        # gana p-2
Card(bg=colors.white, style="backdrop-filter: blur(8px)")
```

Son la vía de escape para lo que los tokens no cubren. Todo lo demás puede
convivir: la mezcla de utilidades se resuelve con el mismo `tw()` de siempre, así
que no se duplican reglas.

---

## 7. Descubrir los tokens

Todos los espacios de nombres son explorables: el editor autocompleta con
`dir()` y un token mal escrito falla al instante con un mensaje que sugiere
alternativas.

```pycon
>>> sorted(dir(colors))[:4]
['black', 'danger', "hex('#22d3ee')", 'indigo_600']
>>> colors.morado
AttributeError: colors.morado no existe. Prueba con: red_500, indigo_600, …
```

---

## 8. Si añades tokens nuevos

Los tokens se combinan en tiempo de ejecución, así que Tailwind no los ve al
escanear el código: la combinación final tiene que estar en el safelist de
[`frontend/src/styles.css`](../frontend/src/styles.css). Si añades un espacio de
nombres, añade también su matriz `@source inline(...)` y recompila:

```bash
interui assets        # o: cd frontend && npm run build
```

`tests/test_theme.py` comprueba que las clases que generan los tokens existen de
verdad en `interui/static/app.css`, así que un token sin safelist rompe la CI en
lugar de fallar en silencio.
