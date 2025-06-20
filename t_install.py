import requests
from dhti_elixir_template.bootstrap import bootstrap
bootstrap()
from dhti_elixir_template.chain import chain


try:
    input = {
        "input": "Answer in one word: What is the capital of France?"
    }
    result = chain.invoke(input = input) # type: ignore
    assert result == 'Paris'
except (requests.exceptions.ConnectionError) as e:
    print("ConnectionError: Skipping test")
    assert True