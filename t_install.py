import requests

from tests.bootstrap import bootstrap

bootstrap()
from dhti_elixir_base.chain import BaseChain

input = {"input": "Answer in one word: What is the capital of France?"}
result = BaseChain().chain.invoke(input=input)  # type: ignore
print(result)
assert result == "Paris"

