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
import logging
from kink import inject
from langchain_community.tools import StructuredTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_mcp_adapters.tools import to_fastmcp
from pydantic import BaseModel, ConfigDict

from .cds_hook.generate_cards import add_card
from .cds_hook.request_parser import get_context
from .mydi import camel_to_snake, get_di


logger = logging.getLogger(__name__)

@inject
class BaseChain:

    class ChainInput(BaseModel):
        """
        Input model for BaseChain.

        Attributes:
            input (Any): The input string or CDSHookRequest object for the chain.
        """

        input: Any
        model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)

    def __init__(
        self,
        prompt=None,
        name=None,
        description=None,
        main_llm=None,
        clinical_llm=None,
        grounding_llm=None,
        input_type=None,
        output_type=None,
    ):
        self._prompt = prompt or get_di("main_prompt")
        self._main_llm = main_llm or get_di("base_main_llm")
        self._clinical_llm = clinical_llm or get_di("base_clinical_llm")
        self._grounding_llm = grounding_llm or get_di("base_grounding_llm")
        self._input_type = input_type or self.ChainInput
        self._output_type = output_type
        self._name = name
        self._description = description
        self.init_prompt()

    @property
    def chain(self):
        """Get the runnable chain.

        Example usage of an agent in the chain:
        BaseAgent takes llm, prompt, tools as input. If tools is not provided, it loads tools from MCP. default llm is function_llm from DI.
        Default prompt is "You are a helpful assistant."
        self.my_agent = BaseAgent().get_agent_response # in __init__
        _chain = (
            RunnablePassthrough()
            | get_string_message_to_agent
            | self.my_agent
            | StrOutputParser()
        )

        RunnableParallel / RunnablePassthrough / RunnableSequential / RunnableLambda / RunnableMap / RunnableBranch
        """
        if self.prompt is None:
            raise ValueError("Prompt must not be None when building the chain.")
        _sequential = (
            RunnablePassthrough()
            | get_context  # function to extract context from input # type: ignore
            | self.prompt  # "{input}""
            | self.main_llm
            | StrOutputParser()
            | add_card  # function to wrap output in CDSHookCard
        )
        chain = _sequential.with_types(input_type=self.input_type)
        return chain

    @property
    def prompt(self):
        return self._prompt

    @property
    def main_llm(self):
        if self._main_llm is None:
            self._main_llm = get_di("base_main_llm")
        return self._main_llm

    @property
    def clinical_llm(self):
        if self._clinical_llm is None:
            self._clinical_llm = get_di("base_clinical_llm")
        return self._clinical_llm

    @property
    def grounding_llm(self):
        if self._grounding_llm is None:
            self._grounding_llm = get_di("base_grounding_llm")
        return self._grounding_llm

    @property
    def input_type(self):
        if self._input_type is None:
            self._input_type = self.ChainInput
        return self._input_type

    @property
    def output_type(self):
        return self._output_type

    @property
    def name(self):
        if self._name is None:
            return camel_to_snake(self.__class__.__name__)

    @property
    def description(self):
        if self._description is None:
            self._description = f"Chain for {self.name}"
        return self._description

    @prompt.setter
    def prompt(self, value):
        self._prompt = value
        self.init_prompt()

    @main_llm.setter
    def main_llm(self, value):
        self._main_llm = value

    @clinical_llm.setter
    def clinical_llm(self, value):
        self._clinical_llm = value

    @grounding_llm.setter
    def grounding_llm(self, value):
        self._grounding_llm = value

    @input_type.setter
    def input_type(self, value):
        self._input_type = value

    @output_type.setter
    def output_type(self, value):
        self._output_type = value

    @name.setter
    def name(self, value):
        self._name = value

    @description.setter
    def description(self, value):
        self._description = value

    def invoke(self, **kwargs):
        if self.chain is None:
            raise ValueError("Chain is not initialized.")
        return self.chain.invoke(kwargs)

    def __call__(self, **kwargs):
        return self.invoke(**kwargs)

    @DeprecationWarning
    def get_runnable(self, **kwargs):
        return self.chain

    # * Override these methods in subclasses
    def init_prompt(self):
        pass

    def generate_llm_config(self):
        """
        Generate the configuration schema for the LLM function call.

        Returns:
            dict: A dictionary containing the function schema for the LLM, including name, description, and parameters.
        """
        # Use Pydantic v2 API; `schema()` is deprecated in favor of `model_json_schema()`
        _input_schema = self.input_type.model_json_schema()
        function_schema = {
            "name": (self.name or self.__class__.__name__).lower().replace(" ", "_"),
            "description": self.description,
            "parameters": {
                "type": _input_schema.get("type", "object"),
                "properties": _input_schema.get("properties", {}),
                "required": _input_schema.get("required", []),
            },
        }
        return function_schema

    def get_chain_as_langchain_tool(self):
        """
        Convert the chain to a LangChain StructuredTool.

        Returns:
            StructuredTool: An instance of LangChain StructuredTool wrapping the chain.
        """

        def _run(**kwargs):
            # Invoke the underlying runnable chain with provided kwargs
            return self.chain.invoke(kwargs)  # type: ignore

        return StructuredTool.from_function(
            func=_run,
            name=self.name or self.__class__.__name__,
            description=self.description or f"Chain for {self.name}",
            args_schema=self.input_type,
        )

    def get_chain_as_mcp_tool(self):
        """
        Convert the chain to an MCP tool using the FastMCP adapter.

        Returns:
            Any: An MCP tool instance wrapping the chain.
        """
        _fast_mcp = to_fastmcp(
            self.get_chain_as_langchain_tool(),
        )
        _fast_mcp.title = self.name or self.__class__.__name__
        return _fast_mcp

    def print_log(self, message):
        logger.info(message)
        return message
