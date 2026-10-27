import pytest

import interui as ui
from interui.html import Markup, attr_string, element, escape, raw
from interui.style import tw


def test_escape_blocks_markup():
    assert escape("<script>alert(1)</script>") == "&lt;script&gt;alert(1)&lt;/script&gt;"
    assert escape('a "b" & c') == "a &quot;b&quot; &amp; c"


def test_markup_is_not_escaped_again():
    safe = raw("<b>hola</b>")
    assert isinstance(safe, Markup)
    assert escape(safe) == "<b>hola</b>"


def test_attr_string_handles_booleans_lists_and_none():
    html = attr_string({"disabled": True, "hidden": False, "title": None, "class": ["a", "b"]})
    assert "disabled" in html
    assert "hidden" not in html
    assert "title" not in html
    assert 'class="a b"' in html


def test_element_void_tags_are_self_closed():
    assert element("img", src="a.png") == '<img src="a.png" />'
    assert element("div", "x", role="main") == '<div role="main">x</div>'


def test_text_children_are_escaped_but_components_render():
    node = ui.Div("<b>no</b>", ui.Strong("sí"))
    html = ui.render(node)
    assert "&lt;b&gt;no&lt;/b&gt;" in html
    assert "<strong" in html


class TestTw:
    @pytest.mark.parametrize(
        ("raw_classes", "expected"),
        [
            ("p-2 p-6", "p-6"),
            ("p-2 px-4", "p-2 px-4"),
            ("flex flex-col", "flex flex-col"),
            ("hidden flex", "flex"),
            ("rounded-lg rounded-full", "rounded-full"),
            ("text-sm text-slate-900", "text-sm text-slate-900"),
            ("border border-slate-200 border-t", "border border-slate-200 border-t"),
            ("ring-1 ring-inset ring-slate-200", "ring-1 ring-inset ring-slate-200"),
            ("divide-y divide-slate-100", "divide-y divide-slate-100"),
            ("shadow-sm shadow-lg", "shadow-lg"),
            ("bg-slate-50 dark:bg-slate-950", "bg-slate-50 dark:bg-slate-950"),
            ("hover:bg-x hover:bg-y", "hover:bg-y"),
            ("w-full h-10 w-4", "h-10 w-4"),
        ],
    )
    def test_conflicts(self, raw_classes, expected):
        assert tw(raw_classes) == expected

    def test_accepts_dicts_and_lists(self):
        assert tw({"p-2": True, "p-8": False}, ["gap-2", "gap-4"]) == "p-2 gap-4"

    def test_user_class_wins(self):
        card = ui.Card(class_="p-10")
        assert "p-10" in card.base_class.split() or "p-10" in card.class_
        html = ui.render(card)
        assert 'class="' in html
        assert "p-10" in html
