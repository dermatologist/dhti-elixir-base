import pytest


@pytest.fixture(scope="session")
def server():
    from src.dhti_elixir_base import BaseServer

    with pytest.raises(TypeError):
        return BaseServer()  # type: ignore


def test_base_server(server, capsys):
    pass
