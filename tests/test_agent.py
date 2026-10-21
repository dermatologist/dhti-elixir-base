import pytest


@pytest.fixture(scope="session")
def agent():
    from src.dhti_elixir_base import BaseAgent

    return BaseAgent()


def test_agent_response(agent, capsys):
    input_data = {"input": "Answer in one word: What is the capital of France?"}
    _agent = agent.get_agent_response(context=input_data["input"])
    print(_agent)
    captured = capsys.readouterr()
    assert "processing your request" in captured.out


def test_base_agent(agent, capsys):
    o = agent.name
    print("Agent name: ", o)
    captured = capsys.readouterr()
    assert "Agent name:  base_agent" in captured.out


def test_base_agent_accepts_legacy_mcp_config():
    from src.dhti_elixir_base import BaseAgent

    custom_agent = BaseAgent(
        mcp={
            "test": {
                "transport": "http",
                "url": "http://localhost:9000/mcp",
            }
        }
    )
    assert custom_agent.client is not None
