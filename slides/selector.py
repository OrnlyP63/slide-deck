from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ContentSignals:
    """All signals needed for FFT traversal. Structural signals set by code; content signals from LLM Call 1."""
    is_opener: bool = False
    is_section: bool = False
    has_scr: bool = False
    has_chart: bool = False
    has_columns: bool = False
    has_bullets: bool = True


@dataclass
class FFTNode:
    """One cue in a Fast-and-Frugal Tree.

    At least one of true_exit / false_exit must be set.
    Last node in a tree must have both set (termination guarantee).
    """
    cue: str
    true_exit: str | None = None
    false_exit: str | None = None


class FFTSelector:
    """Walks FFT nodes and returns the first slide type name on exit.

    Cue order = distinctiveness order (most specific first).
    O(n) worst case; most real inputs exit in 1-2 nodes.
    """

    def __init__(self, nodes: list[FFTNode]) -> None:
        if not nodes:
            raise ValueError("FFTSelector requires at least one node")
        last = nodes[-1]
        if last.true_exit is None or last.false_exit is None:
            raise ValueError("Last FFTNode must have both true_exit and false_exit set")
        self._nodes = nodes

    def classify(self, signals: ContentSignals) -> str:
        for node in self._nodes:
            val: bool = getattr(signals, node.cue)
            exit_type = node.true_exit if val else node.false_exit
            if exit_type is not None:
                return exit_type
        raise RuntimeError("FFT traversal exhausted all nodes without exit")  # pragma: no cover


DEFAULT_FFT = FFTSelector([
    FFTNode("is_opener",   true_exit="TitleSlide"),
    FFTNode("is_section",  true_exit="SectionSlide"),
    FFTNode("has_scr",     true_exit="SCRNarrativeSlide"),
    FFTNode("has_chart",   true_exit="ChartPlaceholderSlide"),
    FFTNode("has_columns", true_exit="TwoColumnSlide"),
    FFTNode("has_bullets", true_exit="ContentSlide", false_exit="ContentSlide"),
])
