import pytest



@pytest.fixture(scope="session")
def agent():
    from dhti_elixir_base import BaseAgent
    return BaseAgent()


def test_base_agent(agent, capsys):
    o = agent.name
    print("Agent name: ", o)
    captured = capsys.readouterr()
    assert "Agent name:  base_agent" in captured.out
