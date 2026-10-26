# Autonomous AI Researcher (Research Division)
> **Autonomous AI Research & Data Science System — Terminal Academic Division**  
> Powered by Google Gemini (Official `google-genai` SDK) & LangGraph Workflow Orchestration.

---

## 🔬 Overview & Scientific Architecture

The **Autonomous AI Researcher** is an agentic command-line system designed to automate end-to-end academic research without hallucination or fabrication:

```
Research Query
      │
      ▼
[1. Research Planner] ────────► Formalize Objective, Constraints, & Targeted Academic Queries
      │
      ▼
[2. Paper Retrieval]  ────────► Live arXiv API (Atom XML) & Semantic Scholar Graph API
      │                          └─► Deduplication, stable identifiers [P001, P002...], abstract boundary
      ▼
[3. Paper Analyzer]   ────────► Decompose Problem, Methodology, Datasets, Metrics, Findings, Limitations
      │
      ▼
[4. Literature Review] ───────► Comparative Cross-Paper Synthesis with Strict Bracketed Citations [Pxxx]
      │
      ▼
[5. Gap & Hypothesis] ────────► Detect Provisional Research Gaps & Formulate Falsifiable Hypotheses
      │
      ▼
[6. Experiment Design] ───────► Methodological Protocols, Baseline Methods, Controls, Predicted Outcomes
      │
      ▼
[7. Research Judge]   ────────► Deterministic Citation Checks & Gemini Peer Review Critique
      │                          └─► Bounded Revision Loop if Deficiencies / Orphan Links Detected
      ▼
[8. Report Generator] ────────► Local Persistence as both Academic Markdown (.md) and JSON (.json)
```

---

## 🛠 Tech Stack

- **Python**: 3.10 / 3.11+
- **Gemini SDK**: Official `google-genai` SDK (`gemini-3-flash-preview`, `gemini-3.8-flash`, etc.)
- **Orchestration**: `langgraph` StateGraph with typed dictionary state & conditional branching
- **Data Validation**: `pydantic` v2 (schemas for papers, analyses, reviews, gaps, hypotheses, experiments)
- **Academic Retrieval**: Official `arXiv` API (Atom XML parsing via `xml.etree.ElementTree`) + `Semantic Scholar`
- **Citation Verifier**: Regex citation extraction, orphan hypothesis detection, ungrounded ID rejection
- **Terminal UX**: Native interactive CLI with clean `rich` formatting
- **Testing**: `pytest` test suite with 100% mocked offline tests (no paid calls required)

---

## 🚀 Quickstart & Setup (Windows, Linux, macOS)

### 1. Create a Virtual Environment

On Windows (PowerShell):
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

On Linux / macOS (Bash):
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure API Credentials

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
*(On Windows PowerShell: `Copy-Item .env.example .env`)*

