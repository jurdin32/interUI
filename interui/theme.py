"""Estilos con notación de punto: ``bg=colors.red_500``, ``pad=pad.py_6``.

El framework habla Tailwind por debajo, pero no hace falta escribir clases a mano.
Cada utilidad tiene un nombre con puntos y el valor se asigna con ``=``:

.. code-block:: python

    from interui import Card, Text, colors, pad, radius, shadow, font

    Card(
        bg=colors.white,
        border=colors.slate_200,
        pad=pad.all_6,
        rounded=radius.x2l,
        shadow=shadow.md,
    )(
        Text("Hola", font=font.lg.semibold, color=colors.slate_700),
    )

Hay tres reglas y no más:

* **el nombre del argumento dice qué se cambia** (``bg``, ``color``, ``pad``,
  ``margin``, ``gap``, ``rounded``, ``shadow``, ``w``, ``h``, ``font``,
  ``opacity``, ``leading``, ``tracking``, ``z``);
* **el token dice cuánto** (``pad.py_6`` = ``py-6``, ``colors.red_500``);
* **todo admite un prefijo de variante**: ``hover_bg``, ``dark_pad``,
  ``md_font`` o combinados como ``md_hover_bg``.

Los guiones de Tailwind se escriben con ``_`` porque Python no admite ``-`` en un
nombre; ``pad.py_6`` se lee igual que ``py-6``.

Cuando hace falta un valor que Tailwind no tiene (un hexadecimal, un degradado,
una medida exacta) se usa el mismo ``=`` con un valor literal:

.. code-block:: python

    Card(bg=colors.hex("#0f172a"))
    Card(bg=gradient.r(colors.indigo_500, colors.fuchsia_500))
    Card(pad=pad.py("13px"))

Los valores literales se emiten como CSS en línea, así que funcionan sin
recompilar la hoja de estilos del paquete.

``class_=`` y ``style=`` siguen disponibles para cualquier caso que los tokens no
cubran.
"""

from __future__ import annotations

import re
from functools import partial
from typing import Any, Callable, Iterable, Sequence

from ._palette import FAMILIES, PALETTE, SHADES

__all__ = [
    "Token",
    "Color",
    "CssColor",
    "Css",
    "Gradient",
    "colors",
    "gradient",
    "pad",
    "margin",
    "gap",
    "radius",
    "shadow",
    "border",
    "font",
    "width",
    "height",
    "opacity",
    "flex",
    "variant",
    "tone",
    "size",
    "side",
    "layer",
    "Word",
    "STYLE_PROPS",
    "resolve_style_props",
    "utility",
    "paint",
    "style_attr",
    "juntar_estilos",
]

_NUM = re.compile(r"\d+(?:\.\d+)?")


# ---------------------------------------------------------------------------
# tipos de valor
# ---------------------------------------------------------------------------
class Css(str):
    """Declaraciones CSS listas para el atributo ``style``."""


class Color(str):
    """Color de la paleta **sin** prefijo de utilidad: ``"red-500"``.

    El prefijo lo pone el argumento: ``bg=colors.red_500`` genera ``bg-red-500``
    y ``color=colors.red_500`` genera ``text-red-500``.
    """


class CssColor(str):
    """Color literal de CSS: ``#22d3ee``, ``rgb(34 211 238)``, ``oklch(…)``."""


class Token(str):
    """Utilidad de Tailwind ya completa, por ejemplo ``rounded-xl``.

    Se pueden encadenar para juntar varias utilidades del mismo grupo:
    ``font.lg.semibold`` equivale a ``text-lg font-semibold``.
    """

    def __new__(cls, value: str, resolver: Callable[[str], Any] | None = None) -> "Token":
        obj = super().__new__(cls, value)
        obj._resolver = resolver
        return obj

    def __getattr__(self, name: str) -> "Token":
        if name.startswith("_"):
            raise AttributeError(name)
        resolver = self.__dict__.get("_resolver")
        if resolver is None:
            raise AttributeError(name)
        extra = resolver(name)
        if extra is None:
            raise AttributeError(f"{str(self)!r} no admite «{name}»")
        return Token(f"{self} {extra}", resolver)


