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

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from pydantic import BaseModel, ConfigDict
import asyncio
import logging
from .mydi import camel_to_snake, get_di


logger = logging.getLogger(__name__)
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
        prompt=None,
        input_type: type[BaseModel] | None = None,
        tools: list | None = None,
        mcp={
            "mcpx": {
                "transport": "http",
                "url": "http://mcpx:9000/mcp",
            }
        },
    ):
        self.llm = llm or get_di("function_llm")
        self.prompt = prompt or get_di("agent_prompt") or "You are a helpful assistant."
        self.tools = tools if tools is not None else []
        self._name = name or camel_to_snake(self.__class__.__name__)
        self._description = description or f"Agent for {self._name}"
        if input_type is None:
            self.input_type = self.AgentInput
        else:
            self.input_type = input_type
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

    def has_tool(self) -> bool:
        """Check if the agent has any tools."""
        try:
            _tools = asyncio.run(self.client.get_tools())
            return bool(_tools)
        except Exception as e:
            logger.error(f"Error checking tools: {e}")
            return False

    def get_agent_response(self, context: str) -> str:
        if self.llm is None:
            raise ValueError("llm must not be None when initializing the agent.")
        result = "Agent encountered an error while processing your request."
        try:
            # if self.tools is an empty list, load tools from MCP
            if not self.tools:
                _tools = asyncio.run(self.client.get_tools())
            else:
                _tools = self.tools
            _agent = create_agent(model=self.llm, tools=_tools, system_prompt=self.prompt)

            result = asyncio.run(_agent.ainvoke(
                {"messages": [{"role": "user", "content": context}]}
            ))
            ai_message = result["messages"][-1].content
            return str(ai_message)
        except Exception as e:
            logger.error(f"Error in agent processing: {e}")
            return str(result)

    async def get_langgraph_mcp_agent(self):
        """Get the agent executor for async execution."""
        if self.llm is None:
            raise ValueError("llm must not be None when initializing the agent executor.")
        if self.client is None:
            raise ValueError("MCP client must not be None when initializing the agent.")
        tools = await self.get_langgraph_mcp_tools()
        agent = create_agent(
            model=self.llm,
            tools=tools,
            system_prompt=self.prompt,
        )
        return agent

    async def get_langgraph_mcp_tools(self, session_name="dhti"):
        """Get the agent executor for async execution with session."""
        if self.client is None:
            raise ValueError("MCP client must not be None when initializing the agent.")
        async with self.client.session(session_name) as session:
            tools = await load_mcp_tools(session)
        return tools
