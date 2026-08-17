"""Generate explicitly synthetic retail-banking CSV data (fixed seed)."""
from pathlib import Path
import runpy

# The full reproducible generator is included at project root for portability.
runpy.run_path(str(Path(__file__).parents[1] / "scripts" / "generate_and_clean_stdlib.py"), run_name="__main__")
