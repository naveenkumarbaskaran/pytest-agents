"""Tests for MockLLM."""

from pytest_agents.mock_llm import LLMResponse, MockLLM, ToolCall


def test_mock_llm_basic():
    mock = MockLLM()
    mock.add_response(LLMResponse(content="Hello!"))
    result = mock.complete("Hi")
    assert result.content == "Hello!"
    assert mock.call_count == 1


def test_mock_llm_multiple_responses():
    mock = MockLLM()
    mock.add_responses([
        LLMResponse(content="First"),
        LLMResponse(content="Second"),
    ])
    assert mock.complete("a").content == "First"
    assert mock.complete("b").content == "Second"
    assert mock.call_count == 2


def test_mock_llm_default_response():
    mock = MockLLM()
    mock.set_default_response(LLMResponse(content="Default"))
    assert mock.complete("anything").content == "Default"
    assert mock.complete("anything else").content == "Default"


def test_mock_llm_empty_raises():
    mock = MockLLM()
    try:
        mock.complete("test")
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "no responses queued" in str(e)


def test_mock_llm_tool_calls():
    mock = MockLLM()
    mock.add_response(LLMResponse(
        content="",
        tool_calls=[ToolCall(name="search", arguments={"query": "test"})],
    ))
    result = mock.complete("search for test")
    assert len(result.tool_calls) == 1
    assert result.tool_calls[0].name == "search"


def test_mock_llm_tokens():
    mock = MockLLM()
    resp = LLMResponse(content="Hi", tokens={"prompt": 10, "completion": 5})
    mock.add_response(resp)
    result = mock.complete("test")
    assert result.total_tokens == 15


def test_mock_llm_assert_called():
    mock = MockLLM()
    mock.set_default_response(LLMResponse(content="ok"))
    mock.complete("test")
    mock.assert_called()
    mock.assert_called_n_times(1)


def test_mock_llm_assert_message_contains():
    mock = MockLLM()
    mock.set_default_response(LLMResponse(content="ok"))
    mock.complete("What is the weather in Berlin?")
    mock.assert_last_message_contains("berlin")


def test_mock_llm_reset():
    mock = MockLLM()
    mock.add_response(LLMResponse(content="test"))
    mock.complete("a")
    mock.reset()
    assert mock.call_count == 0
