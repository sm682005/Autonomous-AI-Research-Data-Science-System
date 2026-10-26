"""
Research State Definition.
Strongly typed shared state coordinated by LangGraph across all workflow stages.
"""

from typing import TypedDict, List, Optional, Tuple, Any
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


class ResearchState(TypedDict, total=False):
    """LangGraph shared research state."""
    # Inputs
    research_question: str
    target_paper_count: int
    date_range: Optional[Tuple[int, int]]
    detail_level: str

    # Agent outputs
    research_plan: Optional[ResearchPlan]
    retrieved_papers: List[PaperMetadata]
    paper_analyses: List[PaperAnalysis]
    literature_review: Optional[LiteratureReview]
    research_gaps: List[ResearchGap]
    hypotheses: List[Hypothesis]
    experiment_designs: List[ExperimentDesign]
    validation_result: Optional[ValidationResult]
    final_report: Optional[FinalReport]

    # Control flow & status
    revision_count: int
    max_revisions: int
    current_stage: str
    warnings: List[str]
    error_message: Optional[str]
    status: str  # "IN_PROGRESS", "COMPLETED", "NO_PAPERS_FOUND", "REVISION_EXHAUSTED"
