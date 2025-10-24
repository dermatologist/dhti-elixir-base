import pytest


@pytest.fixture(scope="session")
def embedding():
    from src.dhti_elixir_base import BaseEmbedding

    with pytest.raises(TypeError):
        return BaseEmbedding()  # type: ignore


def test_base_embedding(embedding, capsys):
    pass
