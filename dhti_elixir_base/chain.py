from kink import di, inject
import re
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.output_parser import StrOutputParser
from .mydi import get_di
@inject
class BaseChain:

    class ChainInput(BaseModel):
        question: str = Field()

    def __init__(self,
                 chain=None,
                 prompt={},
                 name=None,
                 description=None,
                 main_llm=None,
                 clinical_llm=None,
                 grounding_llm=None,
                 input_type=None,
                 output_type=None
                ):
        self._chain = chain
        self._prompt = prompt
        self._main_llm = main_llm
        self._clinical_llm = clinical_llm
        self._grounding_llm = grounding_llm
        self._input_type = input_type or self.ChainInput
        self._output_type = output_type
        self._name = name
        self._description = description
        self.init_prompt()

    @property
    def chain(self):
        if self._chain is None:
            """Get the runnable chain."""
            """ RunnableParallel / RunnablePassthrough / RunnableSequential / RunnableLambda / RunnableMap / RunnableBranch """
            _cot = RunnablePassthrough.assign(
                question = lambda x: x["question"],
                ) | self.prompt | self.main_llm | StrOutputParser()
            chain = _cot.with_types(input_type=self.input_type)
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
            return re.sub(r'(?<!^)(?=[A-Z])', '_', self.__class__.__name__).lower()

    @property
    def description(self):
        if self._description is None:
            self._description = f"Chain for {self.name}"
        return self._description

    @chain.setter
    def chain(self, value):
        self._chain = value

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
        return self.chain.invoke(kwargs)

    def __call__(self, **kwargs):
        return self.invoke(**kwargs)

    @DeprecationWarning
    def get_runnable(self, **kwargs):
        return self.chain

    #* Override these methods in subclasses
    def init_prompt(self):
        pass

    def generate_llm_config(self):
        _input_schema = self.input_type.schema()
        function_schema = {
            "name": self.name.lower().replace(" ", "_"),
            "description": self.description,
            "parameters": {
                "type": _input_schema["type"],
                "properties": _input_schema["properties"],
                "required": _input_schema["required"],
            },
        }
        return function_schema
