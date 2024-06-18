import functools
import re
from kink import inject
from langgraph.graph import END, StateGraph
import operator
from typing import Annotated, Sequence, TypedDict, Literal
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, HumanMessage

@inject
class BaseGraph:
    # Ref 1: https://github.com/langchain-ai/langgraph/blob/main/examples/multi_agent/multi-agent-collaboration.ipynb
    # Ref 2: https://medium.com/@cplog/introduction-to-langgraph-a-beginners-guide-14f9be027141
    # * call_tools = tool_node
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]
        sender: str

    def __init__(self,
                 agents=[], #required
                 edges = [], # [{"from": "agent1", "to": "agent2", "conditional": True}, {"from": "agent2", "to": "agent1", "conditional": True}] #required
                 entry_point="", #required agent_1
                 ends=[], #required but can be empty
                 nodes = None, #generated
                 workflow = None, #generated
                 router = None, #generated based on edges
                 name = None, #generated
                 recursion_limit=150 #default
    ):
        self._agents = agents
        self._edges = edges
        self._nodes = nodes
        self._workflow = workflow
        self._router = router
        self._entry_point = entry_point
        self._ends = ends
        self._recursion_limit = recursion_limit
        self._name = name

    def init_graph(self):
        # We create a workflow that will be used to manage the state of the agents
        if self._workflow is None:
            self._workflow = StateGraph(self.AgentState)
        # We create the nodes for each agent
        if self._nodes is None:
            self._nodes = []
            for agent in self._agents:
                self._nodes.append(self.agent_node(agent))
        # We add the nodes to the workflow
        for node, agent in zip(self._nodes, self._agents):
            self._workflow.add_node(agent.name, node)
        # We set the entry point of the workflow
        self._workflow.set_entry_point(self._entry_point)
        # We set the end points of the workflow
        for end in self._ends:
            self._workflow.add_edge(end, END)
        # We set the router
        if self._router is None:
            self._router = self.router
        # Add  edges
        for edge in self._edges:
            if edge["conditional"]:
                self._workflow.add_conditional_edges(
                    edge["from"],
                    self._router,
                    {"continue": edge["to"], "__end__": END},
                )
            else:
                self._workflow.add_edge(edge["from"], edge["to"])
        self._graph = self._workflow.compile()

    @property
    def name(self):
        if self._name:
            return self._name
        return re.sub(r'(?<!^)(?=[A-Z])', '_', self.__class__.__name__).lower()

    @name.setter
    def name(self, value):
        self._name = value

    # Helper function to create a node for a given agent
    @staticmethod
    def create_agent_node(state, agent):
        try:
            result = agent.invoke(state)
        except ValueError as e:
            _result = agent.invoke({"input": state})
            result = _result["input"]["messages"][0]

        if "output" in _result:
            result = ToolMessage(content=_result["output"], tool_call_id="myTool")
        # We convert the agent output into a format that is suitable to append to the global state
        if isinstance(result, ToolMessage):
            pass
        else:
            try:
                result = AIMessage(**result.dict(exclude={"type", "name"}), name=agent.name)
            except Exception as e:
                result = AIMessage(content=result.content, name=agent.name)
        return {
            "messages": [result],
            # Since we have a strict workflow, we can
            # track the sender so we know who to pass to next.
            "sender": agent.name,
        }

    def agent_node(self, agent):
        return functools.partial(self.create_agent_node, agent=agent)

    def router(self,state) -> Literal["call_tool", "__end__", "continue"]:
        # This is the router
        messages = state["messages"]
        last_message = messages[-1]
        try:
            if "FINAL ANSWER" in last_message.content:
                # Any agent decided the work is done
                return "__end__"
        except AttributeError:
            if "FINAL ANSWER" in last_message["output"]:
                # Any agent decided the work is done
                return "__end__"
        return "continue"

    def invoke(self, message):
        events = self._graph.stream(
        {
                "messages": [
                    HumanMessage(
                        content=message,
                    )
                ],
            },
            # Maximum number of steps to take in the graph
            {"recursion_limit": self._recursion_limit},
        )
        return events
