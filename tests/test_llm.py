import pytest


@pytest.fixture(scope="session")
def llm():
    from src.dhti_elixir_base import BaseLLM
    return BaseLLM(
        base_url="https://api.example.com/llm",
        model="example-llm-model",
        api_key="test-api-key",
    )

def test_base_llm(llm, capsys):
    pass
