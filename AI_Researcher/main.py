"""
Autonomous AI Researcher - Terminal Command-Line Application.
Research Division | Powered by Google Gemini & LangGraph
"""

import os
import sys
from pathlib import Path
from typing import Optional, Tuple

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_ROOT.parent
for p in [str(PROJECT_ROOT), str(REPO_ROOT)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from AI_Researcher.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    DEFAULT_PAPER_COUNT,
    MAX_REVISIONS,
    get_config_status,
)
from AI_Researcher.graph.workflow import build_research_graph
from AI_Researcher.services.report_service import (
    list_saved_reports,
    load_report_by_folder,
    render_markdown_report,
)

# Optional rich formatting for enhanced terminal aesthetics
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    rich_available = True
    console = Console()
except ImportError:
    rich_available = False
    console = None


def print_banner():
    """Prints the official system banner."""
    title = (
        "============================================================\n"
        "                  AUTONOMOUS AI RESEARCHER                  \n"
        "          Research Division | Powered by Google Gemini       \n"
        "============================================================"
    )
    if rich_available and console:
        console.print(
            Panel(
                "[bold cyan]AUTONOMOUS AI RESEARCHER[/bold cyan]\n"
                "[dim]Research Division | Multi-Agent Academic Pipeline Powered by Google Gemini & LangGraph[/dim]",
                border_style="cyan",
            )
        )
    else:
        print(title)


def print_menu():
    """Displays the main terminal menu."""
    print("\nMenu:")
    print("  1. Start new research")
    print("  2. View previous research reports")
    print("  3. Open a previous report")
    print("  4. View configuration status")
    print("  5. Exit")


def check_api_key_or_warn() -> bool:
    """Verifies GEMINI_API_KEY is present before initiating research."""
    key = os.getenv("GEMINI_API_KEY", GEMINI_API_KEY).strip()
    if not key or key == "MY_GEMINI_API_KEY":
        msg = (
            "\n[ERROR] GEMINI_API_KEY is missing or unconfigured.\n"
            "To use the Autonomous AI Researcher:\n"
            "  1. Obtain a free key from Google AI Studio: https://aistudio.google.com/app/apikey\n"
            "  2. Add it to AI_Researcher/.env (e.g. GEMINI_API_KEY=\"AIza...\")\n"
            "     or run: export GEMINI_API_KEY=\"your_key_here\"\n"
        )
        if rich_available and console:
            console.print(f"[bold red]{msg}[/bold red]")
        else:
            print(msg)
        return False
    return True


def start_new_research():
    """Guides the user through initiating an autonomous research run."""
    if not check_api_key_or_warn():
        return

    print("\n--- Start New Academic Research Run ---")
    topic = input("Enter research topic or question: ").strip()
    if not topic:
        print("Research topic cannot be empty. Returning to menu.")
        return

    # Paper count prompt
    count_str = input(f"Number of academic papers to retrieve [{DEFAULT_PAPER_COUNT}]: ").strip()
    try:
        paper_count = int(count_str) if count_str else DEFAULT_PAPER_COUNT
        paper_count = max(2, min(paper_count, 20))
    except ValueError:
        print(f"Invalid number. Defaulting to {DEFAULT_PAPER_COUNT}.")
        paper_count = DEFAULT_PAPER_COUNT

    # Date range prompt
    date_str = input("Publication year filter (e.g., '2020-2025' or press Enter for All): ").strip()
    date_range: Optional[Tuple[int, int]] = None
    if date_str and "-" in date_str:
        try:
            parts = date_str.split("-")
            date_range = (int(parts[0].strip()), int(parts[1].strip()))
        except Exception:
            print("Could not parse date range. Searching across all years.")

    # Detail level prompt
    detail_choice = input("Report detail level ('detailed' or 'concise') [detailed]: ").strip().lower()
    detail_level = "concise" if detail_choice == "concise" else "detailed"

    print("\nInitializing LangGraph autonomous research workflow...")
    app = build_research_graph()

    initial_state = {
        "research_question": topic,
        "target_paper_count": paper_count,
        "date_range": date_range,
        "detail_level": detail_level,
        "revision_count": 0,
        "max_revisions": MAX_REVISIONS,
        "warnings": [],
        "retrieved_papers": [],
        "paper_analyses": [],
        "research_gaps": [],
        "hypotheses": [],
        "experiment_designs": [],
        "status": "IN_PROGRESS",
    }

    print(f"\n[Executing] Topic: '{topic}' | Target Papers: {paper_count} | Model: {GEMINI_MODEL}")
    print("-" * 65)

    last_stage = ""
    final_state = {}

    try:
        # Stream the nodes as they complete execution
        for event in app.stream(initial_state):
            for node_name, node_output in event.items():
                stage = node_output.get("current_stage", node_name)
                if stage != last_stage:
                    print(f"\n▶ [{node_name.upper()}] {stage}")
                    last_stage = stage

                # Print intermediate paper discoveries
                if "retrieved_papers" in node_output and node_output["retrieved_papers"]:
                    papers = node_output["retrieved_papers"]
                    print(f"  ✓ Retrieved and verified {len(papers)} authentic academic papers:")
                    for p in papers:
                        auth_preview = ", ".join(p.authors[:2]) + (" et al." if len(p.authors) > 2 else "")
                        print(f"    • [{p.id}] {p.title} ({p.published_date or 'n.d.'})")
                        print(f"      Source: {p.source} | URL: {p.url}")

                if "research_gaps" in node_output and node_output["research_gaps"]:
                    gaps = node_output["research_gaps"]
                    print(f"  ✓ Identified {len(gaps)} candidate research gaps:")
                    for g in gaps:
                        print(f"    • [{g.gap_id}] {g.description[:90]}... (Cites: {g.supporting_paper_ids})")

                if "hypotheses" in node_output and node_output["hypotheses"]:
                    hyps = node_output["hypotheses"]
                    print(f"  ✓ Formulated {len(hyps)} testable hypotheses:")
                    for h in hyps:
                        print(f"    • [{h.hypothesis_id}] {h.statement[:90]}...")

                if "experiment_designs" in node_output and node_output["experiment_designs"]:
                    exps = node_output["experiment_designs"]
                    print(f"  ✓ Formulated {len(exps)} experimental validation protocols:")
                    for e in exps:
                        print(f"    • [{e.experiment_id}] Objective: {e.research_objective[:80]}...")

                if "validation_result" in node_output and node_output["validation_result"]:
                    val = node_output["validation_result"]
                    status_text = "APPROVED" if val.is_valid else "CAVEATS NOTED"
                    print(f"  ✓ Peer Review Audit: {status_text} | Rigor Score: {val.score:.1f}/10.0")
                    if val.warnings:
                        print("    Warnings / Epistemic Caveats:")
                        for w in val.warnings[:3]:
                            print(f"      - ⚠️  {w}")

                final_state.update(node_output)

        print("\n" + "=" * 65)
        print("✓ RESEARCH WORKFLOW COMPLETED")
        print("=" * 65)

        report = final_state.get("final_report")
        if report:
            print(f"\nTitle: {report.title}")
            print(f"Audit Score: {report.validation.score:.1f}/10.0")
            print(f"\nExecutive Summary:\n{report.executive_summary}\n")

            # Show saved location
            reports = list_saved_reports()
            if reports:
                latest = reports[0]
                print(f"Saved Markdown Report: {latest.get('md_path')}")
                print(f"Saved JSON Data:       {latest.get('json_path')}")

    except Exception as e:
        print(f"\n[Execution Error] Workflow halted: {e}")
        import traceback
        traceback.print_exc()


