"""Controles avanzados: editores, markdown, terminal e incrustaciones."""

from __future__ import annotations

import html as _html
import re
from typing import Any, Sequence

from ..base import Component, bind_many
from ..context import RenderContext
from ..html import escape, raw
from ..icons import Icon
from ..style import tw

__all__ = [
    "Html", "CodeEditor", "RichTextEditor", "Markdown", "Terminal", "Iframe", "Canvas",
    "KeyValueEditor", "ProgressTable",
]


class Html(Component):
    """Escotilla de escape: inserta HTML literal (confía en el contenido)."""

    tag = ""

    def __init__(self, markup: str = "", **props: Any) -> None:
        self.markup = markup
        super().__init__(**props)

    def render(self, ctx: RenderContext, path: str) -> str:
        return self.markup


class CodeEditor(Component):
    """Editor de código simple: área de texto monoespaciada con numeración."""

    tag = "div"

    def __init__(
        self,
        value: str = "",
        *,
        language: str | None = None,
        line_numbers: bool = True,
        readonly: bool = False,
        rows: int = 14,
        max_h: str = "none",
        placeholder: str | None = None,
        on_change: Any = None,
        **props: Any,
    ) -> None:
        self.value = value or ""
        self.language = language
        self.line_numbers = line_numbers
        self.readonly = readonly
        self.rows = rows
        self.max_h = max_h
        self.placeholder = placeholder
        if on_change is not None:
            props["on_input"] = on_change
            props["on_change"] = on_change
        props["base_class"] = tw(
            "overflow-hidden rounded-xl border border-slate-800 bg-slate-950 shadow-sm",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        lines = self.value.count("\n") + 1
        gutter = ""
        if self.line_numbers:
            numbers = "".join(
                f'<div class="text-right text-slate-600">{index + 1}</div>' for index in range(lines)
            )
            gutter = (
                f'<div class="select-none border-r border-slate-800 px-3 py-3 text-[12.5px] leading-relaxed '
                f'font-mono">{numbers}</div>'
            )
        header = (
            '<div class="flex items-center justify-between border-b border-slate-800 bg-slate-900/70 px-3 py-1.5">'
            f'<span class="font-mono text-[11px] uppercase tracking-wide text-slate-500">'
            f"{escape(self.language or 'texto')}</span>"
            f'<span class="text-[11px] text-slate-600">{lines} líneas</span></div>'
            if self.language or True
            else ""
        )
        overflow = "overflow-auto" if self.max_h != "none" else ""
        height = f"max-h-{self.max_h}" if self.max_h != "none" else ""
        attrs = (
            f'id="{escape(uid)}" data-iui-on="input,change" data-iui-debounce="400" '
            f'rows="{self.rows}" spellcheck="false"'
            + (" readonly" if self.readonly else "")
            + (f' placeholder="{escape(self.placeholder)}"' if self.placeholder else "")
        )
        return (
            f"{header}<div class=\"flex {overflow} {height}\">{gutter}"
            f'<textarea {attrs} class="w-full resize-none border-0 bg-transparent p-3 font-mono '
            f'text-[12.5px] leading-relaxed text-slate-100 placeholder:text-slate-600 '
            f'focus:outline-none">{escape(self.value)}</textarea></div>'
        )


class RichTextEditor(Component):
    """Editor de texto enriquecido (``contenteditable`` + comandos nativos)."""

    tag = "div"

    def __init__(
        self,
        value: str = "",
        *,
        on_change: Any = None,
        min_h: str = "40",
        toolbar: bool = True,
        **props: Any,
    ) -> None:
        self.value = value or ""
        self.min_h = min_h
        self.toolbar = toolbar
        if on_change is not None:
            props["on_input"] = on_change
        props["base_class"] = tw(
            "overflow-hidden rounded-xl border border-slate-300 bg-white shadow-sm "
            "focus-within:border-indigo-500 focus-within:ring-2 focus-within:ring-indigo-500/25 "
            "dark:border-slate-700 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        tools = [
            ("bold", "B", "Negrita"),
            ("italic", "I", "Cursiva"),
            ("underline", "U", "Subrayado"),
            ("insertUnorderedList", "•", "Lista"),
            ("insertOrderedList", "1.", "Lista numerada"),
            ("formatBlock:h2", "H", "Encabezado"),
            ("removeFormat", "✕", "Limpiar formato"),
        ]
        bar = ""
        if self.toolbar:
            buttons = "".join(
                f'<button type="button" data-iui-rt="{escape(command.split(":")[0])}" '
                + (f'data-iui-rt-value="{escape(command.split(":")[1])}" ' if ":" in command else "")
                + f'data-iui-rt-target="{escape(uid)}" title="{escape(title)}" '
                'class="flex h-7 min-w-7 items-center justify-center rounded px-1.5 text-xs font-semibold '
                'text-slate-600 transition hover:bg-slate-200 dark:text-slate-300 dark:hover:bg-slate-700">'
                f"{escape(label)}</button>"
                for command, label, title in tools
            )
            bar = (
                '<div class="flex flex-wrap items-center gap-0.5 border-b border-slate-200 bg-slate-50 '
                f'px-2 py-1 dark:border-slate-700 dark:bg-slate-800/60">{buttons}</div>'
            )
        return (
            f"{bar}"
            f'<div id="{escape(uid)}" contenteditable="true" data-iui-on="input" data-iui-debounce="400" '
            f'class="min-h-{self.min_h} max-h-[32rem] overflow-y-auto p-3 text-sm leading-relaxed '
            'text-slate-800 focus:outline-none dark:text-slate-100">'
            f"{self.value}</div>"
        )


class Markdown(Component):
    """Renderizador markdown ligero (subconjunto habitual)."""

    tag = "div"

    def __init__(self, text: str = "", **props: Any) -> None:
        self.text = text or ""
        props["base_class"] = tw("prose-sm max-w-none text-slate-700 dark:text-slate-200",
                                 props.get("base_class"))
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        return render_markdown(self.text)


def render_markdown(text: str) -> str:
    blocks: list[str] = []
    lines = text.split("\n")
    index = 0
    paragraph: list[str] = []

    def flush() -> None:
        if paragraph:
            body = " ".join(paragraph).strip()
            if body:
                blocks.append(f'<p class="my-2 leading-relaxed">{_inline(body)}</p>')
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush()
            index += 1
            code: list[str] = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code.append(lines[index])
                index += 1
            blocks.append(
                '<pre class="my-3 overflow-x-auto rounded-lg bg-slate-950 p-3 text-[12.5px] text-slate-100">'
                f'<code class="font-mono">{escape(chr(10).join(code))}</code></pre>'
            )
            index += 1
            continue
        heading = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if heading:
            flush()
            level = len(heading.group(1))
            size = {1: "text-2xl", 2: "text-xl", 3: "text-lg"}.get(level, "text-base")
            blocks.append(
                f'<h{level} class="mt-4 mb-2 {size} font-semibold text-slate-900 dark:text-white">'
                f"{_inline(heading.group(2))}</h{level}>"
            )
            index += 1
            continue
        if stripped in ("---", "***"):
            flush()
            blocks.append('<hr class="my-4 border-slate-200 dark:border-slate-800"/>')
            index += 1
            continue
        if stripped.startswith(">"):
            flush()
            quote: list[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote.append(lines[index].strip().lstrip(">").strip())
                index += 1
            blocks.append(
                '<blockquote class="my-3 border-l-4 border-indigo-400 pl-3 italic text-slate-600 '
                f'dark:text-slate-300">{_inline(" ".join(quote))}</blockquote>'
            )
            continue
        bullet = re.match(r"^[-*+]\s+(.*)$", stripped)
        if bullet:
            flush()
            items = []
            while index < len(lines):
                match = re.match(r"^[-*+]\s+(.*)$", lines[index].strip())
                if not match:
                    break
                items.append(f"<li>{_inline(match.group(1))}</li>")
                index += 1
            blocks.append(f'<ul class="my-2 ml-5 list-disc space-y-1">{"".join(items)}</ul>')
            continue
        numbered = re.match(r"^\d+[.)]\s+(.*)$", stripped)
        if numbered:
            flush()
            items = []
            while index < len(lines):
                match = re.match(r"^\d+[.)]\s+(.*)$", lines[index].strip())
                if not match:
                    break
                items.append(f"<li>{_inline(match.group(1))}</li>")
                index += 1
            blocks.append(f'<ol class="my-2 ml-5 list-decimal space-y-1">{"".join(items)}</ol>')
            continue
        if not stripped:
            flush()
            index += 1
            continue
        paragraph.append(stripped)
        index += 1
    flush()
    return "".join(blocks)


def _inline(text: str) -> str:
    out = escape(text)
    out = re.sub(r"`([^`]+)`",
                 lambda m: f'<code class="rounded bg-slate-100 px-1 py-0.5 font-mono text-[0.85em] '
                           f'text-rose-600 dark:bg-slate-800 dark:text-rose-300">{m.group(1)}</code>', out)
    out = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"__([^_]+)__", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", out)
    out = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                 r'<a class="text-indigo-600 underline underline-offset-2 dark:text-indigo-400" href="\2">\1</a>', out)
    return out.replace("&amp;lt;", "&lt;")


class Terminal(Component):
    tag = "div"

    def __init__(
        self,
        lines: Sequence[Any] | None = None,
        *,
        prompt: str = "$",
        title: str = "terminal",
        max_h: str = "72",
        **props: Any,
    ) -> None:
        self.lines = list(lines or [])
        self.prompt = prompt
        self.term_title = title
        self.max_h = max_h
        props["base_class"] = tw(
            "overflow-hidden rounded-xl border border-slate-800 bg-slate-950 font-mono shadow-inner",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        rows = "".join(
            '<div class="whitespace-pre-wrap text-slate-300">'
            f'<span class="text-emerald-400">{escape(self.prompt)}</span> {escape(line)}</div>'
            for line in self.lines
        )
        return (
            '<div class="flex items-center gap-1.5 border-b border-slate-800 bg-slate-900/70 px-3 py-2">'
            '<span class="h-2.5 w-2.5 rounded-full bg-rose-500/80"></span>'
            '<span class="h-2.5 w-2.5 rounded-full bg-amber-400/80"></span>'
            '<span class="h-2.5 w-2.5 rounded-full bg-emerald-500/80"></span>'
            f'<span class="ml-2 text-[11px] text-slate-500">{escape(self.term_title)}</span></div>'
            f'<div class="max-h-{self.max_h} overflow-auto px-3 py-2 text-[12.5px] leading-relaxed">{rows}'
            f'<div class="text-slate-300"><span class="text-emerald-400">{escape(self.prompt)}</span> '
            '<span class="ml-0.5 inline-block h-4 w-2 animate-pulse bg-slate-400 align-middle"></span></div></div>'
        )


class Iframe(Component):
    tag = "iframe"

    def __init__(
        self,
        src: str | None = None,
        *,
        srcdoc: str | None = None,
        height: str = "420",
        sandbox: str = "allow-scripts allow-forms allow-popups",
        **props: Any,
    ) -> None:
        if src:
            props["src"] = src
        if srcdoc:
            props["srcdoc"] = srcdoc
        props["sandbox"] = sandbox
        props["base_class"] = tw(f"h-{height} w-full rounded-xl border border-slate-200 "
                                 "dark:border-slate-800", props.get("base_class"))
        super().__init__(**props)


class Canvas(Component):
    tag = "canvas"

    def __init__(self, width: int = 400, height: int = 200, *, script: str | None = None, **props: Any) -> None:
        self.script = script
        props["width"] = width
        props["height"] = height
        props["base_class"] = tw("w-full rounded-xl border border-slate-200 bg-white "
                                 "dark:border-slate-800 dark:bg-slate-900", props.get("base_class"))
        super().__init__(**props)

    def wrap(self, html: str, ctx: RenderContext, uid: str) -> str:
        if not self.script:
            return html
        return html + f"<script>window.interui && window.interui.run({uid!r})</script>"


class KeyValueEditor(Component):
    """Editor de pares clave/valor con alta y baja de filas."""

    tag = "div"

    def __init__(
        self,
        items: dict[str, Any] | Sequence[Any] | None = None,
        *,
        on_change: Any = None,
        on_add: Any = None,
        on_remove: Any = None,
        **props: Any,
    ) -> None:
        self.items = list(items.items()) if isinstance(items, dict) else list(items or [])
        if on_change is not None:
            props["on_change"] = on_change
        if on_add is not None:
            props["on_add"] = on_add
        if on_remove is not None:
            props["on_remove"] = on_remove
        props["base_class"] = tw("flex flex-col gap-2", props.get("base_class"))
        super().__init__(**props)

    def render(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        bind_many(ctx, uid, {"remove": self.handlers.get("remove")},
                  [f"r{index}" for index in range(len(self.items))])
        bind_many(ctx, uid, {"add": self.handlers.get("add")}, ["add"])
        return super().render(ctx, path)

    def content(self, ctx: RenderContext, path: str) -> str:
        uid = ctx.uid(path, self.key, self.explicit_id)
        base = (
            "h-9 w-full rounded-lg border border-slate-300 bg-white px-2.5 text-sm text-slate-800 "
            "shadow-sm focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/25 focus:outline-none "
            "dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100"
        )
        rows = "".join(
            '<div class="flex items-center gap-2">'
            f'<input type="text" value="{escape(key)}" placeholder="clave" class="{base} max-w-40"/>'
            f'<input type="text" value="{escape(value)}" placeholder="valor" class="{base}"/>'
            f'<button type="button" id="{escape(uid)}-r{index}" data-iui-emit="remove" '
            f'data-iui-value="{index}" data-iui-cast="int" aria-label="Eliminar fila" '
            'class="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg text-slate-400 '
            'transition hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-500/10">'
            + Icon("trash", size=4).render(ctx, f"{uid}-ri{index}")
            + "</button></div>"
            for index, (key, value) in enumerate(self.items)
        )
        return (
            f"{rows}"
            f'<button type="button" id="{escape(uid)}-add" data-iui-emit="add" '
            'class="inline-flex h-9 items-center gap-1.5 self-start rounded-lg border border-dashed '
            'border-slate-300 px-3 text-sm font-medium text-slate-600 transition hover:border-indigo-400 '
            'hover:text-indigo-600 dark:border-slate-700 dark:text-slate-300">'
            + Icon("plus", size=4).render(ctx, uid + "-ai")
            + "Añadir fila</button>"
        )


class ProgressTable(Component):
    """Tabla compacta con barras de progreso por fila."""

    tag = "div"

    def __init__(self, rows: Sequence[Any] | None = None, *, max_value: float = 100, **props: Any) -> None:
        self.rows = list(rows or [])
        self.max_value = max_value or 100
        props["base_class"] = tw(
            "overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm "
            "dark:border-slate-800 dark:bg-slate-900",
            props.get("base_class"),
        )
        super().__init__(**props)

    def content(self, ctx: RenderContext, path: str) -> str:
        items = []
        for row in self.rows:
            label = row.get("label", "") if isinstance(row, dict) else str(row)
            value = float(row.get("value", 0)) if isinstance(row, dict) else 0.0
            percent = max(0.0, min(100.0, value / self.max_value * 100))
            items.append(
                '<div class="flex items-center gap-3 px-3 py-2">'
                f'<span class="w-32 shrink-0 truncate text-sm text-slate-700 dark:text-slate-200">{escape(label)}</span>'
                '<div class="h-2 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-800">'
                f'<div class="h-full rounded-full bg-indigo-500" style="width:{percent:.1f}%"></div></div>'
                f'<span class="w-10 shrink-0 text-right text-xs font-medium text-slate-500">{percent:.0f}%</span>'
                "</div>"
            )
        return "".join(items)


_ = raw, _html
