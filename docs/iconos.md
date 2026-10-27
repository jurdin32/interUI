# Catálogo de iconos

interUI incluye su propio set de iconos vectoriales (trazo 24×24, `stroke-width`
1.8): no depende de ninguna librería externa ni de la red, así que funciona
igual en macOS, Windows y Linux, dentro del ejecutable empaquetado.

```python
import interui as ui

ui.Icon("check", size=6, class_="text-emerald-600")   # por nombre
ui.icon_grid(columns=10, searchable=True)             # galería navegable
len(ui.ICON_NAMES)                                    # cuántos hay
```

Los nombres inexistentes no rompen la interfaz: se dibuja un icono de ayuda.

> Este archivo se genera desde el código con `python scripts/gen_docs.py`.


202 iconos disponibles.


## Lista de nombres

| Nombre | Nombre | Nombre | Nombre |
|---|---|---|---|
| `activity` | `columns` | `link` | `server` |
| `alert` | `compass` | `list` | `settings` |
| `alert-circle` | `component` | `list-checks` | `share` |
| `alert-triangle` | `copy` | `list-ordered` | `shield` |
| `align-center` | `corner-up-right` | `loader` | `shopping-bag` |
| `align-left` | `cpu` | `loader-2` | `shrink` |
| `align-right` | `credit-card` | `lock` | `sidebar` |
| `anchor` | `crosshair` | `log-in` | `sliders` |
| `archive` | `database` | `log-out` | `smartphone` |
| `arrow-down` | `download` | `mail` | `snowflake` |
| `arrow-down-left` | `droplet` | `map` | `sort` |
| `arrow-down-right` | `edit` | `map-pin` | `sparkles` |
| `arrow-left` | `expand` | `maximize` | `square` |
| `arrow-right` | `external` | `menu` | `square-check` |
| `arrow-up` | `eye` | `message-circle` | `star` |
| `arrow-up-left` | `eye-off` | `message-square` | `store` |
| `arrow-up-right` | `fan` | `mic` | `strikethrough` |
| `at-sign` | `file` | `mic-off` | `sun` |
| `award` | `file-plus` | `minimize` | `sunrise` |
| `badge-check` | `file-text` | `minus` | `sunset` |
| `banknote` | `filter` | `monitor` | `table` |
| `battery` | `flag` | `moon` | `tablet` |
| `bell` | `flame` | `more-h` | `tag` |
| `bold` | `flask` | `more-v` | `target` |
| `bookmark` | `folder` | `mouse-pointer` | `terminal` |
| `bookmark-plus` | `folder-open` | `move` | `terminal-2` |
| `box` | `folder-plus` | `music` | `thermometer` |
| `boxes` | `gauge` | `navigation` | `thumbs-down` |
| `braces` | `gift` | `outdent` | `thumbs-up` |
| `bug` | `git-branch` | `package` | `ticket` |
| `calendar` | `git-commit` | `panel-left` | `timer` |
| `camera` | `git-merge` | `panel-right` | `trash` |
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
| `code` | `leaf` | `send` |  |
