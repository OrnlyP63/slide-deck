"""Tests for FFTSelector, FFTNode, ContentSignals, and DEFAULT_FFT."""

import pytest
from slides.selector import ContentSignals, DEFAULT_FFT, FFTNode, FFTSelector


# ---------------------------------------------------------------------------
# FFTSelector construction guards
# ---------------------------------------------------------------------------

class TestFFTSelectorConstruction:
    def test_empty_nodes_raises(self):
        with pytest.raises(ValueError, match="at least one node"):
            FFTSelector([])

    def test_last_node_missing_false_exit_raises(self):
        with pytest.raises(ValueError, match="Last FFTNode"):
            FFTSelector([FFTNode("is_opener", true_exit="TitleSlide", false_exit=None)])

    def test_last_node_missing_true_exit_raises(self):
        with pytest.raises(ValueError, match="Last FFTNode"):
            FFTSelector([FFTNode("is_opener", true_exit=None, false_exit="ContentSlide")])

    def test_single_node_with_both_exits_ok(self):
        sel = FFTSelector([FFTNode("is_opener", true_exit="TitleSlide", false_exit="ContentSlide")])
        assert sel is not None

    def test_intermediate_node_may_have_one_exit(self):
        sel = FFTSelector([
            FFTNode("is_opener", true_exit="TitleSlide"),
            FFTNode("has_bullets", true_exit="ContentSlide", false_exit="ContentSlide"),
        ])
        assert sel is not None


# ---------------------------------------------------------------------------
# DEFAULT_FFT — one test per exit branch
# ---------------------------------------------------------------------------

class TestDefaultFFTClassify:
    def test_is_opener_exits_title_slide(self):
        assert DEFAULT_FFT.classify(ContentSignals(is_opener=True)) == "TitleSlide"

    def test_is_section_exits_section_slide(self):
        assert DEFAULT_FFT.classify(ContentSignals(is_section=True)) == "SectionSlide"

    def test_has_scr_exits_scr_narrative(self):
        assert DEFAULT_FFT.classify(ContentSignals(has_scr=True)) == "SCRNarrativeSlide"

    def test_has_chart_exits_chart_placeholder(self):
        assert DEFAULT_FFT.classify(ContentSignals(has_chart=True)) == "ChartPlaceholderSlide"

    def test_has_columns_exits_two_column(self):
        assert DEFAULT_FFT.classify(ContentSignals(has_columns=True)) == "TwoColumnSlide"

    def test_default_exits_content_slide(self):
        assert DEFAULT_FFT.classify(ContentSignals()) == "ContentSlide"

    def test_no_bullets_still_content_slide(self):
        assert DEFAULT_FFT.classify(ContentSignals(has_bullets=False)) == "ContentSlide"


# ---------------------------------------------------------------------------
# Priority ordering — earlier cues beat later ones
# ---------------------------------------------------------------------------

class TestFFTPriority:
    def test_opener_beats_scr(self):
        s = ContentSignals(is_opener=True, has_scr=True)
        assert DEFAULT_FFT.classify(s) == "TitleSlide"

    def test_opener_beats_chart(self):
        s = ContentSignals(is_opener=True, has_chart=True)
        assert DEFAULT_FFT.classify(s) == "TitleSlide"

    def test_section_beats_scr(self):
        s = ContentSignals(is_section=True, has_scr=True)
        assert DEFAULT_FFT.classify(s) == "SectionSlide"

    def test_section_beats_chart(self):
        s = ContentSignals(is_section=True, has_chart=True)
        assert DEFAULT_FFT.classify(s) == "SectionSlide"

    def test_scr_beats_chart(self):
        s = ContentSignals(has_scr=True, has_chart=True)
        assert DEFAULT_FFT.classify(s) == "SCRNarrativeSlide"

    def test_scr_beats_columns(self):
        s = ContentSignals(has_scr=True, has_columns=True)
        assert DEFAULT_FFT.classify(s) == "SCRNarrativeSlide"

    def test_chart_beats_columns(self):
        s = ContentSignals(has_chart=True, has_columns=True)
        assert DEFAULT_FFT.classify(s) == "ChartPlaceholderSlide"

    def test_columns_beats_bullets(self):
        s = ContentSignals(has_columns=True, has_bullets=True)
        assert DEFAULT_FFT.classify(s) == "TwoColumnSlide"


# ---------------------------------------------------------------------------
# Custom trees
# ---------------------------------------------------------------------------

class TestCustomFFT:
    def test_two_node_tree(self):
        sel = FFTSelector([
            FFTNode("has_chart", true_exit="ChartPlaceholderSlide"),
            FFTNode("has_bullets", true_exit="ContentSlide", false_exit="ContentSlide"),
        ])
        assert sel.classify(ContentSignals(has_chart=True)) == "ChartPlaceholderSlide"
        assert sel.classify(ContentSignals()) == "ContentSlide"

    def test_false_exit_branch(self):
        sel = FFTSelector([
            FFTNode("has_chart", true_exit="ChartPlaceholderSlide", false_exit="ContentSlide"),
        ])
        assert sel.classify(ContentSignals(has_chart=False)) == "ContentSlide"
        assert sel.classify(ContentSignals(has_chart=True)) == "ChartPlaceholderSlide"
