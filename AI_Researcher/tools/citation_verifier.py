"""
Citation Verifier Tool.
Deterministic verification of paper identifiers (P001, P002...), orphan detection,
and scientific integrity checks across generated literature, gaps, and hypotheses.
"""

import re
from typing import List, Dict, Set, Tuple
from AI_Researcher.schemas.research import PaperMetadata, ResearchGap, Hypothesis


def extract_citation_ids(text: str) -> List[str]:
    """Finds all paper reference identifiers in the format P001, P002, etc."""
    if not text:
        return []
    matches = re.findall(r"\b(P\d{3,4})\b", text)
    # Deduplicate while preserving occurrence order
    seen = set()
    ordered = []
    for m in matches:
        if m not in seen:
            seen.add(m)
            ordered.append(m)
    return ordered


def verify_citations(
    papers: List[PaperMetadata],
    text_blocks: List[Tuple[str, str]],  # List of (context_name, text)
) -> Tuple[bool, List[str], List[str]]:
    """
    Checks that every referenced paper ID exists in the retrieved paper records.
    Returns:
        (is_valid, invalid_ids, warning_messages)
    """
    valid_ids: Set[str] = {p.id for p in papers}
    invalid_ids: Set[str] = set()
    warnings: List[str] = []

    for context_name, text in text_blocks:
        found_ids = extract_citation_ids(text)
        for cid in found_ids:
            if cid not in valid_ids:
                invalid_ids.add(cid)
                warnings.append(
                    f"Invalid Citation in [{context_name}]: Paper identifier '{cid}' was cited but does not exist in retrieved papers ({sorted(list(valid_ids))})."
                )

    is_valid = len(invalid_ids) == 0
    return is_valid, sorted(list(invalid_ids)), warnings


def verify_gap_hypothesis_alignment(
    papers: List[PaperMetadata],
    gaps: List[ResearchGap],
    hypotheses: List[Hypothesis],
) -> List[str]:
    """
    Validates the structural alignment between retrieved papers, research gaps, and hypotheses.
    """
    warnings: List[str] = []
    valid_paper_ids = {p.id for p in papers}
    valid_gap_ids = {g.gap_id for g in gaps}

    # Verify gaps cite valid papers
    for gap in gaps:
        if not gap.supporting_paper_ids:
            warnings.append(f"Research Gap [{gap.gap_id}] has no supporting paper citations.")
        else:
            for pid in gap.supporting_paper_ids:
                if pid not in valid_paper_ids:
                    warnings.append(f"Research Gap [{gap.gap_id}] references nonexistent paper ID: '{pid}'.")

    # Verify hypotheses link to valid gaps
    for hyp in hypotheses:
        if not hyp.linked_gap_id:
            warnings.append(f"Hypothesis [{hyp.hypothesis_id}] is orphan (has no linked research gap).")
        elif hyp.linked_gap_id not in valid_gap_ids:
            warnings.append(
                f"Hypothesis [{hyp.hypothesis_id}] links to unknown gap ID: '{hyp.linked_gap_id}'."
            )

    return warnings
