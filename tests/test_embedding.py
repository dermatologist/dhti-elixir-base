from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def embedding():
    from src.dhti_elixir_base import BaseEmbedding

    return BaseEmbedding(
        base_url="https://api.example.com/embeddings",
        model="example-model",
        api_key="test-api-key",
    )


def test_base_embedding_initialization(embedding):
    """Test that BaseEmbedding initializes correctly."""
    assert embedding.base_url == "https://api.example.com/embeddings"
    assert embedding.model == "example-model"
    assert embedding.api_key == "test-api-key"


@patch("requests.post")
def test_base_embedding_embed_query(mock_post, embedding):
    """Test that BaseEmbedding can embed queries with mocked API calls."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"embeddings": [[0.1, 0.2, 0.3]]}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = embedding.embed_query("test query")

    assert result == [0.1, 0.2, 0.3]
    mock_post.assert_called_once()
