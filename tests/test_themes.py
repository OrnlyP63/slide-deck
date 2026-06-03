"""Compile a minimal deck with every theme — verifies LaTeX renders without error."""

import pytest
from pathlib import Path

from slides.api import build
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
    Stat,
    StatsSlide,
    TableSlide,
    TimelineSlide,
    TitleSlide,
    TwoColumnSlide,
)
from slides.theme import THEMES


def _minimal_deck(theme_name: str) -> ParsedDeck:
    """Deck exercising all 12 slide types."""
    return ParsedDeck(
        title="Theme Test Deck",
        author="Test",
        theme=theme_name,
        slides=[
            TitleSlide(action_title="Theme Test Deck", subtitle="Automated test"),
            SectionSlide(action_title="1. Test Section"),
            AgendaSlide(action_title="Four topics today", items=["Market", "Solution", "Traction", "Ask"]),
            SCRNarrativeSlide(
                action_title="Market gap creates opportunity worth capturing now",
                situation="Market growing 35% YoY",
                complication="No viable solution exists today",
                resolution="Our platform addresses the gap directly",
            ),
            ContentSlide(
                action_title="Three trends accelerate our entry window",
                bullets=[
                    BulletPoint(text="Regulatory tailwind since 2024 directive"),
                    BulletPoint(text="Competitor funding dried up Q1 2025"),
                    BulletPoint(text="Customer demand doubled year-on-year"),
                ],
                source="IDC 2025",
            ),
            TwoColumnSlide(
                action_title="We outperform alternatives on cost and coverage",
                left_header="Competitors",
                left_bullets=[BulletPoint(text="Reactive alerts only")],
                right_header="Our Platform",
                right_bullets=[BulletPoint(text="Predictive drift detection")],
            ),
            ChartPlaceholderSlide(
                action_title="Revenue grew 3x in twelve months driven by enterprise",
                chart_label="Exhibit 1: ARR Growth",
                chart_description="Monthly ARR from $700K to $2.1M over 12 months",
                source="Company financials Q1 2026",
            ),
            StatsSlide(
                action_title="Three metrics prove product-market fit",
                stats=[
                    Stat(label="ARR", value="$2.1M"),
                    Stat(label="NRR", value="94%"),
                    Stat(label="CAC", value="$38"),
                ],
                source="Internal Q1 2026",
            ),
            QuoteSlide(
                action_title="Expert validation supports our thesis",
                quote="The best way to predict the future is to create it.",
                attribution="Peter Drucker",
            ),
            TimelineSlide(
                action_title="Three-phase rollout delivers full coverage in 18 months",
                steps=["Q1 2026: Foundation", "Q2-Q3 2026: Buildout", "Q4 2026: Scale"],
            ),
            TableSlide(
                action_title="Revenue breakdown by segment shows enterprise dominance",
                headers=["Segment", "ARR", "Growth"],
                rows=[["Enterprise", "$1.4M", "+67%"], ["SMB", "$0.5M", "+23%"]],
                source="Internal Q1 2026",
            ),
            ClosingSlide(
                action_title="Thank You",
                contact="hello@example.com",
                website="https://github.com/OrnlyP63/slide-deck",
            ),
        ],
    )


@pytest.mark.parametrize("theme_name", list(THEMES.keys()))
def test_theme_compiles(theme_name: str, tmp_path: Path) -> None:
    deck = _minimal_deck(theme_name)
    pdf_path = build(deck, output_dir=tmp_path, theme=theme_name)
    assert Path(pdf_path).exists(), f"PDF not produced for theme '{theme_name}'"
    assert Path(pdf_path).stat().st_size > 1024, f"PDF suspiciously small for theme '{theme_name}'"


def test_all_themes_registered() -> None:
    expected = {
        "consulting", "minimal", "dark",
        "startup", "academic", "finance", "tech",
        "government", "healthcare", "creative",
    }
    assert set(THEMES.keys()) == expected
