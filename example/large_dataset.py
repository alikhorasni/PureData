"""
Million rows, performance measurement.

Generates a large dataset with various quality issues and cleans it,
reporting elapsed time and peak memory.
"""

import time
import tracemalloc
import polars as pl
import numpy as np
from turboclean import DataPurityEngine

N = 1_000_000
np.random.seed(42)

# Generate string columns with empty strings instead of None to avoid Object dtype
categories = np.random.choice(["A", "B", "C", ""], N)
dates = np.random.choice(["2021-01-01", "01/02/2022", "", ""], N)

df = pl.DataFrame(
    {
        "id": range(N),
        "value": np.random.normal(100, 15, N).tolist(),
        "category": categories,
        "date": dates,
    }
)

df.write_csv("large_dirty.csv")
print(f"Generated {N} rows")

engine = DataPurityEngine()
tracemalloc.start()
t0 = time.monotonic()

engine.load("large_dirty.csv").suggest_cleansing_rules().clean().write(
    "large_clean.parquet"
)

elapsed = time.monotonic() - t0
_, peak = tracemalloc.get_traced_memory()
tracemalloc.stop()

print(f"✅ Cleaned in {elapsed:.2f}s, peak memory {peak / 1024**2:.1f} MiB")
