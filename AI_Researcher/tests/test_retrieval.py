"""
Unit tests for academic paper retrieval tools.
Tests arXiv Atom XML parsing, title normalization, deduplication,
missing metadata resilience, and network failure tolerance.
"""

import xml.etree.ElementTree as ET
from unittest.mock import patch, MagicMock
import pytest
import requests

from AI_Researcher.tools.arxiv_search import (
    clean_text,
    normalize_title,
    parse_arxiv_entry,
    search_arxiv,
    ATOM_NS,
)
from AI_Researcher.tools.semantic_scholar import search_semantic_scholar


SAMPLE_ARXIV_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2301.00001v1</id>
    <published>2023-01-01T12:00:00Z</published>
    <title>  Sample Academic Paper on   Reinforcement Learning  </title>
    <summary>   This paper introduces a novel actor-critic formulation.
    Empirical results demonstrate convergence.   </summary>
    <author>
      <name>Alice Smith</name>
    </author>
    <author>
      <name>Bob Jones</name>
    </author>
    <link href="http://arxiv.org/pdf/2301.00001v1" title="pdf" type="application/pdf"/>
  </entry>
  <entry>
    <id>http://arxiv.org/abs/2301.00002v2</id>
    <published>2023-02-15T08:30:00Z</published>
    <title>SAMPLE ACADEMIC PAPER ON REINFORCEMENT LEARNING</title>
    <summary>Duplicate paper title testing deduplication logic.</summary>
    <author>
      <name>Alice Smith</name>
    </author>
  </entry>
</feed>
"""

SAMPLE_MISSING_METADATA_XML = f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <id>http://arxiv.org/abs/2402.12345v1</id>
    <title>Paper With Minimal Metadata</title>
  </entry>
</feed>
"""


def test_clean_text():
    """Tests whitespace and newline stripping."""
    raw = "   Line 1\n\n   Line 2   \t "
    assert clean_text(raw) == "Line 1 Line 2"
    assert clean_text(None) == ""


def test_normalize_title():
    """Tests title normalization for duplicate detection."""
    t1 = "Attention Is All You Need!"
    t2 = "attention is all you need"
    t3 = "Attention-Is-All-You-Need"
    assert normalize_title(t1) == normalize_title(t2)
    assert normalize_title(t2) == normalize_title(t3)


def test_parse_arxiv_entry():
    """Tests parsing a real Atom XML entry into PaperMetadata."""
    root = ET.fromstring(SAMPLE_ARXIV_XML)
    entry = root.find(f"{ATOM_NS}entry")
    assert entry is not None

    paper = parse_arxiv_entry(entry, 1)
    assert paper is not None
    assert paper.id == "P001"
    assert paper.title == "Sample Academic Paper on Reinforcement Learning"
    assert paper.authors == ["Alice Smith", "Bob Jones"]
    assert "actor-critic formulation" in paper.abstract
    assert paper.published_date == "2023-01-01T12:00:00Z"
    assert paper.paper_id == "2301.00001v1" or "2301.00001" in paper.paper_id
    assert paper.pdf_url == "http://arxiv.org/pdf/2301.00001v1"
    assert paper.abstract_only is True


def test_parse_missing_metadata():
    """Tests resilience when authors, summary, or links are absent."""
    root = ET.fromstring(SAMPLE_MISSING_METADATA_XML)
    entry = root.find(f"{ATOM_NS}entry")
    paper = parse_arxiv_entry(entry, 2)

    assert paper is not None
    assert paper.id == "P002"
    assert paper.title == "Paper With Minimal Metadata"
    assert paper.authors == []
    assert paper.abstract == ""
    assert paper.published_date is None


@patch("requests.get")
def test_search_arxiv_mocked(mock_get):
    """Tests search_arxiv with mocked network response and deduplication."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = SAMPLE_ARXIV_XML
    mock_get.return_value = mock_resp

    papers = search_arxiv(query="reinforcement learning", max_results=10)

    # Note: Second entry has identical normalized title, so deduplication should yield 1 paper
    assert len(papers) == 1
    assert papers[0].id == "P001"
    assert papers[0].title == "Sample Academic Paper on Reinforcement Learning"


@patch("requests.get")
def test_search_arxiv_network_failure(mock_get):
    """Tests graceful handling when arXiv API returns network errors."""
    mock_get.side_effect = requests.RequestException("Connection refused")

    papers = search_arxiv(query="quantum computing", max_results=5)
    # Must not raise unhandled exception, must return empty list without fabricating papers
    assert papers == []


@patch("requests.get")
def test_semantic_scholar_rate_limiting(mock_get):
    """Tests that Semantic Scholar 429 rate limit is safely caught without crashing."""
    mock_resp = MagicMock()
    mock_resp.status_code = 429
    mock_get.return_value = mock_resp

    papers = search_semantic_scholar(query="deep learning", max_results=5)
    assert papers == []
