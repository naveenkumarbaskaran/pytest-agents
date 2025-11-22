"""pytest-agents — Pytest plugin for testing AI agents."""

from pytest_agents.mock_llm import LLMResponse, MockLLM
from pytest_agents.tracer import AgentTracer
from pytest_agents.tokens import TokenTracker
from pytest_agents.recorder import record_llm, replay_llm
from pytest_agents.snapshot import prompt_snapshot

__version__ = "0.1.0"
__all__ = [
    "LLMResponse",
    "MockLLM",
    "AgentTracer",
    "TokenTracker",
    "record_llm",
    "replay_llm",
    "prompt_snapshot",
]
