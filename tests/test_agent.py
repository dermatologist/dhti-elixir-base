import pytest


@pytest.fixture(scope="session")
def agent():
    from src.dhti_elixir_base import BaseAgent

    return BaseAgent()


def test_agent_invoke(agent, capsys):
    input_data = {"input": "Answer in one word: What is the capital of France?"}
    _agent = agent.get_agent()
    result = _agent.invoke(input=input_data)
    print(result)
    captured = capsys.readouterr()
    assert "Paris" in captured.out


def test_base_agent(agent, capsys):
    o = agent.name
    print("Agent name: ", o)
    captured = capsys.readouterr()
    assert "Agent name:  base_agent" in captured.out
