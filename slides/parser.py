"""
Markdown → ParsedDeck converter.

Conventions:
  # H1          → deck title + TitleSlide (index 0)
  ## H2         → SectionSlide
  ### H3        → content slide; body determines type via FFT
  #### H4 (×2) → TwoColumnSlide columns
  - / * bullet  → BulletPoint
  > blockquote  → source attribution
  **Label:**    → SCR field (Situation / Complication / Resolution)
  ![lbl](desc)  → ChartPlaceholderSlide
  <!-- notes: →  presenter notes (any slide)
  <!-- author:   deck author metadata
  <!-- theme:    theme name (consulting / minimal / dark)
"""

from __future__ import annotations

import re
from pathlib import Path

from slides.model import (
    BulletPoint,
    ChartPlaceholderSlide,
    ContentSlide,
    ParsedDeck,
    SCRNarrativeSlide,
    SectionSlide,
    Slide,
    TitleSlide,
    TwoColumnSlide,
)
from slides.selector import ContentSignals, DEFAULT_FFT

_H1 = re.compile(r"^#\s+(.+)$")
_H2 = re.compile(r"^##\s+(.+)$")
_H3 = re.compile(r"^###\s+(.+)$")
_H4 = re.compile(r"^####\s+(.+)$")
_BULLET = re.compile(r"^\s*[-*]\s+(.+)$")
_BLOCKQUOTE = re.compile(r"^>\s*(.+)$")
_SCR = re.compile(r"^\*\*(Situation|Complication|Resolution):\*\*\s*(.+)$", re.IGNORECASE)
_IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]*)\)\s*$")
_NOTES = re.compile(r"<!--\s*notes:\s*(.+?)\s*-->", re.IGNORECASE)
_AUTHOR = re.compile(r"<!--\s*author:\s*(.+?)\s*-->", re.IGNORECASE)
_THEME = re.compile(r"<!--\s*theme:\s*(.+?)\s*-->", re.IGNORECASE)


def _classify_body(index: int, action_title: str, body: list[str]) -> Slide:
    source = ""
    notes = ""
    bullets: list[BulletPoint] = []
    scr: dict[str, str] = {}
    chart_label = ""
    chart_desc = ""
    columns: list[tuple[str, list[BulletPoint]]] = []
    col_header: str | None = None
    col_bullets: list[BulletPoint] = []

    for line in body:
        if m := _NOTES.search(line):
            notes = m.group(1)
            continue
        if m := _AUTHOR.search(line):
            continue  # metadata handled at deck level
        if m := _THEME.search(line):
            continue
        if m := _BLOCKQUOTE.match(line):
            src = m.group(1).strip()
            source = src[7:].strip() if src.lower().startswith("source:") else src
            continue
        if m := _H4.match(line):
            if col_header is not None:
                columns.append((col_header, col_bullets))
            col_header = m.group(1).strip()
            col_bullets = []
            continue
        if m := _IMAGE.match(line):
            chart_label = m.group(1).strip()
            chart_desc = m.group(2).strip()
            continue
        if m := _SCR.match(line):
            scr[m.group(1).lower()] = m.group(2).strip()
            continue
        if m := _BULLET.match(line):
            bp = BulletPoint(text=m.group(1).strip())
            if col_header is not None:
                col_bullets.append(bp)
            else:
                bullets.append(bp)
            continue

    if col_header is not None:
        columns.append((col_header, col_bullets))

    signals = ContentSignals(
        is_opener=index == 0,
        is_section=False,
        has_scr=all(k in scr for k in ("situation", "complication", "resolution")),
        has_chart=bool(chart_label or chart_desc),
        has_columns=len(columns) == 2,
        has_bullets=bool(bullets) or any(b for _, b in columns),
    )
    template = DEFAULT_FFT.classify(signals)
    base = dict(action_title=action_title, source=source, notes=notes)

    match template:
        case "TitleSlide":
            return TitleSlide(**base)
        case "SCRNarrativeSlide":
            return SCRNarrativeSlide(
                **base,
                situation=scr.get("situation", ""),
                complication=scr.get("complication", ""),
                resolution=scr.get("resolution", ""),
            )
        case "ChartPlaceholderSlide":
            return ChartPlaceholderSlide(**base, chart_label=chart_label, chart_description=chart_desc)
        case "TwoColumnSlide":
            (lh, lb), (rh, rb) = columns[0], columns[1]
            return TwoColumnSlide(**base, left_header=lh, left_bullets=lb, right_header=rh, right_bullets=rb)
        case _:
            return ContentSlide(**base, bullets=bullets)


def parse_md(path: str | Path) -> ParsedDeck:
    lines = Path(path).read_text(encoding="utf-8").splitlines()

    title = "Untitled"
    author = ""
    theme = "consulting"
    slides: list[Slide] = []

    cur_h3: str | None = None
    cur_body: list[str] = []

    def flush() -> None:
        if cur_h3 is None:
            return
        slides.append(_classify_body(len(slides), cur_h3, cur_body))

    for line in lines:
        # Deck-level metadata comments (can appear anywhere)
        if m := _AUTHOR.search(line):
            author = m.group(1).strip()
            continue
        if m := _THEME.search(line):
            theme = m.group(1).strip()
            continue

        if m := _H1.match(line):
            flush()
            cur_h3 = None
            cur_body = []
            title = m.group(1).strip()
            slides.append(TitleSlide(action_title=title))
            continue

        if m := _H2.match(line):
            flush()
            cur_h3 = None
            cur_body = []
            slides.append(SectionSlide(action_title=m.group(1).strip()))
            continue

        if m := _H3.match(line):
            flush()
            cur_h3 = m.group(1).strip()
            cur_body = []
            continue

        if cur_h3 is not None:
            cur_body.append(line)

    flush()
    return ParsedDeck(title=title, author=author, theme=theme, slides=slides)
