"""
Unit tests for Pydantic schema validation, constraints, serialization, and deserialization.
No external network or API keys required.
"""

import pytest
from pydantic import ValidationError
from AI_Researcher.schemas.research import (
    PaperMetadata,
    ResearchPlan,
    PaperAnalysis,
    LiteratureReview,
    ResearchGap,
    Hypothesis,
    ExperimentDesign,
    ValidationResult,
    FinalReport,
)


def test_paper_metadata_valid():
    """Tests valid creation of PaperMetadata."""
    p = PaperMetadata(
        id="P001",
        title="Attention Is All You Need",
        authors=["Vaswani, A.", "Shazeer, N."],
        abstract="The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
        published_date="2017-06-12",
        source="arXiv",
        paper_id="1706.03762",
        url="https://arxiv.org/abs/1706.03762",
        pdf_url="https://arxiv.org/pdf/1706.03762.pdf",
        abstract_only=True,
    )
    assert p.id == "P001"
    assert len(p.authors) == 2
    assert p.abstract_only is True


def test_research_plan_valid():
    """Tests ResearchPlan schema validation."""
    plan = ResearchPlan(
        research_objective="Investigate state space models for long-context language modeling.",
        search_queries=["state space models", "Mamba long context", "S4 sequence modeling"],
        subquestions=["How do SSMs compare to multi-head self-attention on associative recall?"],
        scope_and_constraints="Language modeling benchmarks with context lengths up to 32k tokens.",
        analysis_plan="Extract architectural parameters, memory scaling, and perplexity on standard corpora.",
    )
    assert len(plan.search_queries) == 3
    data = plan.model_dump()
    assert "research_objective" in data


def test_validation_result_score_bounds():
    """Tests score boundaries on ValidationResult (0.0 to 10.0)."""
    val = ValidationResult(
        is_valid=True,
        score=9.5,
        warnings=[],
        critique="Rigorous methodology.",
        revision_needed=False,
    )
    assert val.score == 9.5

    # Should raise error if score is above 10.0
    with pytest.raises(ValidationError):
        ValidationResult(
            is_valid=True,
            score=11.0,
            warnings=[],
            critique="Invalid score",
            revision_needed=False,
        )

    # Should raise error if score is below 0.0
    with pytest.raises(ValidationError):
        ValidationResult(
            is_valid=False,
            score=-1.0,
            warnings=[],
            critique="Negative score",
            revision_needed=True,
        )


def test_research_gap_and_hypothesis_linking():
    """Tests structure and linkage of research gaps and hypotheses."""
    gap = ResearchGap(
        gap_id="GAP-01",
        description="Limited theoretical understanding of sub-quadratic attention on non-synthetic tasks.",
        supporting_paper_ids=["P001", "P002"],
        evidence_summary="Both papers evaluate synthetic synthetic benchmarks only.",
        counterevidence="Preliminary work in P003 tested code generation.",
        why_it_matters="Real-world deployment demands verification on messy multi-turn documents.",
        confidence_level="Medium",
        required_further_research="Evaluation on multi-document summarization corpora.",
    )
    assert gap.gap_id == "GAP-01"
    assert "P001" in gap.supporting_paper_ids

    hyp = Hypothesis(
        hypothesis_id="HYP-01",
        linked_gap_id="GAP-01",
        statement="Selective state space layers yield lower latency with parity in BLEU on 32k context documents compared to dense attention.",
        supporting_evidence="Linear time complexity demonstrated in P002.",
        variables_to_investigate=["Context window length (8k-32k)", "Inference latency (ms)", "BLEU score"],
        expected_relationship="Sub-linear latency growth with no degradation in factual recall.",
        testability_method="Controlled A/B testing on GovReport and QMSum datasets.",
        known_uncertainties="Hardware kernel optimization differences across GPU architectures.",
    )
    assert hyp.linked_gap_id == gap.gap_id


def test_final_report_serialization():
    """Tests that a complete FinalReport serializes and deserializes accurately."""
    paper = PaperMetadata(
        id="P001",
        title="Test Paper Title",
        authors=["Author One"],
        abstract="Test abstract content.",
        source="arXiv",
        paper_id="2401.00001",
        url="https://arxiv.org/abs/2401.00001",
    )
    analysis = PaperAnalysis(
        paper_id="P001",
        research_problem="Problem statement",
        methodology="Test methodology",
        dataset="Not reported in abstract",
        evaluation_metrics="Accuracy",
        main_findings="Significant improvement",
        limitations="Abstract evidence only",
        future_directions="Full scaling experiments",
    )
    lit = LiteratureReview(
        synthesis_narrative="Comparative synthesis of [P001].",
        common_methodologies=["Transformer architectures"],
        divergent_approaches=["Sparse vs dense"],
        agreements_and_disagreements=["Consensus on scaling laws"],
        evidence_limitations=["Abstract only"],
        unresolved_questions=["Sample efficiency"],
    )
    val = ValidationResult(
        is_valid=True,
        score=8.5,
        warnings=[],
        critique="Well grounded in retrieved evidence.",
        revision_needed=False,
    )
    report = FinalReport(
        title="Autonomous Scientific Assessment: AI Efficiency",
        research_question="How to optimize inference efficiency?",
        executive_summary="Summary text",
        methodology="Methodology text",
        papers=[paper],
        analyses=[analysis],
        literature_review=lit,
        research_gaps=[],
        hypotheses=[],
        experiment_designs=[],
        validation=val,
        limitations_and_uncertainties=["Test limitation"],
        references=[{"id": "P001", "title": "Test Paper Title", "authors": "Author One", "published": "2024", "source": "arXiv", "url": "https://arxiv.org/abs/2401.00001", "pdf_url": "N/A"}],
        generated_at="2026-10-26T00:00:00",
    )

    dumped = report.model_dump_json()
    reloaded = FinalReport.model_validate_json(dumped)
    assert reloaded.title == report.title
    assert len(reloaded.papers) == 1
    assert reloaded.papers[0].id == "P001"
