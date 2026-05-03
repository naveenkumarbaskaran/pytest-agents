"""Pytest plugin entry point — fixtures, hooks, CLI options."""

from __future__ import annotations

import pytest

from pytest_agents.markers import MARKERS
from pytest_agents.mock_llm import MockLLM
from pytest_agents.tokens import TokenTracker
from pytest_agents.tracer import AgentTracer

# ─── Registration ───────────────────────────────────────────────

def pytest_configure(config: pytest.Config) -> None:
    """Register markers and CLI options."""
    for marker in MARKERS:
        config.addinivalue_line("markers", marker)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add CLI options."""
    group = parser.getgroup("agents", "Agent testing options")
    group.addoption(
        "--agent-report",
        action="store_true",
        default=False,
        help="Print token/cost summary after test run",
    )
    group.addoption(
        "--snapshot-update",
        action="store_true",
        default=False,
        help="Update prompt snapshots instead of checking them",
    )


# ─── Fixtures ───────────────────────────────────────────────────

@pytest.fixture
def mock_llm() -> MockLLM:
    """Provides a fresh MockLLM instance per test."""
    return MockLLM()


@pytest.fixture
def agent_tracer() -> AgentTracer:
    """Provides a fresh AgentTracer per test."""
    return AgentTracer()


@pytest.fixture
def token_tracker() -> TokenTracker:
    """Provides a fresh TokenTracker per test."""
    return TokenTracker()


# ─── Token/Cost Budget Enforcement ─────────────────────────────

# Store per-test trackers for reporting
_test_trackers: dict[str, TokenTracker] = {}


@pytest.fixture(autouse=True)
def _agent_budget_check(request: pytest.FixtureRequest) -> None:  # type: ignore[misc]
    """Auto-check token/cost budgets after each test."""
    tracker = TokenTracker()
    _test_trackers[request.node.nodeid] = tracker

    yield  # type: ignore[misc]

    # Check @pytest.mark.max_tokens
    max_tokens_marker = request.node.get_closest_marker("max_tokens")
    if max_tokens_marker and max_tokens_marker.args:
        max_tokens = max_tokens_marker.args[0]
        tracker.assert_under_tokens(max_tokens)

    # Check @pytest.mark.max_cost_usd
    max_cost_marker = request.node.get_closest_marker("max_cost_usd")
    if max_cost_marker and max_cost_marker.args:
        max_cost = max_cost_marker.args[0]
        tracker.assert_under_cost(max_cost)


# ─── Session Report ─────────────────────────────────────────────

def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter,
    exitstatus: int,
    config: pytest.Config,
) -> None:
    """Print agent token/cost summary if --agent-report is set."""
    if not config.getoption("--agent-report", default=False):
        return

    total_tokens = sum(t.total_tokens for t in _test_trackers.values())
    total_cost = sum(t.total_cost_usd for t in _test_trackers.values())
    total_calls = sum(t.call_count for t in _test_trackers.values())

    terminalreporter.section("Agent Test Report")
    terminalreporter.line(f"Tests with tracking: {len(_test_trackers)}")
    terminalreporter.line(f"Total LLM calls:     {total_calls}")
    terminalreporter.line(f"Total tokens:        {total_tokens:,}")
    terminalreporter.line(f"Estimated cost:      ${total_cost:.4f}")
