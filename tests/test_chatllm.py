import json
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from src.dhti_elixir_base import BaseChatLLM


@pytest.fixture(scope="session")
def chatllm():
    """Fixture for creating a BaseChatLLM instance for testing."""
    return BaseChatLLM(
        base_url="https://api.example.com/chat",
        model="example-chat-model",
        api_key="test-api-key",
    )


@pytest.fixture
def mock_successful_response():
    """Fixture for a successful API response."""
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "This is a test response from the chat model."
                }
            }
        ]
    }


@pytest.fixture
def mock_text_response():
    """Fixture for an API response with text field instead of message."""
    return {
        "choices": [
            {
                "text": "This is a test response using text field."
            }
        ]
    }


def test_chatllm_initialization(chatllm):
    """Test that BaseChatLLM initializes correctly with required parameters."""
    assert chatllm.base_url == "https://api.example.com/chat"
    assert chatllm.model == "example-chat-model"
    assert chatllm.api_key == "test-api-key"
    assert chatllm.backend == "dhti"
    assert chatllm.temperature == 0.1


def test_chatllm_identifying_params(chatllm):
    """Test that identifying parameters are correctly returned."""
    params = chatllm._identifying_params
    assert params["model"] == "example-chat-model"
    assert params["base_url"] == "https://api.example.com/chat"
    assert "model_parameters" in params
    assert params["model_parameters"]["temperature"] == 0.1


def test_chatllm_llm_type(chatllm):
    """Test that the LLM type is correctly identified."""
    assert chatllm._llm_type == "dhti-chat"


def test_chatllm_model_default_parameters(chatllm):
    """Test that default model parameters are correctly set."""
    params = chatllm._get_model_default_parameters
    assert params["max_output_tokens"] == 512
    assert params["n_predict"] == 256
    assert params["top_k"] == 40
    assert params["top_p"] == 0.8
    assert params["temperature"] == 0.1
    assert params["n_batch"] == 8
    assert params["repeat_penalty"] == 1.18
    assert params["repeat_last_n"] == 64


def test_prepare_payload_single_human_message(chatllm):
    """Test payload preparation with a single human message."""
    messages = [HumanMessage(content="Hello, how are you?")]
    payload = chatllm._prepare_payload(messages)
    
    assert payload["model"] == "example-chat-model"
    assert "options" in payload
    assert "messages" in payload
    assert len(payload["messages"]) == 1
    assert payload["messages"][0]["role"] == "user"
    assert payload["messages"][0]["content"] == "Hello, how are you?"


def test_prepare_payload_conversation(chatllm):
    """Test payload preparation with a conversation (multiple messages)."""
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What is the weather today?"),
        AIMessage(content="I don't have access to real-time weather data."),
        HumanMessage(content="Okay, thanks anyway."),
    ]
    payload = chatllm._prepare_payload(messages)
    
    assert len(payload["messages"]) == 4
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][0]["content"] == "You are a helpful assistant."
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][1]["content"] == "What is the weather today?"
    assert payload["messages"][2]["role"] == "assistant"
    assert payload["messages"][2]["content"] == "I don't have access to real-time weather data."
    assert payload["messages"][3]["role"] == "user"
    assert payload["messages"][3]["content"] == "Okay, thanks anyway."


@patch('requests.post')
def test_generate_successful_response(mock_post, chatllm, mock_successful_response):
    """Test _generate method with a successful API response."""
    # Mock the API response
    mock_response = MagicMock()
    mock_response.json.return_value = mock_successful_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Test generation
    messages = [HumanMessage(content="Hello!")]
    result = chatllm._generate(messages)
    
    # Verify the result
    assert len(result.generations) == 1
    generation = result.generations[0]
    assert isinstance(generation.message, AIMessage)
    assert generation.message.content == "This is a test response from the chat model."
    
    # Verify the API was called correctly
    mock_post.assert_called_once()
    call_args = mock_post.call_args
    assert call_args[1]["timeout"] == 60
    assert "Authorization" in call_args[1]["headers"]
    assert call_args[1]["headers"]["Authorization"] == "Bearer test-api-key"


@patch('requests.post')
def test_generate_text_field_response(mock_post, chatllm, mock_text_response):
    """Test _generate method with a response using text field."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_text_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    messages = [HumanMessage(content="Test")]
    result = chatllm._generate(messages)
    
    assert len(result.generations) == 1
    assert result.generations[0].message.content == "This is a test response using text field."


@patch('requests.post')
def test_generate_fallback_to_json(mock_post, chatllm):
    """Test _generate method falls back to JSON when content cannot be extracted."""
    mock_response = MagicMock()
    mock_response.json.return_value = {"unexpected": "format"}
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    messages = [HumanMessage(content="Test")]
    result = chatllm._generate(messages)
    
    # Should return the JSON as a string
    assert len(result.generations) == 1
    content = result.generations[0].message.content
    assert "unexpected" in content
    assert "format" in content


@patch('requests.post')
def test_generate_api_error(mock_post, chatllm):
    """Test _generate method handles API errors correctly."""
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.raise_for_status.side_effect = Exception("API Error")
    mock_post.return_value = mock_response
    
    messages = [HumanMessage(content="Test")]
    
    with pytest.raises(RuntimeError) as exc_info:
        chatllm._generate(messages)
    
    assert "API request failed" in str(exc_info.value)
    assert "status=500" in str(exc_info.value)


@patch('requests.post')
def test_invoke_method(mock_post, chatllm, mock_successful_response):
    """Test that invoke method works correctly (inherited from BaseChatModel)."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_successful_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Test with string input (should be converted to HumanMessage)
    result = chatllm.invoke("Hello!")
    
    assert isinstance(result, AIMessage)
    assert result.content == "This is a test response from the chat model."


@patch('requests.post')
def test_invoke_with_message_list(mock_post, chatllm, mock_successful_response):
    """Test invoke method with a list of messages."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_successful_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    messages = [
        SystemMessage(content="You are helpful."),
        HumanMessage(content="Hi there!"),
    ]
    result = chatllm.invoke(messages)
    
    assert isinstance(result, AIMessage)
    assert result.content == "This is a test response from the chat model."


def test_custom_parameters():
    """Test that custom parameters can be passed during initialization."""
    custom_chatllm = BaseChatLLM(
        base_url="https://custom.api.com",
        model="custom-model",
        api_key="custom-key",
        temperature=0.5,
        max_output_tokens=1024,
        top_p=0.9,
    )
    
    assert custom_chatllm.temperature == 0.5
    assert custom_chatllm.max_output_tokens == 1024
    assert custom_chatllm.top_p == 0.9
    
    params = custom_chatllm._get_model_default_parameters
    assert params["temperature"] == 0.5
    assert params["max_output_tokens"] == 1024
    assert params["top_p"] == 0.9
