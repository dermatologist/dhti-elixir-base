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

from crewai_tools import BaseTool as CrewAIBaseTool
from langchain_core.tools import BaseTool as LangChainBaseTool


class CrewAILangChainToolWrapper(CrewAIBaseTool):
    """
    Wrapper class to make LangChain Tool usable within CrewAI.

    This wrapper allows the use of standard LangChain tools within the CrewAI framework
    by adapting their interface to CrewAI's tool requirements.

    Args:
        langchain_tool: An instance of LangChain BaseTool
        **kwargs: Additional keyword arguments

    Example:
        ```python
        from langchain_community.tools import WikipediaQueryRun
        from langchain_community.utilities import WikipediaAPIWrapper
        from dhti_elixir_base.crewai import CrewAILangChainToolWrapper

        # Create a LangChain tool
        wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

        # Wrap it for use with CrewAI
        crewai_tool = CrewAILangChainToolWrapper(langchain_tool=wikipedia)
        ```
    """

    name: str = "LangChain Tool"
    description: str = "A tool that wraps a LangChain tool for use in CrewAI"

    def __init__(
        self,
        langchain_tool: LangChainBaseTool | Any,
        **kwargs: Any,
    ):
        """
        Initialize the CrewAI LangChain Tool wrapper.

        Args:
            langchain_tool: An instance of LangChain BaseTool or compatible tool
            **kwargs: Additional keyword arguments
        """
        self._langchain_tool = langchain_tool
        
        # Extract name and description from the LangChain tool
        tool_name = getattr(langchain_tool, "name", "langchain_tool")
        tool_description = getattr(
            langchain_tool, 
            "description", 
            "A LangChain tool wrapped for CrewAI"
        )
        
        # Initialize the base tool
        super().__init__(
            name=tool_name,
            description=tool_description,
            **kwargs,
        )

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """
        Execute the underlying LangChain tool.

        Args:
            *args: Positional arguments passed to the tool
            **kwargs: Keyword arguments passed to the tool

        Returns:
            str: The result of the tool execution
        """
        # Try different invocation methods based on the tool type
        try:
            # Try using the run method (common in LangChain tools)
            if hasattr(self._langchain_tool, "run"):
                if args and not kwargs:
                    result = self._langchain_tool.run(*args)
                elif kwargs:
                    result = self._langchain_tool.run(**kwargs)
                else:
                    result = self._langchain_tool.run()
            # Try using the invoke method (newer LangChain tools)
            elif hasattr(self._langchain_tool, "invoke"):
                if args and not kwargs:
                    result = self._langchain_tool.invoke(args[0] if len(args) == 1 else args)
                elif kwargs:
                    result = self._langchain_tool.invoke(kwargs)
                else:
                    result = self._langchain_tool.invoke({})
            # Try calling the tool directly
            elif callable(self._langchain_tool):
                if args and not kwargs:
                    result = self._langchain_tool(*args)
                elif kwargs:
                    result = self._langchain_tool(**kwargs)
                else:
                    result = self._langchain_tool()
            else:
                raise AttributeError(
                    f"LangChain tool {type(self._langchain_tool)} does not have "
                    "run, invoke, or __call__ methods"
                )
            
            # Convert result to string
            return str(result)
            
        except Exception as e:
            return f"Error executing LangChain tool: {e!s}"

    def __str__(self) -> str:
        """Return string representation of the wrapper."""
        return f"CrewAILangChainToolWrapper(tool={self._langchain_tool.name})"

    def __repr__(self) -> str:
        """Return detailed string representation of the wrapper."""
        return self.__str__()
