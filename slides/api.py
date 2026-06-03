"""
Public API — three composable functions for PydanticAI tools or direct import.

    from slides.api import parse, validate, build

PydanticAI usage:
    @agent.tool
    def parse_markdown(ctx, md_path: str) -> ParsedDeck:
        return parse(md_path)

    @agent.tool
    def validate_deck(ctx, deck: ParsedDeck) -> list[str]:
        return validate(deck)

    @agent.tool
    def build_deck(ctx, deck: ParsedDeck, theme: str = "consulting") -> str:
        return build(deck, theme=theme)
"""

from __future__ import annotations

from pathlib import Path

from slides.compiler import Compiler
from slides.model import ParsedDeck, validate_parsed
from slides.parser import parse_md
from slides.renderer import Renderer
from slides.theme import get_theme


def parse(path: str | Path) -> ParsedDeck:
    """Parse a Markdown file into a fully-typed ParsedDeck."""
    return parse_md(path)


def validate(deck: ParsedDeck) -> list[str]:
    """Run ghost-deck linter. Returns warnings; never raises."""
    return validate_parsed(deck)


def build(
    deck: ParsedDeck,
    output_dir: str | Path = "output",
    engine: str = "pdflatex",
    theme: str | None = None,
) -> str:
    """Render ParsedDeck → LaTeX → compile → return PDF path string."""
    resolved_theme = get_theme(theme or deck.theme)
    tex = Renderer().render(deck.slides, resolved_theme, deck.title, deck.author)
    safe_name = deck.title.lower().replace(" ", "_")[:40]
    result = Compiler(Path(output_dir), engine).compile(tex, safe_name)
    if not result.success:
        raise RuntimeError(f"LaTeX compilation failed: {result.errors}\nSee: {result.tex_path}")
    return str(result.pdf_path)


def build_from_md(path: str | Path, output_dir: str | Path = "output", engine: str = "pdflatex") -> str:
    """One-shot convenience: parse .md file → PDF. Returns PDF path."""
    deck = parse(path)
    warnings = validate(deck)
    for w in warnings:
        print(f"⚠  {w}")
    return build(deck, output_dir, engine)
