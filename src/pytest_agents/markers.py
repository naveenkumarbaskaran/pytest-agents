"""Custom pytest markers for agent tests."""

from __future__ import annotations

MARKERS = [
    "agent: mark test as an agent test (for filtering with -m agent)",
    "max_tokens(n): fail if test exceeds n total tokens",
    "max_cost_usd(n): fail if test exceeds $n in LLM cost",
    "slow_agent: mark slow agent tests (skip with -m 'not slow_agent')",
]
