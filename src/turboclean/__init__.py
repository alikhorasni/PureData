"""
TurboClean: Ultra-fast, adaptive data cleansing engine.

TurboClean is an enterprise‑grade library for intelligent data screening,
adaptive cleaning, and quality improvement.  It supports lazy, streaming
execution over datasets of any size, with zero‑copy conversion between
CSV, JSON, Parquet, and other industrial formats.

Public API
----------
- :class:`DataPurityEngine` – main entry point for loading, profiling, and cleaning.
- :class:`DynamicProfiler` – statistical profiler with distribution drift detection.
- Built‑in cleaning rules (all implement :class:`CleanseRule`):
  * :class:`MissingCleaner`
  * :class:`OutlierCleaner`
  * :class:`DriftCorrector`
  * :class:`Normalizer`
  * :class:`CategoryCleaner`
  * :class:`DateFormatter`
  * :class:`Deduplicator`
  * :class:`TextNormalizer`
  * :class:`TypeCaster`
- :class:`ReportGenerator` – create Markdown/JSON quality reports.
- :func:`rule_factory` – convert YAML/JSON configurations into rule lists.
- :class:`FileFormat` – enum of supported file formats.
- Protocols: :class:`CleanseRule`, :class:`DataProfile`, :class:`ColumnProfile`.
"""

from __future__ import annotations

from .cleaners import (
    CategoryCleaner,
    DateFormatter,
    Deduplicator,
    DriftCorrector,
    MissingCleaner,
    Normalizer,
    OutlierCleaner,
    TextNormalizer,
    TypeCaster,
)
from .contracts import CleanseRule, ColumnProfile, DataProfile, FileFormat
from .engine import DataPurityEngine
from .profiling import DynamicProfiler
from .reporting import ReportGenerator
from .rule_factory import rule_factory

__version__: str = "0.3.3"

__all__ = [
    "__version__",
    "DataPurityEngine",
    "DynamicProfiler",
    "MissingCleaner",
    "OutlierCleaner",
    "DriftCorrector",
    "Normalizer",
    "CategoryCleaner",
    "DateFormatter",
    "Deduplicator",
    "TextNormalizer",
    "TypeCaster",
    "ReportGenerator",
    "rule_factory",
    "FileFormat",
    "CleanseRule",
    "DataProfile",
    "ColumnProfile",
]
