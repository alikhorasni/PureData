"""
Custom Isolation Forest outlier flagger.

Shows how to inject a machine‑learning model into the cleaning pipeline.
"""
import polars as pl
import numpy as np
from sklearn.ensemble import IsolationForest
from turboclean import DataPurityEngine
from turboclean.contracts import CleanseRule

# Custom rule
class IsolationForestOutlier(CleanseRule):
    name = "isolation_forest_outlier"
    def __init__(self, column: str, contamination: float = 0.05):
        self.column = column
        self.contamination = contamination
        self.parameters = {"contamination": contamination}
    def apply(self, lf):
        df = lf.select(pl.col(self.column)).collect()
        vals = df[self.column].to_numpy().reshape(-1, 1).copy()
        mask = np.isnan(vals)
        vals[mask] = np.nanmean(vals)
        model = IsolationForest(contamination=self.contamination, random_state=42)
        preds = model.fit_predict(vals)
        flags = (preds == -1)
        return lf.collect().with_columns(pl.Series("__outlier", flags)).lazy()

# Generate fake transaction data
np.random.seed(42)
amounts = np.random.exponential(50, 5000)
amounts[np.random.choice(5000, 50)] = np.random.uniform(5000, 50000, 50)  # fraud
df = pl.DataFrame({"amount": amounts, "id": range(5000)})
df.write_csv("fraud.csv")

engine = DataPurityEngine()
engine.load("fraud.csv")
engine.pipe(IsolationForestOutlier("amount", contamination=0.01))
engine.write("fraud_flagged.parquet")
print("✅ Fraud flagged with Isolation Forest")
