from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def llm():
    from src.dhti_elixir_base import BaseLLM

    return BaseLLM(
        base_url="https://api.example.com/llm",
        model="example-llm-model",
        api_key="test-api-key",
    )


def test_base_llm_initialization(llm):
    """Test that BaseLLM initializes correctly."""
    assert llm.base_url == "https://api.example.com/llm"
    assert llm.model == "example-llm-model"
    assert llm.api_key == "test-api-key"


@patch("requests.post")
def test_base_llm_invoke(mock_post, llm):
    """Test that BaseLLM can invoke with mocked API calls."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"result": "test response"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = llm.invoke("test prompt")

    assert result is not None
    mock_post.assert_called_once()
