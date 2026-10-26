"""
Research Judge Agent.
Combines deterministic structural checks (citation integrity, orphan links)
with a rigorous Gemini critique for scientific validity, feasibility, and claim calibration.
"""

from typing import List, Optional, Tuple, Any
from pydantic import BaseModel, Field
from AI_Researcher.config import GEMINI_MODEL, get_gemini_client
from AI_Researcher.schemas.research import (
    PaperMetadata,
    LiteratureReview,
    ResearchGap,
    Hypothesis,
    ExperimentDesign,
    ValidationResult,
)
from AI_Researcher.tools.citation_verifier import verify_citations, verify_gap_hypothesis_alignment
from AI_Researcher.agents.gemini_helper import generate_structured

SYSTEM_PROMPT = """You are the Senior Research Judge and Peer Review Director in an Academic Research System.
Evaluate the proposed literature review, research gaps, hypotheses, and experiment designs.
Scrutinize for:
1. Unsupported claims or overgeneralized assertions beyond the provided paper abstracts.
2. Conceptual alignment between gaps, hypotheses, and experiments.
3. Feasibility of proposed experiments and prevention of data leakage.
4. Correct epistemic labeling (predictions must NOT be phrased as completed measurements).
Be objective, rigorous, and constructive.
"""


class JudgeCritique(BaseModel):
    """Schema for Gemini-based peer review evaluation."""
    score: float = Field(ge=0.0, le=10.0, description="Quality & rigor score between 0.0 and 10.0")
    critique: str = Field(description="Detailed academic review detailing strengths and weaknesses")
    warnings: List[str] = Field(default_factory=list, description="Specific scientific weaknesses or missing controls")
    revision_recommended: bool = Field(description="True if methodological defects necessitate a revision pass")


def judge_research(
    research_question: str,
    papers: List[PaperMetadata],
    lit_review: LiteratureReview,
    gaps: List[ResearchGap],
    hypotheses: List[Hypothesis],
    experiments: List[ExperimentDesign],
    client: Optional[Any] = None,
    model: str = GEMINI_MODEL,
) -> ValidationResult:
    """
    Performs deterministic citation checks and an LLM peer-review audit.
    """
    all_warnings: List[str] = []

    # 1. Deterministic Citation and Alignment Verification
    text_blocks: List[Tuple[str, str]] = [
        ("Literature Review Narrative", lit_review.synthesis_narrative),
    ]
    for gap in gaps:
        text_blocks.append((f"Research Gap {gap.gap_id}", f"{gap.description} {gap.evidence_summary}"))
    for hyp in hypotheses:
        text_blocks.append((f"Hypothesis {hyp.hypothesis_id}", f"{hyp.statement} {hyp.supporting_evidence}"))
    for exp in experiments:
        text_blocks.append((f"Experiment {exp.experiment_id}", f"{exp.proposed_approach} {exp.expected_outcomes_predictions}"))

    citations_valid, invalid_citations, citation_warnings = verify_citations(papers, text_blocks)
    all_warnings.extend(citation_warnings)

    alignment_warnings = verify_gap_hypothesis_alignment(papers, gaps, hypotheses)
    all_warnings.extend(alignment_warnings)

    # Deterministic check on paper count
    if len(papers) == 0:
        all_warnings.append("Critical Warning: Zero academic papers retrieved. Findings lack empirical foundation.")

    # 2. LLM Peer-Review Evaluation
    if client is None:
        client = get_gemini_client()

    papers_brief = "\n".join(f"[{p.id}] {p.title}" for p in papers)
    gaps_brief = "\n".join(f"[{g.gap_id}] {g.description} (Cites: {g.supporting_paper_ids})" for g in gaps)
    hyp_brief = "\n".join(f"[{h.hypothesis_id}] {h.statement} (Addresses: {h.linked_gap_id})" for h in hypotheses)
    exp_brief = "\n".join(f"[{e.experiment_id}] Objective: {e.research_objective} | Baselines: {e.baseline_methods}" for e in experiments)

    prompt = f"""Conduct a formal peer-review audit of this autonomous research workflow:

Research Question: "{research_question}"

Available Papers:
{papers_brief}

Literature Review Summary:
{lit_review.synthesis_narrative[:600]}...

Identified Gaps:
{gaps_brief}

Formulated Hypotheses:
{hyp_brief}

Experiment Designs:
{exp_brief}

Evaluate:
1. Are claims supported by the literature?
2. Are hypotheses testable and falsifiable?
3. Are the experiment designs methodologically sound with proper controls?
4. Are predicted outcomes clearly delineated from measured reality?
Provide a score (0.0 to 10.0), a constructive critique, any specific warnings, and whether a revision is recommended.
"""

    llm_critique = generate_structured(
        client=client,
        model=model,
        prompt=prompt,
        schema_cls=JudgeCritique,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1,
    )

    all_warnings.extend(llm_critique.warnings)

    # Deduplicate warnings
    unique_warnings = list(dict.fromkeys(all_warnings))

    # A revision is needed if deterministic checks failed (e.g. invalid citations) or judge explicitly recommends it
    revision_needed = (not citations_valid) or llm_critique.revision_recommended or (len(invalid_citations) > 0)
    is_valid = citations_valid and (llm_critique.score >= 5.0) and (len(invalid_citations) == 0)

    return ValidationResult(
        is_valid=is_valid,
        score=llm_critique.score,
        warnings=unique_warnings,
        critique=llm_critique.critique,
        revision_needed=revision_needed,
        unverified_citations=invalid_citations,
    )
