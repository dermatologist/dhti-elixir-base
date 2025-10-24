import pytest


@pytest.fixture(scope="session")
def embedding():
    from src.dhti_elixir_base import BaseEmbedding
    return BaseEmbedding(
        base_url="https://api.example.com/embeddings",
        model="example-model",
        api_key="test-api-key",
    )


def test_base_embedding(embedding, capsys):
    pass
