import json
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool

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
                    "content": "This is a test response from the chat model.",
                }
            }
        ]
    }


@pytest.fixture
def mock_text_response():
    """Fixture for an API response with text field instead of message."""
    return {"choices": [{"text": "This is a test response using text field."}]}


@pytest.fixture
def mock_tool_call_response():
    """Fixture for an API response with tool calls."""
    return {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": "get_weather",
                                "arguments": json.dumps({"location": "Boston"}),
                            },
                        }
                    ],
                }
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
    assert (
        payload["messages"][2]["content"]
        == "I don't have access to real-time weather data."
    )
    assert payload["messages"][3]["role"] == "user"
    assert payload["messages"][3]["content"] == "Okay, thanks anyway."


def test_prepare_payload_with_tool_calls(chatllm):
    """Test payload preparation with AIMessage containing tool calls."""
    messages = [
        HumanMessage(content="What's the weather in Boston?"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_123",
                    "name": "get_weather",
                    "args": {"location": "Boston"},
                    "type": "tool_call",
                }
            ],
        ),
    ]
    payload = chatllm._prepare_payload(messages)

    assert len(payload["messages"]) == 2
    assert payload["messages"][1]["role"] == "assistant"
    assert "tool_calls" in payload["messages"][1]
    assert len(payload["messages"][1]["tool_calls"]) == 1
    assert payload["messages"][1]["tool_calls"][0]["id"] == "call_123"
    assert payload["messages"][1]["tool_calls"][0]["function"]["name"] == "get_weather"


def test_prepare_payload_with_tool_message(chatllm):
    """Test payload preparation with ToolMessage."""
    messages = [
        HumanMessage(content="What's the weather?"),
        AIMessage(
            content="",
            tool_calls=[
                {
                    "id": "call_123",
                    "name": "get_weather",
                    "args": {"location": "Boston"},
                    "type": "tool_call",
                }
            ],
        ),
        ToolMessage(content="The weather is sunny.", tool_call_id="call_123"),
    ]
    payload = chatllm._prepare_payload(messages)

    assert len(payload["messages"]) == 3
    assert payload["messages"][2]["role"] == "tool"
    assert payload["messages"][2]["tool_call_id"] == "call_123"
    assert payload["messages"][2]["content"] == "The weather is sunny."


def test_prepare_payload_with_bound_tools(chatllm):
    """Test payload preparation includes tools when bound."""
    chatllm.bound_tools = [{"type": "function", "function": {"name": "test_tool"}}]
    messages = [HumanMessage(content="Test")]
    payload = chatllm._prepare_payload(messages)

    assert "tools" in payload
    assert payload["tools"] == [{"type": "function", "function": {"name": "test_tool"}}]


def test_prepare_payload_empty_messages(chatllm):
    """Test payload preparation with empty messages list."""
    messages = []
    payload = chatllm._prepare_payload(messages)

    assert payload["messages"] == []
    assert payload["model"] == "example-chat-model"


@patch("requests.post")
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


@patch("requests.post")
def test_generate_text_field_response(mock_post, chatllm, mock_text_response):
    """Test _generate method with a response using text field."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_text_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    messages = [HumanMessage(content="Test")]
    result = chatllm._generate(messages)

    assert len(result.generations) == 1
    assert (
        result.generations[0].message.content
        == "This is a test response using text field."
    )


@patch("requests.post")
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


@patch("requests.post")
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


@patch("requests.post")
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


@patch("requests.post")
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


@patch("requests.post")
def test_generate_with_stop_sequences(mock_post, chatllm, mock_successful_response):
    """Test _generate method with stop sequences."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_successful_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    messages = [HumanMessage(content="Test")]
    result = chatllm._generate(messages, stop=["END", "STOP"])

    call_args = mock_post.call_args
    assert call_args[1]["json"]["stop"] == ["END", "STOP"]


@patch("requests.post")
def test_generate_with_tool_calls(mock_post, chatllm, mock_tool_call_response):
    """Test _generate method with tool calls in response."""
    mock_response = MagicMock()
    mock_response.json.return_value = mock_tool_call_response
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    messages = [HumanMessage(content="What's the weather?")]
    result = chatllm._generate(messages)

    assert len(result.generations) == 1
    message = result.generations[0].message
    assert isinstance(message, AIMessage)
    assert len(message.tool_calls) == 1
    assert message.tool_calls[0]["id"] == "call_123"
    assert message.tool_calls[0]["name"] == "get_weather"
    assert message.tool_calls[0]["args"] == {"location": "Boston"}


def test_parse_tool_calls(chatllm):
    """Test _parse_tool_calls method."""
    raw_tool_calls = [
        {
            "id": "call_123",
            "type": "function",
            "function": {
                "name": "get_weather",
                "arguments": json.dumps({"location": "Boston"}),
            },
        }
    ]

    parsed = chatllm._parse_tool_calls(raw_tool_calls)

    assert len(parsed) == 1
    assert parsed[0]["id"] == "call_123"
    assert parsed[0]["name"] == "get_weather"
    assert parsed[0]["args"] == {"location": "Boston"}
    assert parsed[0]["type"] == "tool_call"


def test_parse_tool_calls_with_dict_arguments(chatllm):
    """Test _parse_tool_calls with already-parsed dict arguments."""
    raw_tool_calls = [
        {
            "id": "call_456",
            "type": "function",
            "function": {"name": "get_time", "arguments": {"timezone": "UTC"}},
        }
    ]

    parsed = chatllm._parse_tool_calls(raw_tool_calls)

    assert len(parsed) == 1
    assert parsed[0]["args"] == {"timezone": "UTC"}


