"""Tests for slides/api.py — parse, validate, build, build_from_md."""

import textwrap
from pathlib import Path

import pytest

from slides.api import build, build_from_md, parse, validate
from slides.model import (
    BulletPoint,
    ContentSlide,
    ParsedDeck,
    SectionSlide,
    TitleSlide,
)


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "deck.md"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def _simple_deck(theme: str = "consulting") -> ParsedDeck:
    return ParsedDeck(
        title="Test Deck",
        author="Tester",
        theme=theme,
        slides=[
            TitleSlide(action_title="Test Deck"),
            SectionSlide(action_title="1. Section"),
            ContentSlide(
                action_title="Three points support our recommendation",
                bullets=[BulletPoint(text="Point one"), BulletPoint(text="Point two")],
                source="Test source",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# parse()
# ---------------------------------------------------------------------------

class TestParse:
    def test_returns_parsed_deck(self, tmp_path):
        f = _write(tmp_path, "# My Deck\n### Slide\n- bullet\n")
        deck = parse(f)
        assert isinstance(deck, ParsedDeck)

    def test_title_extracted(self, tmp_path):
        f = _write(tmp_path, "# Great Title\n")
        assert parse(f).title == "Great Title"

    def test_accepts_string_path(self, tmp_path):
        f = _write(tmp_path, "# Deck\n")
        deck = parse(str(f))
        assert isinstance(deck, ParsedDeck)

    def test_accepts_path_object(self, tmp_path):
        f = _write(tmp_path, "# Deck\n")
        deck = parse(Path(f))
        assert isinstance(deck, ParsedDeck)

    def test_nonexistent_file_raises(self, tmp_path):
        with pytest.raises(Exception):
            parse(tmp_path / "missing.md")


# ---------------------------------------------------------------------------
# validate()
# ---------------------------------------------------------------------------

class TestValidate:
    def test_clean_deck_returns_no_warnings(self):
        assert validate(_simple_deck()) == []

    def test_missing_title_slide_warns(self):
        deck = ParsedDeck(
            title="X",
            slides=[ContentSlide(action_title="Only slide", bullets=[BulletPoint(text="x")])],
        )
        warnings = validate(deck)
        assert any("title slide" in w.lower() for w in warnings)

    def test_missing_section_slide_warns(self):
        deck = ParsedDeck(
            title="X",
            slides=[
                TitleSlide(action_title="Title"),
                ContentSlide(action_title="Slide", bullets=[BulletPoint(text="x")]),
            ],
        )
        warnings = validate(deck)
        assert any("section" in w.lower() for w in warnings)

    def test_title_too_long_warns(self):
        deck = ParsedDeck(
            title="X",
            slides=[
                TitleSlide(action_title="One two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen")
            ],
        )
        warnings = validate(deck)
        assert any("words" in w for w in warnings)

    def test_title_with_and_warns(self):
        deck = ParsedDeck(
            title="X",
            slides=[TitleSlide(action_title="Revenue grew and costs fell")],
        )
        warnings = validate(deck)
        assert any("and" in w for w in warnings)

    def test_too_many_bullets_warns(self):
        deck = ParsedDeck(
            title="X",
            slides=[
                ContentSlide(
                    action_title="Dense slide",
                    bullets=[BulletPoint(text=f"Point {i}") for i in range(6)],
                )
            ],
        )
        warnings = validate(deck)
        assert any("dense" in w.lower() or "bullet" in w.lower() for w in warnings)

    def test_returns_list_never_raises(self):
        result = validate(ParsedDeck(title="X", slides=[]))
        assert isinstance(result, list)


# ---------------------------------------------------------------------------
# build()
# ---------------------------------------------------------------------------

class TestBuild:
    def test_produces_pdf(self, tmp_path):
        path = build(_simple_deck(), output_dir=tmp_path)
        assert Path(path).exists()
        assert path.endswith(".pdf")

    def test_pdf_nonempty(self, tmp_path):
        path = build(_simple_deck(), output_dir=tmp_path)
        assert Path(path).stat().st_size > 1024

    def test_theme_override(self, tmp_path):
        path = build(_simple_deck(), output_dir=tmp_path, theme="startup")
        assert Path(path).exists()

    def test_lualatex_engine(self, tmp_path):
        path = build(_simple_deck(), output_dir=tmp_path, engine="lualatex")
        assert Path(path).exists()

    def test_cache_skips_recompile(self, tmp_path):
        deck = _simple_deck()
        path1 = build(deck, output_dir=tmp_path)
        mtime1 = Path(path1).stat().st_mtime
        path2 = build(deck, output_dir=tmp_path)
        assert Path(path2).stat().st_mtime == mtime1  # file unchanged = cached

    def test_content_change_recompiles(self, tmp_path):
        path1 = build(_simple_deck("consulting"), output_dir=tmp_path)
        mtime1 = Path(path1).stat().st_mtime
        deck2 = _simple_deck("consulting")
        deck2.slides[2].action_title = "Modified title forces recompile"
        path2 = build(deck2, output_dir=tmp_path)
        assert Path(path2).stat().st_mtime >= mtime1

    def test_output_dir_created_if_missing(self, tmp_path):
        out = tmp_path / "nested" / "output"
        build(_simple_deck(), output_dir=out)
        assert out.exists()


# ---------------------------------------------------------------------------
# build_from_md()
# ---------------------------------------------------------------------------

class TestBuildFromMd:
    def test_end_to_end_md_to_pdf(self, tmp_path):
        f = _write(tmp_path, """\
            # E2E Test Deck
            ## Section
            ### Key finding supports our core recommendation
            - Finding one with specific data
            - Finding two with specific data
            > Source: Test 2025
        """)
        out = tmp_path / "out"
        pdf = build_from_md(f, output_dir=out)
        assert Path(pdf).exists()

    def test_example_deck_builds(self, tmp_path):
        example = Path(__file__).parent.parent / "examples" / "ml_monitoring.md"
        pdf = build_from_md(example, output_dir=tmp_path)
        assert Path(pdf).exists()
