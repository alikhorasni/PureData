# examples/

This directory contains ready‑to‑run scripts that demonstrate **TurboClean** in action across a variety of
real‑world scenarios.  Each script is self‑contained and heavily commented.

## 📁 Contents

| File | Description |
|------|-------------|
| `basic_auto_magic.py` | The famous one‑liner – auto‑magic cleaning on a small CSV |
| `cli_auto_magic.md` | CLI one‑liner (no Python needed) |
| `custom_rules.py` | Manually combining built‑in cleaners |
| `yaml_config.py` | Loading cleaning rules from a YAML file |
| `large_dataset.py` | Processing a 1M‑row dataset with performance measurement |
| `financial_fraud.py` | Complex pipeline with custom Isolation Forest outlier flagger |
| `time_series_interpolation.py` | Custom rule for linear interpolation on time series |
| `gps_validation.py` | Removing invalid GPS coordinates with a custom rule |
| `batch_processing.py` | Cleaning multiple files in a loop |
| `quality_report.py` | Generating Markdown and JSON quality reports |
| `streaming_from_url.py` | Loading directly from a URL (requires `fsspec`) |
| `merge_and_clean.py` | Loading two sources, joining, and cleaning |

---

## 🚀 How to run
1. Install TurboClean:
   ```bash
   pip install turboclean
   ```
(Optional) Install extras for some examples:

```bash
pip install "turboclean[all]"
```

Run any script:

```bash
python examples/basic_auto_magic.py
```
1. Install TurboClean:
   ```bash
   pip install turboclean
