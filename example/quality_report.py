"""
Generating data quality reports.
"""
from turboclean import DataPurityEngine
from turboclean.reporting import ReportGenerator
import polars as pl

df = pl.DataFrame({"age": [25, None, 130], "city": ["London", "london ", None]})
df.write_csv("report_data.csv")

engine = DataPurityEngine()
engine.load("report_data.csv")
engine.suggest_cleansing_rules()

# Markdown report
md = ReportGenerator.generate_markdown(engine._profile)
with open("quality_report.md", "w") as f:
    f.write(md)

# JSON report
js = ReportGenerator.generate_json(engine._profile)
with open("quality_report.json", "w") as f:
    f.write(js)

print("✅ Reports saved")
