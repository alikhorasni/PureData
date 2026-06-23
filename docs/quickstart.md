# Quickstart

Install TurboClean:
```bash
pip install turboclean
```
1‑Line Magic
```python
from turboclean import DataPurityEngine
DataPurityEngine().load("dirty.csv").suggest_cleansing_rules().clean().write("clean.parquet")
```
CLI
```bash
turboclean clean dirty.csv clean.parquet --auto-magic
turboclean profile dirty.csv --report report.md
```
Custom Cleaning Rules (YAML)
```yaml
- type: missing
  column: age
  strategy: median
- type: outlier
  column: salary
  method: iqr
```
```bash
turboclean clean dirty.csv clean.parquet --config rules.yaml
```
