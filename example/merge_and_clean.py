"""
Loading two datasets, joining, and cleaning.
"""
import polars as pl
from turboclean import DataPurityEngine

# Create two related CSVs
users = pl.DataFrame({"id": [1,2,3], "name": ["Alice", "Bob", None]})
orders = pl.DataFrame({"user_id": [1,2,2,3], "amount": [100, 200, None, 150]})
users.write_csv("users.csv")
orders.write_csv("orders.csv")

# Clean and join
engine = DataPurityEngine()
engine.load("users.csv")
engine.suggest_cleansing_rules().clean().write("clean_users.parquet")

# Re‑load cleaned users, join with orders
clean_users = pl.read_parquet("clean_users.parquet")
orders_df = pl.read_csv("orders.csv")
merged = orders_df.join(clean_users, left_on="user_id", right_on="id", how="inner")
merged.write_csv("merged_clean.csv")
print("✅ Merged and cleaned")
