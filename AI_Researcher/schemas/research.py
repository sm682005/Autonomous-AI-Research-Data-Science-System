"""
Pydantic Schemas for Autonomous AI Researcher.
Enforces rigorous typing, serialization, and validation across all agent stages.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class PaperMetadata(BaseModel):
    """Metadata for an academic paper retrieved from arXiv or Semantic Scholar."""
    id: str = Field(description="Unique stable reference ID, e.g. P001, P002")
    title: str = Field(description="Title of the paper")
    authors: List[str] = Field(default_factory=list, description="List of author names")
    abstract: str = Field(default="", description="Abstract text of the paper")
    published_date: Optional[str] = Field(default=None, description="Publication date or year (ISO or YYYY)")
    source: str = Field(default="arXiv", description="Source repository e.g. arXiv, Semantic Scholar")
    paper_id: str = Field(description="Original ID in the source repository, e.g. 2305.18290")
    url: str = Field(description="Web URL to paper landing page or abstract")
    pdf_url: Optional[str] = Field(default=None, description="Direct URL to PDF if available")
    abstract_only: bool = Field(default=True, description="True if analysis is restricted to abstract evidence")


class ResearchPlan(BaseModel):
    """Structured output from the Research Planner Agent."""
    research_objective: str = Field(description="Clear, formalized scientific research objective")
    search_queries: List[str] = Field(description="Targeted academic search queries for arXiv/APIs")
    subquestions: List[str] = Field(description="Key scientific subquestions to investigate")
    scope_and_constraints: str = Field(description="Defined domain scope, boundaries, and methodology constraints")
    analysis_plan: str = Field(description="Systematic plan for comparative paper analysis and synthesis")


class PaperAnalysis(BaseModel):
    """Detailed scientific extraction from a single retrieved academic paper."""
    paper_id: str = Field(description="Stable reference identifier, e.g. P001")
    research_problem: str = Field(description="The primary scientific or technical problem addressed")
    methodology: str = Field(description="Algorithms, architectures, or theoretical frameworks used")
    dataset: str = Field(default="Not reported in abstract", description="Datasets, benchmarks, or data sources")
    evaluation_metrics: str = Field(default="Not reported in abstract", description="Metrics used for assessment")
    main_findings: str = Field(description="Key discoveries, performance gains, or proven properties")
    limitations: str = Field(description="Reported or identified limitations and failure modes")
    future_directions: str = Field(description="Suggested future research avenues indicated by authors")


class LiteratureReview(BaseModel):
    """Synthesized cross-paper literature review and comparative analysis."""
    synthesis_narrative: str = Field(description="Cohesive academic literature review citing papers via [Pxxx]")
    common_methodologies: List[str] = Field(description="Methodological paradigms shared across multiple papers")
    divergent_approaches: List[str] = Field(description="Contrasting techniques and algorithmic divergences")
    agreements_and_disagreements: List[str] = Field(description="Consensus points vs disputed claims in literature")
    evidence_limitations: List[str] = Field(description="Caveats regarding dataset scale, benchmarks, or abstract-only depth")
    unresolved_questions: List[str] = Field(description="High-priority scientific questions still unanswered")


class ResearchGap(BaseModel):
    """Identified candidate research gap grounded in analyzed literature."""
    gap_id: str = Field(description="Identifier e.g. GAP-01")
    description: str = Field(description="Precise description of the gap or unaddressed challenge")
    supporting_paper_ids: List[str] = Field(description="Paper IDs demonstrating the gap, e.g. ['P001', 'P003']")
    evidence_summary: str = Field(description="Synthesis of evidence indicating the gap exists")
    counterevidence: Optional[str] = Field(default=None, description="Any identified counterevidence or partial solutions")
    why_it_matters: str = Field(description="Scientific and practical significance of resolving this gap")
    confidence_level: str = Field(default="Medium", description="Confidence in gap validity: High, Medium, or Low")
    required_further_research: str = Field(description="Necessary empirical or theoretical steps to verify this gap")


class Hypothesis(BaseModel):
    """Testable scientific hypothesis addressing an identified research gap."""
    hypothesis_id: str = Field(description="Identifier e.g. HYP-01")
    linked_gap_id: str = Field(description="Identifier of the research gap addressed, e.g. GAP-01")
    statement: str = Field(description="Formal testable hypothesis statement")
    supporting_evidence: str = Field(description="Foundational evidence and theoretical rationale from papers")
    variables_to_investigate: List[str] = Field(description="Independent, dependent, and controlled variables")
    expected_relationship: str = Field(description="Hypothesized relationship, directionality, or mechanism")
    testability_method: str = Field(description="Specific empirical or statistical procedure to test validity")
    known_uncertainties: str = Field(description="Potential failure modes, risks, and confounding effects")


class ExperimentDesign(BaseModel):
    """Concrete experiment specification for testing a hypothesis."""
    experiment_id: str = Field(description="Identifier e.g. EXP-01")
    linked_hypothesis_id: str = Field(description="Identifier of tested hypothesis, e.g. HYP-01")
    research_objective: str = Field(description="Target objective and scientific question of the experiment")
    required_dataset_characteristics: str = Field(description="Dataset domain, size, distribution, and split criteria")
    baseline_methods: List[str] = Field(description="Standard or state-of-the-art baselines for comparison")
    proposed_approach: str = Field(description="Architectural or procedural intervention to be tested")
    experimental_steps: List[str] = Field(description="Step-by-step reproducible protocol")
    evaluation_metrics: List[str] = Field(description="Quantitative metrics for validation and significance testing")
    data_leakage_prevention: str = Field(description="Measures to avoid target leakage, snooping, or train-test overlap")
    confounding_factors: List[str] = Field(description="Confounding variables and control strategies")
    expected_outcomes_predictions: str = Field(description="Explicitly labeled predictions (NOT measured outcomes)")
    limitations_and_reproducibility: str = Field(description="Computational budget, seeds, and reproducibility checklist")


class ValidationResult(BaseModel):
    """Review results from the Research Judge and Citation Verifier."""
    is_valid: bool = Field(description="Whether the research outputs meet scientific quality and citation standards")
    score: float = Field(ge=0.0, le=10.0, description="Overall rigor score from 0.0 to 10.0")
    warnings: List[str] = Field(default_factory=list, description="Specific warnings, unverified claims, or citation defects")
    critique: str = Field(description="Qualitative critical review of logic, consistency, and feasibility")
    revision_needed: bool = Field(default=False, description="True if a revision pass should be triggered")
    unverified_citations: List[str] = Field(default_factory=list, description="Paper IDs referenced that do not exist")


class FinalReport(BaseModel):
    """Complete consolidated research dossier ready for export."""
    title: str = Field(description="Scientific report title")
    research_question: str = Field(description="Original research question entered by user")
    executive_summary: str = Field(description="High-level executive summary of findings and proposed roadmap")
    methodology: str = Field(description="Workflow and search strategy utilized by the autonomous researcher")
    papers: List[PaperMetadata] = Field(description="All retrieved and verified academic papers")
    analyses: List[PaperAnalysis] = Field(description="Individual paper analyses")
    literature_review: LiteratureReview = Field(description="Comparative literature review and synthesis")
    research_gaps: List[ResearchGap] = Field(description="Identified research gaps")
    hypotheses: List[Hypothesis] = Field(description="Formulated testable hypotheses")
    experiment_designs: List[ExperimentDesign] = Field(description="Proposed experiment designs")
    validation: ValidationResult = Field(description="Validation audit findings from Research Judge")
    limitations_and_uncertainties: List[str] = Field(description="Explicit limitations and caveats")
    references: List[Dict[str, str]] = Field(description="Full bibliographic references with direct URLs")
    generated_at: str = Field(description="ISO timestamp of generation")
