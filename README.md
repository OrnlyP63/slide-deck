# slide-deck

Python library that converts Markdown files into LaTeX (Beamer) PDF slide decks.  
Write `.md` → get a consulting-quality PDF. No API key required.

---

## Quick start

```bash
uv add jinja2 click rich pydantic          # runtime deps
uv add --dev pytest ruff                   # dev deps
uv run main.py build examples/ml_monitoring.md
uv run main.py validate examples/ml_monitoring.md   # lint only
```

---

## How it works

### Pipeline overview

```mermaid
flowchart TD
    A(["deck.md file"]) --> B["parse(path)"]
    B -->|ParsedDeck| C["validate(deck)"]
    C -->|"list[str] warnings"| D["build(deck)"]
    D --> E(["output/deck.pdf"])

    subgraph inside parse
        P1["read lines"] --> P2["scan headings"]
        P2 --> P3["collect slide body"]
        P3 --> P4["FFT classify → typed slide"]
    end

    B -.-> inside parse

    subgraph inside build
        B1["get_theme"] --> B2["Renderer.render → .tex"]
        B2 --> B3["sha256 cache check"]
        B3 -->|"miss"| B4["pdflatex ×2"]
        B3 -->|"hit"| B5(["return cached PDF"])
        B4 --> B6(["return PDF path"])
    end

    D -.-> inside build
```

---

### 1. `parse(path)` — `slides/parser.py`

Reads a `.md` file line-by-line, maps headings to slide roles, and runs the FFT classifier on each slide body to produce fully-typed Pydantic slide objects.

```mermaid
flowchart TD
    A(["path to .md file"]) --> B["read lines"]
    B --> C{"heading level?"}
    C -->|"# H1"| D["TitleSlide\n(index 0)"]
    C -->|"## H2"| E["SectionSlide"]
    C -->|"### H3"| F["collect body lines"]
    C -->|"other line"| G["append to body"]
    F --> H["flush previous slide"]
    G --> I{{"body: bullets / SCR labels\n/ image / H4 columns"}}
    I --> J["build ContentSignals"]
    J --> K["DEFAULT_FFT.classify"]
    K --> L{"template?"}
    L -->|"is_opener"| M["TitleSlide"]
    L -->|"has_scr"| N["SCRNarrativeSlide"]
    L -->|"has_chart"| O["ChartPlaceholderSlide"]
    L -->|"has_columns"| P["TwoColumnSlide"]
    L -->|"default"| Q["ContentSlide"]
    M & N & O & P & Q --> R["append to slides list"]
    R --> S(["ParsedDeck"])
```

**Output:** `ParsedDeck` — `title`, `author`, `theme`, `slides: list[Slide]` fully typed.

---

### 2. `validate(deck)` — `slides/api.py`

Runs the ghost-deck linter against MBB consulting standards. Never raises — always returns warnings as strings.

```mermaid
flowchart TD
    A(["ParsedDeck"]) --> B["check slides[0] is TitleSlide"]
    B -->|"missing"| C["⚠ warn: no title slide"]
    B -->|"ok"| D["check SectionSlide present"]
    D -->|"missing"| E["⚠ warn: no section dividers"]
    D -->|"ok"| F["for each slide"]
    C & E --> F
    F --> G{"action_title\nword count > 15?"}
    G -->|"yes"| H["⚠ warn: title too long"]
    G -->|"no"| I{"contains 'and'?"}
    I -->|"yes"| J["⚠ warn: consider splitting"]
    I -->|"no"| K{"ContentSlide\nbullets > 5?"}
    K -->|"yes"| L["⚠ warn: too dense"]
    K -->|"no"| M["next slide"]
    H & J & L --> M
    M --> N(["list[str] warnings"])
```

**Output:** `list[str]` — zero or more warning messages; empty list means deck passes.

---

### 3. `build(deck)` — `slides/api.py` + `slides/renderer.py` + `slides/compiler.py`

Renders typed slide objects to a LaTeX Beamer document, then compiles to PDF with a content-hash cache.

```mermaid
flowchart TD
    A(["ParsedDeck"]) --> B["get_theme(deck.theme)"]
    B --> C["Renderer.render(slides, theme)"]
    C --> D["for each slide:\ntype.__name__ → snake_case → .tex.j2"]
    D --> E["Jinja2 render\n+ latex_escape filter"]
    E --> F[".tex string"]
    F --> G["sha256(tex_content)"]
    G --> H[("output/.cache/\nname.hash")]
    H -->|"hash match + PDF exists"| I(["return cached PDF path"])
    H -->|"miss"| J["write output/name.tex"]
    J --> K["pdflatex pass 1"]
    K --> L["pdflatex pass 2\n(cross-refs)"]
    L --> M{"returncode == 0?"}
    M -->|"error"| N(["raise RuntimeError\n+ error lines"])
    M -->|"ok"| O["write new hash"]
    O --> P(["return PDF path str"])
```

