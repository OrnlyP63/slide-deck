from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BulletPoint(BaseModel):
    text: str
    sub_bullets: list[str] = []
    emphasis: bool = False


class SlideBase(BaseModel):
    action_title: str = Field(..., description="Complete sentence ≤15 words stating the slide's key takeaway")
    notes: str = ""
    source: str = ""


class TitleSlide(SlideBase):
    subtitle: str = ""
    author: str = ""
    date: str = ""


class SectionSlide(SlideBase):
    pass


class ContentSlide(SlideBase):
    bullets: list[BulletPoint] = []
    body_text: str = ""


class TwoColumnSlide(SlideBase):
    left_header: str = ""
    left_bullets: list[BulletPoint] = []
    right_header: str = ""
    right_bullets: list[BulletPoint] = []


class ChartPlaceholderSlide(SlideBase):
    chart_label: str = Field("", description="Exhibit label, e.g. 'Exhibit 1: Revenue by Region'")
    chart_description: str = Field("", description="What the chart shows and its key insight")


class SCRNarrativeSlide(SlideBase):
    situation: str = Field("", description="Current state — shared context establishing why action is needed")
    complication: str = Field("", description="Problem or tension disrupting the situation")
    resolution: str = Field("", description="Recommended solution and next steps")


Slide = TitleSlide | SectionSlide | ContentSlide | TwoColumnSlide | ChartPlaceholderSlide | SCRNarrativeSlide


class ParsedDeck(BaseModel):
    """Fully-typed deck produced by the Markdown parser. Primary data contract between tools."""
    title: str
    author: str = ""
    theme: str = "consulting"
    slides: list[TitleSlide | SectionSlide | ContentSlide | TwoColumnSlide | ChartPlaceholderSlide | SCRNarrativeSlide] = []


def validate_parsed(deck: ParsedDeck) -> list[str]:
    warnings = []
    slides = deck.slides
    types = [type(s).__name__ for s in slides]

    if not slides or not isinstance(slides[0], TitleSlide):
        warnings.append("Deck should start with a title slide")
    if "SectionSlide" not in types:
        warnings.append("No section dividers — consider adding ## sections for narrative structure")

    for i, s in enumerate(slides):
        words = len(s.action_title.split())
        if words > 15:
            warnings.append(f"Slide {i}: action title is {words} words (>15): '{s.action_title}'")
        if " and " in s.action_title.lower():
            warnings.append(f"Slide {i}: title contains 'and' — consider splitting")
        if isinstance(s, ContentSlide) and len(s.bullets) > 5:
            warnings.append(f"Slide {i}: {len(s.bullets)} bullets (>5) — too dense")

    return warnings


class SlideSignals(BaseModel):
    """LLM-extracted content signals for FFT template classification (Call 1 output)."""
    has_scr: bool = Field(False, description="True if topic warrants situation/complication/resolution narrative structure")
    has_chart: bool = Field(False, description="True if topic calls for a chart, graph, or data visualization")
    has_columns: bool = Field(False, description="True if topic compares two parallel items side-by-side")


class SlideDescriptor(BaseModel):
    index: int
    type: Literal["title", "section", "content", "two_column", "chart", "scr"]
    action_title: str = Field(..., description="Complete sentence ≤15 words")
    brief: str = Field("", description="One sentence describing what this slide should cover")


class GhostDeckOutput(BaseModel):
    deck_title: str
    author: str = ""
    theme: str = "consulting"
    slides: list[SlideDescriptor]


def validate_deck(ghost: GhostDeckOutput) -> list[str]:
    warnings = []
    slides = ghost.slides
    types = [s.type for s in slides]

    if not slides or slides[0].type != "title":
        warnings.append("Deck should start with a title slide")
    if "section" not in types:
        warnings.append("No section dividers — consider adding section slides for narrative structure")

    for s in slides:
        words = len(s.action_title.split())
        if words > 15:
            warnings.append(f"Slide {s.index}: action title is {words} words (>15): '{s.action_title}'")
        if " and " in s.action_title.lower():
            warnings.append(f"Slide {s.index}: title contains 'and' — consider splitting into two slides")

    return warnings
