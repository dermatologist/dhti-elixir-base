"""Tests for CrewAI LLM Wrapper."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def dhti_base_llm():
    """Create a mock BaseLLM instance."""
    from src.dhti_elixir_base import BaseLLM

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test response"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        llm = BaseLLM(
            base_url="https://api.example.com/llm",
            model="test-model",
            api_key="test-key",
        )
        yield llm


@pytest.fixture
def dhti_chat_llm():
    """Create a mock BaseChatLLM instance."""
    from src.dhti_elixir_base import BaseChatLLM

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Test chat response"}}]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        llm = BaseChatLLM(
            base_url="https://api.example.com/chat",
            model="test-chat-model",
            api_key="test-key",
        )
        yield llm


def test_crewai_llm_wrapper_initialization_with_base_llm(dhti_base_llm):
    """Test that CrewAILLMWrapper initializes correctly with BaseLLM."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAILLMWrapper

    wrapper = CrewAILLMWrapper(llm=dhti_base_llm)
    assert wrapper is not None
    assert wrapper._dhti_llm == dhti_base_llm
    assert "test-model" in str(wrapper.model)


def test_crewai_llm_wrapper_initialization_with_chat_llm(dhti_chat_llm):
    """Test that CrewAILLMWrapper initializes correctly with BaseChatLLM."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAILLMWrapper

    wrapper = CrewAILLMWrapper(llm=dhti_chat_llm)
    assert wrapper is not None
    assert wrapper._dhti_llm == dhti_chat_llm
    assert "test-chat-model" in str(wrapper.model)


@patch("requests.post")
def test_crewai_llm_wrapper_call_with_base_llm(mock_post, dhti_base_llm):
    """Test that CrewAILLMWrapper can call BaseLLM."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAILLMWrapper

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response from BaseLLM"}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    wrapper = CrewAILLMWrapper(llm=dhti_base_llm)
    messages = [
        {"role": "user", "content": "Hello"},
    ]
    
    result = wrapper.call(messages)
    assert result is not None
    assert isinstance(result, str)


@patch("requests.post")
def test_crewai_llm_wrapper_call_with_chat_llm(mock_post, dhti_chat_llm):
    """Test that CrewAILLMWrapper can call BaseChatLLM."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAILLMWrapper

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Response from BaseChatLLM"}}]
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    wrapper = CrewAILLMWrapper(llm=dhti_chat_llm)
    messages = [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Hello"},
    ]
    
    result = wrapper.call(messages)
    assert result is not None
    assert isinstance(result, str)


def test_crewai_llm_wrapper_string_representation(dhti_base_llm):
    """Test string representation of the wrapper."""
    pytest.importorskip("crewai")
    from src.dhti_elixir_base.crewai import CrewAILLMWrapper

    wrapper = CrewAILLMWrapper(llm=dhti_base_llm)
    str_repr = str(wrapper)
    assert "CrewAILLMWrapper" in str_repr
    assert "BaseLLM" in str_repr
