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
from typing import List

from langchain.agents import AgentType, initialize_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel, Field, ConfigDict

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
        input_type: type[BaseModel] | None = None,
        prefix=None,
        suffix=None,
        tools: List = [],
    ):
        self.llm = llm or get_di("function_llm")
        self.prefix = prefix or get_di("prefix")
        self.suffix = suffix or get_di("suffix")
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

    # ! This is currently supported only for models supporting llm.bind_tools. See function return
    def langgraph_agent(self):
        """Create an agent."""
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
        return prompt | self.llm.bind_tools(self.tools)  # type: ignore
