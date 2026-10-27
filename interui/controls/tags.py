"""Etiquetas HTML básicas listas para usar en el árbol de componentes."""

from __future__ import annotations

from typing import Any

from ..base import Component
from ..html import Markup
from ..style import tw

__all__ = [
    "Div", "Span", "Section", "Article", "Header", "Main", "Aside", "Nav", "P", "H1",
    "H2", "H3", "H4", "H5", "H6", "Ul", "Ol", "Li", "A", "Img", "Hr", "Br", "Pre",
    "B", "I", "U", "S", "Sub", "Sup", "Time", "Figure", "Figcaption", "Details",
    "Summary", "DetailsBlock", "Template",
]


class Div(Component):
    tag = "div"


class Span(Component):
    tag = "span"


class Section(Component):
    tag = "section"


class Article(Component):
    tag = "article"


class Header(Component):
    tag = "header"


class Main(Component):
    tag = "main"

    def __init__(self, *children: Any, **props: Any) -> None:
        props.setdefault("base_class", "flex-1")
        super().__init__(*children, **props)


class Aside(Component):
    tag = "aside"


class Nav(Component):
    tag = "nav"


class P(Component):
    tag = "p"


class H1(Component):
    tag = "h1"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("text-3xl font-semibold tracking-tight", props.get("base_class"))
        super().__init__(*children, **props)


class H2(Component):
    tag = "h2"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("text-2xl font-semibold tracking-tight", props.get("base_class"))
        super().__init__(*children, **props)


class H3(Component):
    tag = "h3"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("text-xl font-semibold", props.get("base_class"))
        super().__init__(*children, **props)


class H4(Component):
    tag = "h4"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("text-lg font-semibold", props.get("base_class"))
        super().__init__(*children, **props)


class H5(Component):
    tag = "h5"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("text-base font-semibold", props.get("base_class"))
        super().__init__(*children, **props)


class H6(Component):
    tag = "h6"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("text-sm font-semibold uppercase tracking-wide", props.get("base_class"))
        super().__init__(*children, **props)


class Ul(Component):
    tag = "ul"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("ml-5 list-disc space-y-1 text-sm", props.get("base_class"))
        super().__init__(*children, **props)


class Ol(Component):
    tag = "ol"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("ml-5 list-decimal space-y-1 text-sm", props.get("base_class"))
        super().__init__(*children, **props)


class Li(Component):
    tag = "li"


class A(Component):
    tag = "a"

    def __init__(self, *children: Any, href: str = "#", **props: Any) -> None:
        props["href"] = href
        props["base_class"] = tw(
            "font-medium text-indigo-600 underline-offset-4 hover:underline dark:text-indigo-400",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class Img(Component):
    tag = "img"

    def __init__(self, src: str = "", *, alt: str = "", **props: Any) -> None:
        props["src"] = src
        props["alt"] = alt
        super().__init__(**props)


class Hr(Component):
    tag = "hr"

    def __init__(self, **props: Any) -> None:
        props["base_class"] = tw("my-4 border-slate-200 dark:border-slate-800", props.get("base_class"))
        super().__init__(**props)


class Br(Component):
    tag = "br"

    def __init__(self, **props: Any) -> None:
        super().__init__(**props)


class Pre(Component):
    tag = "pre"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw(
            "overflow-auto rounded-lg bg-slate-950 p-3 font-mono text-[12.5px] text-slate-100",
            props.get("base_class"),
        )
        super().__init__(*children, **props)


class B(Component):
    tag = "b"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("font-semibold", props.get("base_class"))
        super().__init__(*children, **props)


class I(Component):
    tag = "i"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("italic", props.get("base_class"))
        super().__init__(*children, **props)


class U(Component):
    tag = "u"


class S(Component):
    tag = "s"


class Sub(Component):
    tag = "sub"


class Sup(Component):
    tag = "sup"


class Time(Component):
    tag = "time"


class Figure(Component):
    tag = "figure"


class Figcaption(Component):
    tag = "figcaption"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("mt-1 text-xs text-slate-500 dark:text-slate-400", props.get("base_class"))
        super().__init__(*children, **props)


class Details(Component):
    tag = "details"

    def __init__(self, *children: Any, open: bool = False, **props: Any) -> None:
        if open:
            props["open"] = True
        props["base_class"] = tw(
            "rounded-lg border border-slate-200 p-3 dark:border-slate-800", props.get("base_class")
        )
        super().__init__(*children, **props)


class Summary(Component):
    tag = "summary"

    def __init__(self, *children: Any, **props: Any) -> None:
        props["base_class"] = tw("cursor-pointer text-sm font-medium", props.get("base_class"))
        super().__init__(*children, **props)


DetailsBlock = Details


class Template(Component):
    """Envoltura sin etiqueta semántica útil para composición."""

    tag = "div"


def _ensure_markup(value: Any) -> Markup:
    return value if isinstance(value, Markup) else Markup(str(value))
