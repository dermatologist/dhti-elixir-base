import pytest



@pytest.fixture(scope="session")
def space():
    from dhti_elixir_base import BaseSpace
    return BaseSpace()


def test_base_space(space, capsys):
    pass