def view_previous_reports():
    """Lists saved research reports."""
    reports = list_saved_reports()
    if not reports:
        print("\nNo saved research reports found in 'reports/' directory.")
        return

    print("\n--- Saved Research Reports ---")
    if rich_available and console:
        table = Table(title="Archived Research Dossiers")
        table.add_column("#", style="dim", width=4)
        table.add_column("Folder / Run", style="cyan")
        table.add_column("Topic / Question", style="white")
        table.add_column("Papers", justify="center")
        table.add_column("Score", justify="center")

        for idx, r in enumerate(reports, start=1):
            table.add_row(
                str(idx),
                r["folder_name"][:25],
                r["research_question"][:45] + ("..." if len(r["research_question"]) > 45 else ""),
                str(r["paper_count"]),
                f"{r['score']:.1f}",
            )
        console.print(table)
    else:
        for idx, r in enumerate(reports, start=1):
            print(f"{idx}. [{r['folder_name']}] {r['research_question']}")
            print(f"   Papers: {r['paper_count']} | Score: {r['score']:.1f}/10.0 | Path: {r['json_path']}")


def open_previous_report():
    """Allows selecting and inspecting a past report in terminal."""
    reports = list_saved_reports()
    if not reports:
        print("\nNo saved research reports to open.")
        return

    view_previous_reports()
    choice = input("\nEnter report number to open (or press Enter to return): ").strip()
    if not choice:
        return

    try:
        idx = int(choice)
        if 1 <= idx <= len(reports):
            selected = reports[idx - 1]
            report_obj = load_report_by_folder(selected["folder_name"])
            if report_obj:
                md_text = render_markdown_report(report_obj)
                print("\n" + "=" * 65)
                if rich_available and console:
                    console.print(Markdown(md_text))
                else:
                    print(md_text)
                print("=" * 65)
                print(f"File Path: {selected['md_path']}")
            else:
                print(f"Could not load report content from {selected['folder_name']}.")
        else:
            print("Invalid report selection number.")
    except ValueError:
        print("Invalid input.")


def view_configuration_status():
    """Displays current environment and API settings without exposing secrets."""
    status = get_config_status()
    print("\n--- Autonomous AI Researcher Configuration Status ---")
    for key, val in status.items():
        print(f"  {key.replace('_', ' ').capitalize()}: {val}")


def main():
    """Main CLI entrypoint loop."""
    print_banner()
    while True:
        print_menu()
        choice = input("\nEnter option (1-5): ").strip()
        if choice == "1":
            start_new_research()
        elif choice == "2":
            view_previous_reports()
        elif choice == "3":
            open_previous_report()
        elif choice == "4":
            view_configuration_status()
        elif choice == "5" or choice.lower() in ["exit", "quit", "q"]:
            print("\nExiting Autonomous AI Researcher. Academic integrity preserved.")
            break
        else:
            print("Invalid option. Please enter a number between 1 and 5.")


if __name__ == "__main__":
    main()
