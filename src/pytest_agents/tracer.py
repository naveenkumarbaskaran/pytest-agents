"""Agent tool call tracer — records and asserts tool usage patterns."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Any, Generator


@dataclass
class ToolInvocation:
    """A single recorded tool invocation."""

    name: str
    arguments: dict[str, Any]
    result: Any = None
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)
    error: str | None = None


class AgentTracer:
    """Traces tool calls made by an agent during execution.

    Usage:
        tracer = AgentTracer()
        with tracer.trace():
            agent.run("query")
        tracer.assert_tools_called(["search", "summarize"])
    """

    def __init__(self) -> None:
        self._invocations: list[ToolInvocation] = []
        self._active = False

    @contextmanager
    def trace(self) -> Generator[AgentTracer, None, None]:
        """Context manager to enable tracing."""
        self._active = True
        self._invocations.clear()
        try:
            yield self
        finally:
            self._active = False

    def record(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
        result: Any = None,
        duration_ms: float = 0.0,
        error: str | None = None,
    ) -> None:
        """Record a tool invocation (call from your agent's tool wrapper)."""
        if not self._active:
            return
        self._invocations.append(ToolInvocation(
            name=name,
            arguments=arguments or {},
            result=result,
            duration_ms=duration_ms,
            error=error,
        ))

    @property
    def tool_names(self) -> list[str]:
        """Names of all tools called, in order."""
        return [inv.name for inv in self._invocations]

    @property
    def tool_count(self) -> int:
        return len(self._invocations)

    @property
    def invocations(self) -> list[ToolInvocation]:
        return list(self._invocations)

    @property
    def errors(self) -> list[ToolInvocation]:
        """Return only invocations that had errors."""
        return [inv for inv in self._invocations if inv.error]

    def get_calls(self, tool_name: str) -> list[ToolInvocation]:
        """Get all invocations of a specific tool."""
        return [inv for inv in self._invocations if inv.name == tool_name]

    # ─── Assertions ─────────────────────────────────────────────

    def assert_tools_called(self, expected: list[str]) -> None:
        """Assert tool call sequence matches exactly."""
        actual = self.tool_names
        assert actual == expected, (
            f"Expected tool sequence {expected}, got {actual}"
        )

    def assert_tools_called_any_order(self, expected: list[str]) -> None:
        """Assert all expected tools were called (order doesn't matter)."""
        actual = set(self.tool_names)
        expected_set = set(expected)
        missing = expected_set - actual
        assert not missing, (
            f"Expected tools {missing} were not called. Called: {sorted(actual)}"
        )

    def assert_tool_called(self, name: str, times: int | None = None) -> None:
        """Assert a specific tool was called (optionally N times)."""
        calls = self.get_calls(name)
        assert len(calls) > 0, (
            f"Expected tool '{name}' to be called, but it wasn't. "
            f"Called: {self.tool_names}"
        )
        if times is not None:
            assert len(calls) == times, (
                f"Expected '{name}' called {times} times, got {len(calls)}"
            )

    def assert_tool_not_called(self, name: str) -> None:
        """Assert a tool was NOT called."""
        calls = self.get_calls(name)
        assert len(calls) == 0, (
            f"Expected '{name}' not to be called, but it was called {len(calls)} times"
        )

    def assert_tool_called_with(self, name: str, **expected_args: Any) -> None:
        """Assert a tool was called with specific arguments."""
        calls = self.get_calls(name)
        assert calls, f"Tool '{name}' was never called"

        for call in calls:
            match = all(
                call.arguments.get(k) == v
                for k, v in expected_args.items()
            )
            if match:
                return

        # No matching call found
        actual_args = [c.arguments for c in calls]
        raise AssertionError(
            f"Tool '{name}' was never called with {expected_args}. "
            f"Actual calls: {actual_args}"
        )

    def assert_tool_called_before(self, first: str, second: str) -> None:
        """Assert tool 'first' was called before tool 'second'."""
        names = self.tool_names
        assert first in names, f"Tool '{first}' was never called"
        assert second in names, f"Tool '{second}' was never called"
        assert names.index(first) < names.index(second), (
            f"Expected '{first}' before '{second}', but order was: {names}"
        )

    def assert_no_errors(self) -> None:
        """Assert no tool calls resulted in errors."""
        errors = self.errors
        assert not errors, (
            f"{len(errors)} tool call(s) had errors: "
            + ", ".join(f"{e.name}: {e.error}" for e in errors)
        )

    def assert_max_calls(self, n: int) -> None:
        """Assert total tool calls don't exceed n."""
        assert self.tool_count <= n, (
            f"Expected at most {n} tool calls, got {self.tool_count}: {self.tool_names}"
        )
