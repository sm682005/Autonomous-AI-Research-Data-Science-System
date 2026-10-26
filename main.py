"""
Root Entrypoint for Autonomous AI Researcher.
Enables running `python main.py` directly from workspace root or inside AI_Researcher/.
"""

import sys
from pathlib import Path

# Add project root and AI_Researcher to path
root_dir = Path(__file__).resolve().parent
ai_researcher_dir = root_dir / "AI_Researcher"

for p in [str(root_dir), str(ai_researcher_dir)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from AI_Researcher.main import main

if __name__ == "__main__":
    main()
