
from tests.bootstrap import bootstrap

bootstrap()
from dhti_elixir_base.chain import BaseChain

input = {"input": "Answer in one word: What is the capital of France?"}
result = BaseChain().chain.invoke(input=input)  # type: ignore
print(result["cards"])
assert result is not None

input = {
    "hookInstance": "test_hook",
    "fhirServer": "http://example.com/fhir",
    "fhirAuthorization": "Bearer test_token",
    "hook": "patient-view",
    "context": {"input": "Answer in one word: What is the capital of France?"},
    "prefetch": {},
}
result = BaseChain().chain.invoke(input=input)  # type: ignore
print(result)
assert result is not None
