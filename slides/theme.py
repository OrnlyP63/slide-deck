from pydantic import BaseModel


class Theme(BaseModel):
    name: str
    preamble: str


def get_theme(name: str) -> Theme:
    if name not in THEMES:
        raise ValueError(f"Unknown theme '{name}'. Available: {list(THEMES)}")
    return THEMES[name]


def register_theme(theme: Theme) -> None:
    THEMES[theme.name] = theme


# ---------------------------------------------------------------------------
# Theme registry — 10 audience-based themes using community Beamer .sty files
# ---------------------------------------------------------------------------

THEMES: dict[str, Theme] = {

    # 1. CONSULTING — Metropolis + Fira Sans, navy/gold (MBB / strategy)
    "consulting": Theme(name="consulting", preamble=r"""
\usepackage{FiraSans}
\usetheme[progressbar=frametitle, block=fill, titleformat=regular]{metropolis}
\definecolor{mcPrimary}{HTML}{003366}
\definecolor{mcAccent}{HTML}{C9A84C}
\setbeamercolor{palette primary}{fg=white, bg=mcPrimary}
\setbeamercolor{frametitle}{fg=white, bg=mcPrimary}
\setbeamercolor{progress bar}{fg=mcAccent, bg=mcPrimary!50}
\setbeamercolor{alerted text}{fg=mcAccent}
\setbeamercolor{title separator}{fg=mcAccent}
"""),

    # 2. STARTUP — Trigon, orange/teal (VC / Series A-B pitch)
    "startup": Theme(name="startup", preamble=r"""
\definecolor{tPrim}{HTML}{FF6B35}
\definecolor{tSec}{HTML}{E8501A}
\definecolor{tAccent}{HTML}{00D4AA}
\usetheme{trigon}
\setbeamertemplate{navigation symbols}{}
"""),

    # 3. ACADEMIC — Metropolis + Palatino serif, burgundy/gold (research / university)
    "academic": Theme(name="academic", preamble=r"""
\usepackage{palatino}
\usefonttheme{serif}
\usetheme[progressbar=none, block=fill, titleformat=regular]{metropolis}
\definecolor{acadPrimary}{HTML}{5C1A1A}
\definecolor{acadAccent}{HTML}{8B6914}
\setbeamercolor{palette primary}{fg=white, bg=acadPrimary}
\setbeamercolor{frametitle}{fg=white, bg=acadPrimary}
\setbeamercolor{progress bar}{fg=acadAccent}
\setbeamercolor{alerted text}{fg=acadPrimary}
\setbeamercolor{title separator}{fg=acadAccent}
"""),

    # 4. FINANCE — Focus, dark forest green (banking / PE / hedge fund)
    "finance": Theme(name="finance", preamble=r"""
\definecolor{main}{HTML}{1B4332}
\definecolor{background}{HTML}{FFFFFF}
\usetheme[nofirafonts, numbering=fraction]{focus}
"""),

    # 5. TECH — Metropolis + Fira, deep blue/cyan, foot progressbar (SaaS / engineering)
    "tech": Theme(name="tech", preamble=r"""
\usepackage{FiraSans}
\usetheme[progressbar=foot, block=fill, titleformat=regular]{metropolis}
\definecolor{techPrimary}{HTML}{0F4C81}
\definecolor{techAccent}{HTML}{00B4D8}
\setbeamercolor{palette primary}{fg=white, bg=techPrimary}
\setbeamercolor{frametitle}{fg=white, bg=techPrimary}
\setbeamercolor{progress bar}{fg=techAccent, bg=techPrimary!50}
\setbeamercolor{alerted text}{fg=techAccent}
\setbeamercolor{title separator}{fg=techAccent}
"""),

    # 6. GOVERNMENT — SimpleDarkBlue base + formal navy/red override (public sector)
    "government": Theme(name="government", preamble=r"""
\usetheme{SimpleDarkBlue}
\definecolor{GovNavy}{HTML}{1C2B4A}
\definecolor{GovRed}{HTML}{C0392B}
\setbeamercolor{structure}{fg=GovNavy}
\setbeamercolor{title}{bg=GovNavy, fg=white}
\setbeamercolor{frametitle}{bg=GovNavy, fg=white}
\setbeamercolor{block title}{fg=white, bg=GovNavy}
\setbeamercolor{block body}{fg=black, bg=GovNavy!8}
\setbeamercolor{alerted text}{fg=GovRed}
\setbeamertemplate{navigation symbols}{}
"""),

    # 7. HEALTHCARE — Pure-Minimalistic, medical blue accent (medical / pharma)
    "healthcare": Theme(name="healthcare", preamble=r"""
\usetheme[nofooterlogo]{pureminimalistic}
\renewcommand{\logoheader}{}
\renewcommand{\logotitle}{}
\renewcommand{\logofooter}{}
\definecolor{pureminimalistic@text@red}{HTML}{005B96}
\setbeamercolor{normal text}{fg=black}
\setbeamertemplate{navigation symbols}{}
"""),

    # 8. CREATIVE — Trigon dark mode, purple/gold (agency / design / media)
    "creative": Theme(name="creative", preamble=r"""
\definecolor{tPrim}{HTML}{6A0572}
\definecolor{tSec}{HTML}{4A0550}
\definecolor{tAccent}{HTML}{FFB703}
\usetheme[background=dark]{trigon}
\setbeamertemplate{navigation symbols}{}
"""),

    # 9. MINIMAL — Pure-Minimalistic, clean white (any audience, zero distraction)
    "minimal": Theme(name="minimal", preamble=r"""
\usetheme[nofooterlogo]{pureminimalistic}
\renewcommand{\logoheader}{}
\renewcommand{\logotitle}{}
\renewcommand{\logofooter}{}
\setbeamertemplate{navigation symbols}{}
"""),

    # 10. DARK — Metropolis dark canvas, dark navy/red (tech demo / product)
    "dark": Theme(name="dark", preamble=r"""
\usepackage{FiraSans}
\usetheme[progressbar=frametitle, block=fill, titleformat=regular]{metropolis}
\definecolor{darkBg}{HTML}{1A1A2E}
\definecolor{darkAccent}{HTML}{E94560}
\setbeamercolor{background canvas}{bg=darkBg}
\setbeamercolor{normal text}{fg=white, bg=darkBg}
\setbeamercolor{palette primary}{fg=white, bg=darkBg}
\setbeamercolor{frametitle}{fg=white, bg=darkBg}
\setbeamercolor{progress bar}{fg=darkAccent, bg=darkBg!80}
\setbeamercolor{alerted text}{fg=darkAccent}
\setbeamercolor{title separator}{fg=darkAccent}
\setbeamercolor{structure}{fg=white}
"""),
}
