"""Token counting and cost tracking for agent tests."""

from __future__ import annotations

from dataclasses import dataclass, field

# Pricing per 1M tokens (approximate, as of 2026)
MODEL_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4-turbo": {"prompt": 10.00, "completion": 30.00},
    "gpt-3.5-turbo": {"prompt": 0.50, "completion": 1.50},
    "claude-3-5-sonnet": {"prompt": 3.00, "completion": 15.00},
    "claude-3-haiku": {"prompt": 0.25, "completion": 1.25},
    "claude-3-opus": {"prompt": 15.00, "completion": 75.00},
    "claude-sonnet-4": {"prompt": 3.00, "completion": 15.00},
    "claude-opus-4": {"prompt": 15.00, "completion": 75.00},
}


@dataclass
class TokenUsage:
    """Token usage for a single LLM call."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = "gpt-4o-mini"

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    @property
    def cost_usd(self) -> float:
        """Estimated cost in USD."""
        pricing = MODEL_PRICING.get(self.model, {"prompt": 1.0, "completion": 3.0})
        prompt_cost = (self.prompt_tokens / 1_000_000) * pricing["prompt"]
        completion_cost = (self.completion_tokens / 1_000_000) * pricing["completion"]
        return prompt_cost + completion_cost


@dataclass
class TokenTracker:
    """Tracks token usage across multiple LLM calls within a test.

    Usage:
        tracker = TokenTracker()
        tracker.record(prompt_tokens=100, completion_tokens=50, model="gpt-4o")
        tracker.record(prompt_tokens=200, completion_tokens=80, model="gpt-4o")
        assert tracker.total_tokens < 5000
        assert tracker.total_cost_usd < 0.01
    """

    usages: list[TokenUsage] = field(default_factory=list)

    def record(
        self,
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        model: str = "gpt-4o-mini",
    ) -> None:
        """Record token usage from an LLM call."""
        self.usages.append(TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model=model,
        ))

    @property
    def total_prompt_tokens(self) -> int:
        return sum(u.prompt_tokens for u in self.usages)

    @property
    def total_completion_tokens(self) -> int:
        return sum(u.completion_tokens for u in self.usages)

    @property
    def total_tokens(self) -> int:
        return sum(u.total_tokens for u in self.usages)

    @property
    def total_cost_usd(self) -> float:
        return sum(u.cost_usd for u in self.usages)

    @property
    def call_count(self) -> int:
        return len(self.usages)

    def summary(self) -> dict[str, object]:
        """Return a summary dict for reporting."""
        return {
            "calls": self.call_count,
            "prompt_tokens": self.total_prompt_tokens,
            "completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_tokens,
            "cost_usd": round(self.total_cost_usd, 6),
        }

    def reset(self) -> None:
        """Clear all recorded usages."""
        self.usages.clear()

    # ─── Assertions ─────────────────────────────────────────────

    def assert_under_tokens(self, max_tokens: int) -> None:
        """Assert total tokens are under the limit."""
        assert self.total_tokens <= max_tokens, (
            f"Token budget exceeded: {self.total_tokens} > {max_tokens}"
        )

    def assert_under_cost(self, max_usd: float) -> None:
        """Assert total cost is under the limit."""
        assert self.total_cost_usd <= max_usd, (
            f"Cost budget exceeded: ${self.total_cost_usd:.4f} > ${max_usd:.4f}"
        )

    def assert_max_calls(self, n: int) -> None:
        """Assert number of LLM calls doesn't exceed n."""
        assert self.call_count <= n, (
            f"Too many LLM calls: {self.call_count} > {n}"
        )
