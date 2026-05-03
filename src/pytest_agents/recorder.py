"""Record and replay LLM calls — VCR-style cassettes for agents."""

from __future__ import annotations

import functools
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pytest_agents.mock_llm import LLMResponse, ToolCall


def _serialize_response(resp: LLMResponse) -> dict[str, Any]:
    """Serialize an LLMResponse to JSON-safe dict."""
    return {
        "content": resp.content,
        "model": resp.model,
        "tool_calls": [
            {"name": tc.name, "arguments": tc.arguments, "id": tc.id}
            for tc in resp.tool_calls
        ],
        "tokens": resp.tokens,
        "finish_reason": resp.finish_reason,
    }


def _deserialize_response(data: dict[str, Any]) -> LLMResponse:
    """Deserialize a dict back to LLMResponse."""
    return LLMResponse(
        content=data.get("content", ""),
        model=data.get("model", "mock-model"),
        tool_calls=[
            ToolCall(name=tc["name"], arguments=tc["arguments"], id=tc.get("id", ""))
            for tc in data.get("tool_calls", [])
        ],
        tokens=data.get("tokens", {"prompt": 0, "completion": 0}),
        finish_reason=data.get("finish_reason", "stop"),
    )


class LLMCassette:
    """Records and replays LLM interactions to/from a JSON file.

    Usage (record mode):
        cassette = LLMCassette("fixtures/test_greeting.json", mode="record")
        # ... run agent, cassette.record_response() on each LLM call ...
        cassette.save()

    Usage (replay mode):
        cassette = LLMCassette("fixtures/test_greeting.json", mode="replay")
        response = cassette.next_response()  # Returns recorded responses in order
    """

    def __init__(self, path: str | Path, mode: str = "replay") -> None:
        self.path = Path(path)
        self.mode = mode
        self._responses: list[LLMResponse] = []
        self._replay_index = 0

        if mode == "replay" and self.path.exists():
            self._load()

    def _load(self) -> None:
        """Load recorded responses from file."""
        data = json.loads(self.path.read_text())
        self._responses = [_deserialize_response(r) for r in data["responses"]]

    def save(self) -> None:
        """Save recorded responses to file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": 1,
            "responses": [_serialize_response(r) for r in self._responses],
        }
        self.path.write_text(json.dumps(data, indent=2))

    def record_response(self, response: LLMResponse) -> None:
        """Record a response (record mode)."""
        self._responses.append(response)

    def next_response(self) -> LLMResponse:
        """Get next recorded response (replay mode)."""
        if self._replay_index >= len(self._responses):
            raise RuntimeError(
                f"LLMCassette: no more recorded responses. "
                f"Replayed {self._replay_index}/{len(self._responses)}. "
                f"Re-record with mode='record'."
            )
        resp = self._responses[self._replay_index]
        self._replay_index += 1
        return resp

    @property
    def response_count(self) -> int:
        return len(self._responses)

    def reset(self) -> None:
        """Reset replay index to beginning."""
        self._replay_index = 0


def record_llm(path: str) -> Callable[..., Any]:
    """Decorator: record LLM calls to a cassette file.

    Usage:
        @record_llm("fixtures/test_greeting.json")
        def test_greeting():
            result = agent.run("Hello")
            assert "hello" in result.lower()
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cassette = LLMCassette(path, mode="record")
            kwargs["_cassette"] = cassette
            try:
                result = func(*args, **kwargs)
            finally:
                cassette.save()
            return result
        return wrapper
    return decorator


def replay_llm(path: str) -> Callable[..., Any]:
    """Decorator: replay LLM calls from a cassette file.

    Usage:
        @replay_llm("fixtures/test_greeting.json")
        def test_greeting():
            result = agent.run("Hello")
            assert "hello" in result.lower()
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            cassette = LLMCassette(path, mode="replay")
            kwargs["_cassette"] = cassette
            return func(*args, **kwargs)
        return wrapper
    return decorator
