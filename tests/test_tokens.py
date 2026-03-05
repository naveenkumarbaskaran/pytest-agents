"""Tests for TokenTracker."""

from pytest_agents.tokens import TokenTracker, TokenUsage


def test_token_usage_basic():
    usage = TokenUsage(prompt_tokens=100, completion_tokens=50, model="gpt-4o-mini")
    assert usage.total_tokens == 150
    assert usage.cost_usd > 0


def test_token_tracker_record():
    tracker = TokenTracker()
    tracker.record(prompt_tokens=100, completion_tokens=50, model="gpt-4o")
    tracker.record(prompt_tokens=200, completion_tokens=80, model="gpt-4o")

    assert tracker.total_prompt_tokens == 300
    assert tracker.total_completion_tokens == 130
    assert tracker.total_tokens == 430
    assert tracker.call_count == 2


def test_token_tracker_cost():
    tracker = TokenTracker()
    tracker.record(prompt_tokens=1_000_000, completion_tokens=0, model="gpt-4o")
    # gpt-4o prompt is $2.50/1M → should be $2.50
    assert abs(tracker.total_cost_usd - 2.50) < 0.01


def test_token_tracker_assert_under():
    tracker = TokenTracker()
    tracker.record(prompt_tokens=100, completion_tokens=50)
    tracker.assert_under_tokens(5000)


def test_token_tracker_assert_over_fails():
    tracker = TokenTracker()
    tracker.record(prompt_tokens=3000, completion_tokens=3000)
    try:
        tracker.assert_under_tokens(5000)
        assert False, "Should have raised"
    except AssertionError:
        pass


def test_token_tracker_summary():
    tracker = TokenTracker()
    tracker.record(prompt_tokens=100, completion_tokens=50, model="gpt-4o")
    summary = tracker.summary()
    assert summary["calls"] == 1
    assert summary["total_tokens"] == 150
    assert "cost_usd" in summary


def test_token_tracker_reset():
    tracker = TokenTracker()
    tracker.record(prompt_tokens=100, completion_tokens=50)
    tracker.reset()
    assert tracker.total_tokens == 0
    assert tracker.call_count == 0
