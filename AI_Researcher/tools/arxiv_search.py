"""
arXiv Search Tool.
Retrieves authentic academic papers from the official arXiv API via Atom XML feed.
Extracts clean metadata, deduplicates, and assigns stable paper IDs (P001, P002...).
"""

import re
import time
import urllib.parse
import xml.etree.ElementTree as ET
from typing import List, Optional, Tuple
import requests

from AI_Researcher.config import ARXIV_API_URL, REQUEST_TIMEOUT, MAX_RETRIES
from AI_Researcher.schemas.research import PaperMetadata

# Standard XML namespaces for arXiv API
ATOM_NS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"


def clean_text(text: Optional[str]) -> str:
    """Removes irregular newlines, excessive whitespace, and XML artifacts."""
    if not text:
        return ""
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned


def normalize_title(title: str) -> str:
    """Normalizes paper title for reliable deduplication."""
    return re.sub(r"[^a-zA-Z0-9]", "", title.lower())


def parse_arxiv_entry(entry: ET.Element, index: int) -> Optional[PaperMetadata]:
    """Parses a single Atom XML <entry> element into a PaperMetadata model."""
    title_el = entry.find(f"{ATOM_NS}title")
    title = clean_text(title_el.text) if title_el is not None else ""
    if not title:
        return None

    summary_el = entry.find(f"{ATOM_NS}summary")
    abstract = clean_text(summary_el.text) if summary_el is not None else ""

    id_el = entry.find(f"{ATOM_NS}id")
    raw_id = id_el.text.strip() if id_el is not None and id_el.text else ""
    
    # Extract clean arXiv identifier (e.g., 2305.18290v1 -> 2305.18290)
    arxiv_id_match = re.search(r"arxiv\.org/abs/([0-9]+\.[0-9]+|[\w\-]+/[0-9]+)", raw_id)
    arxiv_id = arxiv_id_match.group(1) if arxiv_id_match else raw_id.split("/")[-1]

    # Authors
    authors: List[str] = []
    for author_el in entry.findall(f"{ATOM_NS}author"):
        name_el = author_el.find(f"{ATOM_NS}name")
        if name_el is not None and name_el.text:
            cleaned_name = clean_text(name_el.text)
            if cleaned_name:
                authors.append(cleaned_name)

    # Published date
    published_el = entry.find(f"{ATOM_NS}published")
    published_date = published_el.text.strip() if published_el is not None and published_el.text else None

    # URLs
    landing_url = f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else raw_id
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf" if arxiv_id else None

    # Check links for explicit pdf link
    for link_el in entry.findall(f"{ATOM_NS}link"):
        if link_el.attrib.get("title") == "pdf" or link_el.attrib.get("type") == "application/pdf":
            href = link_el.attrib.get("href")
            if href:
                pdf_url = href

    paper_stable_id = f"P{index:03d}"

    return PaperMetadata(
        id=paper_stable_id,
        title=title,
        authors=authors,
        abstract=abstract,
        published_date=published_date,
        source="arXiv",
        paper_id=arxiv_id,
        url=landing_url,
        pdf_url=pdf_url,
        abstract_only=True,
    )


def search_arxiv(
    query: str,
    max_results: int = 8,
    date_range: Optional[Tuple[int, int]] = None,
    timeout: int = REQUEST_TIMEOUT,
) -> List[PaperMetadata]:
    """
    Executes real academic retrieval against the official arXiv API.
    Handles bounded retries, network errors, and deduplication.
    """
    # Sanitize and format search query
    cleaned_query = query.strip()
    if not cleaned_query:
        return []

    # Encode query for arXiv API
    encoded_query = urllib.parse.quote(cleaned_query)
    # Request extra results to allow for deduplication & date filtering
    request_limit = min(max_results * 2, 40)
    url = f"{ARXIV_API_URL}?search_query=all:{encoded_query}&start=0&max_results={request_limit}&sortBy=relevance&sortOrder=descending"

    headers = {
        "User-Agent": "Autonomous-AI-Researcher-Agent/1.0 (academic-research-automation; mailto:researcher@local.project)"
    }

    last_error: Optional[Exception] = None
    response_text = ""

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            if resp.status_code == 200:
                response_text = resp.text
                break
            elif resp.status_code == 503 or resp.status_code == 429:
                time.sleep(attempt * 1.5)
            else:
                resp.raise_for_status()
        except requests.RequestException as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(attempt * 1.2)
            else:
                break

    if not response_text:
        if last_error:
            # Propagate or log rather than fabricating data
            print(f"[Warning] arXiv search request failed: {last_error}")
        return []

    try:
        root = ET.fromstring(response_text)
    except ET.ParseError as pe:
        print(f"[Warning] Failed to parse arXiv XML response: {pe}")
        return []

    entries = root.findall(f"{ATOM_NS}entry")
    papers: List[PaperMetadata] = []
    seen_titles = set()

    paper_counter = 1
    for entry in entries:
        parsed = parse_arxiv_entry(entry, paper_counter)
        if not parsed:
            continue

        norm_title = normalize_title(parsed.title)
        if norm_title in seen_titles:
            continue
        seen_titles.add(norm_title)

        # Date range filtering if requested
        if date_range and parsed.published_date:
            try:
                pub_year = int(parsed.published_date[:4])
                start_yr, end_yr = date_range
                if not (start_yr <= pub_year <= end_yr):
                    continue
            except (ValueError, IndexError):
                pass

        papers.append(parsed)
        paper_counter += 1

        if len(papers) >= max_results:
            break

    return papers
