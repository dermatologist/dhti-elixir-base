import json
from collections.abc import Mapping, Sequence
from typing import Any

import requests
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ToolMessage,
)
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.utils.function_calling import convert_to_openai_tool
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

        
    ChatModel implementation compatible with:

    - invoke()
    - ainvoke()
    - stream()
    - create_tool_calling_agent()
    - LangGraph
    - bind_tools()

    Assumes OpenAI-compatible tool calling:
    request:
        {
          "messages": [...],
          "tools": [...]
        }

    response:
        {
          "choices": [
            {
              "message": {
                "content": "",
                "tool_calls": [...]
              }
            }
          ]
        }
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

    bound_tools: list[dict[str, Any]] = Field(default_factory=list)

    def __init__(self, base_url: str, model: str, **kwargs):
        super().__init__(**kwargs)

        self.base_url = base_url
        self.model = model

        self.params = {
            **self._get_model_default_parameters,
            **kwargs,
        }

    @property
    def _llm_type(self) -> str:
        return "dhti-chat"

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {
            "model": self.model,
            "base_url": self.base_url,
            "model_parameters": self._get_model_default_parameters,
        }

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

    def _prepare_payload(
        self,
        messages: Sequence[BaseMessage],
    ) -> dict[str, Any]:

        api_messages = []

        for message in messages:

            role_map = {
                "human": "user",
                "ai": "assistant",
                "system": "system",
                "tool": "tool",
            }

            role = role_map.get(
                getattr(message, "type", ""),
                "user",
            )

            msg = {
                "role": role,
                "content": message.content,
            }

            #
            # Forward previous assistant tool calls
            #
            if isinstance(message, AIMessage) and message.tool_calls:
                msg["tool_calls"] = [
                    {
                        "id": tc.get("id"),
                        "type": "function",
                        "function": {
                            "name": tc.get("name"),
                            "arguments": json.dumps(
                                tc.get("args", {})
                            ),
                        },
                    }
                    for tc in message.tool_calls
                ]

            #
            # Forward tool outputs
            #
            if isinstance(message, ToolMessage):
                msg["tool_call_id"] = message.tool_call_id

            api_messages.append(msg)

        payload = {
            "model": self.model,
            "options": self._get_model_default_parameters,
            "messages": api_messages,
        }

        #
        # Add tool definitions when bound
        #
        if self.bound_tools:
            payload["tools"] = self.bound_tools

        return payload

    def _post(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=self.timeout,
        )

        try:
            response.raise_for_status()

        except Exception as e:
            raise RuntimeError(
                f"API request failed: {e}; "
                f"status={response.status_code}; "
                f"body={response.text}"
            )

        return response.json()

    def _parse_tool_calls(
        self,
        raw_tool_calls: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        parsed = []

        for tc in raw_tool_calls:

            function = tc.get("function", {})

            arguments = function.get("arguments", {})

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except Exception:
                    arguments = {}

            parsed.append(
                {
                    "id": tc.get("id"),
                    "name": function.get("name"),
                    "args": arguments,
                    "type": "tool_call",
                }
            )

        return parsed

    def _extract_ai_message(
        self,
        data: dict[str, Any],
    ) -> AIMessage:

        content = ""
        tool_calls = []

        if data.get("choices"):

            choice = data["choices"][0]

            if (
                isinstance(choice, dict)
                and "message" in choice
            ):
                message = choice["message"]

                content = message.get("content") or ""

                raw_tool_calls = (
                    message.get("tool_calls")
                    or []
                )

                if raw_tool_calls:
                    tool_calls = self._parse_tool_calls(
                        raw_tool_calls
                    )

            elif "text" in choice:
                content = choice["text"]

        else:
            content = json.dumps(data)

        return AIMessage(
            content=content,
            tool_calls=tool_calls,
        )

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs,
    ) -> ChatResult:

        payload = self._prepare_payload(messages)

        if stop:
            payload["stop"] = stop

        payload.update(kwargs)

        data = self._post(payload)

        ai_message = self._extract_ai_message(data)

        return ChatResult(
            generations=[
                ChatGeneration(
                    message=ai_message
                )
            ]
        )

    def bind_tools(
        self,
        tools: Sequence[Any],
        tool_choice: Any = None,
        **kwargs,
    ):
        """
        True LangChain tool binding.

        Converts LangChain tools/functions into OpenAI
        tool schemas and returns a copied runnable model.

        Required by create_tool_calling_agent().
        """

        bound = self.model_copy(deep=True)

        converted_tools = []

        for tool in tools:

            try:
                converted_tools.append(
                    convert_to_openai_tool(tool)
                )

            except Exception:
                #
                # fallback for already-converted schemas
                #
                if isinstance(tool, dict):
                    converted_tools.append(tool)
                else:
                    raise

        bound.bound_tools = converted_tools

        #
        # Optional forced tool selection
        #
        if tool_choice is not None:
            bound.params = {
                **dict(bound.params),
                "tool_choice": tool_choice,
            }

        return bound
