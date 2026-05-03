"""Tests for LLM recorder (cassette)."""

import json
from pathlib import Path

from pytest_agents.mock_llm import LLMResponse, ToolCall
from pytest_agents.recorder import LLMCassette


def test_cassette_record_and_replay(tmp_path: Path):
    path = tmp_path / "test_cassette.json"

    # Record
    cassette = LLMCassette(path, mode="record")
    cassette.record_response(
        LLMResponse(content="Hello!", model="gpt-4o", tokens={"prompt": 10, "completion": 5})
    )
    cassette.record_response(LLMResponse(content="Goodbye!", model="gpt-4o"))
    cassette.save()

    assert path.exists()

    # Replay
    replay = LLMCassette(path, mode="replay")
    assert replay.response_count == 2
    assert replay.next_response().content == "Hello!"
    assert replay.next_response().content == "Goodbye!"


def test_cassette_with_tool_calls(tmp_path: Path):
    path = tmp_path / "tools.json"

    cassette = LLMCassette(path, mode="record")
    cassette.record_response(LLMResponse(
        content="",
        tool_calls=[ToolCall(name="search", arguments={"q": "test"}, id="call_1")],
    ))
    cassette.save()

    replay = LLMCassette(path, mode="replay")
    resp = replay.next_response()
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "search"
    assert resp.tool_calls[0].arguments == {"q": "test"}


def test_cassette_replay_exhausted(tmp_path: Path):
    path = tmp_path / "short.json"
    cassette = LLMCassette(path, mode="record")
    cassette.record_response(LLMResponse(content="only one"))
    cassette.save()

    replay = LLMCassette(path, mode="replay")
    replay.next_response()

    try:
        replay.next_response()
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "no more recorded" in str(e)


def test_cassette_reset(tmp_path: Path):
    path = tmp_path / "reset.json"
    cassette = LLMCassette(path, mode="record")
    cassette.record_response(LLMResponse(content="first"))
    cassette.save()

    replay = LLMCassette(path, mode="replay")
    replay.next_response()
    replay.reset()
    assert replay.next_response().content == "first"


def test_cassette_json_format(tmp_path: Path):
    path = tmp_path / "format.json"
    cassette = LLMCassette(path, mode="record")
    cassette.record_response(LLMResponse(content="test", model="gpt-4o"))
    cassette.save()

    data = json.loads(path.read_text())
    assert data["version"] == 1
    assert len(data["responses"]) == 1
    assert data["responses"][0]["content"] == "test"
