"""Tests for prompt snapshot."""

from pathlib import Path

from pytest_agents.snapshot import PromptSnapshot


def test_snapshot_save_and_check(tmp_path: Path):
    manager = PromptSnapshot(snapshot_dir=tmp_path)
    manager.save("test_prompt", "You are a helpful assistant.")

    matches, msg = manager.check("test_prompt", "You are a helpful assistant.")
    assert matches is True


def test_snapshot_detects_change(tmp_path: Path):
    manager = PromptSnapshot(snapshot_dir=tmp_path)
    manager.save("test_prompt", "Original prompt text")

    matches, msg = manager.check("test_prompt", "Modified prompt text!")
    assert matches is False
    assert "has changed" in msg


def test_snapshot_missing(tmp_path: Path):
    manager = PromptSnapshot(snapshot_dir=tmp_path)
    matches, msg = manager.check("nonexistent", "some text")
    assert matches is False
    assert "No snapshot found" in msg


def test_snapshot_file_created(tmp_path: Path):
    manager = PromptSnapshot(snapshot_dir=tmp_path)
    manager.save("my_prompt", "test content")
    assert (tmp_path / "my_prompt.json").exists()
