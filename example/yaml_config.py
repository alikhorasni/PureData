"""
Using a YAML configuration file.

Write rules in a human‑friendly YAML file and load them with rule_factory.
"""
import yaml
from turboclean import DataPurityEngine
from turboclean.rule_factory import rule_factory

# Create a YAML config
config = [
    {"type": "missing", "column": "age", "strategy": "median"},
    {"type": "outlier", "column": "age", "method": "iqr"},
    {"type": "category", "column": "department", "rare_threshold": 0.05},
]
with open("rules.yaml", "w") as f:
    yaml.dump(config, f)

engine = DataPurityEngine()
engine.load("example_dirty.csv")

with open("rules.yaml") as f:
    rules = rule_factory(yaml.safe_load(f))

engine.clean(rules)
engine.write("example_yaml_clean.csv")
print("✅ Cleaned using YAML rules")