# ---------------------------------------------------------------------------
# espacio de nombres
# ---------------------------------------------------------------------------
class _Namespace:
    """Resuelve ``ns.nombre_6`` a un :class:`Token` con ``__getattr__``."""

    __slots__ = ("_name", "_resolve", "_hint")

    def __init__(
        self,
        name: str,
        resolve: Callable[[str], Any],
        hint: Sequence[str] = (),
    ) -> None:
        self._name = name
        self._resolve = resolve
        self._hint = tuple(hint)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            # ``2xl`` no es un identificador válido en Python: se escribe ``_2xl``.
            if len(name) > 1 and name[1].isdigit():
                return self.__getattr__(name[1:])
            raise AttributeError(name)
        value = self._resolve(_SIZE_ALIASES.get(name, name))
        if value is None:
            examples = ", ".join(self._hint[:10]) or "—"
            raise AttributeError(f"{self._name}.{name} no existe. Prueba con: {examples}")
        return value

    def __dir__(self) -> list[str]:
        return sorted(self._hint)

    def __repr__(self) -> str:
        return f"<interui.{self._name}>"


_SIZE_ALIASES = {"xxl": "2xl", "xxxl": "3xl", "xxxxl": "4xl"}


def _ns(name: str, resolve: Callable[[str], Any], hint: Sequence[str]) -> _Namespace:
    return _Namespace(name, resolve, hint)


# ---------------------------------------------------------------------------
# colores
# ---------------------------------------------------------------------------
SEMANTIC_COLORS = {
    "primary": "indigo-600",
    "primary_hover": "indigo-500",
    "primary_soft": "indigo-50",
    "accent": "indigo-500",
    "success": "emerald-600",
    "warning": "amber-500",
    "danger": "rose-600",
    "info": "sky-600",
    "neutral": "slate-600",
    "muted": "slate-500",
    "surface": "white",
    "ink": "slate-900",
    "line": "slate-200",
}

_SPECIAL_COLORS = ("white", "black", "transparent", "inherit", "current")


def _color(name: str) -> Color | None:
    if name in SEMANTIC_COLORS:
        return Color(SEMANTIC_COLORS[name])
    if name in _SPECIAL_COLORS:
        return Color(name)
    family, _, shade = name.rpartition("_")
    if not family:
        family, shade = shade, ""
    if family not in FAMILIES:
        return None
    if not shade:
        return Color(f"{family}-500")
    if shade not in SHADES:
        return None
    return Color(f"{family}-{shade}")


_HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})")


class _Colors(_Namespace):
    """Paleta de Tailwind con nombres con puntos: ``colors.red_500``."""

    def hex(self, value: str) -> CssColor:
        """Color hexadecimal: ``colors.hex("#22d3ee")`` o ``colors.hex("22d3ee")``."""
        text = str(value).strip()
        if not text.startswith("#"):
            text = f"#{text}"
        if not _HEX_RE.fullmatch(text):
            raise ValueError(f"color hexadecimal inválido: {value!r}")
        return CssColor(text)

    custom = hex

    def rgb(self, r: int, g: int, b: int, alpha: float | None = None) -> CssColor:
        """``colors.rgb(34, 211, 238)`` / ``colors.rgb(34, 211, 238, 0.5)``."""
        parts = f"{int(r)} {int(g)} {int(b)}"
        if alpha is None:
            return CssColor(f"rgb({parts})")
        return CssColor(f"rgb({parts} / {alpha})")

    def hsl(self, h: float, s: float, light: float, alpha: float | None = None) -> CssColor:
        """``colors.hsl(190, 95, 54)``."""
        parts = f"{h} {s}% {light}%"
        if alpha is None:
            return CssColor(f"hsl({parts})")
        return CssColor(f"hsl({parts} / {alpha})")


