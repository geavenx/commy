"""
Git utilities for the commy tool.
Provides functions to interact with Git repositories.
"""

import subprocess
from typing import Optional, Tuple


def is_git_repository() -> bool:
    """Check if the current directory is a Git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except FileNotFoundError:
        return False


def has_staged_changes() -> bool:
    """Check if there are any staged changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return bool(result.stdout.strip())
    except subprocess.CalledProcessError:
        return False


def get_staged_diff(truncate_length: Optional[int] = None) -> Tuple[str, bool]:
    """
    Get the diff of staged changes.

    Args:
        truncate_length: Maximum length of the diff in characters.
                         If None, no truncation is performed.

    Returns:
        A tuple containing (diff_content, is_truncated)
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--cached"], capture_output=True, text=True, check=True
        )
        diff = result.stdout

        if truncate_length and len(diff) > truncate_length:
            return diff[
                :truncate_length
            ] + "\n[... diff truncated due to size ...]", True

        return diff, False
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get staged diff: {e.stderr}")


def get_staged_files() -> list:
    """Get a list of staged files."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line for line in result.stdout.splitlines() if line]
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to get staged files: {e.stderr}")


def commit_changes(message: str) -> bool:
    """
    Commit the staged changes with the given message.

    Args:
        message: The commit message to use.

    Returns:
        True if the commit was successful, False otherwise.
    """
    try:
        # Escape double quotes in the message
        safe_message = message.replace('"', '\\"')

        result = subprocess.run(
            ["git", "commit", "-m", safe_message],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Commit failed: {e.stderr}")
        return False
