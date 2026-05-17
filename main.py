#!/usr/bin/env python3
"""
Agentic Plugin — Main CLI Entry Point

Commands:
    agentic init                                       → Install plugin into current repo
    agentic run --prd path/to/prd.md                   → Full pipeline (PRD → Tickets → Code → PR)
    agentic run --prd path/to/dev-doc.md --mode direct → Direct pipeline (Doc → Code → PR)

The plugin reads ALL configuration from the target repo's .agentic/ directory.
No config lives inside the plugin itself — it's fully agnostic.
"""

import argparse
import os
import sys

from rich.console import Console
from rich.panel import Panel

console = Console()


def cmd_init(args):
    """Handle the 'init' subcommand."""
    from core.init_command import init_agentic

    repo_path = args.repo or os.getcwd()
    init_agentic(repo_path)


def cmd_run(args):
    """Handle the 'run' subcommand."""
    from config import resolve_config, validate_config
    from core.orchestrator import Orchestrator

    repo_path = args.repo or os.getcwd()

    # Banner
    console.print(
        Panel(
            "[bold cyan]🤖 Agentic Plugin[/bold cyan]\n"
            "[dim]From PRD to Pull Request — powered by AI agents[/dim]",
            style="bold",
            padding=(1, 4),
        )
    )

    # Resolve config from the target repo
    config = resolve_config(repo_path)

    # Validate
    errors = validate_config(config)
    if errors:
        console.print("[bold red]❌ Configuration Errors:[/bold red]")
        for err in errors:
            console.print(f"  • {err}")
        console.print(
            "\n[dim]Run 'agentic init' first, then fill in .agentic/config.yaml[/dim]"
        )
        sys.exit(1)

    mode = args.mode

    # Display resolved config
    dev_model = config.models.get("developer")
    mode_label = (
        "Full (PRD → Tickets → Code → PR)"
        if mode == "full"
        else "Direct (Doc → Code → PR)"
    )
    console.print(f"  📄 Document:      {args.prd}")
    console.print(f"  🔀 Mode:          {mode_label}")
    console.print(f"  📁 Repo:          {repo_path}")
    console.print(f"  🐙 GitHub Repo:   {config.github_repo}")
    console.print(
        f"  💻 Developer LLM: {dev_model.provider}/{dev_model.model}"
        if dev_model
        else ""
    )
    console.print(f"  🔁 Max Iterations: {config.max_ralph_iterations}")
    console.print()

    # Run the pipeline
    try:
        orchestrator = Orchestrator(prd_path=args.prd, config=config)
        if mode == "direct":
            orchestrator.run_direct_pipeline()
        else:
            orchestrator.run_full_pipeline()
    except FileNotFoundError as e:
        console.print(f"[red]ERROR: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user. Exiting...[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[red]UNEXPECTED ERROR: {e}[/red]")
        raise


def main():
    parser = argparse.ArgumentParser(
        prog="agentic",
        description="🤖 Agentic Plugin: Turn PRDs into Pull Requests",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- agentic init ---
    init_parser = subparsers.add_parser(
        "init",
        help="Initialize the .agentic/ config directory in a repo",
    )
    init_parser.add_argument(
        "--repo",
        default=None,
        help="Path to the repo (default: current directory)",
    )

    # --- agentic run ---
    run_parser = subparsers.add_parser(
        "run",
        help="Run the full pipeline: PRD → Tickets → Code → Tests → PR",
    )
    run_parser.add_argument(
        "--prd",
        required=True,
        help="Path to the PRD/SRD/Dev document (Markdown or PDF)",
    )
    run_parser.add_argument(
        "--repo",
        default=None,
        help="Path to the target repo (default: current directory)",
    )
    run_parser.add_argument(
        "--mode",
        choices=["full", "direct"],
        default="full",
        help=(
            "Pipeline mode. "
            "'full': PRD → Create Tickets → Code → Tests → PR (default). "
            "'direct': Dev Doc → Code → Tests → PR (skip ticket creation)."
        ),
    )

    args = parser.parse_args()

    if args.command == "init":
        cmd_init(args)
    elif args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
