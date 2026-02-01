"""
pytest configuration and shared fixtures.

Run from project root: pytest tests/ -v
"""

import sys
from pathlib import Path

# Ensure project root is on path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))
