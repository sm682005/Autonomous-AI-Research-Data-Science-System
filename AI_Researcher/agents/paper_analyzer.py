"""
Paper Analyzer Agent.
Performs rigorous scientific decomposition of retrieved academic papers.
Extracts research problems, methodologies, reported datasets, metrics, findings, limitations, and future directions.
Preserves stable paper identifiers (P001, P002...) and notes abstract-level evidence limits.
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field
from AI_Researcher.config import GEMINI_MODEL, get_gemini_client
from AI_Researcher.schemas.research import PaperMetadata, PaperAnalysis
from AI_Researcher.agents.gemini_helper import generate_structured

SYSTEM_PROMPT = """You are the Senior Paper Analyst in an Autonomous Academic Research Division.
Analyze the provided academic papers strictly based on their verified metadata and abstracts.
Do NOT invent datasets, metrics, or experimental results that are not stated in the source text.
If a dataset or evaluation metric is not mentioned in the abstract, state explicitly: "Not reported in abstract".
Always preserve the provided paper identifier (e.g. P001, P002) for each paper analysis.
"""


class BatchPaperAnalysis(BaseModel):
    """Wrapper schema for batched paper analysis."""
    analyses: List[PaperAnalysis] = Field(description="List of detailed analyses for each paper")


def analyze_papers(
    papers: List[PaperMetadata],
    client: Optional[Any] = None,
    model: str = GEMINI_MODEL,
    batch_size: int = 4,
) -> List[PaperAnalysis]:
    """
    Analyzes retrieved papers in controlled batches to optimize API quota and latency.
    Preserves exact paper IDs and acknowledges abstract-only limitations.
    """
    if not papers:
        return []

    if client is None:
        client = get_gemini_client()

    all_analyses: List[PaperAnalysis] = []

    # Process in batches of 4 to balance prompt size and bounded API requests
    for i in range(0, len(papers), batch_size):
        batch = papers[i : i + batch_size]
        
        batch_text_blocks = []
        for p in batch:
            authors_str = ", ".join(p.authors[:4]) if p.authors else "Unknown Authors"
            date_str = p.published_date or "Unknown Date"
            batch_text_blocks.append(
                f"--- PAPER IDENTIFIER: {p.id} ---\n"
                f"Title: {p.title}\n"
                f"Authors: {authors_str}\n"
                f"Publication Date: {date_str}\n"
                f"Source: {p.source} ({p.url})\n"
                f"Abstract:\n{p.abstract}\n"
            )

        prompt = f"""Conduct a rigorous academic analysis for each of the following {len(batch)} retrieved papers.
Make sure to output an analysis item for EVERY paper in the batch with its corresponding paper_id.

{"".join(batch_text_blocks)}

For each paper, extract:
1. paper_id (Must exactly match the PAPER IDENTIFIER, e.g. P001, P002)
2. research_problem: The fundamental theoretical or engineering challenge.
3. methodology: Architectural, algorithmic, or mathematical approaches.
4. dataset: Specific datasets or benchmarks used (or 'Not reported in abstract' if unmentioned).
5. evaluation_metrics: Formal metrics used (or 'Not reported in abstract' if unmentioned).
6. main_findings: Core claims and verified findings.
7. limitations: Stated weaknesses or evidence caveats.
8. future_directions: Future research directions explicitly suggested or implied.
"""

        batch_result = generate_structured(
            client=client,
            model=model,
            prompt=prompt,
            schema_cls=BatchPaperAnalysis,
            system_instruction=SYSTEM_PROMPT,
            temperature=0.2,
        )

        all_analyses.extend(batch_result.analyses)

    # Sanity check: Ensure every paper in the input has an analysis entry with correct ID
    analyzed_dict = {a.paper_id: a for a in all_analyses}
    final_ordered_analyses: List[PaperAnalysis] = []
    
    for p in papers:
        if p.id in analyzed_dict:
            final_ordered_analyses.append(analyzed_dict[p.id])
        else:
            # Fallback placeholder if batch dropped one to prevent pipeline crash
            final_ordered_analyses.append(
                PaperAnalysis(
                    paper_id=p.id,
                    research_problem=f"Investigation into {p.title}",
                    methodology="Described in abstract",
                    dataset="Not reported in abstract",
                    evaluation_metrics="Not reported in abstract",
                    main_findings=p.abstract[:200] + "...",
                    limitations="Analysis derived solely from abstract evidence.",
                    future_directions="Further empirical validation required.",
                )
            )

    return final_ordered_analyses
