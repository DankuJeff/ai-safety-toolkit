"""
CLI entry point for running the red-team eval suite.

Usage:
    python run_eval.py
    python run_eval.py --categories hate_speech violence
    python run_eval.py --prompt-ids hs-001 pi-003
    python run_eval.py --target-model claude-haiku-4-5-20251001
"""
import os
import sys
import logging

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich import print as rprint

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))

from shared.claude_client import ClaudeClient
from runner.evaluator import Evaluator
from tracker.database import init_db
from tracker.repository import RunRepository

console = Console()
logging.basicConfig(level=logging.WARNING)


@click.command()
@click.option("--categories", "-c", multiple=True, help="Filter by category name(s)")
@click.option("--prompt-ids", "-p", multiple=True, help="Run specific prompt IDs only")
@click.option("--target-model", default=None, help="Model to evaluate (overrides env TARGET_MODEL)")
@click.option("--judge-model", default=None, help="Judge model (overrides env JUDGE_MODEL)")
def main(categories, prompt_ids, target_model, judge_model):
    target = target_model or os.getenv("TARGET_MODEL", "claude-sonnet-4-6")
    judge = judge_model or os.getenv("JUDGE_MODEL", "claude-haiku-4-5-20251001")

    console.rule("[bold blue]GP-2: LLM Red-Teaming Eval Runner")
    console.print(f"  Target model : [cyan]{target}[/cyan]")
    console.print(f"  Judge model  : [cyan]{judge}[/cyan]")
    if categories:
        console.print(f"  Categories   : {', '.join(categories)}")
    if prompt_ids:
        console.print(f"  Prompt IDs   : {', '.join(prompt_ids)}")
    console.print()

    init_db()

    target_client = ClaudeClient(default_model=target)
    judge_client = ClaudeClient(default_model=judge)

    with RunRepository() as repo:
        evaluator = Evaluator(
            target_client=target_client,
            judge_client=judge_client,
            target_model=target,
            judge_model=judge,
            repository=repo,
        )

        with console.status("[bold green]Running eval suite..."):
            summary = evaluator.run(
                categories=list(categories) if categories else None,
                prompt_ids=list(prompt_ids) if prompt_ids else None,
            )

    # Print results table
    table = Table(title=f"Run {summary.run_id[:8]} — {summary.model}", show_lines=True)
    table.add_column("Metric", style="bold")
    table.add_column("Value", justify="right")

    eligible = summary.total - summary.errors
    pass_rate_pct = f"{summary.pass_rate * 100:.1f}%"
    color = "green" if summary.pass_rate >= 0.8 else "yellow" if summary.pass_rate >= 0.6 else "red"

    table.add_row("Total prompts", str(summary.total))
    table.add_row("Passed", f"[green]{summary.passed}[/green]")
    table.add_row("Failed", f"[red]{summary.failed}[/red]")
    table.add_row("Errors", str(summary.errors))
    table.add_row("Pass rate", f"[{color}]{pass_rate_pct}[/{color}]")

    console.print(table)
    console.print(f"\n[dim]Full results available at http://localhost:8002/dashboard (run main.py to start server)[/dim]")


if __name__ == "__main__":
    main()
