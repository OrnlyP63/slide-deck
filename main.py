from __future__ import annotations

from pathlib import Path

import click
from rich.console import Console

console = Console()


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.argument("md_file", type=click.Path(exists=True))
@click.option("--output-dir", default="output", show_default=True)
@click.option("--engine", default="pdflatex", type=click.Choice(["pdflatex", "lualatex"]), show_default=True)
@click.option("--theme", default=None, type=click.Choice(["consulting", "minimal", "dark"]), help="Override deck theme")
def build(md_file: str, output_dir: str, engine: str, theme: str | None) -> None:
    """Parse a .md file and compile to PDF."""
    from slides.api import parse, validate, build as api_build

    deck = parse(md_file)
    warnings = validate(deck)
    for w in warnings:
        console.print(f"[yellow]⚠[/yellow]  {w}")

    pdf = api_build(deck, output_dir, engine, theme)
    console.print(f"[green]✓[/green]  PDF: [bold]{pdf}[/bold]")


@cli.command()
@click.argument("md_file", type=click.Path(exists=True))
def validate(md_file: str) -> None:
    """Lint a .md deck file without compiling."""
    from slides.api import parse, validate as api_validate

    deck = parse(md_file)
    warnings = api_validate(deck)
    if not warnings:
        console.print("[green]✓[/green]  No issues found.")
    for w in warnings:
        console.print(f"[yellow]⚠[/yellow]  {w}")
    console.print(f"\n[dim]{len(deck.slides)} slides parsed[/dim]")
    for i, s in enumerate(deck.slides):
        console.print(f"  [{i}] {type(s).__name__:<25} {s.action_title}")


if __name__ == "__main__":
    cli()
