#!/usr/bin/env python3
"""Simulated pytest-agents demo for terminal recording."""
import time, sys, os

os.environ["TERM"] = "xterm-256color"

def c(code, text):
    return f"\033[{code}m{text}\033[0m"

def slow(text, delay=0.012):
    for ch in text:
        sys.stdout.write(ch); sys.stdout.flush(); time.sleep(delay)
    print()

print(c("1;35", """
  ██████╗ ██╗   ██╗████████╗███████╗███████╗████████╗
  ██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝
  ██████╔╝ ╚████╔╝    ██║   █████╗  ███████╗   ██║
  ██╔═══╝   ╚██╔╝     ██║   ██╔══╝  ╚════██║   ██║
  ██║        ██║      ██║   ███████╗███████║   ██║
  ╚═╝        ╚═╝      ╚═╝   ╚══════╝╚══════╝   ╚═╝
   █████╗  ██████╗ ███████╗███╗   ██╗████████╗███████╗
  ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔════╝
  ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ███████╗
  ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ╚════██║
  ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ███████║
  ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚══════╝"""))

time.sleep(0.2)
print(c("2", "  v0.1.0 • Pytest plugin for testing AI agents"))
time.sleep(0.4)

# Show test file
print(c("1;36", "\n  ─── test_weather_agent.py ───────────────────────────"))
time.sleep(0.2)

code_lines = [
    ('36', 'from'),  # placeholder
]

# Print code with syntax highlighting
code = """  import pytest
  from pytest_agents import mock_llm, AgentTracer

  def test_weather_agent_tool_calls():
      with mock_llm(responses=["Berlin weather: 22°C, sunny"]):
          tracer = AgentTracer()
          result = weather_agent.run("Weather in Berlin?")

          tracer.assert_tools_called(["geocode", "weather_api"])
          tracer.assert_no_hallucination(result)
          assert "22°C" in result"""

for line in code.split('\n'):
    # Simple syntax highlighting
    highlighted = line
    for kw in ['import', 'from', 'def', 'with', 'assert']:
        highlighted = highlighted.replace(f' {kw} ', f' {c("35", kw)} ')
        if highlighted.startswith(f'  {kw} '):
            highlighted = f'  {c("35", kw)} ' + highlighted[len(f'  {kw} '):]
    # Strings
    if '"' in highlighted:
        parts = highlighted.split('"')
        for i in range(1, len(parts), 2):
            if i < len(parts):
                parts[i] = c("32", f'"{parts[i]}"')[4:-4]
        highlighted = '"'.join(parts)
    print(c("37", highlighted))
    time.sleep(0.05)

time.sleep(0.4)

# Run pytest
print(c("1;36", "\n  ─── $ pytest test_weather_agent.py -v ─────────────"))
time.sleep(0.3)

print(c("1", "\n  ========================= test session starts ========================="))
print(c("2", "  platform darwin -- Python 3.12.0, pytest-8.3.2, pluggy-1.5.0"))
print(c("2", "  plugins: pytest-agents-0.1.0"))
print(c("1", "  collected 4 items\n"))
time.sleep(0.3)

tests = [
    ("test_weather_agent_tool_calls",     "PASSED",  "32", "0.02s"),
    ("test_mock_llm_returns_expected",    "PASSED",  "32", "0.01s"),
    ("test_token_budget_enforced",        "PASSED",  "32", "0.03s"),
    ("test_prompt_regression_check",      "FAILED",  "31", "0.04s"),
]

for name, status, color, dur in tests:
    prefix = "✓" if status == "PASSED" else "✗"
    sym = c(color, prefix)
    print(f"  {sym} {c('1',name):52s} {c(color, status)} {c('2',dur)}")
    time.sleep(0.25)

# Show failure detail
time.sleep(0.3)
print(c("1;31", "\n  ─── FAILURES ─────────────────────────────────────"))
print(c("31", "  test_prompt_regression_check"))
print(c("2",  "    Prompt fingerprint changed:"))
print(f"    {c('31','- Expected')}: sha256:a3f8c2...  (v1.2 baseline)")
print(f"    {c('32','+ Got')}:      sha256:7b1d4e...  (current)")
print(c("33", "    → Prompt was modified. Run: pytest --update-baselines"))
time.sleep(0.4)

# Token report
print(c("1;36", "\n  ─── Token & Cost Report ──────────────────────────"))
time.sleep(0.2)

print(f"  {c('1','Test'):42s} {c('1','Tokens'):>10s} {c('1','Cost'):>10s}")
print(f"  {'─'*42} {'─'*10} {'─'*10}")
data = [
    ("test_weather_agent_tool_calls",  "1,240",  "$0.006"),
    ("test_mock_llm_returns_expected",   "380",  "$0.002"),
    ("test_token_budget_enforced",     "2,100",  "$0.010"),
    ("test_prompt_regression_check",     "890",  "$0.004"),
]
for name, tok, cost in data:
    print(f"  {name:42s} {c('33',tok):>18s} {c('36',cost):>18s}")
    time.sleep(0.1)

print(f"\n  {c('1','Total')}: {c('1;33','4,610 tokens')} • {c('1;36','$0.022')} • {c('2','avg 1,153/test')}")

time.sleep(0.3)
print(c("1", "\n  ============ 3 passed, 1 failed in 0.42s ============"))
print(c("2", "  Mock LLM calls: 4 | Real LLM calls: 0 | Budget: within limits\n"))
time.sleep(1.0)
