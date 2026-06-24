"""
Processing multiple files in a loop.
"""
from pathlib import Path
from turboclean import DataPurityEngine
import polars as pl

# Create a few dirty files
for i in range(3):
    pl.DataFrame({"x": [1, None, 3], "y": [" a", "B ", None]}).write_csv(f"batch_{i}.csv")

engine = DataPurityEngine()
for path in Path().glob("batch_*.csv"):
    engine.load(path) \
          .suggest_cleansing_rules() \
          .clean() \
          .write(f"clean_{path.stem}.parquet")
    print(f"✅ Cleaned {path}")
