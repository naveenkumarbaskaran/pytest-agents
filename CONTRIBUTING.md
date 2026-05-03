# Contributing to pytest-agents

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/naveenkumarbaskaran/pytest-agents.git
cd pytest-agents
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

This project uses [ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
ruff check .
ruff format .
```

## Making Changes

1. Fork the repo and create a feature branch from `main`
2. Make your changes with clear, descriptive commits
3. Add or update tests for any new functionality
4. Ensure all tests pass and linting is clean
5. Open a pull request against `main`

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add new assertion helper`
- `fix: handle empty response queue`
- `test: add edge case for token budget`
- `docs: update README examples`

## Adding New Features

- **New fixtures** → add to `plugin.py` and export in `__init__.py`
- **New assertion helpers** → add to the relevant module (tracer, tokens, etc.)
- **New markers** → register in `markers.py` and document in README

## Reporting Issues

- Use GitHub Issues with a clear title and reproduction steps
- Include your Python version and pytest version
- Attach minimal code that reproduces the problem

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