**Output:** `str` — absolute path to compiled PDF, e.g. `output/deck.pdf`.

---

### 4. FFT Template Classifier — `slides/selector.py`

Fast-and-Frugal Tree: checks one cue at a time, exits on first match. Most distinctive signals checked first.

```mermaid
flowchart TD
    A(["ContentSignals"]) --> B{"is_opener?"}
    B -->|"yes"| C(["TitleSlide"])
    B -->|"no"| D{"is_section?"}
    D -->|"yes"| E(["SectionSlide"])
    D -->|"no"| F{"has_scr?\nall 3 bold labels"}
    F -->|"yes"| G(["SCRNarrativeSlide"])
    F -->|"no"| H{"has_chart?\nimage syntax"}
    H -->|"yes"| I(["ChartPlaceholderSlide"])
    H -->|"no"| J{"has_columns?\nexactly 2× H4"}
    J -->|"yes"| K(["TwoColumnSlide"])
    J -->|"no"| L(["ContentSlide"])
```

**Output:** `str` — class name of the winning slide type.

---

## Markdown conventions

```markdown
# Deck Title                         ← TitleSlide
<!-- author: Name -->                ← metadata
<!-- theme: consulting -->           ← see Themes table for all 10 options

## Section Name                      ← SectionSlide

### Slide action title               ← ContentSlide (default)
- bullet one
> Source: IDC 2025

### SCR slide title
**Situation:** current state...      ← SCRNarrativeSlide (all 3 required)
**Complication:** the problem...
**Resolution:** recommendation...

### Chart slide title
![Exhibit 1: Label](description)    ← ChartPlaceholderSlide

### Two-column slide title           ← TwoColumnSlide (exactly 2 H4s)
#### Left Header
- left bullet
#### Right Header
- right bullet

<!-- notes: presenter note -->       ← notes on any slide
```

---

## Usage modes

### CLI

```bash
uv run main.py build deck.md
uv run main.py build deck.md --theme minimal --engine lualatex
uv run main.py validate deck.md
```

### Python / PydanticAI agent

```python
from slides.api import parse, validate, build

# Direct
deck = parse("deck.md")
warnings = validate(deck)
pdf_path = build(deck)

# One-shot
from slides.api import build_from_md
pdf_path = build_from_md("deck.md")

# PydanticAI tools
from pydantic_ai import Agent
from slides.api import parse, validate, build
from slides.model import ParsedDeck

agent = Agent("claude-sonnet-4-6", ...)

@agent.tool
def parse_markdown(ctx, md_path: str) -> ParsedDeck:
    return parse(md_path)

@agent.tool
def validate_deck(ctx, deck: ParsedDeck) -> list[str]:
    return validate(deck)

@agent.tool
def build_deck(ctx, deck: ParsedDeck) -> str:
    return build(deck)
```

---

## Testing

```bash
uv run pytest                          # all tests
uv run pytest tests/test_parser.py -v  # parser only
uv run pytest tests/test_selector.py   # FFT only
uv run pytest tests/test_api.py        # api only
uv run pytest tests/test_themes.py     # compile all 10 themes
```

83 tests total: selector (22), parser (28), api (22), themes (11).

---

## Themes

| Name | Audience | Primary | Accent |
|---|---|---|---|
| `consulting` | Strategy / MBB pitch | Navy `#003366` | Gold `#C9A84C` |
| `minimal` | Any — clean, no distraction | Black `#000000` | Gray `#555555` |
| `dark` | Tech / product demo | Dark navy `#1A1A2E` | Red `#E94560` |
| `startup` | VC / Series A–B pitch | Orange `#FF6B35` | Teal `#00D4AA` |
| `academic` | Research / university | Burgundy `#5C1A1A` | Warm gold `#8B6914` |
| `finance` | Banking / PE / hedge fund | Forest green `#1B4332` | Green `#52B788` |
| `tech` | Engineering / SaaS / cloud | Deep blue `#0F4C81` | Cyan `#00B4D8` |
| `government` | Public sector / policy | Dark navy `#1C2B4A` | Flag red `#C0392B` |
| `healthcare` | Medical / pharma / clinical | Medical blue `#005B96` | Light blue `#48CAE4` |
| `creative` | Agency / design / media | Purple `#6A0572` | Gold `#FFB703` |
