# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

LLM-powered pipeline that generates LaTeX (Beamer) slide decks from a natural language goal. Three-stage pipeline: FFT classifies content → Pydantic model structures it → Jinja2 renders to LaTeX → pdflatex compiles to PDF.

## Commands

```bash
uv add jinja2 click rich pydantic anthropic          # install runtime deps
uv add --dev pytest ruff                             # install dev deps
uv run main.py generate "your deck goal here"        # full LLM pipeline → PDF
uv run main.py outline "your deck goal here"         # Ghost Deck only, print outline
uv run main.py build examples/demo_deck.py           # manual Python deck, no LLM
uv run main.py build examples/demo_deck.py --engine lualatex
uv run pytest                                        # run tests
uv run ruff check slides/                            # lint
```

## Module Map

```
slides/model.py      — Pydantic BaseModel: all slide types, SlideDescriptor, GhostDeckOutput, validate_deck
slides/selector.py   — FFTNode, FFTSelector, ContentSignals, DEFAULT_FFT, extract_signals
slides/llm.py        — Anthropic client + tool wrappers: call_ghost_deck / call_signals / call_fill
slides/pipeline.py   — orchestration: run_pipeline(goal) → Path, run_outline(goal) → list[SlideDescriptor]
slides/renderer.py   — Jinja2: type(slide).__name__ → snake_case → .tex.j2 convention
slides/compiler.py   — subprocess pdflatex ×2, sha256 content-hash cache
slides/theme.py      — Theme Pydantic model + built-in themes (consulting, minimal)
slides/templates/    — per-type .tex.j2 partials + .sty Beamer theme files
main.py              — click CLI: generate / outline / build commands
```

## LLM Pipeline (generate command)

```
Call 0  goal → GhostDeck tool → list[SlideDescriptor]   (flat outline, SCR-structured)
         ↓ validate_deck warnings printed
per slide:
  code    derives is_opener / is_section from SlideDescriptor.type + index
  Call 1  ContentSignals tool → {has_scr, has_chart, has_comparison}
          merge with structural signals → DEFAULT_FFT → template class name
  Call 2  TemplateModel.model_json_schema() as tool → model_validate → Pydantic instance
  render  type(slide).__name__ → snake_case → templates/slides/<name>.tex.j2
compile   pdflatex ×2 → output/<name>.pdf
```

## Key Design Decisions

- **Pydantic replaces dataclasses** in `model.py` — models serve as both data objects and JSON schema source for LLM tool definitions (`Model.model_json_schema()`)
- **Tool use (not prompt + parsing)** for all LLM calls — guarantees structured output, no retry logic for malformed JSON
- **FFT runs between Call 1 and Call 2** — structural signals (`is_opener`, `is_section`) derived from outline in code; content signals (`has_scr`, `has_chart`, `has_comparison`) from Call 1
- **Template dispatch by convention** — `type(slide).__name__` → `snake_case` → `.tex.j2` filename; no registry to maintain
- **`llm.py` / `pipeline.py` split** — `llm.py` owns Anthropic API calls, `pipeline.py` owns sequencing; swap providers by touching only `llm.py`
- **Two pdflatex passes** always run (cross-reference requirement)
- **Cache**: `output/.cache/{name}.hash` stores sha256 of .tex; skip recompile if unchanged

## Slide Types (model.py)

`TitleSlide`, `SectionSlide`, `ContentSlide`, `TwoColumnSlide`, `ChartPlaceholderSlide`, `SCRNarrativeSlide`

All inherit `SlideBase(action_title, notes, source)`. FFT cue order (most distinctive first): `is_opener → is_section → has_scr → has_chart → has_columns → ContentSlide` (fallback).

## Ghost Deck Linter (validate_deck)

`validate_deck(deck) -> list[str]` — warnings only, never blocks compile or generation:
- Action title >15 words
- Title contains "and" (split signal)
- >5 bullets on one slide
- No source on data slides
- No `TitleSlide` or `SectionSlide` separators
