import sys
from pathlib import Path

# Add project root to sys.path so "core" can be imported in all tests
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
