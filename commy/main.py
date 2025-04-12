"""
Main module for the commy tool.
Contains the Typer CLI interface.
"""

import sys

import typer
from rich.console import Console
from rich.panel import Panel

from .ai_utils import generate_commit_message
from .config_utils import load_config
from .git_utils import (
    commit_changes,
    get_staged_diff,
    get_staged_files,
    has_staged_changes,
    is_git_repository,
)

app = typer.Typer(help="AI-powered commit message generator")
console = Console()


@app.callback()
def callback():
    """
    Commy: AI-powered commit message generator.
    """
    pass


@app.command()
def generate(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show more details including the diff"
    ),
):
    """
    Generate a commit message for staged changes and prompt for commit action.
    """
    # Check if current directory is a Git repository
    if not is_git_repository():
        console.print(
            "[bold red]Error:[/bold red] Current directory is not a Git repository."
        )
        sys.exit(1)

    # Check if there are staged changes
    if not has_staged_changes():
        console.print(
            "[bold yellow]Warning:[/bold yellow] No staged changes to commit."
        )
        sys.exit(0)

    # Get staged files
    staged_files = get_staged_files()
    console.print(f"[bold green]Staged files:[/bold green] {', '.join(staged_files)}")

    # Get config
    config = load_config()
    truncate_length = config.get("diff_truncation_limit", 4000)

    # Get the diff
    try:
        diff, is_truncated = get_staged_diff(truncate_length)

        if verbose:
            console.print(Panel(diff, title="Git Diff", expand=False))

        if is_truncated:
            console.print(
                "[bold yellow]Warning:[/bold yellow] Diff was truncated due to size."
            )
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

    # Generate commit message
    with console.status("[bold green]Generating commit message...[/bold green]"):
        try:
            commit_message = generate_commit_message(diff)
        except Exception as e:
            console.print(
                f"[bold red]Error:[/bold red] Failed to generate commit message: {str(e)}"
            )
            sys.exit(1)

    # Display the generated message
    console.print("\n[bold]Generated commit message:[/bold]")
    console.print(Panel(commit_message, expand=False))

    # Ask for user action
    while True:
        choice = typer.prompt(
            "\nDo you want to [y]es commit, [r]egenerate message, or [n]o abort?",
            default="y",
        ).lower()

        if choice in ["y", "yes"]:
            # Commit changes
            if commit_changes(commit_message):
                console.print("[bold green]Commit successful![/bold green]")
            else:
                console.print("[bold red]Commit failed.[/bold red]")
            break
        elif choice in ["r", "regenerate"]:
            # Regenerate the commit message
            with console.status(
                "[bold green]Regenerating commit message...[/bold green]"
            ):
                try:
                    commit_message = generate_commit_message(diff)
                    console.print("\n[bold]Regenerated commit message:[/bold]")
                    console.print(Panel(commit_message, expand=False))
                except Exception as e:
                    console.print(
                        f"[bold red]Error:[/bold red] Failed to regenerate commit message: {str(e)}"
                    )
                    sys.exit(1)
        elif choice in ["n", "no"]:
            console.print(
                "[bold yellow]Aborted. No changes were committed.[/bold yellow]"
            )
            break
        else:
            console.print("[bold red]Invalid choice. Please try again.[/bold red]")


def main():
    """Entry point for the commy CLI."""
    app()


if __name__ == "__main__":
    main()
