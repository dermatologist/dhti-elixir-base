try:
    from agency.agent import Agent, action
except ImportError:
    # If agency is not installed, create dummy classes
    class Agent:  # type: ignore[no-redef]
        """Dummy Agent class when agency is not installed."""
        pass

    def action(func):  # type: ignore[no-redef]
        """Dummy action decorator when agency is not installed."""
        return func

from . import BaseAgent


class BaseSpace(Agent):

    from typing import Optional

    def __init__(self, agent: BaseAgent | None = None, *args, **kwargs):
        if agent:
            self.agent = agent.get_agent()
            super().__init__(id=agent.name, *args, **kwargs)

    @action
    def say(self, content: str, current_patient_context: str = ""):
        """Search for a patient in the FHIR database."""
        #! TODO: Needs bootstrapping here.

        message = {
            "input": content,
            "current_patient_context": current_patient_context,
        }
        response_content = self.agent.invoke(message)
        self.send(
            {
                "to": self.current_message()["from"],  # type: ignore[index]
                "action": {
                    "name": "say",
                    "args": {
                        "content": response_content["output"],
                    },
                },
            }
        )
        return True
