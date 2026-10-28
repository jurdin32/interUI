# Catálogo de iconos

interUI incluye su propio set de iconos vectoriales (trazo 24×24, `stroke-width`
1.8): no depende de ninguna librería externa ni de la red, así que funciona
igual en macOS, Windows y Linux, dentro del ejecutable empaquetado.

Cada icono tiene su nombre con puntos: `icons.car`, `icons.edit`,
`icons.chevron_down`. Los guiones de Tailwind se escriben con `_`.

```python
import interui as ui
from interui import icons

icons.car                     # el nombre: sirve en icon=…
ui.Icon(icons.car, size=6)    # el control
icons.car(size=6, stroke=2)   # el control con opciones
ui.Card(icons.edit, "Editar") # como hijo se dibuja el icono
icons.close                   # alias: close→x, delete→trash, exit→power
ui.icon_grid(columns=10, searchable=True)   # galería navegable
```

Un nombre inexistente falla al instante (`AttributeError` con sugerencias); si el
nombre llega en una variable, `icons("car")`.

Los nombres desconocidos pasados a `ui.Icon(...)` no rompen la interfaz: se dibuja
un icono de ayuda.

> Este archivo se genera desde el código con `python scripts/gen_docs.py`.


203 iconos disponibles.


## Lista de nombres

| Nombre | Nombre | Nombre | Nombre |
|---|---|---|---|
| `activity` | `code` | `leaf` | `send` |
| `alert` | `columns` | `link` | `server` |
| `alert-circle` | `compass` | `list` | `settings` |
| `alert-triangle` | `component` | `list-checks` | `share` |
| `align-center` | `copy` | `list-ordered` | `shield` |
| `align-left` | `corner-up-right` | `loader` | `shopping-bag` |
| `align-right` | `cpu` | `loader-2` | `shrink` |
| `anchor` | `credit-card` | `lock` | `sidebar` |
| `archive` | `crosshair` | `log-in` | `sliders` |
| `arrow-down` | `database` | `log-out` | `smartphone` |
| `arrow-down-left` | `download` | `mail` | `snowflake` |
| `arrow-down-right` | `droplet` | `map` | `sort` |
| `arrow-left` | `edit` | `map-pin` | `sparkles` |
| `arrow-right` | `expand` | `maximize` | `square` |
| `arrow-up` | `external` | `menu` | `square-check` |
| `arrow-up-left` | `eye` | `message-circle` | `star` |
| `arrow-up-right` | `eye-off` | `message-square` | `store` |
| `at-sign` | `fan` | `mic` | `strikethrough` |
| `award` | `file` | `mic-off` | `sun` |
| `badge-check` | `file-plus` | `minimize` | `sunrise` |
| `banknote` | `file-text` | `minus` | `sunset` |
| `battery` | `filter` | `monitor` | `table` |
| `bell` | `flag` | `moon` | `tablet` |
| `bold` | `flame` | `more-h` | `tag` |
| `bookmark` | `flask` | `more-v` | `target` |
| `bookmark-plus` | `folder` | `mouse-pointer` | `terminal` |
| `box` | `folder-open` | `move` | `terminal-2` |
| `boxes` | `folder-plus` | `music` | `thermometer` |
| `braces` | `gauge` | `navigation` | `thumbs-down` |
| `bug` | `gift` | `outdent` | `thumbs-up` |
| `calendar` | `git-branch` | `package` | `ticket` |
| `camera` | `git-commit` | `panel-left` | `timer` |
| `car` | `git-merge` | `panel-right` | `trash` |
| `cart` | `globe` | `paperclip` | `trophy` |
| `cast` | `grid` | `paste` | `underline` |
| `chart` | `hand` | `pause` | `undo` |
| `check` | `hard-drive` | `phone` | `unlock` |
| `check-circle` | `hash` | `pie` | `upload` |
| `chevron-down` | `headphones` | `pin` | `user` |
| `chevron-left` | `heart` | `play` | `users` |
| `chevron-right` | `help` | `plug` | `video` |
| `chevron-up` | `home` | `plus` | `video-off` |
| `chevron-up-down` | `image` | `power` | `volume` |
| `chevrons-left` | `inbox` | `printer` | `volume-x` |
| `chevrons-right` | `indent` | `receipt` | `wallet` |
| `chevrons-up` | `info` | `redo` | `wifi` |
| `circle` | `italic` | `refresh` | `wrench` |
| `circle-dot` | `key` | `regex` | `x` |
| `clipboard` | `keyboard` | `save` | `x-circle` |
| `clock` | `layers` | `scissors` | `zap` |
| `cloud` | `layout` | `search` |  |
