"""
Research Planner Agent.
Formalizes user research questions into an academic research objective,
targeted search queries for arXiv/academic search, subquestions, scope boundaries, and an analysis plan.
"""

from typing import Optional, Tuple, Any
from AI_Researcher.config import GEMINI_MODEL, get_gemini_client
from AI_Researcher.schemas.research import ResearchPlan
from AI_Researcher.agents.gemini_helper import generate_structured

SYSTEM_PROMPT = """You are the Senior Research Planner in an Autonomous Academic Research Division.
Your goal is to translate a research question into a rigorous academic research plan.
You must formulate high-precision search queries optimized for academic paper repositories like arXiv and Semantic Scholar.
Avoid generic conversational words; focus on key technical nouns, algorithmic names, and domain terminology.
"""


def plan_research(
    research_question: str,
    paper_count: int = 8,
    date_range: Optional[Tuple[int, int]] = None,
    detail_level: str = "detailed",
    client: Optional[Any] = None,
    model: str = GEMINI_MODEL,
) -> ResearchPlan:
    """
    Formulates a structured scientific research plan from the user's research topic.
    """
    if client is None:
        client = get_gemini_client()

    date_clause = f"Target publication date range: {date_range[0]} to {date_range[1]}." if date_range else "Publication date: All relevant years."

    prompt = f"""Generate a structured academic research plan for the following topic:

Topic / Question: "{research_question}"
Target Paper Count: {paper_count}
{date_clause}
Report Detail Level: {detail_level}

Requirements:
1. Formalize a concise and ambitious scientific Research Objective.
2. Provide 3-5 distinct, targeted search queries designed for academic search engines (e.g. arXiv).
3. Identify 3-5 critical scientific subquestions that current literature must answer.
4. Establish concrete scope boundaries and methodological constraints.
5. Provide a step-by-step analysis plan for evaluating comparative papers.
"""

    return generate_structured(
        client=client,
        model=model,
        prompt=prompt,
        schema_cls=ResearchPlan,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,
    )
