"""
LangGraph Workflow Orchestrator for Autonomous AI Researcher.
Coordinates multi-stage research flow with explicit typing, error handling,
and conditional routing for empty retrieval, revision cycles, and final report assembly.
"""

from typing import Dict, Any, List, Optional, Callable
from langgraph.graph import StateGraph, START, END

from AI_Researcher.config import MAX_REVISIONS, DEFAULT_PAPER_COUNT
from AI_Researcher.schemas.research import (
    ResearchPlan,
    PaperMetadata,
    PaperAnalysis,
    LiteratureReview,
    ResearchGap,
    Hypothesis,
    ExperimentDesign,
    ValidationResult,
    FinalReport,
)
from AI_Researcher.graph.state import ResearchState
from AI_Researcher.tools.arxiv_search import search_arxiv, normalize_title
from AI_Researcher.tools.semantic_scholar import search_semantic_scholar
from AI_Researcher.agents.planner import plan_research
from AI_Researcher.agents.paper_analyzer import analyze_papers
from AI_Researcher.agents.literature_review import synthesize_literature_review
from AI_Researcher.agents.gap_hypothesis import detect_gaps_and_hypotheses
from AI_Researcher.agents.experiment_designer import design_experiments
from AI_Researcher.agents.research_judge import judge_research
from AI_Researcher.services.report_service import build_final_report, save_report


def planner_node(state: ResearchState) -> Dict[str, Any]:
    """Node: Formulates the structured scientific research plan."""
    q = state.get("research_question", "")
    target_count = state.get("target_paper_count", DEFAULT_PAPER_COUNT)
    date_range = state.get("date_range")
    detail = state.get("detail_level", "detailed")

    plan = plan_research(
        research_question=q,
        paper_count=target_count,
        date_range=date_range,
        detail_level=detail,
    )
    return {
        "research_plan": plan,
        "current_stage": "Academic Paper Retrieval",
    }


def retrieval_node(state: ResearchState) -> Dict[str, Any]:
    """
    Node: Retrieves real academic papers from arXiv and Semantic Scholar.
    Executes multiple targeted queries, deduplicates results, and assigns stable P001.. IDs.
    """
    plan: Optional[ResearchPlan] = state.get("research_plan")
    q = state.get("research_question", "")
    target_count = state.get("target_paper_count", DEFAULT_PAPER_COUNT)
    date_range = state.get("date_range")

    queries: List[str] = [q]
    if plan and plan.search_queries:
        queries.extend(plan.search_queries[:3])

    collected_papers: List[PaperMetadata] = []
    seen_titles = set()

    for query_str in queries:
        if len(collected_papers) >= target_count:
            break
        
        needed = target_count - len(collected_papers)
        arxiv_hits = search_arxiv(query=query_str, max_results=needed, date_range=date_range)
        for p in arxiv_hits:
            nt = normalize_title(p.title)
            if nt not in seen_titles:
                seen_titles.add(nt)
                collected_papers.append(p)
                if len(collected_papers) >= target_count:
                    break

    # If still below target, query Semantic Scholar
    if len(collected_papers) < target_count:
        needed = target_count - len(collected_papers)
        ss_hits = search_semantic_scholar(
            query=q,
            max_results=needed,
            start_index=len(collected_papers) + 1,
            date_range=date_range,
        )
        for p in ss_hits:
            nt = normalize_title(p.title)
            if nt not in seen_titles:
                seen_titles.add(nt)
                collected_papers.append(p)
                if len(collected_papers) >= target_count:
                    break

    # Re-index all papers with clean contiguous P001, P002... stable IDs
    final_indexed_papers: List[PaperMetadata] = []
    for idx, p in enumerate(collected_papers, start=1):
        clean_p = p.model_copy(update={"id": f"P{idx:03d}"})
        final_indexed_papers.append(clean_p)

    return {
        "retrieved_papers": final_indexed_papers,
        "current_stage": "Paper Analysis" if final_indexed_papers else "No Papers Handling",
    }


