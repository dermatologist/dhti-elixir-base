import pytest



@pytest.fixture(scope="session")
def chain():
    from dhti_elixir_base import BaseChain
    return BaseChain()


def test_base_agent(chain, capsys):
    o = chain.name
    print("Chain name: ", o)
    captured = capsys.readouterr()
    assert "Chain name:  base_chain" in captured.out
