"""Portable reference pipeline. Run from project root: python scripts/generate_and_clean_stdlib.py

The packaged CSVs were generated with seed 20260816. This implementation uses only
the Python standard library; the equivalent PySpark transformations live in src/.
"""
from pathlib import Path
import runpy

# A standalone copy of the exact build logic is kept in the portfolio package.
builder = Path(__file__).with_name("project_data_builder.py")
runpy.run_path(str(builder), run_name="__main__")
