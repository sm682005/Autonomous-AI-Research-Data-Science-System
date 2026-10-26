"""
Research Gap Detector and Hypothesis Generator Agent.
Derives candidate research gaps from synthesized literature evidence,
and formulates rigorous, testable hypotheses linked directly to those gaps.
Labels gaps as provisional to avoid claiming unverified absolute novelty.
"""

from typing import List, Tuple, Optional, Any
from pydantic import BaseModel, Field
from AI_Researcher.config import GEMINI_MODEL, get_gemini_client
from AI_Researcher.schemas.research import PaperMetadata, LiteratureReview, ResearchGap, Hypothesis
from AI_Researcher.agents.gemini_helper import generate_structured

SYSTEM_PROMPT = """You are the Senior Research Gap & Hypothesis Specialist in an Autonomous Academic Research Division.
Identify genuine, actionable candidate research gaps from the provided literature review and paper records.
Label candidate research gaps as provisional, acknowledging that retrieval is limited to sample academic indexes.
For each candidate gap, formulate a testable scientific hypothesis with explicit independent/dependent variables.
Ensure every hypothesis has a valid 'linked_gap_id' matching one of your generated gaps (e.g. GAP-01).
Ensure every research gap cites genuine supporting paper IDs from the retrieved paper list (e.g. ['P001']).
"""


class GapsAndHypotheses(BaseModel):
    """Container schema for research gaps and linked hypotheses."""
    research_gaps: List[ResearchGap] = Field(description="List of candidate research gaps identified")
    hypotheses: List[Hypothesis] = Field(description="List of testable scientific hypotheses linked to gaps")


def detect_gaps_and_hypotheses(
    research_question: str,
    papers: List[PaperMetadata],
    lit_review: LiteratureReview,
    client: Optional[Any] = None,
    model: str = GEMINI_MODEL,
) -> Tuple[List[ResearchGap], List[Hypothesis]]:
    """
    Identifies candidate research gaps and generates linked testable hypotheses.
    """
    if client is None:
        client = get_gemini_client()

    paper_summaries = []
    for p in papers:
        paper_summaries.append(f"[{p.id}] {p.title} - {p.abstract[:200]}...")

    prompt = f"""Based on the synthesized literature and paper collection for:
Research Question: "{research_question}"

Retrieved Verified Papers:
{"".join(paper_summaries)}

Key Unresolved Questions from Synthesis:
{chr(10).join(f"- {q}" for q in lit_review.unresolved_questions)}

Synthesized Evidence Limitations:
{chr(10).join(f"- {l}" for l in lit_review.evidence_limitations)}

Task:
1. Identify 2 to 4 Candidate Research Gaps (ID format: GAP-01, GAP-02...).
   - Each gap MUST cite the specific supporting paper IDs (e.g. ['P001', 'P002']).
   - Detail any counterevidence or partial solutions if found.
   - Explain why resolving the gap matters scientifically.
   - Set confidence_level ('High', 'Medium', or 'Low') and denote as provisional.
   - State what additional research is needed to verify the gap.

2. For each gap, formulate 1 or 2 Testable Scientific Hypotheses (ID format: HYP-01, HYP-02...).
   - Set 'linked_gap_id' to the exact corresponding gap (e.g. 'GAP-01').
   - Provide a formal falsifiable hypothesis statement.
   - Detail independent, dependent, and control variables.
   - Detail how the hypothesis could be empirically tested.
   - State known uncertainties and failure risks.
"""

    result = generate_structured(
        client=client,
        model=model,
        prompt=prompt,
        schema_cls=GapsAndHypotheses,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,
    )

    return result.research_gaps, result.hypotheses
