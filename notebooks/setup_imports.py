import sys
import os
from pathlib import Path

# Compute the project root (parent of the notebooks directory)
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)