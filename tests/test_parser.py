"""Tests for slides/parser.py — Markdown → ParsedDeck conversion."""

import textwrap
from pathlib import Path

import pytest

from slides.model import (
    ChartPlaceholderSlide,
    ContentSlide,
    ParsedDeck,
    SCRNarrativeSlide,
    SectionSlide,
    TitleSlide,
    TwoColumnSlide,
)
from slides.parser import parse_md


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "deck.md"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def _write_slide(tmp_path: Path, content: str) -> Path:
    """Prefix with H1 so the H3 slide under test is never at index 0."""
    return _write(tmp_path, "# Deck Title\n" + textwrap.dedent(content))


# ---------------------------------------------------------------------------
# Deck-level metadata
# ---------------------------------------------------------------------------

class TestDeckMetadata:
    def test_h1_sets_title(self, tmp_path):
        f = _write(tmp_path, "# My Deck\n")
        deck = parse_md(f)
        assert deck.title == "My Deck"

    def test_author_comment(self, tmp_path):
        f = _write(tmp_path, "<!-- author: Jane Smith -->\n# Deck\n")
        assert parse_md(f).author == "Jane Smith"

    def test_theme_comment(self, tmp_path):
        f = _write(tmp_path, "<!-- theme: startup -->\n# Deck\n")
        assert parse_md(f).theme == "startup"

    def test_defaults_when_no_metadata(self, tmp_path):
        f = _write(tmp_path, "### Plain slide\n- bullet\n")
        deck = parse_md(f)
        assert deck.title == "Untitled"
        assert deck.author == ""
        assert deck.theme == "consulting"

    def test_metadata_comments_anywhere(self, tmp_path):
        f = _write(tmp_path, "# Title\n<!-- author: Bob -->\n<!-- theme: dark -->\n")
        deck = parse_md(f)
        assert deck.author == "Bob"
        assert deck.theme == "dark"


# ---------------------------------------------------------------------------
# Heading → slide type mapping
# ---------------------------------------------------------------------------

class TestHeadingDispatch:
    def test_h1_produces_title_slide(self, tmp_path):
        f = _write(tmp_path, "# Deck Title\n")
        deck = parse_md(f)
        assert len(deck.slides) == 1
        assert isinstance(deck.slides[0], TitleSlide)
        assert deck.slides[0].action_title == "Deck Title"

    def test_h2_produces_section_slide(self, tmp_path):
        f = _write(tmp_path, "## Section One\n")
        deck = parse_md(f)
        assert isinstance(deck.slides[0], SectionSlide)
        assert deck.slides[0].action_title == "Section One"

    def test_h3_plain_bullets_produces_content_slide(self, tmp_path):
        f = _write_slide(tmp_path, "### Slide title\n- bullet\n")
        deck = parse_md(f)
        assert isinstance(deck.slides[1], ContentSlide)

    def test_multiple_headings_produce_correct_sequence(self, tmp_path):
        f = _write(tmp_path, """\
            # Title
            ## Section
            ### Content slide
            - bullet
        """)
        deck = parse_md(f)
        assert [type(s).__name__ for s in deck.slides] == [
            "TitleSlide", "SectionSlide", "ContentSlide"
        ]


# ---------------------------------------------------------------------------
# ContentSlide — bullets and body text
# ---------------------------------------------------------------------------

class TestContentSlide:
    def test_bullets_parsed(self, tmp_path):
        f = _write_slide(tmp_path, "### Slide\n- first\n- second\n- third\n")
        slide = parse_md(f).slides[1]
        assert isinstance(slide, ContentSlide)
        assert [b.text for b in slide.bullets] == ["first", "second", "third"]

    def test_star_bullets_parsed(self, tmp_path):
        f = _write_slide(tmp_path, "### Slide\n* alpha\n* beta\n")
        slide = parse_md(f).slides[1]
        assert len(slide.bullets) == 2

    def test_source_from_blockquote(self, tmp_path):
        f = _write_slide(tmp_path, "### Slide\n- bullet\n> Source: IDC 2025\n")
        slide = parse_md(f).slides[1]
        assert slide.source == "IDC 2025"

    def test_source_without_prefix(self, tmp_path):
        f = _write_slide(tmp_path, "### Slide\n- bullet\n> Company filings\n")
        slide = parse_md(f).slides[1]
        assert slide.source == "Company filings"

    def test_notes_from_comment(self, tmp_path):
        f = _write_slide(tmp_path, "### Slide\n- bullet\n<!-- notes: speaker note here -->\n")
        slide = parse_md(f).slides[1]
        assert slide.notes == "speaker note here"


# ---------------------------------------------------------------------------
# SCRNarrativeSlide
# ---------------------------------------------------------------------------

