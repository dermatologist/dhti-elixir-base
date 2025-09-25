"""
Copyright 2023 Bell Eapen

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import re
from typing import List, Dict

from langchain.agents import AgentType, initialize_agent, AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field, ConfigDict
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from .mydi import get_di


# from langchain_core.prompts import MessagesPlaceholder
# from langchain.memory.buffer import ConversationBufferMemory
class BaseAgent:

    class AgentInput(BaseModel):
        """Chat history with the bot."""
        input: str
        model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    def __init__(
        self,
        name=None,
        description=None,
        llm=None,
        prompt={},
        input_type: type[BaseModel] | None = None,
        prefix=None,
        suffix=None,
        tools: List = [],
        mcp=None,
    ):
        self.llm = llm or get_di("function_llm")
        self.prefix = prefix or get_di("prefix")
        self.suffix = suffix or get_di("suffix")
        self.prompt = prompt or get_di("agent_prompt") or "You are a helpful assistant."
        self.tools = tools
        self._name = (
            name or re.sub(r"(?<!^)(?=[A-Z])", "_", self.__class__.__name__).lower()
        )
        self._description = description or f"Agent for {self._name}"
        # current_patient_context = MessagesPlaceholder(variable_name="current_patient_context")
        # memory = ConversationBufferMemory(memory_key="current_patient_context", return_messages=True)
        self.agent_kwargs = {
            "prefix": self.prefix,
            "suffix": self.suffix,
            # "memory_prompts": [current_patient_context],
            "input_variables": ["input", "agent_scratchpad", "current_patient_context"],
        }
        if input_type is None:
            self.input_type = self.AgentInput
        else:
            self.input_type = input_type
        if mcp is not None:
            self.client = MultiServerMCPClient(mcp)

    @property
    def name(self):
        return self._name

    @property
    def description(self):
        return self._description

    @name.setter
    def name(self, value):
        self._name = value

    @description.setter
    def description(self, value):
        self._description = value

    def get_agent(self):
        if self.llm is None:
            raise ValueError("llm must not be None when initializing the agent.")
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            stop=["\nObservation:"],
            max_iterations=len(self.tools) + 3,
            handle_parsing_errors=True,
            agent_kwargs=self.agent_kwargs,
            verbose=True,
        ).with_types(
            input_type=self.input_type # type: ignore
        )

    def get_react_agent(self):
        if self.llm is None:
            raise ValueError("llm must not be None when initializing the agent.")
        return create_react_agent(
            model=self.llm,
            tools=self.tools,
            prompt=self.prompt,
        ).with_types(
            input_type=self.input_type # type: ignore
        )

    # ! This is currently supported only for models supporting llm.bind_tools. See function return
    def get_agent_prompt(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "{prefix}"
                    " You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(prefix=self.prefix)
        prompt = prompt.partial(system_message=self.suffix)
        prompt = prompt.partial(
            tool_names=", ".join([tool.name for tool in self.tools])
        )
        return prompt

    def get_agent_chat_prompt_with_memory(self):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant."),
                # First put the history
                ("placeholder", "{chat_history}"),
                # Then the new input
                ("human", "{input}"),
                # Finally the scratchpad
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

    def langgraph_agent(self):
        """Create an agent."""
        prompt = self.get_agent_prompt()
        if not hasattr(self.llm, "bind_tools"):
            raise ValueError(
                "The LLM does not support binding tools. Please use a compatible LLM."
            )
        return prompt | self.llm.bind_tools(self.tools)  # type: ignore

    def get_langgraph_agent_executor(self):
        """Get the agent executor."""
        if self.llm is None:
            raise ValueError("llm must not be None when initializing the agent executor.")
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.get_agent_prompt(),
        )
        agent_executor = AgentExecutor(agent=agent, tools=self.tools)
        return agent_executor

    def get_langgraph_agent_executor_with_memory(self):
        from langchain_core.chat_history import InMemoryChatMessageHistory
        from langchain_core.runnables.history import RunnableWithMessageHistory
        if self.llm is None:
            raise ValueError(
                "llm must not be None when initializing the agent executor."
            )
        memory = InMemoryChatMessageHistory()
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "You are a helpful assistant."),
                # First put the history
                ("placeholder", "{chat_history}"),
                # Then the new input
                ("human", "{input}"),
                # Finally the scratchpad
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        agent = create_tool_calling_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt,
        )
        agent_executor = AgentExecutor(agent=agent, tools=self.tools)
        return RunnableWithMessageHistory(
            agent_executor,  # type: ignore
            # This is needed because in most real world scenarios, a session id is needed
            # It isn't really used here because we are using a simple in memory ChatMessageHistory
            lambda session_id: memory,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

    async def get_langgraph_mcp_agent(self):
        """Get the agent executor for async execution."""
        if self.llm is None:
            raise ValueError("llm must not be None when initializing the agent executor.")
        if self.client is None:
            raise ValueError("MCP client must not be None when initializing the agent.")
        tools = await self.get_langgraph_mcp_tools()
        agent = create_react_agent(
            model=self.llm,
            tools=tools,
            prompt=self.prompt,
        )
        return agent

    async def get_langgraph_mcp_tools(self, session_name="dhti"):
        """Get the agent executor for async execution with session."""
        if self.client is None:
            raise ValueError("MCP client must not be None when initializing the agent.")
        async with self.client.session(session_name) as session:
            tools = await load_mcp_tools(session)
        return tools
