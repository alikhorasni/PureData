"""
Loading a remote CSV and cleaning it.

Uses the Iris dataset (publicly available) and shows two methods:
1. Directly via Polars' `scan_csv` (if supported)
2. Fallback: download with `read_csv` and write a temporary file
"""

import tempfile
import polars as pl
from turboclean import DataPurityEngine

# Reliable public CSV (Iris dataset)
URL = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"

engine = DataPurityEngine()

try:
    engine._lf = pl.scan_csv(URL)
    engine.suggest_cleansing_rules().clean().write("iris_clean.parquet")
    print("✅ Cleaned remote Iris dataset directly via scan_csv")
except Exception:
    print("Direct URL scan not supported, downloading first...")
    df = pl.read_csv(URL)
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        df.write_csv(tmp.name)
        engine.load(tmp.name).suggest_cleansing_rules().clean().write(
            "iris_clean.parquet"
        )
    print("✅ Cleaned remote Iris dataset via temporary file")