def test_parse_tool_calls_with_invalid_json(chatllm):
    """Test _parse_tool_calls handles invalid JSON gracefully."""
    raw_tool_calls = [
        {
            "id": "call_789",
            "type": "function",
            "function": {"name": "test", "arguments": "invalid json"},
        }
    ]

    parsed = chatllm._parse_tool_calls(raw_tool_calls)

    assert len(parsed) == 1
    assert parsed[0]["args"] == {}


def test_extract_ai_message_with_content(chatllm):
    """Test _extract_ai_message with content."""
    data = {"choices": [{"message": {"content": "Hello!", "role": "assistant"}}]}

    message = chatllm._extract_ai_message(data)

    assert isinstance(message, AIMessage)
    assert message.content == "Hello!"
    assert message.tool_calls == []


def test_extract_ai_message_with_empty_content(chatllm):
    """Test _extract_ai_message with empty content."""
    data = {"choices": [{"message": {"content": "", "role": "assistant"}}]}

    message = chatllm._extract_ai_message(data)

    assert message.content == ""


def test_extract_ai_message_with_tool_calls(chatllm):
    """Test _extract_ai_message with tool calls."""
    data = {
        "choices": [
            {
                "message": {
                    "content": "",
                    "tool_calls": [
                        {
                            "id": "call_123",
                            "type": "function",
                            "function": {
                                "name": "test_tool",
                                "arguments": json.dumps({"arg": "value"}),
                            },
                        }
                    ],
                }
            }
        ]
    }

    message = chatllm._extract_ai_message(data)

    assert len(message.tool_calls) == 1
    assert message.tool_calls[0]["name"] == "test_tool"


def test_extract_ai_message_fallback(chatllm):
    """Test _extract_ai_message fallback to JSON string."""
    data = {"unexpected": "format"}

    message = chatllm._extract_ai_message(data)

    assert "unexpected" in message.content
    assert "format" in message.content


def test_bind_tools_with_langchain_tool(chatllm):
    """Test bind_tools with a LangChain tool."""

    @tool
    def get_weather(location: str) -> str:
        """Get the weather for a location."""
        return f"Weather in {location}"

    bound_model = chatllm.bind_tools([get_weather])

    assert bound_model is not chatllm
    assert len(bound_model.bound_tools) == 1
    assert bound_model.bound_tools[0]["type"] == "function"
    assert bound_model.bound_tools[0]["function"]["name"] == "get_weather"


def test_bind_tools_with_dict_schema(chatllm):
    """Test bind_tools with already-converted dict schema."""
    tool_schema = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "A test tool",
            "parameters": {"type": "object"},
        },
    }

    bound_model = chatllm.bind_tools([tool_schema])

    assert len(bound_model.bound_tools) == 1
    assert bound_model.bound_tools[0] == tool_schema


def test_bind_tools_with_tool_choice(chatllm):
    """Test bind_tools with tool_choice parameter."""

    @tool
    def get_weather(location: str) -> str:
        """Get the weather for a location."""
        return f"Weather in {location}"

    bound_model = chatllm.bind_tools([get_weather], tool_choice="auto")

    assert "tool_choice" in bound_model.params
    assert bound_model.params["tool_choice"] == "auto"


def test_bind_tools_preserves_original_model(chatllm):
    """Test that bind_tools doesn't modify the original model."""

    @tool
    def get_weather(location: str) -> str:
        """Get the weather for a location."""
        return f"Weather in {location}"

    original_tools = chatllm.bound_tools.copy()
    bound_model = chatllm.bind_tools([get_weather])

    assert chatllm.bound_tools == original_tools
    assert bound_model.bound_tools != original_tools


def test_bind_tools_deep_copy(chatllm):
    """Test that bind_tools creates a deep copy."""

    @tool
    def get_weather(location: str) -> str:
        """Get the weather for a location."""
        return f"Weather in {location}"

    bound_model = chatllm.bind_tools([get_weather])

    bound_model.temperature = 0.9
    assert chatllm.temperature == 0.1


def test_post_method_success(chatllm):
    """Test _post method with successful response."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        payload = {"model": "test", "messages": []}
        result = chatllm._post(payload)

        assert result == {"result": "success"}
        mock_post.assert_called_once()


def test_post_method_with_custom_timeout(chatllm):
    """Test _post method uses custom timeout."""
    custom_chatllm = BaseChatLLM(
        base_url="https://api.example.com/chat",
        model="test-model",
        api_key="test-key",
        timeout=120,
    )

    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": "success"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        custom_chatllm._post({"model": "test", "messages": []})

        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 120


def test_post_method_404_error(chatllm):
    """Test _post method handles 404 error."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_response.raise_for_status.side_effect = Exception("404 Client Error")
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            chatllm._post({"model": "test", "messages": []})

        assert "status=404" in str(exc_info.value)
        assert "Not Found" in str(exc_info.value)


def test_post_method_401_error(chatllm):
    """Test _post method handles 401 authentication error."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.raise_for_status.side_effect = Exception("401 Client Error")
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError) as exc_info:
            chatllm._post({"model": "test", "messages": []})

        assert "status=401" in str(exc_info.value)


def test_model_copy_preserves_attributes(chatllm):
    """Test that model_copy preserves all attributes."""
    copied = chatllm.model_copy(deep=True)

    assert copied.base_url == chatllm.base_url
    assert copied.model == chatllm.model
    assert copied.api_key == chatllm.api_key
    assert copied.temperature == chatllm.temperature
    assert copied.timeout == chatllm.timeout
