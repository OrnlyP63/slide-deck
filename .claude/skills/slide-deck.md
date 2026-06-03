# slide-deck skill

Build a PDF slide deck from a Markdown file.

## How to invoke

```bash
uv run main.py build <file.md>            # parse + compile → PDF
uv run main.py validate <file.md>         # lint only, no compile
uv run main.py build <file.md> --theme minimal
uv run main.py build <file.md> --engine lualatex
```

## Markdown conventions

```markdown
# Deck Title                        ← TitleSlide (first slide)
<!-- author: Your Name -->          ← deck metadata
<!-- theme: consulting -->          ← consulting | minimal | dark

## Section Name                     ← SectionSlide (chapter divider)

### Slide Action Title              ← content slide; body determines type

- bullet point                      ← ContentSlide (default)
- another bullet
> Source: IDC 2025                  ← source attribution

### SCR Narrative Slide Title
**Situation:** Current state...     ← SCRNarrativeSlide (all 3 required)
**Complication:** The problem...
**Resolution:** Our recommendation...

### Chart Slide Title
![Exhibit 1: Revenue by Region](YoY growth showing 35% CAGR)
> Source: Company filings

### Two-Column Slide Title          ← TwoColumnSlide (exactly 2 H4s)
#### Left Header
- left bullet
#### Right Header
- right bullet

<!-- notes: presenter note here --> ← notes on any slide
```

## Template selection (FFT rules)

FFT checks cues in order — first match wins:
1. Index 0 or H1 → TitleSlide
2. H2 → SectionSlide
3. All three **Situation/Complication/Resolution:** → SCRNarrativeSlide
4. `![...]()` image → ChartPlaceholderSlide
5. Exactly two `####` H4 blocks → TwoColumnSlide
6. Everything else → ContentSlide

## Workflow when asked to build a deck

1. Understand the topic and goal
2. Plan SCR narrative (Situation 10-15%, Complication 15-25%, Resolution 60-70%)
3. Write action titles first (complete sentences, ≤15 words, quantitative when possible)
4. Write the `.md` file following the conventions above
5. Run `uv run main.py validate <file.md>` — fix any warnings
6. Run `uv run main.py build <file.md>` — deliver the PDF path
