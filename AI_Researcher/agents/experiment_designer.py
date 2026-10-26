"""
Experiment Designer Agent.
Transforms validated scientific hypotheses into reproducible, rigorous experimental protocols.
Explicitly designs baseline comparisons, data leakage prevention, confounding factor controls,
and clearly marks all anticipated results as predictions (NOT executed measurements).
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field
from AI_Researcher.config import GEMINI_MODEL, get_gemini_client
from AI_Researcher.schemas.research import Hypothesis, ExperimentDesign
from AI_Researcher.agents.gemini_helper import generate_structured

SYSTEM_PROMPT = """You are the Senior Experiment Designer in an Autonomous Academic Research Division.
Design concrete, reproducible, and methodologically sound experiments to test each proposed hypothesis.
CRITICAL INTEGRITY RULE: Never claim an experiment was executed or that benchmark numbers were achieved.
All anticipated outcomes must be explicitly labeled as theoretical predictions.
Emphasize data leakage prevention, confounding variables, and baseline comparisons.
"""


class BatchExperimentDesigns(BaseModel):
    """Wrapper schema for experiment designs."""
    experiment_designs: List[ExperimentDesign] = Field(description="List of detailed experiment specifications")


def design_experiments(
    hypotheses: List[Hypothesis],
    client: Optional[Any] = None,
    model: str = GEMINI_MODEL,
) -> List[ExperimentDesign]:
    """
    Formulates a comprehensive experimental protocol for each scientific hypothesis.
    """
    if not hypotheses:
        return []

    if client is None:
        client = get_gemini_client()

    hypotheses_text = []
    for h in hypotheses:
        hypotheses_text.append(
            f"--- HYPOTHESIS: {h.hypothesis_id} (Addressing {h.linked_gap_id}) ---\n"
            f"Statement: {h.statement}\n"
            f"Rationale: {h.supporting_evidence}\n"
            f"Variables: {', '.join(h.variables_to_investigate)}\n"
            f"Testing Protocol: {h.testability_method}\n"
            f"Uncertainties: {h.known_uncertainties}\n"
        )

    prompt = f"""Design a rigorous, reproducible scientific experiment for each of the following hypotheses:

{"".join(hypotheses_text)}

For each hypothesis:
1. experiment_id (e.g. EXP-01, matching HYP-01)
2. linked_hypothesis_id (e.g. HYP-01)
3. research_objective: Specific empirical question and hypothesis falsification criteria.
4. required_dataset_characteristics: Dataset size, sampling distribution, split strategy (e.g. temporal vs stratified).
5. baseline_methods: 2-3 standard or SOTA baselines for empirical benchmarking.
6. proposed_approach: Concrete architectural, algorithmic, or experimental intervention.
7. experimental_steps: Step-by-step numbered protocol for exact reproducibility.
8. evaluation_metrics: Formal quantitative metrics with statistical significance tests (e.g. p-values, bootstrap CIs).
9. data_leakage_prevention: Specific precautions against feature snooping, target leakage, or test set contamination.
10. confounding_factors: Potential hidden confounders and how they are controlled or isolated.
11. expected_outcomes_predictions: MUST be explicitly described as PREDICTIONS (e.g., 'Predicted outcome: ...').
12. limitations_and_reproducibility: Hardware requirements, random seeds, and reproducibility constraints.
"""

    result = generate_structured(
        client=client,
        model=model,
        prompt=prompt,
        schema_cls=BatchExperimentDesigns,
        system_instruction=SYSTEM_PROMPT,
        temperature=0.2,
    )

    return result.experiment_designs
