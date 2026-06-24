"""
Central Polars loader with automatic fallback to CPU‑compatible build.

Standard Polars (with optional GPU support) is tried first.
If it fails due to missing CPU features (AVX2, etc.) or any other
import-time error, the library silently switches to ``polars-lts-cpu``.

Users who want GPU acceleration should install the `gpu` extra:
    pip install "turboclean[gpu]"
"""

from __future__ import annotations

import warnings

# Temporarily suppress the CPU‑check warning so the fallback
# doesn’t frighten the user with scary dumps.
with warnings.catch_warnings():
    warnings.simplefilter("ignore", RuntimeWarning)
    warnings.simplefilter("ignore", UserWarning)

    try:
        import polars as _pl_std

        # Quick sanity – triggers CPU feature check in recent Polars
        _pl_std.DataFrame()
        pl = _pl_std
        _USING_GPU_POLARS = True
    except Exception:
        # Failed to load standard Polars → use the LTS build
        import polars_lts_cpu as _pl_lts

        pl = _pl_lts
        _USING_GPU_POLARS = False

# Clean up temporary names so they are not visible from outside
del _pl_std, _pl_lts

__all__ = ["pl", "_USING_GPU_POLARS"]
