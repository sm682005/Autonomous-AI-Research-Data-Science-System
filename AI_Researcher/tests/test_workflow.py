"""
Unit tests for LangGraph state machine routing, conditional edges,
revision limiting, and report generation service.
"""

from unittest.mock import patch, MagicMock
import pytest

from AI_Researcher.config import get_gemini_client, MAX_REVISIONS
from AI_Researcher.graph.state import ResearchState
from AI_Researcher.graph.workflow import (
    route_after_retrieval,
    route_after_judge,
    refinement_node,
    no_papers_handler_node,
    build_research_graph,
)
from AI_Researcher.schemas.research import (
    PaperMetadata,
    ValidationResult,
    LiteratureReview,
    ResearchPlan,
)
from AI_Researcher.services.report_service import (
    build_final_report,
    render_markdown_report,
    save_report,
    list_saved_reports,
)


def test_missing_api_key_raises_informative_error(monkeypatch):
    """Tests that missing or placeholder GEMINI_API_KEY raises a descriptive ValueError."""
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(ValueError) as excinfo:
        get_gemini_client()
    assert "GEMINI_API_KEY is missing" in str(excinfo.value)

    monkeypatch.setenv("GEMINI_API_KEY", "MY_GEMINI_API_KEY")
    with pytest.raises(ValueError) as excinfo2:
        get_gemini_client()
    assert "GEMINI_API_KEY is missing" in str(excinfo2.value)


def test_route_after_retrieval_empty():
    """Tests that empty retrieval routes to no_papers_handler."""
    state: ResearchState = {"retrieved_papers": []}
    next_node = route_after_retrieval(state)
    assert next_node == "no_papers_handler"


def test_route_after_retrieval_with_papers():
    """Tests that successful retrieval routes to paper_analyzer."""
    paper = PaperMetadata(
        id="P001",
        title="Test",
        source="arXiv",
        paper_id="2401.0001",
        url="http://arxiv.org",
    )
    state: ResearchState = {"retrieved_papers": [paper]}
    next_node = route_after_retrieval(state)
    assert next_node == "paper_analyzer"


def test_route_after_judge_revision_needed():
    """Tests that validation requesting revision routes to refinement if under max revisions."""
    val = ValidationResult(
        is_valid=False,
        score=5.0,
        warnings=["Unverified claims"],
        critique="Needs revision",
        revision_needed=True,
    )
    state: ResearchState = {
        "validation_result": val,
        "revision_count": 0,
        "max_revisions": 1,
    }
    next_node = route_after_judge(state)
    assert next_node == "refinement_node"


def test_route_after_judge_revision_limit_reached():
    """Tests that reaching max revisions terminates loop to report_generator without hanging."""
    val = ValidationResult(
        is_valid=False,
        score=5.0,
        warnings=["Persistent defect"],
        critique="Revision exhausted",
        revision_needed=True,
    )
    state: ResearchState = {
        "validation_result": val,
        "revision_count": 1,  # Equal to max_revisions
        "max_revisions": 1,
    }
    next_node = route_after_judge(state)
    assert next_node == "report_generator"


def test_refinement_node_increments_counter():
    """Tests revision counter incrementation."""
    state: ResearchState = {
        "revision_count": 0,
        "warnings": ["Warning 1"],
        "validation_result": ValidationResult(
            is_valid=False, score=4.0, warnings=["Warning 2"], critique="Fix citations", revision_needed=True
        ),
    }
    updated = refinement_node(state)
    assert updated["revision_count"] == 1
    assert "Warning 1" in updated["warnings"]
    assert "Warning 2" in updated["warnings"]


def test_no_papers_handler_generates_limitation_state():
    """Tests no_papers_handler creates an honest limitation record rather than fabricating."""
    state: ResearchState = {"research_question": "Unknown obscure query 12345"}
    result = no_papers_handler_node(state)
    assert result["status"] == "NO_PAPERS_FOUND"
    assert result["retrieved_papers"] == []
    assert result["validation_result"].is_valid is False
    assert any("refuses to fabricate" in w for w in result["validation_result"].warnings)


def test_build_and_render_report_offline():
    """Tests full local report compilation and markdown rendering without external calls."""
    paper = PaperMetadata(
        id="P001",
        title="Offline Test Paper",
        authors=["Scientist A"],
        abstract="Offline testing abstract.",
        source="arXiv",
        paper_id="2401.99999",
        url="https://arxiv.org/abs/2401.99999",
        pdf_url="https://arxiv.org/pdf/2401.99999.pdf",
    )
    lit = LiteratureReview(
        synthesis_narrative="Synthetic review analyzing [P001].",
        common_methodologies=["Offline simulation"],
        divergent_approaches=["None"],
        agreements_and_disagreements=["Consensus"],
        evidence_limitations=["Simulation depth only"],
        unresolved_questions=["Real world transfer"],
    )
    val = ValidationResult(
        is_valid=True,
        score=9.0,
        warnings=[],
        critique="Methodologically rigorous offline audit.",
        revision_needed=False,
    )
    report = build_final_report(
        research_question="How to build offline autonomous test harnesses?",
        papers=[paper],
        analyses=[],
        lit_review=lit,
        gaps=[],
        hypotheses=[],
        experiment_designs=[],
        validation=val,
    )

    md = render_markdown_report(report)
    assert "# Autonomous Scientific Assessment:" in md
    assert "Retrieved and verified **1** peer-reviewed records:" in md
    assert "[P001]" in md

    # Save to disk
    run_dir, md_path, json_path = save_report(report)
    assert md_path.exists()
    assert json_path.exists()

    # List saved reports
    archived = list_saved_reports()
    assert len(archived) >= 1
    assert any("offline" in a["research_question"].lower() for a in archived)


def test_langgraph_compilation():
    """Tests that the LangGraph StateGraph compiles cleanly with all nodes and conditional edges."""
    graph = build_research_graph()
    assert graph is not None
