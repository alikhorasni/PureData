# API Reference

## `DataPurityEngine`

- `load(source, format=None, lazy=True)` → Self
- `infer_schema(sample_size=10000)` → `pa.Schema`
- `suggest_cleansing_rules()` → `list[CleanseRule]`
- `clean(rules=None)` → Self
- `write(destination, format)` → None
- `collect()` → `pl.DataFrame`

## Built‑in Cleaners

- `MissingCleaner(column, strategy)`
- `OutlierCleaner(column, method, factor)`
- `DriftCorrector(column)`
- `Normalizer(column, method)`
- `CategoryCleaner(column, max_categories, rare_threshold)`
- `DateFormatter(column, target_format)`
- `Deduplicator(subset)`
- `TextNormalizer(column, lower, trim)`
- `TypeCaster(column, target_type)`

## `DynamicProfiler`

- `generate_profile()` → `ConcreteDataProfile`