class TestSCRNarrativeSlide:
    def _scr_file(self, tmp_path):
        return _write_slide(tmp_path, """\
            ### Narrative slide title
            **Situation:** Market growing 35% YoY
            **Complication:** No viable solution exists
            **Resolution:** Our platform addresses the gap
        """)

    def test_all_three_labels_produce_scr(self, tmp_path):
        slide = parse_md(self._scr_file(tmp_path)).slides[1]
        assert isinstance(slide, SCRNarrativeSlide)

    def test_scr_fields_populated(self, tmp_path):
        slide = parse_md(self._scr_file(tmp_path)).slides[1]
        assert slide.situation == "Market growing 35% YoY"
        assert slide.complication == "No viable solution exists"
        assert slide.resolution == "Our platform addresses the gap"

    def test_missing_one_label_falls_back_to_content(self, tmp_path):
        f = _write_slide(tmp_path, "### Slide\n**Situation:** x\n**Complication:** y\n")
        slide = parse_md(f).slides[1]
        assert isinstance(slide, ContentSlide)

    def test_scr_case_insensitive(self, tmp_path):
        f = _write_slide(tmp_path, """\
            ### Slide
            **situation:** x
            **COMPLICATION:** y
            **Resolution:** z
        """)
        slide = parse_md(f).slides[1]
        assert isinstance(slide, SCRNarrativeSlide)


# ---------------------------------------------------------------------------
# ChartPlaceholderSlide
# ---------------------------------------------------------------------------

class TestChartPlaceholderSlide:
    def test_image_syntax_produces_chart(self, tmp_path):
        f = _write_slide(tmp_path, "### Chart slide\n![Exhibit 1](Revenue YoY growth)\n")
        slide = parse_md(f).slides[1]
        assert isinstance(slide, ChartPlaceholderSlide)

    def test_chart_label_and_description(self, tmp_path):
        f = _write_slide(tmp_path, "### Chart slide\n![My Label](My Description)\n")
        slide = parse_md(f).slides[1]
        assert slide.chart_label == "My Label"
        assert slide.chart_description == "My Description"

    def test_empty_image_alt_text(self, tmp_path):
        f = _write_slide(tmp_path, "### Chart slide\n![](some description)\n")
        slide = parse_md(f).slides[1]
        assert isinstance(slide, ChartPlaceholderSlide)
        assert slide.chart_label == ""
        assert slide.chart_description == "some description"


# ---------------------------------------------------------------------------
# TwoColumnSlide
# ---------------------------------------------------------------------------

class TestTwoColumnSlide:
    def _two_col_file(self, tmp_path):
        return _write_slide(tmp_path, """\
            ### Comparison slide
            #### Left Header
            - left one
            - left two
            #### Right Header
            - right one
        """)

    def test_two_h4_produces_two_column(self, tmp_path):
        slide = parse_md(self._two_col_file(tmp_path)).slides[1]
        assert isinstance(slide, TwoColumnSlide)

    def test_column_headers(self, tmp_path):
        slide = parse_md(self._two_col_file(tmp_path)).slides[1]
        assert slide.left_header == "Left Header"
        assert slide.right_header == "Right Header"

    def test_column_bullets(self, tmp_path):
        slide = parse_md(self._two_col_file(tmp_path)).slides[1]
        assert [b.text for b in slide.left_bullets] == ["left one", "left two"]
        assert [b.text for b in slide.right_bullets] == ["right one"]

    def test_single_h4_does_not_produce_two_column(self, tmp_path):
        f = _write_slide(tmp_path, "### Slide\n#### Only One Header\n- bullet\n")
        slide = parse_md(f).slides[1]
        assert not isinstance(slide, TwoColumnSlide)

    def test_three_h4_does_not_produce_two_column(self, tmp_path):
        f = _write_slide(tmp_path, """\
            ### Slide
            #### A
            - a
            #### B
            - b
            #### C
            - c
        """)
        slide = parse_md(f).slides[1]
        assert not isinstance(slide, TwoColumnSlide)


# ---------------------------------------------------------------------------
# Full deck integration
# ---------------------------------------------------------------------------

class TestFullDeckParse:
    def test_example_deck_parses(self):
        path = Path(__file__).parent.parent / "examples" / "ml_monitoring.md"
        deck = parse_md(path)
        assert deck.title == "ML Monitoring Platform: Series B Pitch"
        assert deck.author == "Team"
        assert deck.theme == "consulting"
        assert len(deck.slides) == 10

    def test_example_deck_slide_types(self):
        path = Path(__file__).parent.parent / "examples" / "ml_monitoring.md"
        types = [type(s).__name__ for s in parse_md(path).slides]
        assert types[0] == "TitleSlide"
        assert "SectionSlide" in types
        assert "SCRNarrativeSlide" in types
        assert "TwoColumnSlide" in types
        assert "ChartPlaceholderSlide" in types
        assert "ContentSlide" in types

    def test_slide_count_matches_headings(self, tmp_path):
        f = _write(tmp_path, """\
            # Title
            ## Section A
            ### Slide 1
            - bullet
            ### Slide 2
            - bullet
            ## Section B
            ### Slide 3
            - bullet
        """)
        deck = parse_md(f)
        assert len(deck.slides) == 6  # title + 2 sections + 3 content
