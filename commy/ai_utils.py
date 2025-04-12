"""
AI utilities for the commy tool.
Handles interaction with AI providers to generate commit messages.
"""

from abc import ABC, abstractmethod
from typing import Optional

import requests

from .config_utils import get_api_key, load_config


def create_commit_prompt(diff: str, commit_style: str = "conventional") -> str:
    """
    Create a prompt for the AI based on the diff content and desired commit style.

    Args:
        diff: The Git diff content.
        commit_style: The commit message style to use.

    Returns:
        A prompt string for the AI.
    """
    prompt_base = "Analyze the following Git diff and generate a concise, informative commit message that describes the changes:\n\n"
    prompt_base += f"{diff}\n\n"

    if commit_style == "conventional":
        prompt_base += (
            "Use the Conventional Commits format (type(scope): description).\n"
            "Choose the most appropriate type from: feat, fix, docs, style, refactor, perf, test, chore.\n"
            "Ensure the first line is no more than 72 characters.\n"
            "Commit message:"
        )
    else:
        prompt_base += (
            "Commit message (concise, present tense, less than 72 characters):"
        )

    return prompt_base


class AIProvider(ABC):
    """Base class for AI providers."""

    @abstractmethod
    def generate_commit_message(self, prompt: str) -> str:
        """Generate a commit message using the AI provider."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI implementation for generating commit messages."""

    def __init__(
        self,
        api_key: Optional[str] = "",
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 100,
    ):
        self.api_key = api_key or ""
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def generate_commit_message(self, prompt: str) -> str:
        """
        Generate a commit message using OpenAI's API.

        Args:
            prompt: The prompt to send to the API.

        Returns:
            The generated commit message.

        Raises:
            RuntimeError: If the API call fails.
        """
        if not self.api_key:
            raise RuntimeError(
                "OpenAI API key not found. Please set it in the configuration file "
                "at ~/.commy/config.yaml or set the COMMY_API_KEY environment variable."
            )

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            response = requests.post(
                self.api_url, headers=headers, json=data, timeout=30
            )
            response.raise_for_status()

            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except requests.RequestException as e:
            raise RuntimeError(f"Error calling OpenAI API: {str(e)}")


def get_ai_provider() -> AIProvider:
    """
    Factory function to create the appropriate AI provider based on configuration.

    Returns:
        An instance of AIProvider.
    """
    config = load_config()
    api_key = get_api_key()
    provider_name = config["ai"]["provider"].lower()

    if provider_name == "openai":
        return OpenAIProvider(
            api_key=api_key,
            model=config["ai"]["model"],
            temperature=config["ai"]["temperature"],
            max_tokens=config["ai"]["max_tokens"],
        )
    else:
        raise ValueError(f"Unsupported AI provider: {provider_name}")


def generate_commit_message(diff: str) -> str:
    """
    Generate a commit message for the given diff.

    Args:
        diff: The Git diff content.

    Returns:
        The generated commit message.
    """
    config = load_config()
    commit_style = config.get("commit_style", "conventional")

    # Create the prompt
    prompt = create_commit_prompt(diff, commit_style)

    # Get the AI provider and generate the message
    provider = get_ai_provider()
    return provider.generate_commit_message(prompt)
