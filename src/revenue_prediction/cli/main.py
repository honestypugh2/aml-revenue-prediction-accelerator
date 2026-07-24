"""Typer-based CLI entry point.

All commands run fully offline by default. Azure/Fabric commands are opt-in and
fail gracefully with actionable messages when credentials or the optional
``azure`` / ``fabric`` extras are not present.
"""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ..config.loader import load_settings

app = typer.Typer(
    help="Healthcare facility net-revenue prediction accelerator (synthetic data).",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.command("generate-data")
def generate_data(
    environment: str = typer.Option("dev", "--env", "-e", help="dev|test|prod"),
) -> None:
    """Generate and persist the synthetic, sample, and invalid datasets."""
    from ..data.io import materialise_default_datasets

    settings = load_settings(environment)
    outputs = materialise_default_datasets(settings.data)
    table = Table(title="Synthetic datasets written")
    table.add_column("dataset")
    table.add_column("path")
    for name, path in outputs.items():
        table.add_row(name, str(path))
    console.print(table)


@app.command("train-local")
def train_local(
    environment: str = typer.Option("dev", "--env", "-e"),
    output_dir: Path = typer.Option(Path("outputs"), "--out", "-o"),
    track_mlflow: bool = typer.Option(False, "--mlflow", help="Log runs to a local MLflow store"),
) -> None:
    """Train all code-first candidates offline and select champion/challenger."""
    from ..pipelines.local_pipeline import run_local_pipeline

    settings = load_settings(environment)
    result = run_local_pipeline(settings, output_dir=output_dir, track_mlflow=track_mlflow)

    table = Table(title=f"Model comparison (primary metric: {result.selection.metric})")
    for col in result.comparison.columns:
        table.add_column(str(col))
    for _, row in result.comparison.iterrows():
        table.add_row(*[f"{v:.4g}" if isinstance(v, float) else str(v) for v in row])
    console.print(table)

    console.print(f"[bold green]Champion:[/] {result.selection.champion}")
    if result.selection.challenger:
        console.print(f"[bold]Challenger:[/] {result.selection.challenger}")
    if result.bundle_path:
        console.print(f"Champion bundle saved to: {result.bundle_path}")


@app.command("predict")
def predict(
    bundle_path: Path = typer.Argument(..., help="Path to a saved champion bundle"),
    data_path: Path = typer.Argument(..., help="Path to snapshot data (parquet/csv)"),
    output_path: Path = typer.Option(Path("outputs/predictions.csv"), "--out", "-o"),
    cutoff_day: int | None = typer.Option(None, "--cutoff-day"),
) -> None:
    """Score a dataset with a saved champion bundle (batch inference)."""
    from ..data.io import read_dataset, write_dataset
    from ..inference.predict import batch_predict, load_bundle

    bundle = load_bundle(bundle_path)
    frame = read_dataset(data_path)
    predictions = batch_predict(bundle, frame, cutoff_day=cutoff_day)
    write_dataset(predictions, output_path)
    console.print(f"[green]Wrote {len(predictions)} predictions to {output_path}[/]")


@app.command("validate-data")
def validate_data(
    data_path: Path = typer.Argument(..., help="Path to snapshot data (parquet/csv)"),
    require_target: bool = typer.Option(True, "--require-target/--no-require-target"),
) -> None:
    """Validate a dataset against the schema and leakage rules."""
    from ..data.contracts import (
        ContractViolation,
        validate_leakage_rules,
        validate_raw_snapshots,
    )
    from ..data.io import read_dataset

    frame = read_dataset(data_path)
    try:
        validate_raw_snapshots(frame, require_target=require_target)
        validate_leakage_rules(frame)
    except ContractViolation as exc:
        console.print(f"[red]Contract violation:[/] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]OK[/] — {len(frame)} rows passed schema + leakage checks")


@app.command("info")
def info(environment: str = typer.Option("dev", "--env", "-e")) -> None:
    """Show resolved configuration (secrets are never printed)."""
    settings = load_settings(environment)
    console.print(f"[bold]Environment:[/] {settings.environment}")
    console.print(f"[bold]Facilities:[/] {settings.data.n_facilities}")
    console.print(f"[bold]Months:[/] {settings.data.n_months}")
    console.print(f"[bold]Snapshot days:[/] {settings.data.snapshot_days}")
    console.print(f"[bold]Candidates:[/] {settings.model.candidates}")
    console.print(f"[bold]Azure ML configured:[/] {settings.azure_ml.is_configured()}")
    console.print(f"[bold]Fabric configured:[/] {settings.fabric.is_configured()}")


if __name__ == "__main__":  # pragma: no cover
    app()
