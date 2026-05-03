"""Tests for AgentTracer."""

import pytest

from pytest_agents.tracer import AgentTracer


def test_tracer_basic():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("search", {"query": "test"})
        tracer.record("summarize", {"text": "result"})

    assert tracer.tool_names == ["search", "summarize"]
    assert tracer.tool_count == 2


def test_tracer_assert_tools_called():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("search", {"q": "a"})
        tracer.record("fetch", {"url": "b"})

    tracer.assert_tools_called(["search", "fetch"])


def test_tracer_assert_tools_called_any_order():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("fetch", {})
        tracer.record("search", {})

    tracer.assert_tools_called_any_order(["search", "fetch"])


def test_tracer_assert_tool_called_with():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("geocode", {"city": "Berlin"})
        tracer.record("weather", {"lat": 52.5, "lon": 13.4})

    tracer.assert_tool_called_with("geocode", city="Berlin")
    tracer.assert_tool_called_with("weather", lat=52.5)


def test_tracer_assert_tool_not_called():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("search", {})

    tracer.assert_tool_not_called("delete")


def test_tracer_assert_order():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("search", {})
        tracer.record("summarize", {})

    tracer.assert_tool_called_before("search", "summarize")


def test_tracer_assert_no_errors():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("search", {}, result="ok")

    tracer.assert_no_errors()


def test_tracer_detects_errors():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("search", {}, error="timeout")

    assert len(tracer.errors) == 1
    with pytest.raises(AssertionError, match="tool call.*had errors"):
        tracer.assert_no_errors()


def test_tracer_max_calls():
    tracer = AgentTracer()
    with tracer.trace():
        tracer.record("a", {})
        tracer.record("b", {})

    tracer.assert_max_calls(5)
    with pytest.raises(AssertionError, match="at most 1"):
        tracer.assert_max_calls(1)


def test_tracer_inactive_ignores():
    tracer = AgentTracer()
    tracer.record("should_ignore", {})
    assert tracer.tool_count == 0
