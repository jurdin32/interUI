# Catálogo de iconos

interUI incluye su propio set de iconos vectoriales (trazo 24×24, `stroke-width`
1.8): no depende de ninguna librería externa ni de la red, así que funciona
igual en macOS, Windows y Linux, dentro del ejecutable empaquetado.

Cada icono tiene su nombre con puntos: `icons.car`, `icons.edit`,
`icons.chevron_down`. Los guiones de las utilidades CSS se escriben con `_`.

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


204 iconos disponibles.


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
| `arrow-down-left` | `download` | `mail` | `smile` |
| `arrow-down-right` | `droplet` | `map` | `snowflake` |
| `arrow-left` | `edit` | `map-pin` | `sort` |
| `arrow-right` | `expand` | `maximize` | `sparkles` |
| `arrow-up` | `external` | `menu` | `square` |
| `arrow-up-left` | `eye` | `message-circle` | `square-check` |
| `arrow-up-right` | `eye-off` | `message-square` | `star` |
| `at-sign` | `fan` | `mic` | `store` |
| `award` | `file` | `mic-off` | `strikethrough` |
| `badge-check` | `file-plus` | `minimize` | `sun` |
| `banknote` | `file-text` | `minus` | `sunrise` |
| `battery` | `filter` | `monitor` | `sunset` |
| `bell` | `flag` | `moon` | `table` |
| `bold` | `flame` | `more-h` | `tablet` |
| `bookmark` | `flask` | `more-v` | `tag` |
| `bookmark-plus` | `folder` | `mouse-pointer` | `target` |
| `box` | `folder-open` | `move` | `terminal` |
| `boxes` | `folder-plus` | `music` | `terminal-2` |
| `braces` | `gauge` | `navigation` | `thermometer` |
| `bug` | `gift` | `outdent` | `thumbs-down` |
| `calendar` | `git-branch` | `package` | `thumbs-up` |
| `camera` | `git-commit` | `panel-left` | `ticket` |
| `car` | `git-merge` | `panel-right` | `timer` |
| `cart` | `globe` | `paperclip` | `trash` |
| `cast` | `grid` | `paste` | `trophy` |
| `chart` | `hand` | `pause` | `underline` |
| `check` | `hard-drive` | `phone` | `undo` |
| `check-circle` | `hash` | `pie` | `unlock` |
| `chevron-down` | `headphones` | `pin` | `upload` |
| `chevron-left` | `heart` | `play` | `user` |
| `chevron-right` | `help` | `plug` | `users` |
| `chevron-up` | `home` | `plus` | `video` |
| `chevron-up-down` | `image` | `power` | `video-off` |
| `chevrons-left` | `inbox` | `printer` | `volume` |
| `chevrons-right` | `indent` | `receipt` | `volume-x` |
| `chevrons-up` | `info` | `redo` | `wallet` |
| `circle` | `italic` | `refresh` | `wifi` |
| `circle-dot` | `key` | `regex` | `wrench` |
| `clipboard` | `keyboard` | `save` | `x` |
| `clock` | `layers` | `scissors` | `x-circle` |
| `cloud` | `layout` | `search` | `zap` |
