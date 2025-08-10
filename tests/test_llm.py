import pytest


@pytest.fixture(scope="session")
def llm():
    from src.dhti_elixir_base import BaseLLM

    with pytest.raises(TypeError):
        return BaseLLM()  # type: ignore


def test_base_llm(llm, capsys):
    pass
