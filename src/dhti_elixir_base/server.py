import logging
import sys
from abc import ABC
from typing import Any

from pydantic import BaseModel, Field

from . import BaseDhtiModel
from .mydi import camel_to_snake

# Set up logger
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
log = logging.getLogger(__name__)


class BaseServer(ABC):
    """A server class to load the model and tokenizer"""

    class RequestSchema(BaseModel):
        text: str = Field()
        labels: list = Field()
        required: list = Field()

    class ResponseSchema(BaseModel):
        text: str = Field()

    request_schema = RequestSchema
    response_schema = ResponseSchema

    def __init__(
        self, model: BaseDhtiModel, request_schema: Any = None, response_schema: Any = None
    ) -> None:
        self.model = model
        if request_schema is not None:
            self.request_schema = request_schema
        if response_schema is not None:
            self.response_schema = response_schema

    @property
    def name(self):
        return camel_to_snake(self.__class__.__name__)

    def health_check(self) -> Any:
        """Health check endpoint"""
        self.model.load()
        return {"status": "ok"}

    def get_schema(self) -> Any:
        """Get the request schema"""
        return self.request_schema

    def predict(self, input: Any, **kwargs) -> Any:
        _input = self.request_schema(**input)  # type: ignore
        _result = self.model.predict(_input, **kwargs)
        result = self.response_schema(**_result)  # type: ignore
        return result
