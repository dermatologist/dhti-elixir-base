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
    from crewai_tools import BaseTool as CrewAIBaseTool

from ..chain import BaseChain


class CrewAIChainToolWrapper(CrewAIBaseTool):
    """
    Wrapper class to make BaseChain usable as a Tool within CrewAI.

    This wrapper allows the use of DHTI's BaseChain as a tool within the CrewAI framework
    by adapting its interface to CrewAI's tool requirements.

    Args:
        chain: An instance of BaseChain from dhti_elixir_base
        name: Name of the tool (optional, uses chain's name if not provided)
        description: Description of the tool (optional, uses chain's description if not provided)
        **kwargs: Additional keyword arguments

    Example:
        ```python
        from dhti_elixir_base import BaseChain
        from dhti_elixir_base.crewai import CrewAIChainToolWrapper

        # Create a DHTI chain instance
        dhti_chain = BaseChain(
            name="medical_analyzer",
            description="Analyzes medical records"
        )

        # Wrap it as a CrewAI tool
        crewai_tool = CrewAIChainToolWrapper(
            chain=dhti_chain,
            name="Medical Analyzer",
            description="Analyzes medical records and provides insights"
        )
        ```
    """

    name: str = "BaseChain Tool"
    description: str = "A tool that wraps a DHTI BaseChain for use in CrewAI"
    _dhti_chain: BaseChain = PrivateAttr()

    def __init__(
        self,
        chain: BaseChain,
        name: str | None = None,
        description: str | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the CrewAI Chain Tool wrapper.

        Args:
            chain: An instance of BaseChain
            name: Name of the tool
            description: Description of the tool
            **kwargs: Additional keyword arguments
        """
        # Set name and description from chain if not provided
        tool_name = name or chain.name or "chain_tool"
        tool_description = (
            description or chain.description or "A chain tool for processing inputs"
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

        # Store the DHTI chain reference
        self._dhti_chain = chain

    def _generate_description(self) -> None:
        """Override to prevent automatic description generation."""
        # Do nothing - we want to keep the simple description
        pass

    def _run(self, *args: Any, **kwargs: Any) -> str:
        """
        Execute the underlying DHTI chain.

        Args:
            *args: Positional arguments (first arg used as input if no kwargs)
            **kwargs: Keyword arguments passed to the chain

        Returns:
            str: The result of the chain execution
        """
        # If kwargs are provided, use them directly
        if kwargs:
            result = self._dhti_chain.invoke(**kwargs)
        # If a single positional arg is provided, treat it as the input
        elif args:
            result = self._dhti_chain.invoke(input=args[0])
        else:
            raise ValueError(
                "Either provide input as a keyword argument or as a positional argument"
            )

        # Convert result to string
        if isinstance(result, dict):
            # If result is a dict, try to extract the most relevant value
            if "cards" in result:
                # Handle CDS Hook response format
                return str(result.get("cards", []))
            elif "output" in result:
                return str(result["output"])
            else:
                return str(result)

        return str(result)

    def __str__(self) -> str:
        """Return string representation of the wrapper."""
        return f"CrewAIChainToolWrapper(chain={self._dhti_chain.name})"

    def __repr__(self) -> str:
        """Return detailed string representation of the wrapper."""
        return self.__str__()
