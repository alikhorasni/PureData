"""
Custom linear interpolation for time series.
"""
from datetime import datetime, timedelta
import polars as pl
from turboclean import DataPurityEngine
from turboclean.contracts import CleanseRule

class TimeSeriesInterpolator(CleanseRule):
    name = "time_series_interpolator"
    def __init__(self, time_col: str, value_col: str):
        self.column = value_col
        self.time_col = time_col
        self.value_col = value_col
        self.parameters = {}
    def apply(self, lf):
        df = lf.sort(self.time_col).collect()
        df = df.with_columns(pl.col(self.value_col).interpolate())
        return df.lazy()

# Create data with gaps
times = [datetime(2023,1,1) + timedelta(hours=i) for i in range(100)]
values = [i + (None if i % 10 == 0 else 0) for i in range(100)]
df = pl.DataFrame({"time": times, "sensor": values})
df.write_csv("sensor.csv")

engine = DataPurityEngine()
engine.load("sensor.csv")
engine.pipe(TimeSeriesInterpolator("time", "sensor"))
engine.write("sensor_clean.csv")
print("✅ Gaps interpolated")