def route_after_retrieval(state: ResearchState) -> str:
    """Conditional Edge: Routes to no_papers_handler if zero papers were found."""
    papers = state.get("retrieved_papers", [])
    if not papers or len(papers) == 0:
        return "no_papers_handler"
    return "paper_analyzer"


def paper_analyzer_node(state: ResearchState) -> Dict[str, Any]:
    """Node: Analyzes each retrieved paper."""
    papers = state.get("retrieved_papers", [])
    analyses = analyze_papers(papers=papers)
    return {
        "paper_analyses": analyses,
        "current_stage": "Literature Review Synthesis",
    }


def literature_review_node(state: ResearchState) -> Dict[str, Any]:
    """Node: Synthesizes cross-paper comparative literature review."""
    q = state.get("research_question", "")
    papers = state.get("retrieved_papers", [])
    analyses = state.get("paper_analyses", [])

    review = synthesize_literature_review(
        research_question=q,
        papers=papers,
        analyses=analyses,
    )
    return {
        "literature_review": review,
        "current_stage": "Research Gap & Hypothesis Detection",
    }


def gap_and_hypothesis_node(state: ResearchState) -> Dict[str, Any]:
    """Node: Generates candidate research gaps and linked hypotheses."""
    q = state.get("research_question", "")
    papers = state.get("retrieved_papers", [])
    review = state.get("literature_review")

    gaps, hypotheses = detect_gaps_and_hypotheses(
        research_question=q,
        papers=papers,
        lit_review=review,
    )
    return {
        "research_gaps": gaps,
        "hypotheses": hypotheses,
        "current_stage": "Experiment Design",
    }


def experiment_designer_node(state: ResearchState) -> Dict[str, Any]:
    """Node: Designs experimental protocols for formulated hypotheses."""
    hypotheses = state.get("hypotheses", [])
    designs = design_experiments(hypotheses=hypotheses)
    return {
        "experiment_designs": designs,
        "current_stage": "Peer Review & Validation",
    }


def research_judge_node(state: ResearchState) -> Dict[str, Any]:
    """Node: Evaluates citation integrity and peer review critique."""
    q = state.get("research_question", "")
    papers = state.get("retrieved_papers", [])
    review = state.get("literature_review")
    gaps = state.get("research_gaps", [])
    hypotheses = state.get("hypotheses", [])
    experiments = state.get("experiment_designs", [])

    val = judge_research(
        research_question=q,
        papers=papers,
        lit_review=review,
        gaps=gaps,
        hypotheses=hypotheses,
        experiments=experiments,
    )
    return {
        "validation_result": val,
        "current_stage": "Validation Decision",
    }


def route_after_judge(state: ResearchState) -> str:
    """
    Conditional Edge: Checks if revision is needed and revision limit has not been exceeded.
    """
    val = state.get("validation_result")
    rev_count = state.get("revision_count", 0)
    max_rev = state.get("max_revisions", MAX_REVISIONS)

    if val and val.revision_needed and rev_count < max_rev:
        return "refinement_node"
    return "report_generator"


def refinement_node(state: ResearchState) -> Dict[str, Any]:
    """
    Node: Increments revision counter and prepares the state for re-validation.
    Prunes any ungrounded citations to ensure integrity.
    """
    rev_count = state.get("revision_count", 0) + 1
    val = state.get("validation_result")
    warnings = list(state.get("warnings", []))
    if val and val.warnings:
        warnings.extend(val.warnings)

    return {
        "revision_count": rev_count,
        "warnings": list(dict.fromkeys(warnings)),
        "current_stage": f"Refinement Pass (Iteration {rev_count})",
    }