_COLOR_HINTS = (
    "red_500", "indigo_600", "slate_200", "white", "black", "primary", "danger",
    "hex('#22d3ee')",
)

colors = _Colors("colors", _color, _COLOR_HINTS)


def css_value(value: Any) -> str:
    """Valor CSS de un color (para degradados y CSS en línea)."""
    if isinstance(value, Color):
        return PALETTE.get(str(value), str(value))
    return str(value)


# ---------------------------------------------------------------------------
# degradados
# ---------------------------------------------------------------------------
_DIRECTIONS = {
    "r": "to right",
    "l": "to left",
    "t": "to top",
    "b": "to bottom",
    "tr": "to top right",
    "tl": "to top left",
    "br": "to bottom right",
    "bl": "to bottom left",
}


class Gradient:
    """Degradado listo para ``bg=``. Se emite como ``background-image``."""

    def __init__(self, stops: Iterable[Any], direction: str = "r", kind: str = "linear") -> None:
        self.stops = tuple(stops)
        self.direction = direction
        self.kind = kind
        if not self.stops:
            raise ValueError("un degradado necesita al menos dos colores")

    @property
    def css(self) -> str:
        direction = _DIRECTIONS.get(self.direction, self.direction)
        stops = ", ".join(css_value(stop) for stop in self.stops)
        return f"{self.kind}-gradient({direction}, {stops})"

    def __str__(self) -> str:
        return f"background-image: {self.css}"


class _Gradients:
    """``gradient.r(a, b)``, ``gradient.radial(a, b)``, ``gradient(a, b)``."""

    def __call__(
        self,
        *stops: Any,
        direction: str = "r",
        kind: str = "linear",
    ) -> Gradient:
        return Gradient(stops, direction, kind)

    def __getattr__(self, name: str) -> Callable[..., Gradient]:
        if name.startswith("_"):
            raise AttributeError(name)
        if name in ("linear", "radial", "conic"):
            default = "circle" if name == "radial" else ("at center" if name == "conic" else "r")

            def build(*stops: Any, direction: str = default) -> Gradient:
                return Gradient(stops, direction, name)

            return build
        if name in _DIRECTIONS:

            def build_direction(*stops: Any) -> Gradient:
                return Gradient(stops, name, "linear")

            return build_direction
        raise AttributeError(
            f"gradient.{name} no existe. Direcciones: {', '.join(_DIRECTIONS)}; "
            "tipos: linear, radial, conic"
        )

    def __repr__(self) -> str:
        return "<interui.gradient>"


gradient = _Gradients()


# ---------------------------------------------------------------------------
# espaciado (padding / margin / gap)
# ---------------------------------------------------------------------------
# Pasos que existen en la hoja compilada; el resto se emite como CSS en línea
# con `calc()`, igual que haría Tailwind, para que no haya valores muertos.
_SAFE_STEPS = frozenset({0.5, 1.5, 2.5, 3.5, *range(0, 33)})


def _spacing_value(css_prop: str, prefix: str, value: str) -> Token | Css:
    if float(value) in _SAFE_STEPS:
        return Token(f"{prefix}-{value}")
    return Css(f"{css_prop}: calc(var(--spacing) * {value})")


def _spacing_resolver(
    prefixes: dict[str, tuple[str, str]],
    allow_auto: bool,
) -> Callable[[str], Any]:
    def resolve(name: str) -> Token | Css | None:
        head, sep, value = name.rpartition("_")
        if not sep:
            head, value = "all", name
        entry = prefixes.get(head)
        if entry is None:
            return None
        css_prop, prefix = entry
        if value == "auto":
            return Token(f"{prefix}-auto") if allow_auto else None
        if value in ("none", "zero"):
            return Token(f"{prefix}-0")
        if not _NUM.fullmatch(value):
            return None
        return _spacing_value(css_prop, prefix, value)

    return resolve


_NEGATIVE_CALC = re.compile(r"calc\(var\(--spacing\) \* ([0-9.]+)\)")


