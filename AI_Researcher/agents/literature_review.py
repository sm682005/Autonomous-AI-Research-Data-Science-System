"""
Literature Review Synthesizer Agent.
Performs cross-paper comparative synthesis rather than isolated summaries.
Compares methodologies, identifies agreements/disagreements, surfaces unresolved questions,
and supports factual claims strictly with paper identifiers [P001], [P002], etc.
"""

from typing import List, Optional, Any
from AI_Researcher.config import GEMINI_MODEL, get_gemini_client
from AI_Researcher.schemas.research import PaperMetadata, PaperAnalysis, LiteratureReview
from AI_Researcher.agents.gemini_helper import generate_structured

SYSTEM_PROMPT = """You are the Senior Literature Review Synthesizer in an Autonomous Academic Research Division.
Synthesize the analyzed academic literature into a coherent comparative analysis.
Do NOT just summarize papers one after another. You must compare and contrast their approaches, assumptions, and tradeoffs.
CRITICAL CITATION RULE: Whenever you state a finding, approach, or limitation from a paper, you MUST cite the exact paper identifier in brackets, e.g. [P001] or [P002, P003].
Do NOT cite any paper ID that is not provided in the paper list.
Explicitly acknowledge that findings are derived from abstract-level peer-reviewed records.
"""


def synthesize_literature_review(
    research_question: str,
    papers: List[PaperMetadata],
    analyses: List[PaperAnalysis],
    client: Optional[Any] = None,
    model: str = GEMINI_MODEL,
) -> LiteratureReview:
    """
    Produces a deeply comparative literature review supported by verified citations.
    """
    if client is None:
        client = get_gemini_client()

    analysis_map = {a.paper_id: a for a in analyses}

    dossier_lines = []
    for p in papers:
        analysis = analysis_map.get(p.id)
        dossier_lines.append(
            f"Paper [{p.id}]: \"{p.title}\" ({p.published_date or 'n.d.'})\n"
            f"  Authors: {', '.join(p.authors[:3])}\n"
            f"  Problem: {analysis.research_problem if analysis else 'See abstract'}\n"
            f"  Methodology: {analysis.methodology if analysis else 'See abstract'}\n"
            f"  Main Findings: {analysis.main_findings if analysis else p.abstract[:150]}\n"
            f"  Limitations: {analysis.limitations if analysis else 'Abstract only'}\n"
        )

    prompt = f"""Synthesize a rigorous comparative literature review for this research query:
Research Question: "{research_question}"

Available Verified Papers (Citations MUST only use these exact IDs):
{"".join(dossier_lines)}

Required outputs:
1. synthesis_narrative: An academic narrative synthesizing the state of research, citing papers with [Pxxx].
2. common_methodologies: 3-5 dominant methodological paradigms shared across works.
3. divergent_approaches: Key algorithmic or conceptual divergence points between distinct approaches.
4. agreements_and_disagreements: Areas of consensus vs disputed claims or conflicting findings.
5. evidence_limitations: Explicit caveats regarding benchmark coverage, scale, or abstract-only depth.
6. unresolved_questions: 3-5 open, unanswered scientific questions emerging from the comparative analysis.
"""

    return generate_structured(
        client=client,
        model=model,
        prompt=prompt,
        schema_cls=LiteratureReview,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,
    )