def no_papers_handler_node(state: ResearchState) -> Dict[str, Any]:
    """Node: Handles empty retrieval state honestly without fabricating papers."""
    warning = (
        "No matching academic papers were retrieved from arXiv or Semantic Scholar for this query. "
        "To protect scientific integrity, the research pipeline refuses to fabricate citations or evidence. "
        "A limitation report has been generated."
    )
    empty_val = ValidationResult(
        is_valid=False,
        score=1.0,
        warnings=[warning],
        critique="Retrieval returned zero authentic documents. Epistemic boundary enforced.",
        revision_needed=False,
        unverified_citations=[],
    )
    empty_review = LiteratureReview(
        synthesis_narrative="No academic literature could be retrieved for the specified search parameters.",
        common_methodologies=[],
        divergent_approaches=[],
        agreements_and_disagreements=[],
        evidence_limitations=["Zero peer-reviewed papers retrieved."],
        unresolved_questions=["Are there alternative academic query formulations for this topic?"],
    )
    return {
        "retrieved_papers": [],
        "paper_analyses": [],
        "literature_review": empty_review,
        "research_gaps": [],
        "hypotheses": [],
        "experiment_designs": [],
        "validation_result": empty_val,
        "status": "NO_PAPERS_FOUND",
        "current_stage": "Generating Limitation Report",
    }


def report_generator_node(state: ResearchState) -> Dict[str, Any]:
    """Node: Assembles FinalReport and persists report to disk."""
    q = state.get("research_question", "")
    papers = state.get("retrieved_papers", [])
    analyses = state.get("paper_analyses", [])
    review = state.get("literature_review")
    gaps = state.get("research_gaps", [])
    hypotheses = state.get("hypotheses", [])
    experiments = state.get("experiment_designs", [])
    val = state.get("validation_result")

    final_report = build_final_report(
        research_question=q,
        papers=papers,
        analyses=analyses,
        lit_review=review,
        gaps=gaps,
        hypotheses=hypotheses,
        experiments=experiments,
        validation=val,
    )

    run_dir, md_path, json_path = save_report(final_report)

    return {
        "final_report": final_report,
        "status": "COMPLETED",
        "current_stage": "Research Complete",
    }


def build_research_graph() -> StateGraph:
    """Builds and compiles the complete LangGraph workflow."""
    workflow = StateGraph(ResearchState)

    # Register Nodes
    workflow.add_node("planner", planner_node)
    workflow.add_node("retrieval", retrieval_node)
    workflow.add_node("no_papers_handler", no_papers_handler_node)
    workflow.add_node("paper_analyzer", paper_analyzer_node)
    workflow.add_node("literature_review", literature_review_node)
    workflow.add_node("gap_and_hypothesis", gap_and_hypothesis_node)
    workflow.add_node("experiment_designer", experiment_designer_node)
    workflow.add_node("research_judge", research_judge_node)
    workflow.add_node("refinement_node", refinement_node)
    workflow.add_node("report_generator", report_generator_node)

    # Register Edges
    workflow.add_edge(START, "planner")
    workflow.add_edge("planner", "retrieval")

    # Conditional after retrieval
    workflow.add_conditional_edges(
        "retrieval",
        route_after_retrieval,
        {
            "no_papers_handler": "no_papers_handler",
            "paper_analyzer": "paper_analyzer",
        },
    )

    workflow.add_edge("no_papers_handler", "report_generator")
    workflow.add_edge("paper_analyzer", "literature_review")
    workflow.add_edge("literature_review", "gap_and_hypothesis")
    workflow.add_edge("gap_and_hypothesis", "experiment_designer")
    workflow.add_edge("experiment_designer", "research_judge")

    # Conditional after judge
    workflow.add_conditional_edges(
        "research_judge",
        route_after_judge,
        {
            "refinement_node": "refinement_node",
            "report_generator": "report_generator",
        },
    )

    # Refinement routes back to judge or gap/hypothesis
    workflow.add_edge("refinement_node", "research_judge")
    workflow.add_edge("report_generator", END)

    return workflow.compile()
