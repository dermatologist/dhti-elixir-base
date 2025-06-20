
```python
from dhti_elixir_base import BaseAgent, BaseGraph
# Import things that are needed generically
from pydantic import BaseModel, Field
from langchain.tools import tool
from langchain.schema import (
    HumanMessage
)

from bootstrap import bootstrap
bootstrap()


class DoctorAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        print("Doctor Agent is running")


class PatientAgent(BaseAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        print("Patient Agent is running")

class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")


@tool("ask-question-tool", args_schema=SearchInput, return_direct=False)
def ask_question(*args, **kwargs) -> str:
    """Answer a question
        The only input is a string named query.
    """
    query = kwargs.get("query")
    if "query" not in kwargs:
        return "Please provide a query"
    if "fever" in query:
        return "Yes you have fever. You should take a rest."
    return "I am not sure about that."

# Agents can be CrewAI crew: https://github.com/joaomdmoura/crewAI-examples/tree/main/CrewAI-LangGraph
doctor = DoctorAgent(
    suffix = "I am here to help you with your health issues",
    tools=[ask_question],
).get_agent()
doctor.name = "doctor_agent"

patient = PatientAgent(
    suffix = "I want information on my health",
    tools=[ask_question],
).get_agent()
patient.name = "patient_agent"


class clinicGraph(BaseGraph):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


clinic = clinicGraph(
    agents=[doctor, patient],
    edges = [{"from": "doctor_agent", "to": "patient_agent", "conditional": True, "router": "default"}, {"from": "patient_agent", "to": "doctor_agent", "conditional": True, "router": "default"}],
    entry_point="doctor_agent",
    recursion_limit=5
)

clinic.init_graph()

message = [HumanMessage(content="I have fever. Should I take paracetamol?")]

events = clinic.invoke(message=message)

for s in events:
    print(s)
    print("----")
```

