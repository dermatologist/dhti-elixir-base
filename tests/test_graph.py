import pytest
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage

@pytest.fixture
def base_graph():
    from dhti_elixir_base import BaseGraph
    agents = ["agent1", "agent2"]
    tools = ["tool1", "tool2"]
    edges = [{"from": "agent1", "to": "agent2", "contitional": True}]
    entry_point = "agent1"
    ends = ["agent2"]
    return BaseGraph(agents, tools, edges, entry_point, ends)

def test_init(base_graph):
    assert base_graph._agents == ["agent1", "agent2"]
    assert base_graph._tools == ["tool1", "tool2"]
    assert base_graph._edges == [{"from": "agent1", "to": "agent2", "contitional": True}]
    assert base_graph._entry_point == "agent1"
    assert base_graph._ends == ["agent2"]

def test_init_graph(base_graph):
    base_graph.init_graph()
    assert base_graph._workflow is not None
    assert base_graph._nodes is not None
    assert base_graph._router is not None
    assert base_graph._graph is not None

def test_create_agent_node(base_graph):
    agent = "agent1"
    state = {"messages": [], "sender": ""}
    result = base_graph.create_agent_node(state, agent)
    assert isinstance(result["messages"][0], AIMessage)
    assert result["sender"] == agent

def test_agent_node(base_graph):
    agent = "agent1"
    result = base_graph.agent_node(agent)
    assert callable(result)

def test_router(base_graph):
    state = {"messages": [AIMessage(content="FINAL ANSWER")]}
    result = base_graph.router(state)
    assert result == "__end__"

def test_invoke(base_graph):
    message = "Hello, world!"
    result = base_graph.invoke(message)
    assert isinstance(result, list)