"""
Unit tests for Citation Verifier and Alignment Auditor.
Tests detection of valid IDs, orphan citations, ungrounded references, and gap-hypothesis linking.
"""

from AI_Researcher.schemas.research import PaperMetadata, ResearchGap, Hypothesis
from AI_Researcher.tools.citation_verifier import (
    extract_citation_ids,
    verify_citations,
    verify_gap_hypothesis_alignment,
)


def create_sample_papers():
    return [
        PaperMetadata(
            id="P001",
            title="Foundations of Transformers",
            authors=["Vaswani et al."],
            abstract="Attention mechanism formulation.",
            source="arXiv",
            paper_id="1706.03762",
            url="https://arxiv.org/abs/1706.03762",
        ),
        PaperMetadata(
            id="P002",
            title="BERT: Pre-training of Deep Bidirectional Transformers",
            authors=["Devlin et al."],
            abstract="Masked language modeling.",
            source="arXiv",
            paper_id="1810.04805",
            url="https://arxiv.org/abs/1810.04805",
        ),
    ]


def test_extract_citation_ids():
    """Tests regex extraction of stable paper IDs."""
    text = "As shown in [P001] and contrasting with P002, earlier work like P001 was influential."
    extracted = extract_citation_ids(text)
    assert extracted == ["P001", "P002"]


def test_verify_citations_all_valid():
    """Tests when all cited IDs exist in retrieved papers."""
    papers = create_sample_papers()
    text_blocks = [
        ("Lit Review", "Prior work [P001] and [P002] explored bidirectional encodings."),
    ]
    is_valid, invalid_ids, warnings = verify_citations(papers, text_blocks)
    assert is_valid is True
    assert len(invalid_ids) == 0
    assert len(warnings) == 0


def test_verify_citations_detects_fabricated_or_missing_id():
    """Tests that citing an unretrieved paper ID flags an integrity defect."""
    papers = create_sample_papers()
    text_blocks = [
        ("Lit Review", "P001 established attention, whereas [P099] introduced graph tokens."),
    ]
    is_valid, invalid_ids, warnings = verify_citations(papers, text_blocks)
    assert is_valid is False
    assert "P099" in invalid_ids
    assert len(warnings) > 0
    assert "P099" in warnings[0]


def test_verify_gap_hypothesis_alignment():
    """Tests linking between papers, gaps, and hypotheses."""
    papers = create_sample_papers()
    
    # Gap citing valid paper
    gap1 = ResearchGap(
        gap_id="GAP-01",
        description="Quadratic computational complexity in long sequences.",
        supporting_paper_ids=["P001"],
        evidence_summary="Shown in P001.",
        why_it_matters="Scaling barrier.",
        confidence_level="High",
        required_further_research="Empirical profiling.",
    )
    
    # Gap citing NONEXISTENT paper
    gap2 = ResearchGap(
        gap_id="GAP-02",
        description="Missing evaluation on edge hardware.",
        supporting_paper_ids=["P777"],
        evidence_summary="Invalid citation.",
        why_it_matters="Edge devices.",
        confidence_level="Low",
        required_further_research="Edge testing.",
    )

    # Hypothesis linking to valid gap
    hyp1 = Hypothesis(
        hypothesis_id="HYP-01",
        linked_gap_id="GAP-01",
        statement="Linear attention reduces memory without accuracy loss.",
        supporting_evidence="P001 baseline.",
        variables_to_investigate=["Memory", "Tokens"],
        expected_relationship="Linear scaling.",
        testability_method="Benchmark profiling.",
        known_uncertainties="Hardware dependencies.",
    )

    # Hypothesis linking to NONEXISTENT gap
    hyp2 = Hypothesis(
        hypothesis_id="HYP-02",
        linked_gap_id="GAP-99",  # Invalid
        statement="Orphan hypothesis test.",
        supporting_evidence="No evidence.",
        variables_to_investigate=["Var1"],
        expected_relationship="Unknown.",
        testability_method="None.",
        known_uncertainties="High.",
    )

    warnings = verify_gap_hypothesis_alignment(papers, [gap1, gap2], [hyp1, hyp2])
    assert any("P777" in w for w in warnings)
    assert any("GAP-99" in w for w in warnings)
