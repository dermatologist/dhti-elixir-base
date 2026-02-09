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

from pydantic import PrivateAttr

try:
    from crewai.tools import BaseTool as CrewAIBaseTool
except ImportError:
    from crewai.tools.base_tool import BaseTool as CrewAIBaseTool

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
    _langchain_tool: LangChainBaseTool | Any = PrivateAttr()

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
        # Extract name and description from the LangChain tool
        tool_name = str(getattr(langchain_tool, "name", "langchain_tool"))
        tool_description = str(
            getattr(
                langchain_tool, "description", "A LangChain tool wrapped for CrewAI"
            )
        )

        # Initialize the base tool
        super().__init__(
            name=tool_name,
            description=tool_description,
            **kwargs,
        )

        # Restore the original description since CrewAI's _generate_description
        # prepends tool name and arguments to it
        self.description = tool_description

        # Store the LangChain tool reference
        self._langchain_tool = langchain_tool

    def _generate_description(self) -> None:
        """Override to prevent automatic description generation."""
        # Do nothing - we want to keep the simple description
        pass

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """
        Execute the underlying LangChain tool.

        Args:
            *args: Positional arguments passed to the tool
            **kwargs: Keyword arguments passed to the tool

        Returns:
            str: The result of the tool execution

        Raises:
            AttributeError: If no valid invocation method is found on the tool
        """
        try:
            # Try using the run method (common in LangChain tools)
            if hasattr(self._langchain_tool, "run"):
                try:
                    if args and not kwargs:
                        result = self._langchain_tool.run(*args)
                    elif kwargs:
                        result = self._langchain_tool.run(**kwargs)
                    else:
                        result = self._langchain_tool.run(tool_input={})
                    return str(result)
                except (AttributeError, TypeError):
                    # run method doesn't exist or failed, try next option
                    pass

            # Try using the invoke method (newer LangChain tools)
            if hasattr(self._langchain_tool, "invoke"):
                try:
                    if args and not kwargs:
                        result = self._langchain_tool.invoke(
                            args[0] if len(args) == 1 else args # type: ignore
                        )
                    elif kwargs:
                        result = self._langchain_tool.invoke(kwargs)
                    else:
                        result = self._langchain_tool.invoke({})
                    return str(result)
                except (AttributeError, TypeError):
                    # invoke method doesn't exist or failed, try next option
                    pass

            # Check if __call__ is explicitly set on the object (for test mocks)
            if "__call__" in self._langchain_tool.__dict__:
                __call_method = self._langchain_tool.__dict__["__call__"]
                if args and not kwargs:
                    result = __call_method(*args)
                elif kwargs:
                    result = __call_method(**kwargs)
                else:
                    result = __call_method()
                return str(result)

            # Try calling the tool directly if it's callable
            if callable(self._langchain_tool):
                try:
                    if args and not kwargs:
                        result = self._langchain_tool(*args)
                    elif kwargs:
                        result = self._langchain_tool(**kwargs)
                    else:
                        result = self._langchain_tool()
                    return str(result)
                except (AttributeError, TypeError):
                    # Direct call didn't work
                    pass

            # If we got here, no valid method was found
            tool_type = type(self._langchain_tool).__name__
            raise AttributeError(
                f"LangChain tool '{tool_type}' does not have any of the following: "
                "run(), invoke(), or __call__() methods"
            )

        except AttributeError:
            raise
        except Exception as e:
            return f"Error executing LangChain tool: {e!s}"

    def __str__(self) -> str:
        """Return string representation of the wrapper."""
        return f"CrewAILangChainToolWrapper(tool={self._langchain_tool.name})"

    def __repr__(self) -> str:
        """Return detailed string representation of the wrapper."""
        return self.__str__()
