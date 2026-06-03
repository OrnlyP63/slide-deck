"""
Markdown → ParsedDeck converter.

Conventions:
  # H1            → deck title + TitleSlide (index 0)
  ## H2           → SectionSlide
  ### H3          → content slide; body determines type via FFT
  #### H4 (×2)   → TwoColumnSlide columns
  - / * bullet    → BulletPoint (ContentSlide)
  1. 2. 3.        → TimelineSlide
  | table |       → TableSlide
  **Label:** Val  → StatsSlide (≥2 non-SCR bold-key lines)
  **Situation/Complication/Resolution:** → SCRNarrativeSlide
  > "quote"       → QuoteSlide
  > — Attribution → quote attribution
  > blockquote    → source attribution
  ![lbl](desc)    → ChartPlaceholderSlide
  <!-- closing --> → ClosingSlide
  <!-- agenda -->  → AgendaSlide
  <!-- notes: ... → presenter notes
  <!-- author: ...→ deck author metadata
  <!-- theme: ... → theme name
"""

from __future__ import annotations

import re
from pathlib import Path

from slides.model import (
    AgendaSlide,
    BulletPoint,
    ChartPlaceholderSlide,
    ClosingSlide,
    ContentSlide,
    ParsedDeck,
    QuoteSlide,
    SCRNarrativeSlide,
    SectionSlide,
    Slide,
    Stat,
    StatsSlide,
    TableSlide,
    TimelineSlide,
    TitleSlide,
    TwoColumnSlide,
)
from slides.selector import ContentSignals, DEFAULT_FFT

_H1 = re.compile(r"^#\s+(.+)$")
_H2 = re.compile(r"^##\s+(.+)$")
_H3 = re.compile(r"^###\s+(.+)$")
_H4 = re.compile(r"^####\s+(.+)$")
_BULLET = re.compile(r"^\s*[-*]\s+(.+)$")
_ORDERED = re.compile(r"^\s*\d+\.\s+(.+)$")
_BLOCKQUOTE = re.compile(r"^>\s*(.+)$")
_SCR = re.compile(r"^\*\*(Situation|Complication|Resolution):\*\*\s*(.+)$", re.IGNORECASE)
_STAT = re.compile(r"^\*\*(?!Situation|Complication|Resolution)([^*:]+):\*\*\s*(.+)$", re.IGNORECASE)
_IMAGE = re.compile(r"^!\[([^\]]*)\]\(([^)]*)\)\s*$")
_TABLE_ROW = re.compile(r"^\|(.+)\|$")
_TABLE_SEP = re.compile(r"^\|[-| :]+\|$")
_NOTES = re.compile(r"<!--\s*notes:\s*(.+?)\s*-->", re.IGNORECASE)
_AUTHOR = re.compile(r"<!--\s*author:\s*(.+?)\s*-->", re.IGNORECASE)
_THEME = re.compile(r"<!--\s*theme:\s*(.+?)\s*-->", re.IGNORECASE)
_CLOSING = re.compile(r"<!--\s*(closing|thank.?you)\s*-->", re.IGNORECASE)
_AGENDA = re.compile(r"<!--\s*agenda\s*-->", re.IGNORECASE)
_QUOTE_LINE = re.compile(r'^["“](.+?)["”]?\s*$')
_ATTRIBUTION = re.compile(r"^[—\-]{1,3}\s*(.+)$")
_URL = re.compile(r"https?://\S+")
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}")


