"""
Copyright 2025 Bell Eapen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from typing import Any

from crewai.llms.base_llm import BaseLLM as CrewAIBaseLLM

from ..chatllm import BaseChatLLM
from ..llm import BaseLLM


class CrewAILLMWrapper(CrewAIBaseLLM):
    """
    Wrapper class to make BaseLLM and BaseChatLLM compatible with CrewAI.

    This wrapper allows the use of DHTI's LLM classes within the CrewAI framework
    by adapting their interfaces to CrewAI's requirements.

    Args:
        llm: An instance of BaseLLM or BaseChatLLM from dhti_elixir_base
        **kwargs: Additional keyword arguments

    Example:
        ```python
        from dhti_elixir_base import BaseChatLLM
        from dhti_elixir_base.crewai import CrewAILLMWrapper

        # Create a DHTI LLM instance
        dhti_llm = BaseChatLLM(
            base_url="https://api.example.com/chat",
            model="gpt-4",
            api_key="your-api-key"
        )

        # Wrap it for use with CrewAI
        crewai_llm = CrewAILLMWrapper(llm=dhti_llm)
        ```
    """

    def __init__(self, llm: BaseLLM | BaseChatLLM, **kwargs: Any):
        """
        Initialize the CrewAI LLM wrapper.

        Args:
            llm: An instance of BaseLLM or BaseChatLLM
            **kwargs: Additional keyword arguments
        """
        self._dhti_llm = llm
        self._model_name = getattr(llm, "model", "custom-model")

    def call(self, messages: list[dict[str, Any]], *args: Any, **kwargs: Any) -> str:
        """
        Call the underlying DHTI LLM with the provided messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            str: The generated response from the LLM
        """
        # Convert messages to the format expected by DHTI LLMs
        if isinstance(self._dhti_llm, BaseChatLLM):
            # For BaseChatLLM, convert to LangChain messages
            from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

            lc_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))
                else:  # user or any other role
                    lc_messages.append(HumanMessage(content=content))

            result = self._dhti_llm.invoke(lc_messages)
            return result.content if hasattr(result, "content") else str(result)
        else:
            # For BaseLLM, combine messages into a single prompt
            prompt = "\n".join(
                [
                    f"{msg.get('role', 'user')}: {msg.get('content', '')}"
                    for msg in messages
                ]
            )
            return self._dhti_llm.invoke(prompt)

    @property
    def is_litellm(self) -> bool:
        """Return whether this LLM is a LiteLLM provider."""
        return False

    @property
    def model(self) -> str:
        """Return the model name."""
        return self._model_name

    @property
    def provider(self) -> str:
        """Return the provider name."""
        return "dhti-elixir"

    def get_context_window_size(self) -> int:
        """Get the context window size for the model."""
        # Default context window size
        # This can be overridden in subclasses for specific models
        return 4096

    def get_token_usage_summary(self) -> dict[str, Any]:
        """Get token usage summary."""
        return {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    def supports_stop_words(self) -> bool:
        """Check if the model supports stop words."""
        return False

    def __str__(self) -> str:
        """Return string representation of the wrapper."""
        return f"CrewAILLMWrapper(llm={self._dhti_llm.__class__.__name__})"

    def __repr__(self) -> str:
        """Return detailed string representation of the wrapper."""
        return self.__str__()
