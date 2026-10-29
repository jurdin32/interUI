"""Tema global: colores, tamaños y estilos para **todas** las ventanas.

Sirve para no repetir el mismo `bg`, `pad` o `rounded` en cada vista. Lo que se
declara aquí es el **valor por defecto** de cada control; una vista puede
seguir pisándolo pasándolo explícitamente.

```python
import interui as ui

ui.apply_theme(
    {
        "*": dict(rounded="xl"),                            # todos los controles
        "Button": dict(pad=ui.pad.px_4, font=ui.font.sm),   # solo los botones
        "Card": dict(bg=ui.colors.white, border=ui.colors.slate_200),
    }
)
```

Además de las utilidades de estilo (`bg`, `color`, `border`, `ring`, `pad`,
`margin`, `gap`, `rounded`, `shadow`, `w`, `h`, `font`, `opacity`, `leading`,
`tracking`, `z`, `flex`), se aceptan sus variantes (`hover_bg`, `dark_pad`,
`md_font`, `lg_pad`…) y `class_`/`style`.

Los controles con opciones propias (la cabecera de una tarjeta, la franja de una
página, el panel de un diálogo…) también se pueden fijar aquí: sus clases lo
piden con :func:`theme_default`. Por ejemplo::

    apply_theme({"ModelForm": dict(header_bg=ui.colors.slate_100)})

El proyecto que genera ``iui startproject`` trae un ``estilos.py`` con el catálogo
completo, todo comentado, listo para descomentar lo que haga falta.
"""

from __future__ import annotations

from typing import Any, Mapping

from .theme import STYLE_PROPS, _VARIANT_FIRST

__all__ = [
    "TEMA",
    "apply_theme",
    "reset_theme",
    "current_theme",
    "styles_for",
    "theme_default",
    # nombres en español: siguen funcionando
    "aplicar_tema",
    "reiniciar_tema",
    "tema_actual",
    "estilos_de",
    "por_defecto",
]

#: Valores por defecto por control (``"*"`` = todos).
TEMA: dict[str, dict[str, Any]] = {}


def _es_estilo(nombre: str) -> bool:
    """¿La clave es una utilidad de estilo (con sus variantes)?"""
    if nombre in ("class_", "style") or nombre in STYLE_PROPS:
        return True
    if nombre.partition("_")[0] not in _VARIANT_FIRST:
        return False
    from .theme import _parse_style_key

    return _parse_style_key(nombre) is not None


def apply_theme(
    valores: Mapping[str, Mapping[str, Any]] | None = None,
    *,
    reiniciar: bool = False,
) -> dict[str, dict[str, Any]]:
    """Registra los valores por defecto de los controles.

    Se pueden llamar varias veces: lo que se añade se **suma** (las claves
    repetidas se quedan con el último valor). ``reiniciar=True`` borra lo
    anterior antes de aplicar.
    """
    if reiniciar:
        TEMA.clear()
    for control, opciones in (valores or {}).items():
        destino = TEMA.setdefault(str(control), {})
        for clave, valor in dict(opciones or {}).items():
            if valor is not None:
                destino[str(clave)] = valor
    return TEMA


def reset_theme() -> None:
    """Vuelve al tema de fábrica (sin valores por defecto)."""
    TEMA.clear()


def current_theme() -> dict[str, dict[str, Any]]:
    """Copia del tema vigente (útil para depurar o para tests)."""
    return {control: dict(valores) for control, valores in TEMA.items()}


def _nombres(control: Any) -> list[str]:
    """Nombres con los que buscar el control, del más general al más propio.

    Se sube por la jerarquía para que ``"RecordTable"`` también valga para una
    tabla declarada (``class PersonaTable(ui.RecordTable)``).
    """
    if isinstance(control, str):
        return [control]
    clase = control if isinstance(control, type) else type(control)
    nombres = [c.__name__ for c in getattr(clase, "__mro__", (clase,))]
    return [n for n in reversed(nombres) if n != "object"]


def styles_for(control: Any) -> dict[str, Any]:
    """Estilos por defecto de un control (clase, instancia o nombre)."""
    valores = dict(TEMA.get("*", {}))
    if isinstance(control, str):
        nombres = [control]
    else:
        nombres = _nombres(control)
    for nombre in nombres:
        valores.update(TEMA.get(nombre, {}))
    return valores


def theme_default(clase: Any, nombre: str, valor: Any = None) -> Any:
    """Valor del tema para una opción concreta, si el control no lo recibió."""
    if valor is not None:
        return valor
    return styles_for(clase).get(nombre, valor)


def _con_tema(clase: Any, props: dict[str, Any]) -> dict[str, Any]:
    """Completa ``props`` con el tema (solo utilidades de estilo).

    Las opciones propias de un control (``header_bg``, ``title_pad``…) no se
    meten aquí: cada control las lee con :func:`por_defecto`.
    """
    if not TEMA:
        return props
    for clave, valor in styles_for(clase).items():
        if _es_estilo(clave) and clave not in props:
            props[clave] = valor
    return props


# -- alias en español (se conservan: hay proyectos que ya los usan) ---------
aplicar_tema = apply_theme
reiniciar_tema = reset_theme
tema_actual = current_theme
estilos_de = styles_for
por_defecto = theme_default
