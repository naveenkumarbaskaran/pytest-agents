"""Mock LLM for deterministic agent testing."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolCall:
    """Represents a tool/function call made by the LLM."""

    name: str
    arguments: dict[str, Any]
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = f"call_{int(time.time() * 1000)}"


@dataclass
class LLMResponse:
    """A canned LLM response for testing."""

    content: str = ""
    model: str = "mock-model"
    tool_calls: list[ToolCall] = field(default_factory=list)
    tokens: dict[str, int] = field(default_factory=lambda: {"prompt": 0, "completion": 0})
    finish_reason: str = "stop"
    latency_ms: float = 0.0

    @property
    def total_tokens(self) -> int:
        return self.tokens.get("prompt", 0) + self.tokens.get("completion", 0)


class MockLLM:
    """Queue-based LLM mock for deterministic testing.

    Usage:
        mock = MockLLM()
        mock.add_response(LLMResponse(content="Hello!"))
        result = mock.complete("Hi there")
        assert result.content == "Hello!"
    """

    def __init__(self) -> None:
        self._responses: list[LLMResponse] = []
        self._calls: list[dict[str, Any]] = []
        self._default_response: LLMResponse | None = None

    def add_response(self, response: LLMResponse) -> None:
        """Queue a response to return on the next call."""
        self._responses.append(response)

    def add_responses(self, responses: list[LLMResponse]) -> None:
        """Queue multiple responses."""
        self._responses.extend(responses)

    def set_default_response(self, response: LLMResponse) -> None:
        """Set a fallback response when queue is empty."""
        self._default_response = response

    def complete(
        self,
        messages: str | list[dict[str, Any]],
        **kwargs: Any,
    ) -> LLMResponse:
        """Simulate an LLM completion call."""
        # Normalize messages
        if isinstance(messages, str):
            messages = [{"role": "user", "content": messages}]

        self._calls.append({
            "messages": messages,
            "kwargs": kwargs,
            "timestamp": time.time(),
        })

        if self._responses:
            return self._responses.pop(0)

        if self._default_response:
            return self._default_response

        raise RuntimeError(
            f"MockLLM: no responses queued and no default set. "
            f"Call #{len(self._calls)} with: {messages[-1] if messages else '(empty)'}"
        )

    @property
    def call_count(self) -> int:
        return len(self._calls)

    @property
    def calls(self) -> list[dict[str, Any]]:
        return list(self._calls)

    @property
    def last_call(self) -> dict[str, Any] | None:
        return self._calls[-1] if self._calls else None

    @property
    def total_tokens(self) -> int:
        """Total tokens across all (returned) responses — estimated from calls."""
        return 0  # Token tracking is in TokenTracker

    def reset(self) -> None:
        """Clear all responses and call history."""
        self._responses.clear()
        self._calls.clear()
        self._default_response = None

    def assert_called(self) -> None:
        """Assert that at least one call was made."""
        assert self.call_count > 0, "Expected MockLLM to be called, but it wasn't"

    def assert_called_n_times(self, n: int) -> None:
        """Assert exact number of calls."""
        assert self.call_count == n, (
            f"Expected MockLLM to be called {n} times, got {self.call_count}"
        )

    def assert_last_message_contains(self, text: str) -> None:
        """Assert last user message contains given text."""
        assert self.last_call is not None, "No calls recorded"
        messages = self.last_call["messages"]
        last_content = messages[-1].get("content", "") if messages else ""
        assert text.lower() in last_content.lower(), (
            f"Expected '{text}' in last message, got: {last_content[:200]}"
        )
