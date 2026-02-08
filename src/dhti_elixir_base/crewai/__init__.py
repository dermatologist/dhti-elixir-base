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

"""
CrewAI Wrappers for DHTI Elixir Base.

This module provides wrapper classes that allow DHTI's LangChain-based components
(LLMs, Agents, Chains, and Tools) to be used within the CrewAI framework.

Available Wrappers:
    - CrewAILLMWrapper: Wraps BaseLLM and BaseChatLLM for CrewAI
    - CrewAIAgentWrapper: Wraps BaseAgent for CrewAI
    - CrewAIChainToolWrapper: Wraps BaseChain as a CrewAI Tool
    - CrewAILangChainToolWrapper: Wraps LangChain Tools for CrewAI

Example:
    ```python
    from dhti_elixir_base import BaseChatLLM, BaseAgent, BaseChain
    from dhti_elixir_base.crewai import (
        CrewAILLMWrapper,
        CrewAIAgentWrapper,
        CrewAIChainToolWrapper
    )
    
    # Wrap a DHTI LLM
    llm = BaseChatLLM(base_url="...", model="...", api_key="...")
    crewai_llm = CrewAILLMWrapper(llm=llm)
    
    # Wrap a DHTI Agent
    agent = BaseAgent(name="assistant", llm=llm)
    crewai_agent = CrewAIAgentWrapper(agent=agent)
    
    # Wrap a DHTI Chain as a Tool
    chain = BaseChain()
    crewai_tool = CrewAIChainToolWrapper(chain=chain)
    ```
"""

from .agent_wrapper import CrewAIAgentWrapper
from .chain_tool_wrapper import CrewAIChainToolWrapper
from .langchain_tool_wrapper import CrewAILangChainToolWrapper
from .llm_wrapper import CrewAILLMWrapper

__all__ = [
    "CrewAILLMWrapper",
    "CrewAIAgentWrapper",
    "CrewAIChainToolWrapper",
    "CrewAILangChainToolWrapper",
]
