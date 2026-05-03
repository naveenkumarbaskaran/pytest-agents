"""Prompt snapshot regression testing."""

from __future__ import annotations

import functools
import hashlib
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

# Default snapshot directory
SNAPSHOT_DIR = Path(".snapshots")


def _hash_prompt(text: str) -> str:
    """Create a stable hash of prompt text."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


class PromptSnapshot:
    """Manages prompt snapshots for regression testing.

    Stores prompt text + hash. On subsequent runs, detects if the
    prompt has changed and fails the test (unless --snapshot-update).
    """

    def __init__(self, snapshot_dir: Path | None = None) -> None:
        self.snapshot_dir = snapshot_dir or SNAPSHOT_DIR

    def _path(self, name: str) -> Path:
        return self.snapshot_dir / f"{name}.json"

    def save(self, name: str, prompt_text: str) -> None:
        """Save a prompt snapshot."""
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)
        data = {
            "name": name,
            "hash": _hash_prompt(prompt_text),
            "text": prompt_text,
            "version": 1,
        }
        self._path(name).write_text(json.dumps(data, indent=2))

    def check(self, name: str, prompt_text: str) -> tuple[bool, str]:
        """Check if prompt matches snapshot.

        Returns:
            (matches, message)
        """
        path = self._path(name)
        if not path.exists():
            return False, f"No snapshot found for '{name}'. Run with --snapshot-update to create."

        data = json.loads(path.read_text())
        saved_hash = data.get("hash", "")
        current_hash = _hash_prompt(prompt_text)

        if saved_hash == current_hash:
            return True, "Prompt matches snapshot."

        saved_text = data.get("text", "")
        return False, (
            f"Prompt '{name}' has changed!\n"
            f"  Saved hash:   {saved_hash}\n"
            f"  Current hash: {current_hash}\n"
            f"  Run with --snapshot-update to accept the new version.\n"
            f"  --- Saved ---\n{saved_text[:500]}\n"
            f"  --- Current ---\n{prompt_text[:500]}"
        )


# Global snapshot manager (overridable in plugin)
_snapshot_manager = PromptSnapshot()


def prompt_snapshot(name: str) -> Callable[..., Any]:
    """Decorator: regression-test a prompt for unexpected changes.

    The decorated function should return the prompt text.

    Usage:
        @prompt_snapshot("my_system_prompt")
        def test_system_prompt():
            return agent.system_prompt

    First run: creates snapshot. Subsequent runs: fails if prompt changed.
    Use --snapshot-update to accept changes.
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            prompt_text = func(*args, **kwargs)
            if not isinstance(prompt_text, str):
                raise TypeError(
                    f"@prompt_snapshot function must return str, got {type(prompt_text).__name__}"
                )

            # Check if --snapshot-update mode (set by plugin)
            update_mode = kwargs.pop("_snapshot_update", False)
            if update_mode:
                _snapshot_manager.save(name, prompt_text)
                return prompt_text

            matches, message = _snapshot_manager.check(name, prompt_text)
            if not matches:
                # If no snapshot exists yet, create it
                if "No snapshot found" in message:
                    _snapshot_manager.save(name, prompt_text)
                    return prompt_text
                raise AssertionError(message)

            return prompt_text
        return wrapper
    return decorator
