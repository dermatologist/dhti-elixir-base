import json
from collections.abc import Mapping
from typing import Any, Sequence

import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from pydantic import Field


class BaseChatLLM(BaseChatModel):
    """
    BaseChatLLM extends BaseChatModel to support chat-based LLM invocations.

    This class handles message-based interactions (HumanMessage, AIMessage, SystemMessage)
    instead of plain string prompts, making it suitable for conversational AI applications.

    Args:
        base_url: The API endpoint URL for the chat model
        model: The name/identifier of the model to use
        api_key: Authentication key for API access
        temperature: Controls randomness in output (0.0-1.0, default: 0.1)
        max_output_tokens: Maximum tokens in the response (default: 512)
        top_p: Nucleus sampling parameter (default: 0.8)
        top_k: Top-k sampling parameter (default: 40)
        timeout: Request timeout in seconds (default: 60)

    Example:
        ```python
        from dhti_elixir_base import BaseChatLLM
        from langchain_core.messages import HumanMessage, SystemMessage

        chatllm = BaseChatLLM(
            base_url="https://api.example.com/chat",
            model="gpt-4",
            api_key="your-api-key",
            temperature=0.7
        )

        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What is the weather like?")
        ]
        response = chatllm.invoke(messages)
        ```
    """

    base_url: str | None = Field(None, alias="base_url")
    model: str | None = Field(None, alias="model")
    api_key: str | None = Field(None, alias="api_key")
    params: Mapping[str, Any] = Field(default_factory=dict, alias="params")
    timeout: int = 60
    backend: str | None = "dhti"
    temperature: float | None = 0.1
    top_p: float | None = 0.8
    top_k: int | None = 40
    n_batch: int | None = 8
    n_threads: int | None = 4
    n_predict: int | None = 256
    max_output_tokens: int | None = 512
    repeat_last_n: int | None = 64
    repeat_penalty: float | None = 1.18

    def __init__(self, base_url: str, model: str, **kwargs):
        super().__init__(**kwargs)
        self.base_url = base_url
        self.model = model
        self.params = {**self._get_model_default_parameters, **kwargs}

    @property
    def _get_model_default_parameters(self):
        return {
            "max_output_tokens": self.max_output_tokens,
            "n_predict": self.n_predict,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temperature": self.temperature,
            "n_batch": self.n_batch,
            "repeat_penalty": self.repeat_penalty,
            "repeat_last_n": self.repeat_last_n,
        }

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """
        Get all the identifying parameters
        """
        return {
            "model": self.model,
            "base_url": self.base_url,
            "model_parameters": self._get_model_default_parameters,
        }

    @property
    def _llm_type(self) -> str:
        return "dhti-chat"

    def _prepare_payload(self, messages: list[BaseMessage]) -> dict:
        """
        Prepare the API payload from a list of messages.

        Args:
            messages: List of BaseMessage objects (HumanMessage, AIMessage, SystemMessage, etc.)

        Returns:
            Dictionary payload for the API request
        """
        # Convert LangChain messages to API format
        api_messages = []
        for message in messages:
            # Extract role and content from the message
            if hasattr(message, "type"):
                # Map LangChain message types to API roles
                role_map = {
                    "human": "user",
                    "ai": "assistant",
                    "system": "system",
                }
                role = role_map.get(message.type, "user")
            else:
                role = "user"

            api_messages.append({"role": role, "content": message.content})

        return {
            "model": self.model,
            "options": self._get_model_default_parameters,
            "messages": api_messages,
        }

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs,
    ) -> ChatResult:
        """
        Generate a chat response from a list of messages.

        Args:
            messages: List of BaseMessage objects representing the conversation history
            stop: Optional list of strings to stop generation when encountered
            run_manager: Optional run manager for callbacks and tracing
            **kwargs: Additional keyword arguments

        Returns:
            ChatResult containing the generated response
        """
        payload = self._prepare_payload(messages)
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        resp = requests.post(
            self.base_url, headers=headers, json=payload, timeout=self.timeout  # type: ignore
        )
        try:
            resp.raise_for_status()
        except Exception as e:
            raise RuntimeError(
                f"API request failed: {e}; status={resp.status_code}; body={resp.text}"
            )

        data = resp.json()

        # Parse the response to extract the assistant's message
        message_content = None
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            # Support both "message" and direct "text" formats
            if (
                isinstance(choice, dict)
                and "message" in choice
                and isinstance(choice["message"], dict)
            ):
                message_content = choice["message"].get("content")
            elif "text" in choice:
                message_content = choice.get("text")

        # If we couldn't extract content, use raw JSON as fallback
        if message_content is None:
            message_content = json.dumps(data)

        # Create an AIMessage with the response
        message = AIMessage(content=message_content)

        # Wrap in ChatGeneration and ChatResult
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    def bind_tools(
        self, tools: Sequence[Any], tool_choice: Any = None, **kwargs
    ) -> "BaseChatLLM":
        """
        Bind external tools or functions to the LLM instance.

        Args:
            tools: Sequence of tool objects, types, or callables to be used by the LLM.
            tool_choice: Optional tool selection logic or identifier.
            **kwargs: Additional keyword arguments for tool binding.
        Returns:
            self (to allow chaining)
        """
        if not hasattr(self, "_bound_tools"):
            self._bound_tools = []
        self._bound_tools.extend(tools)
        return self
