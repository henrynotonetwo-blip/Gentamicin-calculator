"""
Deployment entrypoint for Streamlit Community Cloud (and other hosts).

This repo's source code lives under:
  Gentmicin Calculator Code/Calculator Code/

To avoid reshuffling the project, this wrapper simply runs the real Streamlit app
from its existing location.
"""

from __future__ import annotations

import runpy
from pathlib import Path


APP_PATH = (
    Path(__file__).resolve().parent
    / "Gentmicin Calculator Code"
    / "Calculator Code"
    / "streamlit_app.py"
)

runpy.run_path(str(APP_PATH), run_name="__main__")

