# Commy

Commy is an AI-powered commit message generator that automatically generates high-quality commit messages based on the content of staged files in a Git repository.

## Features

- Automatically generates commit messages based on staged changes
- Uses AI to analyze diffs and create meaningful commit messages
- Supports Conventional Commits format
- User-friendly CLI with color output
- Configurable through a YAML configuration file

## Installation

### From PyPI (recommended)

```bash
pip install commy
```

### From Source

```bash
git clone https://github.com/username/commy.git
cd commy
pip install -e .
```

## Configuration

Commy looks for a configuration file at `~/.commy/config.yaml`. If it doesn't exist, a default one will be created on first run.

Example configuration:

```yaml
ai:
  provider: openai
  model: gpt-3.5-turbo
  temperature: 0.7
  max_tokens: 100
  api_key: your_openai_api_key_here
commit_style: conventional
diff_truncation_limit: 4000
```

You can also set your API key via the environment variable `COMMY_API_KEY`:

```bash
export COMMY_API_KEY=your_openai_api_key_here
```

## Usage

1. Stage your changes using `git add`
2. Run `commy` to generate a commit message
3. Choose whether to accept, regenerate, or reject the message

```bash
# Basic usage
commy

# Show the diff along with the generated message
commy --verbose
```

## Security Note

This tool sends your code diffs to an external AI service (OpenAI by default). Please be cautious and review your diffs to ensure no sensitive information is being sent. This is especially important for projects with secrets, credentials, or proprietary code.

## License

GPL-3.0
