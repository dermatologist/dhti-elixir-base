import pytest



@pytest.fixture(scope="session")
def server():
    from dhti_elixir_base import BaseServer
    with pytest.raises(TypeError):
        return BaseServer()


def test_base_llm(server, capsys):
    pass