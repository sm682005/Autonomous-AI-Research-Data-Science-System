"""
Semantic Scholar Academic Retrieval Tool.
Provides secondary academic paper search for computer science, AI, and interdisciplinary fields.
Designed to supplement arXiv results gracefully with rate-limit and error tolerance.
"""

import time
from typing import List, Optional, Tuple
import requests

from AI_Researcher.config import SEMANTIC_SCHOLAR_URL, REQUEST_TIMEOUT, MAX_RETRIES
from AI_Researcher.schemas.research import PaperMetadata
from AI_Researcher.tools.arxiv_search import clean_text, normalize_title


def search_semantic_scholar(
    query: str,
    max_results: int = 5,
    start_index: int = 1,
    date_range: Optional[Tuple[int, int]] = None,
    timeout: int = REQUEST_TIMEOUT,
) -> List[PaperMetadata]:
    """
    Queries the public Semantic Scholar Graph API for academic publications.
    Safely catches 429 (rate limits) and returns empty list without raising fatal errors.
    """
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    params = {
        "query": cleaned_query,
        "limit": min(max_results * 2, 20),
        "fields": "paperId,title,abstract,authors,year,url,openAccessPdf",
    }

    headers = {
        "User-Agent": "Autonomous-AI-Researcher-Agent/1.0"
    }

    papers: List[PaperMetadata] = []
    seen_titles = set()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(SEMANTIC_SCHOLAR_URL, params=params, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("data", [])
                
                counter = start_index
                for item in items:
                    title = clean_text(item.get("title"))
                    if not title:
                        continue
                    
                    norm_t = normalize_title(title)
                    if norm_t in seen_titles:
                        continue
                    seen_titles.add(norm_t)

                    year = item.get("year")
                    if date_range and year:
                        start_yr, end_yr = date_range
                        if not (start_yr <= int(year) <= end_yr):
                            continue

                    abstract = clean_text(item.get("abstract")) or "Abstract not provided by repository index."
                    authors_list = [a.get("name") for a in item.get("authors", []) if a.get("name")]
                    paper_id = item.get("paperId", "")
                    url = item.get("url") or f"https://www.semanticscholar.org/paper/{paper_id}"
                    pdf_info = item.get("openAccessPdf") or {}
                    pdf_url = pdf_info.get("url")

                    papers.append(
                        PaperMetadata(
                            id=f"P{counter:03d}",
                            title=title,
                            authors=authors_list,
                            abstract=abstract,
                            published_date=str(year) if year else None,
                            source="Semantic Scholar",
                            paper_id=paper_id,
                            url=url,
                            pdf_url=pdf_url,
                            abstract_only=True,
                        )
                    )
                    counter += 1
                    if len(papers) >= max_results:
                        break
                return papers
            elif resp.status_code == 429:
                # Rate limited on public Semantic Scholar endpoint
                time.sleep(attempt * 1.5)
            else:
                break
        except requests.RequestException:
            if attempt < MAX_RETRIES:
                time.sleep(attempt * 1.0)
            else:
                break

    return papers
