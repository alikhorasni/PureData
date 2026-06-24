from __future__ import annotations

from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .cleaners import MissingCleaner, Normalizer, OutlierCleaner
from .contracts import FileFormat
from .engine import DataPurityEngine
from .reporting import ReportGenerator
from .rule_factory import rule_factory

console = Console()


def _detect_format(path: str) -> FileFormat:
    """Infer file format from extension, defaulting to CSV for unknown extensions."""
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


def _resolve_columns(
    lf_columns: list[str],
    user_specified: str | None,
) -> list[str]:
    """Validate and return a list of columns to process.

    Raises click.BadParameter if any requested column does not exist.
    """
    if not user_specified:
        return lf_columns

    requested = [col.strip() for col in user_specified.split(",")]
    invalid = [col for col in requested if col not in lf_columns]
    if invalid:
        raise click.BadParameter(
            f"Column(s) not found: {', '.join(invalid)}. "
            f"Available columns: {', '.join(lf_columns)}"
        )
    return requested


def _print_rules(rules: list, verbose: bool = False) -> None:
    """Display a table of cleaning rules, with details if verbose is True."""
    if not rules:
        if verbose:
            console.print("[dim]No cleaning rules applied.[/dim]")
        return

    table = Table(
        title="📋 Cleaning Rules Applied",
        title_style="bold cyan",
        border_style="cyan",
        header_style="bold white",
    )
    table.add_column("Column", style="cyan", no_wrap=True)
    table.add_column("Rule", style="green")
    table.add_column("Parameters", style="dim")

    for rule in rules:
        col_display = "ALL COLUMNS" if rule.column == "__all__" else rule.column
        params = ", ".join(
            f"{k}={v}" for k, v in rule.parameters.items() if k != "column"
        )
        table.add_row(col_display, rule.name, params or "—")
    console.print(table)


def _build_summary_panel(rows: int, cols: int, output: str, dry_run: bool) -> Panel:
    """Create a rich Panel summarizing the cleaning result."""
    if dry_run:
        return Panel.fit(
            f"Would process [bold]{rows}[/bold] rows × [bold]{cols}[/bold] columns.\n"
            "No output written (dry‑run).",
            title="🔍 Dry‑Run Complete",
            border_style="yellow",
        )
    return Panel.fit(
        f"Rows: [bold]{rows}[/bold]\nColumns: [bold]{cols}[/bold]\nOutput: [bold green]{output}[/bold green]",
        title="✅ Cleaning Complete",
        border_style="green",
    )


