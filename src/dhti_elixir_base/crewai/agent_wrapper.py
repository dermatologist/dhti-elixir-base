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

from crewai import Agent as CrewAIAgent

from ..agent import BaseAgent
from .llm_wrapper import CrewAILLMWrapper


class CrewAIAgentWrapper(CrewAIAgent):
    """
    Wrapper class to make BaseAgent compatible with CrewAI.

    This wrapper allows the use of DHTI's BaseAgent within the CrewAI framework
    by adapting its interface to CrewAI's requirements.

    Args:
        agent: An instance of BaseAgent from dhti_elixir_base
        role: The role of the agent (optional, uses agent's description if not provided)
        goal: The goal of the agent (optional, uses agent's name if not provided)
        backstory: The backstory of the agent (optional)
        **kwargs: Additional keyword arguments passed to the CrewAI Agent

    Example:
        ```python
        from dhti_elixir_base import BaseAgent
        from dhti_elixir_base.crewai import CrewAIAgentWrapper

        # Create a DHTI agent instance
        dhti_agent = BaseAgent(
            name="medical_assistant",
            description="A medical assistant agent",
            llm=my_llm,
            prompt="You are a helpful medical assistant."
        )

        # Wrap it for use with CrewAI
        crewai_agent = CrewAIAgentWrapper(
            agent=dhti_agent,
            role="Medical Assistant",
            goal="Assist with medical queries"
        )
        ```
    """

    def __init__(
        self,
        agent: BaseAgent,
        role: str | None = None,
        goal: str | None = None,
        backstory: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the CrewAI Agent wrapper.

        Args:
            agent: An instance of BaseAgent
            role: The role of the agent
            goal: The goal of the agent
            backstory: The backstory of the agent
            **kwargs: Additional keyword arguments
        """
        self._dhti_agent = agent
        
        # Extract information from the DHTI agent
        agent_role = role or agent.description or "Assistant"
        agent_goal = goal or f"Execute tasks related to {agent.name}"
        agent_backstory = backstory or f"An agent specialized in {agent.name} tasks"
        
        # Wrap the LLM if available
        llm = None
        if agent.llm is not None:
            llm = CrewAILLMWrapper(llm=agent.llm)
        
        # Convert tools if available
        tools = kwargs.pop("tools", None)
        if tools is None and hasattr(agent, "tools") and agent.tools:
            # Use the agent's tools if available
            tools = agent.tools
        
        # Initialize CrewAI Agent
        super().__init__(
            role=agent_role,
            goal=agent_goal,
            backstory=agent_backstory,
            llm=llm,
            tools=tools,
            **kwargs,
        )

    def execute_task(self, task: Any, *args: Any, **kwargs: Any) -> str:
        """
        Execute a task using the underlying DHTI agent.

        Args:
            task: The task to execute
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            str: The result of the task execution
        """
        # Extract the task context/input
        task_context = str(task) if not hasattr(task, "description") else task.description
        
        # Use the DHTI agent's response method
        return self._dhti_agent.get_agent_response(task_context)

    def __str__(self) -> str:
        """Return string representation of the wrapper."""
        return f"CrewAIAgentWrapper(agent={self._dhti_agent.name})"

    def __repr__(self) -> str:
        """Return detailed string representation of the wrapper."""
        return self.__str__()
