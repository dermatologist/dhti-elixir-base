import pytest



@pytest.fixture(scope="session")
def model():
    from dhti_elixir_base import BaseModel
    with pytest.raises(TypeError):
        return BaseModel()


def test_base_llm(model, capsys):
    pass