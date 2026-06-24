"""
TurboClean Example 01 – One‑line auto‑magic cleaning.

Creates a small messy CSV, then cleans it with a single method chain.
"""
import polars as pl
from turboclean import DataPurityEngine

# Create a tiny dirty dataset
df = pl.DataFrame({
    "name": ["Alice", "Bob", None, "Charlie"],
    "age": [30, 25, 130, 22],                 # 130 is an outlier
    "salary": [50000, 60000, None, 70000]      # missing salary
})
df.write_csv("example_dirty.csv")

# 🪄 The magic one‑liner
DataPurityEngine() \
    .load("example_dirty.csv") \
    .suggest_cleansing_rules() \
    .clean() \
    .write("example_clean.csv")

print("✅ Cleaned data saved to example_clean.csv")
