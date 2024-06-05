import pytest


@pytest.fixture
def chain():
    from dhti_elixir_template.chain import chain
    return chain

def test_chain(chain):
    result = chain.invoke(input = "Answer in one word: What is the capital of France?")
    assert result == 'Paris'