class _Negative:
    """``margin.neg.mt_2`` → ``-mt-2`` y ``margin.neg.mt("2rem")`` → ``-2rem``."""

    def __init__(self, namespace: _Spacing) -> None:
        self._namespace = namespace
        for head in namespace._map:
            setattr(self, head, partial(self._exact, head))

    def _negate(self, token: Token | Css) -> Token | Css:
        if isinstance(token, Css):
            return Css(_NEGATIVE_CALC.sub(r"calc(var(--spacing) * -\1)", str(token)))
        return Token(" ".join(f"-{part}" for part in str(token).split()))

    def _exact(self, head: str, value: Any) -> Token | Css:
        return self._negate(self._namespace._exact(head, value))

    def __getattr__(self, name: str) -> Token | Css:
        if name.startswith("_"):
            raise AttributeError(name)
        token = self._namespace._resolve(name)
        if token is None:
            raise AttributeError(f"neg.{name} no existe")
        return self._negate(token)


_PAD = {
    "all": ("padding", "p"), "p": ("padding", "p"),
    "x": ("padding-inline", "px"), "px": ("padding-inline", "px"),
    "y": ("padding-block", "py"), "py": ("padding-block", "py"),
    "t": ("padding-top", "pt"), "pt": ("padding-top", "pt"),
    "r": ("padding-right", "pr"), "pr": ("padding-right", "pr"),
    "b": ("padding-bottom", "pb"), "pb": ("padding-bottom", "pb"),
    "l": ("padding-left", "pl"), "pl": ("padding-left", "pl"),
    "s": ("padding-inline-start", "ps"), "ps": ("padding-inline-start", "ps"),
    "e": ("padding-inline-end", "pe"), "pe": ("padding-inline-end", "pe"),
}

_MARGIN = {
    "all": ("margin", "m"), "m": ("margin", "m"),
    "x": ("margin-inline", "mx"), "mx": ("margin-inline", "mx"),
    "y": ("margin-block", "my"), "my": ("margin-block", "my"),
    "t": ("margin-top", "mt"), "mt": ("margin-top", "mt"),
    "r": ("margin-right", "mr"), "mr": ("margin-right", "mr"),
    "b": ("margin-bottom", "mb"), "mb": ("margin-bottom", "mb"),
    "l": ("margin-left", "ml"), "ml": ("margin-left", "ml"),
    "s": ("margin-inline-start", "ms"), "ms": ("margin-inline-start", "ms"),
    "e": ("margin-inline-end", "me"), "me": ("margin-inline-end", "me"),
}

_GAP = {
    "all": ("gap", "gap"), "g": ("gap", "gap"), "gap": ("gap", "gap"), "n": ("gap", "gap"),
    "x": ("column-gap", "gap-x"), "y": ("row-gap", "gap-y"),
}

_SPACE_HINTS = ("all_4", "x_4", "y_6", "t_2", "r_8", "b_0", "l_2", "px_4", "py_6")


class _Spacing(_Namespace):
    """Espaciado con notación de punto y métodos para medidas exactas.

    ``pad.py_6`` (token) y ``pad.py(6)`` / ``pad.py("18px")`` (valor exacto)
    conviven porque los nombres con ``_`` los resuelve ``__getattr__`` y los
    sueltos son métodos creados a partir del mapa del espacio de nombres.
    """

    def __init__(
        self,
        name: str,
        mapping: dict[str, tuple[str, str]],
        allow_auto: bool,
        hint: Sequence[str],
    ) -> None:
        super().__init__(name, _spacing_resolver(mapping, allow_auto), hint)
        self._map = mapping
        for head in mapping:
            if not hasattr(self, head):
                setattr(self, head, partial(self._exact, head))

    @property
    def neg(self) -> _Negative:
        return _Negative(self)

    def _exact(self, head: str, value: Any) -> Token | Css:
        entry = self._map.get(head)
        if entry is None:
            raise AttributeError(f"{self._name}.{head}(...) no existe")
        css_prop, prefix = entry
        text = f"{value:g}" if isinstance(value, (int, float)) else str(value)
        if _NUM.fullmatch(text):
            return _spacing_value(css_prop, prefix, text)
        return Css(f"{css_prop}: {text}")


