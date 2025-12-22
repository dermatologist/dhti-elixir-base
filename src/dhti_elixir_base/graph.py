"""
Copyright 2024 Bell Eapen

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

import functools
import operator
from collections.abc import Sequence
from typing import Annotated, Literal, TypedDict

from kink import di, inject
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, ToolMessage
from langgraph.graph import END, StateGraph

from .mydi import camel_to_snake

"""_summary_

    Helper class to add multi-agent support with langgraph.
    The agents can be BaseAgent derived classes and support VertexAI.
"""


@inject
class BaseGraph:
    # Ref 1: https://github.com/langchain-ai/langgraph/blob/main/examples/multi_agent/multi-agent-collaboration.ipynb
    # Ref 2: https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141
    # * call_tools = tool_node [ToolNode is currently not supported by VertexAI because of the lack of llm.bind_tools()]
    # ! Tools are handled by the respective agents
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        sender: str

    def __init__(
        self,
        agents=None,  # required
        edges=None,  # [{"from": "agent1", "to": "agent2", "conditional": True, "router": "default"}, {"from": "agent2", "to": "agent1", "conditional": True, "router": "default"}] #required
        entry_point="",  # required agent_1
        ends=None,  # optional
        end_words=None,  # optional ["exit", "quit", "bye", "sorry", "final"] The words that will trigger the end of the conversation
        agent_state=None,  # optional default AgentState above
        nodes=None,  # optional, generated
        workflow=None,  # optional, generated
        name=None,  # optional, generated
        recursion_limit=15,  # optional, default
    ):
        self.agents = agents if agents is not None else []
        self.edges = edges if edges is not None else []
        self.end_words = end_words if end_words is not None else []
        self.nodes = nodes
        self.workflow = workflow
        self.entry_point = entry_point
        self.agent_state = agent_state or self.AgentState
        self.ends = ends if ends is not None else []
        self.recursion_limit = recursion_limit
        self._name = name

    def init_graph(self):
        # We create a workflow that will be used to manage the state of the agents
        if self.workflow is None:
            self.workflow = StateGraph(self.agent_state)
        # We create the nodes for each agent
        if self.nodes is None:
            self.nodes = []
            for agent in self.agents:
                self.nodes.append(self.agent_node(agent))
        # We add the nodes to the workflow
        for node, agent in zip(self.nodes, self.agents):
            self.workflow.add_node(agent.name, node)
        # We set the entry point of the workflow
        self.workflow.set_entry_point(self.entry_point)
        # We set the end points of the workflow
        for end in self.ends:
            self.workflow.add_edge(end, END)
        # Add  edges
        for edge in self.edges:
            if edge["conditional"]:
                if edge["router"] == "default":
                    _router = self.router
                else:
                    _router = di[
                        edge["router"]
                    ]  # This is a dependency injection of router if needed
                self.workflow.add_conditional_edges(
                    edge["from"],
                    _router,
                    {"continue": edge["to"], "__end__": END},
                )
            else:
                self.workflow.add_edge(edge["from"], edge["to"])
        self.graph = self.workflow.compile()

    @property
    def name(self):
        if self._name:
            return self._name
        return camel_to_snake(self.__class__.__name__)

    @name.setter
    def name(self, value):
        self._name = value

    # Helper function to create a node for a given agent
    @staticmethod
    def create_agent_node(state, agent):
        _result = None
        try:
            result = agent.invoke(state)
        except ValueError:
            _result = agent.invoke({"input": state})
            result = _result["input"]["messages"][0]

        if _result is not None and "output" in _result:
            result = ToolMessage(content=_result["output"], tool_call_id="myTool")
        # We convert the agent output into a format that is suitable to append to the global state
        if isinstance(result, ToolMessage):
            pass
        else:
            try:
                result = AIMessage(
                    **result.dict(exclude={"type", "name"}), name=agent.name
                )
            except Exception:
                result = AIMessage(content=result.content, name=agent.name)
        return {
            "messages": [result],  # Yes, this should be an array!
            "sender": agent.name,
            # * Return other state variables if any
        }

    def agent_node(self, agent):
        return functools.partial(self.create_agent_node, agent=agent)

    def router(self, state) -> Literal["__end__", "continue"]:
        # This is the default router
        messages = state["messages"]
        last_message = messages[-1]
        if any(
            [exit.lower() in last_message.content.lower() for exit in self.end_words]
        ):
            return "__end__"
        return "continue"

    def invoke(self, message):
        events = self.graph.stream(
            {
                "messages": [
                    HumanMessage(
                        content=message,
                    )
                ],
            },
            # Maximum number of steps to take in the graph
            {"recursion_limit": self.recursion_limit},
        )
        return events