@click.group()
@click.version_option(version=__version__, prog_name="TurboClean")
def main() -> None:
    """TurboClean – Ultra‑fast, intelligent data cleansing at scale.

    \b
    Examples:
      turboclean clean dirty.csv clean.parquet --auto-magic
      turboclean profile messy.csv --report quality.md
      turboclean clean data.csv out.csv --missing mean --outliers iqr --columns age,salary
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
    "--outliers",
    type=click.Choice(["iqr", "zscore"]),
    help="Outlier detection method.",
)
@click.option(
    "--normalize/--no-normalize",
    default=False,
    help="Apply z‑score normalisation.",
)
@click.option(
    "--columns",
    help="Comma‑separated list of columns to target (default: all numeric columns).",
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
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Show what would be done without writing the output.",
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Show detailed profiling information and rules.",
)
@click.option(
    "--quiet",
    is_flag=True,
    default=False,
    help="Suppress all non‑error output (useful for scripting).",
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit the number of rows loaded for quick tests.",
)
def clean(
    input: str,
    output: str,
    missing: str | None,
    outliers: str | None,
    normalize: bool,
    columns: str | None,
    config: str | None,
    auto_magic: bool,
    dry_run: bool,
    verbose: bool,
    quiet: bool,
    limit: int | None,
) -> None:
    """Clean a dataset and write the result to OUTPUT."""
    if quiet:
        console.quiet = True
    try:
        engine = DataPurityEngine()
        in_fmt = _detect_format(input)
        out_fmt = _detect_format(output)

        if not quiet:
            console.print("[bold]Loading data…[/bold]", end=" ")
        engine.load(input, format=in_fmt)
        if not quiet:
            console.print("[green]done.[/green]")

        rules = []
        if config:
            with open(config) as f:
                cfg = yaml.safe_load(f)
            rules = rule_factory(cfg)
        elif auto_magic:
            if not quiet:
                console.print("[bold]Profiling with auto‑magic…[/bold]")
            engine.suggest_cleansing_rules()
            if verbose and not quiet:
                _print_rules(engine._rules, verbose=True)
            rules = engine._rules  # use the suggested ones
        else:
            lf = engine._lf
            if lf is not None:
                all_cols = lf.columns
                target_cols = _resolve_columns(all_cols, columns)
                for col in target_cols:
                    if missing:
                        rules.append(MissingCleaner(col, strategy=missing))
                    if outliers:
                        rules.append(OutlierCleaner(col, method=outliers))
                    if normalize:
                        rules.append(Normalizer(col))
                if verbose and not quiet:
                    _print_rules(rules, verbose=True)

        if not quiet:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
            ) as progress:
                task = progress.add_task("Cleaning…", total=None)
                engine.clean(rules)
                progress.update(task, description="Cleaning complete.")
        else:
            engine.clean(rules)

        df = engine.collect()

        if not dry_run:
            engine.write(output, out_fmt)

        if not quiet:
            panel = _build_summary_panel(df.shape[0], df.shape[1], output, dry_run)
            console.print(panel)

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


@main.command()
@click.argument("input", type=click.Path(exists=True, readable=True))
@click.option(
    "--output", "-o", type=click.Path(), help="Save report to file (Markdown)."
)
@click.option("--json", "output_json", type=click.Path(), help="Save report as JSON.")
@click.option(
    "--verbose", is_flag=True, default=False, help="Show detailed profiling info."
)
@click.option(
    "--quiet", is_flag=True, default=False, help="Suppress all non‑error output."
)
@click.option(
    "--limit",
    type=int,
    default=None,
    help="Limit the number of rows loaded for quick profiling.",
)
def profile(
    input: str,
    output: str | None,
    output_json: str | None,
    verbose: bool,
    quiet: bool,
    limit: int | None,
) -> None:
    """Generate a detailed data quality profile."""
    if quiet:
        console.quiet = True
    try:
        engine = DataPurityEngine()
        if not quiet:
            console.print("[bold]Loading data…[/bold]", end=" ")
        engine.load(input)  # limit not yet supported directly, but could be added
        if not quiet:
            console.print("[green]done.[/green]")

        if not quiet:
            console.print("[bold]Profiling…[/bold]")
        engine.suggest_cleansing_rules()

        if engine._profile is None:
            console.print("[red]Could not generate profile.[/red]")
            return

        if output:
            with open(output, "w") as f:
                f.write(ReportGenerator.generate_markdown(engine._profile))
            if not quiet:
                console.print(f"[bold green]✔[/bold green] Report saved to {output}")
        if output_json:
            with open(output_json, "w") as f:
                f.write(ReportGenerator.generate_json(engine._profile))
            if not quiet:
                console.print(
                    f"[bold green]✔[/bold green] JSON report saved to {output_json}"
                )

        if not quiet:
            table = Table(
                title="📊 Column Overview",
                title_style="bold cyan",
                border_style="cyan",
                header_style="bold white",
            )
            table.add_column("Column", style="cyan", no_wrap=True)
            table.add_column("Type")
            table.add_column("Nulls", justify="right")
            table.add_column("Null %", justify="right")
            table.add_column("Drift", justify="right")
            table.add_column("Suggested Rules", style="green")

            for col, prof in engine._profile.column_profiles.items():
                null_pct = (
                    f"{prof.null_ratio:.1%}" if hasattr(prof, "null_ratio") else "N/A"
                )
                drift = (
                    f"{prof.distribution_drift_score:.3f}"
                    if prof.distribution_drift_score is not None
                    else "N/A"
                )
                rules_str = ", ".join(r.name for r in prof.suggested_rules)
                table.add_row(
                    col,
                    str(prof.dtype),
                    str(prof.null_count),
                    null_pct,
                    drift,
                    rules_str,
                )
            console.print(table)

        if verbose and not quiet:
            _print_rules(engine._rules, verbose=True)

    except click.Abort:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()


if __name__ == "__main__":
    main()
