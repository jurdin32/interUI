"""La documentación se comprueba como el código: enlaces y estructura.

Un enlace relativo roto o un ancla que ya no existe es un error de
documentación, y se detecta antes de publicar.
"""

from __future__ import annotations

import pathlib
import re

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]

DOCS = [ROOT / "README.md", *sorted((ROOT / "docs").glob("*.md"))]
EXAMPLE_DOCS = sorted((ROOT / "examples").rglob("*.md"))
PAGES = [*DOCS, *EXAMPLE_DOCS]

_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)")


def _slug(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text).strip("-")


def _anchors(path: pathlib.Path) -> set[str]:
    headings = re.findall(r"^#{1,6}\s+(.+)$", path.read_text(encoding="utf-8"), re.M)
    seen: dict[str, int] = {}
    out: set[str] = set()
    for heading in headings:
        base = _slug(heading)
        count = seen.get(base, 0)
        out.add(base if count == 0 else f"{base}-{count}")
        seen[base] = count + 1
    return out


@pytest.mark.parametrize("page", PAGES, ids=lambda p: str(p.relative_to(ROOT)))
def test_los_enlaces_relativos_existen(page: pathlib.Path) -> None:
    for target in _LINK.findall(page.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        file_part, _, anchor = target.partition("#")
        resolved = (page.parent / file_part).resolve() if file_part else page.resolve()
        assert resolved.exists(), f"{page.relative_to(ROOT)}: enlace roto a {target}"
        if anchor and resolved.suffix == ".md":
            assert anchor in _anchors(resolved), (
                f"{page.relative_to(ROOT)}: el ancla #{anchor} no existe en "
                f"{resolved.relative_to(ROOT)}"
            )


def test_el_indice_enlaza_todas_las_paginas() -> None:
    """Toda página de docs/ aparece en el índice de la documentación."""
    index = (ROOT / "docs" / "indice.md").read_text(encoding="utf-8")
    faltan = [
        page.name
        for page in sorted((ROOT / "docs").glob("*.md"))
        if page.name != "indice.md" and f"({page.name})" not in index and f"({page.name}#" not in index
    ]
    assert not faltan, f"páginas sin enlace desde docs/indice.md: {faltan}"
