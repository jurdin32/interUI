"""Los iconos también van con notación de punto: ``icons.car``, ``icons.edit``."""

from __future__ import annotations

import pytest

import interui as ui
from interui import IconName, colors, icons
from interui.icons import ICON_ALIASES, ICON_NAMES


def test_every_icon_is_reachable() -> None:
    """Los 200+ iconos existen como atributo, con ``_`` en vez de ``-``."""
    for name in ICON_NAMES:
        token = getattr(icons, name.replace("-", "_"))
        assert isinstance(token, IconName)
        assert token == name


def test_names_with_dashes() -> None:
    assert icons.chevron_down == "chevron-down"
    assert icons.more_h == "more-h"
    assert icons.arrow_left == "arrow-left"


def test_aliases() -> None:
    assert icons.close == "x"
    assert icons.delete == "trash"
    assert icons.exit == "power"
    for alias, target in ICON_ALIASES.items():
        assert target in ICON_NAMES, f"{alias} apunta a un icono inexistente"


def test_dynamic_lookup() -> None:
    assert icons("car") == "car"
    assert icons("chevron-down") == "chevron-down"
    with pytest.raises(AttributeError):
        icons("no-existe")


def test_unknown_icon_suggests_alternatives() -> None:
    with pytest.raises(AttributeError) as info:
        _ = icons.chevrondown
    assert "chevron" in str(info.value)


def test_namespace_is_discoverable() -> None:
    listing = dir(icons)
    assert "chevron_down" in listing
    assert "close" in listing
    assert len(listing) >= len(ICON_NAMES)


def test_icon_accepts_a_token() -> None:
    html = ui.render(ui.Icon(icons.car))
    assert "<svg" in html
    assert "h-5 w-5" in html


def test_icon_token_takes_options() -> None:
    component = icons.edit(size=8, stroke=2.5)
    assert isinstance(component, ui.Icon)
    html = ui.render(component)
    assert "h-8 w-8" in html
    assert 'stroke-width="2.5"' in html


def test_icon_token_paints_with_color_tokens() -> None:
    html = ui.render(ui.Icon(icons.car, color=colors.red_500))
    assert "text-red-500" in html
    html = ui.render(ui.Icon(icons.car, color=colors.hex("#f00")))
    assert 'style="color: #f00"' in html


def test_icon_token_as_child_renders_the_icon() -> None:
    html = ui.render(ui.Card(icons.edit, ui.Text("Editar")))
    assert "<svg" in html
    assert ">edit<" not in html


def test_plain_strings_are_still_text() -> None:
    assert ui.render(ui.Text("edit")) == (
        '<p id="r" class="text-[15px] text-slate-900 dark:text-slate-100">edit</p>'
    )


def test_icon_argument_accepts_a_token() -> None:
    html = ui.render(ui.Button("Guardar", icon=icons.check))
    assert "<svg" in html
    html = ui.render(ui.Input(icon=icons.search))
    assert "<svg" in html
