import pytest


@pytest.fixture(scope="session")
def chain():
    from src.dhti_elixir_base import BaseChain

    return BaseChain()


def test_chain_invoke(chain, capsys):
    input_data = input = {"input": "Answer in one word: What is the capital of France?"}
    result = chain.chain.invoke(input=input_data)  # type: ignore
    print(result)
    captured = capsys.readouterr()
    assert "Paris" in captured.out


def test_base_chain(chain, capsys):
    o = chain.name
    print("Chain name: ", o)
    captured = capsys.readouterr()
    assert "Chain name:  base_chain" in captured.out


def generate_llm_config(chain):
    o = chain.generate_llm_config()
    print(o)
    assert o == {
        "name": "base_chain",
        "description": "Chain for base_chain",
        "parameters": {
            "type": "object",
            "properties": {"question": {"title": "Question", "type": "string"}},
            "required": ["question"],
        },
    }
