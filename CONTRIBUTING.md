# Contributing to TurboClean

First off, thank you for considering contributing to TurboClean!  
We believe that data quality should never be a bottleneck, and your help makes that vision stronger.

This document outlines the rules, best practices, and workflow to follow when contributing to the project.  
TurboClean is built with **strict typing (`mypy --strict`)**, **ultra‑low latency (Polars LazyFrame)**, and a **Strategy‑based architecture** in mind — please keep these principles in every contribution.

---

## 📦 Development Setup

1. **Fork & Clone** the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/TurboClean.git
   cd TurboClean
   ```

2. **Create a virtual environment** (Python 3.10+ required):
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # or .venv\Scripts\activate on Windows
   ```

3. **Install in editable mode with all dev dependencies**:
   ```bash
   pip install -e ".[all,dev]"
   ```

4. **Install pre‑commit hooks** (runs linters and formatters automatically before each commit):
   ```bash
   pre-commit install
   ```

---

## 🧪 Running Tests & Linters

We enforce a zero‑warning policy. Before pushing, make sure everything passes:

```bash
# Auto‑fix lint issues and format code
ruff check --fix src tests
ruff format src tests

# Run strict type checking
mypy src

# Run the full test suite
pytest tests --cov=turboclean --cov-report=term-missing
```

All three commands must exit with **zero errors**.

> **CI:** Every push and pull request triggers the same checks via GitHub Actions.  
> If your PR fails, check the CI logs — the exact line and error are always shown.

---

## 🧩 Adding a New Built‑in Cleaner

TurboClean uses the **Strategy Pattern**. Adding a new cleaner is a matter of implementing one protocol.

### Step‑by‑step

1. **Create your class** in `src/turboclean/cleaners.py`:

   ```python
   from .contracts import CleanseRule
   import polars as pl

   class MyNewCleaner(CleanseRule):
       name = "my_new_cleaner"          # unique name

       def __init__(self, column: str, ...):   # your parameters
           self.column = column
           self.parameters = { ... }

       def apply(self, lf: pl.LazyFrame) -> pl.LazyFrame:
           # Your lazy transformation logic here
           return lf.with_columns(...)
   ```

2. **Register it** in `src/turboclean/rule_factory.py`:
   ```python
   from .cleaners import MyNewCleaner

   _RULE_MAP = {
       ...
       "my_new_cleaner": MyNewCleaner,
   }
   ```

3. **Write tests** in `tests/test_cleaners.py`:
   ```python
   def test_my_new_cleaner():
       lf = pl.LazyFrame(...)
       cleaner = MyNewCleaner(...)
       result = cleaner.apply(lf).collect()
       assert ...
   ```

4. **(Optional) Add automatic suggestion** in `src/turboclean/profiling.py` — if your cleaner should be part of the `suggest_cleansing_rules()` output, add it inside the `for col in columns` loop of `DynamicProfiler.generate_profile`.

5. **Update this file** if your cleaner introduces a new concept or parameters that need documentation.

---

## 🧱 Architecture Guidelines

- **All core logic must operate on `pl.LazyFrame`** — never collect data unless absolutely necessary (e.g., to compute statistics).  
- **Use `pyarrow` for schema inference** and `polars` for execution.  
- **Keep zero‑copy in mind** — converting between formats should not duplicate memory.  
- **Type hints are mandatory** — our `mypy` config is `strict`.  
- **All public methods must be decorated with `@benchmark`** from `turboclean.utils` — this automatically logs time and memory.  
- **Handle edge cases gracefully** — empty DataFrames, all‑null columns, zero‑variance data, etc. **must not crash** the engine.  
- **Security first** — output paths are sanitised, user input is validated, and clear exceptions are raised when something is wrong.

---

## 📄 Documentation

- Update `README.md` if your change impacts the public API or user experience.  
- Add inline docstrings to new classes and methods.  
- If you add a new feature, update `docs/api.md`.

---

## 🗣️ Pull Request Process

1. Open an issue describing what you want to do **before** writing code (for anything larger than a typo fix).  
2. Create a feature branch from `main`.  
3. Implement your changes, write/update tests, and run the full lint‑type‑test pipeline locally.  
4. Push and open a Pull Request against `main`.  
5. In the PR description, explain **what** you changed, **why**, and how you tested it.  
6. Wait for review — a maintainer will merge it once all checks pass and the discussion is resolved.

---

## 🧙 Philosophy

TurboClean is more than a tool — it's a **platform for data quality automation**.  
We optimise for:

- **Speed** — every millisecond counts.  
- **Safety** — the library must never crash on malformed input.  
- **Extensibility** — anyone should be able to add a cleaner in under 5 minutes.

If you share these values, you’re in the right place. We’re excited to see what you’ll build.

---

**Thank you for helping make data cleaner, faster, and more reliable for everyone.** 💚