Open `.env` and set your Google Gemini API key obtained from [Google AI Studio](https://aistudio.google.com/app/apikey):
```ini
GEMINI_API_KEY="AIzaSy..."
GEMINI_MODEL="gemini-3-flash-preview"
DEFAULT_PAPER_COUNT=8
MAX_REVISIONS=1
REQUEST_TIMEOUT=15
```

---

## 💻 Running the Terminal Application

Run the application directly from your IDE terminal (VS Code, PyCharm, or Windows Terminal):

```bash
python main.py
```

### Interactive Menu

```text
============================================================
                  AUTONOMOUS AI RESEARCHER                  
          Research Division | Powered by Google Gemini       
============================================================

Menu:
  1. Start new research
  2. View previous research reports
  3. Open a previous report
  4. View configuration status
  5. Exit
```

- **Option 1: Start new research**  
  Prompts for research topic, number of papers (e.g. 8), optional publication date filter (e.g. `2022-2025`), and detail level (`detailed` / `concise`). Displays the multi-agent stages live, outputs discovered papers with URLs, and compiles the final report.
- **Option 2: View previous research reports**  
  Displays an overview table of archived research dossiers in `reports/` with folder name, topic, paper count, and peer-review rigor score.
- **Option 3: Open a previous report**  
  Select a previous dossier to inspect its complete synthesized Markdown paper directly in the terminal.
- **Option 4: View configuration status**  
  Checks API key status (masked), selected Gemini model, operational thresholds, and active repositories.
- **Option 5: Exit**  
  Terminates session cleanly.

---

## 🧪 Automated Testing

Execute the comprehensive unit and integration test suite:

```bash
python -m pytest -q
```

All unit tests execute completely offline without making external paid API calls:
- `test_schemas.py`: Pydantic model validation, invalid score rejection, JSON serialization/deserialization.
- `test_retrieval.py`: arXiv XML parsing, title normalization, deduplication, missing metadata handling, network error recovery.
- `test_citations.py`: Regex paper ID extraction, orphan citation detection, ungrounded claim warnings.
- `test_workflow.py`: LangGraph state machine routing, conditional branching (no papers, validation failure, revision limits, mock report generation).

---

## 📁 Project Structure

```
AI_Researcher/
├── main.py                  # Terminal interactive CLI application & menu loop
├── requirements.txt         # Core lightweight dependencies
├── .env.example             # Template for API credentials and model configurations
├── .gitignore               # Ignores .venv, .env, and caches
├── README.md                # Full academic module documentation
├── config.py                # Environment configuration & Gemini client initialization
├── agents/                  # Multi-agent cognitive modules
│   ├── __init__.py
│   ├── planner.py           # Formulates research objective & targeted search queries
│   ├── paper_analyzer.py    # Decomposes problem, method, dataset, metrics, findings
│   ├── literature_review.py # Synthesizes comparative review with [Pxxx] citations
│   ├── gap_hypothesis.py    # Detects provisional gaps & formulates falsifiable hypotheses
│   ├── experiment_designer.py # Designs reproducible protocols with controls & predictions
│   ├── research_judge.py    # Combines deterministic checks & peer-review audit
│   └── gemini_helper.py     # Fault-tolerant structured generation with retries
├── tools/                   # Academic retrieval & verification tools
│   ├── __init__.py
│   ├── arxiv_search.py      # Real arXiv API client with Atom XML parsing & deduplication
│   ├── semantic_scholar.py  # Secondary Semantic Scholar graph query tool
│   └── citation_verifier.py # Deterministic citation validation & orphan detection
├── graph/                   # Workflow orchestration
│   ├── __init__.py
│   ├── state.py             # Strongly typed ResearchState dictionary
│   └── workflow.py          # StateGraph compilation, nodes, & conditional edges
├── services/                # Storage and formatting
│   ├── __init__.py
│   └── report_service.py    # Markdown/JSON serialization & report browsing
├── schemas/                 # Pydantic data models
│   ├── __init__.py
│   └── research.py          # PaperMetadata, ResearchPlan, FinalReport, etc.
├── reports/                 # Output directory for saved research dossiers
│   └── .gitkeep
└── tests/                   # Automated pytest test suite
    ├── __init__.py
    ├── test_schemas.py
    ├── test_retrieval.py
    ├── test_citations.py
    └── test_workflow.py
```

---

## 📑 Output Artifacts

Each research run saves into an isolated subfolder under `reports/YYYYMMDD_HHMMSS_<sanitized_topic>/`:
1. `report.md`: Complete academic research paper ready for presentation, formatted in clean Markdown.
2. `report.json`: Machine-readable structured database containing raw metadata, analyses, gaps, hypotheses, experimental steps, and peer review scores.

---

## ⚖️ Academic Integrity & Reliability Rules

- **Zero Fabrication**: Academic papers are retrieved from live APIs; if search parameters yield no papers, a limitation report is produced instead of inventing mock papers.
- **Stable References**: Retain identifiers like `[P001]`, `[P002]`, linked to direct source URLs and PDF links.
- **Abstract Boundary**: Since open APIs supply abstracts, conclusions are explicitly marked as grounded in abstract-level peer-reviewed records.
- **Epistemic Calibration**: Research gaps are designated *provisional*; anticipated experimental results are strictly described as *predictions*.