pad = _Spacing("pad", _PAD, False, _SPACE_HINTS)
margin = _Spacing("margin", _MARGIN, True, _SPACE_HINTS)
gap = _Spacing("gap", _GAP, False, ("all_4", "x_2", "y_6"))


# ---------------------------------------------------------------------------
# gap, radio, sombra, borde, tipografía, tamaños, opacidad, flex
# ---------------------------------------------------------------------------
_RADII = ("none", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl", "full")
_CORNERS = ("t", "r", "b", "l", "tl", "tr", "bl", "br", "s", "e", "ss", "se", "es", "ee")


def _radius(name: str) -> Token | None:
    if name in _RADII:
        return Token(f"rounded-{name}")
    corner, _, size = name.rpartition("_")
    if corner in _CORNERS and size in _RADII:
        return Token(f"rounded-{corner}-{size}")
    return None


radius = _ns("radius", _radius, _RADII)


def _shadow(name: str) -> Token | None:
    if name in ("none", "sm", "md", "lg", "xl", "2xl", "inner"):
        return Token(f"shadow-{name}")
    return None


shadow = _ns("shadow", _shadow, ("none", "sm", "md", "lg", "xl", "2xl", "inner"))


def _border(name: str) -> Token | None:
    if name in ("none", "solid", "dashed", "dotted", "double", "hidden"):
        return Token(f"border-{name}")
    if _NUM.fullmatch(name):
        return Token(f"border-{name}")
    side, _, width = name.rpartition("_")
    if not _NUM.fullmatch(width):
        return None
    if side == "w":
        return Token(f"border-{width}")
    if side in ("x", "y", "t", "r", "b", "l", "s", "e"):
        return Token(f"border-{side}-{width}")
    return None


border = _ns("border", _border, ("w_2", "t_2", "dashed", "none"))


_TEXT_SIZES = ("xs", "sm", "base", "lg", "xl", "2xl", "3xl", "4xl", "5xl", "6xl", "7xl", "8xl", "9xl")
_FONT_WEIGHTS = (
    "thin", "extralight", "light", "normal", "medium", "semibold", "bold", "extrabold", "black",
)
_FONT_FAMILIES = ("sans", "serif", "mono")
_TEXT_ALIGNS = ("left", "center", "right", "justify", "start", "end")
_LEADING = ("tight", "snug", "relaxed", "loose", "none")
_TRACKING = ("tighter", "wide", "wider", "widest")


def _font(name: str) -> Token | None:
    if name in _TEXT_SIZES:
        return Token(f"text-{name}", _font)
    if name in _FONT_WEIGHTS:
        return Token(f"font-{name}", _font)
    if name in _FONT_FAMILIES:
        return Token(f"font-{name}", _font)
    if name in _TEXT_ALIGNS:
        return Token(f"text-{name}", _font)
    if name in ("uppercase", "lowercase", "capitalize"):
        return Token(name, _font)
    if name == "normal_case":
        return Token("normal-case", _font)
    if name in _LEADING:
        return Token(f"leading-{name}", _font)
    if name in _TRACKING:
        return Token(f"tracking-{name}", _font)
    return None


font = _ns("font", _font, ("lg", "sm", "bold", "semibold", "center", "mono", "tight"))

_SIZE_SPECIAL = {
    "full": "full", "auto": "auto", "screen": "screen", "fit": "fit",
    "min": "min", "max": "max", "px": "px",
    "half": "1/2", "third": "1/3", "two_thirds": "2/3",
    "quarter": "1/4", "three_quarters": "3/4",
}


def _size_resolver(kind: str) -> Callable[[str], Token | None]:
    def resolve(name: str) -> Token | None:
        if name in _SIZE_SPECIAL:
            return Token(f"{kind}-{_SIZE_SPECIAL[name]}")
        if _NUM.fullmatch(name):
            return Token(f"{kind}-{name}")
        head, _, value = name.rpartition("_")
        if head in ("n", "num") and _NUM.fullmatch(value):
            return Token(f"{kind}-{value}")
        return None

    return resolve


width = _ns("width", _size_resolver("w"), ("full", "auto", "screen", "n_64", "half"))
height = _ns("height", _size_resolver("h"), ("full", "auto", "screen", "n_64", "half"))


def _opacity(name: str) -> Token | None:
    if name in ("none", "zero"):
        return Token("opacity-0")
    if name in ("full", "all"):
        return Token("opacity-100")
    if _NUM.fullmatch(name):
        return Token(f"opacity-{name}")
    head, _, value = name.rpartition("_")
    if head in ("n", "num") and _NUM.fullmatch(value):
        return Token(f"opacity-{value}")
    return None


opacity = _ns("opacity", _opacity, ("n_50", "n_75", "n_100", "n_0"))

_FLEX = {
    "row": "flex-row",
    "row_reverse": "flex-row-reverse",
    "col": "flex-col",
    "col_reverse": "flex-col-reverse",
    "wrap": "flex-wrap",
    "wrap_reverse": "flex-wrap-reverse",
    "nowrap": "flex-nowrap",
    "one": "flex-1",
    "auto": "flex-auto",
    "initial": "flex-initial",
    "none": "flex-none",
    "grow": "grow",
    "grow_0": "grow-0",
    "shrink": "shrink",
    "shrink_0": "shrink-0",
    "center": "items-center justify-center",
    "between": "justify-between",
    "around": "justify-around",
    "evenly": "justify-evenly",
    "start": "justify-start",
    "end": "justify-end",
    "items_start": "items-start",
    "items_center": "items-center",
    "items_end": "items-end",
    "items_stretch": "items-stretch",
    "items_baseline": "items-baseline",
    "justify_start": "justify-start",
    "justify_center": "justify-center",
    "justify_end": "justify-end",
    "justify_between": "justify-between",
}


def _flex(name: str) -> Token | None:
    value = _FLEX.get(name)
    return Token(value, _flex) if value else None


flex = _ns("flex", _flex, ("row", "col", "center", "between", "wrap", "grow", "none"))


# ---------------------------------------------------------------------------
# enumerados de diseño: variant, tone, size
# ---------------------------------------------------------------------------
class Word(str):
    """Valor de un enumerado de diseño: ``variant.primary``, ``tone.muted``.

    Es un ``str``, así que los controles lo aceptan donde esperan el nombre.
    """


def _words(name: str, values: Sequence[str]) -> _Namespace:
    allowed = {value.replace("_", "-"): value for value in values}

    def resolve(attr: str) -> Word | None:
        value = allowed.get(attr.replace("_", "-"))
        return Word(value) if value is not None else None

    return _Namespace(name, resolve, values)


variant = _words(
    "variant",
    (
        "primary", "secondary", "outline", "ghost", "soft", "link",
        "danger", "success", "warning", "info", "neutral", "line", "dark", "pills",
    ),
)

tone = _words(
    "tone",
    (
        "default", "muted", "subtle", "primary", "success",
        "warning", "danger", "info", "neutral", "inherit",
    ),
)

size = _words("size", ("xs", "sm", "base", "md", "lg", "xl"))

side = _words("side", ("left", "right", "start", "end", "top", "bottom"))

layer = _words("layer", ("page", "panel", "modal", "blocking", "alert"))


# ---------------------------------------------------------------------------
# argumentos de estilo
# ---------------------------------------------------------------------------
STYLE_PROPS: dict[str, str | None] = {
    "bg": "bg",
    "color": "text",
    "border": "border",
    "ring": "ring",
    "pad": "p",
    "padding": "p",
    "margin": "m",
    "gap": "gap",
    "rounded": "rounded",
    "shadow": "shadow",
    "w": "w",
    "h": "h",
    "font": None,
    "flex": None,
    "opacity": "opacity",
    "leading": "leading",
    "tracking": "tracking",
    "z": "z",
}

_PROP_ALIASES: dict[str, tuple[str, ...]] = {
    "bg": ("bg",),
    "color": ("text",),
    "border": ("border",),
    "ring": ("ring",),
    "pad": ("p", "px", "py", "pt", "pr", "pb", "pl", "ps", "pe"),
    "padding": ("p", "px", "py", "pt", "pr", "pb", "pl", "ps", "pe"),
    "margin": ("m", "mx", "my", "mt", "mr", "mb", "ml", "ms", "me"),
    "gap": ("gap", "gap-x", "gap-y"),
    "rounded": ("rounded",),
    "shadow": ("shadow",),
    "w": ("w", "size", "min-w", "max-w"),
    "h": ("h", "size", "min-h", "max-h"),
    "font": ("text", "font", "leading", "tracking"),
    "flex": ("flex", "grow", "shrink", "items", "justify", "self"),
    "opacity": ("opacity",),
    "leading": ("leading",),
    "tracking": ("tracking",),
    "z": ("z",),
}

_BARE_RESOLVERS: dict[str, Callable[[str], Token | None]] = {"font": _font, "flex": _flex}

_CSS_COLOR_PROP = {
    "bg": "background-color",
    "color": "color",
    "border": "border-color",
    "ring": "box-shadow",
}

_VARIANTS = {
    "hover": "hover",
    "focus": "focus",
    "focus_visible": "focus-visible",
    "focus_within": "focus-within",
    "active": "active",
    "disabled": "disabled",
    "dark": "dark",
    "group_hover": "group-hover",
    "peer_hover": "peer-hover",
    "checked": "checked",
    "selected": "selected",
    "placeholder": "placeholder",
    "first": "first",
    "last": "last",
    "odd": "odd",
    "even": "even",
    "visited": "visited",
    "before": "before",
    "after": "after",
    "sm": "sm",
    "md": "md",
    "lg": "lg",
    "xl": "xl",
    "xxl": "2xl",
}

_VARIANT_TOKENS = sorted(_VARIANTS, key=len, reverse=True)
_VARIANT_FIRST = frozenset(token.split("_")[0] for token in _VARIANTS)


def _parse_style_key(key: str) -> tuple[list[str], str] | None:
    """``"md_hover_bg"`` → ``(["md", "hover"], "bg")``."""
    rest = key
    prefixes: list[str] = []
    changed = True
    while changed:
        changed = False
        for token in _VARIANT_TOKENS:
            if rest.startswith(f"{token}_"):
                prefixes.append(_VARIANTS[token])
                rest = rest[len(token) + 1:]
                changed = True
                break
    if prefixes and rest in STYLE_PROPS:
        return prefixes, rest
    return None


def _looks_like_utility(text: str, prop: str) -> bool:
    head = text.split()[0]
    return any(head == alias or head.startswith(f"{alias}-") for alias in _PROP_ALIASES[prop])


def _declarations(css: Css) -> dict[str, str]:
    out: dict[str, str] = {}
    for chunk in str(css).split(";"):
        if ":" not in chunk:
            continue
        name, _, value = chunk.partition(":")
        out[name.strip()] = value.strip()
    return out


def _style_for(prop: str, value: Any) -> tuple[list[str], dict[str, str]]:
    """Traduce ``prop=valor`` a clases de Tailwind y/o declaraciones CSS."""
    if value is None:
        return [], {}
    prefix = STYLE_PROPS[prop]
    if isinstance(value, Gradient):
        if prop != "bg":
            raise TypeError(f"{prop}= no acepta un degradado; usa bg=gradient.…(...)")
        return [], {"background-image": value.css}
    if isinstance(value, CssColor):
        css_prop = _CSS_COLOR_PROP.get(prop)
        if css_prop is None:
            raise TypeError(
                f"{prop}= no acepta un color literal; usa bg=, color=, border= o class_=…"
            )
        if prop == "ring":
            return [], {"box-shadow": f"0 0 0 3px {value}"}
        return [], {css_prop: str(value)}
    if isinstance(value, Css):
        return [], _declarations(value)
    if isinstance(value, Token):
        return str(value).split(), {}
    if isinstance(value, Color):
        if prefix is None:
            raise TypeError(f"{prop}= no acepta un color de la paleta; usa bg=, color= o border=")
        return [f"{prefix}-{value}"], {}
    if isinstance(value, bool):
        raise TypeError(f"{prop}= espera un valor de estilo, no un booleano")
    if isinstance(value, (int, float)):
        if prefix is None:
            raise TypeError(f"{prop}= no acepta números; usa un token como font.lg")
        return [f"{prefix}-{value:g}"], {}
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return [], {}
        resolver = _BARE_RESOLVERS.get(prop)
        if resolver is not None:
            resolved = resolver(text)
            if resolved is not None:
                return str(resolved).split(), {}
            return text.split(), {}
        if prefix is None or _looks_like_utility(text, prop):
            return text.split(), {}
        return [f"{prefix}-{text}"], {}
    raise TypeError(f"{prop}= no entiende {type(value).__name__}; usa un token o una cadena")


def resolve_style_props(props: dict[str, Any]) -> tuple[list[str], dict[str, str]]:
    """Extrae y elimina de ``props`` los argumentos de estilo.

    Devuelve ``(clases, declaraciones)``: las clases van a ``base_class`` y las
    declaraciones al atributo ``style``.
    """
    classes: list[str] = []
    declarations: dict[str, str] = {}
    for key in [name for name in props if name in STYLE_PROPS]:
        add_classes, add_decls = _style_for(key, props.pop(key))
        classes.extend(add_classes)
        declarations.update(add_decls)
    for key in list(props):
        if key.partition("_")[0] not in _VARIANT_FIRST:
            continue
        parsed = _parse_style_key(key)
        if parsed is None:
            continue
        variants, prop = parsed
        value = props.pop(key)
        add_classes, add_decls = _style_for(prop, value)
        if not add_classes and not add_decls:
            continue
        if variants:
            if add_decls:
                raise TypeError(
                    f"{key}=: las variantes ({':'.join(variants)}) no admiten valores "
                    "literales; usa un color de la paleta o class_=…"
                )
            prefix = "".join(f"{variant}:" for variant in variants)
            classes.extend(f"{prefix}{name}" for name in add_classes)
        else:
            classes.extend(add_classes)
            declarations.update(add_decls)
    return classes, declarations


def utility(prefix: str, value: Any) -> str:
    """``utility("gap", 4)`` → ``gap-4``; respeta un token ya completo."""
    text = str(value)
    if isinstance(value, (Token, Color)) or text == prefix or text.startswith(f"{prefix}-"):
        return text
    return f"{prefix}-{text}"


def paint(utilidad: str, valor: Any) -> tuple[str, str]:
    """Clases y CSS para una utilidad, acepte token, clase o valor literal.

    ```pycon
    >>> paint("bg", colors.slate_100)
    ('bg-slate-100', '')
    >>> paint("bg", colors.hex("#876005"))
    ('', 'background-color: #876005')
    ```

    Es la vía para que las opciones propias de los controles (``header_bg``,
    ``title_bg``, ``zebra``…) admitan lo mismo que ``bg=``: un token de la
    paleta, una clase escrita a mano, un ``hex()``, un ``rgb()`` o un degradado.
    """
    if valor is None or valor == "":
        return "", ""
    clases, declaraciones = resolve_style_props({utilidad: valor})
    estilo = "; ".join(f"{nombre}: {dato}" for nombre, dato in declaraciones.items())
    return " ".join(clases), estilo


def style_attr(estilo: str) -> str:
    """``style_attr("color: red")`` → ``' style="color: red"'`` (o ``""``)."""
    if not estilo:
        return ""
    from .html import escape

    return f' style="{escape(estilo)}"'


def juntar_estilos(*partes: str) -> str:
    """Une declaraciones CSS saltándose las vacías."""
    return "; ".join(parte for parte in partes if parte)
