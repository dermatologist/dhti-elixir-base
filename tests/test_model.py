import pytest


@pytest.fixture(scope="session")
def model():
    from src.dhti_elixir_base import BaseModel

    with pytest.raises(TypeError):
        return BaseModel()  # type: ignore


def test_base_model(model, capsys):
    pass
