"""
PureData CLI – A beautiful, intuitive command-line interface.
Powered by Click and Rich.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from .engine import DataPurityEngine
from .contracts import FileFormat
from .rule_factory import rule_factory
from .cleaners import MissingCleaner, OutlierCleaner, Normalizer
from .reporting import ReportGenerator

console = Console()


def _detect_format(path: str) -> FileFormat:
    ext = Path(path).suffix.lower()
    mapping = {
        ".csv": FileFormat.CSV,
        ".tsv": FileFormat.CSV,
        ".json": FileFormat.JSON,
        ".parquet": FileFormat.PARQUET,
        ".avro": FileFormat.AVRO,
        ".xlsx": FileFormat.EXCEL,
        ".xml": FileFormat.XML,
    }
    return mapping.get(ext, FileFormat.CSV)


@click.group()
@click.version_option(version="0.3.0", prog_name="PureData")
def main() -> None:
    """PureData – Ultra-fast, intelligent data cleansing at scale.

    Example usage:

    \b
    puredata clean data.csv output.parquet --auto-magic
    puredata profile dirty.json --report profile.md
    """


@main.command()
@click.argument("input", type=click.Path(exists=True, readable=True))
@click.argument("output", type=click.Path())
@click.option(
    "--missing",
    type=click.Choice(
        ["drop", "mean", "median", "mode", "forward_fill", "backward_fill"]
    ),
    help="Strategy for handling missing values.",
)
@click.option(
    "--outliers", type=click.Choice(["iqr", "zscore"]), help="Outlier detection method."
)
@click.option(
    "--normalize/--no-normalize", default=False, help="Apply z-score normalisation."
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="YAML file with custom cleaning rules.",
)
@click.option(
    "--auto-magic",
    is_flag=True,
    default=False,
    help="Let the engine analyse data and choose the best strategies automatically.",
)
@click.option("--progress/--no-progress", default=True, help="Show a progress bar.")
def clean(
    input: str,
    output: str,
    missing: Optional[str],
    outliers: Optional[str],
    normalize: bool,
    config: Optional[str],
    auto_magic: bool,
    progress: bool,
) -> None:
    """Clean a dataset and write the result to OUTPUT."""
    engine = DataPurityEngine()
    in_fmt = _detect_format(input)
    out_fmt = _detect_format(output)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as prog:
        task = prog.add_task("Loading data...", start=False)
        prog.start_task(task)
        engine.load(input, format=in_fmt)
        prog.update(task, description="Profiling and applying rules...")

        rules = []
        if config:
            with open(config, "r") as f:
                cfg = yaml.safe_load(f)
            rules = rule_factory(cfg)
            engine.clean(rules)
        elif auto_magic:
            engine.suggest_cleansing_rules()
            engine.clean()
        else:
            lf = engine._lf
            if lf is not None:
                cols = lf.columns
                num_cols = [c for c in cols if lf.schema[c].is_numeric()]
                for col in num_cols:
                    if missing:
                        rules.append(
                            MissingCleaner(col, strategy=missing)
                        )  # noqa: F821
                    if outliers:
                        rules.append(OutlierCleaner(col, method=outliers))  # noqa: F821
                    if normalize:
                        rules.append(Normalizer(col))  # noqa: F821
                engine.clean(rules)

        prog.update(task, description="Writing output...")
        engine.write(output, out_fmt)
        prog.update(task, description="Done!")

    console.print(
        f"[bold green]✔[/bold green] Cleaned data saved to [bold]{output}[/bold]"
    )


@main.command()
@click.argument("input", type=click.Path(exists=True, readable=True))
@click.option(
    "--output", "-o", type=click.Path(), help="Save report to file (Markdown)."
)
@click.option("--json", "output_json", type=click.Path(), help="Save report as JSON.")
def profile(input: str, output: Optional[str], output_json: Optional[str]) -> None:
    """Generate a detailed data quality profile."""
    engine = DataPurityEngine()
    engine.load(input)
    engine.suggest_cleansing_rules()

    if engine._profile is None:
        console.print("[red]Could not generate profile.[/red]")
        return

    if output:
        with open(output, "w") as f:
            f.write(ReportGenerator.generate_markdown(engine._profile))  # noqa: F821
        console.print(f"[bold green]✔[/bold green] Report saved to {output}")
    if output_json:
        with open(output_json, "w") as f:
            f.write(ReportGenerator.generate_json(engine._profile))  # noqa: F821
        console.print(f"[bold green]✔[/bold green] JSON report saved to {output_json}")

    # Always print a summary table
    table = Table(title="Column Overview")
    table.add_column("Column", style="cyan")
    table.add_column("Type")
    table.add_column("Nulls", justify="right")
    table.add_column("Drift", justify="right")
    table.add_column("Suggested Rules")

    for col, prof in engine._profile.column_profiles.items():
        drift = (
            f"{prof.distribution_drift_score:.3f}"
            if prof.distribution_drift_score is not None
            else "N/A"
        )
        table.add_row(
            col,
            str(prof.dtype),
            str(prof.null_count),
            drift,
            ", ".join(r.name for r in prof.suggested_rules),
        )

    console.print(table)


if __name__ == "__main__":
    main()
