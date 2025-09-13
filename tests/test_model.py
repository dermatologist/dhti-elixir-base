import pytest


@pytest.fixture(scope="session")
def model():
    from src.dhti_elixir_base import BaseDhtiModel

    with pytest.raises(TypeError):
        return BaseDhtiModel()  # type: ignore


def test_base_model(model, capsys):
    pass
