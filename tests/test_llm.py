import pytest



@pytest.fixture(scope="session")
def llm():
    from dhti_elixir_base import BaseLLM
    with pytest.raises(TypeError):
        return BaseLLM()


def test_base_llm(llm, capsys):
    pass