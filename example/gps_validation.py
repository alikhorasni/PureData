"""
Removing rows with invalid GPS coordinates.
"""
import polars as pl
import numpy as np
from turboclean import DataPurityEngine
from turboclean.contracts import CleanseRule

class GPSCleaner(CleanseRule):
    name = "gps_cleaner"
    def __init__(self, lat_col: str, lon_col: str):
        self.column = lat_col
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.parameters = {}
    def apply(self, lf):
        return lf.filter(
            pl.col(self.lat_col).is_between(-90, 90) &
            pl.col(self.lon_col).is_between(-180, 180)
        )

# Mix of valid and invalid coordinates
df = pl.DataFrame({
    "lat": [52.52, 200.0, -95.0, 0.0],
    "lon": [13.40, 100.0, 300.0, -74.0],
})
df.write_csv("gps.csv")

engine = DataPurityEngine()
engine.load("gps.csv")
engine.pipe(GPSCleaner("lat", "lon"))
engine.write("gps_clean.csv")
print("✅ Invalid GPS rows removed")
