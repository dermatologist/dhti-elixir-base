import pytest


@pytest.fixture(scope="session")
def graph():
    from src.dhti_elixir_base import BaseGraph

    return BaseGraph()


def test_base_graph(graph, capsys):
    o = graph.name
    print("Graph name: ", o)
    captured = capsys.readouterr()
    assert "Graph name:  base_graph" in captured.out