def _classify_body(index: int, action_title: str, body: list[str]) -> Slide:  # noqa: C901
    source = notes = ""
    bullets: list[BulletPoint] = []
    steps: list[str] = []
    agenda_items: list[str] = []
    scr: dict[str, str] = {}
    stats: list[Stat] = []
    chart_label = chart_desc = ""
    columns: list[tuple[str, list[BulletPoint]]] = []
    col_header: str | None = None
    col_bullets: list[BulletPoint] = []
    table_rows: list[list[str]] = []
    table_headers: list[str] = []
    quote = attribution = contact = website = ""
    has_closing = has_agenda = False
    last_was_quote = False

    for line in body:
        if m := _NOTES.search(line):
            notes = m.group(1)
            continue
        if _CLOSING.search(line):
            has_closing = True
            continue
        if _AGENDA.search(line):
            has_agenda = True
            continue
        if _AUTHOR.search(line):
            continue
        if _THEME.search(line):
            continue

        # Blockquote — quote OR source OR attribution
        if m := _BLOCKQUOTE.match(line):
            raw = m.group(1).strip()
            # Attribution line (starts with em-dash or ---)
            if ma := _ATTRIBUTION.match(raw):
                if last_was_quote:
                    attribution = ma.group(1).strip()
                    last_was_quote = False
                    continue
            # Quote line (starts with " or ")
            if mq := _QUOTE_LINE.match(raw):
                quote = mq.group(1).strip()
                last_was_quote = True
                continue
            last_was_quote = False
            src = raw
            source = src[7:].strip() if src.lower().startswith("source:") else src
            continue

        last_was_quote = False

        # H4 column header
        if m := _H4.match(line):
            if col_header is not None:
                columns.append((col_header, col_bullets))
            col_header = m.group(1).strip()
            col_bullets = []
            continue

        # Image (chart)
        if m := _IMAGE.match(line):
            chart_label = m.group(1).strip()
            chart_desc = m.group(2).strip()
            continue

        # SCR field
        if m := _SCR.match(line):
            scr[m.group(1).lower()] = m.group(2).strip()
            continue

        # Stat field (non-SCR bold-key)
        if m := _STAT.match(line):
            stats.append(Stat(label=m.group(1).strip(), value=m.group(2).strip()))
            continue

        # Table row
        if _TABLE_SEP.match(line):
            continue  # skip separator rows
        if m := _TABLE_ROW.match(line):
            cells = [c.strip() for c in m.group(1).split("|")]
            if not table_headers:
                table_headers = cells
            else:
                table_rows.append(cells)
            continue

        # Ordered list (timeline / agenda items)
        if m := _ORDERED.match(line):
            text = m.group(1).strip()
            steps.append(text)
            if has_agenda:
                agenda_items.append(text)
            continue

        # Bullet
        if m := _BULLET.match(line):
            bp = BulletPoint(text=m.group(1).strip())
            if col_header is not None:
                col_bullets.append(bp)
            elif has_closing:
                # bullets in closing slide = contact lines
                t = m.group(1).strip()
                if _URL.search(t):
                    website = t
                elif _EMAIL.search(t):
                    contact = t
                else:
                    contact = contact or t
            else:
                bullets.append(bp)
            continue

        # Plain line in closing slide = contact info
        if has_closing and line.strip():
            t = line.strip()
            if _URL.search(t):
                website = t
            elif _EMAIL.search(t):
                contact = t

    if col_header is not None:
        columns.append((col_header, col_bullets))

    signals = ContentSignals(
        is_opener=index == 0,
        is_section=False,
        has_closing=has_closing,
        has_agenda=has_agenda,
        has_scr=all(k in scr for k in ("situation", "complication", "resolution")),
        has_quote=bool(quote),
        has_stats=len(stats) >= 2,
        has_chart=bool(chart_label or chart_desc),
        has_timeline=len(steps) >= 2 and not has_agenda,
        has_columns=len(columns) == 2,
        has_table=bool(table_headers),
        has_bullets=bool(bullets) or any(b for _, b in columns),
    )
    template = DEFAULT_FFT.classify(signals)
    base = dict(action_title=action_title, source=source, notes=notes)

    match template:
        case "TitleSlide":
            return TitleSlide(**base)
        case "SectionSlide":
            return SectionSlide(**base)
        case "ClosingSlide":
            return ClosingSlide(**base, contact=contact, website=website)
        case "AgendaSlide":
            items = agenda_items if agenda_items else steps
            return AgendaSlide(**base, items=items)
        case "SCRNarrativeSlide":
            return SCRNarrativeSlide(
                **base,
                situation=scr.get("situation", ""),
                complication=scr.get("complication", ""),
                resolution=scr.get("resolution", ""),
            )
        case "QuoteSlide":
            return QuoteSlide(**base, quote=quote, attribution=attribution)
        case "StatsSlide":
            return StatsSlide(**base, stats=stats)
        case "ChartPlaceholderSlide":
            return ChartPlaceholderSlide(**base, chart_label=chart_label, chart_description=chart_desc)
        case "TimelineSlide":
            return TimelineSlide(**base, steps=steps)
        case "TwoColumnSlide":
            (lh, lb), (rh, rb) = columns[0], columns[1]
            return TwoColumnSlide(**base, left_header=lh, left_bullets=lb, right_header=rh, right_bullets=rb)
        case "TableSlide":
            return TableSlide(**base, headers=table_headers, rows=table_rows)
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
